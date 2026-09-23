"""Validation for deck plans written by the plan-deck skill."""

from __future__ import annotations

from collections import Counter

from src.core.facts import cited_fact_ids, defined_fact_ids
from src.core.validate import (
    MAX_TRANSITION_SLIDES,
    MIN_TRANSITION_SLIDES,
    OutlineValidation,
    SLIDE_HEADER_PATTERN,
)
from src.plan.parse import PLAN_ROLES, PlanDocument, parse_plan

CONTENT_ROLES = frozenset({"hook", "content", "cta"})


def validate_plan(text: str, facts: str | None = None) -> OutlineValidation:
    """Warn on missing plan structure; do not hard-fail.

    With *facts* (the text of ``facts.md``), also check that every cited
    ``Evidence:`` ID is defined there.
    """
    warnings: list[str] = []
    stripped = text.strip()
    if not stripped.startswith("# PPT Outline:"):
        warnings.append("Plan should start with '# PPT Outline: [Title]'.")
    if "## Appendix" not in stripped and "Appendix: Global Visual Requirements" not in stripped:
        warnings.append("Plan is missing '## Appendix: Global Visual Requirements'.")

    if not SLIDE_HEADER_PATTERN.search(stripped):
        warnings.append("No '## Slide N:' headers found.")
        return OutlineValidation(warnings=warnings)

    document = parse_plan(text)
    transitions = 0
    for slide in document.slides:
        label = f"## Slide {slide.index}:"
        if slide.role is None:
            warnings.append(f"{label} missing '- Role:' line.")
        elif slide.role == "transition":
            transitions += 1
            if not slide.title.lower().startswith("roadmap:"):
                warnings.append(f"{label} transition title should start with 'Roadmap:'.")
        if slide.role == "transition" and not slide.section:
            warnings.append(f"{label} missing '- Section: k/total' line.")
        if not 2 <= len(slide.points) <= 4:
            warnings.append(
                f"{label} has {len(slide.points)} Point line(s); expected 2-4."
            )
        if not slide.visual_hook:
            warnings.append(f"{label} missing '- Visual hook:' line.")
        elif slide.visual_hook_count > 1:
            warnings.append(
                f"{label} has {slide.visual_hook_count} Visual hook lines; expected exactly 1."
            )
        if slide.role in CONTENT_ROLES and not slide.evidence:
            warnings.append(f"{label} missing '- Evidence:' line citing facts.md.")

    if transitions < MIN_TRANSITION_SLIDES or transitions > MAX_TRANSITION_SLIDES:
        warnings.append(
            f"Plan has {transitions} transition slide(s); expected "
            f"{MIN_TRANSITION_SLIDES}-{MAX_TRANSITION_SLIDES}."
        )
    warnings.extend(section_warnings(document))
    if facts is not None:
        warnings.extend(evidence_warnings(document, facts))
    return OutlineValidation(warnings=warnings)


def evidence_warnings(document: PlanDocument, facts: str) -> list[str]:
    """Check that ``Evidence:`` fact IDs exist in *facts* and that IDs are unique."""
    defined = defined_fact_ids(facts)
    if not defined:
        return ["facts.md defines no fact IDs; write each fact as '- **F1 Name.** ...'."]
    warnings = [
        f"facts.md defines {fact_id} {count} times."
        for fact_id, count in Counter(defined).items()
        if count > 1
    ]
    known = set(defined)
    for slide in document.slides:
        missing = [fact_id for fact_id in cited_fact_ids(slide.evidence) if fact_id not in known]
        if missing:
            warnings.append(
                f"## Slide {slide.index}: Evidence cites {', '.join(missing)}, "
                "not defined in facts.md."
            )
    return warnings


def section_warnings(document: PlanDocument) -> list[str]:
    """Check that ``Section: k/total`` lines agree with the roadmap order.

    Transitions count 1..total with total equal to the number of transitions;
    any other slide that names a section must name the one it sits in.
    """
    warnings: list[str] = []
    total = section_count(document)
    current = 0
    for slide in document.slides:
        if slide.role == "transition":
            current += 1
        if not slide.section:
            continue
        number, _, declared_total = slide.section.partition("/")
        if int(number) != current or int(declared_total) != total:
            warnings.append(
                f"## Slide {slide.index}: Section {slide.section} does not match the "
                f"roadmap (expected {current}/{total})."
            )
    return warnings


def plan_counts(document: PlanDocument) -> Counter[str]:
    """Count slides by role. Missing roles are counted as 'unknown'."""
    counts: Counter[str] = Counter()
    for slide in document.slides:
        counts[slide.role or "unknown"] += 1
    return counts


def content_slide_count(document: PlanDocument) -> int:
    """Hook, teaching, and call-to-action slides. Cover, transition, and ending are extra."""
    return sum(1 for slide in document.slides if slide.role in CONTENT_ROLES)


def section_count(document: PlanDocument) -> int:
    return sum(1 for slide in document.slides if slide.role == "transition")


def format_plan_report(document: PlanDocument) -> list[str]:
    """Human-readable role, section, and content counts."""
    counts = plan_counts(document)
    role_bits = [
        f"{role} {counts[role]}"
        for role in (*PLAN_ROLES, "unknown")
        if counts[role]
    ]
    return [
        f"Slides: {len(document.slides)}",
        f"Content slides: {content_slide_count(document)}",
        f"Sections: {section_count(document)}",
        "Roles: " + (", ".join(role_bits) if role_bits else "none"),
    ]
