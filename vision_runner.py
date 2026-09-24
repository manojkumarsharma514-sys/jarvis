from __future__ import annotations

import os
import sys

from vision import describe_screen


def analyze_active_screen() -> str:
    return describe_screen("latest_screenshot.png")


if __name__ == "__main__":
    print(analyze_active_screen())
