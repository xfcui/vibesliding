"""Parse a deck plan into structured slides."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.core.parser import SLIDE_PREFIX_PATTERN
from src.core.validate import SLIDE_HEADER_PATTERN

PLAN_ROLES = ("cover", "hook", "content", "transition", "cta", "ending")
ROLE_PATTERN = re.compile(
    r"^[-*]\s+Role:\s*(cover|hook|content|transition|cta|ending)\b",
    re.IGNORECASE,
)
SECTION_PATTERN = re.compile(
    r"^[-*]\s+Section:\s*(\d+)\s*/\s*(\d+)\s*$",
    re.IGNORECASE,
)
POINT_PATTERN = re.compile(r"^[-*]\s+Point:\s*(.+)$", re.IGNORECASE)
EVIDENCE_PATTERN = re.compile(r"^[-*]\s+Evidence:\s*(.+)$", re.IGNORECASE)
VISUAL_HOOK_PATTERN = re.compile(r"^[-*]\s+Visual hook:\s*(.+)$", re.IGNORECASE)
STYLE_TAG_PATTERN = re.compile(r"\[Styles?\s*:\s*(.*?)\]", re.IGNORECASE | re.DOTALL)
REFERENCE_TAG_PATTERN = re.compile(
    r"\[(?:Reference(?:\s+(?:Images?|Photos?))?|Refs?)\s*:\s*(.*?)\]",
    re.IGNORECASE | re.DOTALL,
)
TITLE_PATTERN = re.compile(r"^#\s*PPT Outline:\s*(.+)$", re.MULTILINE)
APPENDIX_PATTERN = re.compile(
    r"^##\s+Appendix:.*$",
    re.MULTILINE,
)


@dataclass
class PlanSlide:
    """One slide in a deck plan."""

    index: int
    title: str
    role: str | None
    section: str | None
    points: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    visual_hook: str = ""
    visual_hook_count: int = 0
    style_tag: str | None = None
    reference_tag: str | None = None
    body: str = ""


@dataclass
class PlanDocument:
    """A parsed deck plan."""

    title: str
    slides: list[PlanSlide]
    appendix: str


def _tag(pattern: re.Pattern[str], body: str, label: str) -> str | None:
    match = pattern.search(body)
    if not match:
        return None
    value = " ".join(match.group(1).split())
    return f"[{label}: {value}]" if value else None


def parse_plan(text: str) -> PlanDocument:
    """Split a plan into title, slides, and appendix."""
    title_match = TITLE_PATTERN.search(text)
    title = title_match.group(1).strip() if title_match else ""
    appendix_match = APPENDIX_PATTERN.search(text)
    appendix = text[appendix_match.start() :].strip() if appendix_match else ""
    body = text[: appendix_match.start()] if appendix_match else text

    headers = list(SLIDE_HEADER_PATTERN.finditer(body))
    slides: list[PlanSlide] = []
    for index, match in enumerate(headers):
        line_end = body.find("\n", match.start())
        if line_end == -1:
            line_end = len(body)
        header_line = body[match.start() : line_end]
        start = line_end + 1
        end = headers[index + 1].start() if index + 1 < len(headers) else len(body)
        block = body[start:end].strip()
        slide_title = SLIDE_PREFIX_PATTERN.sub("", header_line.lstrip("#").strip()).strip()
        role = None
        section = None
        points: list[str] = []
        evidence: list[str] = []
        visual_hook = ""
        visual_hook_count = 0
        for line in block.splitlines():
            stripped = line.strip()
            role_match = ROLE_PATTERN.match(stripped)
            if role_match:
                role = role_match.group(1).lower()
                continue
            section_match = SECTION_PATTERN.match(stripped)
            if section_match:
                section = f"{section_match.group(1)}/{section_match.group(2)}"
                continue
            point_match = POINT_PATTERN.match(stripped)
            if point_match:
                points.append(point_match.group(1).strip())
                continue
            evidence_match = EVIDENCE_PATTERN.match(stripped)
            if evidence_match:
                evidence.append(evidence_match.group(1).strip())
                continue
            hook_match = VISUAL_HOOK_PATTERN.match(stripped)
            if hook_match:
                visual_hook = hook_match.group(1).strip()
                visual_hook_count += 1
        slides.append(
            PlanSlide(
                index=index + 1,
                title=slide_title,
                role=role,
                section=section,
                points=points,
                evidence=evidence,
                visual_hook=visual_hook,
                visual_hook_count=visual_hook_count,
                style_tag=_tag(STYLE_TAG_PATTERN, block, "Style"),
                reference_tag=_tag(REFERENCE_TAG_PATTERN, block, "Reference"),
                body=block,
            )
        )
    return PlanDocument(title=title, slides=slides, appendix=appendix)
