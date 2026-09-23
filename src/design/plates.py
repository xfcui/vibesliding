"""Generate deck style plates from a script and a design brief."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

from src.core.api_client import (
    ImagePrompt,
    OpenRouterClient,
    STYLE_IMAGE_PIXEL_SIZE,
    STYLE_IMAGE_SIZE,
    VolcengineClient,
)
from src.core.export import build_contact_sheet, save_image, save_style_reference_image
from src.core.parser import extract_global_style, parse_markdown
from src.core.roles import SlideRole
from src.core.validate import CJK_CHAR_PATTERN

STYLE_BASE_NONCONTENT_FILENAME: Final[str] = "style_base_noncontent.png"
STYLE_BASE_CONTENT_FILENAME: Final[str] = "style_base_content.png"
STYLE_COVER_FILENAME: Final[str] = "style_cover.png"
STYLE_TRANSITION_FILENAME: Final[str] = "style_transition.png"
STYLE_CONTENT_FILENAME: Final[str] = "style_content.png"
STYLE_CANDIDATES_DIRNAME: Final[str] = "style_candidates"
STYLE_PROMPT_SUFFIX: Final[str] = "_prompt.txt"


def install_style_candidate(candidate: Path, plate: Path) -> Path:
    """Install a chosen candidate as a style plate, downscaling when larger than 1280×720."""
    save_style_reference_image(
        candidate.read_bytes(),
        plate,
        target_size=STYLE_IMAGE_PIXEL_SIZE,
    )
    return plate

BaseRefKind = Literal["none", "noncontent", "content"]

BRIEF_FIELD_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[-*]\s+\*\*(.+?):\*\*\s*(.+)$"
)
HEX_PATTERN: Final[re.Pattern[str]] = re.compile(r"#[0-9A-Fa-f]{6}")
COVER_TITLE_SEPARATORS: Final[tuple[str, ...]] = (" — ", " – ", " - ", ": ")

DEFAULT_DARK: Final[str] = "#101418"
DEFAULT_LIGHT: Final[str] = "#F7F8FA"
DEFAULT_ACCENT: Final[str] = "#2563EB"
DEFAULT_INK: Final[str] = "#101418"
DEFAULT_MUTED: Final[str] = "#5B6470"

SPELLING_RULES: Final[str] = """# SPELL EXACTLY
Render ONLY the words listed under ON-SLIDE TEXT in this brief. Copy each word letter-for-letter.
Put a visible space between every word. Never merge words. Never invent taglines or extra labels.
Last-letter doubling is the usual failure — never add a second copy of the final letter.
If a word is not in the list, do not draw it.
"""

STYLE_PATHS_BY_ROLE: Final[Mapping[SlideRole, tuple[str, ...]]] = {
    "cover": (STYLE_COVER_FILENAME, STYLE_BASE_NONCONTENT_FILENAME),
    "ending": (STYLE_COVER_FILENAME, STYLE_BASE_NONCONTENT_FILENAME),
    "transition": (STYLE_TRANSITION_FILENAME, STYLE_BASE_NONCONTENT_FILENAME),
    "content": (STYLE_CONTENT_FILENAME, STYLE_BASE_CONTENT_FILENAME),
}

StyleSelectFn = Callable[[str, Path, int], int]


def style_system_prompt(style: "DeckStyle") -> str:
    return f"""You are a brand designer at a top studio producing the MASTER STYLE PLATE for a
conference keynote deck. Generate one 1920×1080 (16:9) slide image that defines the deck's reusable visual
system: background tone, typographic hierarchy, layout grid, deck furniture, and one signature motif.

# RESTRAINED BUT PREMIUM
- Uncluttered, editorial, expensive-looking. Clean geometry and disciplined alignment, never busy.
- Exactly ONE signature motif, specified in the plate brief below, deliberately composed and echoed once at
  small scale. No incidental decoration scattered around.
- Depth comes from craft, not effects: hairline borders, 1–2 px accent rules, 3–6 % panel tints, and at most
  a very subtle tonal falloff in the background. No noise, no grain, no heavy glows, no 3D renders, no photos.
- The plate must look deliberately designed and finished — never like an empty, unstyled template.

# TYPOGRAPHIC HIERARCHY (the main source of polish)
- Eyebrow / kicker: very small uppercase or short label, wide letterspacing, accent color.
- Title: large, heavy, tight-tracked sans-serif with clear optical alignment to the left margin.
- Support line: lighter weight, cool gray, noticeably smaller than the title.
- Micro-labels and numerals: small type for chips, indices, and progress markers.
- Establish real size contrast between these levels; everything sits on a shared grid and baseline.

# DECK FURNITURE
Include the quiet details a designed deck has: a consistent left margin shared by every zone, a thin rule or
corner mark that frames the composition, and small footer type (deck name, slide number) where requested.

# TWO-TONE DECK SYSTEM
Each plate uses exactly one background tone, set in its CONSTRAINTS. Never mix both tones in one plate.

# RULES
- Short placeholder labels only — no sentences, no paragraphs, no lorem ipsum.
- No typography specimens, font showcases, or color swatches with hex codes.
- Correct spelling, high contrast, crisp vector-quality edges, everything inside the safe margin from
  GLOBAL VISUAL REQUIREMENTS (5 % when it names none).
- NO watermarks, fake logos, AI-generation stamps, or photorealistic human faces.
- On-slide language: {style.language}. Copy the supplied words exactly. Do not translate them.

# TOPIC FAMILY
{style.topic_family}
Mood: {style.mood}
Never depict: {style.avoid}

# REFERENCE IMAGE
If a reference plate is attached, reuse its accent colors, type hierarchy, line weights, and signature motif so
the plates belong to one deck — but use the background tone THIS prompt asks for, even when it is the opposite
of the reference.
"""


@dataclass
class DeckStyle:
    """Deck-specific facts that fill the five style-plate prompts."""

    title: str
    display_title: str
    appendix: str
    topic_family: str
    mood: str
    motif: str
    avoid: str
    language: str
    footer: str
    cover_eyebrow: str
    cover_title: str
    cover_support: str
    content_eyebrow: str
    content_title: str
    content_stages: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    dark_bg: str = DEFAULT_DARK
    light_bg: str = DEFAULT_LIGHT
    accent: str = DEFAULT_ACCENT
    ink: str = DEFAULT_INK
    muted: str = DEFAULT_MUTED

    @classmethod
    def from_files(cls, script: str, design_brief: str) -> "DeckStyle":
        title = extract_presentation_title(script, fallback="Presentation")
        display = cover_display_title(title, fallback=title or "Presentation")
        appendix = extract_global_visual_requirements(script) or ""
        fields = _brief_fields(design_brief)
        sections = _section_labels(script)
        stages = _split_labels(fields.get("content stages", ""))
        language = (fields.get("language") or _guess_language(script)).strip() or "en"
        footer = fields.get("footer") or _footer_from_title(display)
        return cls(
            title=title,
            display_title=display,
            appendix=appendix,
            topic_family=fields.get("topic family") or title,
            mood=fields.get("mood") or "restrained editorial lecture",
            motif=fields.get("signature motif") or "one small geometric mark tied to the topic",
            avoid=fields.get("avoid") or "fake logos, watermarks, photorealistic faces, clip-art",
            language=language,
            footer=footer,
            cover_eyebrow=fields.get("cover eyebrow") or ("讲座" if language.startswith("zh") else "LECTURE"),
            cover_title=fields.get("cover title") or display,
            cover_support=fields.get("cover support") or (
                "讲清楚。再验证。" if language.startswith("zh") else "MAKE IT CLEAR."
            ),
            content_eyebrow=fields.get("content eyebrow") or ("证据" if language.startswith("zh") else "EVIDENCE"),
            content_title=fields.get("content title") or (
                "核验" if language.startswith("zh") else "CHECK THE CLAIM"
            ),
            content_stages=stages or (["一看", "一比", "一证"] if language.startswith("zh") else ["LOOK", "COMPARE", "CHECK"]),
            sections=sections or ["SECTION"],
            dark_bg=_hex_near(appendix, ("dark", "curtain", "navy"), DEFAULT_DARK),
            light_bg=_hex_near(appendix, ("light", "white", "content"), DEFAULT_LIGHT),
            accent=_hex_near(appendix, ("accent", "primary"), DEFAULT_ACCENT),
            ink=_hex_near(appendix, ("ink", "text"), DEFAULT_INK),
            muted=_hex_near(appendix, ("muted", "slate", "gray", "grey"), DEFAULT_MUTED),
        )


@dataclass
class StyleRefJob:
    """One style-reference image to generate."""

    filename: str
    label: str
    user_prompt: str
    base_ref: BaseRefKind = "none"
    system_prompt: str = ""


def extract_presentation_title(outline: str, *, fallback: str) -> str:
    match = re.search(r"^#\s*PPT Outline:\s*(.+)$", outline, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback.strip()[:120] or "Presentation Title"


def cover_display_title(title: str, *, fallback: str = "Presentation") -> str:
    """First clause of *title* — short enough to typeset on a cover plate."""
    text = title.strip()
    if not text:
        return fallback
    for sep in COVER_TITLE_SEPARATORS:
        if sep in text:
            text = text.split(sep, 1)[0].strip()
            break
    return text or fallback


def extract_global_visual_requirements(outline: str) -> str | None:
    slides = parse_markdown(outline)
    return extract_global_style(slides)


def _brief_fields(design_brief: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in design_brief.splitlines():
        match = BRIEF_FIELD_PATTERN.match(line.strip())
        if match:
            fields[match.group(1).strip().lower()] = match.group(2).strip()
    return fields


def _split_labels(raw: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,，、]", raw) if part.strip()]


def _chip_label(title: str) -> str:
    text = title.strip()
    if CJK_CHAR_PATTERN.search(text):
        return text[:8]
    words = text.split()
    return " ".join(words[:2]).upper()[:18] or "SECTION"


def _section_labels(script: str) -> list[str]:
    labels: list[str] = []
    for slide in parse_markdown(script):
        if slide.title.lower().startswith("roadmap:"):
            label = slide.title.split(":", 1)[1].strip()
            labels.append(_chip_label(label))
    return labels


def _guess_language(script: str) -> str:
    sample = script[:1500]
    cjk = len(CJK_CHAR_PATTERN.findall(sample))
    return "zh" if cjk >= 8 else "en"


def _footer_from_title(title: str) -> str:
    text = title.strip()
    if not text:
        return "DECK"
    if CJK_CHAR_PATTERN.search(text):
        return text[:4]
    return text.split()[0][:12]


def _hex_near(appendix: str, needles: tuple[str, ...], default: str) -> str:
    for line in appendix.splitlines():
        lower = line.lower()
        if any(needle in lower for needle in needles):
            found = HEX_PATTERN.search(line)
            if found:
                return found.group(0)
    return default


def _visual_requirements_block(style: DeckStyle) -> str:
    if style.appendix.strip():
        return f"\n# GLOBAL VISUAL REQUIREMENTS\n{style.appendix.strip()}\n"
    return (
        "\n# GLOBAL VISUAL REQUIREMENTS\n"
        f"Two-tone lecture. Content slides: {style.light_bg}. "
        f"Non-content slides: {style.dark_bg}. Accent {style.accent}. "
        f"Ink {style.ink}. Muted {style.muted}. Motif: {style.motif}.\n"
    )


def _motif_block(style: DeckStyle) -> str:
    return (
        "# SIGNATURE MOTIF\n"
        f"{style.motif}\n"
        f"Never: {style.avoid}\n"
        "Keep the mark small on teaching plates and large only on the cover.\n"
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


def build_style_ref_jobs(style: DeckStyle) -> list[StyleRefJob]:
    """Build prompts for two-tone style plates from *style*."""
    system = style_system_prompt(style)
    visual = _visual_requirements_block(style)
    motif = _motif_block(style)
    sections = style.sections
    chips = "    ".join(f"{index:02d} {label}" for index, label in enumerate(sections, start=1))
    highlight = 2 if len(sections) >= 2 else 1
    progress = f"{highlight:02d} / {len(sections):02d}"
    stages = "    ".join(style.content_stages)
    stage_count = len(style.content_stages)
    topic = f'Presentation topic (context only, do not typeset): "{style.title}"'

    dark = f"""CREATE STYLE PLATE: DARK CURTAIN BASE (non-content slides)
{topic}
{visual}
{SPELLING_RULES}
Design the DARK master plate on a single 1920×1080 canvas. It is the structural curtain inherited by the
cover, roadmap transitions, and ending.

# ON-SLIDE TEXT (render these words only, spelled exactly)
- Eyebrow: {style.cover_eyebrow}
- Title: {style.display_title}
- Footer left: {style.footer}

# COMPOSITION
- Flat, quiet field. Shared left margin. Small motif beside the eyebrow.
- Heavy title in a light color. One 2 px accent rule in {style.accent}.
- Central working zone: one low-contrast panel. Generous negative space.
- Footer baseline with {style.footer} left. No slide number: cover, roadmap, and ending slides never show one.
{motif}
# CONSTRAINTS
- Dark background only: {style.dark_bg}.
- NO hero diagram, roadmap chips, bullet text, logos, or extra words.
"""

    light = f"""CREATE STYLE PLATE: LIGHT CONTENT BASE (content slides)
{topic}
{visual}
{SPELLING_RULES}
Design the LIGHT master plate on one 1920×1080 canvas. It is the flexible base beneath teaching slides.

The attached dark curtain plate is a palette, type, line-weight, and motif reference ONLY.
Do not copy its dark background. Build the light half of the same deck.

# ON-SLIDE TEXT (render these words only, spelled exactly)
- Eyebrow: {style.content_eyebrow}
- Title: {style.content_title}
- Footer left: {style.footer}
- Footer right: 01

# COMPOSITION
- Same left margin and header baseline as the dark plate.
- Near-black {style.ink} title, short accent rule in {style.accent}.
- Leave most of the canvas as an adaptable content grid. No permanent illustration column.
- Footer {style.footer} left and monospaced 01 right in {style.muted}.
{motif}
# CONSTRAINTS
- Light background only: {style.light_bg}. No dark curtain.
- NO roadmap chips, diagrams, bullet text, logos, or extra words.
"""

    cover = f"""CREATE STYLE PLATE: COVER / TITLE SLIDE (non-content)
{topic}
{visual}
{SPELLING_RULES}
Design a bold lecture cover on one 1920×1080 canvas.

# ON-SLIDE TEXT (render these words only, spelled exactly)
- Eyebrow: {style.cover_eyebrow}
- Title: {style.cover_title}
- Support: {style.cover_support}

# COMPOSITION
- Match the dark base margins, line weights, and type.
- Left side: eyebrow, then the title in huge heavy type, then the support line in {style.muted}.
- Right side: one large signature motif. Keep breathing room around it. No footer and no slide number.
{motif}
# CONSTRAINTS
- Dark background only: {style.dark_bg}.
- No bullets, paragraphs, photos, faces, roadmap chips, logos, or extra text.
"""

    transition = f"""CREATE STYLE PLATE: TRANSITION / ROADMAP SLIDE (non-content)
{topic}
{visual}
{SPELLING_RULES}
Design the reusable roadmap on one 1920×1080 canvas. Every transition slide reuses this composition
and changes only the highlighted section.

# ON-SLIDE TEXT (render these words only, spelled exactly)
- Eyebrow: {style.cover_eyebrow}
- Title: {style.display_title}
- Chips: {chips}
- Progress: {progress}
- Footer left: {style.footer}

# COMPOSITION
- Match the dark base margins and footer.
- Middle band: one horizontal row of {len(sections)} compact roadmap chips. Highlight chip {highlight:02d}.
- Lower area: empty headline zone for the generated roadmap title.
- Bottom: a segmented progress rule and monospaced {progress}.
{motif}
# CONSTRAINTS
- Dark background only: {style.dark_bg}. Roadmap chips lead; the motif stays secondary.
- No diagrams, bullet lists, photos, or extra words.
"""

    content = f"""CREATE STYLE PLATE: CONTENT / TEACHING SLIDE
{topic}
{visual}
{SPELLING_RULES}
Design a representative teaching slide on one 1920×1080 canvas. Show a flexible grammar for a short
sequence, not one rigid template.

# ON-SLIDE TEXT (render these words only, spelled exactly)
- Eyebrow: {style.content_eyebrow}
- Title: {style.content_title}
- Stage labels: {stages}
- Footer left: {style.footer}
- Footer right: 02

# COMPOSITION
- Match the light base margins, title baseline, and footer.
- Header stays short: eyebrow, title, accent rule.
- Main area: a horizontal workflow of {stage_count} stages inside a light panel, thin connectors, accent {style.accent}.
- Keep most of the canvas usable for real slide content.
- Footer {style.footer} left, page number 02 right — the page only, never a total.
{motif}
# CONSTRAINTS
- Light background only: {style.light_bg}. Near-black body text.
- No logos, dense paragraphs, or extra words.
"""

    prompts = {
        "base_noncontent": (STYLE_BASE_NONCONTENT_FILENAME, dark, "none"),
        "base_content": (STYLE_BASE_CONTENT_FILENAME, light, "noncontent"),
        "cover": (STYLE_COVER_FILENAME, cover, "noncontent"),
        "transition": (STYLE_TRANSITION_FILENAME, transition, "noncontent"),
        "content": (STYLE_CONTENT_FILENAME, content, "content"),
    }
    jobs: list[StyleRefJob] = []
    for label, (filename, prompt, base_ref) in prompts.items():
        jobs.append(
            StyleRefJob(
                filename,
                label,
                prompt,
                base_ref=base_ref,  # type: ignore[arg-type]
                system_prompt=system,
            )
        )
    return jobs


BASE_REF_FILENAMES: Final[Mapping[BaseRefKind, tuple[str, ...]]] = {
    "none": (),
    "noncontent": (STYLE_BASE_NONCONTENT_FILENAME,),
    "content": (STYLE_BASE_CONTENT_FILENAME,),
}


def style_prompt_path(image_path: Path) -> Path:
    """Sidecar text file holding the prompt used to generate *image_path*."""
    return image_path.with_name(f"{image_path.stem}{STYLE_PROMPT_SUFFIX}")


def render_style_prompt_record(job: StyleRefJob) -> str:
    """Render the full prompt bundle for *job* as reviewable text."""
    references = BASE_REF_FILENAMES[job.base_ref]
    system = job.system_prompt or style_system_prompt(DeckStyle.from_files("", ""))
    return "\n".join(
        [
            f"# Style plate: {job.label}",
            f"Image: {job.filename}",
            f"Reference images: {', '.join(references) if references else 'none'}",
            "",
            "## System prompt",
            system.strip(),
            "",
            "## User prompt",
            job.user_prompt.strip(),
            "",
        ]
    )


def save_style_prompt(job: StyleRefJob, image_path: Path) -> Path:
    """Write the prompt used for *image_path* next to it, and return the sidecar path."""
    prompt_path = style_prompt_path(image_path)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(render_style_prompt_record(job), encoding="utf-8")
    return prompt_path


def _default_select(_label: str, _choices_path: Path, _count: int) -> int:
    return 1


async def _generate_candidate_batch(
    client: OpenRouterClient | VolcengineClient,
    *,
    prompt: str,
    system_prompt: str,
    count: int,
    reference_images: list[bytes] | None,
) -> list[bytes]:
    if count < 1:
        raise ValueError("count must be >= 1")
    prompts = [
        ImagePrompt(prompt, system_prompt, reference_images) for _ in range(count)
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
            prompt=job.user_prompt,
            system_prompt=job.system_prompt,
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
    script: str,
    design_brief: str,
    output_dir: Path,
    candidates: int = 1,
    select: StyleSelectFn | None = None,
) -> list[Path]:
    """Generate two-tone style-reference PNGs in *output_dir*.

    Stages:
    1. Non-content (dark curtain) base
    2. Content (light) base, motif-linked to the non-content base
    3. Cover, transition, and content plates

    Each plate also gets a ``<plate>_prompt.txt`` sidecar.
    """
    if candidates < 1:
        raise ValueError("candidates must be >= 1")

    picker = select or _default_select
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir = output_dir / STYLE_CANDIDATES_DIRNAME
    candidates_dir.mkdir(parents=True, exist_ok=True)

    jobs = build_style_ref_jobs(DeckStyle.from_files(script, design_brief))
    for job in jobs:
        save_style_prompt(job, output_dir / job.filename)
    noncontent_job = jobs[0]
    content_base_job = jobs[1]
    plate_jobs = jobs[2:]

    noncontent_bytes = await _select_stage_with_regen(
        client,
        job=noncontent_job,
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

    batch_results = await client.generate_images_parallel(
        [
            ImagePrompt(
                job.user_prompt,
                job.system_prompt,
                _reference_bytes_for_job(
                    job,
                    noncontent_base=noncontent_bytes,
                    content_base=content_base_bytes,
                ),
            )
            for job in plate_jobs
            for _ in range(candidates)
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
                system_prompt=job.system_prompt,
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

