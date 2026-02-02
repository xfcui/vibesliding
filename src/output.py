"""Output handler - save images and generate PDF."""

import io
from pathlib import Path

import img2pdf
from PIL import Image


def save_image(image_data: bytes, path: Path) -> None:
    """Save raw image bytes to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_data)


def create_pdf_from_images(image_paths: list[Path], output_path: Path) -> None:
    """Combine multiple images into a single PDF, ensuring consistent 16:9 size."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    valid_paths = [p for p in image_paths if p.exists()]
    if not valid_paths:
        raise ValueError("No valid image paths to create PDF")
    
    target_size = (1920, 1080)
    processed_images = []
    
    for p in valid_paths:
        try:
            with Image.open(p) as img:
                # Check if resize is needed
                if img.size != target_size:
                    # Resize to target 16:9 resolution
                    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                    
                    # Save to bytes
                    img_byte_arr = io.BytesIO()
                    # Default to PNG if format is unknown, or keep original format
                    fmt = img.format if img.format else 'PNG'
                    img_resized.save(img_byte_arr, format=fmt)
                    processed_images.append(img_byte_arr.getvalue())
                else:
                    # If size is correct, use the file directly
                    processed_images.append(p.read_bytes())
        except Exception as e:
            print(f"Warning: skipping invalid image {p}: {e}")
            continue

    if not processed_images:
        raise ValueError("No valid images to process")

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(processed_images))
