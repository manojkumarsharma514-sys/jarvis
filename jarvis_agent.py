from __future__ import annotations

import webbrowser


def search_web(query: str) -> str:
    q = (query or "").strip()
    if not q:
        return "Please provide a search term."
    webbrowser.open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
    return f"Searching the web for: {q}"
