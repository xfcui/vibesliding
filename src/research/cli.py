"""CLI entry point for DeepResearch (`python -m src.research.cli`)."""

from __future__ import annotations

from pathlib import Path

import click
from dotenv import load_dotenv

from src.core.config import DeepResearchMode, load_outline_config
from src.core.paths import (
    DEFAULT_WORK_DIR,
    IDEA_FILENAME,
    RESEARCH_FILENAME,
    SOURCES_FILENAME,
    read_nonempty_text,
)
from src.research.deepresearch import (
    TqdmProgressReporter,
    format_sources_for_prompt,
    run_deepresearch,
)

load_dotenv()


@click.command()
@click.option(
    "--work",
    "work_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_WORK_DIR,
    show_default=True,
    help="Work directory containing idea.md; research outputs are written here.",
)
@click.option(
    "--mode",
    type=click.Choice(["fast", "standard", "heavy", "max"], case_sensitive=False),
    default=None,
    help="Valyu DeepResearch mode (default: standard or [valyu] mode in .env).",
)
@click.option(
    "--valyu-api-key",
    envvar="VALYU_API_KEY",
    help="Valyu API key (or VALYU_API_KEY / [valyu] api_key in .env).",
)
def main(
    work_dir: Path,
    mode: str | None,
    valyu_api_key: str | None,
) -> None:
    """Run Valyu DeepResearch on work/idea.md and write research.md + sources.md."""
    work_dir.mkdir(parents=True, exist_ok=True)
    idea_path = work_dir / IDEA_FILENAME
    try:
        idea = read_nonempty_text(idea_path, label="Idea file")
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    mode_override: DeepResearchMode | None = (
        mode.lower()  # type: ignore[assignment]
        if mode is not None
        else None
    )

    config = load_outline_config(
        valyu_api_key_override=valyu_api_key,
        valyu_mode_override=mode_override,
    )
    config.validate_research()

    research_path = work_dir / RESEARCH_FILENAME
    sources_path = work_dir / SOURCES_FILENAME

    click.echo(f"Work dir: {work_dir.resolve()}")
    click.echo(f"Idea: {idea_path.resolve()}")
    click.echo(f"Valyu mode: {config.valyu_mode}")
    click.echo("Starting DeepResearch (this may take several minutes)...")

    progress = TqdmProgressReporter()

    def _on_status_retry(error: str, attempt: int, wait_s: float) -> None:
        click.echo(
            f"Network issue while polling DeepResearch (attempt {attempt}); "
            f"retrying in {wait_s:.0f}s: {error}",
            err=True,
        )

    try:
        result = run_deepresearch(
            idea,
            api_key=config.valyu_api_key or "",
            mode=config.valyu_mode,
            on_progress=progress,
            on_status_retry=_on_status_retry,
        )
    finally:
        progress.close()

    click.echo(f"DeepResearch complete (task {result.task_id}, cost ${result.cost:.4f})")

    research_path.write_text(result.report, encoding="utf-8")
    click.echo(f"Saved research report: {research_path.resolve()}")

    sources_text = format_sources_for_prompt(result.sources)
    sources_path.write_text(sources_text, encoding="utf-8")
    click.echo(f"Saved sources: {sources_path.resolve()}")

    click.echo("")
    click.echo("Review research.md, then generate outlines:")
    click.echo("python3 -m src.outline.cli")


if __name__ == "__main__":
    main()
