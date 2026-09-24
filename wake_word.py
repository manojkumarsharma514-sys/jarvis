import os
import sys
import time


def wake_word_detected(text: str, wake_word: str = "jarvis") -> bool:
    if not text:
        return False
    return wake_word.lower() in text.lower()


def listen_for_wake_word() -> str:
    print("[WAKE WORD] Listening for 'jarvis'...")
    while True:
        user_input = input("Voice input: ").strip()
        if wake_word_detected(user_input):
            return user_input
        time.sleep(0.2)


if __name__ == "__main__":
    text = listen_for_wake_word()
    print(f"Wake word detected: {text}")
