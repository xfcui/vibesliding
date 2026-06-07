"""Outline pipeline: research -> presentation outline markdown."""

from src.outline.parser import Slide, extract_global_style, parse_markdown
from src.outline.writer import (
    OutlineValidation,
    write_outline,
    write_outlines_parallel,
    write_style_scaffold,
)

__all__ = [
    "Slide",
    "extract_global_style",
    "parse_markdown",
    "OutlineValidation",
    "write_outline",
    "write_outlines_parallel",
    "write_style_scaffold",
]
