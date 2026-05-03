"""
Lilu — Speech to Text (Whisper)
"""

import logging
import warnings
from pathlib import Path

import config

logger = logging.getLogger("lilu.voice.stt")

# Suppress FP16 warnings from whisper
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class WhisperSTT:
    """Local speech recognition using OpenAI Whisper."""

    def __init__(self):
        self.model = None
        if config.VOICE_ENABLED:
            self._load_model()

    def _load_model(self):
        try:
            import whisper
            logger.info(f"Loading Whisper model: {config.WHISPER_MODEL}...")
            self.model = whisper.load_model(config.WHISPER_MODEL)
            logger.info("Whisper model loaded.")
        except ImportError:
            logger.error("Whisper not installed. Run: pip install openai-whisper")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")

    def transcribe_file(self, audio_path: str | Path) -> str:
        """Transcribe an audio file to text."""
        if not self.model:
            return "Voice recognition is not enabled or model failed to load."
            
        try:
            result = self.model.transcribe(str(audio_path))
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return f"Error transcribing audio: {e}"
