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
