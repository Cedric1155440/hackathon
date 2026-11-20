from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class LessonStatus(str, Enum):
    NORMAL = "normal"
    CANCELLED = "cancelled"
    SUBSTITUTED = "substituted"
    ROOM_CHANGED = "room_changed"


class Lesson(BaseModel):
    id: int | None = None
    subject: str                  # Untis course code, e.g. "E5-GK3"
    teachers: list[str] = []
    rooms: list[str] = []
    start: datetime
    end: datetime
    status: LessonStatus = LessonStatus.NORMAL
    note: str = ""               # substitution / lesson text from Untis


class Homework(BaseModel):
    id: int
    lesson_id: int | None = None
    subject: str | None = None
    teacher: str | None = None
    assigned: date
    due: date
    text: str
    completed: bool = False


class Exam(BaseModel):
    id: int | None = None
    subject: str
    date: date
    text: str = ""


class SpokenHomework(BaseModel):
    text: str
    due: str | None = None        # as said in the lesson, e.g. "Tuesday"


class LessonNote(BaseModel):
    """What the agent extracts from one lesson transcript."""
    summary: str
    concepts: list[str] = []
    definitions: list[str] = []   # definitions and formulas
    test_hints: list[str] = []    # "this will be on the test" moments
    homework: list[SpokenHomework] = []


class CrossCheckItem(BaseModel):
    spoken: SpokenHomework
    in_untis: bool
    match: Homework | None = None


class Analysis(BaseModel):
    lesson: Lesson | None = None
    note: LessonNote
    crosscheck: list[CrossCheckItem]
    llm: str                      # which provider produced the note
