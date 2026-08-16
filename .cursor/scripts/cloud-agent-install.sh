#!/usr/bin/env bash
set -euo pipefail

cd /workspace

if [[ ! -d venv ]]; then
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p voices
VOICE_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium"

if [[ ! -f voices/en_US-lessac-medium.onnx ]]; then
  curl -fsSL -o voices/en_US-lessac-medium.onnx "${VOICE_BASE}/en_US-lessac-medium.onnx"
fi

if [[ ! -f voices/en_US-lessac-medium.onnx.json ]]; then
  curl -fsSL -o voices/en_US-lessac-medium.onnx.json "${VOICE_BASE}/en_US-lessac-medium.onnx.json"
fi

# Pre-download the Whisper model used at runtime so first boot is faster.
python - <<'PY'
from faster_whisper import WhisperModel

WhisperModel("base.en", device="cpu", compute_type="int8")
print("Whisper base.en model ready")
PY

python -m unittest tests.test_ansux_core -q
