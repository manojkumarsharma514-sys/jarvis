from __future__ import annotations

import sys
from typing import Optional

from ai.planner import ask_jarvis
from ai.planner import route_command
from config import WAKE_WORD
from core.safety import handle_confirmation, is_destructive_action, request_confirmation
from memory import Memory
from tools.system_tools import dangerous_action, open_app, read_file, search_web, system_status, take_screenshot


class JarvisAgent:
    def __init__(self, memory: Optional[Memory] = None):
        self.memory = memory or Memory()
        self.awake = False

    def process(self, user_input: str) -> str:
        text = (user_input or "").strip()
        if not text:
            return "I am listening."

        lower = text.lower()

        if "confirm " in lower or lower in {"cancel", "cancel action", "abort"}:
            confirmed, action = handle_confirmation(text)
            if action == "cancelled":
                return "Action cancelled."
            if action in {"shutdown", "restart", "close_app", "delete_file", "taskkill"}:
                return f"Confirmed {action}. Execution would occur here."
            if action == "noop":
                return "No pending action to confirm."

        if WAKE_WORD in lower and not self.awake:
            self.awake = True
            return "Yes, sir. JARVIS is online."

        if lower in {"sleep", "go to sleep", "sleep mode"}:
            self.awake = False
            return "Going to sleep."

        if not self.awake:
            return "Say 'Jarvis' to activate me."

        if lower.startswith("jarvis"):
            text = text[len(WAKE_WORD):].strip()

        route = route_command(text)
        tool = route.get("tool")
        args = route.get("args", {})

        if is_destructive_action(text):
            action_name = "shutdown" if "shutdown" in lower else "restart" if "restart" in lower else "close_app"
            request_confirmation(action_name, text)
            return "This action is destructive and requires confirmation."

        if tool == "open_app":
            return open_app(args.get("app_name", ""))

        if tool == "search_web":
            return search_web(args.get("query", ""))

        if tool == "take_screenshot":
            return take_screenshot()

        if tool == "system_status":
            return system_status()

        if tool == "read_file":
            return read_file(args.get("path", ""))

        if tool == "remember_fact":
            key = args.get("key", "")
            value = args.get("value", "")
            self.memory.set(key, value)
            return f"Saved: {key}"

        if tool == "time":
            from datetime import datetime
            return datetime.now().strftime("The time is %I:%M %p.")

        if tool == "date":
            from datetime import datetime
            return datetime.now().strftime("Today is %A, %B %d, %Y.")

        response = ask_jarvis(text)
        self.memory.add_history(text, response)
        return response


if __name__ == "__main__":
    agent = JarvisAgent()
    print("JARVIS AGENT LOOP ONLINE")
    while True:
        try:
            user_input = input("You: ")
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break
        print(f"JARVIS: {agent.process(user_input)}")
