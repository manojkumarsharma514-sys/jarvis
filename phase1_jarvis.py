#!/usr/bin/env python3
"""Phase 1 JARVIS prototype.

This is a working starter that gives the project:
- a local AI fallback path via Ollama
- a tool layer for safe actions
- conversational memory in SQLite
- optional voice input/output using speech recognition and pyttsx3
- a simple loop that behaves like a desktop JARVIS assistant
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover
    sr = None

try:
    import pyautogui
except Exception:  # pragma: no cover
    pyautogui = None


PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "jarvis_memory.db"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "phi3:mini"


def log(message: str) -> None:
    print(f"[JARVIS] {message}")


class Memory:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def set(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO memory(key, value, updated_at) VALUES(?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            (key, value, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT value FROM memory WHERE key = ?",
            (key,),
        ).fetchone()
        return row[0] if row else None

    def remember(self, key: str, value: str) -> str:
        self.set(key, value)
        return f"Remembered: {key}"

    def add_history(self, user_message: str, assistant_message: str) -> None:
        self.conn.execute(
            "INSERT INTO history(user_message, assistant_message, created_at) VALUES(?, ?, ?)",
            (user_message, assistant_message, datetime.now().isoformat()),
        )
        self.conn.commit()

    def recent_history(self, limit: int = 5) -> list[tuple[str, str]]:
        rows = self.conn.execute(
            "SELECT user_message, assistant_message FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return list(reversed(rows))

    def close(self) -> None:
        self.conn.close()


def speak(text: str) -> bool:
    if not text or pyttsx3 is None:
        return False
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as exc:  # pragma: no cover
        print(f"TTS failed: {exc}")
        return False


def listen_once() -> str:
    if sr is None:
        return ""
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            log("Listening...")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
        return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except Exception:  # pragma: no cover
        return ""


def ollama_available() -> bool:
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def ask_ollama(prompt: str) -> Optional[str]:
    if not ollama_available():
        return None
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 180,
        },
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=(5, 30))
        response.raise_for_status()
        data = response.json()
        result = (data.get("response") or "").strip()
        return result if result else None
    except Exception:
        return None


def normalize_command(raw: str) -> str:
    text = raw.lower().strip()
    text = text.replace("jarvis", "").strip()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def open_app(app_name: str) -> str:
    app_name = app_name.strip().lower()
    aliases = {
        "notepad": "notepad",
        "calculator": "calc",
        "chrome": "chrome",
        "edge": "msedge",
        "explorer": "explorer",
        "files": "explorer",
        "cmd": "cmd",
        "terminal": "cmd",
    }
    target = aliases.get(app_name, app_name)
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(target)
        else:
            subprocess.Popen(["open", target] if sys.platform == "darwin" else ["xdg-open", target])
        return f"Opening {app_name}"
    except Exception as exc:
        return f"I couldn't open {app_name}. {exc}"


def search_web(query: str) -> str:
    url = "https://www.google.com/search?q=" + requests.utils.quote(query)
    webbrowser.open(url)
    return f"Searching the web for: {query}"


def take_screenshot() -> str:
    if pyautogui is None:
        return "Screenshot support is not available because pyautogui is not installed."
    try:
        path = PROJECT_ROOT / "screenshot.png"
        pyautogui.screenshot(str(path))
        return f"Screenshot saved to {path}"
    except Exception as exc:
        return f"I couldn't take a screenshot. {exc}"


def command_router(command: str, memory: Memory) -> str:
    command = normalize_command(command)
    if not command:
        return "I am listening."

    if command in {"hello", "hi", "hey"}:
        return "Hello, sir. JARVIS is online and ready."

    if command in {"time", "what time is it", "current time"}:
        return datetime.now().strftime("The time is %I:%M %p.")

    if command in {"date", "today"}:
        return datetime.now().strftime("Today is %A, %B %d, %Y.")

    if command.startswith("open "):
        app_name = command.replace("open ", "", 1)
        return open_app(app_name)

    if command.startswith("search "):
        query = command.replace("search ", "", 1)
        return search_web(query)

    if command.startswith("remember "):
        key, _, value = command.replace("remember ", "", 1).partition(" as ")
        if not value:
            return "Use the format: remember <key> as <value>"
        return memory.remember(key.strip(), value.strip())

    if command.startswith("what do you remember"):
        key = command.replace("what do you remember", "", 1).strip()
        if key:
            value = memory.get(key)
            return value if value else f"I do not remember anything called '{key}'."
        return "I remember a few things, but not much yet."

    if command.startswith("remember this "):
        item = command.replace("remember this ", "", 1).strip()
        return memory.remember("general_note", item)

    if command.startswith("screenshot"):
        return take_screenshot()

    if command.startswith("status"):
        memory_count = memory.conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
        return f"I am online, and I have {memory_count} remembered items."

    if command.startswith("shutdown") or command.startswith("restart"):
        return "That is a destructive action. I need your confirmation before I can do that."

    if command.startswith("close "):
        return "I can open applications, but I will not force-close things without your explicit confirmation."

    return None


def fallback_response(prompt: str) -> str:
    prompt = prompt.strip()
    if not prompt:
        return "I am listening."
    if any(word in prompt for word in ["who are you", "what are you"]):
        return "I am JARVIS, your local personal assistant."
    if any(word in prompt for word in ["hello", "hi", "hey"]):
        return "Hello, sir. I am ready to help."
    if any(word in prompt for word in ["thank", "thanks"]):
        return "You are welcome, sir."
    return "I understand. I can open apps, search the web, remember facts, and help with basic tasks."


def ask_ai(prompt: str) -> str:
    response = ask_ollama(prompt)
    if response:
        return response
    return fallback_response(prompt)


def interactive_loop() -> None:
    memory = Memory(DB_PATH)
    try:
        log("JARVIS online. Say something or type a command.")
        speak("Jarvis online")
        awake = False

        while True:
            try:
                if sys.stdin.isatty():
                    raw_input = input("\nYou: ")
                else:
                    raw_input = input("\nYou: ")
            except EOFError:
                print("\nGoodbye.")
                break

            if not raw_input.strip():
                continue

            command = raw_input.strip()
            lower = command.lower()

            if "jarvis" in lower and not awake:
                awake = True
                speak("Yes, sir.")
                print("JARVIS: Yes, sir.")
                continue

            if lower in {"sleep", "go to sleep", "sleep mode"}:
                awake = False
                speak("Going to sleep.")
                print("JARVIS: Going to sleep.")
                continue

            if not awake:
                if not lower.startswith("jarvis"):
                    continue
                command = command.replace("jarvis", "", 1).strip()

            user_command = command
            tool_result = command_router(user_command, memory)

            if tool_result is None:
                response = ask_ai(user_command)
            else:
                response = tool_result

            print(f"JARVIS: {response}")
            memory.add_history(user_command, response)
            speak(response)
    finally:
        memory.close()


if __name__ == "__main__":
    interactive_loop()
