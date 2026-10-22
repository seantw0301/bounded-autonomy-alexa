#!/usr/bin/env bash
# Starts the app (prod build), captures raw UI shots, composes AON-style Devpost images, stops the app.
set -e
cd "$(dirname "$0")/.."
mkdir -p artifacts
scripts/stop.sh >/dev/null 2>&1 || true
(cd frontend && npm run build >/dev/null)
(cd backend && .venv/bin/python -m mcp_server.server >../artifacts/mcp.log 2>&1 &)
sleep 1
(cd backend && .venv/bin/uvicorn main:app --port 8000 >../artifacts/api.log 2>&1 &)
(cd frontend && npx next start -p 3000 >../artifacts/ui.log 2>&1 &)
trap 'scripts/stop.sh >/dev/null 2>&1' EXIT
for i in $(seq 40); do curl -sf localhost:3000 >/dev/null && curl -sf localhost:8000/api/boundaries >/dev/null && break; sleep 0.5; done
(cd demo && node capture-shots.mjs)
python3 scripts/aon_shots.py
