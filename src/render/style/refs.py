"""Generate deck style reference images during the outline workflow."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

from src.core.api_client import (
    OpenRouterClient,
    STYLE_IMAGE_PIXEL_SIZE,
    STYLE_IMAGE_SIZE,
    VolcengineClient,
)
from src.core.export import build_contact_sheet, save_image, save_style_reference_image
from src.outline.parser import extract_global_style, parse_markdown
from src.outline.roles import SlideRole

STYLE_BASE_NONCONTENT_FILENAME: Final[str] = "style_base_noncontent.png"
STYLE_BASE_CONTENT_FILENAME: Final[str] = "style_base_content.png"
STYLE_COVER_FILENAME: Final[str] = "style_cover.png"
STYLE_TRANSITION_FILENAME: Final[str] = "style_transition.png"
STYLE_CONTENT_FILENAME: Final[str] = "style_content.png"
STYLE_CANDIDATES_DIRNAME: Final[str] = "style_candidates"

BaseRefKind = Literal["none", "noncontent", "content"]

# Preferred style plates per slide role (ordered). Ending reuses cover treatment.
STYLE_PATHS_BY_ROLE: Final[Mapping[SlideRole, tuple[str, ...]]] = {
    "cover": (STYLE_COVER_FILENAME, STYLE_BASE_NONCONTENT_FILENAME),
    "ending": (STYLE_COVER_FILENAME, STYLE_BASE_NONCONTENT_FILENAME),
    "transition": (STYLE_TRANSITION_FILENAME, STYLE_BASE_NONCONTENT_FILENAME),
    # Content stays on the light half of the two-tone system — do not attach
    # the dark non-content base, or the model may blend conflicting backgrounds.
    "content": (STYLE_CONTENT_FILENAME, STYLE_BASE_CONTENT_FILENAME),
}

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

# TWO-TONE DECK SYSTEM
This deck uses two complementary backgrounds that share one palette and motif language:
- Dark "curtain" plates for cover, transition/roadmap, and ending slides
- Light/white plates for content/teaching slides
Never collapse the deck into a single background tone.

# REFERENCE IMAGE STRICT ADHERENCE
If a reference image is attached:
- Always match its accent palette, graphic language, and core motifs so the slide belongs in the same deck.
- Match its background treatment ONLY when this prompt explicitly says to match the background.
- When this prompt requests the opposite tone (light vs dark), keep motif/palette continuity but use the requested background — do not copy the reference background.
"""


@dataclass(frozen=True)
class StyleRefJob:
    """One style-reference image to generate."""

    filename: str
    label: str
    user_prompt: str
    base_ref: BaseRefKind = "none"


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
        "from the presentation idea and topic. "
        "Enforce two-tone backgrounds: dark curtain for cover/transition/ending, "
        "white/light for content slides.\n"
    )


def select_style_paths_for_role(
    role: SlideRole,
    style_paths: list[Path],
) -> list[Path]:
    """Pick the style plates that match *role*; fall back to all paths if unnamed."""
    if not style_paths:
        return []
    by_name = {path.name.lower(): path for path in style_paths}
    preferred = STYLE_PATHS_BY_ROLE[role]
    selected = [by_name[name.lower()] for name in preferred if name.lower() in by_name]
    return selected or list(style_paths)


def build_style_ref_jobs(
    *,
    idea: str,
    outline: str,
    presentation_title: str | None = None,
) -> list[StyleRefJob]:
    """Build prompts for two-tone style plates: dark base, light base, cover, transition, content."""
    title = presentation_title or extract_presentation_title(outline, fallback=idea)
    visual_requirements = _visual_requirements_block(outline)
    idea_seed = idea.strip()[:500]

    dark_base_prompt = f"""CREATE STYLE REFERENCE: DARK CURTAIN BASE PLATE
Presentation topic: "{title}"
Idea seed: {idea_seed}
{visual_requirements}
Generate a clean, cohesive DARK master background and motif plate on a single 1920×1080 canvas.
This plate is the visual blueprint for NON-CONTENT slides (cover, transitions, ending) — the bold dark "curtain".

The image MUST demonstrate the core visual system without being divided into a grid of isolated rules. Instead, create a beautifully composed, unified slide background that includes:
- A deep near-black / dark slate background with ambient lighting and subtle texture.
- A subtle geometric motif (e.g., abstract beams, glowing nodes, or clean lines) that anchors the deck's identity.
- Generous negative space for future content.
- Elegant panel surfaces (rounded rectangular card/panel styles with thin borders and dark fills) floating in the composition.
- Glowing spots or flares in the accent colors.

# VISUAL STYLE & QUALITY
- Background: Deep near-black background with a subtle dark slate texture and ambient lighting. This is the DARK curtain tone.
- Palette: Strictly use the accent colors defined in the global visual requirements (keep accents luminous on dark).
- Typography: All text labels must be short, uppercase, correctly spelled, and set in a clean, modern sans-serif font. No long sentences or paragraphs.
- Quality: Professional conference-keynote quality, high contrast, generous negative space, clean alignment, and sharp vector-like rendering.
- NO cover titles, NO roadmap chips, NO diagrams, NO bullet lists, NO slide-specific layout.
- This plate is the blank dark canvas that cover, transition, and ending slides inherit.
"""

    light_base_prompt = f"""CREATE STYLE REFERENCE: LIGHT CONTENT BASE PLATE
Presentation topic: "{title}"
Idea seed: {idea_seed}
{visual_requirements}
Generate a clean, cohesive LIGHT master background and motif plate on a single 1920×1080 canvas.
This plate is the visual blueprint for CONTENT / teaching slides — maximum readability on white/light.

A dark-curtain base plate is attached as a motif/palette reference ONLY.
- Reuse the SAME accent colors, geometric motifs, panel language, and line weights from the attached dark plate.
- Do NOT copy the dark background. This plate must be the LIGHT half of the two-tone system.

The image MUST demonstrate the core visual system without being divided into a grid of isolated rules. Instead, create a beautifully composed, unified slide background that includes:
- A pure white or extremely light clean off-white background with subtle soft studio lighting.
- The same geometric motif language as the dark plate, adapted for light backgrounds (darker line weights / ink where needed for contrast).
- Generous negative space for future content.
- Elegant panel surfaces (rounded rectangular card/panel styles with thin borders and extremely light/subtle fills) floating in the composition.
- Soft accent flares that remain readable on white.

# VISUAL STYLE & QUALITY
- Background: Pure white (#FFFFFF) or extremely light clean off-white. This is the LIGHT teaching tone — opposite of the dark curtain.
- Palette: Same accent colors as the attached dark plate, tuned for contrast on white.
- Typography: Short uppercase labels in a clean modern sans-serif, dark navy/slate for high contrast on white.
- Quality: Professional conference-keynote quality, high contrast, generous negative space, clean alignment, and sharp vector-like rendering.
- NO cover titles, NO roadmap chips, NO diagrams, NO bullet lists, NO slide-specific layout.
- This plate is the blank light canvas that content slides inherit.
"""

    cover_prompt = f"""CREATE STYLE REFERENCE: CINEMATIC COVER / TITLE SLIDE
Presentation Title: "{title}"
Idea seed: {idea_seed}
{visual_requirements}
Generate a cinematic, premium title-slide reference plate on a single 1920×1080 canvas. This plate defines the deck's opening impression and establishes the focal visual motif.
This is a NON-CONTENT curtain slide — it MUST use the dark background.

# LAYOUT & COMPOSITION
- Left-aligned typography in the upper-left or middle-left third of the screen.
- Large, bold main title: "{title}" (set in a clean, heavy sans-serif font like Inter Bold).
- Subtitle below the title: A short, compelling subtitle in a smaller, lighter font weight (cool gray or accent color).
- Presenter line at the bottom-left: "PROF. XUEFENG CUI | SHANDONG UNIVERSITY" in a small, clean, uppercase monospaced font.
- Right-aligned focal visual: A spectacular, abstract 3D-like geometric motif (e.g., a glowing concentric ring system, a radiating beam of particles, or a stylized network constellation) that represents "thought propagating into execution".
- The focal visual must have a strong, luminous accent glow that contrasts beautifully against the dark background.

# VISUAL STYLE & CONTINUITY
- Background: Match the EXACT dark background treatment, lighting, and texture of the attached dark base plate. Do not invent a new background. Do not use a white/light background.
- Palette: Strictly use the colors defined in the global visual requirements, matching the dark base plate accents.
- Quality: Professional conference-keynote quality, generous negative space, clean alignment, and sharp vector-like rendering.
- NO bullet text, NO paragraphs, NO decorative unreadable code, NO photorealistic human faces.
"""

    transition_prompt = f"""CREATE STYLE REFERENCE: TRANSITION / ROADMAP SLIDE
Presentation: "{title}"
{visual_requirements}
Generate a section-divider and roadmap reference plate on a single 1920×1080 canvas. This plate defines the visual system for all section dividers and progress tracking in the deck.
This is a NON-CONTENT curtain slide — it MUST use the dark background.

# LAYOUT & COMPOSITION
- Upper section: Large, bold placeholder section title (e.g., "SECTION TITLE HERE") set in a clean sans-serif font, with a short one-sentence placeholder description below in cool gray.
- Middle/Lower section: A horizontal roadmap pipeline consisting of 3 to 5 rounded rectangular cards (roadmap chips) arranged in a clean, perfectly aligned row.
- Each roadmap chip must have a short, uppercase placeholder label (2–3 words max, e.g., "01 / ESSENTIALS", "02 / ADVANCED", "03 / AGENTS").
- Highlight exactly ONE chip (the current section) with a bright glowing border and a subtle background fill in the primary accent color.
- The other chips must be subdued (thin borders, low opacity, no glow) but still clearly readable.
- Progress indicator: A small, elegant progress marker (e.g., "ACT 1 OF 3" or a thin glowing progress bar, or "01 / 03") in the lower-right corner.

# VISUAL STYLE & CONTINUITY
- Background: Match the EXACT dark background treatment, lighting, and texture of the attached dark base plate. Do not invent a new background. Do not use a white/light background.
- Palette: Strictly use the colors defined in the global visual requirements, matching the dark base plate accents.
- Quality: Professional conference-keynote quality, high contrast, generous negative space, clean alignment, and sharp vector-like rendering.
- NO long sentences, NO dense text, NO background artwork competing with the roadmap chips.
"""

    content_prompt = f"""CREATE STYLE REFERENCE: CONTENT / TEACHING SLIDE
Presentation: "{title}"
{visual_requirements}
Generate a content-slide reference plate on a single 1920×1080 canvas. This plate defines the visual system and split-screen layout for all content, teaching, and diagram slides in the deck.
This is a CONTENT teaching slide — it MUST use the white/light background (not the dark curtain).

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
- Background: Match the EXACT pure white / light background treatment, lighting, and texture of the attached light base plate. Do not invent a new background. Do not use a dark curtain background.
- Palette: Strictly use the colors defined in the global visual requirements, matching the light base plate accents.
- Graphic Language: Use clean panel styles, consistent line weights, and elegant connector arrows that fit seamlessly with the light base plate's aesthetic.
- Quality: Professional conference-keynote quality, high contrast, generous negative space, clean alignment, and sharp vector-like rendering.
"""

    return [
        StyleRefJob(
            STYLE_BASE_NONCONTENT_FILENAME,
            "base_noncontent",
            dark_base_prompt,
            base_ref="none",
        ),
        StyleRefJob(
            STYLE_BASE_CONTENT_FILENAME,
            "base_content",
            light_base_prompt,
            base_ref="noncontent",
        ),
        StyleRefJob(
            STYLE_COVER_FILENAME,
            "cover",
            cover_prompt,
            base_ref="noncontent",
        ),
        StyleRefJob(
            STYLE_TRANSITION_FILENAME,
            "transition",
            transition_prompt,
            base_ref="noncontent",
        ),
        StyleRefJob(
            STYLE_CONTENT_FILENAME,
            "content",
            content_prompt,
            base_ref="content",
        ),
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


def _reference_bytes_for_job(
    job: StyleRefJob,
    *,
    noncontent_base: bytes | None,
    content_base: bytes | None,
) -> list[bytes] | None:
    if job.base_ref == "none":
        return None
    if job.base_ref == "noncontent":
        if noncontent_base is None:
            raise RuntimeError(
                f"Non-content base required before generating {job.label}"
            )
        return [noncontent_base]
    if job.base_ref == "content":
        if content_base is None:
            raise RuntimeError(f"Content base required before generating {job.label}")
        return [content_base]
    raise ValueError(f"Unknown base_ref: {job.base_ref!r}")


async def generate_style_references(
    client: OpenRouterClient | VolcengineClient,
    *,
    idea: str,
    outline: str,
    output_dir: Path,
    candidates: int = 4,
    select: StyleSelectFn | None = None,
) -> list[Path]:
    """Generate two-tone style-reference PNGs in *output_dir*.

    Stages:
    1. Non-content (dark curtain) base (`style_base_noncontent.png`)
    2. Content (light) base (`style_base_content.png`), motif-linked to the non-content base
    3. Cover + transition (non-content base) and content plate (content base) in parallel;
       user picks (or regenerates) each plate

    Returns the five canonical style reference paths.
    """
    if candidates < 1:
        raise ValueError("candidates must be >= 1")

    picker = select or _default_select
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir = output_dir / STYLE_CANDIDATES_DIRNAME
    candidates_dir.mkdir(parents=True, exist_ok=True)

    jobs = build_style_ref_jobs(idea=idea, outline=outline)
    noncontent_job = jobs[0]
    content_base_job = jobs[1]
    plate_jobs = jobs[2:]

    noncontent_bytes = await _select_stage_with_regen(
        client,
        job=noncontent_job,
        prompt=noncontent_job.user_prompt,
        candidates=candidates,
        reference_images=None,
        candidates_dir=candidates_dir,
        select=picker,
    )
    save_image(noncontent_bytes, candidates_dir / STYLE_BASE_NONCONTENT_FILENAME)
    noncontent_path = output_dir / STYLE_BASE_NONCONTENT_FILENAME
    save_style_reference_image(
        noncontent_bytes,
        noncontent_path,
        target_size=STYLE_IMAGE_PIXEL_SIZE,
    )

    content_base_bytes = await _select_stage_with_regen(
        client,
        job=content_base_job,
        prompt=content_base_job.user_prompt,
        candidates=candidates,
        reference_images=[noncontent_bytes],
        candidates_dir=candidates_dir,
        select=picker,
    )
    save_image(content_base_bytes, candidates_dir / STYLE_BASE_CONTENT_FILENAME)
    content_base_path = output_dir / STYLE_BASE_CONTENT_FILENAME
    save_style_reference_image(
        content_base_bytes,
        content_base_path,
        target_size=STYLE_IMAGE_PIXEL_SIZE,
    )

    plate_prompts: list[tuple[StyleRefJob, str]] = []
    for job in plate_jobs:
        for _ in range(candidates):
            plate_prompts.append((job, job.user_prompt))

    batch_results = await client.generate_images_parallel(
        [
            (
                prompt,
                STYLE_SYSTEM_PROMPT,
                _reference_bytes_for_job(
                    job,
                    noncontent_base=noncontent_bytes,
                    content_base=content_base_bytes,
                ),
                None,
                None,
            )
            for job, prompt in plate_prompts
        ],
        desc="Style references",
        image_size=STYLE_IMAGE_SIZE,
    )

    by_label: dict[str, list[bytes]] = {job.label: [] for job in plate_jobs}
    cursor = 0
    for job in plate_jobs:
        for _ in range(candidates):
            result = batch_results[cursor]
            cursor += 1
            if isinstance(result, Exception):
                raise RuntimeError(
                    f"Style reference generation failed for {job.label}: {result}"
                ) from result
            by_label[job.label].append(result)

    saved: list[Path] = [noncontent_path, content_base_path]
    for job in plate_jobs:
        prefix = job.filename.removesuffix(".png")
        images = by_label[job.label]
        _save_candidate_variants(
            images,
            prefix=prefix,
            candidates_dir=candidates_dir,
        )
        choices_filename = f"{prefix}_choices.png"
        ref_images = _reference_bytes_for_job(
            job,
            noncontent_base=noncontent_bytes,
            content_base=content_base_bytes,
        )

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
                reference_images=ref_images,
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
