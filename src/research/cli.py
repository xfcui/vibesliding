"""CLI entry point for DeepResearch (`python -m src.research.cli`)."""

from __future__ import annotations

import os
from pathlib import Path

import click
from dotenv import load_dotenv

from src.core.config import DeepResearchMode, load_outline_config
from src.core.paths import (
    DEFAULT_WORK_DIR,
    IDEA_FILENAME,
    RESEARCH_FILENAME,
    RESEARCH_STATE_FILENAME,
    read_nonempty_text,
)
from src.research.deepresearch import (
    TqdmProgressReporter,
    clear_research_state,
    load_research_state,
    resume_deepresearch,
    run_deepresearch,
)

load_dotenv()


def _write_research_report(work_dir: Path, *, report: str) -> Path:
    research_path = work_dir / RESEARCH_FILENAME
    research_path.write_text(report, encoding="utf-8")
    return research_path


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
@click.option(
    "--categories",
    default=None,
    help=(
        "Comma-separated Valyu datasource categories to include "
        "(or VALYU_CATEGORIES / [valyu] categories in .env)."
    ),
)
@click.option(
    "--resume",
    is_flag=True,
    help=(
        "Resume polling an in-progress DeepResearch task from "
        f"{RESEARCH_STATE_FILENAME} (or --task-id)."
    ),
)
@click.option(
    "--task-id",
    default=None,
    help="Valyu DeepResearch task ID to resume (overrides state file task_id).",
)
@click.option(
    "--fresh",
    is_flag=True,
    help="Start a new DeepResearch task even if a resume state file exists.",
)
def main(
    work_dir: Path,
    mode: str | None,
    valyu_api_key: str | None,
    categories: str | None,
    resume: bool,
    task_id: str | None,
    fresh: bool,
) -> None:
    """Run Valyu DeepResearch on work/idea.md and write research.md."""
    if resume and fresh:
        raise click.UsageError("Use either --resume or --fresh, not both.")

    work_dir.mkdir(parents=True, exist_ok=True)
    state_path = work_dir / RESEARCH_STATE_FILENAME

    mode_override: DeepResearchMode | None = (
        mode.lower()  # type: ignore[assignment]
        if mode is not None
        else None
    )

    config = load_outline_config(
        valyu_api_key_override=valyu_api_key,
        valyu_mode_override=mode_override,
        valyu_categories_override=categories,
    )
    if config.valyu_proxy:
        os.environ["HTTP_PROXY"] = config.valyu_proxy
        os.environ["HTTPS_PROXY"] = config.valyu_proxy
        os.environ["ALL_PROXY"] = config.valyu_proxy
    else:
        for env_var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            os.environ.pop(env_var, None)
    config.validate_research()

    click.echo(f"Work dir: {work_dir.resolve()}")

    progress = TqdmProgressReporter()

    def _on_status_retry(error: str, attempt: int, wait_s: float) -> None:
        click.echo(
            f"Network issue while polling DeepResearch (attempt {attempt}); "
            f"retrying in {wait_s:.0f}s: {error}",
            err=True,
        )

    try:
        if resume or task_id is not None:
            saved_state = None
            if task_id is None:
                try:
                    saved_state = load_research_state(state_path)
                except ValueError as exc:
                    raise click.UsageError(str(exc)) from exc
                task_id = saved_state.task_id

            resume_mode = (
                mode_override
                if mode_override is not None
                else (saved_state.mode if saved_state is not None else config.valyu_mode)
            )
            click.echo(f"Resuming DeepResearch task {task_id} (mode: {resume_mode})...")
            result = resume_deepresearch(
                task_id,
                api_key=config.valyu_api_key or "",
                mode=resume_mode,
                on_progress=progress,
                on_status_retry=_on_status_retry,
                state_path=state_path if saved_state is not None else None,
            )
        else:
            if state_path.is_file() and not fresh:
                raise click.UsageError(
                    f"Incomplete DeepResearch run detected ({state_path.name}). "
                    "Run with --resume to continue polling the existing task, "
                    "or --fresh to start a new one."
                )
            if fresh and state_path.is_file():
                clear_research_state(state_path)
                click.echo("Cleared previous research state; starting fresh.")

            idea_path = work_dir / IDEA_FILENAME
            try:
                idea = read_nonempty_text(idea_path, label="Idea file")
            except ValueError as exc:
                raise click.UsageError(str(exc)) from exc

            click.echo(f"Idea: {idea_path.resolve()}")
            click.echo(f"Valyu mode: {config.valyu_mode}")
            if config.valyu_categories:
                click.echo(f"Valyu categories: {', '.join(config.valyu_categories)}")
            else:
                click.echo("Valyu categories: all")
            click.echo("Starting DeepResearch (this may take several minutes)...")

            result = run_deepresearch(
                idea,
                api_key=config.valyu_api_key or "",
                mode=config.valyu_mode,
                categories=config.valyu_categories,
                on_progress=progress,
                on_status_retry=_on_status_retry,
                state_path=state_path,
            )
    finally:
        progress.close()

    if state_path.is_file():
        clear_research_state(state_path)

    click.echo(f"DeepResearch complete (task {result.task_id}, cost ${result.cost:.4f})")

    research_path = _write_research_report(work_dir, report=result.report)
    click.echo(f"Saved research report: {research_path.resolve()}")

    click.echo("")
    click.echo("Review research.md, then generate outlines:")
    click.echo("python3 -m src.outline.cli")


if __name__ == "__main__":
    main()
