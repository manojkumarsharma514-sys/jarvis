from __future__ import annotations

import base64
import os
import sys
from pathlib import Path


def capture_screenshot(path: str = "latest_screenshot.png") -> str:
    try:
        import pyautogui

        image_path = Path(path)
        pyautogui.screenshot(str(image_path))
        return str(image_path.resolve())
    except Exception as exc:
        return f"Screenshot failed: {exc}"


def image_to_base64(path: str) -> str:
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"Could not read image: {exc}")


def describe_screen(path: str = "latest_screenshot.png") -> str:
    """Basic screen-analysis placeholder.

    This mimics the first stage of a vision-enabled JARVIS: capture a screenshot,
    then describe that the image exists and can be analyzed by an OCR or CV model.
    """

    image_path = capture_screenshot(path)
    if image_path.startswith("Screenshot failed"):
        return image_path

    try:
        encoded = image_to_base64(image_path)
        return (
            f"Screen captured successfully at {image_path}. "
            f"Image data length: {len(encoded)} bytes. "
            f"This image is ready for OCR or CV analysis."
        )
    except Exception as exc:
        return f"Screen captured, but analysis failed: {exc}"
