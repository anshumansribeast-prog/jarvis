"""Windows window management tools."""

from __future__ import annotations

import platform

if platform.system() == "Windows":
    import window_controller as _legacy
else:
    _legacy = None


def switch_to(name: str) -> bool:
    return _legacy.switch_to(name) if _legacy else False


def minimize_active_window() -> None:
    if _legacy:
        _legacy.minimize_active_window()


def maximize_active_window() -> None:
    if _legacy:
        _legacy.maximize_active_window()


def restore_active_window() -> None:
    if _legacy:
        _legacy.restore_active_window()


def show_desktop() -> None:
    if _legacy:
        _legacy.show_desktop()
