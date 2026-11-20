import re

from app.llm.base import LLMClient

HOMEWORK = re.compile(r"hausaufgabe|homework|bis (montag|dienstag|mittwoch|donnerstag|freitag)|for next (lesson|week|time)|due |\bdo (exercise|task|ex\.)|(seite|page|s\.|p\.)\s*\d+", re.I)
TEST = re.compile(r"klausur|klassenarbeit|\btest\b|exam|prüfung|wichtig|important", re.I)
DUE = re.compile(r"\b(?:bis|until|by|due)\s+(\w+)", re.I)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


class StubLLM(LLMClient):
    """Keyword heuristics standing in for a real model. Same output shape, much dumber."""
    name = "stub"

    def complete_json(self, system: str, user: str, schema: dict) -> dict:
        transcript = user.split("TRANSCRIPT:", 1)[-1].strip()
        sents = _sentences(transcript)
        homework, hints, rest = [], [], []
        for s in sents:
            if HOMEWORK.search(s):
                m = DUE.search(s)
                homework.append({"text": s, "due": m.group(1) if m else None})
            elif TEST.search(s):
                hints.append(s)
            else:
                rest.append(s)
        return {
            "summary": " ".join(rest[:2]) or "(empty transcript)",
            "concepts": rest[2:6],
            "definitions": [],
            "test_hints": hints,
            "homework": homework,
        }
