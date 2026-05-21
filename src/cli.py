"""CLI entry point for PPT slide image generator."""

from __future__ import annotations

import asyncio
from datetime import datetime
import glob as glob_module
from pathlib import Path
import re
from typing import Final, cast

import click
from dotenv import load_dotenv

from src.api_client import OpenRouterClient, VolcengineClient
from src.config import Provider, load_config
from src.generator import SlideImageGenerator
from src.output import rebuild_combined_pdf

load_dotenv()

# Constants
SUPPORTED_ARTICLE_EXTENSIONS: Final[set[str]] = {".pdf", ".md", ".markdown"}
SUPPORTED_STYLE_EXTENSIONS: Final[set[str]] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}
ARTICLE_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[(?:Articles?|Text\s+References?|Source\s+References?)\s*:\s*(.*?)\]",
    re.IGNORECASE | re.DOTALL,
)


def parse_page_spec(page_spec: str | None) -> set[int] | None:
    """Parse page specification string into set of page numbers.
    
    Examples:
        '1' -> {1}
        '1,3,5' -> {1, 3, 5}
        '1-5' -> {1, 2, 3, 4, 5}
        '1,3-5,7' -> {1, 3, 4, 5, 7}
    
    Args:
        page_spec: Page specification string or None
    
    Returns:
        Set of page numbers, or None if page_spec is None (all pages)
        
    Raises:
        ValueError: If the specification format is invalid or contains invalid numbers
    """
    if page_spec is None:
        return None
    
    pages: set[int] = set()
    parts = [p.strip() for p in page_spec.split(',')]
    
    for part in parts:
        if '-' in part:
            # Range specification: 'start-end'
            range_parts = part.split('-', 1)
            if len(range_parts) != 2:
                raise ValueError(
                    f"Invalid range specification: '{part}'. Expected format: 'start-end'"
                )
            
            try:
                start, end = int(range_parts[0].strip()), int(range_parts[1].strip())
            except ValueError as e:
                raise ValueError(f"Invalid page number in range: '{part}'") from e
            
            if start < 1:
                raise ValueError(f"Page numbers must be >= 1, got: {start}")
            if start > end:
                raise ValueError(f"Invalid range: {start}-{end}. Start must be <= end")
            
            pages.update(range(start, end + 1))
        else:
            # Single page number
            try:
                page_num = int(part)
            except ValueError as e:
                raise ValueError(f"Invalid page number: '{part}'") from e
            
            if page_num < 1:
                raise ValueError(f"Page numbers must be >= 1, got: {page_num}")
            pages.add(page_num)
    
    return pages if pages else None


def _clean_path_pattern(pattern: str) -> str:
    """Normalize outline/CLI path patterns while preserving spaces in filenames."""
    pattern = pattern.strip().strip("\"'")
    return pattern[1:] if pattern.startswith("@") else pattern


def extract_article_patterns_from_outline(outline_text: str) -> list[str]:
    """Extract article reference path/glob patterns declared in the outline."""
    patterns: list[str] = []
    for match in ARTICLE_TAG_PATTERN.finditer(outline_text):
        raw = match.group(1).replace("\n", ",")
        patterns.extend(
            _clean_path_pattern(segment)
            for segment in raw.split(",")
            if _clean_path_pattern(segment)
        )
    return patterns


def _candidate_patterns(pattern: str, base_dir: Path | None) -> list[str]:
    """Return cwd and outline-relative candidates for a path/glob pattern."""
    pattern = _clean_path_pattern(pattern)
    path = Path(pattern).expanduser()
    candidates = [str(path)]
    if not path.is_absolute() and base_dir is not None:
        candidates.extend([str(base_dir / pattern), str(base_dir.parent / pattern)])
    return candidates


def expand_article_paths(
    patterns: list[str],
    base_dir: Path | None = None,
) -> list[Path]:
    """Expand glob patterns and validate article file paths.
    
    Args:
        patterns: List of file paths or glob patterns
        base_dir: Optional outline directory used to resolve outline-declared paths
        
    Returns:
        List of valid article file paths
        
    Raises:
        click.UsageError: If no files found or unsupported format
    """
    all_paths: list[Path] = []
    
    for pattern in patterns:
        pattern = _clean_path_pattern(pattern)
        if not pattern:
            continue
        # Check if pattern contains glob wildcards
        if any(char in pattern for char in ['*', '?', '[', ']']):
            # Use glob to expand pattern
            matched: list[str] = []
            for candidate in _candidate_patterns(pattern, base_dir):
                matched.extend(glob_module.glob(candidate))
            if not matched:
                raise click.UsageError(f"No files found matching pattern: {pattern}")
            all_paths.extend([Path(p) for p in matched])
        else:
            # Regular file path
            matches = [Path(p) for p in _candidate_patterns(pattern, base_dir) if Path(p).exists()]
            if not matches:
                raise click.UsageError(f"Article file not found: {pattern}")
            all_paths.append(matches[0])
    
    # Validate all files
    for path in all_paths:
        if not path.is_file():
            raise click.UsageError(f"Not a file: {path}")
        
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_ARTICLE_EXTENSIONS:
            ext_list = ", ".join(sorted(SUPPORTED_ARTICLE_EXTENSIONS))
            raise click.UsageError(
                f"Unsupported article format '{suffix}' for {path.name}. "
                f"Supported: {ext_list}"
            )
    
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in all_paths:
        rp = path.resolve()
        if rp not in seen:
            seen.add(rp)
            unique.append(path)

    return unique


def expand_style_paths(patterns: list[str]) -> list[Path]:
    """Expand glob patterns into sorted, unique image paths for style references."""
    if not patterns:
        return []

    raw: list[Path] = []
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
        if any(char in pattern for char in "*?[]"):
            matched = glob_module.glob(pattern)
            if not matched:
                raise click.UsageError(f"No files found matching pattern: {pattern}")
            raw.extend(Path(p) for p in matched)
        else:
            path = Path(pattern)
            if not path.exists():
                raise click.UsageError(f"Style image not found: {pattern}")
            raw.append(path)

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in sorted(raw, key=lambda p: str(p.resolve())):
        rp = path.resolve()
        if rp not in seen:
            seen.add(rp)
            unique.append(path)

    for path in unique:
        if not path.is_file():
            raise click.UsageError(f"Not a file: {path}")
        sfx = path.suffix.lower()
        if sfx not in SUPPORTED_STYLE_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_STYLE_EXTENSIONS))
            raise click.UsageError(
                f"Unsupported style image format '{sfx}' for {path.name}. "
                f"Supported: {supported}"
            )

    return unique


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


@click.command()
@click.option(
    "--outline",
    type=click.Path(path_type=Path, exists=True),
    default=None,
    help="Path to markdown outline file.",
)
@click.option(
    "--style",
    type=str,
    multiple=True,
    default=(),
    help=(
        "Style reference image path(s) or glob; repeatable "
        '(e.g. --style "examples/style_*.png"). If omitted, only the first slide is generated.'
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
    help="Output directory for images and PDF. If not specified, uses 'output_YYYYMMDD_HHMMSS' to avoid overwriting.",
)
@click.option(
    "--article",
    type=str,
    multiple=True,
    default=None,
    help="Path(s) or glob pattern(s) for article files (.pdf, .md, .markdown). Can be specified multiple times or use wildcards like '*.pdf'.",
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
    help="Specific pages to generate (e.g., '1', '1,3,5', '1-5', '1,3-5,7'). Default: all pages. Note: quote comma-separated values when using shell.",
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
    help="Image API (required unless IMAGE_PROVIDER or provider in .env). Overrides IMAGE_PROVIDER.",
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
    outline: Path | None,
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
    """Generate slide images from markdown outline. Without --style: first slide only. With --style: all slides in that style."""
    if balance_only and no_balance:
        raise click.UsageError("--balance-only cannot be used together with --no-balance.")
    if balance_only and outline is not None:
        raise click.UsageError("--outline cannot be used with --balance-only.")
    if pdf_only and balance_only:
        raise click.UsageError("--pdf-only cannot be used with --balance-only.")
    if pdf_only and output is None:
        raise click.UsageError("--pdf-only requires --output (existing output directory).")

    if pdf_only:
        try:
            page_numbers = parse_page_spec(page)
        except ValueError as e:
            raise click.UsageError(str(e)) from e
        try:
            variant_numbers = parse_page_spec(variant)
        except ValueError as e:
            raise click.UsageError(str(e)) from e

        try:
            pdf_path, image_count = rebuild_combined_pdf(
                output,
                page_filter=page_numbers,
                variant_filter=variant_numbers,
            )
        except ValueError as e:
            raise click.UsageError(str(e)) from e

        click.echo(
            f"Created {pdf_path.name} ({image_count} page(s)) in {output.resolve()}"
        )
        return

    if not balance_only and outline is None:
        raise click.UsageError("Missing option '--outline'.")

    if balance_only:
        prov_override: Provider | None = (
            cast(Provider, provider.lower()) if provider else None
        )
        config = load_config(
            output_dir=Path("."),
            api_key_override=api_key,
            proxy_override=proxy,
            provider_override=prov_override,
        )
        config.validate()
        if config.provider != "openrouter":
            raise click.UsageError("--balance-only requires provider openrouter.")
        assert config.api_key is not None
        or_client = OpenRouterClient(
            api_key=config.api_key,
            proxy=config.proxy,
            model=config.model,
            max_concurrent=config.max_concurrent,
            management_api_key=config.openrouter_management_api_key,
        )

        async def _balance() -> None:
            await _echo_openrouter_account_credits(or_client)

        asyncio.run(_balance())
        return

    assert outline is not None

    if style:
        style_paths = expand_style_paths(list(style))
        if not style_paths:
            raise click.UsageError("No style images resolved from --style patterns")
    else:
        style_paths = None

    # Create timestamped output directory if not specified
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = Path(f"./output_{timestamp}")
    
    prov_override = cast(Provider, provider.lower()) if provider else None
    config = load_config(
        output_dir=output,
        api_key_override=api_key,
        proxy_override=proxy,
        provider_override=prov_override,
    )
    config.validate()

    # Parse page specification
    try:
        page_numbers = parse_page_spec(page)
    except ValueError as e:
        raise click.UsageError(str(e)) from e

    outline_text = outline.read_text(encoding="utf-8")
    outline_article_patterns = extract_article_patterns_from_outline(outline_text)
    article_patterns = list(article or ()) + outline_article_patterns

    # Load article content if provided
    article_pdfs: list[bytes] = []
    article_texts: list[str] = []
    article_paths: list[Path] = []
    
    if article_patterns:
        article_paths = expand_article_paths(article_patterns, base_dir=outline.parent)
        
        for path in article_paths:
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                article_pdfs.append(path.read_bytes())
            else:  # Markdown
                article_texts.append(path.read_text(encoding="utf-8"))

    # Display configuration summary
    info_parts = [f"Outline: {outline}", f"copy: {copy}"]
    
    if page_numbers is not None:
        pages_str = ','.join(map(str, sorted(page_numbers)))
        info_parts.append(f"Pages: {pages_str}")
    
    if article_paths:
        pdf_count = len(article_pdfs)
        md_count = len(article_texts)
        types = []
        if pdf_count:
            types.append(f"{pdf_count} PDF")
        if md_count:
            types.append(f"{md_count} Markdown")
        info_parts.append(f"Articles: {len(article_paths)} files ({', '.join(types)})")
    
    if style_paths is not None:
        names = ", ".join(p.name for p in style_paths)
        info_parts.append(f"Style ({len(style_paths)}): {names}")
    
    output_str = str(output.resolve())
    if style_paths is None:
        output_str += " (first slide only)"
    info_parts.append(f"Output: {output_str}")
    
    info_parts.append(f"Provider: {config.provider}")
    click.echo("  |  ".join(info_parts))

    # Initialize components
    assert config.api_key is not None  # validated
    if config.provider == "volcengine":
        client = VolcengineClient(
            api_key=config.api_key,
            model=config.model,
            max_concurrent=config.max_concurrent,
            base_url=config.volcengine_base_url,
            image_size=config.volcengine_image_size,
            response_format=config.volcengine_response_format,
            watermark=config.volcengine_watermark,
            proxy=config.volcengine_proxy,
        )
    else:
        client = OpenRouterClient(
            api_key=config.api_key,
            proxy=config.proxy,
            model=config.model,
            max_concurrent=config.max_concurrent,
            management_api_key=config.openrouter_management_api_key,
        )
    generator = SlideImageGenerator(client=client)

    async def run() -> None:
        try:
            if style_paths is None:
                # When no style is provided, generate first slide only
                # Check if page filter conflicts
                if page_numbers is not None and 1 not in page_numbers:
                    click.echo(
                        "No pages to generate (first slide mode, but page 1 not in filter)"
                    )
                    return
                paths = await generator.generate_first_slide_images(
                    outline=outline_text,
                    copy=copy,
                    output_dir=output,
                    article_pdfs=article_pdfs if article_pdfs else None,
                    article_texts=article_texts if article_texts else None,
                    outline_dir=outline.parent,
                )
                click.echo(f"Done. Saved {len(paths)} image(s) and PDF to {output.resolve()}")
            else:
                by_slide = await generator.generate_all_slide_images(
                    outline=outline_text,
                    style_image_paths=style_paths,
                    copy=copy,
                    output_dir=output,
                    article_pdfs=article_pdfs if article_pdfs else None,
                    article_texts=article_texts if article_texts else None,
                    page_filter=page_numbers,
                    outline_dir=outline.parent,
                )
                total = sum(len(paths) for paths in by_slide.values())
                click.echo(f"Done. Saved {total} image(s) and PDF to {output.resolve()}")
        finally:
            if config.provider == "openrouter" and not no_balance:
                await _echo_openrouter_account_credits(cast(OpenRouterClient, client))

    asyncio.run(run())


if __name__ == "__main__":
    main()
