"""Deterministic Boundary Engine. No LLM involved."""
from dataclasses import dataclass, field


@dataclass
class Decision:
    decision: str  # ALLOW | ASK | BLOCK
    reason: str
    checks: dict = field(default_factory=dict)  # name -> PASS | FAIL | N/A

    def to_dict(self):
        return {"decision": self.decision, "reason": self.reason, "checks": self.checks}


def _checks(product: dict, b) -> dict:
    return {
        "category": "PASS" if product["category"] == b.scope else "FAIL",
        "amount": "PASS" if product["price"] <= b.max_amount else "FAIL",
        "merchant": "PASS" if product["merchant"] in b.allowed_merchants else "FAIL",
        "subscription": "FAIL" if product["subscription"] and not b.subscriptions_allowed else "PASS",
    }


def evaluate(product: dict, boundary) -> Decision:
    if boundary is None:
        return Decision("BLOCK", "No approved authority", {})
    if boundary.status != "ACTIVE":
        return Decision("BLOCK", "Boundary inactive", {})
    c = _checks(product, boundary)
    if c["category"] == "FAIL":
        return Decision("BLOCK", "Category outside authority", c)
    if c["subscription"] == "FAIL":
        return Decision("BLOCK", "Subscription is outside human-approved authority", c)
    if c["merchant"] == "FAIL":
        return Decision("ASK", "Merchant not pre-approved", c)
    if c["amount"] == "FAIL":
        return Decision("ASK", f"Amount exceeds approved ${boundary.max_amount:g} limit", c)
    return Decision("ALLOW", f"Inside approved authority {boundary.id}", c)
