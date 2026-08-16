#!/usr/bin/env bash
set -euo pipefail

cd /workspace
source venv/bin/activate

export ANSUX_HUD_HOST=0.0.0.0
export ANSUX_TEXT_ONLY=true
export ANSUX_OPEN_HUD_ON_START=false

echo "Starting AnshuX server on http://0.0.0.0:${ANSUX_HUD_PORT:-8765}"
python -m ansux.server
