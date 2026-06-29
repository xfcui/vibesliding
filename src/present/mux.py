"""Assemble slide images and audio into a narrated MP4 via ffmpeg."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from src.present.segments import SlideSegment


class FfmpegNotFoundError(RuntimeError):
    """Raised when ffmpeg or ffprobe is not available on PATH."""


def resolve_ffmpeg() -> str:
    """Return an ``ffmpeg`` executable from PATH or imageio-ffmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    raise FfmpegNotFoundError(
        "ffmpeg is required for narrated video export. "
        "Install ffmpeg (https://ffmpeg.org/download.html) or "
        "pip install imageio-ffmpeg."
    )


def require_ffmpeg() -> tuple[str, str]:
    """Return ``(ffmpeg, ffprobe)`` executables or raise."""
    ffmpeg = resolve_ffmpeg()
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise FfmpegNotFoundError(
            "ffprobe is required when probing audio duration. "
            "Install ffmpeg (https://ffmpeg.org/download.html)."
        )
    return ffmpeg, ffprobe


def probe_audio_duration(ffprobe: str, audio_path: Path) -> float:
    """Return audio duration in seconds."""
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    duration = float(result.stdout.strip())
    if duration <= 0:
        raise ValueError(f"Invalid audio duration for {audio_path}: {duration}")
    return duration


def render_slide_segment(
    ffmpeg: str,
    *,
    image_path: Path,
    audio_path: Path | None,
    silent_seconds: float,
    output_path: Path,
) -> None:
    """Render one still-image slide segment to MP4."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # We want a completely uniform video and audio track across all segments
    # to avoid corruption, gaps, and desync when copy-concatenating.
    # Video: libx264, 25 fps, yuv420p, scaled.
    # Audio: aac, stereo (2 channels), 44100 Hz, 192k.
    
    if audio_path is not None and audio_path.is_file():
        cmd: list[str] = [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-r",
            "25",
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-shortest",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ac",
            "2",
            "-ar",
            "44100",
            str(output_path),
        ]
    else:
        # Silent slide: generate a silent audio track of identical format
        # to ensure perfect concatenation stream matching.
        cmd = [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-r",
            "25",
            "-i",
            str(image_path),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-t",
            f"{silent_seconds:.3f}",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_path),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            f"ffmpeg failed for slide {image_path.name}"
            + (f": {stderr}" if stderr else "")
        )


def concat_video_segments(ffmpeg: str, segment_paths: list[Path], output_path: Path) -> None:
    """Concatenate rendered slide segments into one MP4."""
    if not segment_paths:
        raise ValueError("At least one video segment is required")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    ) as list_file:
        for segment_path in segment_paths:
            escaped = str(segment_path.resolve()).replace("'", "'\\''")
            list_file.write(f"file '{escaped}'\n")
        list_path = Path(list_file.name)

    try:
        result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c",
                "copy",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )
    finally:
        list_path.unlink(missing_ok=True)

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            "ffmpeg concat failed"
            + (f": {stderr}" if stderr else "")
        )


def build_presentation_video(
    segments: list[SlideSegment],
    output_path: Path,
    *,
    silent_seconds: float = 3.0,
) -> int:
    """Mux slide segments into a single narrated MP4.

    Each segment uses ``segment.audio_path`` when that file exists; otherwise
    the slide is shown for ``silent_seconds`` with no audio track.
    """
    if not segments:
        raise ValueError("At least one slide segment is required")

    ffmpeg = resolve_ffmpeg()
    rendered: list[Path] = []

    with tempfile.TemporaryDirectory(prefix="vibesliding_present_") as tmp_dir:
        tmp = Path(tmp_dir)
        for index, segment in enumerate(segments):
            segment_path = tmp / f"segment_{index:04d}.mp4"
            audio_path = (
                segment.audio_path
                if segment.audio_path.is_file()
                else None
            )
            render_slide_segment(
                ffmpeg,
                image_path=segment.image_path,
                audio_path=audio_path,
                silent_seconds=silent_seconds,
                output_path=segment_path,
            )
            rendered.append(segment_path)

        concat_video_segments(ffmpeg, rendered, output_path)

    return len(segments)
