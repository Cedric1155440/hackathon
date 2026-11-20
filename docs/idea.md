# Timetable-aware second brain for school (working title)

AI Coding Hackathon, STARTPLATZ Cologne, 20-22 Nov 2026

## One-line pitch
The first school tool that makes sure you actually learn what you sat through: it listens to the lesson, writes the notes, catches the homework your school system missed, and then makes you revise.

## Problem
- Lessons produce a lot of information, and most of it is lost by the evening.
- WebUntis knows the timetable, but not what happened in the lesson. Homework said out loud never reaches it.
- Note-taking AI tools stop at the transcript. Nobody acts on the notes.

## Solution
A loop: **lesson -> notes -> tasks -> revision**, driven by an agent that knows the timetable.

1. **Capture:** record the lesson (with consent) or send a voice note, photo of the board, or text.
2. **Transcribe:** local Whisper, so no audio leaves the machine.
3. **Agent:** gets the transcript plus the Untis context for that exact lesson (subject, teacher, room, existing homework, exam dates). It extracts key concepts, definitions, formulas, "this will be on the test" moments, and spoken homework or deadlines.
4. **Cross-check:** compare with Untis data. Example: "Physik: Hausaufgabe S. 84 Nr. 3, due Tuesday, not in Untis."
5. **Output:** one structured note per lesson in an Obsidian vault, plus tasks with deadlines.
6. **Follow-up:** quiz questions and flashcards per lesson, spaced out, and a revision plan counted back from exam dates.

## Interaction
- **Telegram bot (primary):**
  - send audio, photos, or text; the bot files them to the current lesson by timestamp
  - push alerts: Entfall, substitution, room change, new homework or exam
  - daily digest: what's due, what was cancelled, what to revise
  - quiz questions delivered as chat messages
- **Website (fallback):**
  - same data without Telegram: upload recordings, browse lesson notes, view tasks and the revision plan, take quizzes
  - lets us demo even if Telegram or the network misbehaves

## Architecture
- **Untis poller:** unofficial WebUntis API (`webuntis` Python lib), diffs the timetable every few minutes.
- **Transcription:** faster-whisper, local.
- **Agent:** LLM with tools: `get_lesson`, `get_homework`, `get_exams`, `write_note`, `create_task`, `schedule_quiz`, `notify`.
- **Storage:** Markdown files (Obsidian vault) plus a small SQLite DB for tasks and quiz state.
- **Interfaces:** Telegram bot and a small web app, both calling the same backend.

## Privacy and legality
- Recording only with the teacher's explicit consent (in Germany, recording without consent is an offence, §201 StGB), or only the user's own voice dictation after class.
- Local transcription; no audio leaves the machine.
- Demo with our own or consenting recordings, never a real class.

## Build order (48h)
1. Test the Untis login; if blocked, use mock data and say so.
2. Poller, diff, and Telegram notifications.
3. Transcription, then the agent, then per-lesson note generation.
4. Cross-check against Untis (the demo highlight).
5. Quizzes and revision plan.
6. Web fallback.
7. Pitch prep (start Saturday afternoon, not Sunday morning).

## Team split (suggestion)
- Untis poller, diff, notifications
- Transcription and agent
- Obsidian output, quizzes, revision plan
- Web fallback and pitch

## Demo plan
Record 30 seconds of a consenting person explaining something, and show: transcript, structured note, "homework not in Untis" alert on Telegram, and the generated quiz.

## Risks
- Untis access blocked by the school: fall back to mock data.
- Narrow audience: lead the pitch with the cross-check and the learning loop, not "AI notes".
- Too much scope: the cross-check demo must work before quizzes or the website.
