---
name: record-video
description: Record a narrated MP4 from slide PNGs and [Speech:] tags via MiniMax TTS. Use when the user wants to record a presentation video, narration, voice clone, or remux existing slide audio.
disable-model-invocation: true
---

# Record a video

Turn slide PNGs and `[Speech:]` tags into `presentation_video_YYYYMMDD_HHMMSS.mp4`. Speech is synthesized with MiniMax, then muxed with ffmpeg. The CLI module is still `src.present.cli`.

## Inputs

- A work directory (default `~/work`, expanded to an absolute path, or a folder the user names). Call it `WORK`.
- An image directory from render, holding `slide_p##_v##.png`. If the user does not name one, use the newest `WORK/image_*`.
- `WORK/script_N.md` — the script with `[Speech:]` tags. Pass it as `--script`. A path that was named and is missing stops the run. Omit `--script` only to use the newest `script_*.md` snapshot in the image directory; the CLI prints which file it used.

ffmpeg must be on `PATH`, or `imageio-ffmpeg` must be installed. Check before spending a TTS call:

```bash
command -v ffmpeg || python3 -c "import imageio_ffmpeg"
```

## Workflow

Run every command from the repo root. Pass absolute paths. The CLI defaults are relative to the repo and do not point at `~/work`. Do not read `.env`. The MiniMax key comes from config. Stop on a failed check and report it.

### 1. Record

```bash
python3 -m src.present.cli --work WORK --script WORK/script_N.md --output WORK/image_TS
```

Optional flags, only when the user asks:

- `--variant 1` — one image variant. Default is every variant in the directory.
- `--page 1-5` — a subset of slides.
- `--voice` — a MiniMax voice id. Ignored when `--voice-id` is set.
- `--voice-id` — a saved MiniMax voice.
- `--reference-audio PATH` — clone a voice from a WAV, MP3, or FLAC recording.

`--voice-id` and `--reference-audio` cannot be used together. The CLI rejects that pair.

Slides with no speech, or whose audio file is missing, play for `--silent-seconds` (default 3).

### 2. Remux without TTS

When `slide_p##_v##.mp3` files already sit next to the PNGs:

```bash
python3 -m src.present.cli --work WORK --script WORK/script_N.md --output WORK/image_TS --mux-only
```

### 3. Report

The video is `WORK/presentation_video_YYYYMMDD_HHMMSS.mp4`, using the timestamp of the image directory. Print its absolute path.
