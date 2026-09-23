from src.core.parser import extract_global_style, extract_speech_text, parse_markdown, Slide

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


def test_extract_speech_text_uses_last_nonempty():
    skipped = "[Speech: ]\n[Speech: First take.]\n[Speech:   ]"
    assert extract_speech_text(skipped) == "First take."
    latest = "[Speech: first take]\n[Speech: ]\n[Speech: final take]"
    assert extract_speech_text(latest) == "final take"


def test_extract_speech_text_missing_or_blank():
    assert extract_speech_text("no speech tag") is None
    assert extract_speech_text("[Speech:   ]") == ""
