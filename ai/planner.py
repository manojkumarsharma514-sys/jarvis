from __future__ import annotations

import re
from typing import Any


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def route_command(raw_text: str) -> dict[str, Any]:
    text = normalize_text(raw_text)
    if not text:
        return {"tool": "chat", "args": {"prompt": ""}}

    if text.startswith("open "):
        app_name = text.replace("open ", "", 1).strip()
        return {"tool": "open_app", "args": {"app_name": app_name}}

    if text.startswith("search "):
        query = text.replace("search ", "", 1).strip()
        return {"tool": "search_web", "args": {"query": query}}

    if "screenshot" in text:
        return {"tool": "take_screenshot", "args": {}}

    if text.startswith("remember "):
        if " as " in text:
            left, right = text.replace("remember ", "", 1).split(" as ", 1)
            return {"tool": "remember_fact", "args": {"key": left.strip(), "value": right.strip()}}
        return {"tool": "chat", "args": {"prompt": raw_text}}

    if text.startswith("status"):
        return {"tool": "system_status", "args": {}}

    if text.startswith("read "):
        file_path = text.replace("read ", "", 1).strip()
        return {"tool": "read_file", "args": {"path": file_path}}

    if "time" in text:
        return {"tool": "time", "args": {}}

    if "date" in text:
        return {"tool": "date", "args": {}}

    return {"tool": "chat", "args": {"prompt": raw_text}}
