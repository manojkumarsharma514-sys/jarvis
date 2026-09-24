from __future__ import annotations

import argparse
import sys

from hud_bridge import show_hud, update_hud
from main_agent import JarvisAgent
from memory import Memory


def run_cli(memory: Memory, with_hud: bool = False):
    agent = JarvisAgent(memory)
    print("JARVIS desktop agent online.")
    print("Type 'quit' to exit.")

    if with_hud:
        hud = show_hud()
        if hud is not None:
            hud.append_log("JARVIS desktop agent online")

    while True:
        try:
            user_input = input("You: ")
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        if user_input.strip().lower() in {"quit", "exit", "bye"}:
            print("JARVIS: Shutting down.")
            break

        if with_hud:
            update_hud("LISTENING", user_input)

        response = agent.process(user_input)

        if with_hud:
            update_hud("THINKING", user_input)
            update_hud("SPEAKING", user_input, response)

        print(f"JARVIS: {response}")


def main():
    parser = argparse.ArgumentParser(description="JARVIS desktop assistant")
    parser.add_argument("--hud", action="store_true", help="Launch the HUD window")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode")
    args = parser.parse_args()

    memory = Memory()
    try:
        if args.cli and not args.hud:
            run_cli(memory, with_hud=False)
        else:
            run_cli(memory, with_hud=args.hud)
    finally:
        memory.close()


if __name__ == "__main__":
    main()
