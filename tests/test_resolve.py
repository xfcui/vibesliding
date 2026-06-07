"""Tests for path/glob resolution helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.resolve import (
    PathResolveError,
    clean_path_pattern,
    expand_path_pattern,
    has_glob_chars,
    resolve_patterns,
    unique_paths,
    validate_file_extensions,
)


def test_clean_path_pattern_strips_quotes_and_at_prefix() -> None:
    assert clean_path_pattern('  "@photos/hero.png"  ') == "photos/hero.png"
    assert clean_path_pattern("plain.md") == "plain.md"


def test_has_glob_chars() -> None:
    assert has_glob_chars("style_*.png")
    assert not has_glob_chars("style_cover.png")


def test_expand_path_pattern_resolves_relative_to_base_dir(tmp_path: Path) -> None:
    sub = tmp_path / "refs"
    sub.mkdir()
    img = sub / "hero.png"
    img.write_bytes(b"x")

    got = expand_path_pattern("hero.png", base_dir=sub)
    assert got == [img]


def test_expand_path_pattern_include_parent_base(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    child = parent / "child"
    child.mkdir(parents=True)
    img = parent / "style.png"
    img.write_bytes(b"x")

    got = expand_path_pattern("style.png", base_dir=child, include_parent_base=True)
    assert got == [img]


def test_expand_path_pattern_glob(tmp_path: Path) -> None:
    (tmp_path / "a.png").write_bytes(b"a")
    (tmp_path / "b.png").write_bytes(b"b")

    matched = expand_path_pattern(str(tmp_path / "*.png"))
    assert {p.name for p in matched} == {"a.png", "b.png"}


def test_unique_paths_deduplicates_and_sorts(tmp_path: Path) -> None:
    first = tmp_path / "alpha.png"
    second = tmp_path / "beta.png"
    first.write_bytes(b"1")
    second.write_bytes(b"2")

    unique = unique_paths([second, first, first], sort=True)
    assert unique == [first, second]


def test_validate_file_extensions_rejects_directory(tmp_path: Path) -> None:
    directory = tmp_path / "folder"
    directory.mkdir()
    with pytest.raises(PathResolveError, match="Not a file"):
        validate_file_extensions(
            [directory],
            frozenset({".png"}),
            not_file_error=lambda p: f"Not a file: {p}",
            bad_extension_error=lambda p, s: f"Bad: {s}",
        )


def test_resolve_patterns_glob_miss(tmp_path: Path) -> None:
    with pytest.raises(PathResolveError, match="No files found"):
        resolve_patterns(
            [str(tmp_path / "missing_*.png")],
            supported_extensions=frozenset({".png"}),
            glob_miss_error=lambda p: f"No files found matching pattern: {p}",
            file_miss_error=lambda p: f"File not found: {p}",
            not_file_error=lambda p: f"Not a file: {p}",
            bad_extension_error=lambda p, s: f"Bad ext: {s}",
        )


def test_resolve_patterns_file_miss(tmp_path: Path) -> None:
    with pytest.raises(PathResolveError, match="File not found"):
        resolve_patterns(
            ["does-not-exist.png"],
            supported_extensions=frozenset({".png"}),
            glob_miss_error=lambda p: f"No files found matching pattern: {p}",
            file_miss_error=lambda p: f"File not found: {p}",
            not_file_error=lambda p: f"Not a file: {p}",
            bad_extension_error=lambda p, s: f"Bad ext: {s}",
        )


def test_resolve_patterns_bad_extension(tmp_path: Path) -> None:
    gif = tmp_path / "anim.gif"
    gif.write_bytes(b"g")
    with pytest.raises(PathResolveError, match="Bad ext"):
        resolve_patterns(
            [str(gif)],
            supported_extensions=frozenset({".png"}),
            glob_miss_error=lambda p: f"No files found matching pattern: {p}",
            file_miss_error=lambda p: f"File not found: {p}",
            not_file_error=lambda p: f"Not a file: {p}",
            bad_extension_error=lambda p, s: f"Bad ext: {s}",
        )
