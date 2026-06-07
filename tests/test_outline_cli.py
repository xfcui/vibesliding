"""Tests for outline CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from src.core.paths import IDEA_FILENAME, RESEARCH_FILENAME, SOURCES_FILENAME
from src.outline.cli import main


VALID_OUTLINE = """# PPT Outline: CLI Test

---

## Slide 1: Start
- **Point:** Example
- Core insight: Clear takeaway
[Visual: Simple layout]
[Speech: Hello.]

---

## Appendix: Global Visual Requirements
- **Theme:** Minimal
"""


def test_outline_cli_writes_multiple_outlines(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / IDEA_FILENAME).write_text("Future of AI coding", encoding="utf-8")
    (work_dir / RESEARCH_FILENAME).write_text("# Report\n\nFindings.", encoding="utf-8")
    (work_dir / SOURCES_FILENAME).write_text("1. Source", encoding="utf-8")

    with (
        patch("src.outline.cli.load_dotenv"),
        patch(
            "src.outline.cli.load_outline_config",
            return_value=SimpleNamespace(
                openrouter_api_key="or-test-key",
                txt_model="anthropic/claude-sonnet-4",
                proxy=None,
                max_concurrent=2,
                validate_outline=lambda: None,
            ),
        ),
        patch(
            "src.outline.cli.write_outlines_parallel",
            new=AsyncMock(
                return_value=(
                    "### Deck Title\nCLI Test\n\n### Appendix: Global Visual Requirements\n- **Theme:** Minimal",
                    [
                        (6, VALID_OUTLINE, SimpleNamespace(warnings=[])),
                        (12, VALID_OUTLINE, SimpleNamespace(warnings=[])),
                    ],
                )
            ),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--work", str(work_dir), "--slides", "6,12"],
        )

    outline_6 = work_dir / "outline_6.md"
    outline_12 = work_dir / "outline_12.md"

    assert result.exit_code == 0, result.output
    assert outline_6.read_text(encoding="utf-8") == VALID_OUTLINE
    assert outline_12.read_text(encoding="utf-8") == VALID_OUTLINE
    assert (work_dir / "style_base.md").is_file()
    assert "Saved shared style scaffold" in result.output
    assert "python3 -m src.style.cli" in result.output


def test_outline_cli_missing_research_file(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / IDEA_FILENAME).write_text("idea", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["--work", str(work_dir)])
    assert result.exit_code != 0
    assert "Research file" in result.output
