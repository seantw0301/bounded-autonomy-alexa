# MCP Protocol Compatibility Check

Target: MCP spec **2025-11-25** (pages: `server/tools`, `basic/transports`). Method: raw JSON-RPC over HTTP with `curl` against the running server (`backend/mcp_server/server.py`), plus the SDK client. Package version was **not** used as evidence. No dependencies were modified.

## Summary
| Item | Observed |
|---|---|
| Protocol version | Server answers `initialize` with `2025-11-25` when requested. Supported list (from the server's own 400 error): 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25 |
| Transport | Streamable HTTP, single endpoint `http://127.0.0.1:8001/mcp`, POST + GET + DELETE, `application/json` responses (`json_response=True`) |
| Verdict | **Compatible with 2025-11-25 for the implemented surface** (initialize, tools/list, tools/call, ping, session handling). Two behavioral deviations and some unimplemented SHOULD/MUST items below |

## Initialization (verified)
- Requested `2025-11-25` → `protocolVersion: "2025-11-25"`; requested `2025-06-18` → echoed; requested unknown `2026-01-01` → server counter-offers `2025-11-25` (correct negotiation)
- `MCP-Session-Id` returned on the initialize response (visible ASCII hex)
- `notifications/initialized` → `202 Accepted`
- Capabilities advertised: `tools` (listChanged=false); also `prompts`/`resources` declared although none are defined (harmless)
- `serverInfo.version` is `1.30.0` = the SDK version, not this app's version; no `title`
- SDK client negotiated `2025-11-25` end to end
- Not tested: whether the server rejects requests sent before `notifications/initialized`

## Tool discovery (verified)
- `tools/list` returns `search_product`, `purchase_product`; names valid per spec rules; `inputSchema` is an object schema (no `$schema` → defaults to JSON Schema 2020-12, allowed)
- No pagination (`nextCursor` absent; fine), no `title`, `outputSchema`, `annotations`, `icons`, `execution` (all optional)

## Tool invocation (verified)
- `tools/call` returns `content[].text` containing JSON; no `structuredContent` / `outputSchema` (spec SHOULD-level only when structured output is declared)
- Invalid arguments → result with `isError: true` and a validation message (matches the 2025-11-25 "input validation = tool execution error" guidance)
- `ping` → `{}`

## Transport behavior (verified)
| Check | Result | Spec |
|---|---|---|
| Bad `Origin` | 403 Forbidden | MUST ✔ |
| Bound to 127.0.0.1 | yes | SHOULD ✔ |
| Missing session id | 400 | SHOULD ✔ |
| Terminated session (after DELETE) | 404; DELETE → 200 | ✔ |
| Unsupported `MCP-Protocol-Version` | 400 listing supported versions | MUST ✔ |
| Missing `MCP-Protocol-Version` | accepted (assumes older default) | SHOULD assume 2025-03-26 ✔ |
| GET | `text/event-stream` | ✔ |
| Notification | 202 | MUST ✔ |
| POST without `text/event-stream` in Accept | 400 | spec silent on server status |

## Deviations / gaps (exact)
1. **Unknown tool** — server returns a normal result `{"isError": true, "content":[{"text":"Unknown tool: nope"}]}`. The 2025-11-25 Error Handling section lists unknown tools as a **protocol error** (example: JSON-RPC `-32602`). Source: SDK behavior (mcp 1.30.0), not this app's code.
2. **Business denial reported as success** — `purchase_product` with an invalid token returns `isError: false` with `{"status":"PURCHASE_DENIED"}`. The spec classifies business-logic errors as tool execution errors (`isError: true`). Source: this app's tool code; the backend currently reads the JSON status, so changing it needs a matching backend change.
3. **Rate limiting** — spec Security Considerations say servers MUST rate limit tool invocations; not implemented.
4. **Authentication** — none (spec: SHOULD); acceptable for a localhost demo only.
5. Cosmetic: `serverInfo.version` shows the SDK version; unused `prompts`/`resources` capabilities advertised.

## Does the pinned SDK satisfy the spec?
Yes for protocol version and transport: `mcp==1.30.0` (pinned `<2`) reports `LATEST_PROTOCOL_VERSION = 2025-11-25` and the live handshake confirms it. The only SDK-level deviation found is #1 (unknown-tool error shape). Items #2–#4 are application-level and fixable without changing dependencies.

## Reproduce
Start `cd backend && .venv/bin/python -m mcp_server.server`, then send `initialize` (`Accept: application/json, text/event-stream`), `notifications/initialized`, `tools/list`, `tools/call` with the `mcp-session-id` and `MCP-Protocol-Version: 2025-11-25` headers.
