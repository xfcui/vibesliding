"""Tests for style CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from src.core.paths import DESIGN_BRIEF_FILENAME
from src.design.cli import build_style_selector, main, parse_pick_spec

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
    outline_path = work_dir / "script_16.md"
    outline_path.write_text(VALID_OUTLINE, encoding="utf-8")
    (work_dir / DESIGN_BRIEF_FILENAME).write_text("- **Topic family:** test\n", encoding="utf-8")

    style_output = Path("style")
    style_paths = [
        style_output / "style_base_noncontent.png",
        style_output / "style_base_content.png",
        style_output / "style_cover.png",
        style_output / "style_transition.png",
        style_output / "style_content.png",
    ]
    generate_mock = AsyncMock(return_value=style_paths)

    with (
        patch("src.design.cli.load_dotenv"),
        patch(
            "src.design.cli.load_config",
            return_value=SimpleNamespace(
                validate=lambda: None,
            ),
        ),
        patch("src.design.cli.create_image_client"),
        patch(
            "src.design.cli.generate_style_references",
            new=generate_mock,
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--work",
                str(work_dir),
                "--script",
                str(outline_path),
                "--pick",
                "1,1,1,1,1",
            ],
        )

    assert result.exit_code == 0, result.output
    assert "Generating two-tone style plates" in result.output
    assert "style_base_noncontent.png" in result.output
    assert "style_base_content.png" in result.output
    assert "style_cover.png" in result.output
    assert "python3 -m src.render.cli --work" in result.output
    assert "--script" in result.output
    assert f"--style {work_dir / 'style'}" in result.output
    generate_mock.assert_awaited_once()
    assert generate_mock.await_args.kwargs["output_dir"] == work_dir / "style"


def test_style_cli_missing_outline(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / DESIGN_BRIEF_FILENAME).write_text("- **Topic family:** test\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--work", str(work_dir), "--script", str(work_dir / "missing.md")],
    )
    assert result.exit_code != 0
    assert "Script file" in result.output


def test_parse_pick_spec() -> None:
    picks = parse_pick_spec("2,1,3,4,1", candidates=4)
    assert picks == {
        "base_noncontent": 2,
        "base_content": 1,
        "cover": 3,
        "transition": 4,
        "content": 1,
    }


def test_parse_pick_spec_invalid_count() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        work_dir = Path("work")
        work_dir.mkdir()
        (work_dir / "script_16.md").write_text(VALID_OUTLINE, encoding="utf-8")
        (work_dir / DESIGN_BRIEF_FILENAME).write_text("- **Topic family:** test\n", encoding="utf-8")

        with (
            patch("src.design.cli.load_dotenv"),
            patch(
                "src.design.cli.load_config",
                return_value=SimpleNamespace(validate=lambda: None),
            ),
        ):
            result = runner.invoke(
                main,
                ["--work", str(work_dir), "--pick", "1,2,3"],
            )
    assert result.exit_code != 0
    assert "five comma-separated indices" in result.output


def test_build_style_selector_with_picks(tmp_path: Path) -> None:
    picks = {
        "base_noncontent": 2,
        "base_content": 1,
        "cover": 1,
        "transition": 3,
        "content": 4,
    }
    selector = build_style_selector(candidates=4, picks=picks)
    choices = tmp_path / "style_base_noncontent_choices.png"
    choices.write_bytes(b"x")

    assert selector("base_noncontent", choices, 4) == 2
    assert selector("base_content", choices, 4) == 1
    assert selector("cover", choices, 4) == 1
    assert selector("transition", choices, 4) == 3
    assert selector("content", choices, 4) == 4


def test_build_style_selector_non_tty_defaults_to_first(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("src.design.cli.sys.stdin.isatty", lambda: False)
    selector = build_style_selector(candidates=4, picks=None)
    choices = tmp_path / "style_cover_choices.png"
    choices.write_bytes(b"x")
    assert selector("cover", choices, 4) == 1


def test_style_cli_missing_idea(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    outline_path = work_dir / "script_16.md"
    outline_path.write_text(VALID_OUTLINE, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--work", str(work_dir), "--script", str(outline_path)],
    )
    assert result.exit_code != 0
    assert "Design brief" in result.output


def test_style_cli_generation_failure(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    outline_path = work_dir / "script_16.md"
    outline_path.write_text(VALID_OUTLINE, encoding="utf-8")
    (work_dir / DESIGN_BRIEF_FILENAME).write_text("- **Topic family:** test\n", encoding="utf-8")

    with (
        patch("src.design.cli.load_dotenv"),
        patch(
            "src.design.cli.load_config",
            return_value=SimpleNamespace(validate=lambda: None),
        ),
        patch("src.design.cli.create_image_client"),
        patch(
            "src.design.cli.generate_style_references",
            new=AsyncMock(side_effect=RuntimeError("API down")),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--work",
                str(work_dir),
                "--script",
                str(outline_path),
                "--pick",
                "1,1,1,1,1",
            ],
        )

    assert result.exit_code != 0
    assert "Style plate generation failed" in result.output
