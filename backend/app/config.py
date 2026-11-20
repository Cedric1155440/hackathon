import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_env()


def get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)
