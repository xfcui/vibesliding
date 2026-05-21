import pytest
from pathlib import Path
from src.generator import SlideImageGenerator
from src.parser import Slide

@pytest.fixture
def generator(client):
    return SlideImageGenerator(client)

def test_build_full_outline_context(generator):
    slides = [
        Slide(index=1, title="Title 1", content="Content 1"),
        Slide(index=2, title="Title 2", content="Content 2")
    ]
    context = generator._build_full_outline_context(slides)
    assert "Slide 1: Title 1" in context
    assert "Slide 2: Title 2" in context

def test_extract_global_style(generator):
    slides = [
        Slide(index=1, title="Global Visual Requirements", content="Style content"),
        Slide(index=2, title="Regular Slide", content="Regular content")
    ]
    style = generator._extract_global_style(slides)
    assert style == "Style content"

def test_build_prompt(generator):
    slide = Slide(index=1, title="Test Slide", content="Test content [Visual: A test visual]")
    user_p, sys_p = generator._build_prompt(slide, "Outline context")
    
    assert "Test Slide" in user_p
    assert "A test visual" in user_p
    assert "Outline context" in sys_p
    assert "Test content" in user_p


def test_resolve_slide_reference_images_accepts_cursor_paths(generator, tmp_path):
    ref = tmp_path / "person.png"
    ref.write_bytes(b"fake")
    slide = Slide(
        index=1,
        title="Cover",
        content=f"Intro\n[Reference: @{ref}]\n[Visual: use the photo]",
    )

    assert generator._resolve_reference_image_paths(slide) == [ref]


def test_resolve_slide_reference_images_expands_globs(generator, tmp_path):
    (tmp_path / "peter_2.png").write_bytes(b"2")
    (tmp_path / "peter_1.png").write_bytes(b"1")
    slide = Slide(
        index=2,
        title="Hook",
        content="[Reference: peter_*.png]",
    )

    resolved = generator._resolve_reference_image_paths(slide, outline_dir=tmp_path)

    assert [p.name for p in resolved] == ["peter_1.png", "peter_2.png"]


def test_build_prompt_strips_reference_tags_and_describes_image_roles(generator, tmp_path):
    ref = tmp_path / "data.png"
    slide = Slide(
        index=1,
        title="Cover",
        content=f"Cover copy\n[Reference: {ref}]\n[Visual: use my coding figure]",
    )

    user_p, sys_p = generator._build_prompt(
        slide,
        "Outline context",
        slide_reference_paths=[ref],
        style_reference_count=2,
        with_style_reference=True,
    )

    assert "[Reference:" not in user_p
    assert "Cover copy" in user_p
    assert "Attached Slide References" in user_p
    assert "Attached image(s) 1-2: deck visual style references only" in sys_p
    assert "slide-specific photo/content references" in sys_p
    assert "Photorealistic people are allowed" in sys_p
