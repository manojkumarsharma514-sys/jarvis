from __future__ import annotations

import os
import sys


def basic_ocr(path: str) -> str:
    """Placeholder OCR function.

    This provides a practical first stage for JARVIS screen understanding.
    In a real implementation, this would call Tesseract or a vision model.
    """
    if not os.path.exists(path):
        return "OCR failed: file not found."

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return text.strip() if text.strip() else "No text found in OCR input."
    except Exception as exc:
        return f"OCR failed: {exc}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(basic_ocr(sys.argv[1]))
    else:
        print("Usage: python ocr.py <text-file>")
