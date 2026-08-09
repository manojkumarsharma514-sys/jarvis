"""
JARVIS Runtime State

M1.4:
Centralized runtime state shared by the voice system,
orchestrator, HUD, AI engine, and command system.
"""

from enum import Enum
import threading


class JarvisStatus(str, Enum):
    """Current operational state of JARVIS."""

    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    EXECUTING = "EXECUTING"
    SLEEPING = "SLEEPING"
    ERROR = "ERROR"
    SHUTTING_DOWN = "SHUTTING_DOWN"


# ------------------------------------------------------------------
# EXISTING COMPATIBILITY VARIABLES
# ------------------------------------------------------------------

awake = False
last_app = None
thinking = False


# ------------------------------------------------------------------
# NEW CENTRALIZED STATE
# ------------------------------------------------------------------

status = JarvisStatus.IDLE

last_command = ""
last_response = ""
current_intent = ""

error_message = ""

running = False


# Thread-safety lock.
_lock = threading.RLock()


def set_status(new_status):
    """
    Safely update the current JARVIS status.
    """

    global status

    with _lock:
        if isinstance(new_status, str):
            try:
                new_status = JarvisStatus(
                    new_status.upper()
                )
            except ValueError:
                new_status = JarvisStatus.ERROR

        status = new_status


def get_status():
    """Return the current JARVIS status."""

    with _lock:
        return status


def set_command(command):
    """Store the most recent command."""

    global last_command

    with _lock:
        last_command = command or ""


def set_response(response):
    """Store the most recent response."""

    global last_response

    with _lock:
        last_response = response or ""


def set_intent(intent):
    """Store the current detected intent."""

    global current_intent

    with _lock:
        current_intent = intent or ""


def set_error(message):
    """Store the most recent error."""

    global error_message

    with _lock:
        error_message = message or ""


def clear_error():
    """Clear the current error."""

    global error_message

    with _lock:
        error_message = ""


def reset():
    """Reset runtime state."""

    global awake
    global last_app
    global thinking
    global status
    global last_command
    global last_response
    global current_intent
    global error_message
    global running

    with _lock:
        awake = False
        last_app = None
        thinking = False

        status = JarvisStatus.IDLE

        last_command = ""
        last_response = ""
        current_intent = ""

        error_message = ""

        running = False