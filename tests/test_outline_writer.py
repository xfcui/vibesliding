"""Tests for outline generation from research."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.core.api_client import OpenRouterClient
from src.outline.writer import (
    build_outline_user_prompt,
    load_outline_standards,
    strip_code_fences,
    validate_outline,
    write_outline,
    write_outlines_parallel,
)

VALID_OUTLINE = """# PPT Outline: Test Deck

---

## Slide 1: Introduction
- **Hook:** Why this matters
- Core insight: One clear takeaway
[Visual: Hero image with title left]
[Speech: Welcome everyone.]

---

## Appendix: Global Visual Requirements
- **Theme:** Dark mode
"""


class TestValidateOutline:
    def test_valid_outline_has_no_warnings(self) -> None:
        result = validate_outline(VALID_OUTLINE)
        assert result.ok

    def test_missing_visual_tag_warns(self) -> None:
        bad = VALID_OUTLINE.replace("[Visual: Hero image with title left]", "")
        result = validate_outline(bad)
        assert not result.ok
        assert any("Visual" in w for w in result.warnings)

    def test_missing_title_prefix_warns(self) -> None:
        bad = VALID_OUTLINE.replace("# PPT Outline:", "# Outline:")
        result = validate_outline(bad)
        assert any("PPT Outline" in w for w in result.warnings)


class TestStripCodeFences:
    def test_removes_wrapping_fences(self) -> None:
        text = "```markdown\n# PPT Outline: X\n```"
        assert strip_code_fences(text).startswith("# PPT Outline:")


class TestBuildPrompt:
    def test_includes_idea_and_slide_count(self) -> None:
        prompt = build_outline_user_prompt(
            "My idea",
            "Report text",
            "1. Source",
            target_slides=8,
        )
        assert "My idea" in prompt
        assert "8" in prompt
        assert "content slides" in prompt
        assert "does **not** include" in prompt
        assert "Report text" in prompt


@pytest.mark.asyncio
async def test_write_outline_calls_client_with_standards(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    standards = tmp_path / "standards.mdc"
    standards.write_text("# Outline Standards\n\nUse ## Slide headers.", encoding="utf-8")

    client = OpenRouterClient(api_key="fake", model="text/model")
    client.complete_text = AsyncMock(return_value=VALID_OUTLINE)  # type: ignore[method-assign]

    outline, validation = await write_outline(
        client,
        idea="Test idea",
        report="Research body",
        sources_text="1. Source — https://example.com",
        target_slides=5,
        text_model="anthropic/claude-sonnet-4",
        standards_path=standards,
    )

    assert outline == VALID_OUTLINE
    assert validation.ok
    client.complete_text.assert_awaited_once()
    call_kwargs = client.complete_text.await_args.kwargs
    assert call_kwargs["model"] == "anthropic/claude-sonnet-4"
    system_prompt = client.complete_text.await_args.args[1]
    assert "Outline Standards" in system_prompt


def test_load_outline_standards_from_repo() -> None:
    text = load_outline_standards()
    assert "Outline Standards" in text


class TestSharedStylePrompt:
    def test_outline_user_prompt_includes_scaffold_when_provided(self) -> None:
        scaffold = "### Appendix: Global Visual Requirements\n- **Theme:** Navy #0a1628"
        prompt = build_outline_user_prompt(
            "idea",
            "report",
            "sources",
            target_slides=16,
            style_scaffold=scaffold,
        )
        assert "SHARED STYLE SCAFFOLD" in prompt
        assert "Navy #0a1628" in prompt
        assert "verbatim" in prompt


@pytest.mark.asyncio
async def test_write_outlines_parallel_uses_shared_scaffold(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    standards = tmp_path / "standards.mdc"
    standards.write_text("# Outline Standards\n", encoding="utf-8")

    client = OpenRouterClient(api_key="fake", model="text/model")
    scaffold = "### Deck Title\nTest\n### Appendix: Global Visual Requirements\n- **Theme:** Shared"
    client.complete_text = AsyncMock(return_value=scaffold)  # type: ignore[method-assign]
    client.complete_text_parallel = AsyncMock(  # type: ignore[method-assign]
        return_value=[VALID_OUTLINE, VALID_OUTLINE]
    )

    returned_scaffold, outlines = await write_outlines_parallel(
        client,
        idea="idea",
        report="report",
        sources_text="sources",
        target_slides=[6, 12],
        standards_path=standards,
    )

    assert returned_scaffold == scaffold
    assert len(outlines) == 2
    client.complete_text.assert_awaited_once()
    parallel_prompts = client.complete_text_parallel.await_args.args[0]
    assert all("SHARED STYLE SCAFFOLD" in user for user, _ in parallel_prompts)
    assert all("Shared" in user for user, _ in parallel_prompts)
