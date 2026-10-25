#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
npm ci --ignore-scripts --no-audit --no-fund --cache /workspace/.cache/npm
python -m venv .venv
.venv/bin/python -m pip install --cache-dir /workspace/.cache/pip -r requirements-test.txt
.venv/bin/python tools/build.py --check
test -x "${CHROMIUM_PATH:-/usr/bin/chromium}"
command -v pdftotext >/dev/null
