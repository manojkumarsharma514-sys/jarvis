from __future__ import annotations

import argparse
from typing import List

from hud_bridge import show_hud, update_hud
from main_agent import JarvisAgent
from memory import Memory
from planner import plan_task
from vision import capture_screenshot, describe_screen
from wake_word import wake_word_detected

try:
    from PyQt6.QtWidgets import QApplication
except Exception:  # pragma: no cover
    QApplication = None

try:
    from voice import listen_for_command, speak_response
except Exception:  # pragma: no cover
    listen_for_command = None
    speak_response = None


def _strip_wake_word(text: str) -> str:
    lower = text.lower()
    if "jarvis" in lower:
        return text[lower.index("jarvis") + len("jarvis") :].strip()
    return text.strip()


def _speak_if_enabled(text: str, enabled: bool) -> None:
    if not enabled or speak_response is None:
        return
    try:
        speak_response(text)
    except Exception:
        pass


def _listen_if_enabled(with_hud: bool = False) -> str | None:
    if listen_for_command is None:
        return None
    try:
        if with_hud:
            update_hud("LISTENING", "voice")
        return listen_for_command(timeout_seconds=8, phrase_time_limit=8)
    except Exception:
        return None


def _plan_and_execute(agent: JarvisAgent, user_input: str, with_hud: bool = False, speak: bool = False) -> str:
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

    if speak:
        _speak_if_enabled(response, True)

    return response


def run_cli(memory: Memory, with_hud: bool = False, require_wake_word: bool = True, enable_voice: bool = False):
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
                    update_hud("SPEAKING", text, "Shutting down.")
                    _speak_if_enabled("Shutting down.", enable_voice)
                    app = QApplication.instance()
                    if app is not None:
                        app.quit()
                    return

                update_hud("LISTENING", text)
                if require_wake_word and not wake_word_detected(text):
                    message = "Wake word required. Please say 'Jarvis' before your command."
                    update_hud("SPEAKING", text, message)
                    hud.append_log(f"USER> {text}")
                    hud.append_log(f"JARVIS> {message}")
                    _speak_if_enabled(message, enable_voice)
                    return

                response = _plan_and_execute(agent, text, with_hud=True, speak=enable_voice)
                if response == "shutdown":
                    _speak_if_enabled("Shutting down.", enable_voice)
                    app = QApplication.instance()
                    if app is not None:
                        app.quit()
                    return
                hud.append_log(f"USER> {text}")
                hud.append_log(f"JARVIS> {response}")
                print(f"JARVIS: {response}")

            hud.set_submit_callback(handle_hud_command)
            hud.command_input.setFocus()

            if enable_voice:
                hud.append_log("Voice input enabled. Use the command box or speak after 'Jarvis'.")

            app = QApplication.instance()
            if app is not None:
                app.exec()
            return

    while True:
        try:
            if enable_voice:
                user_input = _listen_if_enabled(with_hud=False)
                if user_input is None:
                    user_input = input("You: ")
            else:
                user_input = input("You: ")
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        if user_input is None:
            continue

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

        response = _plan_and_execute(agent, text, with_hud=with_hud, speak=enable_voice)
        if response == "shutdown":
            break

        print(f"JARVIS: {response}")


def main():
    parser = argparse.ArgumentParser(description="JARVIS desktop assistant")
    parser.add_argument("--hud", action="store_true", help="Launch the HUD window")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode")
    parser.add_argument("--voice", action="store_true", help="Enable microphone input and voice responses")
    parser.add_argument("--no-voice", action="store_false", dest="voice", help="Disable microphone input and speech output")
    parser.set_defaults(voice=True)
    args = parser.parse_args()

    memory = Memory()
    try:
        if args.cli and not args.hud:
            run_cli(memory, with_hud=False, require_wake_word=True, enable_voice=args.voice)
        else:
            run_cli(memory, with_hud=args.hud or True, require_wake_word=True, enable_voice=args.voice)
    finally:
        memory.close()


if __name__ == "__main__":
    main()



