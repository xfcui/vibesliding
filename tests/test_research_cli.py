"""Tests for research CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from src.core.paths import (
    IDEA_FILENAME,
    RESEARCH_FILENAME,
    RESEARCH_STATE_FILENAME,
)
from src.research import ResearchResult, ResearchState
from src.research.cli import main
from src.research.deepresearch import save_research_state


def _mock_research_config(**overrides: object) -> SimpleNamespace:
    defaults = {
        "valyu_api_key": "valyu-test-key",
        "valyu_mode": "fast",
        "valyu_categories": (),
        "valyu_proxy": None,
        "validate_research": lambda: None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


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
            return_value=_mock_research_config(),
        ),
        patch("src.research.cli.run_deepresearch", return_value=research),
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--work", str(work_dir)])

    research_path = work_dir / RESEARCH_FILENAME

    assert result.exit_code == 0, result.output
    assert research_path.read_text(encoding="utf-8") == research.report
    assert "python3 -m src.outline.cli" in result.output


def test_research_cli_missing_idea_file(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    with (
        patch("src.research.cli.load_dotenv"),
        patch(
            "src.research.cli.load_outline_config",
            return_value=_mock_research_config(),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--work", str(work_dir)])
    assert result.exit_code != 0
    assert "Idea file" in result.output


def test_research_cli_blocks_when_state_exists(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / IDEA_FILENAME).write_text("Future of AI coding", encoding="utf-8")
    save_research_state(
        work_dir / RESEARCH_STATE_FILENAME,
        ResearchState(task_id="dr_pending", mode="fast"),
    )

    with (
        patch("src.research.cli.load_dotenv"),
        patch(
            "src.research.cli.load_outline_config",
            return_value=_mock_research_config(),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--work", str(work_dir)])

    assert result.exit_code != 0
    assert "--resume" in result.output
    assert "--fresh" in result.output


def test_research_cli_resume_writes_outputs(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    save_research_state(
        work_dir / RESEARCH_STATE_FILENAME,
        ResearchState(task_id="dr_resume_cli", mode="fast"),
    )

    research = ResearchResult(
        report="# Resumed\n\nFindings.",
        sources=[SimpleNamespace(title="S2", url="https://y.com", snippet="")],
        cost=0.11,
        task_id="dr_resume_cli",
    )

    with (
        patch("src.research.cli.load_dotenv"),
        patch(
            "src.research.cli.load_outline_config",
            return_value=_mock_research_config(),
        ),
        patch("src.research.cli.resume_deepresearch", return_value=research),
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--work", str(work_dir), "--resume"])

    assert result.exit_code == 0, result.output
    assert (work_dir / RESEARCH_FILENAME).read_text(encoding="utf-8") == research.report
    assert "Resuming DeepResearch task dr_resume_cli" in result.output
    assert not (work_dir / RESEARCH_STATE_FILENAME).is_file()


def test_research_cli_fresh_clears_state_and_starts_new(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / IDEA_FILENAME).write_text("Future of AI coding", encoding="utf-8")
    save_research_state(
        work_dir / RESEARCH_STATE_FILENAME,
        ResearchState(task_id="dr_old", mode="fast"),
    )

    research = ResearchResult(
        report="# Fresh\n\nFindings.",
        sources=[],
        cost=0.2,
        task_id="dr_new",
    )

    with (
        patch("src.research.cli.load_dotenv"),
        patch(
            "src.research.cli.load_outline_config",
            return_value=_mock_research_config(),
        ),
        patch("src.research.cli.run_deepresearch", return_value=research) as mock_run,
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--work", str(work_dir), "--fresh"])

    assert result.exit_code == 0, result.output
    mock_run.assert_called_once()
    assert (work_dir / RESEARCH_FILENAME).read_text(encoding="utf-8") == research.report
