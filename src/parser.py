"""Markdown parser - extracts slides from H2 headings."""

import re
from dataclasses import dataclass
from typing import Final

# Constants
H2_PATTERN: Final[re.Pattern] = re.compile(r"^##\s+(.+)$", re.MULTILINE)
SLIDE_PREFIX_PATTERN: Final[re.Pattern] = re.compile(r"^Slide\s+\d+:\s*", re.IGNORECASE)


@dataclass
class Slide:
    """A single slide extracted from markdown outline.
    
    Attributes:
        index: 1-based slide number
        title: Slide title text (from H2 heading)
        content: Full markdown content under this heading
    """

    index: int
    title: str
    content: str


def parse_markdown(markdown_text: str) -> list[Slide]:
    """Split markdown by ## headings into Slide objects.
    
    Each H2 (## Title) starts a new slide. Content between H2s belongs to that slide.
    
    Args:
        markdown_text: Raw markdown text with H2 headings
        
    Returns:
        List of Slide objects in order of appearance
    """
    matches = list(H2_PATTERN.finditer(markdown_text))
    
    if not matches:
        return []

    slides: list[Slide] = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        # Remove "Slide n:" prefix if present
        title = SLIDE_PREFIX_PATTERN.sub("", title).strip()
        start = match.end()
        
        # Content runs until the next H2 or end of text
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        content = markdown_text[start:end].strip()
        
        slides.append(Slide(index=i + 1, title=title, content=content))

    return slides
