"""Image generation orchestrator - parallel slide image generation."""

from pathlib import Path

from src.api_client import OpenRouterClient
from src.output import create_pdf_from_images, save_image
from src.parser import Slide, parse_markdown


class SlideImageGenerator:
    """Orchestrates parallel image generation for PPT slides."""

    def __init__(self, client: OpenRouterClient):
        self.client = client

    @staticmethod
    def _build_full_outline_context(slides: list[Slide]) -> str:
        """Build complete outline string for context."""
        parts = ["# PRESENTATION OUTLINE (Context for visual flow):"]
        for slide in slides:
            parts.append(f"- Slide {slide.index}: {slide.title}")
            content_preview = slide.content[:200].replace("\n", " ") + "..." if len(slide.content) > 200 else slide.content.replace("\n", " ")
            parts.append(f"  Content: {content_preview}")
        return "\n".join(parts)

    @staticmethod
    def _extract_global_style(slides: list[Slide]) -> str | None:
        """Extract global visual style from a slide if present."""
        style_keywords = ["global visual requirements", "visual style", "design standards"]
        for slide in slides:
            if any(k in slide.title.lower() for k in style_keywords):
                return slide.content
        return None

    @staticmethod
    def _build_prompt(
        slide: Slide,
        outline_context: str,
        global_style: str | None = None,
        with_style_reference: bool = False,
        with_article: bool = False,
    ) -> tuple[str, str]:
        """Build user and system prompts for current slide."""
        article_instruction = ""
        if with_article:
            article_instruction = (
                "\n# REFERENCE ARTICLE\n"
                "An original article is provided as context. Use insights, data, and themes from this article to inform slide content and ensure accuracy.\n"
            )
        
        if with_style_reference:
            style_instruction = (
                "\n# VISUAL STYLE REFERENCE (STRICT ADHERENCE REQUIRED):\n"
                "1. **Analyze the Reference Image**: Extract the color palette (background, accents, text), font style, layout grid, and graphic mood.\n"
                "2. **Style Transfer**: Replicate the exact visual style. Match the background texture and color hex codes EXACTLY.\n"
                "3. **Consistency**: The new slide MUST look like it belongs to the same deck as the reference.\n"
                "4. **Content Adaptation**: Keep the reference's LOOK, but replace the content with the new text provided below."
            )
        elif global_style:
             style_instruction = (
                f"\n# GLOBAL VISUAL REQUIREMENTS (STRICT ADHERENCE REQUIRED):\n"
                f"{global_style}\n\n"
                "- **Consistency**: Ensure this slide matches the defined theme, fonts, and palette exactly."
            )
        else:
            style_instruction = (
                "\n# VISUAL STYLE SPECIFICATION (Adaptive Professional):\n"
                "- **Palette**: Derive a professional color palette that fits the *subject matter* (e.g., Tech = Blue/Grey, Nature = Green/Earth, Finance = Navy/Gold).\n"
                "- **Background**: Clean, solid or subtle gradient. High contrast with text.\n"
                "- **Graphics**: Modern, flat, or semi-flat vector illustrations. Minimal shadows.\n"
                "- **Mood**: Professional, trustworthy, clear.\n"
            )

        system_prompt = f"""You are an elite Presentation Designer and Data Visualization Expert.
Your task is to generate a pixel-perfect 1920x1080 (16:9) slide image.

# GLOBAL DESIGN STANDARDS
1. **Aspect Ratio**: 16:9 (Landscape).
2. **Typography**: Use professional, highly legible sans-serif fonts. Title size: 60pt+. Body size: 24pt+.
3. **Margins**: Maintain 5% safety margin on all sides. No content touching edges.
4. **Consistency**: Maintain a cohesive visual identity throughout the presentation.

{outline_context}
{article_instruction}
{style_instruction}

# LAYOUT STRATEGY (Choose one based on content)
- **Title Slide**: Bold, centered title, minimal visual, strong background.
- **Split Screen**: Text on left/right, Image/Chart on opposite side. Best for "Introduction" or "Concept vs. Reality".
- **Bento Grid**: 2-4 distinct rectangular content blocks. Best for "Key Points" or "Features".
- **Data Focus**: Large chart/graph in center, key takeaway text below/side. Best for "Statistics" or "Trends".
- **Statement**: One powerful sentence or quote in center. Best for "Vision" or "Impact".

# VISUAL INTERPRETATION
- If the content contains a `[Visual: ...]` tag, PRIORITIZE that instruction for the imagery/layout.
- Visualize the core concept. Do not just paste the text.
- If the content contains a list, use a clean list layout with custom bullets or icons.
- If the content contains data, visualize it as a chart or infographic.

# NEGATIVE CONSTRAINTS
- NO spelling errors.
- NO lorem ipsum or placeholder text.
- NO cluttered "wall of text" (max 30 words per slide unless a list).
- NO cropped elements.
- NO low-contrast text (e.g., light gray on white).
- NO photorealistic human faces (use silhouettes or stylized avatars if needed)."""

        user_prompt = f"""GENERATE SLIDE {slide.index}
**Title**: {slide.title}

**Content**:
{slide.content}

**Design Instructions**:
1. Select the most appropriate layout from the LAYOUT STRATEGY list above.
2. Visualize the core concept. Do not just paste the text.
3. If the content contains a list, use a clean list layout with custom bullets or icons.
4. If the content contains data, visualize it as a chart or infographic.
5. ENSURE the Title is the most prominent text element.
"""

        return user_prompt, system_prompt

    @staticmethod
    def _report_results(results: list[bytes | Exception], expected: int) -> None:
        """Print success/failure counts for API results."""
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = [r for r in results if isinstance(r, Exception)]
        if failures:
            print(f"API returned: {successes}/{expected} succeeded, {len(failures)} failed")
            for i, ex in enumerate(failures[:3], 1):
                print(f"  Failure {i}: {ex}")
            if len(failures) > 3:
                print(f"  ... and {len(failures) - 3} more")
        else:
            print(f"Generated {successes}/{expected} image(s) successfully.")

    @staticmethod
    def _save_images_and_pdf(
        results: list[bytes | Exception],
        paths: list[Path],
        output_dir: Path,
    ) -> list[Path]:
        """Save non-exception results to paths and create combined PDF. Returns list of saved paths."""
        saved_paths: list[Path] = []
        for result, path in zip(results, paths):
            if isinstance(result, Exception):
                continue
            save_image(result, path)
            saved_paths.append(path)
        if saved_paths:
            print(f"Saving {len(saved_paths)} image(s) to {output_dir}...")
            pdf_path = output_dir / "slide_combined.pdf"
            create_pdf_from_images(saved_paths, pdf_path)
            print(f"Created {pdf_path.name}")
        return saved_paths

    async def generate_first_slide_images(
        self,
        outline: str,
        copy: int,
        output_dir: Path,
        article_pdf: bytes | None = None,
        article_text: str | None = None,
    ) -> list[Path]:
        """Generate copy images for the first slide in parallel."""
        slides = parse_markdown(outline)
        if not slides:
            raise ValueError("No slides found in outline (no H2 headings)")
        
        global_style = self._extract_global_style(slides)
        # Filter out the style slide if present to avoid generating it
        if global_style:
            slides = [s for s in slides if s.content != global_style]
            if not slides:
                 raise ValueError("Only style slide found in outline")

        slide = slides[0]
        print(f"Parsed outline: 1 slide (first slide only). Title: {slide.title!r}")
        print(f"Generating {copy} image(s) for slide 1 (parallel, max {self.client.max_concurrent} concurrent)...")

        outline_context = self._build_full_outline_context(slides)
        with_article = article_pdf is not None or article_text is not None
        user_prompt, system_prompt = self._build_prompt(
            slide,
            outline_context,
            global_style=global_style,
            with_style_reference=False,
            with_article=with_article,
        )
        prompts = [
            (user_prompt, system_prompt, None, article_pdf, article_text)
            for _ in range(copy)
        ]
        results = await self.client.generate_images_parallel(prompts)

        self._report_results(results, copy)

        output_dir = Path(output_dir)
        paths = [output_dir / f"slide_p{slide.index:02d}_v{i + 1:02d}.png" for i in range(len(results))]
        return self._save_images_and_pdf(results, paths, output_dir)

    async def generate_all_slide_images(
        self,
        outline: str,
        style_image_path: Path,
        copy: int,
        output_dir: Path,
        article_pdf: bytes | None = None,
        article_text: str | None = None,
        page_filter: set[int] | None = None,
    ) -> dict[int, list[Path]]:
        """Generate copy images for each slide in parallel batches.
        
        Args:
            page_filter: If provided, only generate images for slides with index in this set.
        """
        slides = parse_markdown(outline)
        if not slides:
            raise ValueError("No slides found in outline (no H2 headings)")

        global_style = self._extract_global_style(slides)
        # Filter out the style slide if present
        if global_style:
             slides = [s for s in slides if s.content != global_style]
        
        # Filter slides if page_filter is provided
        if page_filter is not None:
            slides = [s for s in slides if s.index in page_filter]
            if not slides:
                raise ValueError(f"No slides match the page filter: {sorted(page_filter)}")
        
        total = len(slides) * copy
        print(f"Parsed outline: {len(slides)} slide(s). Titles: {[s.title for s in slides]}")
        print(f"Using style reference: {style_image_path}")
        print(f"Generating {total} image(s) ({len(slides)} slides × {copy} per slide, max {self.client.max_concurrent} concurrent)...")

        ref_image = style_image_path.read_bytes()
        outline_context = self._build_full_outline_context(slides)
        with_article = article_pdf is not None or article_text is not None
        all_prompts: list[
            tuple[str, str | None, bytes | None, bytes | None, str | None]
        ] = []
        for slide in slides:
            user_prompt, system_prompt = self._build_prompt(
                slide,
                outline_context,
                global_style=global_style,
                with_style_reference=True,
                with_article=with_article,
            )
            all_prompts.extend(
                [
                    (user_prompt, system_prompt, ref_image, article_pdf, article_text)
                    for _ in range(copy)
                ]
            )

        results = await self.client.generate_images_parallel(all_prompts)

        self._report_results(results, total)

        output_dir = Path(output_dir)
        paths = []
        for slide in slides:
            for v in range(copy):
                paths.append(output_dir / f"slide_p{slide.index:02d}_v{v + 1:02d}.png")
        self._save_images_and_pdf(results, paths, output_dir)

        slide_paths: dict[int, list[Path]] = {}
        idx = 0
        for slide in slides:
            slide_paths[slide.index] = []
            for v in range(copy):
                if idx < len(results) and not isinstance(results[idx], Exception):
                    path = output_dir / f"slide_p{slide.index:02d}_v{v + 1:02d}.png"
                    slide_paths[slide.index].append(path)
                idx += 1
        return slide_paths
