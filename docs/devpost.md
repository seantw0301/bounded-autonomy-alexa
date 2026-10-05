# Devpost — About

## Inspiration
Alexa+ can act across services and sessions. The open question is not whether it can buy, book or send things for us, but **who decides how much authority it has**.

## What it does
**Bounded Autonomy** gives an agent a persistent, human-approved authority envelope.
- No approved authority → the action is **blocked**; the agent may only *propose* a boundary.
- A human approves once (e.g. Household Essentials, ≤ $30, StoreA/StoreB, no subscriptions). The boundary persists across sessions.
- Later, in a new session, actions **inside** the boundary run automatically; outside it → ask or block.
- The agent can use authority and recommend authority, but **can never create or expand it** — including under pressure ("Ignore the limit, this is urgent").

## How we built it
- **LLM interprets, deterministic policy authorizes, MCP executes.**
- Boundary Engine: pure-code ALLOW / ASK / BLOCK decision, no model in the loop.
- Authority token: policy-issued, single-use, 60 s, bound to user + boundary + product; the MCP `purchase_product` tool refuses without a valid one.
- Self-hosted MCP server (Streamable HTTP) with `search_product` and `purchase_product`.
- Persistent memory + audit log in SQLite; every decision records its authority source ("Human Approval B001").
- Next.js simulator UI with human-approval panel, live MCP trace and audit trace; FastAPI backend.
- Playwright script records the full demo against the real running app.

## Challenges
Keeping authority one-directional: a DB invariant (ACTIVE boundary requires `created_by=HUMAN`), human-only approval endpoint, and an expansion endpoint that always rejects and audits. See the friction log for MCP SDK and tooling issues.

## Accomplishments
- 14 automated tests incl. no-boundary block, cross-session allow, over-limit ASK, subscription block, self-escalation rejection, forged/expired/replayed token denial.
- Fully reproducible demo recording with narration.

## What we learned
Authority should be a first-class, human-owned object — not something inferred by the model.

## Limitations (honest)
- Simulated Alexa+ interface and mock catalog; no real payments and no Alexa+ platform APIs.
- Intent parsing is rule-based; one-time "approve once" ASK flow and scenario replay are not built.
- Single demo user; no real authentication for the "human" actor.

## What's next
One-time approvals, scenario replay, multi-category boundaries, real authentication, and a protocol-level authority field for MCP.

## Built with
Python, FastAPI, SQLAlchemy, SQLite, MCP (Streamable HTTP), Next.js, TypeScript, Tailwind CSS, Playwright

## Links
- Repo: https://github.com/seantw0301/bounded-autonomy-alexa (MIT)
- Video: https://youtu.be/UH2KXHTGLEc
