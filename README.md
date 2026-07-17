# VibeSliding ✨

**Transform ideas into stunning presentations in seconds.** Write your content, pick a style, and let AI handle the rest — no design skills required.

## Why VibeSliding? 🚀

- **Save Hours** — What used to take hours now takes minutes
- **Professional Results** — Every slide looks polished and cohesive
- **Zero Learning Curve** — If you can write markdown, you can create presentations
- **Iterate Fast** — Generate multiple variants instantly and pick your favorite

## Features

- 🧪 **DeepResearch** — Turn a one-line idea into a researched, reviewable outline via Valyu
- 🎨 **Two-Tone Style Transfer** — Dark curtain plates (cover/transition/ending) + light teaching plates (content), with shared accents/motifs
- 🖼️ **Slide References** — Attach slide-specific photos or image globs in the outline
- 📚 **Outline Articles** — Declare source markdown/PDF references once at the top
- 🧠 **Role-Aware Render** — Routes each slide to the matching style plates by role (cover / transition / content / ending)
- 🔄 **Multiple Variants** — Generate several design options per slide
- 🎯 **Selective Regeneration** — Redo specific slides without starting over
- ⚡ **Parallel Generation** — Concurrent API calls with configurable concurrency
- 📄 **Auto PDF** — Combined slide PDF + speech-notes PDF
- 🎬 **Narrated Video** — TTS + ffmpeg turns slides and `[Speech:]` tags into MP4
- 🔌 **Multi-Provider** — OpenRouter (text + images) and Volcengine/Doubao Seedream (images)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

## Pipeline

Four tasks — **research → outline → render → present**:

```bash
# 1. Research: idea.md → research.md
python3 -m src.research.cli

# 2. Outline: research.md → outline_16.md, outline_25.md, outline_36.md
python3 -m src.outline.cli

# 3. Render: two-tone style refs → slide images + PDF
python3 -m src.render.style.cli   # base_noncontent → base_content → cover/transition/content
python3 -m src.render.cli

# 4. Present: slide PNGs + [Speech:] tags → narrated MP4 (requires ffmpeg)
python3 -m src.present.cli --output work/image_YYYYMMDD_HHMMSS
```

Then **curate** (delete variants you don't love) and **polish** (`--page` to regenerate individual slides).

> 💡 Steps 1–2 share `./work/` — edit files between steps. Style CLI writes five plates (`style_base_noncontent.png`, `style_base_content.png`, `style_cover.png`, `style_transition.png`, `style_content.png`). Render routes plates by slide role and writes images to `work/image_YYYYMMDD_HHMMSS/` + PDFs to `work/`. Present writes `presentation_video_YYYYMMDD_HHMMSS.mp4` to `work/` (install [ffmpeg](https://ffmpeg.org/download.html) first).

## Usage Examples

```bash
# Render: pick a different outline, or skip interactive style prompts
python3 -m src.render.style.cli --outline work/outline_25.md
python3 -m src.render.style.cli --pick 1,1,2,1,3  # base_noncontent,base_content,cover,transition,content

# Render: multiple variants per slide
python3 -m src.render.cli --copy 4

# Render: longer outline + selective regeneration
python3 -m src.render.cli --outline work/outline_36.md --page "1,3,5-7"

# Render: rebuild PDF after curating (no API calls)
python3 -m src.render.cli --pdf-only --output work/image_20260520_220006
python3 -m src.render.cli --pdf-only --output work/image_20260520_220006 --variant 1

# Render: explicit style plates + article references
python3 -m src.render.cli --style "work/style_*.png" --article "docs/*.pdf"

# Present: TTS + video from curated slides (MiniMax TTS)
python3 -m src.present.cli --output work/image_20260520_220006 --variant 1

# Present: clone your voice from a short reference recording (clean WAV/MP3)
python3 -m src.present.cli --output work/image_20260520_220006 \
  --reference-audio work/voice_sample.wav

# Present: remux only after TTS MP3s already exist (no API calls)
python3 -m src.present.cli --output work/image_20260520_220006 --mux-only
```

## CLI Reference

### `src.research.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--mode` | Valyu mode: `fast` / `standard` / `heavy` / `max` |
| `--categories` | Comma-separated datasource categories (see below) |
| `--valyu-api-key` | Valyu API key override |
| `--resume` | Resume polling from `research_state.json` |
| `--task-id` | Resume a specific task ID |
| `--fresh` | Start new task even if state file exists |

Categories: `research`, `healthcare`, `patents`, `markets`, `company`, `economic`, `predictions`, `legal`, `politics`, `cybersecurity`, `transportation`

### `src.outline.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--slides` | Content slide counts (default: `16,25,36`) |
| `--api-key` | OpenRouter API key override |
| `--txt-model` | Text model override |
| `--proxy` | HTTP/HTTPS proxy for OpenRouter |

### `src.render.style.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Outline file (default: `work/outline_16.md`) |
| `--candidates` | Candidates per stage (default: 4, max: 12) |
| `--pick` | Pre-select indices: `base_noncontent,base_content,cover,transition,content` |
| `--provider` | `openrouter` or `volcengine` |
| `--api-key` | API key override |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |

### `src.render.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Outline file (default: `work/outline_16.md`) |
| `--style` | Style image(s)/glob, repeatable (default: `work/style_*.png`) |
| `--copy` | Variants per slide (default: 1) |
| `--page` | Pages to generate, e.g. `1,3,5-7` |
| `--article` | Article path(s)/glob, repeatable (`.pdf`, `.md`) |
| `--output` | Output dir (default: `work/image_YYYYMMDD_HHMMSS/`); PDFs go to `--work` |
| `--provider` | `openrouter` or `volcengine` |
| `--api-key` | API key override |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |
| `--balance-only` | Print OpenRouter credits and exit |
| `--no-balance` | Skip credits line after run |
| `--pdf-only` | Rebuild PDFs from existing PNGs in `--output` dir (no API calls) |
| `--variant` | With `--pdf-only`: variant filter, e.g. `1` or `1,2` |

> **Credits:** After each OpenRouter run, remaining credits are printed unless `--no-balance`. Requires an OpenRouter [Management API key](https://openrouter.ai/settings/management-keys) — set `OPENROUTER_MANAGEMENT_API_KEY` or `[openrouter] management_api_key` in `.env`.

### `src.present.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Outline file (default: `work/outline_16.md`; falls back to snapshot in `--output`) |
| `--output` | Render image directory with `slide_p##_v##.png` (required) |
| `--page` | Slides to include, e.g. `1,3,5-7` |
| `--variant` | Variant filter, e.g. `1` or `1,2` |
| `--api-key` | MiniMax API key override |
| `--tts-model` | MiniMax TTS model (default: `speech-2.8-hd`) |
| `--voice` | TTS voice (default: `Chinese (Mandarin)_Lyrical_Voice`) |
| `--reference-audio` | WAV/MP3/FLAC of your voice for MiniMax voice cloning |
| `--voice-id` | Saved MiniMax voice ID (alternative to `--reference-audio`) |
| `--mux-only` | Skip TTS; mux existing `slide_p##_v##.mp3` files (no API calls) |
| `--silent-seconds` | Duration for slides without speech (default: `3.0`) |

> **Prerequisite:** [ffmpeg](https://ffmpeg.org/download.html) and `ffprobe` must be on your PATH.
>
> **Voice clone:** `--reference-audio` uploads reference audio and clones voice dynamically via MiniMax.

## Input/Output

### Work Directory

```
work/
├── idea.md                                    # seed: title, audience, core message
├── research.md                                # DeepResearch report with citations
├── research_state.json                        # (transient) in-progress task state
├── source.md                                  # optional custom source material
├── style_base.md                              # shared style + narrative scaffold
├── outline_16.md                              # 16 content-slide outline
├── outline_25.md                              # 25 content-slide outline
├── outline_36.md                              # 36 content-slide outline
├── style_base_noncontent.png                  # dark curtain base (cover/transition/ending)
├── style_base_content.png                     # light content base (teaching slides)
├── style_cover.png                            # cover-slide reference (dark)
├── style_transition.png                       # transition/roadmap reference (dark)
├── style_content.png                          # content-slide reference (light)
├── style_candidates/                          # all candidates + contact sheets
├── image_YYYYMMDD_HHMMSS/                     # render output (slide PNGs)
├── presentation_slides_YYYYMMDD_HHMMSS.pdf    # combined slide deck
├── presentation_speech_YYYYMMDD_HHMMSS.pdf    # A4: slide image + speech notes
└── presentation_video_YYYYMMDD_HHMMSS.mp4       # narrated slide video
```

### Outline Format

```markdown
# PPT Outline: My Presentation

[Articles: @docs/research.md, @docs/report.pdf]

---

## Slide 1: Introduction
- **Key point:** Why this matters
- Core insight: One takeaway the audience should remember
[Reference: photos/founder.png]
[Visual: Split-screen hero; light content background; Reference style: style_content.png, style_base_content.png]
[Speech: Conversational presenter narration for this slide]

---

## Appendix: Global Visual Requirements
- **Theme:** Two-tone deck — white/light content slides; dark curtain for cover, transitions, ending. Accents: Primary #2563EB, Accent #10B981
- **Fonts:** Title / body families and sizes
```

| Tag | Purpose |
|-----|---------|
| `[Visual: ...]` | Layout, composition, diagrams, icons, motifs; name the correct style plates for the slide role |
| `[Speech: ...]` | Presenter narration (used by present + speech PDF) |
| `[Reference: ...]` | Slide-specific image refs (place immediately before `[Visual:]`; leading `@` accepted) |
| `[Articles: ...]` | Top-of-outline text reference declarations |
| `## Appendix: ...` | Deck-wide text constraints only (theme/hex, fonts/sizes; state two-tone backgrounds) |

Include **3–6 transition slides** (titles prefixed `Roadmap:`) with `progress bar N/total` markers. Render attaches dark plates to cover/transition/ending and light plates to content slides.

### Render Output

```
work/
├── image_YYYYMMDD_HHMMSS/
│   ├── outline_16.md                    # outline snapshot used for this run
│   ├── slide_p01_v01.png              # Slide 1, variant 1
│   ├── slide_p01_v01.mp3              # TTS audio (after present)
│   ├── slide_p01_v02.png              # Slide 1, variant 2
│   └── slide_p02_v01.png              # Slide 2, variant 1
├── presentation_slides_YYYYMMDD_HHMMSS.pdf   # all slides in one PDF
├── presentation_speech_YYYYMMDD_HHMMSS.pdf   # A4: slide image + speech notes
└── presentation_video_YYYYMMDD_HHMMSS.mp4    # narrated MP4
```

## Configuration

Copy `.env.example` → `.env` and fill in your keys. INI-style sections:

| Section | Used by | Key settings |
|---------|---------|-------------|
| *(preamble)* | All | `provider`, `max_concurrent`, `proxy` |
| `[openrouter]` | Outline / Render (when `provider = openrouter`) | `api_key`, `management_api_key`, `img_model`, `txt_model`, `use_proxy` |
| `[volcengine]` | Render (when `provider = volcengine`) | `api_key`, `img_model`, `txt_model`, `use_proxy` |
| `[minimax]` | Present (+ future text/image) | `api_key`, `img_model`, `txt_model`, `use_proxy`, optional `tts_model`, `tts_voice` |
| `[valyu]` | Research | `api_key`, `mode`, `categories`, `use_proxy` |

- **Research** → `[valyu]` for DeepResearch
- **Outline** → `txt_model` from the active `provider` section (falls back across `[openrouter]`, `[volcengine]`, `[minimax]`)
- **Render** → `img_model` from the active `provider` (`src.render.style.cli` + `src.render.cli`)
- **Present** → MiniMax TTS via `[minimax]` `tts_model` / `tts_voice` or `--tts-model` / `--voice` (defaults: `speech-2.8-hd`, `Chinese (Mandarin)_Lyrical_Voice`) with optional voice cloning
- Global `proxy` applies when a section's `use_proxy = true`; section-level `proxy` overrides are still supported
- `ark_api_key` in the preamble aliases `[volcengine] api_key`

## License

See LICENSE file for details.

---

**Happy Sliding! 🎨✨** Transform your markdown into beautiful presentations in minutes, not hours.
