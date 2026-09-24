from __future__ import annotations

import re
from typing import List


def plan_task(user_request: str) -> List[str]:
    text = (user_request or "").strip()
    if not text:
        return ["Ask for a task."]

    request = text.lower()
    steps: List[str] = []

    if "open" in request or "launch" in request:
        steps.append("1. Identify the requested application or document.")
        steps.append("2. Confirm the target is allowed and safe to open.")
        steps.append("3. Launch the app or file.")

    if "search" in request or "find" in request:
        steps.append("1. Extract the search query.")
        steps.append("2. Perform the web search.")
        steps.append("3. Return the top results or relevant information.")

    if "remember" in request:
        steps.append("1. Parse the key and value to save.")
        steps.append("2. Store the fact in persistent memory.")
        steps.append("3. Confirm the memory was saved.")

    if "status" in request:
        steps.append("1. Check system health and activity.")
        steps.append("2. Read current CPU/RAM/disk status.")
        steps.append("3. Return the summary.")

    if "screenshot" in request or "screen" in request:
        steps.append("1. Capture a screenshot of the current display.")
        steps.append("2. Save the image.")
        steps.append("3. Optionally analyze the screenshot or OCR the result.")

    if not steps:
        steps = [
            "1. Parse the user intent.",
            "2. Select the right tool or AI action.",
            "3. Execute the task safely.",
            "4. Present the result back to the user.",
        ]

    return steps


if __name__ == "__main__":
    example = "Jarvis open chrome and search for python tutorials"
    print("\n".join(plan_task(example)))
