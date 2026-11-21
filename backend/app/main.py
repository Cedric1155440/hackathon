from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.agent.agent import extract_note
from app.crosscheck import cross_check
from app.llm import get_llm
from app.materials import MAX_BYTES, Material, UploadError, file_path, list_materials, save_upload
from app.models import Analysis
from app.untis import get_provider

WEB = Path(__file__).resolve().parents[2] / "web"

app = FastAPI(title="School second brain")
untis = get_provider()
llm = get_llm()


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


@app.get("/api/exams")
def exams():
    today = date.today()
    return untis.exams(today, today + timedelta(days=60))


class AnalyzeRequest(BaseModel):
    transcript: str
    at: datetime | None = None    # when the lesson happened; defaults to now


@app.post("/api/analyze", response_model=Analysis)
def analyze(req: AnalyzeRequest):
    today = date.today()
    lesson = untis.lesson_at(req.at or datetime.now())
    known = untis.homework(today - timedelta(days=14), today + timedelta(days=28))
    if lesson:
        same = [h for h in known if h.subject == lesson.subject]
        known = same or known
    note = extract_note(llm, req.transcript, lesson, known)
    return Analysis(lesson=lesson, note=note, crosscheck=cross_check(note, known), llm=llm.name)


@app.post("/api/materials", response_model=Material)
def upload_material(file: UploadFile = File(...), kurs: str = Form(...), kind: str = Form(...),
                    title: str = Form("")):
    data = file.file.read(MAX_BYTES + 1)
    try:
        return save_upload(data, file.filename or "", kurs, kind, title)
    except UploadError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@app.get("/api/materials", response_model=list[Material])
def materials(kurs: str | None = None):
    return list_materials(kurs)


@app.get("/api/materials/{material_id}/file")
def material_file(material_id: int):
    path = file_path(material_id)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail="No such material.")
    return FileResponse(path)


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")
