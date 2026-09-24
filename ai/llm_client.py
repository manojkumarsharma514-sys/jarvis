from __future__ import annotations

import json
import os
import time
from typing import Any, Optional

import requests

from config import OLLAMA_HOST, OLLAMA_MODEL


SYSTEM_PROMPT = """
You are JARVIS, an advanced personal AI assistant.
Keep replies short and natural.
When a user asks to do a task, prefer actionable, direct responses.
You can call tools like open_app, search_web, system_status, take_screenshot, read_file, remember_fact.
Do not claim to perform actions that are not allowed.
"""


def ask_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout: tuple[int, int] = (5, 30)) -> Optional[str]:
    try:
        response = requests.post(
            f"{OLLAMA_HOST.rstrip('/')}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 180,
                },
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        text = (payload.get("response") or "").strip()
        return text or None
    except Exception:
        return None


def ask_jarvis(prompt: str) -> str:
    answer = ask_ollama(prompt)
    if answer:
        return answer
    if "hello" in prompt.lower() or "hi" in prompt.lower():
        return "Hello, sir. JARVIS is online and ready."
    if "who are you" in prompt.lower():
        return "I am JARVIS, your local AI assistant."
    return "I understand. I can help with basic system tasks, file access, web searching, and memory."
