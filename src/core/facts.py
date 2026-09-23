"""Fact IDs shared by the plan and write stages.

``facts.md`` defines one fact per bullet as ``- **F3 Name.** fact — citation``;
plan ``Evidence:`` lines cite those IDs (``- Evidence: F3, F7``).
"""

from __future__ import annotations

import re
from collections.abc import Iterable

FACT_DEFINITION_PATTERN = re.compile(r"^\s*[-*]\s+\*\*(F\d+)\b", re.MULTILINE)
FACT_CITATION_PATTERN = re.compile(r"\bF\d+\b")


def defined_fact_ids(facts: str) -> list[str]:
    """IDs defined in *facts*, in file order (duplicates kept)."""
    return FACT_DEFINITION_PATTERN.findall(facts)


def fact_id_of(chunk: str) -> str | None:
    """The ID a single fact bullet defines, or None."""
    match = FACT_DEFINITION_PATTERN.match(chunk)
    return match.group(1) if match else None


def cited_fact_ids(evidence: Iterable[str]) -> list[str]:
    """Unique fact IDs cited across *evidence* lines, in first-seen order."""
    seen: dict[str, None] = {}
    for line in evidence:
        for fact_id in FACT_CITATION_PATTERN.findall(line):
            seen.setdefault(fact_id, None)
    return list(seen)
