#!/usr/bin/env bash
# Builds UI (prod mode, no dev overlay), starts services, records demo, stops services.
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
if [ "$NARRATE" = "1" ]; then python3 scripts/narration.py prep; export DEMO_NARRATE=1; fi
{ echo "run: $(date -u +%FT%TZ)"; (cd demo && npx playwright test) ; } 2>&1 | tee artifacts/demo-run.log
[ "$NARRATE" = "1" ] && python3 scripts/narration.py mux || true
