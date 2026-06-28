"""Tests for narrate CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from PIL import Image

from src.narrate.cli import main

OUTLINE = """# Deck

---

## Slide 1: Cover
[Speech: Hello world.]
"""


@pytest.fixture
def image_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "image_test"
    directory.mkdir()
    Image.new("RGB", (64, 36), color="red").save(directory / "slide_p01_v01.png")
    outline = directory / "outline_16.md"
    outline.write_text(OUTLINE, encoding="utf-8")
    return directory


def test_narrate_mux_only(image_dir: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    with patch("src.narrate.cli.build_presentation_video", return_value=1) as mock_build:
        result = runner.invoke(
            main,
            [
                "--output",
                str(image_dir),
                "--work",
                str(tmp_path),
                "--mux-only",
            ],
        )

    assert result.exit_code == 0, result.output
    mock_build.assert_called_once()


def test_narrate_success(image_dir: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    with (
        patch("src.narrate.cli.build_presentation_video", return_value=1) as mock_build,
        patch("src.core.minimax_tts.synthesize_speech_parallel", return_value=[b"fake-mp3"]) as mock_synth,
    ):
        result = runner.invoke(
            main,
            [
                "--output",
                str(image_dir),
                "--work",
                str(tmp_path),
                "--api-key",
                "fake-minimax-key",
            ],
        )

    assert result.exit_code == 0, result.output
    mock_build.assert_called_once()
    mock_synth.assert_called_once()


def test_narrate_with_reference_audio(image_dir: Path, tmp_path: Path) -> None:
    ref = tmp_path / "voice.wav"
    ref.write_bytes(b"RIFFfake")
    runner = CliRunner()
    with (
        patch("src.narrate.cli.build_presentation_video", return_value=1) as mock_build,
        patch("src.core.minimax_tts.setup_cloned_voice", return_value="cloned-voice-id") as mock_clone,
        patch("src.core.minimax_tts.synthesize_speech_parallel", return_value=[b"fake-mp3"]) as mock_synth,
    ):
        result = runner.invoke(
            main,
            [
                "--output",
                str(image_dir),
                "--work",
                str(tmp_path),
                "--reference-audio",
                str(ref),
                "--api-key",
                "fake-minimax-key",
            ],
        )

    assert result.exit_code == 0, result.output
    mock_build.assert_called_once()
    mock_clone.assert_called_once()
    mock_synth.assert_called_once()


def test_narrate_requires_output() -> None:
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "Missing option '--output'" in result.output


def test_narrate_missing_image_dir(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--output",
            str(tmp_path / "missing"),
            "--work",
            str(tmp_path),
            "--mux-only",
        ],
    )
    assert result.exit_code != 0
    assert "Image directory not found" in result.output


def test_narrate_rejects_both_reference_audio_and_voice_id(
    image_dir: Path, tmp_path: Path
) -> None:
    ref = tmp_path / "voice.wav"
    ref.write_bytes(b"RIFFfake")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--output",
            str(image_dir),
            "--work",
            str(tmp_path),
            "--reference-audio",
            str(ref),
            "--voice-id",
            "saved-voice-123",
        ],
    )
    assert result.exit_code != 0
    assert "not both" in result.output
