"""CLI entry point for PPT slide image generator."""

import asyncio
from pathlib import Path

import click
from dotenv import load_dotenv

from src.api_client import OpenRouterClient
from src.config import load_config
from src.generator import SlideImageGenerator

load_dotenv()


def parse_page_spec(page_spec: str | None) -> set[int] | None:
    """Parse page specification string into set of page numbers.
    
    Examples:
        '1' -> {1}
        '1,3,5' -> {1, 3, 5}
        '1-5' -> {1, 2, 3, 4, 5}
        '1,3-5,7' -> {1, 3, 4, 5, 7}
    
    Returns None if page_spec is None (meaning all pages).
    Raises ValueError if the specification is invalid.
    """
    if page_spec is None:
        return None
    
    pages: set[int] = set()
    parts = page_spec.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range specification
            range_parts = part.split('-')
            if len(range_parts) != 2:
                raise ValueError(f"Invalid range specification: '{part}'. Expected format: 'start-end'")
            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                if start > end:
                    raise ValueError(f"Invalid range: {start}-{end}. Start must be <= end.")
                if start < 1:
                    raise ValueError(f"Page numbers must be >= 1, got: {start}")
                pages.update(range(start, end + 1))
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid page number in range: '{part}'") from e
                raise
        else:
            # Single page number
            try:
                page_num = int(part)
                if page_num < 1:
                    raise ValueError(f"Page numbers must be >= 1, got: {page_num}")
                pages.add(page_num)
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid page number: '{part}'") from e
                raise
    
    return pages if pages else None


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
    default=Path("./output"),
    show_default=True,
    help="Output directory for images and PDF.",
)
@click.option(
    "--article",
    type=click.Path(path_type=Path, exists=True),
    default=None,
    help="Path to original article in PDF or Markdown format (.pdf, .md, .markdown).",
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
    help="Specific pages to generate (e.g., '1', '1,3,5', '1-5', '1,3-5,7'). Default: all pages.",
)
def main(
    outline: Path,
    style: Path | None,
    copy: int,
    output: Path,
    article: Path | None,
    api_key: str | None,
    page: str | None,
) -> None:
    """Generate slide images from markdown outline. Without --style: first slide only. With --style: all slides in that style."""
    config = load_config(output_dir=output, api_key_override=api_key)
    config.validate()

    # Parse page specification
    try:
        page_numbers = parse_page_spec(page)
    except ValueError as e:
        raise click.UsageError(str(e)) from e

    article_pdf: bytes | None = None
    article_text: str | None = None
    if article is not None:
        suffix = article.suffix.lower()
        if suffix == ".pdf":
            article_pdf = article.read_bytes()
        elif suffix in (".md", ".markdown"):
            article_text = article.read_text()
        else:
            raise click.UsageError(
                f"Article must be PDF or Markdown (.pdf, .md, .markdown), got: {article.name}"
            )

    parts = [f"Outline: {outline}", f"copy: {copy}"]
    if page_numbers is not None:
        pages_str = ','.join(map(str, sorted(page_numbers)))
        parts.append(f"Pages: {pages_str}")
    if article is not None:
        parts.append(f"Article: {article} ({'PDF' if article_pdf else 'Markdown'})")
    if style is not None:
        parts.append(f"Style: {style}")
    out_str = str(output.resolve())
    if style is None:
        out_str += " (first slide only)"
    parts.append(f"Output: {out_str}")
    click.echo("  |  ".join(parts))

    outline_text = outline.read_text()
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
                article_pdf=article_pdf,
                article_text=article_text,
            )
            click.echo(f"Done. Saved {len(paths)} image(s) and PDF to {output.resolve()}")
        else:
            by_slide = await generator.generate_all_slide_images(
                outline=outline_text,
                style_image_path=style,
                copy=copy,
                output_dir=output,
                article_pdf=article_pdf,
                article_text=article_text,
                page_filter=page_numbers,
            )
            total = sum(len(paths) for paths in by_slide.values())
            click.echo(f"Done. Saved {total} image(s) and PDF to {output.resolve()}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
