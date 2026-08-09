"""
JARVIS Configuration

M1.5:
Centralized configuration for AI, voice, audio,
HUD, application paths, and runtime behavior.

Keep environment-specific settings here rather
than hard-coding them throughout the application.
"""

from pathlib import Path


# ------------------------------------------------------------------
# PROJECT
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# AI / OLLAMA
# ------------------------------------------------------------------

OLLAMA_PATH = (
    Path.home()
    / "AppData"
    / "Local"
    / "Programs"
    / "Ollama"
    / "ollama.exe"
)

# Local Ollama HTTP API
OLLAMA_HOST = "http://127.0.0.1:11434"

OLLAMA_MODEL = "phi3:mini"

# Maximum AI request time
OLLAMA_TIMEOUT = 30


# ------------------------------------------------------------------
# VOICE
# ------------------------------------------------------------------

VOICE_LANGUAGE = "en-US"

VOICE_TIMEOUT = 5

VOICE_PHRASE_TIME_LIMIT = 10

VOICE_AMBIENT_CALIBRATION = 1.0


# ------------------------------------------------------------------
# AUDIO / HUD
# ------------------------------------------------------------------

AUDIO_SAMPLE_RATE = 44100

AUDIO_BLOCK_SIZE = 1024

AUDIO_CHANNELS = 1


# ------------------------------------------------------------------
# APPLICATION
# ------------------------------------------------------------------

DOWNLOADS_PATH = (
    Path.home()
    / "Downloads"
)


# ------------------------------------------------------------------
# JARVIS BEHAVIOR
# ------------------------------------------------------------------

WAKE_WORD = "jarvis"

DEFAULT_STATUS = "IDLE"


# ------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------

LOG_LEVEL = "INFO"

LOG_FILE = PROJECT_ROOT / "debug.log"


def validate_config():
    """
    Validate important configuration values.

    Returns:
        tuple[bool, list[str]]
    """

    errors = []

    if not OLLAMA_MODEL:
        errors.append(
            "OLLAMA_MODEL is empty"
        )

    if VOICE_TIMEOUT <= 0:
        errors.append(
            "VOICE_TIMEOUT must be greater than 0"
        )

    if VOICE_PHRASE_TIME_LIMIT <= 0:
        errors.append(
            "VOICE_PHRASE_TIME_LIMIT must be greater than 0"
        )

    if AUDIO_SAMPLE_RATE <= 0:
        errors.append(
            "AUDIO_SAMPLE_RATE must be greater than 0"
        )

    if AUDIO_BLOCK_SIZE <= 0:
        errors.append(
            "AUDIO_BLOCK_SIZE must be greater than 0"
        )

    return (
        len(errors) == 0,
        errors,
    )