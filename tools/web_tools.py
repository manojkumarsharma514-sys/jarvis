from __future__ import annotations

from pathlib import Path


def list_directory(path: str = ".") -> str:
    try:
        p = Path(path)
        items = sorted([x.name for x in p.iterdir()])
        return "\n".join(items) if items else "Directory is empty."
    except Exception as exc:
        return f"I could not list that directory. {exc}"


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        return f"I could not read that file. {exc}"


def write_file(path: str, content: str) -> str:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Saved to {path}"
    except Exception as exc:
        return f"I could not write that file. {exc}"
