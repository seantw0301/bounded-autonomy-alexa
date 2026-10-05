from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agent.orchestrator import handle_message, propose_boundary, reject_expansion
from db.database import get_db
from db.models import (AuditEvent, AuthorityToken, Boundary, Order, SessionRow, audit,
                       get_product, next_id, now)
from memory.store import active_boundaries
from policy.engine import evaluate

router = APIRouter(prefix="/api")
DEMO_USER = "demo-user"


class MessageIn(BaseModel):
    session_id: str
    text: str


class ProposeIn(BaseModel):
    user_id: str = DEMO_USER
    scope: str = "household_essentials"
    max_amount: float = 30.0
    allowed_merchants: list[str] = ["StoreA", "StoreB"]
    subscriptions_allowed: bool = False


class ApproveIn(BaseModel):
    actor: str  # must be HUMAN
    session_id: str | None = None


class EvaluateIn(BaseModel):
    user_id: str = DEMO_USER
    product_id: str
    boundary_id: str | None = None


class ExpandIn(BaseModel):
    actor: str = "AGENT"
    max_amount: float | None = None
    session_id: str | None = None


@router.post("/session")
def new_session(db: Session = Depends(get_db)):
    for _ in range(5):  # concurrent calls (React StrictMode) can race on the id
        s = SessionRow(id=next_id(db, SessionRow, "S", 3), user_id=DEMO_USER)
        db.add(s)
        try:
            db.commit()
            break
        except IntegrityError:
            db.rollback()
    audit(db, user_id=s.user_id, session_id=s.id, event_type="SESSION_STARTED",
          reason=f"{len(active_boundaries(db, s.user_id))} active boundary(ies) loaded")
    return {"id": s.id, "user_id": s.user_id, "boundaries": [b.to_dict() for b in active_boundaries(db, s.user_id)]}


@router.post("/agent/message")
async def agent_message(body: MessageIn, db: Session = Depends(get_db)):
    s = db.get(SessionRow, body.session_id)
    if not s:
        raise HTTPException(404, "session not found")
    return await handle_message(db, s, body.text)


@router.get("/boundaries")
def list_boundaries(user_id: str = DEMO_USER, db: Session = Depends(get_db)):
    rows = db.query(Boundary).filter(Boundary.user_id == user_id).order_by(Boundary.created_at).all()
    return [b.to_dict() for b in rows]


@router.post("/boundaries/propose")
def propose(body: ProposeIn, db: Session = Depends(get_db)):
    return propose_boundary(db, body.user_id, body.scope, max_amount=body.max_amount,
                            allowed_merchants=body.allowed_merchants,
                            subscriptions_allowed=body.subscriptions_allowed).to_dict()


def _proposed(db, bid) -> Boundary:
    b = db.get(Boundary, bid)
    if not b:
        raise HTTPException(404, "boundary not found")
    if b.status != "PROPOSED":
        raise HTTPException(409, f"boundary is {b.status}")
    return b


@router.post("/boundaries/{bid}/approve")
def approve(bid: str, body: ApproveIn, db: Session = Depends(get_db)):
    if body.actor != "HUMAN":
        reject_expansion(db, DEMO_USER, body.session_id, bid, "approval", actor=body.actor)
        raise HTTPException(403, "Only a human can approve a boundary")
    b = _proposed(db, bid)
    for old in active_boundaries(db, b.user_id):
        if old.scope == b.scope:
            old.status = "SUPERSEDED"
    ev = audit(db, user_id=b.user_id, session_id=body.session_id, event_type="BOUNDARY_APPROVED",
               boundary_id=b.id, decision="APPROVED", reason="Approved by human",
               authority_source=f"Human Approval {b.id}")
    b.created_by, b.status = "HUMAN", "ACTIVE"
    b.approval_event_id, b.approved_in_session = ev.id, body.session_id
    db.commit()
    return b.to_dict()


@router.post("/boundaries/{bid}/reject")
def reject(bid: str, body: ApproveIn, db: Session = Depends(get_db)):
    b = _proposed(db, bid)
    b.status = "REJECTED"
    audit(db, user_id=b.user_id, session_id=body.session_id, event_type="BOUNDARY_REJECTED",
          boundary_id=b.id, decision="REJECTED", reason="Rejected by human")
    db.commit()
    return b.to_dict()


@router.post("/boundaries/{bid}/expand")
def expand(bid: str, body: ExpandIn, db: Session = Depends(get_db)):
    """Authority expansion is never possible through this path; humans propose + approve a new boundary."""
    b = db.get(Boundary, bid)
    reject_expansion(db, b.user_id if b else DEMO_USER, body.session_id, bid, body.max_amount, actor=body.actor)
    raise HTTPException(403, "AUTHORITY_EXPANSION_REJECTED")


@router.post("/decision/evaluate")
def evaluate_endpoint(body: EvaluateIn, db: Session = Depends(get_db)):
    product = get_product(body.product_id)
    if not product:
        raise HTTPException(404, "product not found")
    if body.boundary_id:
        b = db.get(Boundary, body.boundary_id)
    else:
        from memory.store import pick_boundary
        b = pick_boundary(db, body.user_id, product["category"])
    d = evaluate(product, b)
    audit(db, user_id=body.user_id, event_type="DECISION", intent="evaluate", product_id=product["id"],
          boundary_id=b.id if b else None, decision=d.decision, reason=d.reason,
          authority_source=f"Human Approval {b.id}" if d.decision == "ALLOW" else "NONE")
    return {**d.to_dict(), "boundary_id": b.id if b else None}


@router.get("/audit")
def get_audit(db: Session = Depends(get_db)):
    rows = db.query(AuditEvent).order_by(AuditEvent.id.desc()).limit(200).all()
    out = []
    for r in rows:
        d = r.to_dict()
        p = get_product(r.product_id) if r.product_id else None
        d["product_name"], d["price"] = (p["name"], p["price"]) if p else (None, None)
        out.append(d)
    return out


@router.get("/orders")
def orders(db: Session = Depends(get_db)):
    return [{c.name: getattr(o, c.name) for c in o.__table__.columns}
            for o in db.query(Order).order_by(Order.created_at).all()]


@router.post("/demo/reset")
def reset(db: Session = Depends(get_db)):
    for m in (AuditEvent, AuthorityToken, Order, Boundary, SessionRow):
        db.query(m).delete()
    db.commit()
    return {"status": "reset"}
