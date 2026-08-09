# hud/audio_input.py

import logging
import threading
import time

import numpy as np
import sounddevice as sd


logger = logging.getLogger(__name__)


class AudioInput:
    """
    Microphone audio monitor used by the JARVIS HUD.

    M1.3:
    - Does not open the microphone during import.
    - Explicit start/stop lifecycle.
    - Safe repeated start/stop.
    - Audio errors are contained.
    """

    def __init__(self, device=None, samplerate=44100, blocksize=1024):
        self.level = 0.0
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.device = device
        self.stream = None
        self.running = False

        self._lock = threading.Lock()

    def start(self):
        """Start the HUD audio monitor."""

        with self._lock:
            if self.running:
                logger.debug("HUD audio input already running")
                return

            try:
                self.stream = sd.InputStream(
                    device=self.device,
                    channels=1,
                    callback=self.audio_callback,
                    blocksize=self.blocksize,
                    samplerate=self.samplerate,
                )

                self.stream.start()
                self.running = True

                logger.info("HUD audio input started")

            except Exception:
                self.stream = None
                self.running = False

                logger.exception(
                    "Failed to start HUD audio input"
                )

        return self

    def stop(self):
        """Stop and release the HUD audio monitor."""

        with self._lock:
            if self.stream is None:
                self.running = False
                self.level = 0.0
                return

            try:
                self.stream.stop()
                self.stream.close()
                logger.info("HUD audio input stopped")

            except Exception:
                logger.exception(
                    "Error while stopping HUD audio input"
                )

            finally:
                self.stream = None
                self.running = False
                self.level = 0.0

    def audio_callback(self, indata, frames, time_info, status):
        """Receive microphone samples for HUD visualization."""

        if status:
            logger.debug(
                "Audio input status: %s",
                status,
            )

        try:
            self.level = float(np.linalg.norm(indata))

        except Exception:
            logger.exception(
                "Error processing audio input"
            )

    def read_level(self):
        """Return the current microphone level."""
        return self.level

    def push_level(self, value, decay_ms=300):
        """
        Temporarily boost the HUD audio level.

        Used by the voice-recognition system to provide
        visual activity feedback.
        """

        self.level = float(value)

        def decay():
            time.sleep(decay_ms / 1000)

            # Only reset if the real microphone isn't
            # currently producing a meaningful level.
            if self.level == float(value):
                self.level = 0.0

        threading.Thread(
            target=decay,
            daemon=True,
            name="AudioLevelDecay",
        ).start()


# Global instance preserved for compatibility.
#
# IMPORTANT:
# This no longer opens the microphone automatically.
audio_input = AudioInput()