#!/usr/bin/env bash
set -euo pipefail

cd /workspace
source venv/bin/activate

export ANSUX_HUD_HOST=127.0.0.1
export ANSUX_TEXT_ONLY=true
export ANSUX_OPEN_HUD_ON_START=false
export ANSUX_PUBLIC_URL="${ANSUX_PUBLIC_URL:-https://anshux.punah.pro}"

echo "Starting AnshuX backend on 127.0.0.1:${ANSUX_HUD_PORT:-8765}"
echo "Public URL: ${ANSUX_PUBLIC_URL}"
python -m ansux.server
