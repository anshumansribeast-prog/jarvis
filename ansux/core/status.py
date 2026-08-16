"""Live system status for HUD and spoken reports."""

from __future__ import annotations

import platform
import shutil
import sys
from typing import Any

import requests

from ansux.config import settings
from ansux.core import modes

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover
    sd = None


def _ollama_online() -> bool:
    try:
        base = settings.OLLAMA_URL.rsplit("/api/", 1)[0]
        resp = requests.get(f"{base}/api/tags", timeout=2)
        return resp.ok
    except requests.RequestException:
        return False


def _mic_status() -> str:
    if sd is None:
        return "OFFLINE"
    try:
        devices = sd.query_devices()
        inputs = [d for d in devices if d.get("max_input_channels", 0) > 0]
        return "ONLINE" if inputs else "OFFLINE"
    except Exception:
        return "OFFLINE"


def snapshot(voice_ready: bool = False, memory_ready: bool = True) -> dict[str, Any]:
    cpu = psutil.cpu_percent(interval=0.1) if psutil else None
    mem = psutil.virtual_memory().percent if psutil else None
    return {
        "assistant": settings.ASSISTANT_NAME,
        "user": settings.USER_NAME,
        "platform": platform.system(),
        "python": sys.version.split()[0],
        "mode": modes.current_mode().value,
        "status": {
            "online": "ONLINE",
            "voice": "ONLINE" if voice_ready else "OFFLINE",
            "memory": "ONLINE" if memory_ready else "OFFLINE",
            "ai": "ONLINE" if _ollama_online() else "OFFLINE",
            "tools": "ONLINE" if platform.system() == "Windows" else "PARTIAL",
            "microphone": _mic_status(),
        },
        "system": {
            "cpu_percent": cpu,
            "memory_percent": mem,
            "disk_free_gb": round(shutil.disk_usage("/").free / (1024 ** 3), 1)
            if platform.system() != "Windows"
            else None,
        },
    }
