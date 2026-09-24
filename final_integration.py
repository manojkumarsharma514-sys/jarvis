from __future__ import annotations

from typing import List

from main_agent import JarvisAgent
from memory import Memory
from planner import plan_task
from vision import capture_screenshot, describe_screen
from wake_word import wake_word_detected


def run_final_integration(memory: Memory | None = None, with_hud: bool = False):
    agent = JarvisAgent(memory or Memory())
    print("JARVIS final integration online.")
    print("Say 'Jarvis' followed by a command.")

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

        if not wake_word_detected(text):
            if "jarvis" not in text.lower():
                print("JARVIS: Wake word required. Please say 'Jarvis' before your command.")
                continue

        plan: List[str] = plan_task(text)
        for step in plan:
            print(f"  {step}")

        if "screenshot" in text.lower() or "screen" in text.lower() or "vision" in text.lower():
            screenshot_path = capture_screenshot()
            vision_result = describe_screen(screenshot_path)
            print(f"JARVIS vision: {vision_result}")

        response = agent.process(text)
        print(f"JARVIS: {response}")


if __name__ == "__main__":
    run_final_integration()
