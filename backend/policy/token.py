import uuid
from datetime import datetime, timedelta, timezone

from db.models import AuthorityToken, Boundary, now

TTL_SECONDS = 60


def issue_token(db, user_id, boundary_id, product_id, decision) -> AuthorityToken:
    """Only the policy layer calls this, and only after an ALLOW."""
    if decision != "ALLOW":
        raise ValueError("tokens are issued only for ALLOW")
    t = AuthorityToken(
        id=f"AUTH-{uuid.uuid4().hex[:8].upper()}",
        user_id=user_id,
        boundary_id=boundary_id,
        product_id=product_id,
        decision=decision,
        issued_at=now(),
        expires_at=now() + timedelta(seconds=TTL_SECONDS),
    )
    db.add(t)
    db.commit()
    return t


def verify_token(db, token_id, product_id):
    """Returns (token | None, denial_reason | None). Does not consume."""
    t = db.get(AuthorityToken, token_id) if token_id else None
    if t is None:
        return None, "Missing or unknown authority token"
    exp = t.expires_at if t.expires_at.tzinfo else t.expires_at.replace(tzinfo=timezone.utc)
    if exp < datetime.now(timezone.utc):
        return None, "Authority token expired"
    if t.used:
        return None, "Authority token already used"
    if t.decision != "ALLOW":
        return None, "Token is not an ALLOW token"
    if t.product_id != product_id:
        return None, "Token issued for a different product"
    b = db.get(Boundary, t.boundary_id)
    if b is None or b.status != "ACTIVE" or b.created_by != "HUMAN":
        return None, "Invalid boundary"
    return t, None
