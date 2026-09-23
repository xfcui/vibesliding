"""Tests for style reference image generation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from PIL import Image

from src.core.api_client import STYLE_IMAGE_PIXEL_SIZE, _coerce_image_prompt
from src.core.parser import Slide
from src.core.roles import classify_slide_role
from src.design.plates import (
    STYLE_BASE_CONTENT_FILENAME,
    STYLE_BASE_NONCONTENT_FILENAME,
    STYLE_CONTENT_FILENAME,
    STYLE_COVER_FILENAME,
    STYLE_TRANSITION_FILENAME,
    DeckStyle,
    build_style_ref_jobs,
    cover_display_title,
    extract_presentation_title,
    generate_style_references,
    install_style_candidate,
    render_style_prompt_record,
    select_style_paths_for_role,
    style_prompt_path,
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

SAMPLE_BRIEF = """
- **Topic family:** evidence-led lecture about careful iteration
- **Mood:** restrained editorial
- **Signature motif:** a small closed loop
- **Avoid:** fake logos and watermarks
- **Language:** en
- **Footer:** DECK
- **Cover eyebrow:** LECTURE
- **Cover title:** CLEAR LOOP
- **Cover support:** MAKE IT CLEAR
- **Content eyebrow:** EVIDENCE
- **Content title:** CHECK THE CLAIM
- **Content stages:** LOOK, COMPARE, CHECK
"""


def test_install_style_candidate_downscales_to_plate_size(tmp_path: Path) -> None:
    candidate = tmp_path / "style_cover_v02.png"
    Image.new("RGB", (2560, 1440), color="navy").save(candidate)
    plate = tmp_path / "style_cover.png"

    installed = install_style_candidate(candidate, plate)

    assert installed == plate
    with Image.open(plate) as img:
        assert img.size == STYLE_IMAGE_PIXEL_SIZE


def test_extract_presentation_title() -> None:
    assert extract_presentation_title(SAMPLE_OUTLINE, fallback="idea") == "AI Native Development"


def test_build_style_ref_jobs_two_tone_plates() -> None:
    jobs = build_style_ref_jobs(DeckStyle.from_files(SAMPLE_OUTLINE, SAMPLE_BRIEF))
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
    assert "Dark background only" in jobs[2].user_prompt
    assert "Light background only" in jobs[4].user_prompt
    for job in jobs:
        assert "SPELL EXACTLY" in job.user_prompt
        assert "CURSOR" not in job.user_prompt
        assert "VIBE" not in job.user_prompt
    assert "ON-SLIDE TEXT" in jobs[2].user_prompt
    assert "CLEAR LOOP" in jobs[2].user_prompt
    assert "LOOK" in jobs[4].user_prompt
    assert "CHECK" in jobs[4].user_prompt


def test_style_prompts_do_not_conflict() -> None:
    style = DeckStyle.from_files(SAMPLE_OUTLINE, SAMPLE_BRIEF)
    jobs = build_style_ref_jobs(style)
    system = jobs[0].system_prompt
    assert "5 % safe margin" not in system
    assert "GLOBAL VISUAL REQUIREMENTS" in system
    for job in jobs:
        assert "(context only, do not typeset)" in job.user_prompt
        composition = job.user_prompt.split("# COMPOSITION", 1)[1].split("# CONSTRAINTS", 1)[0]
        constraints = job.user_prompt.split("# CONSTRAINTS", 1)[1]
        assert "background" not in composition.lower().replace("background tone", "")
        assert style.dark_bg in constraints or style.light_bg in constraints


def test_cover_display_title_uses_first_clause() -> None:
    assert (
        cover_display_title(
            "Learning AI for Life Science — Why It Matters, Why It Is Hard, How to Do It"
        )
        == "Learning AI for Life Science"
    )
    assert cover_display_title("AI Native Development") == "AI Native Development"
    assert cover_display_title("") == "Presentation"


def test_render_style_prompt_record_includes_system_and_references() -> None:
    jobs = build_style_ref_jobs(DeckStyle.from_files(SAMPLE_OUTLINE, SAMPLE_BRIEF))
    record = render_style_prompt_record(jobs[4])
    assert "# Style plate: content" in record
    assert f"Image: {STYLE_CONTENT_FILENAME}" in record
    assert f"Reference images: {STYLE_BASE_CONTENT_FILENAME}" in record
    assert "## System prompt" in record
    assert "## User prompt" in record
    assert jobs[4].user_prompt.strip() in record
    assert "Reference images: none" in render_style_prompt_record(jobs[0])


def test_style_prompt_path_is_sidecar_of_image(tmp_path: Path) -> None:
    assert (
        style_prompt_path(tmp_path / STYLE_COVER_FILENAME).name
        == "style_cover_prompt.txt"
    )


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


def test_deck_style_falls_back_when_brief_is_empty() -> None:
    english = DeckStyle.from_files(SAMPLE_OUTLINE, "")
    assert english.language == "en"
    assert english.cover_eyebrow == "LECTURE"
    assert english.content_stages == ["LOOK", "COMPARE", "CHECK"]
    assert english.mood == "restrained editorial lecture"

    chinese_script = SAMPLE_OUTLINE.replace(
        "AI Native Development",
        "人工智能原生开发需要先把证据摆在台上",
    )
    chinese = DeckStyle.from_files(chinese_script, "")
    assert chinese.language == "zh"
    assert chinese.cover_eyebrow == "讲座"
    assert chinese.content_stages == ["一看", "一比", "一证"]


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
    marked = Slide(2, "Middle beat", "a progress bar 2/4 across the curtain")
    assert classify_slide_role(marked, position=1, total=4) == "transition"


def test_classify_slide_role_rejects_bad_position() -> None:
    slide = Slide(1, "Cover Title", "opener")
    with pytest.raises(ValueError, match="out of range"):
        classify_slide_role(slide, position=1, total=1)
    with pytest.raises(ValueError, match="total must be >= 1"):
        classify_slide_role(slide, position=0, total=0)


@pytest.mark.asyncio
async def test_generate_style_references_saves_canonical_pngs(tmp_path: Path) -> None:
    client = AsyncMock()
    buf = tmp_path / "fake.png"
    from PIL import Image

    Image.new("RGB", (64, 36), color="navy").save(buf)
    fake_bytes = buf.read_bytes()

    async def fake_parallel(prompts, on_result=None, **kwargs):
        return [_coerce_image_prompt(prompt) and fake_bytes for prompt in prompts]

    client.generate_images_parallel = AsyncMock(side_effect=fake_parallel)

    def pick_first(_label: str, _choices_path: Path, count: int) -> int:
        return 1

    paths = await generate_style_references(
        client,
        script=SAMPLE_OUTLINE,
        design_brief=SAMPLE_BRIEF,
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
    assert all(style_prompt_path(path).exists() for path in paths)
    cover_prompt = style_prompt_path(tmp_path / STYLE_COVER_FILENAME).read_text(
        encoding="utf-8"
    )
    assert "AI Native Development" in cover_prompt
    assert f"Reference images: {STYLE_BASE_NONCONTENT_FILENAME}" in cover_prompt
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
        script=SAMPLE_OUTLINE,
        design_brief=SAMPLE_BRIEF,
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
