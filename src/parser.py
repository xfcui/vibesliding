"""Markdown parser - extracts slides from H2 headings."""

import re
from dataclasses import dataclass


@dataclass
class Slide:
    """A single slide extracted from markdown."""

    index: int
    title: str
    content: str  # Full markdown content under this heading


def parse_markdown(markdown_text: str) -> list[Slide]:
    """Split markdown by ## headings into Slide objects.

    Each H2 (## Title) starts a new slide. Content between H2s belongs to that slide.
    """
    # Match ## at start of line (optional leading whitespace)
    h2_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    slides: list[Slide] = []
    matches = list(h2_pattern.finditer(markdown_text))

    if not matches:
        return slides

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        # Content runs until the next H2 or end of text
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        content = markdown_text[start:end].strip()
        slides.append(Slide(index=i + 1, title=title, content=content))

    return slides
