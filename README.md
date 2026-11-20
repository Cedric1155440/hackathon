# Timetable-aware second brain for school

Loop: lesson -> notes -> tasks -> revision, driven by an agent that knows the WebUntis timetable.
See `docs/idea.md` for the pitch and `docs/structure.md` for the planned layout.

## Progress

**Done**
- Idea and project structure documented (`docs/`).
- WebUntis login works against our school (`hpg.webuntis.com`).
- Untis provider layer (`backend/app/untis/`): `real` and `mock` behind one interface, with timetable (rooms, cancellations, substitution notes), homework and `lesson_at(time)`.
- Shared models (`Lesson`, `Homework`, `Exam`).

**Known limits**
- Student accounts can't read exams from Untis (`no right for getExams()`), so exam dates need another source.
- Subjects are raw course codes (e.g. `E5-GK3`), not readable names yet.

**Next**
- Untis poller + diff + Telegram alerts
- Transcription (faster-whisper) and the agent
- Notes, cross-check against Untis homework, quizzes, web fallback

## Run

```
python3 -m venv .venv && .venv/bin/pip install webuntis pydantic requests
cp .env.example .env        # fill in Untis login; set UNTIS_PROVIDER=real or mock
.venv/bin/python backend/scripts/test_untis.py
```
