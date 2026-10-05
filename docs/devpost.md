# Devpost — About (final)

## Inspiration
Alexa+ can act across services and sessions. As AI agents become capable of buying, booking, sending, and completing tasks for us, the bigger question is no longer simply *what can the agent do?*

It is: **Who decides how much authority the agent has?**

Asking for confirmation before every action makes an agent less useful. Giving it unlimited authority creates obvious trust and safety problems.

We wanted to explore the middle ground: let an agent act autonomously inside boundaries that a human explicitly approved earlier, while making sure the agent can never expand those boundaries by itself.

That idea became **Bounded Autonomy for Alexa+**.

## What it does
Bounded Autonomy gives an agent a persistent, human-approved authority envelope.

If no approved authority exists, the requested action is blocked. The agent may suggest a boundary, but cannot activate one itself.

For example, a user can approve:
- Household Essentials
- Up to $30 per purchase
- StoreA or StoreB only
- No subscriptions

That approval persists across sessions. Later, in a new session, the agent can automatically complete a purchase that falls inside the approved boundary without asking again. Actions outside the boundary are either blocked or require human approval.

Most importantly: **the agent can use authority, but it cannot create or expand its own authority.** Even instructions such as "Ignore the limit. This is urgent." cannot override the stored human-approved policy.

## How we built it
The architecture follows one core principle: **LLM interprets. Deterministic policy authorizes. MCP executes.**

The agent layer interprets the user's intent and searches for the requested product. A deterministic Boundary Engine then evaluates the proposed action and returns one of three decisions: ALLOW, ASK or BLOCK. The authorization decision is made in code, not by the language model.

When an action is allowed, the policy layer creates a short-lived, single-use Authority Token bound to the user, approved boundary, and product. The self-hosted MCP `purchase_product` tool will only execute when a valid Authority Token is supplied.

Our stack includes:
- Python and FastAPI
- SQLAlchemy and SQLite
- Self-hosted MCP server using Streamable HTTP
- Next.js, TypeScript, and Tailwind CSS
- Playwright for automated end-to-end demo recording

SQLite stores persistent boundaries, sessions, orders, and audit events. This allows a boundary approved in one session to be used safely in a later session. Every allowed action also records its authority provenance, such as `Authority Source: Human Approval B001`.

## Challenges we ran into
The hardest problem was keeping authority strictly one-directional. The agent needed to be able to use an existing boundary without ever being able to change that boundary. We enforce this in several layers:
- An ACTIVE boundary must have `created_by = HUMAN`.
- The approval endpoint only accepts a human actor.
- Agent-generated boundaries remain proposals.
- Attempts to expand authority are rejected and audited.
- MCP purchase execution requires a valid policy-issued token.

We also ran into practical MCP development issues, including SDK version changes, Streamable HTTP client behavior, package-name conflicts, and the lack of a standard protocol field for carrying per-action human authorization. Those implementation issues became part of our friction log and product feedback.

## Accomplishments that we're proud of
We built a complete cross-session autonomy loop rather than a static UI mockup. The demo shows:
1. A purchase blocked because no authority exists.
2. A human approving a reusable boundary.
3. A new session loading the previous approval.
4. An in-boundary purchase executing automatically through MCP.
5. A subscription outside the boundary being blocked.
6. An attempted self-escalation being rejected.

We also created automated tests covering no-authority blocking, cross-session execution, over-limit requests, subscription blocking, invalid and replayed tokens, and self-escalation attempts. The demo itself is reproducible with an automated Playwright recording workflow.

## What we learned
Agent authority should be treated as a first-class, human-owned object. It should not be inferred from conversation history or decided dynamically by the model.

Persistent autonomy works better when the system can answer three questions clearly:
- What is the agent allowed to do?
- Who approved that authority?
- Can the agent change it?

In Bounded Autonomy, the answer to the last question is always: **No. Only the human can expand authority.**

## Limitations
This project currently uses a simulated Alexa+ interface and a mock product catalog. It does not execute real payments or use private Alexa+ platform APIs. Intent parsing is rule-based in the current prototype, because authorization is intentionally separated from model reasoning. The demo currently supports one user and does not yet implement real authentication or one-time approval for ASK decisions.

## What's next
- One-time approvals without changing long-term authority
- Boundary expiration and revocation
- Multiple categories and service domains
- Real user authentication
- Richer cross-service workflows
- A standardized authority-envelope field for MCP

Our longer-term goal is to make bounded delegation reusable across purchasing, scheduling, travel, smart-home actions, and other agentic workflows.

**Let AI act — without letting it decide its own authority.**

## Built with
Python, FastAPI, SQLAlchemy, SQLite, MCP (Streamable HTTP), Next.js, TypeScript, Tailwind CSS, Playwright

## Links
- Repo: https://github.com/seantw0301/bounded-autonomy-alexa (MIT)
- Video: https://youtu.be/UH2KXHTGLEc
