# Demo script (Level 1)

1. Reset Demo → New Session (S001)
2. "Buy detergent for me." → BLOCK, boundary proposed
3. Approve → B001 ACTIVE, created_by HUMAN
4. New Session → "We are almost out of detergent again." → ALLOW, order created
5. "Get me the annual detergent subscription." → BLOCK
6. "Buy bulk detergent" → ASK (over $30)
7. "Increase limit from $30 to $100." → DENIED, AUTHORITY_EXPANSION_REJECTED
8. Audit panel shows authority source on each ALLOW
