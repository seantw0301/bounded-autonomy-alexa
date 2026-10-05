"""Self-hosted MCP server (Streamable HTTP). Tools: search_product, purchase_product."""
import os
import re

from mcp.server.fastmcp import FastMCP

from db.database import SessionLocal, init_db
from db.models import Order, audit, get_product, load_products, next_id
from policy.token import verify_token

PORT = int(os.environ.get("BA_MCP_PORT", "8001"))
mcp = FastMCP("alexa-shop", host="127.0.0.1", port=PORT, json_response=True)

_WORD = re.compile(r"[a-z0-9]+")


@mcp.tool()
def search_product(query: str) -> dict:
    """Search the catalog. Returns ranked matches; best match first."""
    q = set(_WORD.findall(query.lower()))
    scored = []
    for p in load_products():
        if not p["available"]:
            continue
        words = _WORD.findall(p["name"].lower())
        hits = len(q & set(words))
        if hits:
            scored.append((hits - 0.01 * len(words), p))
    scored.sort(key=lambda x: -x[0])
    return {"results": [p for _, p in scored]}


@mcp.tool()
def purchase_product(product_id: str, authority_token: str) -> dict:
    """Buy a product. Requires a valid policy-issued authority token."""
    db = SessionLocal()
    try:
        product = get_product(product_id)
        tok, denial = verify_token(db, authority_token, product_id)
        if product is None:
            denial = denial or "Unknown product"
        if denial:
            audit(db, user_id=tok.user_id if tok else "unknown", event_type="PURCHASE_DENIED",
                  product_id=product_id, decision="DENIED", reason=denial,
                  tool_called="purchase_product", executed=False)
            return {"status": "PURCHASE_DENIED", "reason": denial}
        tok.used = True
        order = Order(id=next_id(db, Order, "O", 3), user_id=tok.user_id, product_id=product_id,
                      amount=product["price"], status="completed",
                      authority_source=f"Human Approval {tok.boundary_id}")
        db.add(order)
        db.commit()
        return {"order_id": order.id, "status": "completed", "amount": order.amount,
                "authority_source": order.authority_source}
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    mcp.run(transport="streamable-http")
