from __future__ import annotations

import os

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover
    sr = None

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None


def listen_for_command(timeout_seconds: int = 8, phrase_time_limit: int = 8) -> str | None:
    if sr is None:
        raise RuntimeError("speech_recognition is not installed")

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=timeout_seconds, phrase_time_limit=phrase_time_limit)

    try:
        transcript = recognizer.recognize_google(audio)
        return transcript.strip()
    except Exception:
        return None


def speak_response(text: str) -> None:
    if not text:
        return
    if pyttsx3 is None:
        raise RuntimeError("pyttsx3 is not installed")

    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    text = listen_for_command()
    if text:
        print(f"Heard: {text}")
