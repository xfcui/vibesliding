import pytest
from pathlib import Path
from PIL import Image, ImageDraw

from src.core.api_client import STYLE_IMAGE_PIXEL_SIZE
from src.core.export import (
    build_contact_sheet,
    collect_slide_image_paths,
    create_pdf_from_images,
    create_speech_pdf,
    first_slide_image_paths,
    rebuild_combined_pdf,
    rebuild_speech_pdf,
    render_speech_page,
    save_image,
    save_style_reference_image,
    slides_by_index_from_outline,
    _load_truetype_font,
    _wrap_text_lines,
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


def test_first_slide_image_paths_picks_lowest_variant(tmp_path):
    for name in (
        "slide_p02_v02.png",
        "slide_p01_v02.png",
        "slide_p01_v01.png",
        "slide_p02_v01.png",
        "notes.txt",
    ):
        (tmp_path / name).write_bytes(b"x")

    assert [p.name for p in first_slide_image_paths(list(tmp_path.iterdir()))] == [
        "slide_p01_v01.png",
        "slide_p02_v01.png",
    ]


def test_rebuild_combined_pdf(tmp_path):
    image_dir = tmp_path / "image_test"
    image_dir.mkdir()
    for name in ("slide_p01_v01.png", "slide_p02_v01.png"):
        img = Image.new("RGB", (50, 50), color="blue")
        img.save(image_dir / name)

    pdf_path, count = rebuild_combined_pdf(image_dir, pdf_dir=tmp_path, timestamp="test")
    assert count == 2
    assert pdf_path == tmp_path / "presentation_slides_test.pdf"
    assert pdf_path.exists()


def test_create_speech_pdf(tmp_path):
    outline = """# Deck

---

## Slide 1: Cover
- Hook
[Visual: title]
[Speech: Welcome everyone to this talk.]

---

## Slide 2: Body
- Point
[Visual: diagram]
[Speech: The key insight is simple.]
"""
    img = Image.new("RGB", (320, 180), color="red")
    img.save(tmp_path / "slide_p01_v01.png")
    img.save(tmp_path / "slide_p01_v02.png")
    img.save(tmp_path / "slide_p02_v01.png")

    pdf_path = tmp_path / "presentation_speech.pdf"
    create_speech_pdf(
        [
            tmp_path / "slide_p01_v01.png",
            tmp_path / "slide_p01_v02.png",
            tmp_path / "slide_p02_v01.png",
        ],
        slides_by_index_from_outline(outline),
        pdf_path,
    )

    assert pdf_path.exists()


def test_rebuild_speech_pdf(tmp_path):
    outline = """# Deck

---

## Slide 1: Cover
[Speech: Hello.]

---

## Slide 2: Body
[Speech: Next.]
"""
    image_dir = tmp_path / "image_test"
    image_dir.mkdir()
    for name in ("slide_p01_v01.png", "slide_p01_v02.png", "slide_p02_v01.png"):
        Image.new("RGB", (80, 45), color="green").save(image_dir / name)

    pdf_path, count = rebuild_speech_pdf(
        image_dir, outline, pdf_dir=tmp_path, timestamp="test"
    )
    assert count == 2
    assert pdf_path == tmp_path / "presentation_speech_test.pdf"
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


def test_wrap_text_lines_chinese(tmp_path):
    font = _load_truetype_font(24)
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    max_width = 240
    speech = (
        "各位老师，各位家长，亲爱的2022级计算机菁英班的同学们，"
        "大家下午好！今天是属于你们的日子。"
    )
    lines = _wrap_text_lines(speech, font, max_width, draw)

    assert len(lines) >= 2
    assert all(_line_width(line, font, draw) <= max_width for line in lines if line)
    assert "".join(line.replace(" ", "") for line in lines) == speech.replace(" ", "")


def _line_width(line, font, draw):
    if not line:
        return 0
    bbox = draw.textbbox((0, 0), line, font=font)
    return bbox[2] - bbox[0]


def test_wrap_text_lines_mixed_chinese_english(tmp_path):
    font = _load_truetype_font(24)
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    max_width = 300
    speech = "CCPC 2024 赛场：薛润泽、郭荣祥、乐恩玮组队出战中国大学生程序设计竞赛"
    lines = _wrap_text_lines(speech, font, max_width, draw)

    assert len(lines) >= 2
    assert all(_line_width(line, font, draw) <= max_width for line in lines if line)
    joined = "".join(
        part for line in lines for part in line.split()
    )
    assert "CCPC" in joined
    assert "薛润泽" in speech


def test_create_speech_pdf_chinese(tmp_path):
    outline = """# PPT Outline: 测试

---

## Slide 1: 海阔天空
- 封面
[Visual: cover]
[Speech: 各位老师，各位家长，亲爱的同学们，大家下午好！]

---
"""
    img = Image.new("RGB", (320, 180), color="red")
    img.save(tmp_path / "slide_p01_v01.png")

    pdf_path = tmp_path / "presentation_speech_zh.pdf"
    create_speech_pdf(
        [tmp_path / "slide_p01_v01.png"],
        slides_by_index_from_outline(outline),
        pdf_path,
    )

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0


def test_render_speech_page_chinese_title(tmp_path):
    slide_path = tmp_path / "slide_p01_v01.png"
    Image.new("RGB", (320, 180), color="blue").save(slide_path)
    page = render_speech_page(
        slide_path,
        slide_number=1,
        slide_title="海阔天空，大有可为",
        speech_text="今天是属于你们的日子。",
    )
    assert page.size == (1240, 1754)
