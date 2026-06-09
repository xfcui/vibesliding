"""Tests for style reference image generation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.style.refs import (
    STYLE_BASE_FILENAME,
    STYLE_COVER_FILENAME,
    STYLE_CONTENT_FILENAME,
    STYLE_TRANSITION_FILENAME,
    build_style_ref_jobs,
    extract_presentation_title,
    generate_style_references,
)

SAMPLE_OUTLINE = """# PPT Outline: AI Native Development

---

## Slide 1: Cover
- **Title:** AI Native Development
[Visual: Cinematic cover]
[Speech: Welcome.]

---

## Appendix: Global Visual Requirements
- **Theme:** Dark cinematic
- **Colors:** Cyan accents on navy
"""


def test_extract_presentation_title() -> None:
    assert extract_presentation_title(SAMPLE_OUTLINE, fallback="idea") == "AI Native Development"


def test_build_style_ref_jobs_includes_four_plates() -> None:
    jobs = build_style_ref_jobs(idea="AI tools", outline=SAMPLE_OUTLINE)
    assert [job.filename for job in jobs] == [
        STYLE_BASE_FILENAME,
        STYLE_COVER_FILENAME,
        STYLE_TRANSITION_FILENAME,
        STYLE_CONTENT_FILENAME,
    ]
    assert "AI Native Development" in jobs[1].user_prompt
    assert "NO cover title" in jobs[0].user_prompt or "NO slide-specific layout" in jobs[0].user_prompt
    assert "roadmap" in jobs[2].user_prompt.lower()
    assert "workflow" in jobs[3].user_prompt.lower() or "diagram" in jobs[3].user_prompt.lower()
    assert "Dark cinematic" in jobs[0].user_prompt
    assert "GLOBAL VISUAL REQUIREMENTS" in jobs[0].user_prompt
    assert "TEXT STYLE SPEC" not in jobs[0].user_prompt
    assert jobs[0].use_base_reference is False
    assert all(job.use_base_reference for job in jobs[1:])


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

    assert len(paths) == 4
    assert [path.name for path in paths] == [
        STYLE_BASE_FILENAME,
        STYLE_COVER_FILENAME,
        STYLE_TRANSITION_FILENAME,
        STYLE_CONTENT_FILENAME,
    ]
    assert all(path.exists() for path in paths)
    assert (tmp_path / STYLE_BASE_FILENAME).exists()
    candidates_dir = tmp_path / "style_candidates"
    assert (candidates_dir / STYLE_BASE_FILENAME).exists()
    assert (candidates_dir / "style_base_choices.png").exists()
    assert (candidates_dir / "style_cover_choices.png").exists()
    assert client.generate_images_parallel.await_count == 2
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
        if label == "base":
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

    assert len(paths) == 4
    assert (tmp_path / STYLE_BASE_FILENAME).exists()
    assert base_attempts["count"] == 2
    assert client.generate_images_parallel.await_count == 3
    for call in client.generate_images_parallel.await_args_list:
        assert call.kwargs.get("image_size") == "1K"
