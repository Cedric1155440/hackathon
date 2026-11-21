from pathlib import Path


def extract_text(path: Path) -> str:
    """Read the text out of a photo. Returns "" until a reader is plugged in.

    Candidates: a vision-capable llama-server (needs an mmproj), or Tesseract.
    Uploads work without it; they just stay unsearchable by content.
    """
    return ""
