# Product Feedback

## Alexa+ Track / Simulation Path

**What we used:** A self-built Alexa+ conversational simulator combined with a self-hosted MCP server.

**Onboarding:** The hackathon documentation clearly explained that participants without Alexa+ preview access could build a simulated Alexa+ experience. This made it possible to prototype the interaction model without restricted developer tooling.

**What worked well:** The simulation path allowed us to focus on the agentic workflow, cross-session state, authorization model, and MCP execution.

**What needs improvement:** A public lightweight Alexa+ simulator or reference interaction shell would make it easier to validate interaction patterns and reduce uncertainty around platform-specific UX.

**Would we build with it again?** Yes. The Alexa+ model of persistent, cross-session agentic experiences is a strong fit for bounded delegation and human-approved autonomy.

## MCP (self-hosted server, Python SDK)

**What we used:** FastMCP from the official Python SDK (`mcp==1.30.0`, pinned `<2`), Streamable HTTP, two tools (`search_product`, `purchase_product`). Protocol behavior was checked against spec 2025-11-25 — see [mcp-compatibility.md](mcp-compatibility.md).

**What worked well**
- Tools were quick to define and test; the SDK negotiated protocol 2025-11-25 and handled sessions, Origin checks (403) and protocol-version headers correctly.
- Keeping the authorization decision outside the model made behavior easy to test (14 automated tests).

**What needs improvement**
1. **No standard per-call authority.** A tool cannot tell whether a call was human-approved or model-initiated. We added a policy-issued, single-use authority token as a tool argument; a protocol-level consent/authorization field would make this portable.
2. **Persistent consent has no home.** Cross-session "approved once, valid later" authority is not part of MCP or the agent platform, so every app invents its own store and audit format.
3. **Error semantics.** For an unknown tool the SDK returns an `isError: true` result, while the 2025-11-25 spec's example is a JSON-RPC `-32602` protocol error. Distinguishing business denials (`isError: true` per spec) from success also needs deliberate handling in each tool.
4. **SDK churn.** v1→v2 renamed `FastMCP` → `MCPServer`; `streamablehttp_client` now warns it is deprecated. A pinned, versioned quickstart would help.
5. **One-shot calls are heavy.** A full `initialize` handshake per tool call is verbose for simple backends; a documented stateless client helper would help.
6. **Server security checklist.** The spec says servers MUST rate limit tool invocations; the SDK gives no built-in hook, so it is easy to miss.

**Requests**
- A first-class "authority envelope" (scope, limits, expiry, provenance) that agents can use but not modify.
- Audit/provenance hooks recording which human approval authorized each tool call.
- Stable, versioned quickstarts for MCP server + client.

**Would we build with it again?** Yes — MCP made the tool boundary clean enough to enforce policy at the point of execution.

Details of individual issues: [friction-log.md](friction-log.md).
