"""Export utilities - save images and assemble PDF."""

from __future__ import annotations

import io
import math
import re
import tempfile
from pathlib import Path

import img2pdf
from PIL import Image, ImageDraw, ImageFont

from src.outline.parser import Slide, extract_global_style, extract_speech_text, parse_markdown
from src.core.paths import (
    DEFAULT_WORK_DIR,
    presentation_slides_pdf_path,
    presentation_speech_pdf_path,
    timestamp_from_image_dir,
    timestamp_slug,
)

SLIDE_IMAGE_PATTERN = re.compile(r"^slide_p(\d+)_v(\d+)\.png$", re.IGNORECASE)

# A4 portrait at 150 DPI (210 mm × 297 mm)
A4_WIDTH_PX = 1240
A4_HEIGHT_PX = 1754
A4_MARGIN_PX = 60
SPEECH_TITLE_FONT_SIZE = 32
SPEECH_BODY_FONT_SIZE = 24
SPEECH_LABEL_FONT_SIZE = 20

_CJK_CHAR_PATTERN = re.compile(
    r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3000-\u303f\uff00-\uffef]"
)

# CJK-capable fonts first so Chinese speech notes render correctly.
_SPEECH_FONT_REGULAR: tuple[str, ...] = (
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
)

_SPEECH_FONT_BOLD: tuple[str, ...] = (
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    *_SPEECH_FONT_REGULAR,
)


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


def save_style_reference_image(
    image_data: bytes,
    path: Path,
    *,
    target_size: tuple[int, int],
) -> None:
    """Save a style reference PNG, downscaling to *target_size* when larger."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(image_data)) as img:
        rgb = img.convert("RGB")
        if rgb.size[0] > target_size[0] or rgb.size[1] > target_size[1]:
            rgb = rgb.resize(target_size, Image.Resampling.LANCZOS)
        rgb.save(path, format="PNG")


def _load_truetype_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = _SPEECH_FONT_BOLD if bold else _SPEECH_FONT_REGULAR
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _line_width(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    draw: ImageDraw.ImageDraw,
) -> int:
    if not text:
        return 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _needs_space_before(token: str, current: str) -> bool:
    if not current:
        return False
    return not (
        _CJK_CHAR_PATTERN.match(current[-1])
        or _CJK_CHAR_PATTERN.match(token[0])
    )


def _append_wrap_token(current: str, token: str) -> str:
    if not current:
        return token
    if _needs_space_before(token, current):
        return f"{current} {token}"
    return current + token


def _iter_wrap_tokens(text: str):
    """Yield wrap tokens, keeping Latin words intact and CJK as single characters."""
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if _CJK_CHAR_PATTERN.match(char):
            yield char
            index += 1
            continue
        match = re.match(r"[\w']+", text[index:])
        if match:
            yield match.group(0)
            index += len(match.group(0))
            continue
        yield char
        index += 1


def _wrap_paragraph(
    paragraph: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for token in _iter_wrap_tokens(paragraph):
        candidate = _append_wrap_token(current, token)
        if _line_width(candidate, font, draw) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        if _line_width(token, font, draw) <= max_width:
            current = token
            continue
        for char in token:
            candidate = _append_wrap_token(current, char)
            if _line_width(candidate, font, draw) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = char
    if current:
        lines.append(current)
    return lines


def _wrap_text_lines(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        lines.extend(_wrap_paragraph(paragraph, font, max_width, draw))
    return lines or [""]


def _slide_number_from_path(path: Path) -> int | None:
    match = SLIDE_IMAGE_PATTERN.match(path.name)
    if not match:
        return None
    return int(match.group(1))


def slides_by_index_from_outline(outline_text: str) -> dict[int, Slide]:
    """Return content slides keyed by 1-based slide index."""
    slides = parse_markdown(outline_text)
    global_style = extract_global_style(slides)
    if global_style:
        slides = [slide for slide in slides if slide.content != global_style]
    return {slide.index: slide for slide in slides}


def render_speech_page(
    slide_image_path: Path,
    *,
    slide_number: int,
    slide_title: str,
    speech_text: str,
) -> Image.Image:
    """Render one A4 page with a slide image and its presenter speech."""
    page = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), color=(255, 255, 255))
    draw = ImageDraw.Draw(page)
    content_width = A4_WIDTH_PX - 2 * A4_MARGIN_PX
    y = A4_MARGIN_PX

    title_font = _load_truetype_font(SPEECH_TITLE_FONT_SIZE, bold=True)
    label_font = _load_truetype_font(SPEECH_LABEL_FONT_SIZE, bold=True)
    body_font = _load_truetype_font(SPEECH_BODY_FONT_SIZE)
    footer_font = _load_truetype_font(SPEECH_LABEL_FONT_SIZE)

    # Title with wrapping
    title = f"Slide {slide_number}: {slide_title}"
    wrapped_title = _wrap_text_lines(title, title_font, content_width, draw)
    for line in wrapped_title:
        draw.text((A4_MARGIN_PX, y), line, fill=(15, 23, 42), font=title_font)  # slate-900
        line_bbox = draw.textbbox((A4_MARGIN_PX, y), line, font=title_font)
        y = line_bbox[3] + 8
    y += 16  # Spacing after title block

    # Slide Image with 1px border
    with Image.open(slide_image_path) as slide_img:
        slide_rgb = slide_img.convert("RGB")
        max_slide_width = content_width
        max_slide_height = int(content_width * 9 / 16)
        scale = min(
            max_slide_width / slide_rgb.width,
            max_slide_height / slide_rgb.height,
            1.0,
        )
        target_size = (
            max(1, int(slide_rgb.width * scale)),
            max(1, int(slide_rgb.height * scale)),
        )
        if target_size != slide_rgb.size:
            slide_rgb = slide_rgb.resize(target_size, Image.Resampling.LANCZOS)
        slide_x = A4_MARGIN_PX + (content_width - slide_rgb.width) // 2
        page.paste(slide_rgb, (slide_x, y))
        
        # 1px border
        draw.rectangle(
            (slide_x - 1, y - 1, slide_x + slide_rgb.width, y + slide_rgb.height),
            outline=(226, 232, 240),  # slate-200
            width=1,
        )
        y += slide_rgb.height + 28

    # Separator line
    draw.line(
        (A4_MARGIN_PX, y, A4_WIDTH_PX - A4_MARGIN_PX, y),
        fill=(226, 232, 240),  # slate-200
        width=1,
    )
    y += 24

    # "Speech" Section label
    label = "Speech"
    draw.text((A4_MARGIN_PX, y), label, fill=(100, 116, 139), font=label_font)  # slate-500
    label_bbox = draw.textbbox((A4_MARGIN_PX, y), label, font=label_font)
    y = label_bbox[3] + 16

    # Speech Body Text
    speech = speech_text.strip() or "(No speech text found for this slide.)"
    line_height = SPEECH_BODY_FONT_SIZE + 10
    
    # 48px buffer before bottom margin to avoid overlapping with footer
    max_lines = max(1, (A4_HEIGHT_PX - A4_MARGIN_PX - 48 - y) // line_height)
    wrapped = _wrap_text_lines(speech, body_font, content_width, draw)
    for line in wrapped[:max_lines]:
        if line:
            draw.text((A4_MARGIN_PX, y), line, fill=(51, 65, 85), font=body_font)  # slate-700
        y += line_height
        if y > A4_HEIGHT_PX - A4_MARGIN_PX - 48:
            break

    # Footer
    footer_y = A4_HEIGHT_PX - A4_MARGIN_PX
    draw.line(
        (A4_MARGIN_PX, footer_y - 16, A4_WIDTH_PX - A4_MARGIN_PX, footer_y - 16),
        fill=(241, 245, 249),  # slate-100
        width=1,
    )
    footer_left = "Speech Notes"
    draw.text((A4_MARGIN_PX, footer_y), footer_left, fill=(148, 163, 184), font=footer_font)  # slate-400
    
    footer_right = f"Slide {slide_number}"
    r_bbox = draw.textbbox((0, 0), footer_right, font=footer_font)
    r_width = r_bbox[2] - r_bbox[0]
    draw.text((A4_WIDTH_PX - A4_MARGIN_PX - r_width, footer_y), footer_right, fill=(148, 163, 184), font=footer_font)

    return page


def first_slide_image_paths(image_paths: list[Path]) -> list[Path]:
    """Return the first variant image for each slide page, in page order.

    ``slide_p##_v##.png`` files are grouped by page number; the lowest variant
    number for each page is kept. Paths that do not match the slide naming
    pattern are ignored.
    """
    by_page: dict[int, tuple[int, Path]] = {}
    for path in image_paths:
        match = SLIDE_IMAGE_PATTERN.match(path.name)
        if not match:
            continue
        page_num = int(match.group(1))
        variant_num = int(match.group(2))
        existing = by_page.get(page_num)
        if existing is None or variant_num < existing[0]:
            by_page[page_num] = (variant_num, path)
    return [by_page[page][1] for page in sorted(by_page)]


def create_speech_pdf(
    image_paths: list[Path],
    slides_by_index: dict[int, Slide],
    output_path: Path,
) -> None:
    """Combine slide images and speech notes into one A4 PDF (one slide per page).

    Always uses the first image variant for each slide page.
    """
    image_paths = first_slide_image_paths(image_paths)
    if not image_paths:
        raise ValueError("At least one slide image is required for speech PDF")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_paths: list[Path] = []

    with tempfile.TemporaryDirectory(prefix="vibesliding_speech_") as tmp_dir:
        tmp = Path(tmp_dir)
        for index, image_path in enumerate(image_paths):
            if not image_path.exists():
                continue
            slide_number = _slide_number_from_path(image_path)
            if slide_number is None:
                continue
            slide = slides_by_index.get(slide_number)
            title = slide.title if slide is not None else f"Slide {slide_number}"
            speech = extract_speech_text(slide.content) if slide is not None else None
            page = render_speech_page(
                image_path,
                slide_number=slide_number,
                slide_title=title,
                speech_text=speech or "",
            )
            page_path = tmp / f"speech_page_{index:04d}.png"
            page.save(page_path, format="PNG")
            page_paths.append(page_path)

        if not page_paths:
            raise ValueError("No valid slide images to include in speech PDF")

        with open(output_path, "wb") as pdf_file:
            pdf_file.write(
                img2pdf.convert(
                    [str(path) for path in page_paths],
                    pagesize=(img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)),
                )
            )


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
    image_dir: Path,
    *,
    pdf_dir: Path | None = None,
    timestamp: str | None = None,
    page_filter: set[int] | None = None,
    variant_filter: set[int] | None = None,
) -> tuple[Path, int]:
    """Rebuild ``presentation_slides_{timestamp}.pdf`` from slide PNGs in *image_dir*."""
    image_paths = collect_slide_image_paths(
        image_dir,
        page_filter=page_filter,
        variant_filter=variant_filter,
    )
    work = pdf_dir or DEFAULT_WORK_DIR
    ts = timestamp or timestamp_from_image_dir(image_dir) or timestamp_slug()
    pdf_path = presentation_slides_pdf_path(work, ts)
    create_pdf_from_images(image_paths, pdf_path)
    return pdf_path, len(image_paths)


def rebuild_speech_pdf(
    image_dir: Path,
    outline_text: str,
    *,
    pdf_dir: Path | None = None,
    timestamp: str | None = None,
    page_filter: set[int] | None = None,
) -> tuple[Path, int]:
    """Rebuild ``presentation_speech_{timestamp}.pdf`` from slide PNGs and outline speech tags.

    Always uses the first image variant for each slide (ignores ``--variant``).
    """
    image_paths = first_slide_image_paths(
        collect_slide_image_paths(image_dir, page_filter=page_filter)
    )
    work = pdf_dir or DEFAULT_WORK_DIR
    ts = timestamp or timestamp_from_image_dir(image_dir) or timestamp_slug()
    pdf_path = presentation_speech_pdf_path(work, ts)
    create_speech_pdf(image_paths, slides_by_index_from_outline(outline_text), pdf_path)
    return pdf_path, len(image_paths)
