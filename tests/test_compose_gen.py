import base64
import io

import httpx
import pytest
from pathlib import Path
from PIL import Image

from src.compose.gen import SlideImageGenerator, resolve_reference_image_paths
from src.core.api_client import OpenRouterClient
from src.outline.parser import Slide, extract_global_style

SAMPLE_OUTLINE = """# PPT Outline: Test Deck

---

## Slide 1: Cover
- **Hook:** Opening point
[Visual: Bold title slide]
[Speech: Welcome to the deck.]

---

## Slide 2: Content
- **Point:** Main idea
[Visual: Diagram focus]
[Speech: Here is the main idea.]

---

## Appendix: Global Visual Requirements
- **Theme:** Navy #001122
"""

@pytest.fixture
def generator(client):
    return SlideImageGenerator(client)

def test_build_full_outline_context(generator):
    slides = [
        Slide(index=1, title="Title 1", content="Content 1"),
        Slide(index=2, title="Title 2", content="Content 2")
    ]
    context = generator._build_full_outline_context(slides)
    assert "Slide 1: Title 1" in context
    assert "Slide 2: Title 2" in context

def test_extract_global_style(generator):
    slides = [
        Slide(index=1, title="Global Visual Requirements", content="Style content"),
        Slide(index=2, title="Regular Slide", content="Regular content")
    ]
    style = extract_global_style(slides)
    assert style == "Style content"

def test_build_prompt(generator):
    slide = Slide(index=1, title="Test Slide", content="Test content [Visual: A test visual]")
    user_p, sys_p = generator._build_prompt(slide, "Outline context")
    
    assert "Test Slide" in user_p
    assert "A test visual" in user_p
    assert "Outline context" in sys_p
    assert "Test content" in user_p


def test_resolve_slide_reference_images_accepts_cursor_paths(generator, tmp_path):
    ref = tmp_path / "person.png"
    ref.write_bytes(b"fake")
    slide = Slide(
        index=1,
        title="Cover",
        content=f"Intro\n[Reference: @{ref}]\n[Visual: use the photo]",
    )

    assert resolve_reference_image_paths(slide) == [ref]


def test_resolve_slide_reference_images_expands_globs(generator, tmp_path):
    (tmp_path / "peter_2.png").write_bytes(b"2")
    (tmp_path / "peter_1.png").write_bytes(b"1")
    slide = Slide(
        index=2,
        title="Hook",
        content="[Reference: peter_*.png]",
    )

    resolved = resolve_reference_image_paths(slide, outline_dir=tmp_path)

    assert [p.name for p in resolved] == ["peter_1.png", "peter_2.png"]


def test_build_prompt_injects_text_style_with_style_references(generator):
    slide = Slide(
        index=1,
        title="Cover",
        content="Cover copy\n[Visual: cinematic opener]",
    )
    global_style = "- **Theme:** Navy background\n- **Fonts:** Inter Bold 36pt"

    _user_p, sys_p = generator._build_prompt(
        slide,
        "Outline context",
        global_style=global_style,
        with_style_reference=True,
    )

    assert "VISUAL STYLE REFERENCE" in sys_p
    assert "TEXT STYLE SPEC" in sys_p
    assert "Navy background" in sys_p
    assert "Do not override the layout" in sys_p


def test_build_prompt_strips_reference_tags_and_describes_image_roles(generator, tmp_path):
    ref = tmp_path / "data.png"
    slide = Slide(
        index=1,
        title="Cover",
        content=f"Cover copy\n[Reference: {ref}]\n[Visual: use my coding figure]",
    )

    user_p, sys_p = generator._build_prompt(
        slide,
        "Outline context",
        slide_reference_paths=[ref],
        style_reference_count=2,
        with_style_reference=True,
    )

    assert "[Reference:" not in user_p
    assert "Cover copy" in user_p
    assert "Attached Slide References" in user_p
    assert "Attached image(s) 1-2: deck visual style references only" in sys_p
    assert "slide-specific photo/content references" in sys_p
    assert "Photorealistic people are allowed" in sys_p


def test_resolve_reference_image_paths_missing_raises(tmp_path: Path) -> None:
    slide = Slide(index=1, title="Cover", content="[Reference: missing.png]")
    with pytest.raises(ValueError, match="No reference image found"):
        resolve_reference_image_paths(slide, outline_dir=tmp_path)


def test_report_results_counts_failures(generator, capsys) -> None:
    generator._report_results(
        [
            b"ok",
            RuntimeError("boom"),
            ValueError("bad"),
            OSError("x"),
            TimeoutError("slow"),
        ],
        expected=5,
    )
    out = capsys.readouterr().out
    assert "1/5 succeeded" in out
    assert "Failure 1:" in out
    assert "... and 1 more" in out


def test_report_results_all_success(generator, capsys) -> None:
    generator._report_results([b"a", b"b"], expected=2)
    assert "Generated 2/2 image(s) successfully." in capsys.readouterr().out


def _png_bytes(color: str = "blue") -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), color=color).save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_generate_first_slide_images_mocked(
    generator, tmp_path: Path, respx_mock
) -> None:
    image_bytes = _png_bytes()
    b64 = base64.b64encode(image_bytes).decode("ascii")
    respx_mock.post(f"{OpenRouterClient.BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "images": [
                                {"image_url": {"url": f"data:image/png;base64,{b64}"}}
                            ]
                        }
                    }
                ]
            },
        )
    )

    out_dir = tmp_path / "slides"
    paths = await generator.generate_first_slide_images(
        SAMPLE_OUTLINE,
        copy=2,
        output_dir=out_dir,
    )

    assert len(paths) == 2
    assert all(p.exists() for p in paths)
    assert (out_dir / "slide_combined.pdf").exists()
    assert (out_dir / "slide_speech.pdf").exists()


@pytest.mark.asyncio
async def test_generate_all_slide_images_mocked(
    generator, tmp_path: Path, respx_mock
) -> None:
    image_bytes = _png_bytes()
    b64 = base64.b64encode(image_bytes).decode("ascii")
    respx_mock.post(f"{OpenRouterClient.BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "images": [
                                {"image_url": {"url": f"data:image/png;base64,{b64}"}}
                            ]
                        }
                    }
                ]
            },
        )
    )

    style_ref = tmp_path / "style_cover.png"
    style_ref.write_bytes(image_bytes)
    out_dir = tmp_path / "slides"

    by_slide = await generator.generate_all_slide_images(
        SAMPLE_OUTLINE,
        style_image_paths=[style_ref],
        copy=1,
        output_dir=out_dir,
        page_filter={1, 2},
    )

    assert set(by_slide.keys()) == {1, 2}
    assert len(by_slide[1]) == 1
    assert (out_dir / "slide_p01_v01.png").exists()
    assert (out_dir / "slide_p02_v01.png").exists()


@pytest.mark.asyncio
async def test_generate_all_slide_images_page_filter_miss(generator, tmp_path: Path) -> None:
    style_ref = tmp_path / "style.png"
    style_ref.write_bytes(b"x")
    with pytest.raises(ValueError, match="No slides match the page filter"):
        await generator.generate_all_slide_images(
            SAMPLE_OUTLINE,
            style_image_paths=[style_ref],
            copy=1,
            output_dir=tmp_path / "out",
            page_filter={99},
        )


def test_build_prompt_with_articles(generator) -> None:
    slide = Slide(index=1, title="Stats", content="Key numbers")
    _user_p, sys_p = generator._build_prompt(
        slide,
        "Outline context",
        with_articles=True,
    )
    assert "REFERENCE ARTICLES" in sys_p
