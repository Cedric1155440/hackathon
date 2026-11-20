import base64
import logging
from datetime import date, datetime

import requests
import webuntis

from app import config
from app.models import Exam, Homework, Lesson, LessonStatus
from app.untis.base import UntisProvider

log = logging.getLogger(__name__)


def _parse_untis_date(n: int) -> date:
    return datetime.strptime(str(n), "%Y%m%d").date()


class RealUntisProvider(UntisProvider):
    """WebUntis via python-webuntis (timetable, exams) plus the raw REST API (homework)."""

    def __init__(self) -> None:
        self.server = config.get("UNTIS_SERVER")
        self.school = config.get("UNTIS_SCHOOL")
        self._session = webuntis.Session(
            server=self.server,
            school=self.school,
            username=config.get("UNTIS_USER"),
            password=config.get("UNTIS_PASSWORD"),
            useragent=config.get("UNTIS_CLIENT", "hackathon"),
        )
        self._http: requests.Session | None = None

    def _login(self) -> None:
        self._session.login()
        jsid = self._session.config["jsessionid"]
        http = requests.Session()
        http.cookies.set("JSESSIONID", jsid)
        school_b64 = base64.b64encode(self.school.encode()).decode()
        http.cookies.set("schoolname", f'"_{school_b64}"')
        self._http = http

    def _ensure(self) -> None:
        if self._http is None:
            self._login()

    def timetable(self, start: date, end: date) -> list[Lesson]:
        self._ensure()
        lessons = []
        for p in self._session.my_timetable(start=start, end=end):
            code = (p.code or "").lower()
            status = {
                "cancelled": LessonStatus.CANCELLED,
                "irregular": LessonStatus.SUBSTITUTED,
            }.get(code, LessonStatus.NORMAL)
            lessons.append(
                Lesson(
                    id=getattr(p, "id", None),
                    subject=", ".join(s.name for s in p.subjects) or "?",
                    teachers=[t.name for t in p.teachers],
                    rooms=[r.name for r in p.rooms],
                    start=p.start,
                    end=p.end,
                    status=status,
                )
            )
        return sorted(lessons, key=lambda x: x.start)

    def homework(self, start: date, end: date) -> list[Homework]:
        self._ensure()
        base = f"https://{self.server}/WebUntis"
        tok = self._http.get(f"{base}/api/token/new")
        tok.raise_for_status()
        r = self._http.get(
            f"{base}/api/homeworks/lessons",
            params={"startDate": start.strftime("%Y%m%d"), "endDate": end.strftime("%Y%m%d")},
            headers={"Authorization": f"Bearer {tok.text}"},
        )
        r.raise_for_status()
        data = r.json()["data"]
        subjects = {l["id"]: l["subject"] for l in data.get("lessons", [])}
        teachers = {t["id"]: t["name"] for t in data.get("teachers", [])}
        teacher_of = {rec["homeworkId"]: rec["teacherId"] for rec in data.get("records", [])}
        return [
            Homework(
                id=h["id"],
                lesson_id=h.get("lessonId"),
                subject=subjects.get(h.get("lessonId")),
                teacher=teachers.get(teacher_of.get(h["id"])),
                assigned=_parse_untis_date(h["date"]),
                due=_parse_untis_date(h["dueDate"]),
                text=h["text"],
                completed=h.get("completed", False),
            )
            for h in data.get("homeworks", [])
        ]

    def exams(self, start: date, end: date) -> list[Exam]:
        self._ensure()
        try:
            raw = self._session.exams(start=start, end=end)
        except Exception as e:  # student accounts get "no right for getExams()"
            log.warning("Untis exams unavailable: %s", e)
            return []
        return [
            Exam(id=getattr(x, "id", None),
                 subject=", ".join(s.name for s in getattr(x, "subjects", [])) or "?",
                 date=x.start.date() if hasattr(x.start, "date") else x.start)
            for x in raw
        ]
