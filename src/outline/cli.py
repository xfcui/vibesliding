"""CLI entry point for outline generation (`python -m src.outline.cli`)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click
from dotenv import load_dotenv

from src.core.client_factory import create_text_client
from src.core.config import load_outline_config
from src.core.paths import (
    DEFAULT_WORK_DIR,
    IDEA_FILENAME,
    RESEARCH_FILENAME,
    SOURCE_FILENAME,
    outline_path_for_slides,
    read_nonempty_text,
)

STYLE_SCAFFOLD_FILENAME = "style_base.md"
from src.outline.writer import write_outlines_parallel

load_dotenv()

DEFAULT_SLIDE_COUNTS = "16,25,36"


def _parse_slide_counts(spec: str) -> list[int]:
    counts: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            value = int(part)
        except ValueError as exc:
            raise click.UsageError(
                f"Invalid --slides value {part!r}; expected comma-separated integers."
            ) from exc
        if value < 1:
            raise click.UsageError("--slides values must be at least 1.")
        counts.append(value)
    if not counts:
        raise click.UsageError("--slides must include at least one slide count.")
    return counts


@click.command()
@click.option(
    "--work",
    "work_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_WORK_DIR,
    show_default=True,
    help="Work directory with research.md and idea.md.",
)
@click.option(
    "--slides",
    default=DEFAULT_SLIDE_COUNTS,
    show_default=True,
    help="Comma-separated content slide counts (e.g. 16,25,36).",
)
@click.option(
    "--api-key",
    envvar="OPENROUTER_API_KEY",
    help="OpenRouter API key for outline text generation.",
)
@click.option(
    "--txt-model",
    "txt_model",
    default=None,
    help="OpenRouter text model (or OPENROUTER_TXT_MODEL / [openrouter] txt_model).",
)
@click.option(
    "--proxy",
    default=None,
    help="HTTP/HTTPS proxy URL for OpenRouter text calls.",
)
def main(
    work_dir: Path,
    slides: str,
    api_key: str | None,
    txt_model: str | None,
    proxy: str | None,
) -> None:
    """Turn research.md into one or more presentation outlines in the work dir."""
    work_dir.mkdir(parents=True, exist_ok=True)
    slide_counts = _parse_slide_counts(slides)

    research_path = work_dir / RESEARCH_FILENAME
    idea_path = work_dir / IDEA_FILENAME
    source_path = work_dir / SOURCE_FILENAME

    source = None
    try:
        idea = read_nonempty_text(idea_path, label="Idea file")
        report = read_nonempty_text(research_path, label="Research file")
        if source_path.is_file():
            try:
                source = read_nonempty_text(source_path, label="Source file")
            except ValueError as exc:
                click.echo(f"Warning: {exc}", err=True)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    config = load_outline_config(
        openrouter_api_key_override=api_key,
        txt_model_override=txt_model,
        proxy_override=proxy,
    )
    config.validate_outline()

    click.echo(f"Work dir: {work_dir.resolve()}")
    if source:
        click.echo(f"Source: {source_path.resolve()}")
    click.echo(f"Research: {research_path.resolve()}")
    click.echo(f"Target content slides: {slide_counts} (excluding cover, transition, ending)")
    click.echo(f"Text model: {config.txt_model}")
    click.echo("Writing shared style scaffold, then outline versions with OpenRouter...")

    client = create_text_client(
        api_key=config.openrouter_api_key or "",
        proxy=config.proxy,
        model=config.txt_model,
        max_concurrent=config.max_concurrent,
    )

    async def _run_all() -> tuple[str, list[tuple[int, str, object]]]:
        return await write_outlines_parallel(
            client,
            idea=idea,
            report=report,
            source=source,
            target_slides=slide_counts,
            text_model=config.txt_model,
        )

    try:
        style_scaffold, results = asyncio.run(_run_all())
    except Exception as exc:
        raise click.ClickException(f"Outline generation failed: {exc}") from exc

    scaffold_path = work_dir / STYLE_SCAFFOLD_FILENAME
    scaffold_path.write_text(style_scaffold, encoding="utf-8")
    click.echo(f"Saved shared style scaffold: {scaffold_path.resolve()}")

    for target_slides, outline, validation in results:
        outline_path = outline_path_for_slides(work_dir, target_slides)
        outline_path.write_text(outline, encoding="utf-8")
        click.echo(f"Saved outline: {outline_path.resolve()}")
        if validation.warnings:
            click.echo(f"Validation warnings for {outline_path.name}:", err=True)
            for warning in validation.warnings:
                click.echo(f"  - {warning}", err=True)

    default_outline = outline_path_for_slides(work_dir, slide_counts[0])
    click.echo("")
    click.echo("Review and edit the outlines, then generate style references:")
    if work_dir != DEFAULT_WORK_DIR:
        click.echo(f"python3 -m src.style.cli --work {work_dir} --outline {default_outline}")
    else:
        click.echo(f"python3 -m src.style.cli --outline {default_outline}")


if __name__ == "__main__":
    main()
