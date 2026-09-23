"""CLI entry point for slide scripts (`python -m src.write.cli`)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click
from dotenv import load_dotenv

from src.core.client_factory import create_text_client
from src.core.config import load_write_config
from src.core.paths import (
    DEFAULT_WORK_DIR,
    DESIGN_BRIEF_FILENAME,
    FACTS_FILENAME,
    IDEA_FILENAME,
    WRITE_PROMPTS_DIRNAME,
    read_nonempty_text,
    script_path_for_slides,
)
from src.core.validate import (
    balance_warnings,
    load_outline_standards,
    speech_warnings,
    validate_outline,
)
from src.plan.cli import content_count_from_name
from src.plan.parse import parse_plan
from src.plan.validate import content_slide_count
from src.render.cli import parse_page_spec
from src.write.writer import write_script

load_dotenv()


@click.command()
@click.option(
    "--work",
    "work_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_WORK_DIR,
    show_default=True,
    help="Work directory with the plan, idea, and facts.",
)
@click.option(
    "--plan",
    "plan_path",
    type=click.Path(path_type=Path),
    required=True,
    help="Deck plan markdown (plan_N.md).",
)
@click.option(
    "--page",
    default=None,
    help="Slides to rewrite (e.g. '3,7-9'). Merges into an existing script.",
)
@click.option(
    "--txt-model",
    "txt_model",
    default=None,
    help="Text model (or OPENROUTER_TXT_MODEL / VOLCENGINE_TXT_MODEL / MINIMAX_TXT_MODEL).",
)
@click.option(
    "--api-key",
    envvar="OPENROUTER_API_KEY",
    help="OpenRouter API key for slide script generation.",
)
@click.option(
    "--proxy",
    default=None,
    help="HTTP/HTTPS proxy URL for text calls.",
)
def main(
    work_dir: Path,
    plan_path: Path,
    page: str | None,
    txt_model: str | None,
    api_key: str | None,
    proxy: str | None,
) -> None:
    """Expand a deck plan into a script, one text-model call per slide."""
    work_dir.mkdir(parents=True, exist_ok=True)
    try:
        plan_text = read_nonempty_text(plan_path, label="Plan file")
        facts = read_nonempty_text(work_dir / FACTS_FILENAME, label="Facts file")
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    idea = _optional_text(work_dir / IDEA_FILENAME, "Idea file")
    document = parse_plan(plan_text)
    try:
        page_filter = parse_page_spec(page)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    named = content_count_from_name(plan_path)
    counted = content_slide_count(document) or len(document.slides)
    count = named if named is not None else counted
    script_path = script_path_for_slides(work_dir, count)
    existing = script_path.read_text(encoding="utf-8") if script_path.is_file() else None
    if page_filter is not None and not (existing and existing.strip()):
        raise click.UsageError(
            f"--page needs an existing script to merge into: {script_path}"
        )

    config = load_write_config(
        openrouter_api_key_override=api_key,
        txt_model_override=txt_model,
        proxy_override=proxy,
    )
    config.validate()
    client = create_text_client(
        api_key=config.openrouter_api_key or "",
        proxy=config.proxy,
        model=config.txt_model,
        max_concurrent=config.max_concurrent,
    )

    click.echo(f"Work dir: {work_dir.resolve()}")
    click.echo(f"Plan: {plan_path.resolve()}")
    click.echo(f"Script: {script_path.resolve()}")
    click.echo(f"Text model: {config.txt_model}")

    async def _run() -> tuple[str, list]:
        return await write_script(
            client,
            document,
            idea=idea,
            facts=facts,
            standards=load_outline_standards(),
            prompt_dir=work_dir / WRITE_PROMPTS_DIRNAME,
            text_model=config.txt_model,
            page_filter=page_filter,
            existing_script=existing,
        )

    try:
        script, drafts = asyncio.run(_run())
    except Exception as exc:
        raise click.ClickException(f"Script generation failed: {exc}") from exc

    script_path.write_text(script, encoding="utf-8")
    click.echo(f"Saved script: {script_path.resolve()}")

    script_warnings = (
        validate_outline(script).warnings + balance_warnings(script) + speech_warnings(script)
    )
    if script_warnings:
        click.echo(
            "Script checks (structure, page numbers, text/visual balance, speech length):",
            err=True,
        )
        for warning in script_warnings:
            click.echo(f"  - {warning}", err=True)

    failed = [draft for draft in drafts if draft.failed]
    if failed:
        pages = ",".join(str(draft.index) for draft in failed)
        click.echo(f"Failed slides: {pages}", err=True)
        for draft in failed:
            click.echo(f"  - slide {draft.index}: {'; '.join(draft.reasons)}", err=True)
        click.echo(
            "Rerun failed slides with:\n"
            f"python3 -m src.write.cli --work {work_dir} --plan {plan_path} --page {pages}",
            err=True,
        )
    else:
        click.echo("")
        click.echo("Review the script, then generate style plates:")
        brief = work_dir / DESIGN_BRIEF_FILENAME
        click.echo(
            f"python3 -m src.design.cli --work {work_dir} --script {script_path} "
            f"--brief {brief}"
        )


def _optional_text(path: Path, label: str) -> str:
    if not path.is_file():
        click.echo(f"Warning: {label} not found: {path}", err=True)
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        click.echo(f"Warning: {label} is empty: {path}", err=True)
    return text


if __name__ == "__main__":
    main()
