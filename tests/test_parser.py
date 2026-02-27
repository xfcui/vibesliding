import pytest
from src.parser import parse_markdown, Slide

def test_parse_markdown_basic():
    md = """
## Slide 1: Introduction
This is the first slide.

## Slide 2: Details
- Point 1
- Point 2
"""
    slides = parse_markdown(md)
    assert len(slides) == 2
    assert slides[0].title == "Introduction"
    assert "This is the first slide." in slides[0].content
    assert slides[1].title == "Details"
    assert "Point 1" in slides[1].content

def test_parse_markdown_empty():
    assert parse_markdown("") == []
    assert parse_markdown("Just some text without H2") == []

def test_parse_markdown_no_prefix():
    md = "## No Prefix Title\nContent"
    slides = parse_markdown(md)
    assert slides[0].title == "No Prefix Title"
