import pytest
from pathlib import Path
from PIL import Image

from src.core.api_client import STYLE_IMAGE_PIXEL_SIZE
from src.core.export import (
    build_contact_sheet,
    collect_slide_image_paths,
    create_pdf_from_images,
    rebuild_combined_pdf,
    save_image,
    save_style_reference_image,
)


def test_save_image(tmp_path):
    file_path = tmp_path / "test.png"
    data = b"fake-image-data"
    save_image(data, file_path)
    assert file_path.read_bytes() == data


def test_save_style_reference_image_downscales_to_1k(tmp_path):
    src = tmp_path / "source.png"
    Image.new("RGB", (2560, 1440), color="blue").save(src)
    out = tmp_path / "style_cover.png"
    save_style_reference_image(
        src.read_bytes(),
        out,
        target_size=STYLE_IMAGE_PIXEL_SIZE,
    )
    with Image.open(out) as img:
        assert img.size == STYLE_IMAGE_PIXEL_SIZE


def test_create_pdf_from_images(tmp_path):
    img_path = tmp_path / "slide1.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)

    pdf_path = tmp_path / "output.pdf"
    create_pdf_from_images([img_path], pdf_path)

    assert pdf_path.exists()


def test_collect_slide_image_paths_order_and_filters(tmp_path):
    for name in (
        "slide_p02_v01.png",
        "slide_p01_v02.png",
        "slide_p01_v01.png",
        "notes.txt",
    ):
        (tmp_path / name).write_bytes(b"x")

    assert [p.name for p in collect_slide_image_paths(tmp_path)] == [
        "slide_p01_v01.png",
        "slide_p01_v02.png",
        "slide_p02_v01.png",
    ]
    assert [p.name for p in collect_slide_image_paths(tmp_path, page_filter={2})] == [
        "slide_p02_v01.png",
    ]
    assert [p.name for p in collect_slide_image_paths(tmp_path, variant_filter={1})] == [
        "slide_p01_v01.png",
        "slide_p02_v01.png",
    ]


def test_collect_slide_image_paths_empty_raises(tmp_path):
    with pytest.raises(ValueError, match="No slide images"):
        collect_slide_image_paths(tmp_path)


def test_rebuild_combined_pdf(tmp_path):
    for name in ("slide_p01_v01.png", "slide_p02_v01.png"):
        img = Image.new("RGB", (50, 50), color="blue")
        img.save(tmp_path / name)

    pdf_path, count = rebuild_combined_pdf(tmp_path)
    assert count == 2
    assert pdf_path == tmp_path / "slide_combined.pdf"
    assert pdf_path.exists()


def test_build_contact_sheet(tmp_path):
    images: list[bytes] = []
    for color in ("red", "green", "blue", "yellow"):
        buf = tmp_path / f"{color}.png"
        Image.new("RGB", (120, 80), color=color).save(buf)
        images.append(buf.read_bytes())

    sheet_path = tmp_path / "choices.png"
    build_contact_sheet(images, sheet_path, columns=2)

    assert sheet_path.exists()
    with Image.open(sheet_path) as sheet:
        assert sheet.size == (240, 160)


def test_build_contact_sheet_with_title(tmp_path):
    images: list[bytes] = []
    for color in ("red", "green"):
        buf = tmp_path / f"{color}.png"
        Image.new("RGB", (100, 60), color=color).save(buf)
        images.append(buf.read_bytes())

    sheet_path = tmp_path / "choices_titled.png"
    build_contact_sheet(images, sheet_path, columns=2, title="BASE — pick 1-2")

    assert sheet_path.exists()
    with Image.open(sheet_path) as sheet:
        assert sheet.width == 200
        assert sheet.height > 60


def test_build_contact_sheet_empty_raises(tmp_path):
    with pytest.raises(ValueError, match="At least one image"):
        build_contact_sheet([], tmp_path / "empty.png")
