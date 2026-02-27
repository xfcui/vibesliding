import pytest
from pathlib import Path
from PIL import Image
import io
from src.output import save_image, create_pdf_from_images, TARGET_RESOLUTION

def test_save_image(tmp_path):
    file_path = tmp_path / "test.png"
    data = b"fake-image-data"
    save_image(data, file_path)
    assert file_path.read_bytes() == data

def test_create_pdf_from_images(tmp_path):
    # Create a dummy image
    img_path = tmp_path / "slide1.png"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(img_path)
    
    pdf_path = tmp_path / "output.pdf"
    create_pdf_from_images([img_path], pdf_path)
    
    assert pdf_path.exists()
    # Check if image was resized
    with Image.open(img_path) as saved_img:
        assert saved_img.size == TARGET_RESOLUTION
