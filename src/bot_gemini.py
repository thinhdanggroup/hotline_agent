#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Gemini Bot Implementation.

This module implements a chatbot using Google's Gemini Multimodal Live model.
It includes:
- Real-time audio/video interaction through Daily
- Animated robot avatar
- Speech-to-speech model

The bot runs as part of a pipeline that processes audio/video frames and manages
the conversation flow using Gemini's streaming capabilities.
"""

import asyncio
import os
import sys
from typing import List, Optional
from openai.types.chat import ChatCompletionToolParam
from datetime import datetime
from dotenv import load_dotenv
from src.helpers.datetime import serialize_datetime
from src.models import Conversation
from src.supabase_interface import SupabaseInterface
from loguru import logger
from PIL import Image
from runner import configure
import aiohttp
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    EndFrame,
    Frame,
    OutputImageRawFrame,
    SpriteFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIProcessor
from pipecat.services.gemini_multimodal_live.gemini import (
    GeminiMultimodalLiveLLMService,
)
from pipecat.transports.services.daily import DailyParams, DailyTransport

from energy_vad_analyzer import EnergyBaseVADAnalyzer
from utils import read_file
from webrtc_vad_analyzer import WebRTCVADAnalyzer

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

sprites = []
script_dir = os.path.dirname(__file__)

for i in range(1, 26):
    # Build the full path to the image file
    full_path = os.path.join(script_dir, f"assets/robot0{i}.png")
    # Get the filename without the extension to use as the dictionary key
    # Open the image and convert it to bytes
    with Image.open(full_path) as img:
        sprites.append(
            OutputImageRawFrame(image=img.tobytes(), size=img.size, format=img.format)
        )

# Create a smooth animation by adding reversed frames
flipped = sprites[::-1]
sprites.extend(flipped)

# Define static and animated states
quiet_frame = sprites[0]  # Static frame for when bot is listening
talking_frame = SpriteFrame(
    images=sprites
)  # Animation sequence for when bot is talking

global_task = None


class TalkingAnimation(FrameProcessor):
    """Manages the bot's visual animation states.

    Switches between static (listening) and animated (talking) states based on
    the bot's current speaking status.
    """

    def __init__(self):
        super().__init__()
        self._is_talking = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process incoming frames and update animation state.

        Args:
            frame: The incoming frame to process
            direction: The direction of frame flow in the pipeline
        """
        await super().process_frame(frame, direction)

        # Switch to talking animation when bot starts speaking
        if isinstance(frame, BotStartedSpeakingFrame):
            if not self._is_talking:
                await self.push_frame(talking_frame)
                self._is_talking = True
        # Return to static frame when bot stops speaking
        elif isinstance(frame, BotStoppedSpeakingFrame):
            await self.push_frame(quiet_frame)
            self._is_talking = False

        await self.push_frame(frame, direction)


async def end_conversation():
    global global_task
    if global_task is None:
        print(f"Task not found")
        return
    print(f"Ending conversation")
    # End the conversation after a delay
    await asyncio.sleep(3)

    await global_task.queue_frame(EndFrame())


async def update_transcript(room_url, context):
    # Get conversation record for this room
    conversations_db = SupabaseInterface[Conversation]("conversations")
    conversations = await conversations_db.read_all({"room_url": room_url})
    print(context.get_messages_for_persistent_storage())
    if conversations:
        conversation = conversations[0]
        # Update conversation with transcript and status
        await conversations_db.update(
            conversation["id"],
            {
                "transcript": context.get_messages_for_persistent_storage(),
                "status": "ended",
                "updated_at": serialize_datetime(datetime.now()),
            },
        )


def get_tool() -> List:
    return [
        {
            "function_declarations": [
                {
                    "name": "record_user_contact",
                    "description": "Record user contact information if user provides email or phone number.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "The phone number to use for contact.",
                            },
                            "email": {
                                "type": "string",
                                "description": "The email address to use for contact.",
                            },
                            "notes": {
                                "type": "string",
                                "description": "Summarize the conversation or provide additional context for Admin to follow up.",
                            },
                        },
                        "required": ["email", "notes"],
                    },
                },
                {
                    "name": "end_conversation",
                    "description": "End the conversation with the user if you think it's complete.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "end": {
                                "type": "boolean",
                                "description": "True to end the conversation.",
                            }
                        },
                        "required": ["end"],
                    },
                },
            ]
        }
    ]


async def main():
    """Main bot execution function.

    Sets up and runs the bot pipeline including:
    - Daily video transport with specific audio parameters
    - Gemini Live multimodal model integration
    - Voice activity detection
    - Animation processing
    - RTVI event handling
    """
    vad_engine = os.getenv("AMD_ENGINE", "")
    if vad_engine == "SileroVADAnalyzer":
        vad_analyzer = SileroVADAnalyzer(
            params=VADParams(
                stop_secs=0.5,
            ),
        )

    elif vad_engine == "WebRTCVADAnalyzer":
        vad_analyzer = WebRTCVADAnalyzer(
            params=VADParams(
                stop_secs=0.5,
            ),
        )
    else:
        vad_analyzer = EnergyBaseVADAnalyzer(
            params=VADParams(
                stop_secs=0.5,
            ),
        )
    print(f"Using VAD Analyzer: {vad_analyzer}")

    async with aiohttp.ClientSession() as session:
        (room_url, token, conv_id) = await configure(session)

        # Set up Daily transport with specific audio/video parameters for Gemini
        transport = DailyTransport(
            room_url,
            token,
            "Chatbot",
            DailyParams(
                audio_in_sample_rate=16000,
                audio_out_sample_rate=24000,
                audio_out_enabled=True,
                camera_out_enabled=False,
                # Disable camera output for performance issue
                # camera_out_enabled=True,
                # camera_out_width=1024,
                # camera_out_height=576,
                vad_enabled=True,
                vad_audio_passthrough=True,
                vad_analyzer=vad_analyzer,
            ),
        )

        system_prompt = read_file(filename="src/prompts/system.txt")

        # Initialize the Gemini Multimodal Live model
        llm = GeminiMultimodalLiveLLMService(
            api_key=os.getenv("GEMINI_API_KEY"),
            voice_id="Puck",  # Aoede, Charon, Fenrir, Kore, Puck
            transcribe_user_audio=True,
            transcribe_model_audio=True,
            # model="gemini-1.5-flash-latest",
            system_instruction=system_prompt,
            tools=get_tool(),
        )

        # Optional start callback - called when function execution begins
        async def record_user_contact(function_name, llm, context):
            print(f"[{function_name}] Function execution callback started {context}")

        # Main function handler - called to execute the function
        async def record_user_contact_api(
            function_name, tool_call_id, args, llm, context, result_callback
        ):
            print(
                f"[{function_name}] Function execution started {context} {tool_call_id} {args} {llm}"
            )

            try:
                if room_url:
                    # Initialize Supabase interface
                    conversations_db = SupabaseInterface[Conversation]("conversations")

                    # Find the conversation by room_url
                    conversations = await conversations_db.read_all(
                        {"room_url": room_url}
                    )
                    if conversations:
                        conversation = conversations[0]

                        # Update conversation with contact info in JSONB column
                        update_data = {
                            "updated_at": serialize_datetime(datetime.now()),
                            "contact": {  # Store contact info in JSONB column
                                "email": args.get("email"),
                                "phone_number": args.get("phone_number"),
                                "notes": args.get("notes"),
                            },
                        }

                        await conversations_db.update(conversation["id"], update_data)
                        await result_callback(
                            f"Contact information recorded successfully"
                        )
                    else:
                        await result_callback(
                            f"No active conversation found for this room"
                        )
                else:
                    await result_callback(f"Could not determine room URL")
            except Exception as e:
                print(f"Error recording contact: {str(e)}")
                await result_callback(f"Error recording contact information: {str(e)}")

        # Register the function
        llm.register_function(
            "record_user_contact",
            record_user_contact_api,
            start_callback=record_user_contact,
        )

        async def end_conversation_api(
            function_name, tool_call_id, args, llm, context, result_callback
        ):
            print(
                f"[{function_name}] Function execution started {context} {tool_call_id} {args} {llm}"
            )
            await update_transcript(room_url, context)
            await end_conversation()
            await result_callback(f"Conversation ended: {args}")

        llm.register_function(
            "end_conversation",
            end_conversation_api,
        )

        greeting_prompt = read_file(filename="src/prompts/greeting.txt")

        messages = [
            {
                "role": "user",
                "content": greeting_prompt,
            },
        ]

        # Set up conversation context and management
        # The context_aggregator will automatically collect conversation context
        context = OpenAILLMContext(
            messages=messages,
            tools=get_tool(),
        )
        context_aggregator = llm.create_context_aggregator(context)

        # ta = TalkingAnimation()

        #
        # RTVI events for Pipecat client UI
        #
        rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

        pipeline = Pipeline(
            [
                transport.input(),
                rtvi,
                context_aggregator.user(),
                llm,
                # ta,
                transport.output(),
                context_aggregator.assistant(),
            ]
        )

        task = PipelineTask(
            pipeline,
            PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
                observers=[rtvi.observer()],
            ),
        )
        await task.queue_frame(quiet_frame)

        global global_task
        global_task = task

        @rtvi.event_handler("on_client_ready")
        async def on_client_ready(rtvi):
            await rtvi.set_bot_ready()

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            await transport.capture_participant_transcription(participant["id"])
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        @transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason):
            print(f"Participant left: {participant}")
            await update_transcript(room_url, context)
            await task.queue_frame(EndFrame())

        runner = PipelineRunner()

        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
