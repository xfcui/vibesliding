"""Pair slide images with outline speech text for narrated video export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.core.export import (
    _slide_number_from_path,
    collect_slide_image_paths,
    slides_by_index_from_outline,
)
from src.outline.parser import extract_speech_text


@dataclass(frozen=True)
class SlideSegment:
    """One slide image paired with optional speech and its audio path."""

    slide_number: int
    image_path: Path
    speech_text: str | None
    audio_path: Path

    @property
    def has_speech(self) -> bool:
        return bool(self.speech_text and self.speech_text.strip())


def audio_path_for_image(image_path: Path) -> Path:
    """Return the MP3 path that corresponds to a slide PNG."""
    return image_path.with_suffix(".mp3")


def collect_slide_segments(
    image_dir: Path,
    outline_text: str,
    *,
    page_filter: set[int] | None = None,
    variant_filter: set[int] | None = None,
) -> list[SlideSegment]:
    """Collect slide segments in deck order with speech from the outline."""
    image_paths = collect_slide_image_paths(
        image_dir,
        page_filter=page_filter,
        variant_filter=variant_filter,
    )
    slides_by_index = slides_by_index_from_outline(outline_text)
    segments: list[SlideSegment] = []

    for image_path in image_paths:
        slide_number = _slide_number_from_path(image_path)
        if slide_number is None:
            continue
        slide = slides_by_index.get(slide_number)
        speech = (
            extract_speech_text(slide.content)
            if slide is not None
            else None
        )
        segments.append(
            SlideSegment(
                slide_number=slide_number,
                image_path=image_path,
                speech_text=speech,
                audio_path=audio_path_for_image(image_path),
            )
        )

    if not segments:
        raise ValueError("No slide segments to narrate")

    return segments
