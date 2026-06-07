"""Tests for style CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from src.core.paths import IDEA_FILENAME
from src.style.cli import build_style_selector, main, parse_pick_spec

VALID_OUTLINE = """# PPT Outline: Style CLI Test

---

## Slide 1: Start
- **Point:** Example
[Visual: Simple layout]
[Speech: Hello.]

---

## Appendix: Global Visual Requirements
- **Theme:** Minimal
"""


def test_style_cli_generates_references_and_prints_compose_command(
    tmp_path: Path,
) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    outline_path = work_dir / "outline_16.md"
    outline_path.write_text(VALID_OUTLINE, encoding="utf-8")
    (work_dir / IDEA_FILENAME).write_text("Future of AI coding", encoding="utf-8")

    style_paths = [
        work_dir / "style_base.png",
        work_dir / "style_cover.png",
        work_dir / "style_transition.png",
        work_dir / "style_story.png",
    ]

    with (
        patch("src.style.cli.load_dotenv"),
        patch(
            "src.style.cli.load_config",
            return_value=SimpleNamespace(
                validate=lambda: None,
            ),
        ),
        patch("src.style.cli.create_image_client"),
        patch(
            "src.style.cli.generate_style_references",
            new=AsyncMock(return_value=style_paths),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--work", str(work_dir), "--outline", str(outline_path), "--pick", "1,1,1,1"],
        )

    assert result.exit_code == 0, result.output
    assert "Generating style references" in result.output
    assert "style_base.png" in result.output
    assert "style_cover.png" in result.output
    assert "python3 -m src.compose.cli --outline" in result.output
    assert "style_*.png" in result.output


def test_style_cli_missing_outline(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / IDEA_FILENAME).write_text("idea", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--work", str(work_dir), "--outline", str(work_dir / "missing.md")],
    )
    assert result.exit_code != 0
    assert "Outline file" in result.output


def test_parse_pick_spec() -> None:
    picks = parse_pick_spec("2,1,3,4", candidates=4)
    assert picks == {
        "base": 2,
        "cover": 1,
        "transition": 3,
        "story": 4,
    }


def test_parse_pick_spec_invalid_count() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        work_dir = Path("work")
        work_dir.mkdir()
        (work_dir / "outline_16.md").write_text(VALID_OUTLINE, encoding="utf-8")
        (work_dir / IDEA_FILENAME).write_text("idea", encoding="utf-8")

        with (
            patch("src.style.cli.load_dotenv"),
            patch(
                "src.style.cli.load_config",
                return_value=SimpleNamespace(validate=lambda: None),
            ),
        ):
            result = runner.invoke(
                main,
                ["--work", str(work_dir), "--pick", "1,2,3"],
            )
    assert result.exit_code != 0
    assert "four comma-separated indices" in result.output


def test_build_style_selector_with_picks(tmp_path: Path) -> None:
    picks = {"base": 2, "cover": 1, "transition": 3, "story": 4}
    selector = build_style_selector(candidates=4, picks=picks)
    choices = tmp_path / "style_base_choices.png"
    choices.write_bytes(b"x")

    assert selector("base", choices, 4) == 2
    assert selector("cover", choices, 4) == 1
    assert selector("transition", choices, 4) == 3
    assert selector("story", choices, 4) == 4


def test_build_style_selector_non_tty_defaults_to_first(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("src.style.cli.sys.stdin.isatty", lambda: False)
    selector = build_style_selector(candidates=4, picks=None)
    choices = tmp_path / "style_cover_choices.png"
    choices.write_bytes(b"x")
    assert selector("cover", choices, 4) == 1


def test_style_cli_missing_idea(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    outline_path = work_dir / "outline_16.md"
    outline_path.write_text(VALID_OUTLINE, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--work", str(work_dir), "--outline", str(outline_path)],
    )
    assert result.exit_code != 0
    assert "Idea file" in result.output


def test_style_cli_generation_failure(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    outline_path = work_dir / "outline_16.md"
    outline_path.write_text(VALID_OUTLINE, encoding="utf-8")
    (work_dir / IDEA_FILENAME).write_text("idea", encoding="utf-8")

    with (
        patch("src.style.cli.load_dotenv"),
        patch(
            "src.style.cli.load_config",
            return_value=SimpleNamespace(validate=lambda: None),
        ),
        patch("src.style.cli.create_image_client"),
        patch(
            "src.style.cli.generate_style_references",
            new=AsyncMock(side_effect=RuntimeError("API down")),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--work", str(work_dir), "--outline", str(outline_path), "--pick", "1,1,1,1"],
        )

    assert result.exit_code != 0
    assert "Style reference generation failed" in result.output
