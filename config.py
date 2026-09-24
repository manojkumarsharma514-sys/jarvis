from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "jarvis_memory.db"
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "phi3:mini"
WAKE_WORD = "jarvis"
DEFAULT_TTS_RATE = 170
DEFAULT_TTS_VOLUME = 1.0
