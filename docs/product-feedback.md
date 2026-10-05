# Product Feedback

> Scope note: this project was built against a local Alexa+ **simulator** and a self-hosted MCP server. No Alexa+ developer APIs were used, so the feedback below is about MCP/agent-authorization tooling. Add Alexa+-specific feedback here before submitting.

## What worked
- MCP tools (`search_product`, `purchase_product`) were quick to define and test with FastMCP over Streamable HTTP.
- Keeping the authorization decision outside the model made behavior easy to test (14 automated tests).

## Gaps
1. **No standard per-call authority.** Tools cannot distinguish a human-approved action from a model-initiated one. We added policy-issued tokens as a tool argument; a protocol-level consent/authorization field would make this portable.
2. **Persistent consent is undefined.** Cross-session "approved once, valid later" authority has no home in agent platforms; each app invents its own store and audit format.
3. **SDK churn.** v1→v2 renamed core classes; transport helpers are being renamed with deprecation warnings.
4. **One-shot calls are heavy.** A full handshake per tool call is verbose for simple backends.

## Requests
- A first-class "authority envelope" concept (scope, limits, expiry, provenance) that agents can use but not modify.
- Audit/provenance hooks that record which human approval authorized each tool call.
- Stable, versioned quickstarts for MCP server + client.
