import sqlite3
from pathlib import Path

from app import config

DATA_DIR = Path(config.get("DATA_DIR", str(config.ROOT / "data")))

SCHEMA = """
CREATE TABLE IF NOT EXISTS materials (
    id        INTEGER PRIMARY KEY,
    kurs      TEXT NOT NULL,            -- Untis course code, e.g. "E5-GK3"
    kind      TEXT NOT NULL,            -- exam | worksheet | book | board | notes
    title     TEXT NOT NULL DEFAULT '',
    filename  TEXT NOT NULL,            -- original name, display only
    path      TEXT NOT NULL,            -- stored file, relative to DATA_DIR
    sha256    TEXT NOT NULL,
    ocr_text  TEXT NOT NULL DEFAULT '',
    created   TEXT NOT NULL,
    UNIQUE (kurs, sha256)
);
CREATE VIRTUAL TABLE IF NOT EXISTS materials_fts USING fts5(title, ocr_text);
"""


def connect() -> sqlite3.Connection:
    """New connection per call; FastAPI runs sync endpoints in a thread pool."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(Path(config.get("DB_PATH", str(DATA_DIR / "app.db"))))
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con
