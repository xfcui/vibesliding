from src.outline.parser import parse_markdown, Slide, extract_global_style

def test_parse_markdown():
    md = """
# Title

## Slide 1: First
Content 1

## Slide 2: Second
Content 2
"""
    slides = parse_markdown(md)
    assert len(slides) == 2
    assert slides[0].title == "First"
    assert slides[0].content == "Content 1"
    assert slides[1].title == "Second"


def test_extract_global_style():
    slides = [
        Slide(index=1, title="Global Visual Requirements", content="Style content"),
        Slide(index=2, title="Regular Slide", content="Regular content"),
    ]
    assert extract_global_style(slides) == "Style content"
