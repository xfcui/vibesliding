"""Tests for shared path conventions."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.paths import (
    DEFAULT_IDEA_PATH,
    DEFAULT_OUTLINE_PATH,
    DEFAULT_WORK_DIR,
    IMAGE_DIR_PREFIX,
    backup_outline_to_image_dir,
    default_output_dir,
    outline_path_for_slides,
    presentation_slides_pdf_path,
    presentation_video_path,
    read_nonempty_text,
)


def test_default_work_dir() -> None:
    assert DEFAULT_WORK_DIR == __import__("pathlib").Path("work")


def test_default_idea_and_outline_paths() -> None:
    assert DEFAULT_IDEA_PATH == DEFAULT_WORK_DIR / "idea.md"
    assert DEFAULT_OUTLINE_PATH == DEFAULT_WORK_DIR / "outline_16.md"


def test_default_output_dir_prefix() -> None:
    path = default_output_dir()
    assert path.parent == DEFAULT_WORK_DIR
    assert path.name.startswith(IMAGE_DIR_PREFIX)


def test_presentation_slides_pdf_path() -> None:
    assert presentation_slides_pdf_path(DEFAULT_WORK_DIR, "20260610_120000") == (
        DEFAULT_WORK_DIR / "presentation_slides_20260610_120000.pdf"
    )


def test_presentation_video_path() -> None:
    assert presentation_video_path(DEFAULT_WORK_DIR, "20260610_120000") == (
        DEFAULT_WORK_DIR / "presentation_video_20260610_120000.mp4"
    )


def test_outline_path_for_slides() -> None:
    assert outline_path_for_slides(DEFAULT_WORK_DIR, 25) == DEFAULT_WORK_DIR / "outline_25.md"


def test_read_nonempty_text_success(tmp_path: Path) -> None:
    path = tmp_path / "idea.md"
    path.write_text("  Future of AI  \n", encoding="utf-8")
    assert read_nonempty_text(path) == "Future of AI"


def test_read_nonempty_text_missing(tmp_path: Path) -> None:
    path = tmp_path / "missing.md"
    with pytest.raises(ValueError, match="not found"):
        read_nonempty_text(path, label="Idea file")


def test_read_nonempty_text_empty(tmp_path: Path) -> None:
    path = tmp_path / "empty.md"
    path.write_text("   \n", encoding="utf-8")
    with pytest.raises(ValueError, match="is empty"):
        read_nonempty_text(path)


def test_backup_outline_to_image_dir(tmp_path: Path) -> None:
    outline = tmp_path / "outline_31.md"
    outline.write_text("# Deck\n\nSlide content\n", encoding="utf-8")
    image_dir = tmp_path / "work" / "image_test"
    text = outline.read_text(encoding="utf-8")

    dest = backup_outline_to_image_dir(outline, image_dir, text=text)

    assert dest == image_dir / "outline_31.md"
    assert dest.read_text(encoding="utf-8") == text
    assert image_dir.is_dir()
