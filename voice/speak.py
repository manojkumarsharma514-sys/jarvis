"""
JARVIS Text-to-Speech Engine

Safe TTS implementation for the JARVIS application.
"""

import logging
import threading

import pyttsx3

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# TTS SETTINGS
# ------------------------------------------------------------

TTS_RATE = 170
TTS_VOLUME = 1.0

# Prevent multiple speech requests from running at once.
_speak_lock = threading.Lock()

# Lazy-created TTS engine.
_engine = None


# ------------------------------------------------------------
# ENGINE INITIALIZATION
# ------------------------------------------------------------

def _get_engine():
    """Create and return the TTS engine."""

    global _engine

    if _engine is not None:
        return _engine

    try:
        logger.info("Initializing JARVIS TTS engine...")

        engine = pyttsx3.init()

        engine.setProperty("rate", TTS_RATE)
        engine.setProperty("volume", TTS_VOLUME)

        _engine = engine

        logger.info("JARVIS TTS engine initialized")

        return _engine

    except Exception:
        logger.exception("Failed to initialize TTS engine")
        return None


# ------------------------------------------------------------
# SPEAK
# ------------------------------------------------------------

def speak(text: str) -> bool:
    """
    Speak text using Windows TTS.

    Returns:
        True  -> speech completed
        False -> speech failed
    """

    if not text:
        return False

    text = str(text).strip()

    if not text:
        return False

    print(f"🔊 Jarvis: {text}")

    with _speak_lock:

        engine = _get_engine()

        if engine is None:
            print("❌ JARVIS TTS engine unavailable")
            return False

        try:

            # ------------------------------------------------
            # HUD AUDIO EFFECT
            # ------------------------------------------------

            try:
                from hud.audio_input import audio_input

                audio_input.level += 0.5

            except Exception:
                # HUD failure must NEVER stop speech.
                logger.debug(
                    "HUD audio level update skipped",
                    exc_info=True,
                )

            # ------------------------------------------------
            # SPEAK
            # ------------------------------------------------

            engine.say(text)
            engine.runAndWait()

            return True

        except Exception:

            logger.exception(
                "JARVIS TTS speech failed"
            )

            # Try to recover the engine for the next request.
            try:
                engine.stop()
            except Exception:
                pass

            return False


# ------------------------------------------------------------
# STOP TTS
# ------------------------------------------------------------

def stop_speaking():
    """Immediately stop current speech."""

    global _engine

    if _engine is None:
        return

    try:
        _engine.stop()
    except Exception:
        logger.exception("Failed to stop TTS")


# ------------------------------------------------------------
# DIRECT TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("JARVIS TTS TEST")
    print("=" * 50)

    success = speak(
        "Hello, I am Jarvis. "
        "My voice system is working correctly."
    )

    if success:
        print("✅ TTS TEST PASSED")
    else:
        print("❌ TTS TEST FAILED")