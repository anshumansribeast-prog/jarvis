"""Run AnshuX as a network-accessible server (text + optional voice)."""

from __future__ import annotations

import os

# Server mode binds to all interfaces by default.
os.environ.setdefault("ANSUX_HUD_HOST", "0.0.0.0")
os.environ.setdefault("ANSUX_TEXT_ONLY", "true")
os.environ.setdefault("ANSUX_OPEN_HUD_ON_START", "false")

from ansux.core.assistant import main

if __name__ == "__main__":
    main(voice_enabled=False)
