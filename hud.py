from __future__ import annotations

import argparse
from typing import List

from PyQt6.QtWidgets import QApplication

from hud_bridge import show_hud, update_hud
from main_agent import JarvisAgent
from memory import Memory
from planner import plan_task
from vision import capture_screenshot, describe_screen
from wake_word import wake_word_detected


def _strip_wake_word(text: str) -> str:
    lower = text.lower()
    if "jarvis" in lower:
        return text[lower.index("jarvis") + len("jarvis") :].strip()
    return text.strip()


def _plan_and_execute(agent: JarvisAgent, user_input: str, with_hud: bool = False) -> str:
    text = user_input.strip()
    if not text:
        return "I am listening."

    lower = text.lower()
    if lower in {"quit", "exit", "bye"}:
        return "shutdown"

    if not wake_word_detected(text):
        if "jarvis" not in lower:
            return "Wake word required. Please say 'Jarvis' before your command."

    normalized = _strip_wake_word(text)
    if with_hud:
        update_hud("PLANNING", text)

    plan: List[str] = plan_task(normalized or text)
    for step in plan:
        print(f"  {step}")

    if "screenshot" in lower or "screen" in lower or "vision" in lower:
        screenshot_path = capture_screenshot()
        vision_result = describe_screen(screenshot_path)
        print(f"JARVIS vision: {vision_result}")
        if with_hud:
            update_hud("VISION", text, vision_result)

    if with_hud:
        update_hud("THINKING", text)

    response = agent.process(text)

    if with_hud:
        update_hud("SPEAKING", text, response)

    return response


def run_cli(memory: Memory, with_hud: bool = False, require_wake_word: bool = True):
    agent = JarvisAgent(memory)
    print("JARVIS desktop agent online.")
    print("Type 'quit' to exit.")

    if with_hud:
        hud = show_hud()
        if hud is not None:
            hud.append_log("JARVIS desktop agent online")

            def handle_hud_command(user_text: str):
                text = user_text.strip()
                if not text:
                    return

                if text.lower() in {"quit", "exit", "bye"}:
                    hud.append_log("USER> quit")
                    hud.append_log("JARVIS> Shutting down.")
                    if QApplication.instance() is not None:
                        QApplication.instance().quit()
                    return

                update_hud("LISTENING", text)
                if require_wake_word and not wake_word_detected(text):
                    message = "Wake word required. Please say 'Jarvis' before your command."
                    update_hud("SPEAKING", text, message)
                    hud.append_log(f"USER> {text}")
                    hud.append_log(f"JARVIS> {message}")
                    return

                response = _plan_and_execute(agent, text, with_hud=True)
                if response == "shutdown":
                    if QApplication.instance() is not None:
                        QApplication.instance().quit()
                    return
                hud.append_log(f"USER> {text}")
                hud.append_log(f"JARVIS> {response}")
                print(f"JARVIS: {response}")

            hud.set_submit_callback(handle_hud_command)
            hud.command_input.setFocus()

            app = QApplication.instance()
            if app is not None:
                app.exec()
            return

    while True:
        try:
            user_input = input("You: ")
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        text = user_input.strip()
        if not text:
            continue

        if text.lower() in {"quit", "exit", "bye"}:
            print("JARVIS: Shutting down.")
            break

        if with_hud:
            update_hud("LISTENING", text)

        if require_wake_word and not wake_word_detected(text):
            print("JARVIS: Wake word required. Please say 'Jarvis' before your command.")
            continue

        response = _plan_and_execute(agent, text, with_hud=with_hud)
        if response == "shutdown":
            break

        print(f"JARVIS: {response}")


def main():
    parser = argparse.ArgumentParser(description="JARVIS desktop assistant")
    parser.add_argument("--hud", action="store_true", help="Launch the HUD window")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Require the wake word before processing commands.",
    )
    args = parser.parse_args()

    memory = Memory()
    try:
        if args.cli and not args.hud:
            run_cli(memory, with_hud=False, require_wake_word=args.voice or True)
        else:
            run_cli(memory, with_hud=args.hud, require_wake_word=args.voice or True)
    finally:
        memory.close()


if __name__ == "__main__":
    main()
