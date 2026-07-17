"""Render pipeline: style references + outline → slide images and PDF."""

from src.render.gen import SlideImageGenerator
from src.render.style.refs import (
    STYLE_BASE_CONTENT_FILENAME,
    STYLE_BASE_NONCONTENT_FILENAME,
    STYLE_CONTENT_FILENAME,
    STYLE_COVER_FILENAME,
    STYLE_TRANSITION_FILENAME,
    StyleRefJob,
    StyleSelectFn,
    build_style_ref_jobs,
    extract_presentation_title,
    generate_style_references,
    select_style_paths_for_role,
)

__all__ = [
    "SlideImageGenerator",
    "STYLE_BASE_CONTENT_FILENAME",
    "STYLE_BASE_NONCONTENT_FILENAME",
    "STYLE_CONTENT_FILENAME",
    "STYLE_COVER_FILENAME",
    "STYLE_TRANSITION_FILENAME",
    "StyleRefJob",
    "StyleSelectFn",
    "build_style_ref_jobs",
    "extract_presentation_title",
    "generate_style_references",
    "select_style_paths_for_role",
]
