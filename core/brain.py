def think(command: str) -> dict:
    command = command.lower().strip()

    # OPEN ANY APPLICATION
    if command.startswith("open "):
        app_name = command.replace("open ", "").strip()
        return {"intent": "system", "action": "open app", "target": app_name}

    # SCREENSHOT
    if "screenshot" in command:
        return {"intent": "system", "action": "screenshot", "target": ""}

    # SEARCH
    if command.startswith("search "):
        query = command.replace("search ", "").strip()
        return {"intent": "web", "action": "search", "target": query}

    # OPEN DOWNLOADS
    if "downloads" in command:
        return {"intent": "files", "action": "open folder", "target": "C:\\Users\\admin\\Downloads"}

    # If none matched → AI intent
    return {"intent": "ai", "action": "chat", "target": command}
