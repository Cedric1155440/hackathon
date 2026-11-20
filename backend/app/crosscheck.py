import re
from difflib import SequenceMatcher

from app.models import CrossCheckItem, Homework, LessonNote

STOP = {"the", "a", "an", "and", "to", "for", "of", "in", "on", "is", "are", "we", "you", "your", "do",
        "der", "die", "das", "und", "zu", "für", "von", "in", "ist", "ihr", "wir", "bis", "auf", "im"}


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"\w+", text.lower()) if w not in STOP and len(w) > 1}


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+", text))


def _similar(a: str, b: str) -> bool:
    # Fuzzy, so "conjugation" ~ "Konjugation" across English/German.
    return a == b or SequenceMatcher(None, a, b).ratio() >= 0.8


def _score(spoken: str, untis: str) -> float:
    a, b = _tokens(spoken), _tokens(untis)
    if not a or not b:
        return 0.0
    hits = sum(any(_similar(x, y) for y in b) for x in a)
    overlap = hits / min(len(a), len(b))
    # Shared page / exercise numbers are strong evidence.
    nums = _numbers(spoken) & _numbers(untis)
    return overlap + (0.4 if nums else 0.0)


def cross_check(note: LessonNote, untis_homework: list[Homework],
                threshold: float = 0.5) -> list[CrossCheckItem]:
    items = []
    for spoken in note.homework:
        best = max(untis_homework, key=lambda h: _score(spoken.text, h.text), default=None)
        hit = best is not None and _score(spoken.text, best.text) >= threshold
        items.append(CrossCheckItem(spoken=spoken, in_untis=hit, match=best if hit else None))
    return items
