"""Tests for per-slide script writing."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.core.api_client import OpenRouterClient
from src.plan.parse import PlanSlide, parse_plan
from src.write.prompts import (
    build_system_prompt,
    build_user_prompt,
    select_relevant_facts,
    writing_sections,
)
from src.write.writer import check_slide_body, write_script

PLAN = """# PPT Outline: Loop

---

## Slide 1: Start Here
- Role: cover
- Point: The premise
- Point: The promise
- Visual hook: dark cover
[Style: style_cover.png]

---

## Slide 2: Practice The Loop
- Role: content
- Point: Repeat
- Point: Measure
- Evidence: facts.md — nine flights
- Visual hook: two columns
[Style: style_content.png]
[Reference: notes/photo.png]

---

## Appendix: Global Visual Requirements
- **Theme:** Navy
"""

CONTENT_BODY = """- **Repeat:** Each pass is short
- **Measure:** Count what changed
- **Keep:** Leave the rest
- **Drop:** Cut what failed
- **Again:** Start the next pass
- Core insight: Loops beat one-shot plans
[Visual: two columns, before and after. Slide number: 2]
[Speech: This is the loop, and next we close.]
"""

COVER_BODY = """- **Premise:** Start with the stakes
- **Promise:** Leave with a loop
- **Ask:** Try one pass
[Visual: dark cover with a loop mark]
[Speech: Welcome.]
"""


def _client(results: list[str | Exception]) -> OpenRouterClient:
    client = OpenRouterClient(api_key="fake", model="text/model")
    client.complete_text_parallel = AsyncMock(return_value=results)  # type: ignore[method-assign]
    return client


@pytest.mark.asyncio
async def test_write_script_calls_once_per_slide_and_keeps_tags(tmp_path: Path) -> None:
    document = parse_plan(PLAN)
    client = _client([COVER_BODY, CONTENT_BODY])
    script, drafts = await write_script(
        client,
        document,
        idea="Audience: new members. Language: English.",
        facts="Nine flights.",
        standards="Use message titles.",
        prompt_dir=tmp_path / "write_prompts",
        text_model="anthropic/claude-sonnet-4",
    )
    assert client.complete_text_parallel.await_count == 1
    prompts = client.complete_text_parallel.await_args.args[0]
    assert len(prompts) == 2
    assert not any(draft.failed for draft in drafts)
    assert "[Style: style_cover.png]" in script
    assert "[Style: style_content.png]" in script
    assert "[Reference: notes/photo.png]" in script
    assert script.startswith("# PPT Outline: Loop")
    assert (tmp_path / "write_prompts" / "slide_p01_prompt.txt").is_file()
    assert (tmp_path / "write_prompts" / "slide_p02_prompt.txt").is_file()


@pytest.mark.asyncio
async def test_failed_slide_keeps_plan_text(tmp_path: Path) -> None:
    document = parse_plan(PLAN)
    client = _client([COVER_BODY, "not a slide"])
    script, drafts = await write_script(
        client,
        document,
        idea="",
        facts="",
        standards="standards",
        prompt_dir=tmp_path,
    )
    assert drafts[1].failed
    assert "<!-- write failed:" in script
    assert "Repeat" in script


@pytest.mark.asyncio
async def test_page_filter_merges_into_existing_script(tmp_path: Path) -> None:
    document = parse_plan(PLAN)
    client = _client([COVER_BODY, CONTENT_BODY])
    original, _ = await write_script(
        client,
        document,
        idea="",
        facts="",
        standards="standards",
        prompt_dir=tmp_path / "first",
    )
    assert "before and after" in original
    replacement = CONTENT_BODY.replace("before and after", "a single loop")
    client.complete_text_parallel = AsyncMock(return_value=[replacement])  # type: ignore[method-assign]
    merged, drafts = await write_script(
        client,
        document,
        idea="",
        facts="",
        standards="standards",
        prompt_dir=tmp_path / "second",
        page_filter={2},
        existing_script=original,
    )
    assert len(drafts) == 1
    assert "a single loop" in merged
    assert "Welcome." in merged
    assert merged.count("## Slide ") == 2


@pytest.mark.asyncio
async def test_page_filter_keeps_script_appendix(tmp_path: Path) -> None:
    document = parse_plan(PLAN)
    client = _client([COVER_BODY, CONTENT_BODY])
    original, _ = await write_script(
        client,
        document,
        idea="",
        facts="",
        standards="standards",
        prompt_dir=tmp_path / "first",
    )
    edited = original.replace("Navy", "Edited navy")
    client.complete_text_parallel = AsyncMock(return_value=[CONTENT_BODY])  # type: ignore[method-assign]
    merged, _ = await write_script(
        client,
        document,
        idea="",
        facts="",
        standards="standards",
        prompt_dir=tmp_path / "second",
        page_filter={2},
        existing_script=edited,
    )
    assert "Edited navy" in merged
    assert merged.count("## Appendix") == 1


def test_system_prompt_keeps_writing_rules_only() -> None:
    document = parse_plan(PLAN)
    standards = (
        "## Plan format\nuse Point lines\n\n"
        "## Writing Standards\nmessage titles\n\n"
        "## Visual Tags\nshow the claim\n\n"
        "## Speech Tags\nbridge sentence\n\n"
        "## Appendix Requirements\nhex codes\n"
    )
    prompt = build_system_prompt(standards, document.slides[1])
    assert "message titles" in prompt
    assert "bridge sentence" in prompt
    assert "Plan format" not in prompt
    assert "hex codes" not in prompt
    assert "`Slide number: 2`" in prompt
    document = parse_plan(PLAN)
    slide = document.slides[1]
    body = CONTENT_BODY + "\n[Visual: another]\n[Speech: again]"
    reasons = " ".join(check_slide_body(body, slide))
    assert "[Visual:]" in reasons
    assert "[Speech:]" in reasons


def test_system_prompt_speech_length_follows_role() -> None:
    document = parse_plan(PLAN)
    cover = build_system_prompt("## Writing Standards\nx\n", document.slides[0])
    content = build_system_prompt("## Writing Standards\nx\n", document.slides[1])
    assert "about 30 seconds" in cover and "visual outweighs the text" in cover
    assert "1-2 minutes" in content and "about 30 seconds" not in content


def test_cover_prompt_has_no_page_number() -> None:
    document = parse_plan(PLAN)
    prompt = build_system_prompt("## Writing Standards\nrules\n", document.slides[0])
    assert "Slide number:" not in prompt


@pytest.mark.parametrize(
    "marker",
    ["Slide number: 2/2", "Slide number: 2 / 16", "Slide number: 2 of 16", "Slide number: 3"],
)
def test_content_page_number_rejects_totals_and_wrong_page(marker: str) -> None:
    slide = parse_plan(PLAN).slides[1]
    body = CONTENT_BODY.replace("Slide number: 2", marker)
    reasons = " ".join(check_slide_body(body, slide))
    assert "Slide number: 2" in reasons


def test_content_page_number_passes_without_total() -> None:
    slide = parse_plan(PLAN).slides[1]
    assert check_slide_body(CONTENT_BODY, slide) == []


def test_cover_with_page_number_fails() -> None:
    slide = parse_plan(PLAN).slides[0]
    assert check_slide_body(COVER_BODY, slide) == []
    body = COVER_BODY.replace("loop mark]", "loop mark. Slide number: 1]")
    assert "should not show a slide number" in " ".join(check_slide_body(body, slide))


def test_transition_needs_exactly_four_bullets() -> None:
    slide = PlanSlide(index=3, title="Roadmap: Close The Loop", role="transition", section="1/3")
    four = "- **1:** a\n- **2:** b\n- **3:** c\n- **4:** d\n[Visual: map, progress bar 1/3]\n[Speech: s]"
    assert check_slide_body(four, slide) == []
    three = four.replace("- **4:** d\n", "")
    assert "3 bullets, expected exactly 4" in check_slide_body(three, slide)


STANDARDS_WITH_NOISE = """## Writing Standards
Titles state the message.

```markdown
## Slide 4: Example heading
- Bad bullet
```

## Visual/Text Balance

### Targets

Count words first. Measure with `measure_slide_balance` from `src/outline/writer.py` rather than by eye.

| Slide role | Bullet lines |
|---|---|
| Content | 6 (5 + takeaway) |
| Transition | 4 (roadmap as text) |
| Cover / Ending | 3-4 |

### Anti-patterns

```markdown
## Slide 9: Data Problems
```

## Speech Tags
End with a bridge.

## Appendix Requirements
hex codes
"""


def test_writing_sections_drops_examples_and_repo_refs() -> None:
    text = writing_sections(STANDARDS_WITH_NOISE, "transition")
    assert "## Slide" not in text
    assert "```" not in text
    assert "measure_slide_balance" not in text
    assert "src/outline" not in text
    assert "Count words first." in text
    assert "### Anti-patterns" not in text
    assert "| Transition |" in text
    assert "| Content |" not in text
    assert "| Cover / Ending |" not in text
    assert "|---|---|" in text
    assert "End with a bridge." in text


def test_writing_sections_keeps_all_rows_without_role() -> None:
    text = writing_sections(STANDARDS_WITH_NOISE)
    assert "| Content |" in text and "| Cover / Ending |" in text


def test_select_relevant_facts_ranks_by_overlap() -> None:
    slide = parse_plan(PLAN).slides[1]
    facts = (
        "# Weather\n- Rain fell on Tuesday in the valley\n\n"
        "# Practice\n- Pilots logged nine flights before each measure review\n\n"
        + "Unrelated filler sentence about gardening. " * 200
    )
    picked = select_relevant_facts(facts, slide, budget=300)
    assert "nine flights" in picked
    assert "# Practice" in picked
    assert "Rain fell" not in picked
    assert len(picked) <= 300


def test_select_relevant_facts_pins_cited_ids() -> None:
    plan = PLAN.replace("- Evidence: facts.md — nine flights", "- Evidence: F2")
    slide = parse_plan(plan).slides[1]
    facts = (
        "# Practice\n"
        "- **F1 Review.** Pilots repeat and measure every flight review\n\n"
        "- **F2 Count.** Crews logged 40 sorties\n\n"
        + "Unrelated filler sentence about gardening. " * 200
    )
    picked = select_relevant_facts(facts, slide, budget=90)
    assert "F2 Count" in picked
    assert "F1 Review" not in picked


def test_select_relevant_facts_short_file_is_whole() -> None:
    slide = parse_plan(PLAN).slides[1]
    assert select_relevant_facts("- tiny fact", slide) == "- tiny fact"


def test_select_relevant_facts_falls_back_to_head() -> None:
    slide = parse_plan(PLAN).slides[1]
    facts = "zzz qqq " * 1000
    picked = select_relevant_facts(facts, slide, budget=200)
    assert picked.startswith("zzz qqq")
    assert len(picked) <= 200


def test_user_prompt_includes_neighbor_points() -> None:
    document = parse_plan(PLAN)
    prompt = build_user_prompt(document, document.slides[1], idea="", facts="")
    assert "# NEIGHBOURS" in prompt
    assert "Previous: Slide 1, Start Here (role: cover)" in prompt
    assert "  - The premise" in prompt
    assert "Next:" not in prompt


@pytest.mark.asyncio
async def test_page_filter_with_no_matching_slides_raises(tmp_path: Path) -> None:
    document = parse_plan(PLAN)
    client = _client([CONTENT_BODY])
    with pytest.raises(ValueError, match="No plan slides match"):
        await write_script(
            client,
            document,
            idea="",
            facts="",
            standards="standards",
            prompt_dir=tmp_path,
            page_filter={9},
            existing_script="# PPT Outline: Loop\n",
        )
    client.complete_text_parallel.assert_not_called()


@pytest.mark.asyncio
async def test_page_filter_without_script_raises(tmp_path: Path) -> None:
    document = parse_plan(PLAN)
    client = _client([CONTENT_BODY])
    with pytest.raises(ValueError, match="existing script"):
        await write_script(
            client,
            document,
            idea="",
            facts="",
            standards="standards",
            prompt_dir=tmp_path,
            page_filter={2},
        )
