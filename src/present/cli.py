"""CLI entry point for narrated video export (`python -m src.present.cli`)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click
from click.core import ParameterSource
from dotenv import load_dotenv

from src.render.cli import parse_page_spec
from src.core.config import (
    DEFAULT_MINIMAX_TTS_MODEL,
    DEFAULT_MINIMAX_TTS_VOICE,
    load_minimax_tts_config,
)
from src.core.paths import (
    DEFAULT_SCRIPT_PATH,
    DEFAULT_WORK_DIR,
    presentation_video_path,
    read_nonempty_text,
    timestamp_from_image_dir,
    timestamp_slug,
)
from src.present.mux import build_presentation_video
from src.present.segments import collect_slide_segments

load_dotenv()


def _parse_page_spec_or_usage(page: str | None) -> set[int] | None:
    try:
        return parse_page_spec(page)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc


def _snapshot_scripts(image_dir: Path) -> list[Path]:
    """Prefer ``script_*.md`` snapshots, else ``outline_*.md``, oldest first."""
    scripts = list(image_dir.glob("script_*.md"))
    pool = scripts or list(image_dir.glob("outline_*.md"))
    return sorted(pool, key=lambda path: (path.stat().st_mtime, path.name))


def _resolve_script_path(
    image_dir: Path,
    script_path: Path,
    *,
    explicit: bool,
) -> Path:
    if script_path.is_file():
        return script_path
    if explicit:
        raise click.UsageError(f"Script not found: {script_path.resolve()}")

    snapshots = _snapshot_scripts(image_dir)
    if not snapshots:
        raise click.UsageError(
            f"Script not found: {script_path.resolve()}. "
            "Pass --script or ensure the render output directory contains a script snapshot."
        )
    chosen = snapshots[-1]
    click.echo(
        f"Script not found: {script_path.resolve()}. Using {chosen.resolve()}",
        err=True,
    )
    return chosen


async def _synthesize_speech(
    segments: list,
    *,
    reference_audio: Path | None,
    voice_id: str | None,
    api_key_override: str | None,
    tts_model_override: str | None,
    tts_voice_override: str | None,
) -> None:
    """Run TTS via MiniMax (Chinese-native, with optional voice cloning)."""
    from src.core.minimax_tts import (
        setup_cloned_voice,
        synthesize_speech_parallel,
    )

    config = load_minimax_tts_config(
        api_key_override=api_key_override,
        tts_model_override=tts_model_override,
        tts_voice_override=tts_voice_override,
    )
    if not config.api_key:
        raise RuntimeError(
            "MiniMax API key is required. Set MINIMAX_API_KEY, "
            "[minimax] api_key in .env, or pass --api-key."
        )

    voice_id_to_use: str | None = voice_id
    if reference_audio is not None:
        click.echo("Cloning voice via MiniMax...")
        voice_id_to_use = await setup_cloned_voice(config, reference_audio)
        click.echo(f"Voice cloned: {voice_id_to_use}")

    selected_voice = voice_id_to_use or config.tts_voice
    click.echo(f"Using TTS model: {config.tts_model}, voice: {selected_voice}")

    pending = [
        (index, segment)
        for index, segment in enumerate(segments)
        if segment.has_speech and not segment.audio_path.is_file()
    ]
    if not pending:
        return

    texts = [segment.speech_text or "" for _, segment in pending]
    results = await synthesize_speech_parallel(
        config,
        texts,
        voice_id=voice_id_to_use,
        desc="Speech synthesis",
    )
    if len(pending) != len(results):
        raise RuntimeError(
            f"TTS result count mismatch: {len(results)} results for {len(pending)} slides"
        )
    for (_index, segment), result in zip(pending, results):
        if isinstance(result, Exception):
            raise RuntimeError(
                f"TTS failed for slide {segment.slide_number}: {result}"
            ) from result
        segment.audio_path.write_bytes(result)


def _run_narrate(
    *,
    image_dir: Path,
    work_dir: Path,
    script_path: Path,
    script_explicit: bool,
    page: str | None,
    variant: str | None,
    api_key: str | None,
    tts_model: str,
    voice: str,
    reference_audio: Path | None,
    voice_id: str | None,
    mux_only: bool,
    silent_seconds: float,
) -> None:
    if silent_seconds <= 0:
        raise click.UsageError("--silent-seconds must be greater than 0.")

    if not image_dir.is_dir():
        raise click.UsageError(f"Image directory not found: {image_dir.resolve()}")

    resolved_script = _resolve_script_path(
        image_dir, script_path, explicit=script_explicit
    )
    script_text = read_nonempty_text(resolved_script, label="Script file")
    page_numbers = _parse_page_spec_or_usage(page)
    variant_numbers = _parse_page_spec_or_usage(variant)

    try:
        segments = collect_slide_segments(
            image_dir,
            script_text,
            page_filter=page_numbers,
            variant_filter=variant_numbers,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if not mux_only:
        try:
            asyncio.run(
                _synthesize_speech(
                    segments,
                    reference_audio=reference_audio,
                    voice_id=voice_id,
                    api_key_override=api_key,
                    tts_model_override=tts_model,
                    tts_voice_override=voice,
                )
            )
        except RuntimeError as exc:
            raise click.ClickException(str(exc)) from exc

    ts = timestamp_from_image_dir(image_dir) or timestamp_slug()
    video_path = presentation_video_path(work_dir, ts)
    try:
        segment_count = build_presentation_video(
            segments,
            video_path,
            silent_seconds=silent_seconds,
        )
    except Exception as exc:
        raise click.ClickException(f"Failed to build narrated video: {exc}") from exc

    click.echo(
        f"Created {video_path.name} ({segment_count} slide(s)) in {work_dir.resolve()}"
    )
    click.echo(f"Video: {video_path.resolve()}")
    if reference_audio is not None and not mux_only:
        click.echo(
            f"Voice clone reference: {reference_audio.resolve()} (provider: MiniMax)"
        )


@click.command()
@click.option(
    "--work",
    "work_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_WORK_DIR,
    show_default=True,
    help="Work directory for presentation_video_*.mp4 output.",
)
@click.option(
    "--script",
    "script_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_SCRIPT_PATH,
    show_default=True,
    help=(
        "Script with [Speech:] tags. When this option is omitted and the default "
        "file is missing, uses the newest script_*.md snapshot in --output."
    ),
)
@click.option(
    "--output",
    "image_dir",
    type=click.Path(path_type=Path),
    required=True,
    help="Compose image directory containing slide_p##_v##.png files.",
)
@click.option(
    "--page",
    type=str,
    default=None,
    help="Slides to include (e.g. '1', '1,3,5', '1-5'). Default: all slides.",
)
@click.option(
    "--variant",
    type=str,
    default=None,
    help="Variant numbers to include (e.g. '1' or '1,2'). Default: all variants.",
)
@click.option(
    "--api-key",
    envvar="MINIMAX_API_KEY",
    default=None,
    help="MiniMax API key for TTS (or MINIMAX_API_KEY / .env).",
)
@click.option(
    "--tts-model",
    default=DEFAULT_MINIMAX_TTS_MODEL,
    show_default=True,
    help="MiniMax TTS model slug.",
)
@click.option(
    "--voice",
    default=DEFAULT_MINIMAX_TTS_VOICE,
    show_default=True,
    help=(
        "Voice identifier for the selected TTS model. "
        "Ignored when --voice-id is set; preset fallback when using --reference-audio."
    ),
)
@click.option(
    "--reference-audio",
    type=click.Path(path_type=Path, exists=False),
    default=None,
    help=(
        "Path to a clean recording of your voice (WAV/MP3/FLAC). "
        "Uses MiniMax voice cloning."
    ),
)
@click.option(
    "--voice-id",
    default=None,
    help=(
        "Saved / standard MiniMax voice ID (alternative to --reference-audio)."
    ),
)
@click.option(
    "--mux-only",
    is_flag=True,
    default=False,
    help=(
        "Skip TTS and mux existing slide_p##_v##.mp3 files next to PNGs "
        "(no API calls)."
    ),
)
@click.option(
    "--silent-seconds",
    type=float,
    default=3.0,
    show_default=True,
    help="Duration for slides without speech or missing audio.",
)
def main(
    work_dir: Path,
    script_path: Path,
    image_dir: Path,
    page: str | None,
    variant: str | None,
    api_key: str | None,
    tts_model: str,
    voice: str,
    reference_audio: Path | None,
    voice_id: str | None,
    mux_only: bool,
    silent_seconds: float,
) -> None:
    """Record slide images and script speech tags into a narrated MP4 video."""
    if reference_audio is not None and voice_id:
        raise click.UsageError("Use either --reference-audio or --voice-id, not both.")
    if reference_audio is not None and not reference_audio.is_file():
        raise click.UsageError(
            f"Reference audio not found: {reference_audio.resolve()}"
        )

    script_explicit = (
        click.get_current_context().get_parameter_source("script_path")
        is not ParameterSource.DEFAULT
    )
    _run_narrate(
        image_dir=image_dir,
        work_dir=work_dir,
        script_path=script_path,
        script_explicit=script_explicit,
        page=page,
        variant=variant,
        api_key=api_key,
        tts_model=tts_model,
        voice=voice,
        reference_audio=reference_audio,
        voice_id=voice_id,
        mux_only=mux_only,
        silent_seconds=silent_seconds,
    )


if __name__ == "__main__":
    main()
