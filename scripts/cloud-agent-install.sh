#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -q pytest
.venv/bin/python -c "import pytest; print('pytest', pytest.__version__)"
