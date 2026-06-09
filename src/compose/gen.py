"""Slide image generation orchestrator - parallel slide image generation."""

from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Final

from src.core.api_client import ImagePrompt, OpenRouterClient, VolcengineClient
from src.core.export import (
    create_pdf_from_images,
    create_speech_pdf,
    save_image,
    slides_by_index_from_outline,
)
from src.core.resolve import PathResolveError, resolve_patterns
from src.outline.parser import Slide, extract_global_style, parse_markdown

# Constants
CONTENT_PREVIEW_LENGTH: Final[int] = 200
MAX_FAILURE_PREVIEW: Final[int] = 3
REFERENCE_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[(?:Reference(?:\s+(?:Images?|Photos?))?|"
    r"Image\s+Reference|Photo\s+Reference|Refs?)\s*:\s*(.*?)\]",
    re.IGNORECASE | re.DOTALL,
)
SPEECH_TAG_PATTERN: Final[re.Pattern] = re.compile(
    r"\[Speech\s*:.*?\]", re.IGNORECASE | re.DOTALL,
)
SUPPORTED_REFERENCE_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".png", ".jpg", ".jpeg"}
)


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


def _parse_content_slides(
    outline: str,
    *,
    page_filter: set[int] | None = None,
    require_at_least_one: bool = True,
) -> tuple[list[Slide], str | None]:
    """Parse outline and return content slides with style slide removed."""
    slides = parse_markdown(outline)
    if not slides:
        raise ValueError("No slides found in outline (no H2 headings)")

    global_style = extract_global_style(slides)
    if global_style:
        slides = [slide for slide in slides if slide.content != global_style]
        if require_at_least_one and not slides:
            raise ValueError("Only style slide found in outline")

    if page_filter is not None:
        slides = [slide for slide in slides if slide.index in page_filter]
        if not slides:
            raise ValueError(f"No slides match the page filter: {sorted(page_filter)}")

    return slides, global_style


class SlideImageGenerator:
    """Orchestrates parallel image generation for PPT slides."""

    def __init__(self, client: OpenRouterClient | VolcengineClient) -> None:
        self.client = client

    @staticmethod
    def _build_full_outline_context(slides: list[Slide]) -> str:
        """Build complete outline string for visual flow context."""
        parts = ["# PRESENTATION OUTLINE (Context for visual flow):"]
        for slide in slides:
            parts.append(f"- Slide {slide.index}: {slide.title}")
            content = slide.content.replace("\n", " ")
            if len(content) > CONTENT_PREVIEW_LENGTH:
                content = content[:CONTENT_PREVIEW_LENGTH] + "..."
            parts.append(f"  Content: {content}")
        return "\n".join(parts)

    @staticmethod
    def _build_prompt(
        slide: Slide,
        outline_context: str,
        global_style: str | None = None,
        with_style_reference: bool = False,
        with_articles: bool = False,
        slide_reference_paths: list[Path] | None = None,
        style_reference_count: int = 0,
    ) -> tuple[str, str]:
        """Build user and system prompts for current slide."""
        slide_reference_paths = slide_reference_paths or []
        visual_tag = ""
        visual_match = re.search(r"\[Visual:\s*(.*?)\]", slide.content, re.IGNORECASE)
        if visual_match:
            visual_tag = visual_match.group(1).strip()
            clean_content = slide.content.replace(visual_match.group(0), "").strip()
        else:
            clean_content = slide.content
        clean_content = REFERENCE_TAG_PATTERN.sub("", clean_content)
        clean_content = SPEECH_TAG_PATTERN.sub("", clean_content).strip()

        article_instruction = ""
        if with_articles:
            article_instruction = (
                "\n# REFERENCE ARTICLES\n"
                "Articles are attached as context. Use them to extract accurate numbers, named "
                "examples, domain terminology, and visual metaphors for this slide. "
                "Do not copy article prose verbatim — distill into slide-appropriate labels and visuals.\n"
            )

        style_parts: list[str] = []
        if with_style_reference:
            style_parts.append(
                "\n# VISUAL STYLE REFERENCE (layout + graphics — strict adherence):\n"
                "1. **Analyze**: Extract layout, composition, background treatment, graphic language, "
                "diagram/connector style, icon treatment, and motif vocabulary from the reference images.\n"
                "2. **Replicate**: Match that visual system precisely — same background, layout rhythm, "
                "and graphic language.\n"
                "3. **Consistency**: The generated slide MUST look like it belongs in the same deck "
                "as the references.\n"
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

{outline_context}
{article_instruction}
{style_instruction}
{reference_instruction}

# LAYOUT (match to content type)
- **Title Slide**: Bold centered title, strong background, one focal graphic. Use for cover/closing.
- **Split Screen**: Content column + visual column (either side). Use for concepts, intros, case studies.
- **Bento Grid**: 2–4 distinct blocks with icons or mini-visuals. Use for features, comparisons, multi-point summaries.
- **Diagram Focus**: Large central diagram/pipeline/flowchart with concise labels. Use for processes, architecture, workflows.
- **Statement**: One powerful sentence centered with supporting visual. Use for insights, transitions, takeaways.

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
{person_constraint}"""

        visual_instruction = f"\n**STRICT VISUAL INSTRUCTION**: {visual_tag}" if visual_tag else ""

        user_prompt = f"""GENERATE SLIDE {slide.index}: "{slide.title}"

**Slide Content** (distill into on-slide text — do not paste verbatim):
{clean_content}
{visual_instruction}
{reference_summary}
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
                print(f"  Failure {i}: {exc}")
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
    def _create_output_pdfs(
        saved_paths: list[Path],
        output_dir: Path,
        *,
        outline: str | None = None,
    ) -> None:
        if not saved_paths:
            return
        combined_path = output_dir / "presentation_slides.pdf"
        create_pdf_from_images(saved_paths, combined_path)
        print(f"Created {combined_path.name}")
        if outline is None:
            return
        speech_path = output_dir / "presentation_speech.pdf"
        create_speech_pdf(saved_paths, slides_by_index_from_outline(outline), speech_path)
        print(f"Created {speech_path.name}")

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
        outline_context: str,
        global_style: str | None,
        with_style_reference: bool,
        with_articles: bool,
        style_ref_images: list[bytes] | None,
        style_reference_count: int,
        outline_dir: Path | None,
        article_pdfs: list[bytes] | None,
        article_texts: list[str] | None,
        copy: int,
    ) -> list[ImagePrompt]:
        slide_reference_paths = resolve_reference_image_paths(slide, outline_dir)
        slide_reference_images = [path.read_bytes() for path in slide_reference_paths]
        if style_ref_images is not None:
            combined_ref_images = style_ref_images + slide_reference_images
        else:
            combined_ref_images = slide_reference_images

        user_prompt, system_prompt = self._build_prompt(
            slide,
            outline_context,
            global_style=global_style,
            with_style_reference=with_style_reference,
            with_articles=with_articles,
            slide_reference_paths=slide_reference_paths,
            style_reference_count=style_reference_count,
        )
        ref_payload = combined_ref_images or None
        return [
            ImagePrompt(
                user_prompt,
                system_prompt,
                ref_payload,
                article_pdfs,
                article_texts,
            )
            for _ in range(copy)
        ]

    async def _generate_and_finalize(
        self,
        prompts: list[ImagePrompt],
        paths: list[Path],
        output_dir: Path,
        *,
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
        self._create_output_pdfs(saved_paths, output_dir, outline=outline)
        return saved_slots, saved_paths

    async def generate_first_slide_images(
        self,
        outline: str,
        copy: int,
        output_dir: Path,
        article_pdfs: list[bytes] | None = None,
        article_texts: list[str] | None = None,
        outline_dir: Path | None = None,
    ) -> list[Path]:
        """Generate multiple image variants for the first slide only."""
        slides, global_style = _parse_content_slides(outline)
        slide = slides[0]
        print(f"Parsed outline: 1 slide (first slide only). Title: {slide.title!r}")
        print(
            f"Generating {copy} image(s) for slide 1 "
            f"(parallel, max {self.client.max_concurrent} concurrent)..."
        )

        outline_context = self._build_full_outline_context(slides)
        with_articles = bool(article_pdfs or article_texts)
        slide_reference_paths = resolve_reference_image_paths(slide, outline_dir)
        if slide_reference_paths:
            print(
                "Using slide reference(s): "
                + ", ".join(p.name for p in slide_reference_paths)
            )

        prompts = self._build_slide_prompts(
            slide,
            outline_context=outline_context,
            global_style=global_style,
            with_style_reference=False,
            with_articles=with_articles,
            style_ref_images=None,
            style_reference_count=0,
            outline_dir=outline_dir,
            article_pdfs=article_pdfs,
            article_texts=article_texts,
            copy=copy,
        )

        out_dir = Path(output_dir)
        paths = [
            out_dir / f"slide_p{slide.index:02d}_v{i + 1:02d}.png"
            for i in range(copy)
        ]
        _, saved_paths = await self._generate_and_finalize(
            prompts,
            paths,
            out_dir,
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
        article_pdfs: list[bytes] | None = None,
        article_texts: list[str] | None = None,
        page_filter: set[int] | None = None,
        outline_dir: Path | None = None,
    ) -> dict[int, list[Path]]:
        """Generate multiple image variants for all slides using style reference(s)."""
        slides, global_style = _parse_content_slides(
            outline,
            page_filter=page_filter,
            require_at_least_one=False,
        )
        if not slides:
            assert page_filter is not None
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

        ref_images = [path.read_bytes() for path in style_image_paths]
        outline_context = self._build_full_outline_context(slides)
        with_articles = bool(article_pdfs or article_texts)

        reference_summaries: list[str] = []
        all_prompts: list[ImagePrompt] = []
        for slide in slides:
            slide_reference_paths = resolve_reference_image_paths(slide, outline_dir)
            if slide_reference_paths:
                reference_summaries.append(
                    f"slide {slide.index}: "
                    + ", ".join(path.name for path in slide_reference_paths)
                )
            all_prompts.extend(
                self._build_slide_prompts(
                    slide,
                    outline_context=outline_context,
                    global_style=global_style,
                    with_style_reference=True,
                    with_articles=with_articles,
                    style_ref_images=ref_images,
                    style_reference_count=len(ref_images),
                    outline_dir=outline_dir,
                    article_pdfs=article_pdfs,
                    article_texts=article_texts,
                    copy=copy,
                )
            )

        if reference_summaries:
            print("Using slide reference(s): " + "; ".join(reference_summaries))

        out_dir = Path(output_dir)
        paths = [
            out_dir / f"slide_p{slide.index:02d}_v{v + 1:02d}.png"
            for slide in slides
            for v in range(copy)
        ]
        saved_slots, _ = await self._generate_and_finalize(
            all_prompts,
            paths,
            out_dir,
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
