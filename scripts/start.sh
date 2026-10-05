#!/usr/bin/env bash
# Starts MCP (:8001), API (:8000), UI (:3000). Ctrl-C stops all.
set -e
cd "$(dirname "$0")/../backend"
trap 'kill 0' EXIT
.venv/bin/python -m mcp_server.server &
sleep 1
.venv/bin/uvicorn main:app --port 8000 &
(cd ../frontend && npm run dev) &
wait
