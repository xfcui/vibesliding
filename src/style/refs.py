"""Generate deck style reference images during the outline workflow."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from src.core.api_client import (
    OpenRouterClient,
    STYLE_IMAGE_PIXEL_SIZE,
    STYLE_IMAGE_SIZE,
    VolcengineClient,
)
from src.core.export import build_contact_sheet, save_image, save_style_reference_image
from src.outline.parser import extract_global_style, parse_markdown

STYLE_BASE_FILENAME: Final[str] = "style_base.png"
STYLE_COVER_FILENAME: Final[str] = "style_cover.png"
STYLE_TRANSITION_FILENAME: Final[str] = "style_transition.png"
STYLE_CONTENT_FILENAME: Final[str] = "style_content.png"
STYLE_CANDIDATES_DIRNAME: Final[str] = "style_candidates"

# StyleSelectFn returns 1..count to pick a candidate, or 0 to regenerate the stage.
StyleSelectFn = Callable[[str, Path, int], int]

STYLE_SYSTEM_PROMPT: Final[str] = """You are an elite presentation designer creating a MASTER REFERENCE SLIDE.
Generate a pixel-perfect 1920×1080 (16:9) image that establishes a reusable visual system for an entire slide deck.

This is a master reference slide — it should look like a real, beautifully designed presentation slide that establishes:
- Background treatment (gradient direction, texture, ambient lighting)
- Spacing rhythm, safe margins, and layout grid
- Graphic language (line weight, icon style, diagram connectors, glow/shadow rules)
- One or two recurring motifs that anchor deck identity

# RULES
- Placeholder labels only (2–4 words per element) — no sentences, no paragraphs
- DO NOT render typography samples, font showcases, or color swatches with hex codes (these are defined in text elsewhere)
- Layout structure must be clear enough for downstream slides to replicate exactly
- Professional conference-keynote quality: high contrast, generous negative space, clean alignment
- NO watermarks, fake logos, AI-generation stamps, decorative unreadable code, or photorealistic human faces
- Every piece of rendered text must be short, correctly spelled, and fully legible

# REFERENCE IMAGE STRICT ADHERENCE
If a reference image is attached, you MUST strictly match its background, color palette, lighting, and core motifs. The generated slide must look like it belongs in the exact same deck as the reference image.
"""


@dataclass(frozen=True)
class StyleRefJob:
    """One style-reference image to generate."""

    filename: str
    label: str
    user_prompt: str
    use_base_reference: bool = False


def extract_presentation_title(outline: str, *, fallback: str) -> str:
    match = re.search(r"^#\s*PPT Outline:\s*(.+)$", outline, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback.strip()[:120] or "Presentation Title"


def extract_global_visual_requirements(outline: str) -> str | None:
    slides = parse_markdown(outline)
    return extract_global_style(slides)


def _visual_requirements_block(outline: str) -> str:
    """Appendix visual requirements."""
    appendix = extract_global_visual_requirements(outline)
    if appendix:
        return (
            "\n# GLOBAL VISUAL REQUIREMENTS\n"
            f"{appendix.strip()}\n"
        )
    return (
        "\n# GLOBAL VISUAL REQUIREMENTS\n"
        "Derive a cohesive professional palette and motif system "
        "from the presentation idea and topic.\n"
    )


def build_style_ref_jobs(
    *,
    idea: str,
    outline: str,
    presentation_title: str | None = None,
) -> list[StyleRefJob]:
    """Build prompts for base, cover, transition, and content style-reference slides."""
    title = presentation_title or extract_presentation_title(outline, fallback=idea)
    visual_requirements = _visual_requirements_block(outline)

    base_prompt = f"""CREATE STYLE REFERENCE: MASTER BACKGROUND & MOTIF PLATE
Presentation topic: "{title}"
Idea seed: {idea.strip()[:500]}
{visual_requirements}
Generate a clean, cohesive master background and motif plate on a single 1920×1080 canvas. This plate is the visual blueprint that defines the graphic language for the entire deck.

The image MUST demonstrate the core visual system without being divided into a grid of isolated rules. Instead, create a beautifully composed, unified slide background that includes:
- A clean background with ambient lighting and subtle texture.
- A subtle geometric motif (e.g., abstract beams, glowing nodes, or clean lines) that anchors the deck's identity.
- Generous negative space for future content.
- Elegant panel surfaces (rounded rectangular card/panel styles with thin borders and dark fills) floating in the composition.
- Glowing spots or flares in the accent colors.

# VISUAL STYLE & QUALITY
- Background: Deep near-black background with a subtle dark slate texture and ambient lighting.
- Palette: Strictly use the colors defined in the global visual requirements (teal, amber, violet, dark slate, warm white).
- Typography: All text labels must be short, uppercase, correctly spelled, and set in a clean, modern sans-serif font (like Inter or JetBrains Mono). No long sentences or paragraphs.
- Quality: Professional conference-keynote quality, high contrast, generous negative space, clean alignment, and sharp vector-like rendering.
- NO cover titles, NO roadmap chips, NO diagrams, NO bullet lists, NO slide-specific layout.
- This plate is the blank canvas all slide types inherit.
"""

    cover_prompt = f"""CREATE STYLE REFERENCE: CINEMATIC COVER / TITLE SLIDE
Presentation Title: "{title}"
Idea seed: {idea.strip()[:500]}
{visual_requirements}
Generate a cinematic, premium title-slide reference plate on a single 1920×1080 canvas. This plate defines the deck's opening impression and establishes the focal visual motif.

# LAYOUT & COMPOSITION
- Left-aligned typography in the upper-left or middle-left third of the screen.
- Large, bold main title: "{title}" (set in a clean, heavy sans-serif font like Inter Bold).
- Subtitle below the title: A short, compelling subtitle in a smaller, lighter font weight (cool gray or accent color).
- Presenter line at the bottom-left: "PROF. XUEFENG CUI | SHANDONG UNIVERSITY" in a small, clean, uppercase monospaced font.
- Right-aligned focal visual: A spectacular, abstract 3D-like geometric motif (e.g., a glowing concentric ring system, a radiating beam of particles, or a stylized network constellation) that represents "thought propagating into execution".
- The focal visual must have a strong, luminous accent glow (teal or violet) that contrasts beautifully against the dark background.

# VISUAL STYLE & CONTINUITY
- Background: Match the EXACT background treatment, lighting, and texture of the attached base plate reference image. Do not invent a new background.
- Palette: Strictly use the colors defined in the global visual requirements (teal, amber, violet, dark slate, warm white).
- Quality: Professional conference-keynote quality, generous negative space, clean alignment, and sharp vector-like rendering.
- NO bullet text, NO paragraphs, NO decorative unreadable code, NO photorealistic human faces.
"""

    transition_prompt = f"""CREATE STYLE REFERENCE: TRANSITION / ROADMAP SLIDE
Presentation: "{title}"
{visual_requirements}
Generate a section-divider and roadmap reference plate on a single 1920×1080 canvas. This plate defines the visual system for all section dividers and progress tracking in the deck.

# LAYOUT & COMPOSITION
- Upper section: Large, bold placeholder section title (e.g., "SECTION TITLE HERE") set in a clean sans-serif font, with a short one-sentence placeholder description below in cool gray.
- Middle/Lower section: A horizontal roadmap pipeline consisting of 3 to 5 rounded rectangular cards (roadmap chips) arranged in a clean, perfectly aligned row.
- Each roadmap chip must have a short, uppercase placeholder label (2–3 words max, e.g., "01 / ESSENTIALS", "02 / ADVANCED", "03 / AGENTS").
- Highlight exactly ONE chip (the current section) with a bright glowing border and a subtle background fill in the primary accent color (teal, amber, or violet).
- The other chips must be subdued (thin borders, low opacity, no glow) but still clearly readable.
- Progress indicator: A small, elegant progress marker (e.g., "ACT 1 OF 3" or a thin glowing progress bar, or "01 / 03") in the lower-right corner.

# VISUAL STYLE & CONTINUITY
- Background: Match the EXACT background treatment, lighting, and texture of the attached base plate reference image. Do not invent a new background.
- Palette: Strictly use the colors defined in the global visual requirements (teal, amber, violet, dark slate, warm white).
- Quality: Professional conference-keynote quality, high contrast, generous negative space, clean alignment, and sharp vector-like rendering.
- NO long sentences, NO dense text, NO background artwork competing with the roadmap chips.
"""

    content_prompt = f"""CREATE STYLE REFERENCE: CONTENT / TEACHING SLIDE
Presentation: "{title}"
{visual_requirements}
Generate a content-slide reference plate on a single 1920×1080 canvas. This plate defines the visual system and split-screen layout for all content, teaching, and diagram slides in the deck.

# LAYOUT & COMPOSITION
- Split-screen layout divided into two main columns with generous spacing:
  1. Primary Visual Area (55–65% width, left or right side): A beautifully designed, clear technical diagram, pipeline, or workflow.
     - The diagram must consist of rounded-rectangle nodes with thin borders, connected by directional arrows with glowing joints or soft arrowheads.
     - Each node and connector must have a short, uppercase, highly legible label.
     - The visual composition must carry the narrative, making the slide's core concept understandable before reading any text.
  2. Text Column (35–45% width, opposite side): A clean, well-spaced column of 4 to 5 short bullet points.
     - Each bullet must start with a bold label in the accent color (e.g., "**LABEL:** brief placeholder text").
     - Use generic placeholder text to emphasize the layout structure rather than specific content.

# VISUAL STYLE & CONTINUITY
- Background: Match the EXACT background treatment, lighting, and texture of the attached base plate reference image. Do not invent a new background.
- Palette: Strictly use the colors defined in the global visual requirements (teal, amber, violet, dark slate, warm white).
- Graphic Language: Use clean panel styles, consistent line weights, and elegant connector arrows that fit seamlessly with the base plate's aesthetic.
- Quality: Professional conference-keynote quality, high contrast, generous negative space, clean alignment, and sharp vector-like rendering.
"""

    return [
        StyleRefJob(STYLE_BASE_FILENAME, "base", base_prompt, use_base_reference=False),
        StyleRefJob(STYLE_COVER_FILENAME, "cover", cover_prompt, use_base_reference=True),
        StyleRefJob(
            STYLE_TRANSITION_FILENAME,
            "transition",
            transition_prompt,
            use_base_reference=True,
        ),
        StyleRefJob(STYLE_CONTENT_FILENAME, "content", content_prompt, use_base_reference=True),
    ]


def _default_select(_label: str, _choices_path: Path, _count: int) -> int:
    return 1


async def _generate_candidate_batch(
    client: OpenRouterClient | VolcengineClient,
    *,
    prompt: str,
    count: int,
    reference_images: list[bytes] | None,
) -> list[bytes]:
    if count < 1:
        raise ValueError("count must be >= 1")
    prompts = [
        (prompt, STYLE_SYSTEM_PROMPT, reference_images, None, None) for _ in range(count)
    ]
    results = await client.generate_images_parallel(
        prompts,
        desc="Style references",
        image_size=STYLE_IMAGE_SIZE,
    )
    images: list[bytes] = []
    for index, result in enumerate(results):
        if isinstance(result, Exception):
            raise RuntimeError(
                f"Style reference generation failed at candidate {index + 1}: {result}"
            ) from result
        images.append(result)
    return images


def _save_candidate_variants(
    images: list[bytes],
    *,
    prefix: str,
    candidates_dir: Path,
) -> list[Path]:
    paths: list[Path] = []
    for index, image_bytes in enumerate(images, start=1):
        path = candidates_dir / f"{prefix}_v{index:02d}.png"
        save_image(image_bytes, path)
        paths.append(path)
    return paths


def _select_from_candidates(
    label: str,
    images: list[bytes],
    *,
    choices_filename: str,
    candidates_dir: Path,
    select: StyleSelectFn,
    candidates: int,
) -> bytes | None:
    """Pick a candidate or request regeneration.

    Returns:
        Chosen image bytes, or None when select() returned 0 (regenerate).
    """
    sheet_title = f"{label.upper()} — pick 1-{candidates} (or regenerate)"
    choices_path = candidates_dir / choices_filename
    build_contact_sheet(images, choices_path, title=sheet_title)
    picked = select(label, choices_path, len(images))
    if picked == 0:
        return None
    if picked < 1 or picked > len(images):
        raise ValueError(
            f"Invalid pick for {label}: {picked} (expected 0 to regenerate, "
            f"or 1-{len(images)} to pick)"
        )
    return images[picked - 1]


async def _select_stage_with_regen(
    client: OpenRouterClient | VolcengineClient,
    *,
    job: StyleRefJob,
    prompt: str,
    candidates: int,
    reference_images: list[bytes] | None,
    candidates_dir: Path,
    select: StyleSelectFn,
) -> bytes:
    """Generate candidates for one stage, allowing regeneration until the user picks."""
    prefix = job.filename.removesuffix(".png")
    choices_filename = f"{prefix}_choices.png"

    while True:
        images = await _generate_candidate_batch(
            client,
            prompt=prompt,
            count=candidates,
            reference_images=reference_images,
        )
        _save_candidate_variants(
            images,
            prefix=prefix,
            candidates_dir=candidates_dir,
        )
        chosen = _select_from_candidates(
            job.label,
            images,
            choices_filename=choices_filename,
            candidates_dir=candidates_dir,
            select=select,
            candidates=candidates,
        )
        if chosen is not None:
            return chosen


async def generate_style_references(
    client: OpenRouterClient | VolcengineClient,
    *,
    idea: str,
    outline: str,
    output_dir: Path,
    candidates: int = 4,
    select: StyleSelectFn | None = None,
) -> list[Path]:
    """Generate base, cover, transition, and content style-reference PNGs in *output_dir*.

    Stage 1 generates *candidates* blank base plates; the user picks one (or regenerates).
    Stage 2 generates *candidates* each for cover, transition, and content using the
    chosen base as reference; the user picks one per type (or regenerates that stage).

    Returns the four canonical style reference paths (base, cover, transition, content).
    """
    if candidates < 1:
        raise ValueError("candidates must be >= 1")

    picker = select or _default_select
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir = output_dir / STYLE_CANDIDATES_DIRNAME
    candidates_dir.mkdir(parents=True, exist_ok=True)

    jobs = build_style_ref_jobs(idea=idea, outline=outline)
    base_job = jobs[0]
    content_jobs = jobs[1:]

    base_bytes = await _select_stage_with_regen(
        client,
        job=base_job,
        prompt=base_job.user_prompt,
        candidates=candidates,
        reference_images=None,
        candidates_dir=candidates_dir,
        select=picker,
    )
    save_image(base_bytes, candidates_dir / STYLE_BASE_FILENAME)
    base_path = output_dir / STYLE_BASE_FILENAME
    save_style_reference_image(
        base_bytes,
        base_path,
        target_size=STYLE_IMAGE_PIXEL_SIZE,
    )

    content_prompts: list[tuple[StyleRefJob, str]] = []
    for job in content_jobs:
        for _ in range(candidates):
            content_prompts.append((job, job.user_prompt))

    batch_results = await client.generate_images_parallel(
        [
            (prompt, STYLE_SYSTEM_PROMPT, [base_bytes], None, None)
            for _, prompt in content_prompts
        ],
        desc="Style references",
        image_size=STYLE_IMAGE_SIZE,
    )

    by_label: dict[str, list[bytes]] = {job.label: [] for job in content_jobs}
    cursor = 0
    for job in content_jobs:
        for _ in range(candidates):
            result = batch_results[cursor]
            cursor += 1
            if isinstance(result, Exception):
                raise RuntimeError(
                    f"Style reference generation failed for {job.label}: {result}"
                ) from result
            by_label[job.label].append(result)

    saved: list[Path] = [base_path]
    for job in content_jobs:
        prefix = job.filename.removesuffix(".png")
        images = by_label[job.label]
        _save_candidate_variants(
            images,
            prefix=prefix,
            candidates_dir=candidates_dir,
        )
        choices_filename = f"{prefix}_choices.png"

        while True:
            chosen = _select_from_candidates(
                job.label,
                images,
                choices_filename=choices_filename,
                candidates_dir=candidates_dir,
                select=picker,
                candidates=candidates,
            )
            if chosen is not None:
                break
            images = await _generate_candidate_batch(
                client,
                prompt=job.user_prompt,
                count=candidates,
                reference_images=[base_bytes],
            )
            _save_candidate_variants(
                images,
                prefix=prefix,
                candidates_dir=candidates_dir,
            )

        final_path = output_dir / job.filename
        save_style_reference_image(
            chosen,
            final_path,
            target_size=STYLE_IMAGE_PIXEL_SIZE,
        )
        saved.append(final_path)

    return saved
