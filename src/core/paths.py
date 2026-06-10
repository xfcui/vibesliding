"""Shared input/output path conventions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

DEFAULT_WORK_DIR = Path("work")
DEFAULT_IDEA_PATH = DEFAULT_WORK_DIR / "idea.md"
DEFAULT_OUTLINE_PATH = DEFAULT_WORK_DIR / "outline_16.md"
RESEARCH_FILENAME = "research.md"
RESEARCH_STATE_FILENAME = "research_state.json"
IDEA_FILENAME = "idea.md"
SOURCE_FILENAME = "source.md"
OUTLINE_FILENAME_PATTERN = "outline_{n}.md"
IMAGE_DIR_PREFIX = "image_"
OUTPUT_DIR_PREFIX = IMAGE_DIR_PREFIX
PRESENTATION_SLIDES_PDF_PREFIX = "presentation_slides_"
PRESENTATION_SPEECH_PDF_PREFIX = "presentation_speech_"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


def timestamp_slug() -> str:
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def default_output_dir(timestamp: str | None = None) -> Path:
    slug = timestamp or timestamp_slug()
    return DEFAULT_WORK_DIR / f"{IMAGE_DIR_PREFIX}{slug}"


def presentation_slides_pdf_path(work_dir: Path, timestamp: str) -> Path:
    return work_dir / f"{PRESENTATION_SLIDES_PDF_PREFIX}{timestamp}.pdf"


def presentation_speech_pdf_path(work_dir: Path, timestamp: str) -> Path:
    return work_dir / f"{PRESENTATION_SPEECH_PDF_PREFIX}{timestamp}.pdf"


def timestamp_from_image_dir(path: Path) -> str | None:
    name = path.name
    if not name.startswith(IMAGE_DIR_PREFIX):
        return None
    suffix = name[len(IMAGE_DIR_PREFIX) :]
    return suffix or None


def outline_path_for_slides(work_dir: Path, slide_count: int) -> Path:
    return work_dir / OUTLINE_FILENAME_PATTERN.format(n=slide_count)


def read_nonempty_text(path: Path, *, label: str | None = None) -> str:
    """Read a UTF-8 text file; raise ValueError if missing or empty."""
    name = label or str(path)
    if not path.is_file():
        raise ValueError(f"{name} not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"{name} is empty: {path}")
    return text
