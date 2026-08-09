"""
JARVIS Application Orchestrator

M1.6:
Centralizes application startup, voice-loop lifecycle,
HUD lifecycle, audio lifecycle, runtime state,
Qt event-loop management, deterministic command execution,
and AI fallback processing.

Architecture:

    Voice
      ↓
    Normalize
      ↓
    Deterministic Command Handler
      ↓
    ┌───────────────┐
    │ handled=True  │ → Execute + respond
    │ handled=False │ → AI Brain → Ollama → TTS
    └───────────────┘

Existing voice, TTS, NLP, command handler, HUD,
application launcher, and runtime state implementations
are preserved.
"""

import logging
import threading
from typing import Any, Optional

from PyQt6.QtWidgets import QApplication

from voice.listen import (
    listen,
    start as start_voice,
    stop as stop_voice,
)

from hud.audio_input import audio_input

from voice.speak import speak
from core.command_handler import handle_command
from core.nlp import normalize_command
from core.ai_brain import ask_ai

import core.state as state

from core.app_launcher import build_app_index
from hud.ui import HUD


logger = logging.getLogger(__name__)


class JarvisOrchestrator:
    """Central lifecycle controller for the Jarvis application."""

    def __init__(self):
        self.running = False

        # Optional application components.
        self.components: dict[str, Any] = {}

        # Qt application.
        self.app: Optional[QApplication] = None

        # HUD instance.
        self.hud_dashboard: Optional[HUD] = None

        # Voice worker thread.
        self.voice_thread: Optional[threading.Thread] = None

        # Lifecycle flags.
        self.audio_started = False
        self.voice_started = False

        logger.info(
            "Jarvis Orchestrator initialized"
        )

    # ==================================================================
    # COMPONENT MANAGEMENT
    # ==================================================================

    def register_component(
        self,
        name: str,
        component: Any,
    ):
        """
        Register an optional JARVIS component.

        Components may optionally provide:
            start()
            stop()
        """

        self.components[name] = component

        logger.info(
            "Component registered: %s",
            name,
        )

    # ==================================================================
    # APPLICATION STARTUP
    # ==================================================================

    def start(self):
        """Start the complete JARVIS application."""

        if self.running:
            logger.warning(
                "JARVIS is already running"
            )
            return

        logger.info(
            "Starting JARVIS..."
        )

        try:

            # ----------------------------------------------------------
            # 1. RESET RUNTIME STATE
            # ----------------------------------------------------------

            state.reset()

            state.running = False
            state.awake = False

            # ----------------------------------------------------------
            # 2. BUILD APPLICATION INDEX
            # ----------------------------------------------------------

            logger.info(
                "Building application index..."
            )

            build_app_index()

            # ----------------------------------------------------------
            # 3. CREATE QT APPLICATION
            # ----------------------------------------------------------

            logger.info(
                "Creating Qt application..."
            )

            self.app = QApplication.instance()

            if self.app is None:
                self.app = QApplication([])

            # ----------------------------------------------------------
            # 4. CREATE HUD
            # ----------------------------------------------------------

            logger.info(
                "Initializing JARVIS HUD..."
            )

            self.hud_dashboard = HUD()

            self.hud_dashboard.show()

            # ----------------------------------------------------------
            # 5. START HUD AUDIO MONITOR
            # ----------------------------------------------------------

            logger.info(
                "Starting HUD audio monitor..."
            )

            audio_input.start()

            self.audio_started = True

            logger.info(
                "HUD audio monitor started"
            )

            # ----------------------------------------------------------
            # 6. INITIALIZE SPEECH RECOGNITION
            # ----------------------------------------------------------

            logger.info(
                "Initializing voice recognition..."
            )

            start_voice()

            self.voice_started = True

            logger.info(
                "Voice recognition initialized"
            )

            # ----------------------------------------------------------
            # 7. MARK APPLICATION AS RUNNING
            # ----------------------------------------------------------

            self.running = True

            state.running = True
            state.awake = False
            state.thinking = False

            state.clear_error()

            state.set_status(
                state.JarvisStatus.IDLE
            )

            # ----------------------------------------------------------
            # 8. START VOICE WORKER THREAD
            # ----------------------------------------------------------

            self.voice_thread = threading.Thread(
                target=self.voice_loop,
                name="JarvisVoiceLoop",
                daemon=True,
            )

            self.voice_thread.start()

            logger.info(
                "Voice worker thread started"
            )

            # ----------------------------------------------------------
            # 9. CONNECT QT SHUTDOWN SIGNAL
            # ----------------------------------------------------------

            if self.app is not None:

                self.app.aboutToQuit.connect(
                    self.shutdown
                )

            logger.info(
                "JARVIS started successfully"
            )

            # ----------------------------------------------------------
            # 10. START QT EVENT LOOP
            # ----------------------------------------------------------

            if self.app is not None:

                self.app.exec()

        except Exception as exc:

            logger.exception(
                "Failed to start JARVIS"
            )

            state.set_error(
                str(exc)
            )

            state.set_status(
                state.JarvisStatus.ERROR
            )

            self.running = False
            state.running = False

            self._cleanup_resources()

            raise

    # ==================================================================
    # VOICE LOOP
    # ==================================================================

    def voice_loop(self):
        """Main JARVIS voice-processing loop."""

        logger.info(
            "Voice loop started"
        )

        try:

            # ----------------------------------------------------------
            # JARVIS ONLINE
            # ----------------------------------------------------------

            state.set_status(
                state.JarvisStatus.SPEAKING
            )

            self.update_hud_status(
                "JARVIS ONLINE"
            )

            speak(
                "Jarvis online"
            )

            # ----------------------------------------------------------
            # MAIN LOOP
            # ----------------------------------------------------------

            while self.running:

                # ------------------------------------------------------
                # LISTEN
                # ------------------------------------------------------

                state.set_status(
                    state.JarvisStatus.LISTENING
                )

                self.update_hud_status(
                    "LISTENING"
                )

                query = listen()

                if not query:
                    continue

                query = query.lower().strip()

                logger.info(
                    "Heard command: %s",
                    query,
                )

                state.set_command(
                    query
                )

                # ------------------------------------------------------
                # WAKE JARVIS
                # ------------------------------------------------------

                if (
                    "jarvis" in query
                    and not state.awake
                ):

                    state.awake = True

                    state.set_status(
                        state.JarvisStatus.SPEAKING
                    )

                    self.update_hud_status(
                        "AWAKE"
                    )

                    speak(
                        "Yes sir"
                    )

                    continue

                # ------------------------------------------------------
                # SLEEP COMMAND
                # ------------------------------------------------------

                if "sleep" in query:

                    state.awake = False

                    state.set_status(
                        state.JarvisStatus.SLEEPING
                    )

                    self.update_hud_status(
                        "SLEEPING"
                    )

                    speak(
                        "Going to sleep"
                    )

                    continue

                # ------------------------------------------------------
                # IGNORE COMMANDS WHILE SLEEPING
                # ------------------------------------------------------

                if not state.awake:
                    continue

                # ------------------------------------------------------
                # REMOVE WAKE WORD
                # ------------------------------------------------------

                query = query.replace(
                    "jarvis",
                    "",
                ).strip()

                if not query:
                    continue

                # ------------------------------------------------------
                # THINKING
                # ------------------------------------------------------

                state.thinking = True

                state.set_status(
                    state.JarvisStatus.THINKING
                )

                self.update_hud_status(
                    "THINKING"
                )

                # ------------------------------------------------------
                # NORMALIZE COMMAND
                # ------------------------------------------------------

                try:

                    query = normalize_command(
                        query
                    )

                except Exception as exc:

                    logger.exception(
                        "Command normalization failed"
                    )

                    state.set_error(
                        str(exc)
                    )

                    state.thinking = False

                    state.set_status(
                        state.JarvisStatus.ERROR
                    )

                    self.update_hud_status(
                        "ERROR"
                    )

                    continue

                state.set_command(
                    query
                )

                # ------------------------------------------------------
                # DETERMINISTIC COMMAND HANDLER
                # ------------------------------------------------------

                try:

                    logger.info(
                        "Processing command: %s",
                        query,
                    )

                    state.set_status(
                        state.JarvisStatus.EXECUTING
                    )

                    self.update_hud_status(
                        "EXECUTING"
                    )

                    handled = handle_command(
                        query
                    )

                    # --------------------------------------------------
                    # DETERMINISTIC COMMAND SUCCESS
                    # --------------------------------------------------

                    if handled:

                        state.thinking = False

                        state.set_response(
                            "Done"
                        )

                        state.set_status(
                            state.JarvisStatus.SPEAKING
                        )

                        self.update_hud_status(
                            "SPEAKING"
                        )

                        logger.info(
                            "Command executed successfully: %s",
                            query,
                        )

                        speak(
                            "Done"
                        )

                        continue

                    # --------------------------------------------------
                    # UNKNOWN COMMAND → AI BRAIN
                    # --------------------------------------------------

                    logger.info(
                        "Deterministic handler did not recognize "
                        "command. Sending to AI: %s",
                        query,
                    )

                    state.set_status(
                        state.JarvisStatus.THINKING
                    )

                    self.update_hud_status(
                        "AI THINKING"
                    )

                    # Keep thinking=True while the AI is processing.
                    state.thinking = True

                    # --------------------------------------------------
                    # CALL OLLAMA / AI BRAIN
                    # --------------------------------------------------

                    ai_response = ask_ai(
                        query,
                        speak_response=True,
                    )

                    # --------------------------------------------------
                    # AI SUCCESS
                    # --------------------------------------------------

                    if ai_response:

                        state.thinking = False

                        state.set_response(
                            ai_response
                        )

                        state.set_status(
                            state.JarvisStatus.SPEAKING
                        )

                        self.update_hud_status(
                            "AI RESPONSE"
                        )

                        logger.info(
                            "AI successfully handled command"
                        )

                    # --------------------------------------------------
                    # AI FAILURE
                    # --------------------------------------------------

                    else:

                        state.thinking = False

                        state.set_response(
                            "I could not process that request."
                        )

                        state.set_status(
                            state.JarvisStatus.IDLE
                        )

                        self.update_hud_status(
                            "UNKNOWN COMMAND"
                        )

                        logger.warning(
                            "AI returned no response for: %s",
                            query,
                        )

                        speak(
                            "Sorry sir, "
                            "I could not process that request."
                        )

                # ------------------------------------------------------
                # COMMAND / AI ERROR
                # ------------------------------------------------------

                except Exception as exc:

                    state.thinking = False

                    state.set_error(
                        str(exc)
                    )

                    state.set_status(
                        state.JarvisStatus.ERROR
                    )

                    logger.exception(
                        "Error while processing command: %s",
                        query,
                    )

                    self.update_hud_status(
                        "ERROR"
                    )

                    try:

                        speak(
                            "Sorry sir, "
                            "I encountered an error."
                        )

                    except Exception:

                        logger.exception(
                            "Failed to speak error message"
                        )

        except Exception as exc:

            logger.exception(
                "Fatal error in voice loop"
            )

            state.thinking = False

            state.set_error(
                str(exc)
            )

            state.set_status(
                state.JarvisStatus.ERROR
            )

            self.update_hud_status(
                "ERROR"
            )

        finally:

            state.thinking = False

            logger.info(
                "Voice loop stopped"
            )

    # ==================================================================
    # HUD
    # ==================================================================

    def update_hud_status(
        self,
        status: str,
    ):
        """
        Safely update the HUD status.

        HUD failures must never crash the
        voice-processing system.
        """

        if self.hud_dashboard is None:
            return

        try:

            self.hud_dashboard.update_status(
                status
            )

        except Exception:

            logger.exception(
                "Failed to update HUD status: %s",
                status,
            )

    # ==================================================================
    # STOP
    # ==================================================================

    def stop(self):
        """Stop JARVIS gracefully."""

        if not self.running:

            logger.debug(
                "JARVIS is already stopped"
            )

            self._cleanup_resources()

            return

        logger.info(
            "Stopping JARVIS..."
        )

        # --------------------------------------------------------------
        # 1. STOP MAIN APPLICATION LOOP
        # --------------------------------------------------------------

        self.running = False

        state.running = False
        state.awake = False
        state.thinking = False

        state.set_status(
            state.JarvisStatus.SHUTTING_DOWN
        )

        self.update_hud_status(
            "SHUTTING DOWN"
        )

        # --------------------------------------------------------------
        # 2. WAIT FOR VOICE LOOP
        # --------------------------------------------------------------

        if (
            self.voice_thread is not None
            and self.voice_thread.is_alive()
        ):

            logger.info(
                "Waiting for voice thread..."
            )

            self.voice_thread.join(
                timeout=6
            )

            if self.voice_thread.is_alive():

                logger.warning(
                    "Voice thread did not stop "
                    "within timeout"
                )

        # --------------------------------------------------------------
        # 3. STOP VOICE RECOGNITION
        # --------------------------------------------------------------

        if self.voice_started:

            try:

                logger.info(
                    "Stopping voice recognition..."
                )

                stop_voice()

            except Exception:

                logger.exception(
                    "Error stopping voice recognition"
                )

            finally:

                self.voice_started = False

        # --------------------------------------------------------------
        # 4. STOP HUD AUDIO MONITOR
        # --------------------------------------------------------------

        if self.audio_started:

            try:

                logger.info(
                    "Stopping HUD audio monitor..."
                )

                audio_input.stop()

            except Exception:

                logger.exception(
                    "Error stopping HUD audio monitor"
                )

            finally:

                self.audio_started = False

        # --------------------------------------------------------------
        # 5. STOP REGISTERED COMPONENTS
        # --------------------------------------------------------------

        self._stop_components()

        # --------------------------------------------------------------
        # 6. FINAL STATE
        # --------------------------------------------------------------

        state.set_status(
            state.JarvisStatus.IDLE
        )

        logger.info(
            "JARVIS stopped"
        )

    # ==================================================================
    # RESOURCE CLEANUP
    # ==================================================================

    def _cleanup_resources(self):
        """
        Emergency cleanup used when startup fails
        or when stop() is called before full startup.
        """

        # --------------------------------------------------------------
        # STOP VOICE
        # --------------------------------------------------------------

        if self.voice_started:

            try:

                logger.info(
                    "Cleaning up voice recognition..."
                )

                stop_voice()

            except Exception:

                logger.exception(
                    "Error during voice cleanup"
                )

            finally:

                self.voice_started = False

        # --------------------------------------------------------------
        # STOP AUDIO
        # --------------------------------------------------------------

        if self.audio_started:

            try:

                logger.info(
                    "Cleaning up HUD audio..."
                )

                audio_input.stop()

            except Exception:

                logger.exception(
                    "Error during audio cleanup"
                )

            finally:

                self.audio_started = False

        # --------------------------------------------------------------
        # STOP COMPONENTS
        # --------------------------------------------------------------

        self._stop_components()

    # ==================================================================
    # COMPONENT SHUTDOWN
    # ==================================================================

    def _stop_components(self):
        """Stop registered components in reverse order."""

        for (
            name,
            component,
        ) in reversed(
            list(
                self.components.items()
            )
        ):

            stop_method = getattr(
                component,
                "stop",
                None,
            )

            if not callable(
                stop_method
            ):
                continue

            try:

                logger.info(
                    "Stopping component: %s",
                    name,
                )

                stop_method()

            except Exception:

                logger.exception(
                    "Error stopping component: %s",
                    name,
                )

    # ==================================================================
    # SHUTDOWN
    # ==================================================================

    def shutdown(self):
        """Qt/application shutdown handler."""

        logger.info(
            "JARVIS shutdown requested"
        )

        self.stop()