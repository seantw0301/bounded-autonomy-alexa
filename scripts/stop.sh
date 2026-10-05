#!/usr/bin/env bash
# Stops MCP (:8001), API (:8000), UI (:3000/3001).
for p in 8001 8000 3000 3001; do
  pids=$(lsof -ti tcp:$p -sTCP:LISTEN 2>/dev/null)
  [ -n "$pids" ] && kill $pids && echo "stopped :$p ($pids)"
done
pkill -f "frontend/node_modules/.bin/next" 2>/dev/null
exit 0
