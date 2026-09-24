from __future__ import annotations

import json
import os
import subprocess
import sys
import webbrowser
from typing import Any

import psutil


def open_app(app_name: str) -> str:
    name = (app_name or "").strip().lower()
    aliases = {
        "notepad": "notepad",
        "calculator": "calc",
        "chrome": "chrome",
        "explorer": "explorer",
        "cmd": "cmd",
        "terminal": "cmd",
        "files": "explorer",
    }
    target = aliases.get(name, name)
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(target)
        else:
            subprocess.Popen(["open", target] if sys.platform == "darwin" else ["xdg-open", target])
        return f"Opening {app_name}."
    except Exception as exc:
        return f"I could not open {app_name}. {exc}"


def search_web(query: str) -> str:
    q = (query or "").strip()
    if not q:
        return "Please provide a search term."
    webbrowser.open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
    return f"Searching the web for: {q}"


def take_screenshot(path: str = "screenshot.png") -> str:
    try:
        import pyautogui

        pyautogui.screenshot(path)
        return f"Screenshot saved to {path}"
    except Exception as exc:
        return f"I could not take a screenshot. {exc}"


def system_status() -> str:
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return (
        f"CPU: {cpu}%\n"
        f"RAM: {ram}%\n"
        f"Disk: {disk}%"
    )


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        return f"I could not read that file. {exc}"


def remember_fact(key: str, value: str, memory) -> str:
    if not key or not value:
        return "Please provide both a key and a value."
    memory.set(key.strip(), value.strip())
    return f"Saved: {key.strip()}"


def debug_tool_response(tool_name: str, payload: dict[str, Any]) -> str:
    return f"Tool {tool_name} executed with args: {json.dumps(payload, ensure_ascii=True)}"
