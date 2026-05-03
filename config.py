"""
Lilu AI Assistant — Configuration
Loads environment variables and exposes typed config.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env")


# ── LLM Config ────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "gpt-4o-mini")
FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "llama-3.3-70b-versatile")

# ── Voice Config ──────────────────────────────────────
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
TTS_VOICE: str = os.getenv("TTS_VOICE", "en-US-AriaNeural")

# ── Feature Flags ─────────────────────────────────────
VOICE_ENABLED: bool = os.getenv("VOICE_ENABLED", "false").lower() == "true"
WEB_UI_ENABLED: bool = os.getenv("WEB_UI_ENABLED", "false").lower() == "true"
MEMORY_ENABLED: bool = os.getenv("MEMORY_ENABLED", "true").lower() == "true"

# ── API Keys (Optional) ──────────────────────────────
GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "")
NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")

# ── Paths ─────────────────────────────────────────────
MEMORY_DIR: Path = BASE_DIR / "memory"
CONVERSATIONS_DIR: Path = MEMORY_DIR / "conversations"
USER_PROFILE_PATH: Path = MEMORY_DIR / "user_profile.json"
GOALS_PATH: Path = MEMORY_DIR / "goals.json"

# ── Ensure directories exist ─────────────────────────
MEMORY_DIR.mkdir(exist_ok=True)
CONVERSATIONS_DIR.mkdir(exist_ok=True)


# ── Validation ────────────────────────────────────────
def validate_config() -> list[str]:
    """Return list of warnings about missing config."""
    warnings = []
    if not OPENAI_API_KEY and not GROQ_API_KEY:
        warnings.append("No LLM API key configured. Set OPENAI_API_KEY or GROQ_API_KEY in .env")
    if VOICE_ENABLED:
        try:
            import whisper  # noqa: F401
        except ImportError:
            warnings.append("Voice enabled but whisper not installed. Run: pip install openai-whisper")
    return warnings


def get_active_provider() -> str:
    """Determine which LLM provider to use based on available keys."""
    if OPENAI_API_KEY:
        return "openai"
    elif GROQ_API_KEY:
        return "groq"
    else:
        return "none"
