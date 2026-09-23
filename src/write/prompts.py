"""Prompts that expand one plan slide into bullets, a visual, and speech."""

from __future__ import annotations

import re

from src.core.api_client import ARTICLE_CONTEXT_MAX_CHARS, _clip_text
from src.core.facts import cited_fact_ids, fact_id_of
from src.core.validate import CJK_CHAR_PATTERN
from src.plan.parse import PlanDocument, PlanSlide

CONTENT_ROLES = frozenset({"hook", "content", "cta"})

CODE_FENCE_PATTERN = re.compile(r"^```.*?^```[ \t]*\n?", re.MULTILINE | re.DOTALL)
REPO_REF_SENTENCE_PATTERN = re.compile(
    r"(?:^|(?<=\s))[A-Z](?:[^.\n]|\.(?!\s))*?"
    r"`[^`\n]*(?:src/|measure_slide_balance)[^`\n]*`"
    r"(?:[^.\n]|\.(?!\s))*?\.(?=\s|$)",
    re.MULTILINE,
)
HEADING_PATTERN = re.compile(r"^#{1,6}\s")
TABLE_SEPARATOR_PATTERN = re.compile(r"^\|[\s:|-]+\|$")
BALANCE_ROW_KEYS = {
    "hook": "content",
    "content": "content",
    "cta": "content",
    "transition": "transition",
    "cover": "cover",
    "ending": "ending",
}
FACT_WORD_PATTERN = re.compile(r"[a-z0-9][a-z0-9'-]{2,}")
FACT_STOPWORDS = frozenset(
    {
        "the", "and", "for", "are", "but", "not", "you", "your", "with", "this",
        "that", "from", "into", "than", "then", "they", "their", "have", "has",
        "was", "were", "will", "what", "when", "which", "who", "why", "how",
        "can", "its", "our", "out", "over", "more", "most", "one", "two",
        "slide", "point", "evidence", "none",
    }
)

CONTENT_SPEECH = (
    "1-2 minutes of narration (about 150-300 words, or 300-600 Chinese characters)"
)
NONCONTENT_SPEECH = (
    "about 30 seconds of narration (about 50-100 words, or 100-200 Chinese characters)"
)

ROLE_TARGETS = {
    "content": (
        "This is a content slide. Write exactly 6 bullet lines: five "
        "`**Label:** explanation` bullets plus one takeaway "
        "(`Core insight:`, `Core logic:`, or `Anti-pattern:`). "
        "The [Visual:] tag is production art direction of about 100-170 words and "
        f"includes the page number. The [Speech:] tag is {CONTENT_SPEECH} and "
        "ends with a bridge sentence into the next slide."
    ),
    "hook": (
        "This is a hook slide. Use the same shape as a content slide: exactly 6 "
        "bullet lines (five `**Label:** explanation` bullets plus a takeaway), a "
        "[Visual:] of about 100-170 words with the page number, and a [Speech:] of "
        f"{CONTENT_SPEECH} that ends with a bridge into the next slide."
    ),
    "cta": (
        "This is the call to action. Use the same shape as a content slide: exactly "
        "6 bullet lines, a [Visual:] of about 100-170 words with the page number, and "
        f"a [Speech:] of {CONTENT_SPEECH} that states the next step."
    ),
    "transition": (
        "This is a roadmap transition. Write 4 bullets that spell the full roadmap "
        "as text, with the current section bolded. The [Visual:] reuses the section "
        "map and names `progress bar k/total`, where k/total counts sections. "
        "Keep the bullets to about 80-100 words and make the [Visual:] about "
        "100-140 words, so the visual outweighs the text. "
        f"Do not include a slide number. The [Speech:] is {NONCONTENT_SPEECH}."
    ),
    "cover": (
        "This is the cover. Write 3-4 bullets (about 70-100 words) that make the "
        "premise legible. The [Visual:] is a dark curtain cover of about 100-140 "
        "words, so the visual outweighs the text. Do not include a slide number. "
        f"The [Speech:] is {NONCONTENT_SPEECH} and opens the talk."
    ),
    "ending": (
        "This is the ending. Write 3-4 bullets (about 70-100 words) with one clear "
        "take-home message. The [Visual:] reconnects to the cover on a dark "
        "background in about 100-140 words, so the visual outweighs the text, and "
        f"has no slide number. The [Speech:] is {NONCONTENT_SPEECH}; it recaps the "
        "thesis and invites questions."
    ),
}


def _keep_role_rows(text: str, role: str) -> str:
    """In markdown tables, keep the header, separator, and the row for *role*."""
    key = BALANCE_ROW_KEYS.get(role, "content")
    kept: list[str] = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            kept.append(line)
            continue
        if not in_table or TABLE_SEPARATOR_PATTERN.match(stripped):
            in_table = True
            kept.append(line)
            continue
        first_cell = stripped.strip("|").split("|", 1)[0].lower()
        if key in first_cell:
            kept.append(line)
    return "\n".join(kept)


def _heading_level(line: str) -> int:
    return len(line) - len(line.lstrip("#")) if HEADING_PATTERN.match(line) else 0


def _drop_empty_headings(text: str) -> str:
    """Remove headings left with no body (only same-or-higher headings follow)."""
    lines = text.splitlines()
    kept: list[str] = []
    for position, line in enumerate(lines):
        level = _heading_level(line)
        if level:
            following = next((later for later in lines[position + 1 :] if later.strip()), "")
            next_level = _heading_level(following)
            if not following or (next_level and next_level <= level):
                continue
        kept.append(line)
    return "\n".join(kept)


def writing_sections(standards: str, role: str | None = None) -> str:
    """Keep the writing, visual, and speech rules for one slide.

    Drops plan-format instructions, fenced example slides (their ``## Slide N``
    headings leak into model output), and sentences that point at repo code.
    With *role*, balance tables keep only that role's row.
    """
    start = standards.find("## Writing Standards")
    end = standards.find("## Appendix Requirements")
    if start == -1:
        section = standards
    elif end == -1 or end <= start:
        section = standards[start:]
    else:
        section = standards[start:end]

    section = CODE_FENCE_PATTERN.sub("", section)
    section = REPO_REF_SENTENCE_PATTERN.sub("", section)
    section = re.sub(r"[ \t]{2,}", " ", section)
    section = re.sub(r"[ \t]+$", "", section, flags=re.MULTILINE)
    if role is not None:
        section = _keep_role_rows(section, role)
    section = _drop_empty_headings(section)
    return re.sub(r"\n{3,}", "\n\n", section).strip()


def build_system_prompt(standards: str, slide: PlanSlide) -> str:
    role = slide.role or "content"
    target = ROLE_TARGETS.get(role, ROLE_TARGETS["content"])
    if role in CONTENT_ROLES:
        target += (
            f" Write the page number as `Slide number: {slide.index}` and never "
            "show the total page count."
        )
    return (
        "You write the body of a single presentation slide.\n"
        "Output ONLY markdown: the bullet lines, then exactly one [Visual:] tag, "
        "then exactly one [Speech:] tag.\n"
        "No heading, no code fences, no commentary, and no [Style:] or [Reference:] tags.\n"
        "Do not invent facts beyond the evidence and facts briefing.\n\n"
        f"# THIS SLIDE\nSlide {slide.index}. Role: {role}.\n{target}\n\n"
        f"# STANDARDS\n{writing_sections(standards, role)}"
    )


def _fact_terms(text: str) -> set[str]:
    """Lowercase content words, plus CJK character bigrams."""
    lower = text.lower()
    terms = {word for word in FACT_WORD_PATTERN.findall(lower) if word not in FACT_STOPWORDS}
    cjk = "".join(CJK_CHAR_PATTERN.findall(text))
    terms.update(cjk[i : i + 2] for i in range(len(cjk) - 1))
    return terms


def _fact_chunks(facts: str) -> list[tuple[str | None, str]]:
    """Split facts into (heading, chunk) pairs: one per bullet or paragraph."""
    chunks: list[tuple[str | None, str]] = []
    heading: str | None = None
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            chunks.append((heading, "\n".join(paragraph).strip()))
            paragraph.clear()

    for line in facts.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
        elif HEADING_PATTERN.match(stripped):
            flush()
            heading = stripped
        elif re.match(r"^(?:[-*+]|\d+[.)])\s", stripped):
            flush()
            paragraph.append(line.rstrip())
        elif paragraph and re.match(r"^\s+\S", line):
            paragraph.append(line.rstrip())
        else:
            if paragraph and re.match(r"^(?:[-*+]|\d+[.)])\s", paragraph[0].strip()):
                flush()
            paragraph.append(line.rstrip())
    flush()
    return chunks


def select_relevant_facts(
    facts: str,
    slide: PlanSlide,
    budget: int = ARTICLE_CONTEXT_MAX_CHARS,
) -> str:
    """Pick this slide's cited facts, then the ones sharing the most terms, within *budget*.

    Facts whose ID the slide's ``Evidence:`` lines cite come first. Short facts
    files are returned whole. Chosen chunks keep their original order and
    headings. With no citation and no overlap at all, fall back to the file head.
    """
    text = facts.strip()
    if not text:
        return ""
    if len(text) <= budget:
        return text

    cited = set(cited_fact_ids(slide.evidence))
    query = _fact_terms(
        " ".join([slide.title, slide.visual_hook, *slide.points, *slide.evidence])
    )
    chunks = _fact_chunks(text)
    scored = [
        (fact_id_of(chunk) in cited, len(query & _fact_terms(chunk)), position)
        for position, (_heading, chunk) in enumerate(chunks)
    ]
    ranked = sorted(
        (item for item in scored if item[0] or item[1] > 0),
        key=lambda item: (not item[0], -item[1], item[2]),
    )
    if not ranked:
        return _clip_text(text, budget)

    chosen: set[int] = set()
    used = 0
    for _cited, _score, position in ranked:
        heading, chunk = chunks[position]
        cost = len(chunk) + 1 + (len(heading) + 1 if heading else 0)
        if used + cost > budget:
            continue
        chosen.add(position)
        used += cost

    if not chosen:
        return _clip_text(chunks[ranked[0][2]][1], budget)

    lines: list[str] = []
    last_heading: str | None = None
    for position in sorted(chosen):
        heading, chunk = chunks[position]
        if heading and heading != last_heading:
            lines.append(heading)
            last_heading = heading
        lines.append(chunk)
    return "\n".join(lines)


def _neighbor_block(label: str, other: PlanSlide) -> str:
    points = "\n".join(f"  - {item}" for item in other.points) or "  - (none)"
    return (
        f"- {label}: Slide {other.index}, {other.title} "
        f"(role: {other.role or 'content'})\n{points}"
    )


def build_user_prompt(
    document: PlanDocument,
    slide: PlanSlide,
    *,
    idea: str,
    facts: str,
) -> str:
    neighbors: list[str] = []
    for other in document.slides:
        marker = ""
        if other.index == slide.index - 1:
            marker = " (previous)"
        elif other.index == slide.index:
            marker = " (this slide)"
        elif other.index == slide.index + 1:
            marker = " (next)"
        neighbors.append(f"- Slide {other.index}: {other.title}{marker}")

    position = next(
        (offset for offset, other in enumerate(document.slides) if other.index == slide.index),
        None,
    )
    adjacent: list[str] = []
    if position is not None:
        if position > 0:
            adjacent.append(_neighbor_block("Previous", document.slides[position - 1]))
        if position + 1 < len(document.slides):
            adjacent.append(_neighbor_block("Next", document.slides[position + 1]))
    adjacent_block = "\n".join(adjacent) or "(none)"

    evidence = "\n".join(f"- {item}" for item in slide.evidence) or "- (none)"
    points = "\n".join(f"- {item}" for item in slide.points) or "- (none)"
    facts_block = select_relevant_facts(facts, slide) or "(none)"
    idea_block = idea.strip()[:2000] or "(none)"

    return f"""# DECK
Title: {document.title or "Untitled"}

# IDEA (audience and language)
{idea_block}

# SLIDE ORDER
{chr(10).join(neighbors)}

# NEIGHBOURS (for callbacks and the bridge sentence; do not restate their points)
{adjacent_block}

# THIS SLIDE
Title: {slide.title}
Role: {slide.role or "content"}
Section: {slide.section or "n/a"}
Points:
{points}
Evidence:
{evidence}
Visual hook: {slide.visual_hook or "(none)"}

# FACTS
{facts_block}

# APPENDIX
{document.appendix or "(none)"}
"""
