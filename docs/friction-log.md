# Friction Log

Only issues actually hit while building this project.

| Area | Friction | Impact | Workaround | Suggested Improvement |
|---|---|---|---|---|
| MCP SDK versions | `pip install mcp` pulled v2, which renamed `FastMCP` → `MCPServer` and moved modules; v1 examples fail with `No module named 'mcp.server.fastmcp'` | Server wouldn't import on first try | Pinned `mcp<2` | Version-pinned quickstarts; keep a v1→v2 snippet in the main README |
| Project layout | The spec's `backend/mcp/` package shadows the `mcp` SDK on import | Confusing import errors risk | Renamed to `backend/mcp_server/` | Docs warning against naming local packages `mcp` |
| Streamable HTTP client | `streamablehttp_client` emits a deprecation warning pointing to `streamable_http_client` in v1.30 | Noisy test output; unclear which name is stable | Kept old name, noted for later | Deprecation notes in the transport docs with a one-line migration |
| MCP session model | Every tool call from the backend needs a full `initialize` handshake; no obvious lightweight "one call" client | Extra round trips per step (search, purchase) | Open a short-lived session per call | A documented stateless/one-shot client helper |
| Authorization semantics | MCP has no standard place to carry a *per-call* policy decision; tools can't tell if a call was human-authorized or model-initiated | Had to invent an authority-token argument verified inside the tool | Policy-issued, single-use, product-bound token in tool args, checked by the server | A standard authorization/consent field or annotation on tool calls |
| Runtime | macOS system Python is 3.9; spec needs 3.12 | Install fails out of the box | `uv venv --python 3.12` | Ship a `.python-version` / uv-based install in quickstarts |
| Session state | React dev-mode double effect fired two concurrent `POST /api/session`, both computed the same `S00x` id → duplicate key → HTTP 500 | UI crash on first load in dev | Retry on `IntegrityError` | Use DB-generated ids instead of read-max-plus-one |
| Demo tooling | `npx playwright install chromium` failed once with a stack trace, worked on retry; bundled ffmpeg lacks the `fps` filter | Flaky setup; frame extraction failed | Retried; used system ffmpeg for audio mux and frames | Clearer retry message; document bundled ffmpeg limits |
