#!/usr/bin/env bash
set -euo pipefail

cd /workspace
# shellcheck disable=SC1091
source venv/bin/activate

python - <<'PY'
import os
import sys
import tempfile

import memory_controller
import requests
import sounddevice as sd
from faster_whisper import WhisperModel
from piper import PiperVoice

print("== memory controller ==")
memory_controller.remember("favorite color", "blue")
assert memory_controller.recall("favorite color") == "blue"
print("remember/recall OK")

print("== piper voice ==")
voice = PiperVoice.load("voices/en_US-lessac-medium.onnx")
chunks = list(voice.synthesize("Jarvis online."))
assert chunks, "expected synthesized audio chunks"
print(f"synthesized {len(chunks)} audio chunk(s)")

print("== whisper model ==")
model = WhisperModel("base.en", device="cpu", compute_type="int8")
assert model is not None
print("whisper model loaded")

print("== sounddevice ==")
devices = sd.query_devices()
print(f"found {len(devices)} audio device(s)")

print("== web lookup ==")
resp = requests.get(
    "https://api.duckduckgo.com/",
    params={"q": "Jupiter moons", "format": "json", "no_html": 1, "skip_disambig": 1},
    timeout=10,
)
resp.raise_for_status()
data = resp.json()
assert data is not None
print("duckduckgo API reachable")

print("== project config ==")
assert os.path.isfile("config/apps.json")
assert os.path.isfile("config/projects.json")
print("config files present")

print("ALL SMOKE TESTS PASSED")
PY
