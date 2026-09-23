"""Deck plan validation. Plans are written by the plan-deck skill, not by an API."""

from src.plan.parse import PlanDocument, PlanSlide, parse_plan
from src.plan.validate import content_slide_count, validate_plan

__all__ = [
    "PlanDocument",
    "PlanSlide",
    "content_slide_count",
    "parse_plan",
    "validate_plan",
]
