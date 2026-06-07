"""Shared input/output path conventions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

DEFAULT_WORK_DIR = Path("work")
DEFAULT_IDEA_PATH = DEFAULT_WORK_DIR / "idea.md"
DEFAULT_OUTLINE_PATH = DEFAULT_WORK_DIR / "outline_16.md"
RESEARCH_FILENAME = "research.md"
SOURCES_FILENAME = "sources.md"
IDEA_FILENAME = "idea.md"
OUTLINE_FILENAME_PATTERN = "outline_{n}.md"
OUTPUT_DIR_PREFIX = "slides_"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


def timestamp_slug() -> str:
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def default_output_dir() -> Path:
    return Path(f"./{OUTPUT_DIR_PREFIX}{timestamp_slug()}")


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
