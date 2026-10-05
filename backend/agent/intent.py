"""Rule-based intent parsing (the 'LLM' stand-in). It only interprets; it never authorizes."""
import re

BUY = re.compile(r"\b(buy|get|order|purchase|need|out of|run(ning)? out|restock|subscribe)\b", re.I)
ESCALATE = re.compile(
    r"\b(increase|raise|expand|bump|lift|change|override)\b.*\b(limit|boundary|cap|authority)\b"
    r"|\bignore\b.*\b(limit|boundary|rules?)\b", re.I)
STOP = set("""a an the me my for to of we us are is be it its almost out again please i
buy get order purchase need want some more and or anyway this that now ignore limit
urgent already just can you could would run running low restock subscribe""".split())


def parse(text: str) -> dict:
    escalate = bool(ESCALATE.search(text))
    amounts = re.findall(r"\$\s*(\d+(?:\.\d+)?)", text)
    words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and not w.isdigit()]
    purchase = bool(BUY.search(text)) and bool(words)
    return {
        "escalate": escalate,
        "requested_amount": float(amounts[-1]) if amounts else None,
        "purchase": purchase,
        "query": " ".join(words),
    }
