from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.untis import get_provider

WEB = Path(__file__).resolve().parents[2] / "web"

app = FastAPI(title="School second brain")
untis = get_provider()


def _week(offset: int) -> tuple[date, date]:
    monday = date.today() - timedelta(days=date.today().weekday()) + timedelta(weeks=offset)
    return monday, monday + timedelta(days=6)


@app.get("/api/timetable")
def timetable(week: int = 0):
    start, end = _week(week)
    return {"start": start, "end": end, "lessons": untis.timetable(start, end)}


@app.get("/api/homework")
def homework():
    today = date.today()
    return untis.homework(today - timedelta(days=14), today + timedelta(days=28))


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")
