"""Path and glob resolution for CLI and generator."""

from __future__ import annotations

import glob as glob_module
from collections.abc import Callable
from pathlib import Path


class PathResolveError(Exception):
    """Raised when path resolution fails; callers map to UsageError/ValueError."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def clean_path_pattern(pattern: str) -> str:
    """Normalize outline/CLI path patterns while preserving spaces in filenames."""
    pattern = pattern.strip().strip("\"'")
    return pattern[1:] if pattern.startswith("@") else pattern


def has_glob_chars(pattern: str) -> bool:
    return any(char in pattern for char in "*?[]")


def expand_path_pattern(
    pattern: str,
    *,
    base_dir: Path | None = None,
    include_parent_base: bool = False,
) -> list[Path]:
    """Expand one path or glob pattern into concrete filesystem paths."""
    path = Path(pattern).expanduser()
    candidates = [path]
    if not path.is_absolute() and base_dir is not None:
        candidates.append(base_dir / pattern)
        if include_parent_base:
            candidates.append(base_dir.parent / pattern)

    if has_glob_chars(pattern):
        matched: list[Path] = []
        for candidate in candidates:
            matched.extend(Path(p) for p in glob_module.glob(str(candidate)))
        return matched

    for candidate in candidates:
        if candidate.exists():
            return [candidate]
    return []


def unique_paths(paths: list[Path], *, sort: bool = False) -> list[Path]:
    """Deduplicate paths by resolved location, optionally sorting first."""
    seen: set[Path] = set()
    unique: list[Path] = []
    iterable = sorted(paths, key=lambda p: str(p.resolve())) if sort else paths
    for path in iterable:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def validate_file_extensions(
    paths: list[Path],
    supported_extensions: frozenset[str],
    *,
    not_file_error: Callable[[Path], str],
    bad_extension_error: Callable[[Path, str], str],
) -> list[Path]:
    """Ensure every path is a file with an allowed extension."""
    for path in paths:
        if not path.is_file():
            raise PathResolveError(not_file_error(path))
        suffix = path.suffix.lower()
        if suffix not in supported_extensions:
            raise PathResolveError(bad_extension_error(path, suffix))
    return paths


def resolve_patterns(
    patterns: list[str],
    *,
    supported_extensions: frozenset[str],
    base_dir: Path | None = None,
    include_parent_base: bool = False,
    sort: bool = False,
    normalize: Callable[[str], str] = clean_path_pattern,
    glob_miss_error: Callable[[str], str],
    file_miss_error: Callable[[str], str],
    not_file_error: Callable[[Path], str],
    bad_extension_error: Callable[[Path, str], str],
) -> list[Path]:
    """Expand, deduplicate, and validate a list of path/glob patterns."""
    all_paths: list[Path] = []

    for raw in patterns:
        pattern = normalize(raw)
        if not pattern:
            continue
        matched = expand_path_pattern(
            pattern,
            base_dir=base_dir,
            include_parent_base=include_parent_base,
        )
        if not matched:
            if has_glob_chars(pattern):
                raise PathResolveError(glob_miss_error(pattern))
            raise PathResolveError(file_miss_error(pattern))
        all_paths.extend(matched)

    unique = unique_paths(all_paths, sort=sort)
    return validate_file_extensions(
        unique,
        supported_extensions,
        not_file_error=not_file_error,
        bad_extension_error=bad_extension_error,
    )
