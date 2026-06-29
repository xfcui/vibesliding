"""Present pipeline: slide PNGs + outline speech tags → narrated MP4."""

from src.present.segments import SlideSegment, collect_slide_segments

__all__ = ["SlideSegment", "collect_slide_segments"]
