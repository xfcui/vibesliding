"""Classify outline slides into cover / transition / content / ending roles."""

from __future__ import annotations

import re
from typing import Final, Literal

from src.outline.parser import Slide

SlideRole = Literal["cover", "transition", "content", "ending"]

TRANSITION_TITLE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(roadmap|transition|section|agenda|objectives)\b",
    re.IGNORECASE,
)
PROGRESS_MARKER_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"progress bar\s*\d+\s*/\s*\d+|\bact\s+\d+\s+of\s+\d+\b",
    re.IGNORECASE,
)
ENDING_TITLE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(thank\s*you|thanks|q\s*&\s*a|questions?|closing|end(?:ing)?|wrap[\s-]?up)\b",
    re.IGNORECASE,
)


def is_transition_slide(title: str, content: str = "") -> bool:
    """Return True when the slide is a section-divider / roadmap slide."""
    return bool(
        TRANSITION_TITLE_PATTERN.match(title.strip())
        or PROGRESS_MARKER_PATTERN.search(content)
    )


def classify_slide_role(
    slide: Slide,
    *,
    position: int,
    total: int,
) -> SlideRole:
    """Classify a slide for two-tone style routing.

    ``position`` is 0-based among non-appendix slides; ``total`` is that list length.
    """
    if total < 1:
        raise ValueError("total must be >= 1")
    if position < 0 or position >= total:
        raise ValueError(f"position {position} out of range for total {total}")

    if is_transition_slide(slide.title, slide.content):
        return "transition"
    if position == 0:
        return "cover"
    if position == total - 1:
        return "ending"
    if ENDING_TITLE_PATTERN.search(slide.title):
        return "ending"
    return "content"
