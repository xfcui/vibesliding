"""Output handler - save images and generate PDF."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Final, List, Tuple

import img2pdf
from PIL import Image

# Constants
TARGET_RESOLUTION: Final[tuple[int, int]] = (1920, 1080)  # 16:9 aspect ratio
DEFAULT_IMAGE_FORMAT: Final[str] = 'PNG'


def save_image(image_data: bytes, path: Path) -> None:
    """Save raw image bytes to file.
    
    Args:
        image_data: Raw image bytes
        path: Destination file path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_data)


def create_pdf_from_images(image_paths: list[Path], output_path: Path) -> None:
    """Combine multiple images into a single PDF with consistent 16:9 resolution.
    
    All images are resized to 1920x1080 if needed to ensure consistency.
    
    Args:
        image_paths: List of image file paths to combine
        output_path: Destination PDF file path
        
    Raises:
        ValueError: If no valid images are provided or found
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    valid_paths = [p for p in image_paths if p.exists()]
    if not valid_paths:
        raise ValueError("No valid image paths to create PDF")
    
    processed_images: list[bytes] = []
    
    for path in valid_paths:
        try:
            with Image.open(path) as img:
                # Check if resize is needed
                if img.size != TARGET_RESOLUTION:
                    # Resize to target 16:9 resolution
                    img_resized = img.resize(TARGET_RESOLUTION, Image.Resampling.LANCZOS)
                    
                    # Save to bytes buffer
                    img_byte_arr = io.BytesIO()
                    fmt = img.format if img.format else DEFAULT_IMAGE_FORMAT
                    img_resized.save(img_byte_arr, format=fmt)
                    processed_images.append(img_byte_arr.getvalue())
                else:
                    # Size is correct, use file directly
                    processed_images.append(path.read_bytes())
        except Exception as e:
            print(f"Warning: skipping invalid image {path}: {e}")
            continue

    if not processed_images:
        raise ValueError("No valid images to process after filtering")

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(processed_images))
