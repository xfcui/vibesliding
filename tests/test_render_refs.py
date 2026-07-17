"""Tests for style reference image generation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.outline.parser import Slide
from src.outline.roles import classify_slide_role
from src.render.style.refs import (
    STYLE_BASE_CONTENT_FILENAME,
    STYLE_BASE_NONCONTENT_FILENAME,
    STYLE_CONTENT_FILENAME,
    STYLE_COVER_FILENAME,
    STYLE_TRANSITION_FILENAME,
    build_style_ref_jobs,
    extract_presentation_title,
    generate_style_references,
    select_style_paths_for_role,
)

SAMPLE_OUTLINE = """# PPT Outline: AI Native Development

---

## Slide 1: Cover
- **Title:** AI Native Development
[Visual: Cinematic cover]
[Speech: Welcome.]

---

## Appendix: Global Visual Requirements
- **Theme:** Two-tone — dark curtain for cover/transitions/ending; white for content
- **Colors:** Cyan accents on navy
"""


def test_extract_presentation_title() -> None:
    assert extract_presentation_title(SAMPLE_OUTLINE, fallback="idea") == "AI Native Development"


def test_build_style_ref_jobs_two_tone_plates() -> None:
    jobs = build_style_ref_jobs(idea="AI tools", outline=SAMPLE_OUTLINE)
    assert [job.filename for job in jobs] == [
        STYLE_BASE_NONCONTENT_FILENAME,
        STYLE_BASE_CONTENT_FILENAME,
        STYLE_COVER_FILENAME,
        STYLE_TRANSITION_FILENAME,
        STYLE_CONTENT_FILENAME,
    ]
    assert [job.label for job in jobs] == [
        "base_noncontent",
        "base_content",
        "cover",
        "transition",
        "content",
    ]
    assert "AI Native Development" in jobs[2].user_prompt
    assert "DARK CURTAIN" in jobs[0].user_prompt or "dark" in jobs[0].user_prompt.lower()
    assert "LIGHT CONTENT" in jobs[1].user_prompt or "white" in jobs[1].user_prompt.lower()
    assert "roadmap" in jobs[3].user_prompt.lower()
    assert "workflow" in jobs[4].user_prompt.lower() or "diagram" in jobs[4].user_prompt.lower()
    assert "GLOBAL VISUAL REQUIREMENTS" in jobs[0].user_prompt
    assert "TEXT STYLE SPEC" not in jobs[0].user_prompt
    assert jobs[0].base_ref == "none"
    assert jobs[1].base_ref == "noncontent"
    assert jobs[2].base_ref == "noncontent"
    assert jobs[3].base_ref == "noncontent"
    assert jobs[4].base_ref == "content"
    assert "Do not use a white/light background" in jobs[2].user_prompt
    assert "Do not use a dark curtain background" in jobs[4].user_prompt


def test_select_style_paths_for_role_prefers_two_tone_plates(tmp_path: Path) -> None:
    paths = [
        tmp_path / STYLE_BASE_NONCONTENT_FILENAME,
        tmp_path / STYLE_BASE_CONTENT_FILENAME,
        tmp_path / STYLE_COVER_FILENAME,
        tmp_path / STYLE_TRANSITION_FILENAME,
        tmp_path / STYLE_CONTENT_FILENAME,
    ]
    for path in paths:
        path.write_bytes(b"x")

    assert [p.name for p in select_style_paths_for_role("cover", paths)] == [
        STYLE_COVER_FILENAME,
        STYLE_BASE_NONCONTENT_FILENAME,
    ]
    assert [p.name for p in select_style_paths_for_role("transition", paths)] == [
        STYLE_TRANSITION_FILENAME,
        STYLE_BASE_NONCONTENT_FILENAME,
    ]
    assert [p.name for p in select_style_paths_for_role("content", paths)] == [
        STYLE_CONTENT_FILENAME,
        STYLE_BASE_CONTENT_FILENAME,
    ]
    assert [p.name for p in select_style_paths_for_role("ending", paths)] == [
        STYLE_COVER_FILENAME,
        STYLE_BASE_NONCONTENT_FILENAME,
    ]


def test_select_style_paths_for_role_falls_back_to_all(tmp_path: Path) -> None:
    custom = tmp_path / "custom_style.png"
    custom.write_bytes(b"x")
    assert select_style_paths_for_role("content", [custom]) == [custom]


def test_classify_slide_role_two_tone_routing() -> None:
    slides = [
        Slide(1, "Cover Title", "opener"),
        Slide(2, "Hook: Stakes", "hook"),
        Slide(3, "Roadmap: Section One", "progress bar 1/3"),
        Slide(4, "Teaching Point", "content"),
        Slide(5, "Thank You", "closing"),
    ]
    roles = [
        classify_slide_role(slide, position=i, total=len(slides))
        for i, slide in enumerate(slides)
    ]
    assert roles == ["cover", "content", "transition", "content", "ending"]


@pytest.mark.asyncio
async def test_generate_style_references_saves_canonical_pngs(tmp_path: Path) -> None:
    client = AsyncMock()
    buf = tmp_path / "fake.png"
    from PIL import Image

    Image.new("RGB", (64, 36), color="navy").save(buf)
    fake_bytes = buf.read_bytes()

    async def fake_parallel(prompts, on_result=None, **kwargs):
        return [fake_bytes for _ in prompts]

    client.generate_images_parallel = AsyncMock(side_effect=fake_parallel)

    def pick_first(_label: str, _choices_path: Path, count: int) -> int:
        return 1

    paths = await generate_style_references(
        client,
        idea="AI tools",
        outline=SAMPLE_OUTLINE,
        output_dir=tmp_path,
        candidates=2,
        select=pick_first,
    )

    assert len(paths) == 5
    assert [path.name for path in paths] == [
        STYLE_BASE_NONCONTENT_FILENAME,
        STYLE_BASE_CONTENT_FILENAME,
        STYLE_COVER_FILENAME,
        STYLE_TRANSITION_FILENAME,
        STYLE_CONTENT_FILENAME,
    ]
    assert all(path.exists() for path in paths)
    candidates_dir = tmp_path / "style_candidates"
    assert (candidates_dir / STYLE_BASE_NONCONTENT_FILENAME).exists()
    assert (candidates_dir / STYLE_BASE_CONTENT_FILENAME).exists()
    assert (candidates_dir / "style_base_noncontent_choices.png").exists()
    assert (candidates_dir / "style_base_content_choices.png").exists()
    assert (candidates_dir / "style_cover_choices.png").exists()
    assert client.generate_images_parallel.await_count == 3
    for call in client.generate_images_parallel.await_args_list:
        assert call.kwargs.get("image_size") == "1K"


@pytest.mark.asyncio
async def test_generate_style_references_regenerates_base_stage(tmp_path: Path) -> None:
    client = AsyncMock()
    buf = tmp_path / "fake.png"
    from PIL import Image

    Image.new("RGB", (64, 36), color="navy").save(buf)
    fake_bytes = buf.read_bytes()

    async def fake_parallel(prompts, on_result=None, **kwargs):
        return [fake_bytes for _ in prompts]

    client.generate_images_parallel = AsyncMock(side_effect=fake_parallel)

    base_attempts = {"count": 0}

    def pick_regen_then_first(label: str, _choices_path: Path, count: int) -> int:
        if label == "base_noncontent":
            base_attempts["count"] += 1
            if base_attempts["count"] == 1:
                return 0
        return 1

    paths = await generate_style_references(
        client,
        idea="AI tools",
        outline=SAMPLE_OUTLINE,
        output_dir=tmp_path,
        candidates=2,
        select=pick_regen_then_first,
    )

    assert len(paths) == 5
    assert (tmp_path / STYLE_BASE_NONCONTENT_FILENAME).exists()
    assert (tmp_path / STYLE_BASE_CONTENT_FILENAME).exists()
    assert base_attempts["count"] == 2
    assert client.generate_images_parallel.await_count == 4
    for call in client.generate_images_parallel.await_args_list:
        assert call.kwargs.get("image_size") == "1K"
