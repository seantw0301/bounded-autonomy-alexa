from datetime import datetime

from agent.intent import parse
from db.models import Boundary, SessionRow, audit, next_id, get_product
from mcp_server.client import call_tool
from memory.store import active_boundaries, pending_proposal, pick_boundary
from policy.engine import evaluate
from policy.token import issue_token

DEFAULT_PROPOSAL = dict(max_amount=30.0, allowed_merchants=["StoreA", "StoreB"],
                        subscriptions_allowed=False)


def propose_boundary(db, user_id, scope, **over) -> Boundary:
    """System/agent may RECOMMEND authority. Status stays PROPOSED until a human approves."""
    b = Boundary(id=next_id(db, Boundary, "B", 3), user_id=user_id, scope=scope,
                 created_by="SYSTEM", status="PROPOSED", **{**DEFAULT_PROPOSAL, **over})
    db.add(b)
    db.commit()
    audit(db, user_id=user_id, event_type="BOUNDARY_PROPOSED", boundary_id=b.id,
          decision="PROPOSED", reason=f"Proposed {scope} ≤ ${b.max_amount:g}")
    return b


def reject_expansion(db, user_id, session_id, boundary_id, requested, actor="AGENT"):
    ev = audit(db, user_id=user_id, session_id=session_id, event_type="AUTHORITY_EXPANSION_REJECTED",
               boundary_id=boundary_id, decision="DENIED",
               reason=f"{actor} cannot create or expand authority (requested {requested})",
               authority_source="NONE")
    return ev


def _t(trace, call, result):
    trace.append({"time": datetime.now().strftime("%H:%M:%S"), "call": call, "result": result})


async def handle_message(db, session: SessionRow, text: str) -> dict:
    uid, sid = session.user_id, session.id
    intent = parse(text)
    out = {"session_id": sid, "intent": intent, "product": None, "decision": None,
           "tool_action": None, "proposal": None, "order": None, "notes": [],
           "trace": [], "authority_expansion": None, "trace_id": None}
    trace = out["trace"]
    replies = []

    if intent["escalate"]:
        bs = active_boundaries(db, uid)
        ev = reject_expansion(db, uid, sid, bs[-1].id if bs else None, intent["requested_amount"])
        out["notes"].append("AUTHORITY_EXPANSION_REJECTED")
        out["authority_expansion"] = "REJECTED"
        out["trace_id"] = f"A{ev.id:03d}"
        _t(trace, "authority.expand()", "REJECTED — agents cannot create or expand authority")
        out["decision"] = {"decision": "DENIED", "reason": "Authority expansion rejected",
                           "checks": {}, "audit_event_id": ev.id}
        replies.append("I can't change my own limits. Only you can approve a new boundary.")

    if not intent["purchase"]:
        if not replies:
            replies.append("Tell me what to buy, e.g. “Buy detergent for me.”")
        out["reply"] = " ".join(replies)
        return out

    res = await call_tool("search_product", {"query": intent["query"]})
    results = res.get("results", [])
    _t(trace, f'search_product("{intent["query"]}")',
       f'{results[0]["id"]} / ${results[0]["price"]:g}' if results else "no match")
    if not results:
        out["reply"] = " ".join(replies + [f"I couldn't find “{intent['query']}”."])
        return out
    product = results[0]
    out["product"] = product
    boundary = pick_boundary(db, uid, product["category"])
    d = evaluate(product, boundary)
    _t(trace, f'boundary.evaluate({product["id"]}, {boundary.id if boundary else "none"})',
       f"{d.decision} — {d.reason}")
    src = f"Human Approval {boundary.id}" if d.decision == "ALLOW" else "NONE"
    dec = {**d.to_dict(), "boundary_id": boundary.id if boundary else None, "authority_source": src}
    base = dict(user_id=uid, session_id=sid, event_type="DECISION", intent="purchase",
                product_id=product["id"], boundary_id=boundary.id if boundary else None,
                decision=d.decision, reason=d.reason, authority_source=src)

    if d.decision == "ALLOW":
        tok = issue_token(db, uid, boundary.id, product["id"], d.decision)
        _t(trace, "authority_token.issue()", tok.id)
        result = await call_tool("purchase_product",
                                 {"product_id": product["id"], "authority_token": tok.id})
        done = result.get("status") == "completed"
        _t(trace, f'purchase_product({product["id"]}, {tok.id})',
           f'ORDER {result["order_id"]} COMPLETE' if done else f'DENIED — {result.get("reason")}')
        ev = audit(db, **base, tool_called="purchase_product", executed=done)
        out["tool_action"] = {"tool": "purchase_product", "token": tok.id, "result": result}
        out["order"] = result if done else None
        replies.append(f"Done — bought {product['name']} for ${product['price']:g} "
                       f"({product['merchant']}) under your approval {boundary.id}."
                       if done else f"Purchase was denied: {result.get('reason')}")
    else:
        ev = audit(db, **base)
        _t(trace, "purchase_product()", f"NOT CALLED — {d.decision}")
        if d.decision == "BLOCK":
            replies.append(f"Blocked: {d.reason}.")
        else:
            replies.append(f"I need your approval: {d.reason}. I did not buy anything.")
        if boundary is None:
            if pending_proposal(db, uid) is None:
                out["proposal"] = propose_boundary(db, uid, product["category"]).to_dict()
            else:
                out["proposal"] = pending_proposal(db, uid).to_dict()
            replies.append("I've drafted a boundary for you to review.")
    dec["audit_event_id"] = ev.id
    if out["authority_expansion"]:
        dec["authority_expansion"] = "REJECTED"
    out["trace_id"] = f"A{ev.id:03d}"
    out["decision"] = dec
    out["reply"] = " ".join(replies)
    return out
