"""Filesystem tools — wraps file_controller with cross-platform guards."""

from __future__ import annotations

import os
import platform
import subprocess

if platform.system() == "Windows":
    import file_controller as _legacy
else:
    _legacy = None


def open_known_folder(name: str) -> bool:
    if _legacy is None:
        return False
    return _legacy.open_known_folder(name)


def open_path(path: str) -> None:
    if platform.system() == "Windows" and _legacy:
        _legacy.open_path(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def create_folder(name: str) -> str | None:
    if _legacy is None:
        return None
    return _legacy.create_folder(name)


def create_file(name: str) -> str | None:
    if _legacy is None:
        return None
    return _legacy.create_file(name)


def find(name: str, limit: int = 5) -> list[str]:
    if _legacy is None:
        return []
    return _legacy.find(name, limit=limit)


def read_text_file(path: str, max_chars: int = 800) -> tuple[str, bool]:
    if _legacy is None:
        return "", False
    return _legacy.read_text_file(path, max_chars=max_chars)


def rename(path: str, new_name: str) -> str | None:
    if _legacy is None:
        return None
    return _legacy.rename(path, new_name)


def move(path: str, dest_folder_key: str) -> str | None:
    if _legacy is None:
        return None
    return _legacy.move(path, dest_folder_key)


def delete(path: str) -> None:
    if _legacy is None:
        raise OSError("Delete not available on this platform")
    _legacy.delete(path)
