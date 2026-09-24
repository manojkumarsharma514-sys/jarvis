from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QApplication

from hud import JarvisHUD, start_hud

_APP_INSTANCE: Optional[QApplication] = None
_HUD_INSTANCE: Optional[JarvisHUD] = None


def get_hud() -> Optional[JarvisHUD]:
    return _HUD_INSTANCE


def show_hud() -> Optional[JarvisHUD]:
    global _APP_INSTANCE, _HUD_INSTANCE
    _APP_INSTANCE, _HUD_INSTANCE = start_hud()
    _APP_INSTANCE.processEvents()
    return _HUD_INSTANCE


def update_hud(status: str, command: str = "", response: str = "") -> None:
    if _APP_INSTANCE is not None:
        _APP_INSTANCE.processEvents()
    if _HUD_INSTANCE is not None:
        _HUD_INSTANCE.update_status(status, command, response)
    if _APP_INSTANCE is not None:
        _APP_INSTANCE.processEvents()
