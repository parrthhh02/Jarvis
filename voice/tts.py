"""
Lilu — Text to Speech (Edge TTS)
"""

import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path

import config

logger = logging.getLogger("lilu.voice.tts")


class EdgeTTS:
    """High-quality, free text-to-speech using Microsoft Edge TTS."""

    def __init__(self):
        self.voice = config.TTS_VOICE

    async def _generate_audio(self, text: str, output_path: str):
        """Generate audio file asynchronously."""
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            return True
        except ImportError:
            logger.error("edge-tts not installed. Run: pip install edge-tts")
            return False
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return False

    def speak(self, text: str):
        """Generate and play speech synchronously."""
        if not config.VOICE_ENABLED:
            return

        # Clean text for speech (remove markdown)
        clean_text = self._clean_markdown(text)
        
        if not clean_text.strip():
            return

        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                temp_path = tf.name

            # Generate audio
            asyncio.run(self._generate_audio(clean_text, temp_path))

            # Play audio (Windows specific, adjust for Mac/Linux if needed)
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Use powershell to play mp3 without opening UI
                subprocess.run(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{temp_path}').PlaySync();"],
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            elif system == "Darwin": # macOS
                subprocess.run(["afplay", temp_path])
            else: # Linux
                subprocess.run(["mpg123", "-q", temp_path])
                
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
        finally:
            # Cleanup
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Roughly remove markdown symbols for better speech."""
        import re
        # Remove code blocks
        text = re.sub(r'```.*?```', 'Code block omitted for speech.', text, flags=re.DOTALL)
        # Remove bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove headers
        text = re.sub(r'#+\s*(.*)', r'\1', text)
        # Remove emojis (basic)
        text = re.sub(r'[^\w\s.,?!;:-\'"]', '', text)
        return text
