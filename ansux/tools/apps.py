"""Application launch/close tools."""

from __future__ import annotations

import platform

if platform.system() == "Windows":
    import app_controller as _legacy
else:
    _legacy = None


def launch_app(name: str) -> bool:
    if _legacy is None:
        return False
    return _legacy.launch_app(name)


def close_app(name: str) -> bool:
    if _legacy is None:
        return False
    return _legacy.close_app(name)
