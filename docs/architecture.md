# Architecture (Level 1)

- UI (Next.js :3000) → `/api/*` rewrite → FastAPI (:8000)
- Orchestrator: parse intent → MCP `search_product` → Boundary Engine → token → MCP `purchase_product` → audit
- Boundary Engine (`backend/policy/engine.py`): deterministic, no LLM
- Authority token (`policy/token.py`): `AUTH-xxxx`, 60s TTL, single-use, bound to user/boundary/product, stored in SQLite
- MCP server (`backend/mcp_server`): FastMCP, Streamable HTTP :8001; verifies token before creating Order
- Memory (`backend/memory`): boundaries keyed by user, persisted in SQLite → survive sessions
- Invariant: ACTIVE boundary requires `created_by=HUMAN` (SQLAlchemy listener + approve endpoint requires `actor=HUMAN`)
- Agent may only create `PROPOSED` boundaries; expansion attempts → `AUTHORITY_EXPANSION_REJECTED`

## Deviations from plan
- `backend/mcp/` renamed `backend/mcp_server/` (shadows the `mcp` SDK)
- Intent parser is rule-based (no LLM key needed; LLM never authorizes anyway)
- `mcp<2` pinned (v2 renamed FastMCP)
