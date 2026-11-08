"""Policy copilot: deterministic facts first, Claude only explains them.

Pattern carried over from the Arrow/HAL work:
  1. Emergency words short-circuit to the emergency card (no model call).
  2. Retrieve policy facts by keyword score.
  3. No fact found -> say so and hand off to the broker. Never guess coverage.
  4. Otherwise Claude phrases an answer using ONLY the retrieved facts.
"""
import os
import re

EMERGENCY_WORDS = {
    "emergency", "ambulance", "heart attack", "stroke", "bleeding",
    "unconscious", "urgent", "accident",
    "επείγον", "ασθενοφόρο", "έμφραγμα", "αιμορραγία",
}

_WORD = re.compile(r"[\w']+", re.UNICODE)
_STOP = {"the", "a", "an", "is", "are", "do", "does", "i", "my", "to", "of", "for",
         "and", "in", "it", "can", "what", "how", "me", "am", "be", "on", "with"}

MODEL = os.environ.get("BROKEROS_MODEL", "claude-sonnet-5-5")

SYSTEM = (
    "You are the policy assistant for {broker}. Answer ONLY from the policy facts "
    "provided. Cite the page number for each statement. If the facts do not answer "
    "the question, say you cannot confirm it and suggest contacting the broker at "
    "{contact}. Never invent coverage, amounts or deadlines. Reply in {lang}. "
    "Be short and plain."
)


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2}


def is_emergency(message: str) -> bool:
    low = message.lower()
    return any(w in low for w in EMERGENCY_WORDS)


def retrieve(policy: dict, message: str, k: int = 3) -> list[dict]:
    q = _tokens(message)
    scored = []
    for fact in policy["facts"]:
        # Match on the curated topic keywords only. Matching the full text lets
        # generic words ("covered", "policy") pull in unrelated facts.
        score = len(q & _tokens(fact["topic"]))
        if score:
            scored.append((score, fact))
    scored.sort(key=lambda s: -s[0])
    return [f for _, f in scored[:k]]


def _plain_answer(facts: list[dict]) -> str:
    return "\n".join(f"{f['text']} (policy p.{f['page']})" for f in facts)


def answer(tenant: dict, message: str, lang: str | None = None) -> dict:
    policy = tenant["policy"]
    lang = lang if lang in tenant["languages"] else tenant["default_language"]

    if is_emergency(message):
        em = policy["emergency"]
        return {"kind": "emergency", "reply": f"{em['text']} {em['phone']}", "sources": []}

    facts = retrieve(policy, message)
    if not facts:
        return {
            "kind": "handoff",
            "reply": f"I cannot confirm that from the policy. Please contact {tenant['broker_contact']}.",
            "sources": [],
        }

    sources = [{"id": f["id"], "page": f["page"]} for f in facts]
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:  # offline / test mode: return the facts verbatim
        return {"kind": "facts", "reply": _plain_answer(facts), "sources": sources}

    import anthropic  # imported lazily so tests and offline runs need no SDK call

    client = anthropic.Anthropic(api_key=key)
    context = "\n".join(f"[p.{f['page']}] {f['text']}" for f in facts)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM.format(broker=tenant["display_name"], contact=tenant["broker_contact"], lang=lang),
        messages=[{"role": "user", "content": f"Policy facts:\n{context}\n\nQuestion: {message}"}],
    )
    return {"kind": "answer", "reply": msg.content[0].text, "sources": sources}
