"""Persistent cross-session memory: boundaries live in SQLite, keyed by user (not session)."""
from db.models import Boundary


def active_boundaries(db, user_id):
    return (db.query(Boundary).filter(Boundary.user_id == user_id, Boundary.status == "ACTIVE")
            .order_by(Boundary.created_at).all())


def pick_boundary(db, user_id, category):
    bs = active_boundaries(db, user_id)
    for b in reversed(bs):
        if b.scope == category:
            return b
    return bs[-1] if bs else None


def pending_proposal(db, user_id):
    return (db.query(Boundary).filter(Boundary.user_id == user_id, Boundary.status == "PROPOSED")
            .order_by(Boundary.created_at.desc()).first())
