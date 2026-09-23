"""Tests for shared path conventions."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.paths import (
    DEFAULT_IDEA_PATH,
    DEFAULT_PLAN_PATH,
    DEFAULT_SCRIPT_PATH,
    DEFAULT_STYLE_DIR,
    DEFAULT_WORK_DIR,
    IMAGE_DIR_PREFIX,
    backup_outline_to_image_dir,
    date_slug,
    default_output_dir,
    plan_path_for_slides,
    presentation_video_path,
    read_nonempty_text,
    script_path_for_slides,
    slides_pptx_path,
    style_dir,
    style_images_in_dir,
)


def test_default_work_dir() -> None:
    assert DEFAULT_WORK_DIR == __import__("pathlib").Path("work")


def test_default_idea_and_plan_paths() -> None:
    assert DEFAULT_IDEA_PATH == DEFAULT_WORK_DIR / "idea.md"
    assert DEFAULT_PLAN_PATH == DEFAULT_WORK_DIR / "plan_16.md"
    assert DEFAULT_SCRIPT_PATH == DEFAULT_WORK_DIR / "script_16.md"


def test_default_output_dir_prefix() -> None:
    path = default_output_dir()
    assert path.parent == DEFAULT_WORK_DIR
    assert path.name.startswith(IMAGE_DIR_PREFIX)


def test_default_output_dir_uses_work_dir(tmp_path: Path) -> None:
    path = default_output_dir(tmp_path, "20260923_120000")
    assert path == tmp_path / f"{IMAGE_DIR_PREFIX}20260923_120000"


def test_style_dir_prefers_project_folder(tmp_path: Path) -> None:
    assert style_dir() == DEFAULT_STYLE_DIR == Path("style")
    assert style_dir(tmp_path) == DEFAULT_STYLE_DIR
    project = tmp_path / "style"
    project.mkdir()
    assert style_dir(tmp_path) == project


def test_style_images_in_dir_sorted_and_filtered(tmp_path: Path) -> None:
    (tmp_path / "style_zebra.png").write_bytes(b"z")
    (tmp_path / "style_alpha.JPG").write_bytes(b"a")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "style_deep.png").write_bytes(b"d")

    assert [p.name for p in style_images_in_dir(tmp_path)] == [
        "style_alpha.JPG",
        "style_zebra.png",
    ]


def test_style_images_in_dir_missing_dir(tmp_path: Path) -> None:
    assert style_images_in_dir(tmp_path / "nope") == []


def test_date_slug() -> None:
    assert date_slug("20260610_120000") == "20260610"
    assert date_slug("20260610") == "20260610"
    assert date_slug("test") == "test"


def test_slides_pptx_path() -> None:
    assert slides_pptx_path(DEFAULT_WORK_DIR, "20260610_120000") == (
        DEFAULT_WORK_DIR / "slides_20260610.pptx"
    )
    assert slides_pptx_path(DEFAULT_WORK_DIR, "20260831") == (
        DEFAULT_WORK_DIR / "slides_20260831.pptx"
    )


def test_presentation_video_path() -> None:
    assert presentation_video_path(DEFAULT_WORK_DIR, "20260610_120000") == (
        DEFAULT_WORK_DIR / "presentation_video_20260610_120000.mp4"
    )


def test_plan_and_script_paths() -> None:
    assert plan_path_for_slides(DEFAULT_WORK_DIR, 25) == DEFAULT_WORK_DIR / "plan_25.md"
    assert script_path_for_slides(DEFAULT_WORK_DIR, 25) == DEFAULT_WORK_DIR / "script_25.md"


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
