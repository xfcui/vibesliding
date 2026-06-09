"""Style reference generation: outline → cover/transition/content PNGs."""

from src.style.refs import (
    STYLE_BASE_FILENAME,
    STYLE_CONTENT_FILENAME,
    STYLE_COVER_FILENAME,
    STYLE_TRANSITION_FILENAME,
    StyleRefJob,
    StyleSelectFn,
    build_style_ref_jobs,
    extract_presentation_title,
    generate_style_references,
)

__all__ = [
    "STYLE_BASE_FILENAME",
    "STYLE_CONTENT_FILENAME",
    "STYLE_COVER_FILENAME",
    "STYLE_TRANSITION_FILENAME",
    "StyleRefJob",
    "StyleSelectFn",
    "build_style_ref_jobs",
    "extract_presentation_title",
    "generate_style_references",
]
