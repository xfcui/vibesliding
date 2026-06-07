"""CLI entry point for slide image generation (`python -m src.compose.cli`)."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable
from pathlib import Path
from typing import Final, cast

import click
from dotenv import load_dotenv

from src.compose.gen import SlideImageGenerator
from src.core.api_client import OpenRouterClient
from src.core.client_factory import (
    create_image_client,
    create_text_client,
    normalize_provider,
)
from src.core.config import load_config
from src.core.export import rebuild_combined_pdf
from src.core.paths import DEFAULT_OUTLINE_PATH, DEFAULT_WORK_DIR, default_output_dir
from src.core.resolve import PathResolveError, clean_path_pattern, resolve_patterns

load_dotenv()

SUPPORTED_ARTICLE_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".pdf", ".md", ".markdown"}
)
SUPPORTED_STYLE_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".png", ".jpg", ".jpeg", ".webp"}
)
ARTICLE_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[(?:Articles?|Text\s+References?|Source\s+References?)\s*:\s*(.*?)\]",
    re.IGNORECASE | re.DOTALL,
)


def _resolve_error_builders(
    *,
    kind: str,
    supported_extensions: frozenset[str],
) -> tuple[
    Callable[[str], str],
    Callable[[str], str],
    Callable[[Path], str],
    Callable[[Path, str], str],
]:
    ext_list = ", ".join(sorted(supported_extensions))

    def glob_miss(pattern: str) -> str:
        return f"No files found matching pattern: {pattern}"

    def file_miss(pattern: str) -> str:
        return f"{kind} file not found: {pattern}"

    def not_file(path: Path) -> str:
        return f"Not a file: {path}"

    def bad_extension(path: Path, suffix: str) -> str:
        return (
            f"Unsupported {kind.lower()} format '{suffix}' for {path.name}. "
            f"Supported: {ext_list}"
        )

    return glob_miss, file_miss, not_file, bad_extension


def _expand_paths(
    patterns: list[str],
    *,
    supported_extensions: frozenset[str],
    kind: str,
    base_dir: Path | None = None,
    include_parent_base: bool = False,
    sort: bool = False,
    normalize: Callable[[str], str] = str.strip,
) -> list[Path]:
    glob_miss, file_miss, not_file, bad_extension = _resolve_error_builders(
        kind=kind,
        supported_extensions=supported_extensions,
    )
    try:
        return resolve_patterns(
            patterns,
            supported_extensions=supported_extensions,
            base_dir=base_dir,
            include_parent_base=include_parent_base,
            sort=sort,
            normalize=normalize,
            glob_miss_error=glob_miss,
            file_miss_error=file_miss,
            not_file_error=not_file,
            bad_extension_error=bad_extension,
        )
    except PathResolveError as exc:
        raise click.UsageError(exc.message) from exc


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


def extract_article_patterns_from_outline(outline_text: str) -> list[str]:
    """Extract article reference path/glob patterns declared in the outline."""
    patterns: list[str] = []
    for match in ARTICLE_TAG_PATTERN.finditer(outline_text):
        raw = match.group(1).replace("\n", ",")
        patterns.extend(
            clean_path_pattern(segment)
            for segment in raw.split(",")
            if clean_path_pattern(segment)
        )
    return patterns


def expand_article_paths(
    patterns: list[str],
    base_dir: Path | None = None,
) -> list[Path]:
    """Expand glob patterns and validate article file paths."""
    return _expand_paths(
        patterns,
        supported_extensions=SUPPORTED_ARTICLE_EXTENSIONS,
        kind="Article",
        base_dir=base_dir,
        include_parent_base=True,
    )


def expand_style_paths(patterns: list[str]) -> list[Path]:
    """Expand glob patterns into sorted, unique image paths for style references."""
    if not patterns:
        return []
    return _expand_paths(
        patterns,
        supported_extensions=SUPPORTED_STYLE_EXTENSIONS,
        kind="Style image",
        sort=True,
        normalize=str.strip,
    )


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


def _run_pdf_only(
    output: Path,
    *,
    page: str | None,
    variant: str | None,
) -> None:
    page_numbers = _parse_page_spec_or_usage(page)
    variant_numbers = _parse_page_spec_or_usage(variant)
    try:
        pdf_path, image_count = rebuild_combined_pdf(
            output,
            page_filter=page_numbers,
            variant_filter=variant_numbers,
        )
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    click.echo(
        f"Created {pdf_path.name} ({image_count} page(s)) in {output.resolve()}"
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
    or_client = create_text_client(
        api_key=config.api_key,
        proxy=config.proxy,
        model=config.model,
        max_concurrent=config.max_concurrent,
        management_api_key=config.openrouter_management_api_key,
    )

    async def _balance() -> None:
        await _echo_openrouter_account_credits(or_client)

    asyncio.run(_balance())


def _load_article_content(
    article_patterns: list[str],
    outline: Path,
) -> tuple[list[bytes], list[str], list[Path]]:
    article_pdfs: list[bytes] = []
    article_texts: list[str] = []
    article_paths = expand_article_paths(article_patterns, base_dir=outline.parent)
    for path in article_paths:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            article_pdfs.append(path.read_bytes())
        else:
            article_texts.append(path.read_text(encoding="utf-8"))
    return article_pdfs, article_texts, article_paths


def _resolve_style_paths(
    style: tuple[str, ...],
    work_dir: Path,
) -> list[Path] | None:
    patterns = list(style) if style else [str(work_dir / "style_*.png")]
    style_paths = expand_style_paths(patterns)
    return style_paths or None


def _echo_generation_summary(
    *,
    outline: Path,
    copy: int,
    page_numbers: set[int] | None,
    article_paths: list[Path],
    article_pdfs: list[bytes],
    article_texts: list[str],
    style_paths: list[Path] | None,
    output: Path,
    provider: str,
) -> None:
    info_parts = [f"Outline: {outline}", f"copy: {copy}"]
    if page_numbers is not None:
        pages_str = ",".join(map(str, sorted(page_numbers)))
        info_parts.append(f"Pages: {pages_str}")
    if article_paths:
        types: list[str] = []
        if article_pdfs:
            types.append(f"{len(article_pdfs)} PDF")
        if article_texts:
            types.append(f"{len(article_texts)} Markdown")
        info_parts.append(f"Articles: {len(article_paths)} files ({', '.join(types)})")
    if style_paths is not None:
        names = ", ".join(p.name for p in style_paths)
        info_parts.append(f"Style ({len(style_paths)}): {names}")
    output_str = str(output.resolve())
    if style_paths is None:
        output_str += " (first slide only)"
    info_parts.append(f"Output: {output_str}")
    info_parts.append(f"Provider: {provider}")
    click.echo("  |  ".join(info_parts))


def _run_generation(
    *,
    outline: Path,
    work_dir: Path,
    style: tuple[str, ...],
    copy: int,
    output: Path | None,
    article: tuple[str, ...],
    api_key: str | None,
    page: str | None,
    proxy: str | None,
    provider: str | None,
    no_balance: bool,
) -> None:
    style_paths = _resolve_style_paths(style, work_dir)
    out_dir = output or default_output_dir()
    config = load_config(
        output_dir=out_dir,
        api_key_override=api_key,
        proxy_override=proxy,
        provider_override=normalize_provider(provider),
    )
    config.validate()
    page_numbers = _parse_page_spec_or_usage(page)

    outline_text = outline.read_text(encoding="utf-8")
    outline_article_patterns = extract_article_patterns_from_outline(outline_text)
    article_patterns = list(article or ()) + outline_article_patterns

    article_pdfs: list[bytes] = []
    article_texts: list[str] = []
    article_paths: list[Path] = []
    if article_patterns:
        article_pdfs, article_texts, article_paths = _load_article_content(
            article_patterns,
            outline,
        )

    _echo_generation_summary(
        outline=outline,
        copy=copy,
        page_numbers=page_numbers,
        article_paths=article_paths,
        article_pdfs=article_pdfs,
        article_texts=article_texts,
        style_paths=style_paths,
        output=out_dir,
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
                    outline=outline_text,
                    copy=copy,
                    output_dir=out_dir,
                    article_pdfs=article_pdfs or None,
                    article_texts=article_texts or None,
                    outline_dir=outline.parent,
                )
                click.echo(
                    f"Done. Saved {len(paths)} image(s) and PDF to {out_dir.resolve()}"
                )
            else:
                by_slide = await generator.generate_all_slide_images(
                    outline=outline_text,
                    style_image_paths=style_paths,
                    copy=copy,
                    output_dir=out_dir,
                    article_pdfs=article_pdfs or None,
                    article_texts=article_texts or None,
                    page_filter=page_numbers,
                    outline_dir=outline.parent,
                )
                total = sum(len(paths) for paths in by_slide.values())
                click.echo(
                    f"Done. Saved {total} image(s) and PDF to {out_dir.resolve()}"
                )
        finally:
            if config.provider == "openrouter" and not no_balance:
                await _echo_openrouter_account_credits(cast(OpenRouterClient, client))

    asyncio.run(run())


@click.command()
@click.option(
    "--work",
    "work_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_WORK_DIR,
    show_default=True,
    help="Work directory containing outline and style references.",
)
@click.option(
    "--outline",
    "outline_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTLINE_PATH,
    show_default=True,
    help="Outline markdown file (default: work/outline_16.md).",
)
@click.option(
    "--style",
    type=str,
    multiple=True,
    default=(),
    help=(
        "Style reference image path(s) or glob; repeatable "
        '(default: work/style_*.png). If no images resolve, only the first slide is generated.'
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
    help="Output directory for images and PDF. Default: slides_YYYYMMDD_HHMMSS/.",
)
@click.option(
    "--article",
    type=str,
    multiple=True,
    default=None,
    help="Path(s) or glob pattern(s) for article files (.pdf, .md, .markdown).",
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
    "--pdf-only",
    is_flag=True,
    default=False,
    help=(
        "Rebuild slide_combined.pdf from existing slide_p##_v##.png files "
        "in --output (no API calls; --outline not required)."
    ),
)
@click.option(
    "--variant",
    type=str,
    default=None,
    help=(
        "With --pdf-only: include only these variant numbers "
        "(e.g. '1' or '1,2'). Default: all variants present in --output."
    ),
)
def main(
    work_dir: Path,
    outline_path: Path,
    style: tuple[str, ...],
    copy: int,
    output: Path | None,
    article: tuple[str, ...],
    api_key: str | None,
    page: str | None,
    proxy: str | None,
    provider: str | None,
    balance_only: bool,
    no_balance: bool,
    pdf_only: bool,
    variant: str | None,
) -> None:
    """Compose slide images from a markdown outline and optional style references."""
    if balance_only and no_balance:
        raise click.UsageError("--balance-only cannot be used together with --no-balance.")
    if pdf_only and balance_only:
        raise click.UsageError("--pdf-only cannot be used with --balance-only.")
    if pdf_only and output is None:
        raise click.UsageError("--pdf-only requires --output (existing output directory).")

    if pdf_only:
        assert output is not None
        _run_pdf_only(output, page=page, variant=variant)
        return

    if balance_only:
        _run_balance_only(api_key=api_key, proxy=proxy, provider=provider)
        return

    if not outline_path.is_file():
        raise click.UsageError(f"Outline file not found: {outline_path}")

    _run_generation(
        outline=outline_path,
        work_dir=work_dir,
        style=style,
        copy=copy,
        output=output,
        article=article,
        api_key=api_key,
        page=page,
        proxy=proxy,
        provider=provider,
        no_balance=no_balance,
    )


if __name__ == "__main__":
    main()
