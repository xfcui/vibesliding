"""Tests for plan validation."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from src.plan.cli import content_count_from_name, main
from src.plan.validate import content_slide_count, validate_plan
from src.plan.parse import parse_plan

PLAN = """# PPT Outline: Loop

---

## Slide 1: Open
- Role: cover
- Point: The stakes
- Point: The promise
- Visual hook: dark title

---

## Slide 2: Roadmap: See It
- Role: transition
- Section: 1/3
- Point: Act one
- Point: Act two
- Visual hook: roadmap chips, progress bar 1/3

---

## Slide 3: Roadmap: Try It
- Role: transition
- Section: 2/3
- Point: Act two
- Point: Act three
- Visual hook: roadmap chips, progress bar 2/3

---

## Slide 4: Roadmap: Keep It
- Role: transition
- Section: 3/3
- Point: Act three
- Point: Close
- Visual hook: roadmap chips, progress bar 3/3

---

## Slide 5: Practice The Loop
- Role: content
- Section: 3/3
- Point: One pass
- Point: Then another
- Evidence: F1
- Visual hook: two columns
[Style: style_content.png]

---

## Appendix: Global Visual Requirements
- **Theme:** Light content, dark curtain
"""


def test_validate_plan_accepts_a_small_deck() -> None:
    assert validate_plan(PLAN).ok
    document = parse_plan(PLAN)
    assert content_slide_count(document) == 1
    assert document.slides[4].style_tag == "[Style: style_content.png]"


def test_validate_plan_flags_duplicate_visual_hooks() -> None:
    plan = PLAN.replace("- Visual hook: two columns", "- Visual hook: two columns\n- Visual hook: a chart")
    assert any("2 Visual hook lines" in w for w in validate_plan(plan).warnings)


def test_validate_plan_flags_sections_that_disagree_with_the_roadmap() -> None:
    plan = PLAN.replace("- Section: 2/3", "- Section: 2/4").replace(
        "- Role: content\n- Section: 3/3", "- Role: content\n- Section: 1/3"
    )
    warnings = validate_plan(plan).warnings
    assert any("Slide 3: Section 2/4" in w and "expected 2/3" in w for w in warnings)
    assert any("Slide 5: Section 1/3" in w and "expected 3/3" in w for w in warnings)


FACTS = "## Practice\n\n- **F1 Flights.** Pilots logged 9 flights. — logbook\n"


def test_validate_plan_checks_evidence_against_facts() -> None:
    assert validate_plan(PLAN, FACTS).ok
    plan = PLAN.replace("- Evidence: F1", "- Evidence: F1, F9")
    assert any(
        "Slide 5: Evidence cites F9" in w for w in validate_plan(plan, FACTS).warnings
    )
    duplicated = FACTS + "- **F1 Again.** Same ID. — notes\n"
    assert any("defines F1 2 times" in w for w in validate_plan(PLAN, duplicated).warnings)
    assert any("no fact IDs" in w for w in validate_plan(PLAN, "- loose note").warnings)


def test_validate_plan_flags_content_slide_without_evidence() -> None:
    plan = PLAN.replace("- Evidence: F1\n", "")
    assert any(
        "Slide 5: missing '- Evidence:'" in w for w in validate_plan(plan).warnings
    )


def test_plan_cli_reports_counts(tmp_path: Path) -> None:
    path = tmp_path / "plan_1.md"
    path.write_text(PLAN, encoding="utf-8")
    (tmp_path / "facts.md").write_text(FACTS, encoding="utf-8")
    result = CliRunner().invoke(main, ["--plan", str(path)])
    assert result.exit_code == 0, result.output
    assert "Content slides: 1" in result.output
    assert "Sections: 3" in result.output
    assert "Facts:" in result.output
    assert "structurally sound" in result.output


def test_plan_cli_warns_without_facts(tmp_path: Path) -> None:
    path = tmp_path / "plan_1.md"
    path.write_text(PLAN, encoding="utf-8")
    result = CliRunner().invoke(main, ["--plan", str(path)])
    assert result.exit_code == 0, result.output
    assert "Facts file not found" in result.output
    assert "structurally sound" not in result.output


def test_content_count_from_name() -> None:
    assert content_count_from_name(Path("work/plan_16.md")) == 16
    assert content_count_from_name(Path("work/plan.md")) is None
    assert content_count_from_name(Path("work/plan_v2.md")) is None


def test_plan_cli_notes_filename_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "plan_16.md"
    path.write_text(PLAN, encoding="utf-8")
    (tmp_path / "facts.md").write_text(FACTS, encoding="utf-8")
    result = CliRunner().invoke(main, ["--plan", str(path)])
    assert result.exit_code == 0, result.output
    assert "filename asks for 16 content slides; plan has 1" in result.output


def test_plan_cli_missing_plan(tmp_path: Path) -> None:
    result = CliRunner().invoke(main, ["--plan", str(tmp_path / "plan_1.md")])
    assert result.exit_code != 0
    assert "Plan file not found" in result.output
