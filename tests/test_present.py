"""Tests for narrated video segment collection and ffmpeg muxing."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from src.present.mux import (
    FfmpegNotFoundError,
    build_presentation_video,
    concat_video_segments,
    require_ffmpeg,
    render_slide_segment,
)
from src.present.segments import (
    audio_path_for_image,
    collect_slide_segments,
)


OUTLINE = """# Deck

---

## Slide 1: Cover
[Speech: Welcome everyone.]

---

## Slide 2: Body
[Speech: Here is the main point.]
"""


def test_audio_path_for_image() -> None:
    assert audio_path_for_image(Path("slide_p01_v01.png")) == Path("slide_p01_v01.mp3")


def test_collect_slide_segments(tmp_path: Path) -> None:
    Image.new("RGB", (64, 36), color="red").save(tmp_path / "slide_p01_v01.png")
    Image.new("RGB", (64, 36), color="blue").save(tmp_path / "slide_p02_v01.png")

    segments = collect_slide_segments(tmp_path, OUTLINE)
    assert len(segments) == 2
    assert segments[0].slide_number == 1
    assert segments[0].speech_text == "Welcome everyone."
    assert segments[1].speech_text == "Here is the main point."


def test_collect_slide_segments_page_filter(tmp_path: Path) -> None:
    Image.new("RGB", (64, 36), color="red").save(tmp_path / "slide_p01_v01.png")
    Image.new("RGB", (64, 36), color="blue").save(tmp_path / "slide_p02_v01.png")

    segments = collect_slide_segments(tmp_path, OUTLINE, page_filter={2})
    assert len(segments) == 1
    assert segments[0].slide_number == 2


def test_require_ffmpeg_missing() -> None:
    with patch("src.present.mux.shutil.which", return_value=None):
        with patch("src.present.mux.resolve_ffmpeg", side_effect=FfmpegNotFoundError("ffmpeg")):
            with pytest.raises(FfmpegNotFoundError, match="ffmpeg"):
                require_ffmpeg()


def test_render_slide_segment_invokes_ffmpeg(tmp_path: Path) -> None:
    image_path = tmp_path / "slide.png"
    Image.new("RGB", (64, 36), color="green").save(image_path)
    output_path = tmp_path / "segment.mp4"

    with patch("src.present.mux.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        render_slide_segment(
            "ffmpeg",
            image_path=image_path,
            audio_path=None,
            silent_seconds=2.5,
            output_path=output_path,
        )

    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "ffmpeg"
    assert "-t" in cmd
    assert "2.500" in cmd
    assert "anullsrc" in "".join(cmd)


def test_concat_video_segments_invokes_ffmpeg(tmp_path: Path) -> None:
    seg1 = tmp_path / "seg1.mp4"
    seg2 = tmp_path / "seg2.mp4"
    seg1.write_bytes(b"fake")
    seg2.write_bytes(b"fake")
    output_path = tmp_path / "out.mp4"

    with patch("src.present.mux.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        concat_video_segments("ffmpeg", [seg1, seg2], output_path)

    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "ffmpeg"
    assert "-f" in cmd
    assert "concat" in cmd


def test_build_presentation_video(tmp_path: Path) -> None:
    image_path = tmp_path / "slide_p01_v01.png"
    Image.new("RGB", (64, 36), color="red").save(image_path)
    segments = collect_slide_segments(tmp_path, OUTLINE, page_filter={1})
    output_path = tmp_path / "deck.mp4"

    with (
        patch("src.present.mux.resolve_ffmpeg", return_value="ffmpeg"),
        patch("src.present.mux.render_slide_segment") as mock_render,
        patch("src.present.mux.concat_video_segments") as mock_concat,
    ):
        count = build_presentation_video(segments, output_path, silent_seconds=3.0)

    assert count == 1
    assert mock_render.call_count == 1
    mock_concat.assert_called_once()
