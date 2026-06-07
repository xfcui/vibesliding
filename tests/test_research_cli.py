"""Tests for research CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from click.testing import CliRunner

from src.core.paths import IDEA_FILENAME, RESEARCH_FILENAME, SOURCES_FILENAME
from src.research import ResearchResult
from src.research.cli import main


def test_research_cli_writes_work_dir_and_prints_next_command(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    idea_path = work_dir / IDEA_FILENAME
    idea_path.write_text("Future of AI coding", encoding="utf-8")

    research = ResearchResult(
        report="# Report\n\nFindings.",
        sources=[SimpleNamespace(title="S1", url="https://x.com", snippet="")],
        cost=0.42,
        task_id="dr_cli_test",
    )

    with (
        patch("src.research.cli.load_dotenv"),
        patch(
            "src.research.cli.load_outline_config",
            return_value=SimpleNamespace(
                valyu_api_key="valyu-test-key",
                valyu_mode="fast",
                validate_research=lambda: None,
            ),
        ),
        patch("src.research.cli.run_deepresearch", return_value=research),
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--work", str(work_dir)])

    research_path = work_dir / RESEARCH_FILENAME
    sources_path = work_dir / SOURCES_FILENAME

    assert result.exit_code == 0, result.output
    assert research_path.read_text(encoding="utf-8") == research.report
    assert "S1" in sources_path.read_text(encoding="utf-8")
    assert "python3 -m src.outline.cli" in result.output


def test_research_cli_missing_idea_file(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    runner = CliRunner()
    result = runner.invoke(main, ["--work", str(work_dir)])
    assert result.exit_code != 0
    assert "Idea file" in result.output
