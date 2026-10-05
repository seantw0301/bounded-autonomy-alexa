#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
(cd backend && uv venv --python 3.12 .venv && uv pip install -p .venv -r requirements.txt)
(cd frontend && npm install)
