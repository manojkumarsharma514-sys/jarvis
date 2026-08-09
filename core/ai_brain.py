"""
JARVIS AI Brain

M1.5:
Local Ollama-powered AI engine.

Features:
- Ollama HTTP API
- Streaming generation
- Centralized configuration
- Timeout protection
- Short JARVIS responses
- Optional TTS
- Safe error handling
"""

import json
import logging
from typing import Optional

import requests

from core.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)

from voice.speak import speak


logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------

OLLAMA_GENERATE_URL = (
    f"{OLLAMA_HOST.rstrip('/')}/api/generate"
)

# Connection timeout and generation timeout.
CONNECT_TIMEOUT = 5
READ_TIMEOUT = max(int(OLLAMA_TIMEOUT), 30)


# ------------------------------------------------------------------
# JARVIS SYSTEM PROMPT
# ------------------------------------------------------------------

JARVIS_SYSTEM_PROMPT = """
You are JARVIS, a fast personal AI assistant.

Rules:
- Answer directly.
- Keep responses concise.
- Normally use 1 to 3 sentences.
- Do not repeat the question.
- Do not use unnecessary introductions.
- Do not give long explanations unless specifically requested.
- Speak naturally because your response will be read aloud.
"""


# ------------------------------------------------------------------
# OLLAMA AVAILABILITY
# ------------------------------------------------------------------

def ollama_available() -> bool:
    """
    Check whether Ollama is running and reachable.
    """

    try:
        response = requests.get(
            f"{OLLAMA_HOST.rstrip('/')}/api/tags",
            timeout=CONNECT_TIMEOUT,
        )

        if response.status_code != 200:
            logger.warning(
                "Ollama returned HTTP %s",
                response.status_code,
            )
            return False

        return True

    except requests.RequestException as exc:

        logger.warning(
            "Ollama unavailable: %s",
            exc,
        )

        return False


# ------------------------------------------------------------------
# MODEL CHECK
# ------------------------------------------------------------------

def model_available() -> bool:
    """
    Check whether the configured model exists locally.
    """

    try:

        response = requests.get(
            f"{OLLAMA_HOST.rstrip('/')}/api/tags",
            timeout=CONNECT_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        models = data.get("models", [])

        for model in models:

            name = model.get("name", "")

            if name == OLLAMA_MODEL:
                return True

        logger.error(
            "Ollama model not found: %s",
            OLLAMA_MODEL,
        )

        return False

    except Exception as exc:

        logger.exception(
            "Failed to check Ollama model"
        )

        return False


# ------------------------------------------------------------------
# AI REQUEST
# ------------------------------------------------------------------

def ask_ai(
    prompt: str,
    speak_response: bool = True,
) -> Optional[str]:
    """
    Send a prompt to Ollama using streaming generation.

    Args:
        prompt:
            User's question/command.

        speak_response:
            If True, JARVIS speaks the final response.

    Returns:
        AI response string, or None on failure.
    """

    prompt = str(prompt).strip()

    if not prompt:
        logger.warning(
            "Empty AI prompt received"
        )
        return None

    # --------------------------------------------------------------
    # CHECK OLLAMA
    # --------------------------------------------------------------

    if not ollama_available():

        print(
            "❌ Ollama is not available."
        )

        if speak_response:

            try:
                speak(
                    "Sorry sir, my AI system is unavailable."
                )

            except Exception:
                logger.exception(
                    "Failed to speak Ollama error"
                )

        return None

    # --------------------------------------------------------------
    # CHECK MODEL
    # --------------------------------------------------------------

    if not model_available():

        print(
            f"❌ Ollama model not found: {OLLAMA_MODEL}"
        )

        if speak_response:

            try:
                speak(
                    "Sorry sir, my AI model is unavailable."
                )

            except Exception:
                logger.exception(
                    "Failed to speak model error"
                )

        return None

    # --------------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------------

    payload = {

        "model": OLLAMA_MODEL,

        "prompt": prompt,

        "system": JARVIS_SYSTEM_PROMPT,

        "stream": True,

        "options": {

            # Keep JARVIS responses short.
            "num_predict": 120,

            # Smaller context = less CPU work.
            "num_ctx": 2048,

            # Natural but deterministic responses.
            "temperature": 0.3,
        },
    }

    logger.info(
        "Sending streaming request to Ollama model: %s",
        OLLAMA_MODEL,
    )

    print(
        f"🤖 JARVIS AI: thinking..."
    )

    full_response = ""

    start_time = None

    try:

        import time

        start_time = time.time()

        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            stream=True,
            timeout=(
                CONNECT_TIMEOUT,
                READ_TIMEOUT,
            ),
        )

        response.raise_for_status()

        logger.info(
            "Ollama connection established"
        )

        # ----------------------------------------------------------
        # STREAM RESPONSE
        # ----------------------------------------------------------

        for line in response.iter_lines():

            if not line:
                continue

            try:

                data = json.loads(
                    line.decode("utf-8")
                )

            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
            ):

                logger.warning(
                    "Invalid Ollama stream chunk"
                )

                continue

            token = data.get(
                "response",
                "",
            )

            if token:

                full_response += token

                # Show tokens arriving.
                print(
                    token,
                    end="",
                    flush=True,
                )

            if data.get(
                "done",
                False,
            ):
                break

        print()

        elapsed = (
            time.time() - start_time
        )

        # ----------------------------------------------------------
        # CLEAN RESPONSE
        # ----------------------------------------------------------

        full_response = (
            full_response
            .strip()
        )

        if not full_response:

            logger.warning(
                "Ollama returned an empty response"
            )

            print(
                "❌ AI returned no response."
            )

            return None

        logger.info(
            "AI response received in %.2f seconds",
            elapsed,
        )

        print(
            f"🤖 AI: {full_response}"
        )

        # ----------------------------------------------------------
        # SPEAK
        # ----------------------------------------------------------

        if speak_response:

            try:

                speak(
                    full_response
                )

            except Exception:

                logger.exception(
                    "AI response generated but TTS failed"
                )

        return full_response

    # --------------------------------------------------------------
    # TIMEOUT
    # --------------------------------------------------------------

    except requests.exceptions.ReadTimeout:

        elapsed = (
            time.time() - start_time
            if start_time
            else 0
        )

        logger.error(
            "Ollama generation timed out after %.2f seconds",
            elapsed,
        )

        print(
            "❌ AI generation timed out."
        )

        if speak_response:

            try:

                speak(
                    "Sorry sir, the AI response took too long."
                )

            except Exception:
                logger.exception(
                    "Failed to speak timeout"
                )

        return None

    # --------------------------------------------------------------
    # CONNECTION ERROR
    # --------------------------------------------------------------

    except requests.exceptions.ConnectionError:

        logger.exception(
            "Could not connect to Ollama"
        )

        print(
            "❌ Could not connect to Ollama."
        )

        if speak_response:

            try:

                speak(
                    "Sorry sir, I cannot connect to my AI brain."
                )

            except Exception:
                logger.exception(
                    "Failed to speak connection error"
                )

        return None

    # --------------------------------------------------------------
    # HTTP ERROR
    # --------------------------------------------------------------

    except requests.exceptions.HTTPError as exc:

        logger.exception(
            "Ollama HTTP error: %s",
            exc,
        )

        print(
            f"❌ Ollama HTTP error: {exc}"
        )

        return None

    # --------------------------------------------------------------
    # OTHER ERROR
    # --------------------------------------------------------------

    except Exception as exc:

        logger.exception(
            "Unexpected AI error"
        )

        print(
            f"❌ AI Error: {exc}"
        )

        if speak_response:

            try:

                speak(
                    "Sorry sir, my AI brain encountered an error."
                )

            except Exception:
                logger.exception(
                    "Failed to speak AI error"
                )

        return None


# ------------------------------------------------------------------
# SIMPLE TEST
# ------------------------------------------------------------------

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )

    result = ask_ai(
        "What is artificial intelligence?",
        speak_response=False,
    )

    print()
    print(
        "FINAL RESULT:",
        result,
    )