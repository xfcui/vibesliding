"""CLI entry point for PPT slide image generator."""

import asyncio
from datetime import datetime
import glob as glob_module
from pathlib import Path
from typing import Final

import click
from dotenv import load_dotenv

from src.api_client import OpenRouterClient
from src.config import load_config
from src.generator import SlideImageGenerator

load_dotenv()

# Constants
SUPPORTED_ARTICLE_EXTENSIONS: Final[set[str]] = {".pdf", ".md", ".markdown"}


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


def expand_article_paths(patterns: list[str]) -> list[Path]:
    """Expand glob patterns and validate article file paths.
    
    Args:
        patterns: List of file paths or glob patterns
        
    Returns:
        List of valid article file paths
        
    Raises:
        click.UsageError: If no files found or unsupported format
    """
    all_paths: list[Path] = []
    
    for pattern in patterns:
        # Check if pattern contains glob wildcards
        if any(char in pattern for char in ['*', '?', '[', ']']):
            # Use glob to expand pattern
            matched = glob_module.glob(pattern)
            if not matched:
                raise click.UsageError(f"No files found matching pattern: {pattern}")
            all_paths.extend([Path(p) for p in matched])
        else:
            # Regular file path
            path = Path(pattern)
            if not path.exists():
                raise click.UsageError(f"Article file not found: {pattern}")
            all_paths.append(path)
    
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
    
    return all_paths


@click.command()
@click.option(
    "--outline",
    type=click.Path(path_type=Path, exists=True),
    required=True,
    help="Path to markdown outline file.",
)
@click.option(
    "--style",
    type=click.Path(path_type=Path, exists=True),
    default=None,
    help="Path to style reference image. If omitted, only the first slide is generated.",
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
    help="OpenRouter API key (or set OPENROUTER_API_KEY, or put in .env).",
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
    help="HTTP/HTTPS proxy URL (e.g., 'http://localhost:8080'). Default: no proxy.",
)
def main(
    outline: Path,
    style: Path | None,
    copy: int,
    output: Path | None,
    article: tuple[str, ...],
    api_key: str | None,
    page: str | None,
    proxy: str | None,
) -> None:
    """Generate slide images from markdown outline. Without --style: first slide only. With --style: all slides in that style."""
    # Create timestamped output directory if not specified
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = Path(f"./output_{timestamp}")
    
    config = load_config(output_dir=output, api_key_override=api_key, proxy_override=proxy)
    config.validate()

    # Parse page specification
    try:
        page_numbers = parse_page_spec(page)
    except ValueError as e:
        raise click.UsageError(str(e)) from e

    # Load article content if provided
    article_pdfs: list[bytes] = []
    article_texts: list[str] = []
    article_paths: list[Path] = []
    
    if article:
        article_paths = expand_article_paths(list(article))
        
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
    
    if style is not None:
        info_parts.append(f"Style: {style}")
    
    output_str = str(output.resolve())
    if style is None:
        output_str += " (first slide only)"
    info_parts.append(f"Output: {output_str}")
    
    click.echo("  |  ".join(info_parts))

    # Initialize components
    outline_text = outline.read_text(encoding="utf-8")
    client = OpenRouterClient(
        api_key=config.api_key,
        proxy=config.proxy,
        model=config.model,
        max_concurrent=config.max_concurrent,
    )
    generator = SlideImageGenerator(client=client)

    async def run() -> None:
        if style is None:
            # When no style is provided, generate first slide only
            # Check if page filter conflicts
            if page_numbers is not None and 1 not in page_numbers:
                click.echo("No pages to generate (first slide mode, but page 1 not in filter)")
                return
            paths = await generator.generate_first_slide_images(
                outline=outline_text,
                copy=copy,
                output_dir=output,
                article_pdfs=article_pdfs if article_pdfs else None,
                article_texts=article_texts if article_texts else None,
            )
            click.echo(f"Done. Saved {len(paths)} image(s) and PDF to {output.resolve()}")
        else:
            by_slide = await generator.generate_all_slide_images(
                outline=outline_text,
                style_image_path=style,
                copy=copy,
                output_dir=output,
                article_pdfs=article_pdfs if article_pdfs else None,
                article_texts=article_texts if article_texts else None,
                page_filter=page_numbers,
            )
            total = sum(len(paths) for paths in by_slide.values())
            click.echo(f"Done. Saved {total} image(s) and PDF to {output.resolve()}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
