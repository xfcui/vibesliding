"""CLI entry point for style reference generation (`python -m src.style.cli`)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from src.core.client_factory import create_image_client, normalize_provider, provider_label
from src.core.config import load_config
from src.core.paths import DEFAULT_OUTLINE_PATH, DEFAULT_WORK_DIR, IDEA_FILENAME, read_nonempty_text
from src.style.refs import StyleSelectFn, generate_style_references

load_dotenv()

STAGE_ORDER = ("base", "cover", "transition", "story")


def parse_pick_spec(spec: str, *, candidates: int) -> dict[str, int]:
    """Parse ``base,cover,transition,story`` indices (1-based)."""
    parts = [part.strip() for part in spec.split(",")]
    if len(parts) != len(STAGE_ORDER):
        raise click.UsageError(
            "--pick requires four comma-separated indices: base,cover,transition,story "
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
    """Build a selector that uses pre-picks or interactive contact-sheet prompts."""
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
        try:
            click.launch(str(choices_path.resolve()))
        except Exception:
            pass
        if not is_tty:
            click.echo(
                f"No TTY and no --pick; defaulting {label} to candidate 1."
            )
            return 1

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
    help="Work directory for idea.md and style reference outputs.",
)
@click.option(
    "--outline",
    "outline_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTLINE_PATH,
    show_default=True,
    help="Outline markdown file to style (default: work/outline_16.md).",
)
@click.option(
    "--candidates",
    type=click.IntRange(1, 12),
    default=4,
    show_default=True,
    help="Number of style candidates to generate per stage.",
)
@click.option(
    "--pick",
    default=None,
    help=(
        "Skip prompts and use pre-selected indices: "
        "base,cover,transition,story (e.g. 1,2,1,3)."
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
    outline_path: Path,
    candidates: int,
    pick: str | None,
    api_key: str | None,
    proxy: str | None,
    provider: str | None,
) -> None:
    """Generate style references with staged candidate selection from a reviewable outline."""
    work_dir.mkdir(parents=True, exist_ok=True)
    try:
        outline_text = read_nonempty_text(outline_path, label="Outline file")
        idea = read_nonempty_text(work_dir / IDEA_FILENAME, label="Idea file")
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    picks = parse_pick_spec(pick, candidates=candidates) if pick else None
    selector = build_style_selector(candidates=candidates, picks=picks)

    config = load_config(
        output_dir=work_dir,
        api_key_override=api_key,
        proxy_override=proxy,
        provider_override=normalize_provider(provider),
    )
    config.validate()
    image_client = create_image_client(config)

    click.echo(f"Work dir: {work_dir.resolve()}")
    click.echo(f"Outline: {outline_path.resolve()}")
    click.echo(f"Provider: {provider_label(image_client)}")
    click.echo(
        f"Generating style references ({candidates} candidates per stage: "
        "base, then cover/transition/story)..."
    )

    async def _generate_styles() -> list[Path]:
        return await generate_style_references(
            image_client,
            idea=idea,
            outline=outline_text,
            output_dir=work_dir,
            candidates=candidates,
            select=selector,
        )

    try:
        style_paths = asyncio.run(_generate_styles())
    except Exception as exc:
        raise click.ClickException(f"Style reference generation failed: {exc}") from exc

    click.echo(f"Saved {len(style_paths)} style reference(s):")
    for path in style_paths:
        click.echo(f"  - {path.resolve()}")
    click.echo(f"  - {(work_dir / 'style_candidates').resolve()}/ (all candidates)")

    style_glob = str(work_dir / "style_*.png")
    next_cmd = (
        f'python3 -m src.compose.cli --outline {outline_path} '
        f'--style "{style_glob}"'
    )
    click.echo("")
    click.echo("Review style references, then compose slides:")
    click.echo(next_cmd)


if __name__ == "__main__":
    main()
