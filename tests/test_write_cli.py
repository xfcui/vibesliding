"""Tests for the write CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from src.write.cli import main

PLAN = """# PPT Outline: Loop

---

## Slide 1: Start Here
- Role: cover
- Point: The premise
- Point: The promise
- Visual hook: dark cover

---

## Appendix: Global Visual Requirements
- **Theme:** Navy
"""

BODY = """- **Premise:** Start with the stakes
- **Promise:** Leave with a loop
- **Ask:** Try one pass
[Visual: dark cover]
[Speech: Welcome.]
"""


def test_write_cli_saves_script(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    plan = work / "plan_1.md"
    plan.write_text(PLAN, encoding="utf-8")
    (work / "facts.md").write_text("- **F1 Loop.** Try, measure, update.\n", encoding="utf-8")
    client = SimpleNamespace(
        complete_text_parallel=AsyncMock(return_value=[BODY]),
    )
    config = SimpleNamespace(
        openrouter_api_key="k",
        txt_model="text/model",
        proxy=None,
        max_concurrent=2,
        validate=lambda: None,
    )
    with (
        patch("src.write.cli.load_dotenv"),
        patch("src.write.cli.load_write_config", return_value=config),
        patch("src.write.cli.create_text_client", return_value=client),
        patch("src.write.cli.load_outline_standards", return_value="standards"),
    ):
        result = CliRunner().invoke(
            main,
            ["--work", str(work), "--plan", str(plan)],
        )
    assert result.exit_code == 0, result.output
    script = (work / "script_1.md").read_text(encoding="utf-8")
    assert "Welcome." in script
    assert "python3 -m src.design.cli" in result.output


def test_write_cli_requires_facts(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    plan = work / "plan_1.md"
    plan.write_text(PLAN, encoding="utf-8")
    with (
        patch("src.write.cli.load_dotenv"),
        patch("src.write.cli.load_write_config") as load_config,
    ):
        missing = CliRunner().invoke(main, ["--work", str(work), "--plan", str(plan)])
        (work / "facts.md").write_text("  \n", encoding="utf-8")
        empty = CliRunner().invoke(main, ["--work", str(work), "--plan", str(plan)])
    assert missing.exit_code != 0
    assert "Facts file not found" in missing.output
    assert empty.exit_code != 0
    assert "Facts file is empty" in empty.output
    load_config.assert_not_called()
    assert not (work / "script_1.md").exists()


def test_write_cli_script_name_follows_plan_filename(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    plan = work / "plan_16.md"
    plan.write_text(PLAN, encoding="utf-8")
    (work / "facts.md").write_text("- **F1 Loop.** Try, measure, update.\n", encoding="utf-8")
    client = SimpleNamespace(complete_text_parallel=AsyncMock(return_value=[BODY]))
    config = SimpleNamespace(
        openrouter_api_key="k",
        txt_model="text/model",
        proxy=None,
        max_concurrent=2,
        validate=lambda: None,
    )
    with (
        patch("src.write.cli.load_dotenv"),
        patch("src.write.cli.load_write_config", return_value=config),
        patch("src.write.cli.create_text_client", return_value=client),
        patch("src.write.cli.load_outline_standards", return_value="standards"),
    ):
        result = CliRunner().invoke(main, ["--work", str(work), "--plan", str(plan)])
    assert result.exit_code == 0, result.output
    assert (work / "script_16.md").is_file()
    assert not (work / "script_1.md").exists()


def test_write_cli_rejects_bad_page(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    plan = work / "plan_1.md"
    plan.write_text(PLAN, encoding="utf-8")
    (work / "facts.md").write_text("- **F1 Loop.** Try, measure, update.\n", encoding="utf-8")
    with patch("src.write.cli.load_dotenv"):
        result = CliRunner().invoke(
            main,
            ["--work", str(work), "--plan", str(plan), "--page", "0"],
        )
    assert result.exit_code != 0
    assert "Page numbers must be >= 1" in result.output


def test_write_cli_page_requires_existing_script(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    plan = work / "plan_1.md"
    plan.write_text(PLAN, encoding="utf-8")
    (work / "facts.md").write_text("- **F1 Loop.** Try, measure, update.\n", encoding="utf-8")
    with patch("src.write.cli.load_dotenv"):
        result = CliRunner().invoke(
            main,
            ["--work", str(work), "--plan", str(plan), "--page", "1"],
        )
    assert result.exit_code != 0
    assert "existing script" in result.output
    assert not (work / "script_1.md").exists()
