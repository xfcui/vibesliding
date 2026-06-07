"""Export utilities - save images and assemble PDF."""

from __future__ import annotations

import io
import math
import re
from pathlib import Path

import img2pdf
from PIL import Image, ImageDraw, ImageFont

SLIDE_IMAGE_PATTERN = re.compile(r"^slide_p(\d+)_v(\d+)\.png$", re.IGNORECASE)


def build_contact_sheet(
    images: list[bytes],
    output_path: Path,
    *,
    columns: int = 2,
    title: str | None = None,
) -> Path:
    """Stitch candidate images into a numbered grid for visual selection.

    Args:
        images: Raw image bytes for each candidate (1..N)
        output_path: Destination PNG path
        columns: Grid columns (default 2 for a 2x2 layout when N=4)
        title: Optional header strip text (e.g. ``BASE — pick 1-4``)

    Returns:
        The saved contact sheet path

    Raises:
        ValueError: If *images* is empty or *columns* is invalid
    """
    if not images:
        raise ValueError("At least one image is required for a contact sheet")
    if columns < 1:
        raise ValueError("columns must be >= 1")

    decoded: list[Image.Image] = []
    for index, raw in enumerate(images):
        try:
            img = Image.open(io.BytesIO(raw))
            decoded.append(img.convert("RGB"))
        except Exception as exc:
            raise ValueError(f"Invalid image at index {index + 1}: {exc}") from exc

    cell_w = max(img.width for img in decoded)
    cell_h = max(img.height for img in decoded)
    rows = math.ceil(len(decoded) / columns)

    header_h = 0
    title_font = None
    if title:
        title_font = ImageFont.load_default(size=max(28, min(cell_w, cell_h) // 14))
        probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        title_bbox = probe.textbbox((0, 0), title, font=title_font)
        header_h = (title_bbox[3] - title_bbox[1]) + 24

    grid_w = columns * cell_w
    grid_h = rows * cell_h
    sheet = Image.new("RGB", (grid_w, header_h + grid_h), color=(24, 24, 28))
    draw = ImageDraw.Draw(sheet)

    if title and title_font is not None:
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_x = (grid_w - title_w) // 2
        title_y = 12
        draw.text((title_x, title_y), title, fill=(0, 212, 255), font=title_font)
        draw.line((0, header_h - 2, grid_w, header_h - 2), fill=(64, 64, 72), width=2)

    badge_size = max(56, min(cell_w, cell_h) // 6)
    badge_font = ImageFont.load_default(size=badge_size)
    accent = (0, 180, 220)
    border_color = (48, 48, 56)

    for index, img in enumerate(decoded):
        row, col = divmod(index, columns)
        cell_x = col * cell_w
        cell_y = header_h + row * cell_h

        draw.rectangle(
            (cell_x, cell_y, cell_x + cell_w - 1, cell_y + cell_h - 1),
            outline=border_color,
            width=2,
        )

        x = cell_x + (cell_w - img.width) // 2
        y = cell_y + (cell_h - img.height) // 2
        sheet.paste(img, (x, y))

        label = str(index + 1)
        badge_pad = badge_size // 3
        text_bbox = draw.textbbox((0, 0), label, font=badge_font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        badge_w = text_w + badge_pad * 2
        badge_h = text_h + badge_pad * 2
        badge_x = cell_x + 12
        badge_y = cell_y + 12
        draw.rounded_rectangle(
            (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
            radius=8,
            fill=accent,
        )
        draw.text(
            (badge_x + badge_pad, badge_y + badge_pad - 2),
            label,
            fill=(255, 255, 255),
            font=badge_font,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG")
    return output_path


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
