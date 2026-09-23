"""CLI entry point for slide image generation (`python -m src.render.cli`)."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Final, cast

import click
from click.core import ParameterSource
from dotenv import load_dotenv

from src.render.gen import SlideImageGenerator
from src.core.api_client import OpenRouterClient
from src.core.client_factory import (
    create_image_client,
    normalize_provider,
)
from src.core.config import load_config
from src.core.export import rebuild_combined_pptx
from src.core.paths import (
    DEFAULT_SCRIPT_PATH,
    DEFAULT_STYLE_DIR,
    DEFAULT_WORK_DIR,
    backup_outline_to_image_dir,
    default_output_dir,
    style_dir as project_style_dir,
    style_images_in_dir,
    timestamp_from_image_dir,
    timestamp_slug,
)
from src.core.resolve import has_glob_chars

load_dotenv()

SUPPORTED_STYLE_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".png", ".jpg", ".jpeg", ".webp"}
)


def parse_page_spec(page_spec: str | None) -> set[int] | None:
    """Parse page specification string into set of page numbers."""
    if page_spec is None:
        return None

    pages: set[int] = set()
    parts = [p.strip() for p in page_spec.split(",")]

    for part in parts:
        if "-" in part:
            range_parts = part.split("-", 1)
            if len(range_parts) != 2:
                raise ValueError(
                    f"Invalid range specification: '{part}'. Expected format: 'start-end'"
                )

            try:
                start, end = int(range_parts[0].strip()), int(range_parts[1].strip())
            except ValueError as exc:
                raise ValueError(f"Invalid page number in range: '{part}'") from exc

            if start < 1:
                raise ValueError(f"Page numbers must be >= 1, got: {start}")
            if start > end:
                raise ValueError(f"Invalid range: {start}-{end}. Start must be <= end")

            pages.update(range(start, end + 1))
        else:
            try:
                page_num = int(part)
            except ValueError as exc:
                raise ValueError(f"Invalid page number: '{part}'") from exc

            if page_num < 1:
                raise ValueError(f"Page numbers must be >= 1, got: {page_num}")
            pages.add(page_num)

    return pages if pages else None


def collect_style_images(style_dir: Path) -> list[Path]:
    """Return every style plate inside *style_dir*, sorted by filename."""
    return style_images_in_dir(style_dir)


async def _echo_openrouter_account_credits(client: OpenRouterClient) -> None:
    """Print credits line from GET ``/api/v1/credits`` (best-effort)."""
    outcome = await client.fetch_credits()
    if outcome.credits is not None:
        c = outcome.credits
        remaining = c["total_credits"] - c["total_usage"]
        click.echo(
            "OpenRouter credits: "
            f"{remaining:.4f} remaining "
            f"({c['total_usage']:.4f} used / "
            f"{c['total_credits']:.4f} purchased)"
        )
        return
    err_parts = ["OpenRouter: could not fetch account credits."]
    if outcome.error:
        err_parts.append(f"({outcome.error})")
    if client._management_api_key:
        err_parts.append(
            "With a management key set, failures are usually proxy or network issues "
            "try [openrouter] use_proxy = false or OPENROUTER_USE_PROXY=0."
        )
    else:
        err_parts.append(
            "Use an OpenRouter Management API key: set OPENROUTER_MANAGEMENT_API_KEY "
            "or [openrouter] management_api_key "
            "(create one at https://openrouter.ai/settings/management-keys)."
        )
    click.echo(" ".join(err_parts), err=True)


def _parse_page_spec_or_usage(page: str | None) -> set[int] | None:
    try:
        return parse_page_spec(page)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc


def _run_pptx_only(
    output: Path,
    *,
    work_dir: Path,
    outline: Path | None,
    page: str | None,
    variant: str | None,
) -> None:
    page_numbers = _parse_page_spec_or_usage(page)
    variant_numbers = _parse_page_spec_or_usage(variant)
    ts = timestamp_from_image_dir(output) or timestamp_slug()
    outline_text: str | None = None
    if outline is not None and outline.is_file():
        outline_text = outline.read_text(encoding="utf-8")
    else:
        click.echo(
            "Speaker notes skipped (script not found; pass --script to include [Speech:] notes).",
            err=True,
        )
    try:
        pptx_path, image_count = rebuild_combined_pptx(
            output,
            outline_text,
            pptx_dir=work_dir,
            timestamp=ts,
            page_filter=page_numbers,
            variant_filter=variant_numbers,
        )
    except Exception as exc:
        raise click.ClickException(f"Failed to rebuild PPTX: {exc}") from exc
    click.echo(
        f"Created {pptx_path.name} ({image_count} slide(s)) in {work_dir.resolve()}"
    )


def _run_balance_only(
    *,
    api_key: str | None,
    proxy: str | None,
    provider: str | None,
) -> None:
    config = load_config(
        output_dir=Path("."),
        api_key_override=api_key,
        proxy_override=proxy,
        provider_override=normalize_provider(provider),
    )
    config.validate()
    if config.provider != "openrouter":
        raise click.UsageError("--balance-only requires provider openrouter.")
    assert config.api_key is not None
    or_client = create_image_client(config)

    async def _balance() -> None:
        await _echo_openrouter_account_credits(or_client)

    try:
        asyncio.run(_balance())
    except Exception as exc:
        raise click.ClickException(f"Failed to fetch balance: {exc}") from exc


def _resolve_style_paths(style_dir: Path, *, explicit: bool) -> list[Path] | None:
    """Collect style plates from *style_dir*; None means first-slide-only mode.

    *explicit* marks a user-supplied ``--style``: a bad directory is then an error
    rather than a silent fallback, since the user clearly meant to style the deck.
    """
    if has_glob_chars(str(style_dir)):
        raise click.UsageError(
            f"--style takes a directory, not a glob: {style_dir}. "
            f"Use --style {style_dir.parent if str(style_dir.parent) != '.' else DEFAULT_STYLE_DIR}"
        )
    if style_dir.is_file():
        raise click.UsageError(
            f"--style takes a directory, not a file: {style_dir}. "
            f"Use --style {style_dir.parent}"
        )
    if not style_dir.is_dir():
        if explicit:
            raise click.UsageError(f"Style directory not found: {style_dir.resolve()}")
        return None

    style_paths = collect_style_images(style_dir)
    if not style_paths and explicit:
        supported = ", ".join(sorted(SUPPORTED_STYLE_EXTENSIONS))
        raise click.UsageError(
            f"No style images in {style_dir.resolve()} (supported: {supported}). "
            "Generate them with: python3 -m src.design.cli"
        )
    return style_paths or None


def _echo_generation_summary(
    *,
    script: Path,
    copy: int,
    page_numbers: set[int] | None,
    style_dir: Path,
    style_paths: list[Path] | None,
    output: Path,
    outline_backup: Path,
    provider: str,
) -> None:
    info_parts = [f"Script: {script}", f"copy: {copy}"]
    if page_numbers is not None:
        pages_str = ",".join(map(str, sorted(page_numbers)))
        info_parts.append(f"Pages: {pages_str}")
    if style_paths is not None:
        names = ", ".join(p.name for p in style_paths)
        info_parts.append(f"Style dir: {style_dir} ({len(style_paths)}): {names}")
    output_str = str(output.resolve())
    if style_paths is None:
        output_str += " (first slide only)"
    info_parts.append(f"Output: {output_str}")
    info_parts.append(f"Script backup: {outline_backup.resolve()}")
    info_parts.append(f"Provider: {provider}")
    click.echo("  |  ".join(info_parts))


def _run_generation(
    *,
    script: Path,
    work_dir: Path,
    style_dir: Path,
    style_explicit: bool,
    copy: int,
    output: Path | None,
    api_key: str | None,
    page: str | None,
    proxy: str | None,
    provider: str | None,
    no_balance: bool,
) -> None:
    style_paths = _resolve_style_paths(style_dir, explicit=style_explicit)
    run_ts = timestamp_slug()
    out_dir = output or default_output_dir(work_dir, run_ts)
    config = load_config(
        output_dir=out_dir,
        api_key_override=api_key,
        proxy_override=proxy,
        provider_override=normalize_provider(provider),
    )
    config.validate()
    page_numbers = _parse_page_spec_or_usage(page)

    script_text = script.read_text(encoding="utf-8")
    outline_backup = backup_outline_to_image_dir(
        script,
        out_dir,
        text=script_text,
    )

    _echo_generation_summary(
        script=script,
        copy=copy,
        page_numbers=page_numbers,
        style_dir=style_dir,
        style_paths=style_paths,
        output=out_dir,
        outline_backup=outline_backup,
        provider=config.provider,
    )

    client = create_image_client(config)
    generator = SlideImageGenerator(client=client)

    async def run() -> None:
        try:
            if style_paths is None:
                if page_numbers is not None and 1 not in page_numbers:
                    click.echo(
                        "No pages to generate (first slide mode, but page 1 not in filter)"
                    )
                    return
                paths = await generator.generate_first_slide_images(
                    outline=script_text,
                    copy=copy,
                    output_dir=out_dir,
                    outline_dir=script.parent,
                    work_dir=work_dir,
                    run_timestamp=run_ts,
                )
                click.echo(
                    f"Done. Saved {len(paths)} image(s) to {out_dir.resolve()} "
                    f"and PPTX to {work_dir.resolve()}"
                )
            else:
                by_slide = await generator.generate_all_slide_images(
                    outline=script_text,
                    style_image_paths=style_paths,
                    copy=copy,
                    output_dir=out_dir,
                    page_filter=page_numbers,
                    outline_dir=script.parent,
                    style_dir=style_dir,
                    work_dir=work_dir,
                    run_timestamp=run_ts,
                )
                total = sum(len(paths) for paths in by_slide.values())
                click.echo(
                    f"Done. Saved {total} image(s) to {out_dir.resolve()} "
                    f"and PPTX to {work_dir.resolve()}"
                )
        finally:
            if config.provider == "openrouter" and not no_balance:
                await _echo_openrouter_account_credits(cast(OpenRouterClient, client))

    try:
        asyncio.run(run())
    except Exception as exc:
        raise click.ClickException(f"Slide generation failed: {exc}") from exc


@click.command()
@click.option(
    "--work",
    "work_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_WORK_DIR,
    show_default=True,
    help="Work directory containing the script and style plates.",
)
@click.option(
    "--script",
    "script_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_SCRIPT_PATH,
    show_default=True,
    help="Script markdown file (default: work/script_16.md).",
)
@click.option(
    "--style",
    "style_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_STYLE_DIR,
    show_default=True,
    help=(
        "Directory holding the style images. Slides pick images from here with "
        "[Style: filename]; untagged slides are routed by slide role. "
        "If the default directory has no images, only the first slide is generated."
    ),
)
@click.option(
    "--copy",
    type=int,
    default=1,
    show_default=True,
    help="Number of image variants per slide.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory for slide PNGs. Default: WORK/image_YYYYMMDD_HHMMSS/. PPTX goes to WORK/.",
)
@click.option(
    "--api-key",
    envvar="OPENROUTER_API_KEY",
    help="API key for the selected provider (or OPENROUTER_API_KEY / VOLCENGINE_API_KEY, or .env).",
)
@click.option(
    "--page",
    type=str,
    default=None,
    help="Specific pages to generate (e.g., '1', '1,3,5', '1-5', '1,3-5,7'). Default: all pages.",
)
@click.option(
    "--proxy",
    type=str,
    default=None,
    help="HTTP/HTTPS proxy URL for OpenRouter only (ignored for Volcengine).",
)
@click.option(
    "--provider",
    type=click.Choice(["openrouter", "volcengine"], case_sensitive=False),
    default=None,
    help="Image API (required unless IMAGE_PROVIDER or provider in .env).",
)
@click.option(
    "--balance-only",
    is_flag=True,
    default=False,
    help="Fetch and print OpenRouter account credits, then exit (openrouter only).",
)
@click.option(
    "--no-balance",
    is_flag=True,
    default=False,
    help="Skip printing OpenRouter credits after a successful run.",
)
@click.option(
    "--pptx-only",
    "pptx_only",
    is_flag=True,
    default=False,
    help=(
        "Rebuild slides_YYYYMMDD.pptx in --work from existing "
        "slide_p##_v##.png files in --output (no API calls). "
        "Speaker notes come from --script [Speech:] tags when available."
    ),
)
@click.option(
    "--variant",
    type=str,
    default=None,
    help=(
        "With --pptx-only: include only these variant numbers in the PPTX "
        "(e.g. '1' or '1,2'). Default: all variants present in --output."
    ),
)
def main(
    work_dir: Path,
    script_path: Path,
    style_dir: Path,
    copy: int,
    output: Path | None,
    api_key: str | None,
    page: str | None,
    proxy: str | None,
    provider: str | None,
    balance_only: bool,
    no_balance: bool,
    pptx_only: bool,
    variant: str | None,
) -> None:
    """Compose slide images from a script and optional style plates."""
    if balance_only and no_balance:
        raise click.UsageError("--balance-only cannot be used together with --no-balance.")
    if pptx_only and balance_only:
        raise click.UsageError("--pptx-only cannot be used with --balance-only.")
    if pptx_only and output is None:
        raise click.UsageError("--pptx-only requires --output (existing image directory).")

    if pptx_only:
        assert output is not None
        outline_for_pptx = script_path if script_path.is_file() else None
        _run_pptx_only(
            output,
            work_dir=work_dir,
            outline=outline_for_pptx,
            page=page,
            variant=variant,
        )
        return

    if balance_only:
        _run_balance_only(api_key=api_key, proxy=proxy, provider=provider)
        return

    if not script_path.is_file():
        raise click.UsageError(f"Script file not found: {script_path}")

    style_source = click.get_current_context().get_parameter_source("style_dir")
    style_explicit = style_source is not ParameterSource.DEFAULT
    resolved_style = style_dir if style_explicit else project_style_dir(work_dir)
    _run_generation(
        script=script_path,
        work_dir=work_dir,
        style_dir=resolved_style,
        style_explicit=style_explicit,
        copy=copy,
        output=output,
        api_key=api_key,
        page=page,
        proxy=proxy,
        provider=provider,
        no_balance=no_balance,
    )


if __name__ == "__main__":
    main()
