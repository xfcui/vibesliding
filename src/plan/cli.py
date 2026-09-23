"""CLI entry point for plan validation (`python -m src.plan.cli`)."""

from __future__ import annotations

from pathlib import Path

import click

from src.core.paths import DEFAULT_PLAN_PATH, FACTS_FILENAME, read_nonempty_text
from src.plan.parse import parse_plan
from src.plan.validate import content_slide_count, format_plan_report, validate_plan


def content_count_from_name(path: Path) -> int | None:
    """Return N from ``plan_N.md``, or None when the name has no count."""
    stem = path.stem
    prefix = "plan_"
    if not stem.startswith(prefix):
        return None
    raw = stem[len(prefix) :]
    if raw.isdigit():
        return int(raw)
    return None


@click.command()
@click.option(
    "--plan",
    "plan_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_PLAN_PATH,
    show_default=True,
    help="Deck plan markdown to validate.",
)

def main(plan_path: Path) -> None:
    """Validate a deck plan. Does not call any model API."""
    try:
        text = read_nonempty_text(plan_path, label="Plan file")
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    document = parse_plan(text)
    click.echo(f"Plan: {plan_path.resolve()}")
    if document.title:
        click.echo(f"Title: {document.title}")
    for line in format_plan_report(document):
        click.echo(line)

    expected = content_count_from_name(plan_path)
    actual = content_slide_count(document)
    if expected is not None and actual != expected:
        click.echo(
            f"Note: filename asks for {expected} content slides; plan has {actual}.",
            err=True,
        )

    facts_path = plan_path.parent / FACTS_FILENAME
    facts: str | None = None
    warnings: list[str] = []
    try:
        facts = read_nonempty_text(facts_path, label="Facts file")
    except ValueError as exc:
        warnings.append(f"{exc} (the write stage requires it).")
    else:
        click.echo(f"Facts: {facts_path.resolve()}")

    warnings.extend(validate_plan(text, facts).warnings)
    if warnings:
        click.echo("Validation warnings:", err=True)
        for warning in warnings:
            click.echo(f"  - {warning}", err=True)
        return

    click.echo("Plan looks structurally sound.")


if __name__ == "__main__":
    main()
