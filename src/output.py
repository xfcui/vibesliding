"""Output handler - save images and generate PDF."""

from __future__ import annotations

import re
from pathlib import Path

import img2pdf
from PIL import Image

SLIDE_IMAGE_PATTERN = re.compile(r"^slide_p(\d+)_v(\d+)\.png$", re.IGNORECASE)


def save_image(image_data: bytes, path: Path) -> None:
    """Save raw image bytes to file.
    
    Args:
        image_data: Raw image bytes
        path: Destination file path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_data)


def create_pdf_from_images(image_paths: list[Path], output_path: Path) -> None:
    """Combine multiple saved images into a single PDF.

    Images are validated but not resized or otherwise post-processed, so the
    saved PNG files remain exactly as returned by the image provider.
    
    Args:
        image_paths: List of image file paths to combine
        output_path: Destination PDF file path
        
    Raises:
        ValueError: If no valid images are provided or found
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    valid_paths: list[str] = []
    
    for path in image_paths:
        if not path.exists():
            continue
        try:
            with Image.open(path) as img:
                img.verify()
            
            valid_paths.append(str(path))
        except Exception as e:
            print(f"Warning: skipping invalid image {path}: {e}")
            continue

    if not valid_paths:
        raise ValueError("No valid images to process after filtering")

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(valid_paths))


def collect_slide_image_paths(
    output_dir: Path,
    *,
    page_filter: set[int] | None = None,
    variant_filter: set[int] | None = None,
) -> list[Path]:
    """Collect generated slide PNGs in deck order (page, then variant).

    Args:
        output_dir: Directory containing ``slide_p##_v##.png`` files
        page_filter: If set, only include these slide page numbers
        variant_filter: If set, only include these variant numbers

    Returns:
        Sorted list of matching image paths

    Raises:
        ValueError: If the directory is missing or no images match
    """
    if not output_dir.is_dir():
        raise ValueError(f"Output directory not found: {output_dir}")

    images: list[tuple[int, int, Path]] = []
    for path in output_dir.iterdir():
        if not path.is_file():
            continue
        match = SLIDE_IMAGE_PATTERN.match(path.name)
        if not match:
            continue
        page_num = int(match.group(1))
        variant_num = int(match.group(2))
        if page_filter is not None and page_num not in page_filter:
            continue
        if variant_filter is not None and variant_num not in variant_filter:
            continue
        images.append((page_num, variant_num, path))

    if not images:
        raise ValueError(
            f"No slide images found in {output_dir} "
            "(expected slide_p##_v##.png)"
        )

    images.sort(key=lambda item: (item[0], item[1]))
    return [path for _, _, path in images]


def rebuild_combined_pdf(
    output_dir: Path,
    *,
    page_filter: set[int] | None = None,
    variant_filter: set[int] | None = None,
    pdf_name: str = "slide_combined.pdf",
) -> tuple[Path, int]:
    """Rebuild ``slide_combined.pdf`` from existing slide PNGs in *output_dir*."""
    image_paths = collect_slide_image_paths(
        output_dir,
        page_filter=page_filter,
        variant_filter=variant_filter,
    )
    pdf_path = output_dir / pdf_name
    create_pdf_from_images(image_paths, pdf_path)
    return pdf_path, len(image_paths)
