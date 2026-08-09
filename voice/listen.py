from hud.audio_input import audio_input
import logging

import speech_recognition as sr


logger = logging.getLogger(__name__)


recognizer = sr.Recognizer()

# Microphone is intentionally NOT created during import.
mic = None

_initialized = False
_running = False


def start():
    """
    Initialize the speech-recognition microphone.

    Ambient noise calibration is performed once during startup
    instead of before every command.
    """

    global mic
    global _initialized
    global _running

    if _running:
        logger.debug("Voice listener already running")
        return

    try:
        logger.info("Initializing voice listener...")

        mic = sr.Microphone()

        logger.info(
            "Calibrating microphone for ambient noise..."
        )

        with mic as source:
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1,
            )

        _initialized = True
        _running = True

        logger.info(
            "Voice listener initialized successfully"
        )

    except Exception:
        mic = None
        _initialized = False
        _running = False

        logger.exception(
            "Failed to initialize voice listener"
        )

        raise


def stop():
    """
    Stop the voice listener.

    SpeechRecognition's Microphone does not require a persistent
    stream to close here; the object is released by dropping the
    reference.
    """

    global mic
    global _running
    global _initialized

    logger.info("Stopping voice listener")

    mic = None
    _running = False
    _initialized = False


def listen():
    """
    Listen for one voice command.

    Returns:
        str: Recognized speech or an empty string on failure.
    """

    global mic

    if not _running or mic is None:
        logger.warning(
            "Voice listener is not running"
        )
        return ""

    try:
        with mic as source:

            print("🎙️ Listening...")

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=15,
            )

        query = recognizer.recognize_google(audio)

        logger.info(
            "Recognized speech: %s",
            query,
        )

        # Push activity to HUD.
        audio_input.push_level(
            min(len(query) / 10, 1.0)
        )

        return query

    except sr.WaitTimeoutError:
        logger.debug(
            "No speech detected within timeout"
        )
        return ""

    except sr.UnknownValueError:
        logger.debug(
            "Speech could not be understood"
        )
        return ""

    except sr.RequestError as exc:
        logger.error(
            "Speech recognition service error: %s",
            exc,
        )
        return ""

    except Exception:
        logger.exception(
            "Unexpected voice recognition error"
        )
        return ""