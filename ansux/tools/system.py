"""System control tools."""

from __future__ import annotations

import platform

if platform.system() == "Windows":
    import system_controller as _legacy
else:
    _legacy = None


def volume_up() -> None:
    if _legacy:
        _legacy.volume_up()


def volume_down() -> None:
    if _legacy:
        _legacy.volume_down()


def mute() -> None:
    if _legacy:
        _legacy.mute()


def take_screenshot() -> str | None:
    return _legacy.take_screenshot() if _legacy else None


def lock() -> None:
    if _legacy:
        _legacy.lock()


def sleep() -> None:
    if _legacy:
        _legacy.sleep()


def shutdown() -> None:
    if _legacy:
        _legacy.shutdown()


def restart() -> None:
    if _legacy:
        _legacy.restart()
