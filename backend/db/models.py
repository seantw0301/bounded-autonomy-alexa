import json
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column

from db.database import PRODUCTS_PATH, Base, SessionLocal


def now():
    return datetime.now(timezone.utc)


class Boundary(Base):
    __tablename__ = "boundaries"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    scope: Mapped[str] = mapped_column(String)
    max_amount: Mapped[float] = mapped_column(Float)
    allowed_merchants: Mapped[list] = mapped_column(JSON)
    subscriptions_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str] = mapped_column(String)  # HUMAN | SYSTEM (proposal only)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    status: Mapped[str] = mapped_column(String)  # PROPOSED | ACTIVE | REJECTED | SUPERSEDED
    approval_event_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    approved_in_session: Mapped[str | None] = mapped_column(String, nullable=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@event.listens_for(Boundary, "before_insert")
@event.listens_for(Boundary, "before_update")
def _active_requires_human(_mapper, _conn, b):
    # Invariant: only a human can own an ACTIVE boundary.
    if b.status == "ACTIVE" and b.created_by != "HUMAN":
        raise ValueError("ACTIVE boundary must have created_by=HUMAN")


class SessionRow(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    product_id: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String)
    authority_source: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuthorityToken(Base):
    __tablename__ = "authority_tokens"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    boundary_id: Mapped[str] = mapped_column(String)
    product_id: Mapped[str] = mapped_column(String)
    decision: Mapped[str] = mapped_column(String)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    event_type: Mapped[str] = mapped_column(String)
    intent: Mapped[str | None] = mapped_column(String, nullable=True)
    product_id: Mapped[str | None] = mapped_column(String, nullable=True)
    boundary_id: Mapped[str | None] = mapped_column(String, nullable=True)
    decision: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    authority_source: Mapped[str | None] = mapped_column(String, nullable=True)
    tool_called: Mapped[str | None] = mapped_column(String, nullable=True)
    executed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d["created_at"] = self.created_at.isoformat() if self.created_at else None
        return d


def next_id(db, model, prefix: str, width: int) -> str:
    ids = [int(r[0][len(prefix):]) for r in db.query(model.id).all()]
    return f"{prefix}{(max(ids) + 1 if ids else 1):0{width}d}"


def load_products() -> list[dict]:
    with open(PRODUCTS_PATH) as f:
        return json.load(f)


def get_product(product_id: str) -> dict | None:
    return next((p for p in load_products() if p["id"] == product_id), None)


def audit(db, **kw) -> AuditEvent:
    ev = AuditEvent(**kw)
    db.add(ev)
    db.commit()
    return ev


__all__ = ["SessionLocal"]
