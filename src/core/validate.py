"""Structural checks, visual/text balance, and speech length for script markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from src.core.parser import SLIDE_PREFIX_PATTERN, Slide
from src.core.roles import SlideRole, classify_slide_role, is_transition_slide

OUTLINE_STANDARDS_PATH = Path(".cursor/rules/outline-standards.mdc")
SLIDE_HEADER_PATTERN = re.compile(r"^## Slide \d+:", re.MULTILINE)
SLIDE_NUMBER_HEADER_PATTERN = re.compile(r"^## Slide (\d+):", re.MULTILINE)
H2_LINE_PATTERN = re.compile(r"^## ", re.MULTILINE)
BULLET_LINE_PATTERN = re.compile(r"^[-*]\s+(.+)$")
CJK_CHAR_PATTERN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
PAGE_NUMBER_PATTERN = re.compile(r"slide number\s*:\s*(\d+)(\s*(?:/|of\b))?", re.IGNORECASE)

MIN_TRANSITION_SLIDES = 3
MAX_TRANSITION_SLIDES = 6
CONTENT_BALANCE_BAND: Final[tuple[float, float]] = (0.85, 1.35)
NONCONTENT_MAX_RATIO: Final[float] = 1.0
SPEECH_WORDS_PER_SECOND: Final[float] = 2.5
CONTENT_SPEECH_SECONDS: Final[tuple[int, int]] = (60, 120)
NONCONTENT_SPEECH_SECONDS: Final[tuple[int, int]] = (20, 40)


def count_words(text: str) -> int:
    """Count Latin words, treating each CJK character as about half a word."""
    cjk = len(CJK_CHAR_PATTERN.findall(text))
    latin = CJK_CHAR_PATTERN.sub(" ", text)
    return len(latin.split()) + round(cjk * 0.5)


@dataclass(frozen=True)
class SlideBlock:
    """One ``## Slide N:`` block, up to the next H2 heading."""

    number: int
    header: str
    title: str
    body: str
    role: SlideRole

    @property
    def visual(self) -> str:
        _head, has_visual, rest = self.body.partition("[Visual:")
        return rest.split("[Speech:")[0] if has_visual else ""

    @property
    def speech(self) -> str:
        _head, has_speech, rest = self.body.partition("[Speech:")
        if not has_speech:
            return ""
        spoken, closed, _tail = rest.rpartition("]")
        return spoken if closed else rest


def slide_blocks(outline: str) -> list[SlideBlock]:
    """Every ``## Slide N:`` block in order, with its two-tone role."""
    text = outline.strip()
    headers = list(SLIDE_NUMBER_HEADER_PATTERN.finditer(text))
    raw: list[tuple[int, str, str, str]] = []
    for match in headers:
        next_h2 = H2_LINE_PATTERN.search(text, match.end())
        end = next_h2.start() if next_h2 else len(text)
        lines = text[match.start() : end].splitlines()
        header = lines[0].lstrip("#").strip()
        title = SLIDE_PREFIX_PATTERN.sub("", header).strip()
        raw.append((int(match.group(1)), header, title, "\n".join(lines[1:])))
    total = len(raw)
    return [
        SlideBlock(
            number=number,
            header=header,
            title=title,
            body=body,
            role=classify_slide_role(
                Slide(index=number, title=title, content=body),
                position=position,
                total=total,
            ),
        )
        for position, (number, header, title, body) in enumerate(raw)
    ]


def count_transition_slides(outline: str) -> int:
    """Count transition/roadmap slides via title prefix or progress marker."""
    return sum(1 for block in slide_blocks(outline) if is_transition_slide(block.title, block.body))


@dataclass(frozen=True)
class OutlineValidation:
    """Light structural checks on generated outline markdown."""

    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.warnings


def load_outline_standards(path: Path | None = None) -> str:
    """Load outline-standards rule file used as the generation spec."""
    spec_path = path or OUTLINE_STANDARDS_PATH
    if not spec_path.is_file():
        raise FileNotFoundError(
            f"Outline standards not found at {spec_path}. "
            "Ensure .cursor/rules/outline-standards.mdc exists."
        )
    return spec_path.read_text(encoding="utf-8")


def _page_number_warning(block: SlideBlock) -> str | None:
    """Content slides show only their own page number; other roles show none."""
    label = f"## Slide {block.number}:"
    marks = list(PAGE_NUMBER_PATTERN.finditer(block.visual))
    if block.role != "content":
        if marks:
            return f"{label} {block.role} slide should not show a slide number."
        return None
    if not marks:
        return f"{label} missing 'Slide number: {block.number}' in [Visual:]."
    if any(mark.group(1) != str(block.number) or mark.group(2) for mark in marks):
        return (
            f"{label} should show 'Slide number: {block.number}' only — "
            "its own page, never the total."
        )
    return None


def validate_outline(outline: str) -> OutlineValidation:
    """Warn on missing structural elements; do not hard-fail."""
    warnings: list[str] = []
    text = outline.strip()

    if not text.startswith("# PPT Outline:"):
        warnings.append("Outline should start with '# PPT Outline: [Title]'.")

    if "## Appendix" not in text and "Appendix: Global Visual Requirements" not in text:
        warnings.append("Outline is missing '## Appendix: Global Visual Requirements'.")

    blocks = slide_blocks(text)
    if not blocks:
        warnings.append("No '## Slide N:' headers found.")
        return OutlineValidation(warnings=warnings)

    for block in blocks:
        label = f"## Slide {block.number}:"
        if "[Visual:" not in block.body:
            warnings.append(f"{label} missing [Visual:] tag.")
        elif page_warning := _page_number_warning(block):
            warnings.append(page_warning)
        if "[Speech:" not in block.body:
            warnings.append(f"{label} missing [Speech:] tag.")

    transition_count = sum(1 for block in blocks if block.role == "transition")
    if transition_count < MIN_TRANSITION_SLIDES or transition_count > MAX_TRANSITION_SLIDES:
        warnings.append(
            f"Outline has {transition_count} transition slide(s); expected "
            f"{MIN_TRANSITION_SLIDES}-{MAX_TRANSITION_SLIDES} "
            "(titles prefixed 'Roadmap:' with a 'progress bar k/total' marker)."
        )

    return OutlineValidation(warnings=warnings)


@dataclass(frozen=True)
class SlideBalance:
    """Visual/text weight and speech length of one slide (see the standards)."""

    title: str
    bullets: int
    text_words: int
    visual_words: int
    role: SlideRole = "content"
    speech_words: int = 0

    @property
    def ratio(self) -> float:
        """Bullet words per visual word; 0.0 when the slide has no [Visual:] tag."""
        if not self.visual_words:
            return 0.0
        return self.text_words / self.visual_words

    @property
    def speech_seconds(self) -> float:
        """Estimated speaking time of the [Speech:] tag."""
        return self.speech_words / SPEECH_WORDS_PER_SECOND


def measure_slide_balance(outline: str) -> list[SlideBalance]:
    """Measure bullet vs [Visual:] word weight for every slide, in slide order."""
    rows: list[SlideBalance] = []
    for block in slide_blocks(outline):
        head = block.body.partition("[Visual:")[0]
        bullets = [
            matched.group(1)
            for matched in (BULLET_LINE_PATTERN.match(line.strip()) for line in head.splitlines())
            if matched
        ]
        rows.append(
            SlideBalance(
                title=block.header,
                bullets=len(bullets),
                text_words=count_words("\n".join(bullets)),
                visual_words=count_words(block.visual),
                role=block.role,
                speech_words=count_words(block.speech),
            )
        )
    return rows


def _role_phrase(role: SlideRole) -> str:
    article = "an" if role[0] in "aeiou" else "a"
    return f"{article} {role} slide"


def balance_warnings(outline: str) -> list[str]:
    """Flag content slides outside the ratio band and non-content slides that are not visual-led."""
    warnings: list[str] = []
    for row in measure_slide_balance(outline):
        if not row.visual_words:
            continue
        if row.role != "content":
            if row.ratio >= NONCONTENT_MAX_RATIO:
                warnings.append(
                    f"{row.title}: text outweighs visual on {_role_phrase(row.role)} "
                    f"(ratio {row.ratio:.2f} >= {NONCONTENT_MAX_RATIO}); "
                    "trim the bullets or move weight into the composition."
                )
            continue
        low, high = CONTENT_BALANCE_BAND
        if row.ratio > high:
            warnings.append(
                f"{row.title}: mainly text (ratio {row.ratio:.2f} > {high}); "
                "fold bullets into the takeaway or add visual structure."
            )
        elif row.ratio < low:
            warnings.append(
                f"{row.title}: mainly visual (ratio {row.ratio:.2f} < {low}); "
                "add the reasoning the image cannot show."
            )
    return warnings


def speech_warnings(outline: str) -> list[str]:
    """Flag [Speech:] tags whose estimated speaking time is outside their role's range."""
    warnings: list[str] = []
    for row in measure_slide_balance(outline):
        if not row.speech_words:
            continue
        low, high = CONTENT_SPEECH_SECONDS if row.role == "content" else NONCONTENT_SPEECH_SECONDS
        seconds = row.speech_seconds
        if seconds > high:
            warnings.append(
                f"{row.title}: speech runs long (about {seconds:.0f}s > {high}s for "
                f"{_role_phrase(row.role)}); move detail out or tighten the narration."
            )
        elif seconds < low:
            warnings.append(
                f"{row.title}: speech runs short (about {seconds:.0f}s < {low}s for "
                f"{_role_phrase(row.role)}); add context, a callback, or an example."
            )
    return warnings


def strip_code_fences(text: str) -> str:
    """Remove accidental markdown code fences from model output."""
    if not text.strip().startswith("```"):
        return text
    stripped = text.strip()
    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()
