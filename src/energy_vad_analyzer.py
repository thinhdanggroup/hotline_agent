import numpy as np
from loguru import logger

from pipecat.audio.vad.vad_analyzer import VADAnalyzer, VADParams


class EnergyBaseVADAnalyzer(VADAnalyzer):
    def __init__(self, *, sample_rate: int = 16000, params: VADParams = VADParams()):
        self.frame_duration_ms = 30
        super().__init__(sample_rate=sample_rate, num_channels=1, params=params)
        if sample_rate not in [8000, 16000]:
            raise ValueError("WebRTC VAD requires a sample rate of 8000 or 16000 Hz")

        logger.debug("Initializing WebRTC VAD...")

    def num_frames_required(self) -> int:
        return int(self.sample_rate * self.frame_duration_ms / 1000)

    def voice_confidence(self, buffer) -> float:
        audio_int16 = np.frombuffer(buffer, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_int16.astype(np.float32) ** 2))
        threshold = 500  # Adjust based on testing
        confidence = 1.0 if rms > threshold else 0.0
        return confidence
