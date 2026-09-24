from __future__ import annotations

import webbrowser
from pathlib import Path

import psutil

from tools.file_tools import read_file as read_file_tool


def open_app(app_name: str) -> str:
    import subprocess
    import sys

    alias = {
        "notepad": "notepad",
        "calculator": "calc",
        "chrome": "chrome",
        "explorer": "explorer",
        "terminal": "cmd",
        "files": "explorer",
    }
    target = alias.get((app_name or "").strip().lower(), app_name)
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
    return f"CPU: {cpu}%\nRAM: {ram}%\nDisk: {disk}%"


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        return f"I could not read that file. {exc}"


def dangerous_action(action_name: str) -> str:
    return f"{action_name} is a destructive action and requires explicit confirmation before I can do it."
