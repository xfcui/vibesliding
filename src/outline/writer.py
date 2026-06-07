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


def build_outline_system_prompt(standards: str) -> str:
    return (
        "You are a presentation designer who turns research into structured PPT outlines "
        "with clear narrative flow.\n\n"
        "# OUTPUT FORMAT\n"
        "- Output ONLY valid markdown — no preamble, no code fences, no commentary.\n"
        "- Follow the outline standards below EXACTLY for structure, headers, and required tags.\n\n"
        "# QUALITY RULES\n"
        "- Every bullet must be self-contained (readable without the slide title) and use the "
        "**Label:** explanation pattern.\n"
        "- Prefer concrete examples, named tools, and specific numbers over vague abstractions.\n"
        "- Build narrative momentum: each slide flows naturally from the previous one.\n"
        "- Visual tags describe composition, layout, focal elements, and narrative — never decorative filler.\n"
        "- Speech tags expand on bullets with context and transitions — never repeat bullet text verbatim.\n\n"
        "# APPENDIX BOUNDARY\n"
        "The Appendix contains ONLY text-describable styles: color palette with hex codes, "
        "font families with sizes/weights, and optional format constants (aspect ratio, margins). "
        "Layout, diagram language, icon treatment, and motifs belong exclusively in each slide's "
        "[Visual:] tag — never duplicated in the Appendix.\n\n"
        f"{standards}"
    )



def build_style_scaffold_prompt(
    idea: str,
    report: str,
    *,
    target_slides: list[int],
) -> str:
    counts = ", ".join(str(n) for n in target_slides)
    num_versions = len(target_slides)
    return f"""Create a SHARED STYLE AND NARRATIVE SCAFFOLD for one presentation deck.

{num_versions} outline version(s) will be generated from this scaffold at **{counts} content slides** each.
All versions MUST share identical visual style and the same core narrative — longer versions only add slides; they never change the look or rename topics.

## Presentation idea
{idea.strip()}

## DeepResearch report
{report.strip()}

## Output format (markdown only — no code fences)
Produce exactly these sections:

### Deck Title
One presentation title line (used as `# PPT Outline: [Title]` in every version).

### Narrative Spine
An ordered list of content-slide topics from most essential to optional depth.
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

Every outline version inserts one transition/roadmap slide before each section (3-6 transition slides total), so all versions share the same section structure regardless of content-slide count.

### Shared Visual System
Deck-wide art direction every version must reuse:
- Cover and closing slide visual treatment
- Transition/roadmap visual pattern (MANDATORY): one consistent section-map composition reused on all 3-6 transition slides, highlighting only the current section and showing a `progress bar N/total` marker
- Diagram language (boxes, arrows, connectors, icons, glow rules)
- Recurring motifs and section color accents

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
    return f"""Turn the research below into a presentation outline.
{scaffold_block}

## Presentation idea
{idea.strip()}

**Interpretation guidance** — the idea file may contain structured sections. Honor ALL constraints found:
- **Audience**: calibrate language complexity, examples, and assumed knowledge accordingly.
- **Hook**: open the content slides with the specified narrative.
- **Scope Exclusions**: do NOT create slides on excluded topics even if the research covers them.
- **Structure**: follow any distribution breakdown (e.g. "5 Cursor core + 3 OpenClaw").
- **References**: use listed images/files in appropriate `[Reference:]` and `[Visual:]` tags.

## Target slide count
Produce exactly **{target_slides} content slides** — teaching slides with substantive bullets and a clear takeaway.

This count is **only** content slides. It does **not** include:
- Cover/title slide (always add one)
- Transition/roadmap/section-divider slides (always add **3-6** of them — see below)
- Closing/Q&A/thank-you slide (always add one)

Add the cover, closing, and 3-6 transition slides in addition to the {target_slides} content slides.

## Transition slides (MANDATORY: 3-6)
Segment the deck into 3-6 sections, placing one transition slide before each section so the content never reads as one undifferentiated run.
- Prefix every transition slide title with `Roadmap:` (e.g. `## Slide 6: Roadmap: From Editor to Agent`).
- Give each transition slide a `[Visual:]` tag that repeats the same roadmap/section-map composition, highlights only the current section, and includes a `progress bar N/total` marker (N = this slide's number, total = total slide count).
- Keep transition bullets short (2-4 lines) — they orient the audience, they do not teach.
- Use shorter `[Speech:]` (15-30 s) on transition slides.

## DeepResearch report
{report.strip()}

## Requirements
**Structure:**
- Start with `# PPT Outline: [Title]`
- Separate the title, every slide, and appendix with `---`
- Use sequential `## Slide N: [Title]` headers (cover = Slide 1, content starts at Slide 2)
- Insert 3-6 transition slides (titles prefixed `Roadmap:`) that divide the deck into sections
- Every slide ends with exactly one `[Visual: ...]` tag and one `[Speech: ...]` tag
- End with `## Appendix: Global Visual Requirements`

**Content quality:**
- Each content slide needs an explicit takeaway bullet: `Core insight:`, `Core logic:`, or `Anti-pattern:`
- Prefer concrete over abstract — name specific tools, cite numbers, reference real examples from the research
- If the report references facts or case studies, reflect them accurately in bullets and speech

**Visual tags:**
- Specify composition (layout pattern, focal object, foreground/background structure), not mood words
- Style reference images (`style_base.png`, `style_cover.png`, `style_transition.png`, `style_story.png`) are generated alongside the outline; reference them in `[Visual:]` / `[Reference:]` tags where appropriate

**Speech tags:**
- Conversational tone, 60–90 s delivery per content slide
- Add context and transitions the bullets don't show; never repeat bullet text verbatim
- End each speech with a bridge sentence leading into the next slide's topic

**Appendix:**
- Text-only: Theme (colors + hex), Fonts (families + sizes), optional Format (16:9, margins)
- Layout, diagrams, icons, and motifs belong in `[Visual:]` tags — never in the Appendix
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
    target_slides: int = 16,
    text_model: str | None = None,
    standards_path: Path | None = None,
) -> tuple[str, OutlineValidation]:
    """Generate and validate a presentation outline from research."""
    system_prompt, user_prompts = _outline_prompts_for_targets(
        idea=idea,
        report=report,
        target_slides=[target_slides],
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
    text_model: str | None = None,
    standards_path: Path | None = None,
) -> tuple[str, list[tuple[int, str, OutlineValidation]]]:
    """Generate outlines for multiple slide counts sharing one style scaffold."""
    style_scaffold = await write_style_scaffold(
        client,
        idea=idea,
        report=report,
        target_slides=target_slides,
        text_model=text_model,
        standards_path=standards_path,
    )
    system_prompt, user_prompts = _outline_prompts_for_targets(
        idea=idea,
        report=report,
        target_slides=target_slides,
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
