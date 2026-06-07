"""Tests for shared path conventions."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.paths import (
    DEFAULT_IDEA_PATH,
    DEFAULT_OUTLINE_PATH,
    DEFAULT_WORK_DIR,
    OUTPUT_DIR_PREFIX,
    default_output_dir,
    outline_path_for_slides,
    read_nonempty_text,
)


def test_default_work_dir() -> None:
    assert DEFAULT_WORK_DIR == __import__("pathlib").Path("work")


def test_default_idea_and_outline_paths() -> None:
    assert DEFAULT_IDEA_PATH == DEFAULT_WORK_DIR / "idea.md"
    assert DEFAULT_OUTLINE_PATH == DEFAULT_WORK_DIR / "outline_16.md"


def test_default_output_dir_prefix() -> None:
    path = default_output_dir()
    assert path.name.startswith(OUTPUT_DIR_PREFIX)


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
