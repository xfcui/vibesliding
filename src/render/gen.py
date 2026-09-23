"""Slide image generation orchestrator - parallel slide image generation."""

from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Final

from src.core.api_client import (
    ImagePrompt,
    OpenRouterClient,
    VolcengineClient,
)
from src.core.paths import (
    DEFAULT_WORK_DIR,
    STYLE_IMAGE_EXTENSIONS,
    slides_pptx_path,
    style_images_in_dir,
    timestamp_from_image_dir,
    timestamp_slug,
)
from src.core.export import (
    create_pptx_from_images,
    save_image,
    slides_by_index_from_outline,
)
from src.core.resolve import PathResolveError, resolve_patterns
from src.core.parser import Slide, extract_global_style, parse_markdown
from src.core.roles import SlideRole, classify_slide_role
from src.design.plates import select_style_paths_for_role

# Constants
VISUAL_FOCUS_MAX_CHARS: Final[int] = 160
MAX_FAILURE_PREVIEW: Final[int] = 3
REFERENCE_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[(?:Reference(?:\s+(?:Images?|Photos?))?|"
    r"Image\s+Reference|Photo\s+Reference|Refs?)\s*:\s*(.*?)\]",
    re.IGNORECASE | re.DOTALL,
)
STYLE_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[Styles?\s*:\s*(.*?)\]",
    re.IGNORECASE | re.DOTALL,
)
SPEECH_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[Speech\s*:\s*(.*?)\]", re.IGNORECASE | re.DOTALL,
)
VISUAL_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[Visual\s*:\s*(.*?)\]", re.IGNORECASE | re.DOTALL,
)
HTML_COMMENT_PATTERN: Final[re.Pattern] = re.compile(r"<!--.*?-->", re.DOTALL)
RULE_LINE_PATTERN: Final[re.Pattern] = re.compile(r"^\s*-{3,}\s*$", re.MULTILINE)
SENTENCE_BREAK_PATTERN: Final[re.Pattern] = re.compile(r"(?<=[.!?;。！？；])\s+")
SUPPORTED_REFERENCE_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".png", ".jpg", ".jpeg"}
)
SLIDE_PROMPT_SUFFIX: Final[str] = "_prompt.txt"
ROLE_BRIEFS: Final[dict[str, str]] = {
    "cover": (
        "Cover slide. Dark curtain background. Make the premise legible at a glance. "
        "No slide number."
    ),
    "ending": (
        "Ending slide. Dark curtain background that visually reconnects to the cover. "
        "Land one take-home message. No slide number."
    ),
    "transition": (
        "Roadmap transition. Dark curtain background. Reuse the deck's section map, "
        "highlight only the current section, and show the section progress marker. "
        "No slide number."
    ),
    "content": (
        "Content / teaching slide. White or light background. Show the page number "
        "only where the [Visual:] instruction asks for it, never the total page count."
    ),
}


def _pick_tag(pattern: re.Pattern, text: str) -> re.Match | None:
    """Return the last non-empty match of *pattern*, else the last match."""
    matches = list(pattern.finditer(text))
    if not matches:
        return None
    for match in reversed(matches):
        if match.group(1).strip():
            return match
    return matches[-1]


def _split_visual(content: str) -> tuple[str, str]:
    """Return *content* without its chosen ``[Visual:]`` tag, and the tag text."""
    match = _pick_tag(VISUAL_TAG_PATTERN, content)
    if match is None:
        return content, ""
    rest = content[: match.start()] + content[match.end() :]
    return rest.strip(), match.group(1).strip()


def _clean_slide_content(content: str) -> str:
    """Drop tags, comments, and separators that are not on-slide content."""
    text = HTML_COMMENT_PATTERN.sub("", content)
    text = STYLE_TAG_PATTERN.sub("", text)
    text = REFERENCE_TAG_PATTERN.sub("", text)
    text = SPEECH_TAG_PATTERN.sub("", text)
    text = RULE_LINE_PATTERN.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _visual_focus(content: str, max_chars: int = VISUAL_FOCUS_MAX_CHARS) -> str:
    """First clause of a slide's ``[Visual:]`` tag, collapsed to one line."""
    _, visual = _split_visual(content)
    if not visual:
        return ""
    first = SENTENCE_BREAK_PATTERN.split(visual, maxsplit=1)[0]
    first = re.sub(r"\s+", " ", first).strip().rstrip(";；,，")
    if len(first) <= max_chars:
        return first
    return first[:max_chars].rstrip() + "…"


def _format_generation_failure(exc: Exception) -> str:
    """Include the API error body when httpx hid it behind a status line."""
    from src.core.api_client import _http_error_detail

    response = getattr(exc, "response", None)
    if response is None:
        return str(exc)
    try:
        detail = _http_error_detail(response)
    except Exception:
        return str(exc)
    text = str(exc)
    return text if detail in text else f"{text} — {detail}"


def slide_prompt_path(output_dir: Path, slide_index: int) -> Path:
    """Sidecar text file holding the prompt used for one slide's images."""
    return output_dir / f"slide_p{slide_index:02d}{SLIDE_PROMPT_SUFFIX}"


def save_slide_prompt(
    slide: Slide,
    output_dir: Path,
    *,
    user_prompt: str,
    system_prompt: str,
    style_reference_paths: list[Path],
    slide_reference_paths: list[Path],
) -> Path:
    """Write the prompt used for *slide*'s images into *output_dir*."""

    def _names(paths: list[Path]) -> str:
        return ", ".join(str(path) for path in paths) if paths else "none"

    record = "\n".join(
        [
            f"# Slide {slide.index}: {slide.title}",
            f"Style references: {_names(style_reference_paths)}",
            f"Slide references: {_names(slide_reference_paths)}",
            "",
            "## System prompt",
            system_prompt.strip(),
            "",
            "## User prompt",
            user_prompt.strip(),
            "",
        ]
    )
    prompt_path = slide_prompt_path(output_dir, slide.index)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(record, encoding="utf-8")
    return prompt_path


def _split_reference_patterns(raw_patterns: str) -> list[str]:
    """Split a reference tag into path/glob patterns."""
    patterns: list[str] = []
    for segment in raw_patterns.replace("\n", ",").split(","):
        segment = segment.strip()
        if not segment:
            continue
        try:
            parts = shlex.split(segment)
        except ValueError:
            parts = segment.split()
        patterns.extend(parts)
    return [p[1:] if p.startswith("@") else p for p in patterns if p]


def _extract_reference_patterns(slide: Slide) -> list[str]:
    """Return slide-scoped reference image path/glob patterns from outline tags."""
    patterns: list[str] = []
    for match in REFERENCE_TAG_PATTERN.finditer(slide.content):
        patterns.extend(_split_reference_patterns(match.group(1)))
    return patterns


def resolve_reference_image_paths(
    slide: Slide,
    outline_dir: Path | None = None,
) -> list[Path]:
    """Resolve slide-scoped reference image tags to concrete image files."""
    raw_patterns = _extract_reference_patterns(slide)
    if not raw_patterns:
        return []

    def _miss_message(pattern: str) -> str:
        return f"No reference image found for slide {slide.index}: {pattern}"

    def _not_file(path: Path) -> str:
        return f"Reference image is not a file: {path}"

    def _bad_extension(path: Path, suffix: str) -> str:
        supported = ", ".join(sorted(SUPPORTED_REFERENCE_EXTENSIONS))
        return (
            f"Unsupported reference image format '{suffix}' for {path.name}. "
            f"Supported: {supported}"
        )

    try:
        return resolve_patterns(
            raw_patterns,
            supported_extensions=SUPPORTED_REFERENCE_EXTENSIONS,
            base_dir=outline_dir,
            include_parent_base=True,
            sort=True,
            normalize=str.strip,
            glob_miss_error=_miss_message,
            file_miss_error=_miss_message,
            not_file_error=_not_file,
            bad_extension_error=_bad_extension,
        )
    except PathResolveError as exc:
        raise ValueError(exc.message) from exc


def _extract_style_plate_names(slide: Slide) -> list[str]:
    """Return style-plate filenames declared in the slide's ``[Style:]`` tags."""
    names: list[str] = []
    for match in STYLE_TAG_PATTERN.finditer(slide.content):
        names.extend(_split_reference_patterns(match.group(1)))
    return names


def resolve_style_plate_paths(slide: Slide, style_dir: Path | None) -> list[Path]:
    """Resolve a slide's ``[Style: filename]`` tags to plates inside *style_dir*.

    The tag takes bare filenames, not paths: plates always live in the ``--style``
    directory. Returns an empty list when the slide declares no plate, which lets
    the caller fall back to role-based routing.
    """
    names = _extract_style_plate_names(slide)
    if not names:
        return []
    if style_dir is None:
        raise ValueError(
            f"Slide {slide.index} declares [Style: {', '.join(names)}] but no style "
            "directory is available; pass --style <dir>."
        )

    resolved: list[Path] = []
    for name in names:
        candidate = Path(name)
        if candidate.name != name:
            raise ValueError(
                f"[Style:] on slide {slide.index} takes a filename, not a path: {name!r}. "
                f"Plates are looked up inside {style_dir}."
            )
        suffix = candidate.suffix.lower()
        if suffix not in STYLE_IMAGE_EXTENSIONS:
            supported = ", ".join(sorted(STYLE_IMAGE_EXTENSIONS))
            raise ValueError(
                f"Unsupported style plate format '{suffix}' on slide {slide.index}: "
                f"{name}. Supported: {supported}"
            )
        path = style_dir / name
        if not path.is_file():
            available = ", ".join(p.name for p in style_images_in_dir(style_dir))
            raise ValueError(
                f"Style plate not found for slide {slide.index}: {name}. "
                f"Available in {style_dir}: {available or 'none'}"
            )
        if path not in resolved:
            resolved.append(path)
    return resolved


def _parse_content_slides(
    outline: str,
    *,
    require_at_least_one: bool = True,
) -> tuple[list[Slide], str | None]:
    """Parse outline and return slides with the appendix slide removed.

    Page filters are applied by the caller after roles are classified on this
    full list, so a subset does not get cover or ending roles wrong.
    """
    slides = parse_markdown(outline)
    if not slides:
        raise ValueError("No slides found in outline (no H2 headings)")

    global_style = extract_global_style(slides)
    if global_style:
        slides = [slide for slide in slides if slide.content != global_style]
        if require_at_least_one and not slides:
            raise ValueError("Only style slide found in outline")

    return slides, global_style


class SlideImageGenerator:
    """Orchestrates parallel image generation for PPT slides."""

    def __init__(
        self,
        client: OpenRouterClient | VolcengineClient,
    ) -> None:
        self.client = client

    @staticmethod
    def _build_deck_map(slides: list[Slide], current_index: int) -> str:
        """Title-only deck map plus the neighbours' visual focus for continuity."""
        lines = ["# DECK MAP (context for visual flow; do not render):"]
        position: int | None = None
        for offset, slide in enumerate(slides):
            marker = ""
            if slide.index == current_index:
                marker = " (this slide)"
                position = offset
            lines.append(f"- Slide {slide.index}: {slide.title}{marker}")

        if position is not None:
            neighbors: list[str] = []
            for label, step in (("Previous", -1), ("Next", 1)):
                other_position = position + step
                if not 0 <= other_position < len(slides):
                    continue
                other = slides[other_position]
                focus = _visual_focus(other.content) or "no visual direction"
                neighbors.append(f"- {label}, slide {other.index} ({other.title}): {focus}")
            if neighbors:
                lines.append("")
                lines.append("# NEIGHBOUR VISUALS (keep motifs and layout rhythm continuous):")
                lines.extend(neighbors)
        return "\n".join(lines)

    @staticmethod
    def _build_prompt(
        slide: Slide,
        outline_context: str,
        global_style: str | None = None,
        with_style_reference: bool = False,
        slide_reference_paths: list[Path] | None = None,
        style_reference_count: int = 0,
        role: SlideRole | None = None,
    ) -> tuple[str, str]:
        """Build user and system prompts for current slide."""
        slide_reference_paths = slide_reference_paths or []
        rest, visual_tag = _split_visual(slide.content)
        clean_content = _clean_slide_content(rest)

        role_block = ""
        if role is not None:
            role_block = f"\n# THIS SLIDE\nRole: {role}. {ROLE_BRIEFS[role]}\n"

        style_parts: list[str] = []
        if with_style_reference:
            style_parts.append(
                "\n# VISUAL STYLE REFERENCE (layout + graphics — strict adherence):\n"
                "1. **Analyze**: Extract layout, composition, background treatment, graphic language, "
                "diagram/connector style, icon treatment, and motif vocabulary from the reference images "
                "attached for THIS slide type.\n"
                "2. **Replicate**: Match that visual system precisely — same background tone, layout "
                "rhythm, and graphic language. Content/teaching slides use white/light backgrounds; "
                "cover, transition, and ending slides use the dark curtain background.\n"
                "3. **Consistency**: The generated slide MUST look like it belongs in the same deck "
                "as the references (shared accents/motifs) while keeping the correct two-tone "
                "background for its role.\n"
                "4. **Adapt Content**: Keep the references' visual LOOK but replace all content "
                "with the new slide's text, diagrams, and narrative."
            )
        if global_style:
            text_style_block = (
                "\n# TEXT STYLE SPEC (palette + typography — render exactly):\n"
                f"{global_style}\n\n"
                "Render all on-slide text using these exact fonts, sizes, weights, and colors. "
                "Do not override the layout or composition shown in the reference images."
                if with_style_reference
                else (
                    "\n# TEXT STYLE SPEC (palette + typography — render exactly):\n"
                    f"{global_style}\n\n"
                    "Apply these text styles exactly. Layout and composition come from the "
                    "[Visual:] instruction on this slide."
                )
            )
            style_parts.append(text_style_block)
        if not style_parts:
            style_parts.append(
                "\n# VISUAL STYLE (Adaptive Professional):\n"
                "- **Palette**: Professional colors fitted to subject matter (Tech = deep navy/cyan, Nature = green/earth, Finance = navy/gold).\n"
                "- **Background**: Solid or subtle gradient with high text contrast. No busy textures.\n"
                "- **Graphics**: Modern flat or semi-flat vector illustrations. Clean lines, minimal shadows.\n"
                "- **Typography**: Bold geometric sans for titles, clean sans for body. High legibility."
            )
        style_instruction = "".join(style_parts)

        reference_instruction = ""
        reference_summary = ""
        if slide_reference_paths:
            names = ", ".join(str(p) for p in slide_reference_paths)
            if style_reference_count > 0:
                style_range = (
                    f"1-{style_reference_count}"
                    if style_reference_count > 1
                    else "1"
                )
                start = style_reference_count + 1
                end = style_reference_count + len(slide_reference_paths)
                slide_range = f"{start}-{end}" if start != end else str(start)
                reference_instruction = (
                    "\n# ATTACHED IMAGE ROLES\n"
                    f"- Attached image(s) {style_range}: deck visual style references only.\n"
                    f"- Attached image(s) {slide_range}: slide-specific photo/content references "
                    f"for this slide ({names}). Use these to anchor the subject, pose, "
                    "composition, and recognisable visual details requested by the outline.\n"
                    "- Do not treat slide-specific photos as global deck style. Do not copy "
                    "embedded text, watermarks, or accidental background artifacts unless the "
                    "outline explicitly asks for them.\n"
                )
            else:
                reference_instruction = (
                    "\n# ATTACHED SLIDE REFERENCE IMAGES\n"
                    f"The attached image(s) are slide-specific photo/content references "
                    f"for this slide ({names}). Use them to anchor the subject, pose, "
                    "composition, and recognisable visual details requested by the outline. "
                    "Do not copy embedded text, watermarks, or accidental background artifacts "
                    "unless the outline explicitly asks for them.\n"
                )
            reference_summary = (
                "\n**Attached Slide References**:\n"
                + "\n".join(f"- {p}" for p in slide_reference_paths)
                + "\n"
            )

        person_constraint = (
            "- Photorealistic people are allowed only when the attached slide-specific "
            "reference images request a real person/photo treatment; otherwise use "
            "silhouettes or stylized avatars."
            if slide_reference_paths
            else "- NO photorealistic human faces (use silhouettes or stylized avatars if needed)."
        )

        layout_block = (
            ""
            if visual_tag
            else """
# LAYOUT (match to content type)
- **Title Slide**: Bold centered title, strong background, one focal graphic. Use for cover/closing.
- **Split Screen**: Content column + visual column (either side). Use for concepts, intros, case studies.
- **Bento Grid**: 2–4 distinct blocks with icons or mini-visuals. Use for features, comparisons, multi-point summaries.
- **Diagram Focus**: Large central diagram/pipeline/flowchart with concise labels. Use for processes, architecture, workflows.
- **Statement**: One powerful sentence centered with supporting visual. Use for insights, transitions, takeaways.
"""
        )

        system_prompt = f"""You are an elite Presentation Designer. Generate a pixel-perfect 1920×1080 (16:9) slide image.

# PRIMARY DIRECTIVE
If a `[Visual: ...]` instruction exists for this slide, treat it as the **authoritative** art direction — layout, composition, focal elements, and narrative structure all follow from it. Everything else in this prompt is secondary.

# CORE STANDARDS
1. **Aspect Ratio**: Strictly 16:9 landscape. No square or portrait crops.
2. **Typography**: Professional sans-serif. Titles 60 pt+ bold, body 24 pt+. Every character must be crisp, correctly spelled, and fully legible at presentation distance.
3. **Safe Margins**: 5 % padding on all edges. No content touching or bleeding off the frame.
4. **Visual Hierarchy**: Title → key visual/diagram → supporting text, in that prominence order.
5. **Separation**: Text never overlaps graphics, icons, or diagram elements.
6. **Cohesion**: This slide must look like it belongs in the same deck as every other slide.
{role_block}
{outline_context}
{style_instruction}
{reference_instruction}
{layout_block}
# VISUAL EXECUTION
- **Show, don't tell**: The visual must communicate the slide's core idea before any text is read.
- **Diagrams**: Clean boxes, arrows, labels. Show relationships, flow, or hierarchy — not decoration.
- **Lists on slide**: Icon bullets or numbered steps with generous spacing — never dense paragraphs.
- **Data**: Render as clean charts or infographics, never raw tables of numbers.

# HARD CONSTRAINTS
- NO spelling errors or malformed characters in any rendered text.
- NO placeholder or lorem ipsum text.
- NO dense text walls — keep on-slide text to short labels, titles, and key phrases; use diagrams and visuals to carry detail.
- NO cropped or cut-off elements at any edge.
- NO low-contrast text (must be readable at 3 m viewing distance).
- NO watermarks, AI-generation stamps, or fake brand logos.
- NO page totals: show at most this slide's own page number, only when the [Visual:] asks for it — never "N/total" or "N of M".
- NO new facts: every number, name, and term on the slide matches the slide content exactly.
{person_constraint}"""

        visual_instruction = f"\n**STRICT VISUAL INSTRUCTION**: {visual_tag}" if visual_tag else ""

        user_prompt = f"""GENERATE SLIDE {slide.index}: "{slide.title}"

**Slide Content** (distill into on-slide text — do not paste verbatim):
{clean_content}
{visual_instruction}
{reference_summary}
**On-slide text**: Keep the slide title's wording exactly (a `Roadmap:` prefix may become a small eyebrow). Turn bullets into short labels of a few words. Never render markdown symbols (`**`, list dashes, backticks), takeaway prefixes such as `Core insight:`, or tag names such as `[Visual:]`.

Render a single polished slide image. The visual composition must tell this slide's content at a glance; on-slide text supports and labels, it does not duplicate the visual.
"""

        return user_prompt, system_prompt

    @staticmethod
    def _report_results(results: list[bytes | Exception], expected: int) -> None:
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = [r for r in results if isinstance(r, Exception)]

        if failures:
            print(
                f"API returned: {successes}/{expected} succeeded, {len(failures)} failed"
            )
            for i, exc in enumerate(failures[:MAX_FAILURE_PREVIEW], 1):
                print(f"  Failure {i}: {_format_generation_failure(exc)}")
            remaining = len(failures) - MAX_FAILURE_PREVIEW
            if remaining > 0:
                print(f"  ... and {remaining} more")
        else:
            print(f"Generated {successes}/{expected} image(s) successfully.")

    @staticmethod
    def _save_image_result(result: bytes | Exception, path: Path) -> Path | None:
        if isinstance(result, Exception):
            return None
        save_image(result, path)
        return path

    @staticmethod
    def _create_output_pptx(
        saved_paths: list[Path],
        *,
        pptx_path: Path,
        outline: str | None = None,
    ) -> None:
        if not saved_paths:
            return
        slides_by_index = (
            slides_by_index_from_outline(outline) if outline is not None else None
        )
        create_pptx_from_images(saved_paths, pptx_path, slides_by_index)
        print(f"Created {pptx_path.name}")

    def _make_image_save_callback(
        self,
        paths: list[Path],
        saved_slots: list[Path | None],
    ):
        def on_result(index: int, result: bytes | Exception) -> None:
            if index < 0 or index >= len(paths):
                return
            saved = self._save_image_result(result, paths[index])
            if saved is not None:
                saved_slots[index] = saved

        return on_result

    @staticmethod
    def _ordered_saved_paths(saved_slots: list[Path | None]) -> list[Path]:
        return [path for path in saved_slots if path is not None]

    def _build_slide_prompts(
        self,
        slide: Slide,
        *,
        deck_slides: list[Slide],
        role: SlideRole,
        global_style: str | None,
        with_style_reference: bool,
        style_ref_images: list[bytes] | None,
        style_reference_count: int,
        outline_dir: Path | None,
        copy: int,
        output_dir: Path,
        style_reference_paths: list[Path] | None = None,
    ) -> list[ImagePrompt]:
        slide_reference_paths = resolve_reference_image_paths(slide, outline_dir)
        slide_reference_images = [path.read_bytes() for path in slide_reference_paths]
        if style_ref_images is not None:
            combined_ref_images = style_ref_images + slide_reference_images
        else:
            combined_ref_images = slide_reference_images

        user_prompt, system_prompt = self._build_prompt(
            slide,
            self._build_deck_map(deck_slides, slide.index),
            global_style=global_style,
            with_style_reference=with_style_reference,
            slide_reference_paths=slide_reference_paths,
            style_reference_count=style_reference_count,
            role=role,
        )
        save_slide_prompt(
            slide,
            output_dir,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            style_reference_paths=style_reference_paths or [],
            slide_reference_paths=slide_reference_paths,
        )
        ref_payload = combined_ref_images or None
        return [
            ImagePrompt(
                user_prompt,
                system_prompt,
                ref_payload,
            )
            for _ in range(copy)
        ]

    async def _generate_and_finalize(
        self,
        prompts: list[ImagePrompt],
        paths: list[Path],
        *,
        pptx_path: Path,
        expected: int,
        outline: str | None = None,
    ) -> tuple[list[Path | None], list[Path]]:
        saved_slots: list[Path | None] = [None] * len(paths)
        results = await self.client.generate_images_parallel(
            prompts,
            on_result=self._make_image_save_callback(paths, saved_slots),
            desc="Slide images",
        )
        self._report_results(results, expected)
        saved_paths = self._ordered_saved_paths(saved_slots)
        self._create_output_pptx(
            saved_paths,
            pptx_path=pptx_path,
            outline=outline,
        )
        return saved_slots, saved_paths

    async def generate_first_slide_images(
        self,
        outline: str,
        copy: int,
        output_dir: Path,
        outline_dir: Path | None = None,
        *,
        work_dir: Path = DEFAULT_WORK_DIR,
        run_timestamp: str | None = None,
    ) -> list[Path]:
        """Generate multiple image variants for the first slide only."""
        slides, global_style = _parse_content_slides(outline)
        slide = slides[0]
        print(f"Parsed outline: 1 slide (first slide only). Title: {slide.title!r}")
        print(
            f"Generating {copy} image(s) for slide 1 "
            f"(parallel, max {self.client.max_concurrent} concurrent)..."
        )

        out_dir = Path(output_dir)
        slide_reference_paths = resolve_reference_image_paths(slide, outline_dir)
        if slide_reference_paths:
            print(
                "Using slide reference(s): "
                + ", ".join(p.name for p in slide_reference_paths)
            )

        prompts = self._build_slide_prompts(
            slide,
            deck_slides=slides,
            role=classify_slide_role(slide, position=0, total=len(slides)),
            global_style=global_style,
            with_style_reference=False,
            style_ref_images=None,
            style_reference_count=0,
            outline_dir=outline_dir,
            copy=copy,
            output_dir=out_dir,
        )

        paths = [
            out_dir / f"slide_p{slide.index:02d}_v{i + 1:02d}.png"
            for i in range(copy)
        ]
        ts = run_timestamp or timestamp_from_image_dir(out_dir) or timestamp_slug()
        _, saved_paths = await self._generate_and_finalize(
            prompts,
            paths,
            pptx_path=slides_pptx_path(work_dir, ts),
            expected=copy,
            outline=outline,
        )
        return saved_paths

    async def generate_all_slide_images(
        self,
        outline: str,
        style_image_paths: list[Path],
        copy: int,
        output_dir: Path,
        page_filter: set[int] | None = None,
        outline_dir: Path | None = None,
        *,
        style_dir: Path | None = None,
        work_dir: Path = DEFAULT_WORK_DIR,
        run_timestamp: str | None = None,
    ) -> dict[int, list[Path]]:
        """Generate multiple image variants for all slides using style reference(s).

        A slide's ``[Style: filename]`` tag selects its plates from *style_dir*;
        slides without one fall back to role-based routing over *style_image_paths*.
        """
        all_slides, global_style = _parse_content_slides(
            outline,
            require_at_least_one=False,
        )
        if not all_slides:
            raise ValueError("No slides found in outline (no H2 headings)")
        position_by_index = {slide.index: position for position, slide in enumerate(all_slides)}
        slides = all_slides
        if page_filter is not None:
            slides = [slide for slide in all_slides if slide.index in page_filter]
            if not slides:
                raise ValueError(f"No slides match the page filter: {sorted(page_filter)}")

        total = len(slides) * copy
        slide_titles = [slide.title for slide in slides]
        print(f"Parsed outline: {len(slides)} slide(s). Titles: {slide_titles}")
        print(
            "Using style reference(s): "
            + ", ".join(path.name for path in style_image_paths)
        )
        print(
            f"Generating {total} image(s) ({len(slides)} slides × {copy} per slide, "
            f"max {self.client.max_concurrent} concurrent)..."
        )

        style_bytes_by_path = {path: path.read_bytes() for path in style_image_paths}
        out_dir = Path(output_dir)

        reference_summaries: list[str] = []
        style_summaries: list[str] = []
        all_prompts: list[ImagePrompt] = []
        total_slides = len(all_slides)
        for slide in slides:
            position = position_by_index[slide.index]
            role = classify_slide_role(slide, position=position, total=total_slides)
            declared_style_paths = resolve_style_plate_paths(slide, style_dir)
            role_style_paths = declared_style_paths or select_style_paths_for_role(
                role, style_image_paths
            )
            style_ref_images = [
                style_bytes_by_path.setdefault(path, path.read_bytes())
                for path in role_style_paths
            ]
            source = "outline" if declared_style_paths else role
            style_summaries.append(
                f"slide {slide.index} ({source}): "
                + ", ".join(path.name for path in role_style_paths)
            )
            slide_reference_paths = resolve_reference_image_paths(slide, outline_dir)
            if slide_reference_paths:
                reference_summaries.append(
                    f"slide {slide.index}: "
                    + ", ".join(path.name for path in slide_reference_paths)
                )
            all_prompts.extend(
                self._build_slide_prompts(
                    slide,
                    deck_slides=all_slides,
                    role=role,
                    global_style=global_style,
                    with_style_reference=True,
                    style_ref_images=style_ref_images,
                    style_reference_count=len(style_ref_images),
                    outline_dir=outline_dir,
                    copy=copy,
                    output_dir=out_dir,
                    style_reference_paths=role_style_paths,
                )
            )

        print("Style plates by slide: " + "; ".join(style_summaries))
        if reference_summaries:
            print("Using slide reference(s): " + "; ".join(reference_summaries))

        paths = [
            out_dir / f"slide_p{slide.index:02d}_v{v + 1:02d}.png"
            for slide in slides
            for v in range(copy)
        ]
        ts = run_timestamp or timestamp_from_image_dir(out_dir) or timestamp_slug()
        saved_slots, _ = await self._generate_and_finalize(
            all_prompts,
            paths,
            pptx_path=slides_pptx_path(work_dir, ts),
            expected=total,
            outline=outline,
        )

        slide_paths: dict[int, list[Path]] = {}
        idx = 0
        for slide in slides:
            slide_paths[slide.index] = []
            for _ in range(copy):
                saved = saved_slots[idx]
                if saved is not None:
                    slide_paths[slide.index].append(saved)
                idx += 1

        return slide_paths
