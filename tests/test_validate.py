"""Tests for script validation and visual/text balance."""

from __future__ import annotations

import pytest

from src.core.validate import (
    balance_warnings,
    count_transition_slides,
    count_words,
    load_outline_standards,
    measure_slide_balance,
    speech_warnings,
    strip_code_fences,
    validate_outline,
)

VALID_OUTLINE = """# PPT Outline: Test Deck

---

## Slide 1: Introduction
- **Hook:** Why this matters
- Core insight: One clear takeaway
[Visual: Hero image with title left]
[Speech: Welcome everyone.]

---

## Slide 2: Roadmap: Section One
- **Where we are:** First act
[Visual: Five-chip roadmap, section one highlighted, progress bar 2/6 lower right]
[Speech: First section.]

---

## Slide 3: Roadmap: Section Two
- **Where we are:** Second act
[Visual: Same roadmap, section two highlighted, progress bar 3/6 lower right]
[Speech: Second section.]

---

## Slide 4: Roadmap: Section Three
- **Where we are:** Third act
[Visual: Same roadmap, section three highlighted, progress bar 4/6 lower right]
[Speech: Third section.]

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

    def test_too_few_transition_slides_warns(self) -> None:
        outline = (
            "# PPT Outline: Tiny\n\n---\n\n"
            "## Slide 1: Intro\n[Visual: x]\n[Speech: y]\n\n---\n\n"
            "## Appendix: Global Visual Requirements\n- **Theme:** Dark\n"
        )
        result = validate_outline(outline)
        assert any("transition slide" in w for w in result.warnings)

    def test_too_many_transition_slides_warns(self) -> None:
        blocks = ["# PPT Outline: Big\n"]
        for i in range(1, 8):
            blocks.append(
                f"---\n\n## Slide {i}: Roadmap: Section {i}\n"
                f"[Visual: roadmap progress bar {i}/7]\n[Speech: z]\n"
            )
        blocks.append("---\n\n## Appendix: Global Visual Requirements\n- **Theme:** Dark\n")
        outline = "\n".join(blocks)
        result = validate_outline(outline)
        assert any("transition slide" in w for w in result.warnings)


def _three_slide_deck(
    content_bullets: str = "- **Point:** one two three four five six seven eight nine ten",
    content_visual: str = "one two three four five six seven eight nine. Slide number: 2",
    cover_visual: str = "dark curtain cover",
) -> str:
    return (
        "# PPT Outline: X\n\n---\n\n"
        f"## Slide 1: Open\n- a\n[Visual: {cover_visual}]\n[Speech: s]\n\n---\n\n"
        f"## Slide 2: Teach\n{content_bullets}\n[Visual: {content_visual}]\n[Speech: s]\n\n---\n\n"
        "## Slide 3: Thank You\n- c\n[Visual: dark]\n[Speech: s]\n\n---\n\n"
        "## Appendix: Global Visual Requirements\n- **Theme:** x\n"
    )


def _page_warnings(outline: str) -> list[str]:
    return [w for w in validate_outline(outline).warnings if "lide number" in w]


class TestPageNumbers:
    def test_content_page_number_without_total_passes(self) -> None:
        assert _page_warnings(_three_slide_deck()) == []

    @pytest.mark.parametrize(
        "visual",
        ["panel. Slide number: 2/3", "panel. Slide number: 2 of 3", "panel. Slide number: 5", "panel"],
    )
    def test_content_page_number_must_be_own_page_without_total(self, visual: str) -> None:
        warnings = _page_warnings(_three_slide_deck(content_visual=visual))
        assert len(warnings) == 1
        assert "Slide 2" in warnings[0]

    def test_cover_must_not_show_a_page_number(self) -> None:
        warnings = _page_warnings(_three_slide_deck(cover_visual="dark. Slide number: 1"))
        assert warnings == ["## Slide 1: cover slide should not show a slide number."]


class TestBalanceWarnings:
    def test_balanced_content_slide_passes(self) -> None:
        warnings = balance_warnings(_three_slide_deck())
        assert not any("Slide 2" in w for w in warnings)

    def test_mainly_text_slide_warns(self) -> None:
        outline = _three_slide_deck(content_visual="tiny. Slide number: 2")
        assert any("Slide 2" in w and "mainly text" in w for w in balance_warnings(outline))

    def test_mainly_visual_slide_warns(self) -> None:
        outline = _three_slide_deck(content_bullets="- **A:** one")
        assert any("Slide 2" in w and "mainly visual" in w for w in balance_warnings(outline))

    def test_visual_led_cover_has_no_ratio_floor(self) -> None:
        outline = _three_slide_deck(cover_visual="dark curtain " * 40)
        assert not any("Slide 1" in w for w in balance_warnings(outline))

    def test_text_heavy_cover_warns(self) -> None:
        outline = _three_slide_deck(cover_visual="dark")
        outline = outline.replace("## Slide 1: Open\n- a\n", "## Slide 1: Open\n- a b c\n")
        warnings = [w for w in balance_warnings(outline) if "Slide 1" in w]
        assert len(warnings) == 1
        assert "text outweighs visual on a cover slide" in warnings[0]

    def test_non_content_ratio_of_one_warns(self) -> None:
        outline = _three_slide_deck(cover_visual="dark")
        assert any("Slide 1" in w and "ratio 1.00" in w for w in balance_warnings(outline))


class TestMeasureSlideBalance:
    def test_measures_every_slide_but_not_the_appendix(self) -> None:
        rows = measure_slide_balance(VALID_OUTLINE)
        assert len(rows) == 4
        assert rows[0].title == "Slide 1: Introduction"

    def test_counts_bullet_and_visual_words(self) -> None:
        first = measure_slide_balance(VALID_OUTLINE)[0]
        assert first.bullets == 2
        assert first.text_words == 9
        assert first.visual_words == 5
        assert first.ratio == pytest.approx(1.8)

    def test_separator_lines_are_not_bullets(self) -> None:
        outline = "# PPT Outline: X\n\n---\n\n## Slide 1: Title\n- **A:** one\n[Speech: y]\n\n---\n"
        assert measure_slide_balance(outline)[0].bullets == 1

    def test_excludes_speech_and_reference_text(self) -> None:
        outline = (
            "# PPT Outline: Refs\n\n---\n\n"
            "## Slide 1: Title\n- **A:** one two\n"
            "[Reference: work/a.png]\n[Visual: three four five]\n"
            "[Speech: this narration is not counted at all]\n"
        )
        row = measure_slide_balance(outline)[0]
        assert row.bullets == 1
        assert row.text_words == 3
        assert row.visual_words == 3

    def test_missing_visual_tag_yields_zero_ratio(self) -> None:
        outline = "# PPT Outline: X\n\n---\n\n## Slide 1: Title\n- **A:** one\n[Speech: y]\n"
        assert measure_slide_balance(outline)[0].ratio == 0.0


def _speech_deck(content_speech: str, cover_speech: str) -> str:
    return (
        "# PPT Outline: X\n\n---\n\n"
        f"## Slide 1: Open\n- a\n[Visual: dark curtain cover]\n[Speech: {cover_speech}]\n\n---\n\n"
        "## Slide 2: Teach\n- **A:** one\n[Visual: panel. Slide number: 2]\n"
        f"[Speech: {content_speech}]\n\n---\n\n"
        "## Slide 3: Thank You\n- c\n[Visual: dark]\n[Speech: " + "word " * 75 + "]\n\n---\n\n"
        "## Appendix: Global Visual Requirements\n- **Theme:** x\n"
    )


class TestSpeechLength:
    def test_speech_seconds_excludes_separator_and_bracket(self) -> None:
        rows = measure_slide_balance(_speech_deck("word " * 250, "word " * 75))
        assert rows[1].speech_words == 250
        assert rows[1].speech_seconds == pytest.approx(100.0)

    def test_chinese_speech_counts_characters_at_half_a_word(self) -> None:
        rows = measure_slide_balance(_speech_deck("训练" * 200, "word " * 75))
        assert rows[1].speech_seconds == pytest.approx(80.0)

    def test_speech_in_range_passes(self) -> None:
        assert speech_warnings(_speech_deck("word " * 250, "word " * 75)) == []

    def test_short_content_speech_warns(self) -> None:
        warnings = speech_warnings(_speech_deck("word " * 100, "word " * 75))
        assert len(warnings) == 1
        assert "Slide 2" in warnings[0] and "speech runs short" in warnings[0]

    def test_long_content_speech_warns(self) -> None:
        warnings = speech_warnings(_speech_deck("word " * 400, "word " * 75))
        assert len(warnings) == 1
        assert "Slide 2" in warnings[0] and "speech runs long" in warnings[0]

    def test_long_cover_speech_warns(self) -> None:
        warnings = speech_warnings(_speech_deck("word " * 250, "word " * 150))
        assert len(warnings) == 1
        assert "Slide 1" in warnings[0] and "cover slide" in warnings[0]


class TestCountTransitionSlides:
    def test_counts_roadmap_titles_and_progress_markers(self) -> None:
        assert count_transition_slides(VALID_OUTLINE) == 3

    def test_detects_progress_marker_without_roadmap_title(self) -> None:
        outline = (
            "# PPT Outline: X\n\n---\n\n"
            "## Slide 1: Where We Are\n[Visual: chips, progress bar 1/4]\n[Speech: a]\n"
        )
        assert count_transition_slides(outline) == 1


class TestStripCodeFences:
    def test_removes_wrapping_fences(self) -> None:
        text = "```markdown\n# PPT Outline: X\n```"
        assert strip_code_fences(text).startswith("# PPT Outline:")


def test_load_outline_standards_from_repo() -> None:
    text = load_outline_standards()
    assert "Outline Standards" in text


def test_count_words_treats_cjk_as_half_a_word() -> None:
    assert count_words("one two") == 2
    assert count_words("训练回路") == 2
    assert count_words("训练 two") == 2
