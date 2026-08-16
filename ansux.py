"""AnshuX entry point — opens Personal AI in the browser."""

from __future__ import annotations

import os

os.environ.setdefault("ANSUX_TEXT_ONLY", "true")
os.environ.setdefault("ANSUX_OPEN_HUD_ON_START", "true")
os.environ.setdefault("ANSUX_PUBLIC_URL", "http://127.0.0.1:8765")
os.environ.setdefault("ANSUX_HUD_HOST", "127.0.0.1")

from ansux.core.assistant import main

if __name__ == "__main__":
    main(voice_enabled=False)
