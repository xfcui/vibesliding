"""CLI entry point for style plates (`python -m src.design.cli`)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from src.core.client_factory import create_image_client, normalize_provider, provider_label
from src.core.config import load_config
from src.core.paths import (
    DEFAULT_SCRIPT_PATH,
    DEFAULT_WORK_DIR,
    DESIGN_BRIEF_FILENAME,
    STYLE_DIRNAME,
    read_nonempty_text,
)
from src.design.plates import (
    STYLE_CANDIDATES_DIRNAME,
    StyleSelectFn,
    generate_style_references,
    style_prompt_path,
)

load_dotenv()

STAGE_ORDER = ("base_noncontent", "base_content", "cover", "transition", "content")


def parse_pick_spec(spec: str, *, candidates: int) -> dict[str, int]:
    """Parse ``base_noncontent,base_content,cover,transition,content`` indices (1-based)."""
    parts = [part.strip() for part in spec.split(",")]
    if len(parts) != len(STAGE_ORDER):
        raise click.UsageError(
            "--pick requires five comma-separated indices: "
            "base_noncontent,base_content,cover,transition,content "
            f"(got {len(parts)})"
        )

    picks: dict[str, int] = {}
    for label, raw in zip(STAGE_ORDER, parts):
        try:
            index = int(raw)
        except ValueError as exc:
            raise click.UsageError(
                f"Invalid --pick index for {label}: {raw!r} (expected integer 1-{candidates})"
            ) from exc
        if index < 1 or index > candidates:
            raise click.UsageError(
                f"Invalid --pick index for {label}: {index} (expected 1-{candidates})"
            )
        picks[label] = index
    return picks


def build_style_selector(
    *,
    candidates: int,
    picks: dict[str, int] | None,
) -> StyleSelectFn:
    """Build a selector that uses pre-picks, candidate 1, or an interactive prompt."""
    if candidates == 1 and picks is None:
        def select_only(_label: str, _choices_path: Path, _count: int) -> int:
            return 1

        return select_only

    if picks is not None:
        remaining = dict(picks)

        def select_from_pick(label: str, choices_path: Path, count: int) -> int:
            if label not in remaining:
                raise ValueError(f"Unexpected selection stage: {label}")
            picked = remaining.pop(label)
            if picked < 1 or picked > count:
                raise ValueError(
                    f"Invalid pick for {label}: {picked} (expected 1-{count})"
                )
            click.echo(
                f"Using pre-selected {label}: candidate {picked} "
                f"({choices_path.name})"
            )
            return picked

        return select_from_pick

    is_tty = sys.stdin.isatty()
    stage_index = {"value": 0}

    def interactive_select(label: str, choices_path: Path, count: int) -> int:
        stage_index["value"] += 1
        stage_num = stage_index["value"]
        total_stages = len(STAGE_ORDER)

        click.echo("")
        click.echo(f"Stage {stage_num}/{total_stages}: {label}")
        click.echo(f"Contact sheet: {choices_path.resolve()}")
        if not is_tty:
            click.echo(
                f"No TTY and no --pick; defaulting {label} to candidate 1."
            )
            return 1

        try:
            click.launch(str(choices_path.resolve()))
        except Exception:
            pass

        click.echo(f"Enter 1-{count} to pick, or r to regenerate.")
        while True:
            raw = click.prompt(f"Pick {label} style", type=str).strip().lower()
            if raw in {"r", "regen", "regenerate"}:
                click.echo(f"Regenerating {label} candidates...")
                return 0
            try:
                picked = int(raw)
            except ValueError:
                click.echo(f"Invalid input {raw!r}. Enter 1-{count} or r.")
                continue
            if 1 <= picked <= count:
                return picked
            click.echo(f"Out of range. Enter 1-{count} or r.")

    return interactive_select


@click.command()
@click.option(
    "--work",
    "work_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_WORK_DIR,
    show_default=True,
    help="Work directory for the script and style images.",
)
@click.option(
    "--script",
    "script_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_SCRIPT_PATH,
    show_default=True,
    help="Script markdown (script_N.md).",
)
@click.option(
    "--brief",
    "brief_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Design brief markdown. Default: WORK/design_brief.md.",
)
@click.option(
    "--style",
    "style_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for the five style images. Default: WORK/style/.",
)
@click.option(
    "--candidates",
    type=click.IntRange(1, 12),
    default=1,
    show_default=True,
    help="Candidates per style image. 1 skips interactive picking.",
)
@click.option(
    "--pick",
    default=None,
    help=(
        "Skip prompts and use pre-selected indices: "
        "base_noncontent,base_content,cover,transition,content (e.g. 1,1,2,1,3)."
    ),
)
@click.option(
    "--api-key",
    envvar="OPENROUTER_API_KEY",
    help="API key for the selected image provider.",
)
@click.option(
    "--proxy",
    default=None,
    help="HTTP/HTTPS proxy URL for OpenRouter image calls.",
)
@click.option(
    "--provider",
    type=click.Choice(["openrouter", "volcengine"], case_sensitive=False),
    default=None,
    help="Image API (required unless provider in .env).",
)
def main(
    work_dir: Path,
    script_path: Path,
    brief_path: Path | None,
    style_dir: Path | None,
    candidates: int,
    pick: str | None,
    api_key: str | None,
    proxy: str | None,
    provider: str | None,
) -> None:
    """Generate two-tone style plates from a script and a design brief."""
    work_dir.mkdir(parents=True, exist_ok=True)
    brief = brief_path or (work_dir / DESIGN_BRIEF_FILENAME)
    style_output_dir = style_dir or (work_dir / STYLE_DIRNAME)
    picks = parse_pick_spec(pick, candidates=candidates) if pick else None
    try:
        script_text = read_nonempty_text(script_path, label="Script file")
        brief_text = read_nonempty_text(brief, label="Design brief")
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    selector = build_style_selector(candidates=candidates, picks=picks)

    config = load_config(
        output_dir=work_dir,
        api_key_override=api_key,
        proxy_override=proxy,
        provider_override=normalize_provider(provider),
    )
    config.validate()
    image_client = create_image_client(config)
    style_output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Work dir: {work_dir.resolve()}")
    click.echo(f"Script: {script_path.resolve()}")
    click.echo(f"Brief: {brief.resolve()}")
    click.echo(f"Style dir: {style_output_dir.resolve()}")
    click.echo(f"Provider: {provider_label(image_client)}")
    click.echo(
        f"Generating two-tone style plates ({candidates} candidate(s) per stage)..."
    )

    async def _generate_styles() -> list[Path]:
        return await generate_style_references(
            image_client,
            script=script_text,
            design_brief=brief_text,
            output_dir=style_output_dir,
            candidates=candidates,
            select=selector,
        )

    try:
        style_paths = asyncio.run(_generate_styles())
    except Exception as exc:
        raise click.ClickException(f"Style plate generation failed: {exc}") from exc

    click.echo(f"Saved {len(style_paths)} style plate(s):")
    for path in style_paths:
        click.echo(f"  - {path.resolve()}")
        click.echo(f"    prompt: {style_prompt_path(path).resolve()}")
    click.echo(
        f"  - {(style_output_dir / STYLE_CANDIDATES_DIRNAME).resolve()}/ (all candidates)"
    )
    click.echo("")
    click.echo("Review the plates, then render slides:")
    click.echo(
        f"python3 -m src.render.cli --work {work_dir} --script {script_path} "
        f"--style {style_output_dir}"
    )


if __name__ == "__main__":
    main()
