import numpy as np
from loguru import logger

from pipecat.audio.vad.vad_analyzer import VADAnalyzer, VADParams

try:
    import webrtcvad
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error("You need to install `webrtcvad` to use WebRTC VAD. Please run `pip install webrtcvad`.")
    raise Exception(f"Missing module(s): {e}")

class WebRTCVADModel:
    def __init__(self, aggressiveness=1):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rates = [8000, 16000]
        self.frame_duration_ms = 30

    def _validate_input(self, x, sr: int):
        if sr not in self.sample_rates:
            raise ValueError(f"Supported sample rates: {self.sample_rates}")
        if np.ndim(x) != 1:
            raise ValueError("Input audio must be one-dimensional.")
        return x, sr

    def reset_states(self, batch_size=1):
        pass

    def __call__(self, x, sr: int):
        x, sr = self._validate_input(x, sr)
        frame_length = int(sr * self.frame_duration_ms / 1000)

        if len(x) != frame_length:
            raise ValueError(f"Expected {frame_length} samples for a {self.frame_duration_ms}ms frame at {sr}Hz.")

        pcm_data = (x * 32768).astype(np.int16).tobytes()
        is_speech = self.vad.is_speech(pcm_data, sr)
        confidence = np.array([1.0 if is_speech else 0.0], dtype=np.float32)
        return confidence

class WebRTCVADAnalyzer(VADAnalyzer):
    def __init__(self, *, sample_rate: int = 16000, params: VADParams = VADParams()):
        self.frame_duration_ms = 30
        super().__init__(sample_rate=sample_rate, num_channels=1, params=params)
        if sample_rate not in [8000, 16000]:
            raise ValueError("WebRTC VAD requires a sample rate of 8000 or 16000 Hz")

        logger.debug("Initializing WebRTC VAD...")
        self._model = WebRTCVADModel()
        logger.debug("WebRTC VAD initialized")

    def num_frames_required(self) -> int:
        return int(self.sample_rate * self.frame_duration_ms / 1000)

    def voice_confidence(self, buffer) -> float:
        try:
            audio_int16 = np.frombuffer(buffer, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            confidence = self._model(audio_float32, self.sample_rate)[0]
            return confidence
        except Exception as e:
            logger.error(f"Error analyzing audio with WebRTC VAD: {e}")
            return 0.0
