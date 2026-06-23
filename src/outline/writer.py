"""Convert DeepResearch output into a presentation outline."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.core.api_client import OpenRouterClient

OUTLINE_STANDARDS_PATH = Path(".cursor/rules/outline-standards.mdc")
SLIDE_HEADER_PATTERN = re.compile(r"^## Slide \d+:", re.MULTILINE)

MIN_TRANSITION_SLIDES = 3
MAX_TRANSITION_SLIDES = 6
# Transition slides are detectable by a "Roadmap:"-style title prefix or a
# progress marker (e.g. "progress bar 6/29") in the slide body.
TRANSITION_TITLE_PATTERN = re.compile(
    r"^## Slide \d+:\s*(roadmap|transition|section|agenda|objectives)\b",
    re.IGNORECASE,
)
PROGRESS_MARKER_PATTERN = re.compile(
    r"progress bar\s*\d+\s*/\s*\d+|\bact\s+\d+\s+of\s+\d+\b",
    re.IGNORECASE,
)


def count_transition_slides(outline: str) -> int:
    """Count transition/roadmap slides via title prefix or progress marker."""
    text = outline.strip()
    slide_headers = list(SLIDE_HEADER_PATTERN.finditer(text))
    count = 0
    for index, match in enumerate(slide_headers):
        start = match.start()
        end = slide_headers[index + 1].start() if index + 1 < len(slide_headers) else len(text)
        block = text[start:end]
        header_line = block.splitlines()[0] if block else ""
        if TRANSITION_TITLE_PATTERN.match(header_line) or PROGRESS_MARKER_PATTERN.search(block):
            count += 1
    return count


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


def _build_source_context(source: str | None) -> str:
    """Build combined source document block with priority guidance."""
    if not source:
        return ""
    return f"""## Source priority
When source document, idea, and research conflict, resolve in this order:
1. **User source document** — primary source of truth for facts, metrics, structure, and examples
2. **Presentation idea** — high-level direction, audience, scope exclusions
3. **DeepResearch report** — supporting background and citations

## User source document
{source.strip()}

"""


def build_outline_system_prompt(standards: str) -> str:
    return (
        "You are a presentation designer who turns research into structured PPT outlines "
        "with clear narrative flow.\n\n"
        "# RULES\n"
        "- Output ONLY valid markdown — no preamble, no code fences, no commentary.\n"
        "- Follow the outline standards below EXACTLY.\n"
        "- Prefer concrete examples, named tools, and specific numbers over vague abstractions.\n"
        "- Build narrative momentum: each slide flows naturally from the previous one.\n\n"
        "# CRITICAL QUALITY BARS\n"
        "These are the standards models most often violate — pay special attention:\n"
        "- Content slides: 5-6 `**Label:** explanation` bullets where each label is "
        "self-contained (makes sense without the slide title). End every content slide "
        "with an explicit takeaway (`Core insight:`, `Core logic:`, or `Anti-pattern:`).\n"
        "- `[Visual:]` must read as production-ready art direction — name the focal object, "
        "layout pattern (split-screen / grid / pipeline / roadmap / system diagram), "
        "foreground/background structure, and narrative device (contrast / sequence / "
        "hierarchy / cause-effect / before-after).\n"
        "- `[Speech:]` expands on bullets with context the audience needs to hear — "
        "never restate bullets verbatim. Aim for 60-90 seconds on content slides.\n\n"
        f"{standards}"
    )



def build_style_scaffold_prompt(
    idea: str,
    report: str,
    *,
    target_slides: list[int],
    source: str | None = None,
) -> str:
    counts = ", ".join(str(n) for n in target_slides)
    num_versions = len(target_slides)
    source_context = _build_source_context(source)

    return f"""Create a SHARED STYLE AND NARRATIVE SCAFFOLD for one presentation deck.

{num_versions} outline version(s) will be generated from this scaffold at **{counts} content slides** each.
All versions MUST share identical visual style and the same core narrative — longer versions only add slides; they never change the look or rename topics.

{source_context}## Presentation idea
{idea.strip()}

## DeepResearch report
{report.strip()}

## Output format (markdown only — no code fences)
Produce exactly these sections:

### Deck Title
One presentation title line (used as `# PPT Outline: [Title]` in every version).

### Narrative Spine
An ordered list of content-slide topics from most essential to optional depth.
Start with 1-3 hook topics that grab attention and frame the stakes (marked CORE — required in every version).
For each item include:
- **Topic:** short slide title seed
- **Priority:** CORE (required in the shortest version) or EXTENDED (added in longer versions only)
- **Visual hook:** one phrase describing the recurring layout/motif for this topic's `[Visual:]` tag

The shortest version ({min(target_slides)} slides) uses CORE topics only.
Longer versions add EXTENDED topics in spine order without reordering or renaming CORE slides.

### Section Map
Group the narrative spine into **3-6 sections** (acts). For each section give:
- **Section:** short section title
- **Roadmap label:** 2-3 word uppercase chip label (e.g. `01 / ESSENTIALS`)

Every outline version inserts one transition/roadmap slide before each section (3-6 transition slides total); NO transition before the hook or call to action — hook slides start immediately after the cover. All versions share the same section structure regardless of content-slide count.

### Shared Visual System
Deck-wide art direction every version must reuse:
- Cover and closing slide visual treatment — closing visually reconnects to the cover (same focal motif, rendered slightly larger to signal closure) and carries a clear take-home message
- Transition/roadmap visual pattern (MANDATORY): one consistent section-map composition reused on all 3-6 transition slides, highlighting only the current section and showing a `progress bar N/total` marker
- Diagram language (boxes, arrows, connectors, icons, glow rules)
- Recurring motifs (beams, nodes, panels, section color accents) that anchor deck identity across all slide types

### Appendix: Global Visual Requirements
The EXACT appendix block to copy verbatim into every outline version.
Text-only: Theme (colors + hex), Fonts (families + sizes/weights), optional Format (16:9, margins).
Do NOT put layout or diagram rules here — those belong in Shared Visual System and per-slide `[Visual:]` tags.
"""


def build_outline_user_prompt(
    idea: str,
    report: str,
    *,
    target_slides: int,
    source: str | None = None,
    style_scaffold: str | None = None,
) -> str:
    scaffold_block = ""
    if style_scaffold:
        scaffold_block = f"""
## SHARED STYLE SCAFFOLD (MANDATORY)
Copy the appendix from this scaffold **verbatim** into your output.
Reuse the same deck title, visual motifs, diagram language, and cover/closing treatments.
Shorter versions are strict subsets of longer ones: keep CORE spine topics with the same titles and visual hooks; add EXTENDED topics only when the slide budget allows.

{style_scaffold.strip()}

"""
    source_context = _build_source_context(source)
    opening = (
        "Turn the source material and research below"
        if source
        else "Turn the research below"
    )

    return f"""{opening} into a presentation outline.
{scaffold_block}
{source_context}## Presentation idea
{idea.strip()}

**Interpretation guidance** — the idea file may contain structured sections. Honor ALL constraints found:
- **Audience**: calibrate language complexity, examples, and assumed knowledge accordingly.
- **Hook**: open the content slides with the specified narrative.
- **Scope Exclusions**: do NOT create slides on excluded topics even if the research covers them.
- **Structure**: follow any distribution breakdown (e.g. "5 Cursor core + 3 OpenClaw").
- **References**: use listed images/files in appropriate `[Reference:]` and `[Visual:]` tags.

## Target slide count
Produce exactly **{target_slides} content slides** (teaching slides with substantive bullets and a clear takeaway).
This count excludes the cover slide, 3-6 transition/roadmap slides, and the closing slide — add those separately.

Expected total slide breakdown (in this order):
- 1 cover slide (opening title; premise immediately legible)
- 1-3 hook slides (immediately after cover — NO transition before hook)
- [transition slide → section body slides] × 3-6 sections (one `Roadmap:` slide before each section)
- optional 1 call-to-action slide (NO transition before it)
- 1 closing slide (take-home message; visually reconnects to cover)

## DeepResearch report
{report.strip()}

## Reminders
- Slide order: cover → hook (no transition) → [transition → section] × N → optional call to action (no transition) → closing
- Transition slides: title prefixed `Roadmap:`, `progress bar N/total` in `[Visual:]`, 2-4 bullets, 15-30s speech; one per section only
- Content `[Visual:]` tags: name the focal object, a layout pattern (split-screen / grid / pipeline / roadmap / diagram), and a narrative device (contrast / sequence / before-after / cause-effect)
- Content `[Speech:]` tags: 60-90 seconds; end each with a bridge sentence leading into the next slide
- Closing slide: include a clear take-home message — the single idea the audience should remember
- Reference style images in `[Visual:]` where appropriate: `style_base.png`, `style_cover.png`, `style_transition.png`, `style_content.png`
- Reflect facts, case studies, and citations from the research accurately — prefer specific numbers over vague claims
"""


def validate_outline(outline: str) -> OutlineValidation:
    """Warn on missing structural elements; do not hard-fail."""
    warnings: list[str] = []
    text = outline.strip()

    if not text.startswith("# PPT Outline:"):
        warnings.append("Outline should start with '# PPT Outline: [Title]'.")

    if "## Appendix" not in text and "Appendix: Global Visual Requirements" not in text:
        warnings.append("Outline is missing '## Appendix: Global Visual Requirements'.")

    slide_headers = list(SLIDE_HEADER_PATTERN.finditer(text))
    if not slide_headers:
        warnings.append("No '## Slide N:' headers found.")
        return OutlineValidation(warnings=warnings)

    for index, match in enumerate(slide_headers):
        start = match.start()
        end = slide_headers[index + 1].start() if index + 1 < len(slide_headers) else len(text)
        block = text[start:end]
        title = match.group(0)
        if "[Visual:" not in block:
            warnings.append(f"{title} missing [Visual:] tag.")
        if "[Speech:" not in block:
            warnings.append(f"{title} missing [Speech:] tag.")

    transition_count = count_transition_slides(text)
    if transition_count < MIN_TRANSITION_SLIDES or transition_count > MAX_TRANSITION_SLIDES:
        warnings.append(
            f"Outline has {transition_count} transition slide(s); expected "
            f"{MIN_TRANSITION_SLIDES}-{MAX_TRANSITION_SLIDES} "
            "(titles prefixed 'Roadmap:' with a 'progress bar N/total' marker)."
        )

    return OutlineValidation(warnings=warnings)


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


def _outline_prompts_for_targets(
    *,
    idea: str,
    report: str,
    target_slides: list[int],
    source: str | None = None,
    style_scaffold: str | None = None,
    standards_path: Path | None = None,
) -> tuple[str, list[tuple[int, str]]]:
    """Build shared system prompt and per-target user prompts."""
    standards = load_outline_standards(standards_path)
    system_prompt = build_outline_system_prompt(standards)
    user_prompts = [
        (
            count,
            build_outline_user_prompt(
                idea,
                report,
                target_slides=count,
                source=source,
                style_scaffold=style_scaffold,
            ),
        )
        for count in target_slides
    ]
    return system_prompt, user_prompts


async def write_style_scaffold(
    client: OpenRouterClient,
    *,
    idea: str,
    report: str,
    target_slides: list[int],
    source: str | None = None,
    text_model: str | None = None,
    standards_path: Path | None = None,
) -> str:
    """Generate a shared style and narrative scaffold for multiple outline lengths."""
    standards = load_outline_standards(standards_path)
    system_prompt = build_outline_system_prompt(standards)
    user_prompt = build_style_scaffold_prompt(
        idea,
        report,
        target_slides=target_slides,
        source=source,
    )
    raw = await client.complete_text(
        user_prompt,
        system_prompt,
        model=text_model,
    )
    return strip_code_fences(raw)


async def write_outline(
    client: OpenRouterClient,
    *,
    idea: str,
    report: str,
    source: str | None = None,
    target_slides: int = 16,
    text_model: str | None = None,
    standards_path: Path | None = None,
) -> tuple[str, OutlineValidation]:
    """Generate and validate a presentation outline from research."""
    system_prompt, user_prompts = _outline_prompts_for_targets(
        idea=idea,
        report=report,
        target_slides=[target_slides],
        source=source,
        standards_path=standards_path,
    )
    _, user_prompt = user_prompts[0]

    raw = await client.complete_text(
        user_prompt,
        system_prompt,
        model=text_model,
    )
    outline = strip_code_fences(raw)
    validation = validate_outline(outline)
    return outline, validation


async def write_outlines_parallel(
    client: OpenRouterClient,
    *,
    idea: str,
    report: str,
    target_slides: list[int],
    source: str | None = None,
    text_model: str | None = None,
    standards_path: Path | None = None,
) -> tuple[str, list[tuple[int, str, OutlineValidation]]]:
    """Generate outlines for multiple slide counts sharing one style scaffold."""
    style_scaffold = await write_style_scaffold(
        client,
        idea=idea,
        report=report,
        target_slides=target_slides,
        source=source,
        text_model=text_model,
        standards_path=standards_path,
    )
    system_prompt, user_prompts = _outline_prompts_for_targets(
        idea=idea,
        report=report,
        target_slides=target_slides,
        source=source,
        style_scaffold=style_scaffold,
        standards_path=standards_path,
    )
    results = await client.complete_text_parallel(
        [(user_prompt, system_prompt) for _, user_prompt in user_prompts],
        model=text_model,
        desc="Outlines",
    )

    outlines: list[tuple[int, str, OutlineValidation]] = []
    for (count, _), result in zip(user_prompts, results):
        if isinstance(result, Exception):
            raise RuntimeError(
                f"Outline generation failed for {count} slides: {result}"
            ) from result
        outline = strip_code_fences(result)
        outlines.append((count, outline, validate_outline(outline)))
    return style_scaffold, outlines
