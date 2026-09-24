from __future__ import annotations

from typing import Optional

from hud import JarvisHUD, start_hud

_HUD_INSTANCE: Optional[JarvisHUD] = None


def get_hud() -> Optional[JarvisHUD]:
    global _HUD_INSTANCE
    return _HUD_INSTANCE


def show_hud() -> Optional[JarvisHUD]:
    global _HUD_INSTANCE
    app, window = start_hud()
    _HUD_INSTANCE = window
    return window


def update_hud(status: str, command: str = "", response: str = "") -> None:
    if _HUD_INSTANCE is not None:
        _HUD_INSTANCE.update_status(status, command, response)
