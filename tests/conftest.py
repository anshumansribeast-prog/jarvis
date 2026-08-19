"""Shared fixtures for Jarvis unit tests."""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Heavy optional deps (Piper / Whisper / PortAudio) and Windows-only
# modules are not required for command-routing tests. Stub them before
# any test imports jarvis.
for _name in (
    "piper",
    "faster_whisper",
    "sounddevice",
    "truststore",
    "win32api",
    "win32con",
    "win32gui",
    "pywintypes",
    "PIL",
    "PIL.ImageGrab",
):
    sys.modules.setdefault(_name, MagicMock())


@pytest.fixture
def facts_file(tmp_path, monkeypatch):
    path = tmp_path / "facts.json"
    monkeypatch.setattr("memory_controller.FACTS_PATH", str(path))
    return path


@pytest.fixture
def projects_file(tmp_path, monkeypatch):
    path = tmp_path / "projects.json"
    monkeypatch.setattr("memory_controller.PROJECTS_PATH", str(path))
    return path


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    """Point file_controller at a temp home with the usual known folders."""
    folders = {
        "downloads": str(tmp_path / "Downloads"),
        "documents": str(tmp_path / "Documents"),
        "desktop": str(tmp_path / "Desktop"),
        "pictures": str(tmp_path / "Pictures"),
    }
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
    monkeypatch.setattr("file_controller.HOME", str(tmp_path))
    monkeypatch.setattr("file_controller.KNOWN_FOLDERS", folders)
    monkeypatch.setattr("file_controller.DEFAULT_CREATE_DIR", folders["desktop"])
    return tmp_path, folders
