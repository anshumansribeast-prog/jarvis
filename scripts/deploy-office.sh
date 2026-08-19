#!/usr/bin/env bash
# Start ANSHUX Command Office for server deploy (0.0.0.0:8765).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -U pip pytest
fi

export ANSHUX_OFFICE_HOST="${ANSHUX_OFFICE_HOST:-0.0.0.0}"
export ANSHUX_OFFICE_NO_BROWSER="${ANSHUX_OFFICE_NO_BROWSER:-1}"
export ANSHUX_ABHISHEK_EMAIL="${ANSHUX_ABHISHEK_EMAIL:-abhiis@eleven11.pro}"

echo "ANSHUX Command Office"
echo "  host=$ANSHUX_OFFICE_HOST"
echo "  mail=$ANSHUX_ABHISHEK_EMAIL"
echo "  open http://SERVER_IP:8765/  (and /command/)"
echo "  DEPLOY.md has nginx/systemd/Docker steps"
echo

exec .venv/bin/python team.py office
