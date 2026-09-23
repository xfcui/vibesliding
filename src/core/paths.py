"""Shared input/output path conventions."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

DEFAULT_WORK_DIR = Path("work")
DEFAULT_IDEA_PATH = DEFAULT_WORK_DIR / "idea.md"
DEFAULT_PLAN_PATH = DEFAULT_WORK_DIR / "plan_16.md"
DEFAULT_SCRIPT_PATH = DEFAULT_WORK_DIR / "script_16.md"
IDEA_FILENAME = "idea.md"
SOURCE_FILENAME = "source.md"
FACTS_FILENAME = "facts.md"
DESIGN_BRIEF_FILENAME = "design_brief.md"
PLAN_FILENAME_PATTERN = "plan_{n}.md"
SCRIPT_FILENAME_PATTERN = "script_{n}.md"
WRITE_PROMPTS_DIRNAME = "write_prompts"
STYLE_DIRNAME = "style"
DEFAULT_STYLE_DIR = Path(STYLE_DIRNAME)
STYLE_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp"})
IMAGE_DIR_PREFIX = "image_"
OUTPUT_DIR_PREFIX = IMAGE_DIR_PREFIX
SLIDES_PREFIX = "slides_"
PRESENTATION_VIDEO_PREFIX = "presentation_video_"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
DATE_SLUG_LENGTH = 8


def style_dir(work_dir: Path | None = None) -> Path:
    """Style plates for *work_dir* when that folder exists, else the shared ``style/``."""
    if work_dir is not None:
        project_style = work_dir / STYLE_DIRNAME
        if project_style.is_dir():
            return project_style
    return DEFAULT_STYLE_DIR


def style_images_in_dir(directory: Path) -> list[Path]:
    """Every supported style-plate image directly inside *directory*, sorted by name."""
    if not directory.is_dir():
        return []
    return sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in STYLE_IMAGE_EXTENSIONS
        ),
        key=lambda path: path.name,
    )


def timestamp_slug() -> str:
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def default_output_dir(
    work_dir: Path | None = None,
    timestamp: str | None = None,
) -> Path:
    slug = timestamp or timestamp_slug()
    base = work_dir if work_dir is not None else DEFAULT_WORK_DIR
    return base / f"{IMAGE_DIR_PREFIX}{slug}"


def date_slug(timestamp: str) -> str:
    """Return ``YYYYMMDD`` from a timestamp slug, leaving other values unchanged."""
    if len(timestamp) >= DATE_SLUG_LENGTH and timestamp[:DATE_SLUG_LENGTH].isdigit():
        if len(timestamp) == DATE_SLUG_LENGTH or timestamp[DATE_SLUG_LENGTH] == "_":
            return timestamp[:DATE_SLUG_LENGTH]
    return timestamp


def slides_pptx_path(work_dir: Path, timestamp: str) -> Path:
    return work_dir / f"{SLIDES_PREFIX}{date_slug(timestamp)}.pptx"


def presentation_video_path(work_dir: Path, timestamp: str) -> Path:
    return work_dir / f"{PRESENTATION_VIDEO_PREFIX}{timestamp}.mp4"


def timestamp_from_image_dir(path: Path) -> str | None:
    name = path.name
    if not name.startswith(IMAGE_DIR_PREFIX):
        return None
    suffix = name[len(IMAGE_DIR_PREFIX) :]
    return suffix or None


def plan_path_for_slides(work_dir: Path, slide_count: int) -> Path:
    return work_dir / PLAN_FILENAME_PATTERN.format(n=slide_count)


def script_path_for_slides(work_dir: Path, slide_count: int) -> Path:
    return work_dir / SCRIPT_FILENAME_PATTERN.format(n=slide_count)


def backup_outline_to_image_dir(
    outline: Path,
    output_dir: Path,
    *,
    text: str,
) -> Path:
    """Write an outline snapshot into a render image output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / outline.name
    dest.write_text(text, encoding="utf-8")
    return dest


def read_nonempty_text(path: Path, *, label: str | None = None) -> str:
    """Read a UTF-8 text file; raise ValueError if missing or empty."""
    name = label or str(path)
    if not path.is_file():
        raise ValueError(f"{name} not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"{name} is empty: {path}")
    return text
