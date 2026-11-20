import json

from app.llm.base import LLMClient
from app.models import Homework, Lesson, LessonNote

SYSTEM = """You turn a school lesson transcript into structured notes.
Extract only what was actually said. Do not invent content.
- summary: 2-3 sentences.
- concepts: the key ideas taught.
- definitions: definitions and formulas, verbatim where possible.
- test_hints: anything the teacher said will be on a test or exam.
- homework: every homework or deadline said out loud, with the due date as spoken.
Reply with JSON only."""


def build_prompt(transcript: str, lesson: Lesson | None, known_homework: list[Homework]) -> str:
    ctx = ["LESSON CONTEXT:"]
    if lesson:
        ctx.append(f"subject {lesson.subject}, teacher {', '.join(lesson.teachers)}, "
                   f"{lesson.start:%A %d.%m. %H:%M}")
    else:
        ctx.append("unknown lesson")
    if known_homework:
        ctx.append("Homework already in the school system:")
        ctx += [f"- {h.text} (due {h.due})" for h in known_homework]
    return "\n".join(ctx) + f"\n\nTRANSCRIPT:\n{transcript}"


def extract_note(llm: LLMClient, transcript: str, lesson: Lesson | None,
                 known_homework: list[Homework]) -> LessonNote:
    raw = llm.complete_json(SYSTEM, build_prompt(transcript, lesson, known_homework),
                            LessonNote.model_json_schema())
    return LessonNote.model_validate(raw)
