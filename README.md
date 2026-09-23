# VibeSliding ✨

**Transform ideas into stunning presentations in seconds.** Write your content, pick a style, and let AI handle the rest — no design skills required.

## Why VibeSliding? 🚀

- **Save Hours** — What used to take hours now takes minutes
- **Professional Results** — Every slide looks polished and cohesive
- **Zero Learning Curve** — If you can write markdown, you can create presentations
- **Iterate Fast** — Generate multiple variants instantly and pick your favorite

## Features

- 📝 **Plan** — A skill writes the deck plan from your idea and references, with no API calls
- 🎨 **Two-Tone Style Plates** — Dark curtain plates (cover/transition/ending) + light teaching plates (content), filled from a design brief
- 🖼️ **Slide References** — Attach slide-specific photos or image globs in the plan; they pass through to the script
- 🧠 **Role-Aware Render** — Routes each slide to the matching style plates by role (cover / transition / content / ending)
- 🔄 **Multiple Variants** — Generate several design options per slide
- 🎯 **Selective Regeneration** — Redo specific slides without starting over
- ⚡ **Parallel Generation** — Concurrent API calls with configurable concurrency
- 📽️ **Auto PPTX** — One 16:9 deck: slide images plus `[Speech:]` notes in presenter view
- 🎬 **Narrated Video** — TTS + ffmpeg turns slides and `[Speech:]` tags into MP4
- 🔌 **Multi-Provider** — OpenRouter (text + images) and Volcengine/Doubao Seedream (images)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

## Pipeline

Four stages — **plan → write → design → render**. Present is optional.

```bash
# 1. Plan (no API): idea.md + references → facts.md, plan_N.md, design_brief.md
#    Use the plan-deck skill, then check the plan:
python3 -m src.plan.cli --plan work/plan_16.md

# 2. Write: plan_N.md + facts.md (required) → one text call per slide → script_N.md
python3 -m src.write.cli --work work --plan work/plan_16.md

# 3. Design: image calls → work/style/*.png
python3 -m src.design.cli --work work --script work/script_16.md

# 4. Render: one image call per slide → image dir + PPTX
python3 -m src.render.cli --work work --script work/script_16.md

# Optional: slide PNGs + [Speech:] tags → narrated MP4 (requires ffmpeg)
python3 -m src.present.cli --output work/image_YYYYMMDD_HHMMSS
```

Then **curate** (delete variants you don't love) and **polish** (`--page` to regenerate individual slides).

> 💡 Plan writes `facts.md` (one `- **F1 Name.** fact — citation` bullet per fact), `plan_N.md` (slides cite fact IDs in `Evidence:`), and `design_brief.md`; `src.plan.cli` also checks that `Section: k/total` lines match the roadmap and that every cited ID exists in the `facts.md` beside the plan. Write requires `facts.md`, sends each slide its cited facts plus the most related others, expands each slide in parallel, saves prompts under `work/write_prompts/`, and then checks the script for structure, page numbers (`Slide number: N` on content slides only, never a total), text/visual balance (content slides within a 0.85-1.35 text-to-visual ratio; cover, roadmap, and ending slides more visual than text), and speech length (1-2 minutes on content slides, about 30 seconds on the rest). Design writes five plates under `work/style/` (`style_base_noncontent.png`, `style_base_content.png`, `style_cover.png`, `style_transition.png`, `style_content.png`), each with a `*_prompt.txt` sidecar. Render routes plates by slide role on the full deck, then applies `--page`, and writes images to `work/image_YYYYMMDD_HHMMSS/` plus a PPTX in `work/`. Present writes `presentation_video_YYYYMMDD_HHMMSS.mp4` (install [ffmpeg](https://ffmpeg.org/download.html) first).

## Usage Examples

```bash
# Design: one plate per stage, or several candidates to pick from
python3 -m src.design.cli --work work --script work/script_16.md
python3 -m src.design.cli --work work --script work/script_16.md --candidates 4 --pick 1,1,2,1,3

# Write: redo a few slides
python3 -m src.write.cli --work work --plan work/plan_16.md --page "3,7-9"

# Render: multiple variants per slide
python3 -m src.render.cli --work work --script work/script_16.md --copy 4

# Render: selective regeneration
python3 -m src.render.cli --work work --script work/script_36.md --page "1,3,5-7"

# Render: rebuild PPTX after curating (no API calls)
python3 -m src.render.cli --work work --pptx-only --output work/image_20260520_220006
python3 -m src.render.cli --work work --pptx-only --output work/image_20260520_220006 --variant 1

# Present: TTS + video from curated slides (MiniMax TTS)
python3 -m src.present.cli --output work/image_20260520_220006 --variant 1

# Present: clone your voice from a short reference recording (clean WAV/MP3)
python3 -m src.present.cli --output work/image_20260520_220006 \
  --reference-audio work/voice_sample.wav

# Present: remux only after TTS MP3s already exist (no API calls)
python3 -m src.present.cli --output work/image_20260520_220006 --mux-only
```

## CLI Reference

### `src.plan.cli`

| Option | Description |
|--------|-------------|
| `--plan` | Deck plan to validate (default: `work/plan_16.md`); also checks `Evidence:` IDs against `facts.md` in the same folder |

### `src.write.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`); must contain `facts.md`, optional `idea.md` |
| `--plan` | Deck plan (`plan_N.md`), required |
| `--page` | Slides to rewrite, e.g. `3,7-9` (merges into an existing script) |
| `--txt-model` | Text model override |
| `--api-key` | OpenRouter API key override |
| `--proxy` | HTTP/HTTPS proxy for text calls |

### `src.design.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--script` | Script file (default: `work/script_16.md`) |
| `--brief` | Design brief (default: `WORK/design_brief.md`) |
| `--style` | Style directory (default: `WORK/style/`) |
| `--candidates` | Candidates per style image (default: 1, max: 12). `1` skips picking |
| `--pick` | Pre-select indices: `base_noncontent,base_content,cover,transition,content` |
| `--api-key` | API key override |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |
| `--provider` | `openrouter` or `volcengine` |

### `src.render.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--script` | Script file (default: `work/script_16.md`) |
| `--style` | Directory holding the style images (default: `WORK/style` when it exists, else `style/`) |
| `--copy` | Variants per slide (default: 1) |
| `--output` | Output dir (default: `WORK/image_YYYYMMDD_HHMMSS/`); PPTX goes to `--work` |
| `--api-key` | API key override |
| `--page` | Pages to generate, e.g. `1,3,5-7` |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |
| `--provider` | `openrouter` or `volcengine` |
| `--balance-only` | Print OpenRouter credits and exit |
| `--no-balance` | Skip credits line after run |
| `--pptx-only` | Rebuild PPTX from existing PNGs in `--output` dir (no API calls); speaker notes from `--script` `[Speech:]` tags |
| `--variant` | With `--pptx-only`: variant filter for the PPTX, e.g. `1` or `1,2` |

> **Credits:** After each OpenRouter run, remaining credits are printed unless `--no-balance`. Requires an OpenRouter [Management API key](https://openrouter.ai/settings/management-keys) — set `OPENROUTER_MANAGEMENT_API_KEY` or `[openrouter] management_api_key` in `.env`.

### `src.present.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--script` | Script with `[Speech:]` tags (default: `work/script_16.md`). A named missing file is an error. When omitted and the default is missing, uses the newest `script_*.md` snapshot in `--output` |
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
├── idea.md                                    # seed: title, audience, language
├── facts.md                                   # verified facts with citations
├── source.md                                  # optional extra source material
├── design_brief.md                            # motif, palette language, on-plate labels
├── plan_16.md                                 # deck plan (content-slide count in the name)
├── script_16.md                               # full slide script
├── write_prompts/                             # one prompt file per slide
├── style/                                     # five style plates for this deck
│   ├── style_base_noncontent.png
│   ├── style_base_content.png
│   ├── style_cover.png
│   ├── style_transition.png
│   ├── style_content.png
│   ├── style_*_prompt.txt
│   └── style_candidates/
├── image_YYYYMMDD_HHMMSS/                     # render output (slide PNGs)
├── slides_YYYYMMDD.pptx                       # slide images + speaker notes
└── presentation_video_YYYYMMDD_HHMMSS.mp4     # narrated slide video
```

### Outline Format

```markdown
# PPT Outline: My Presentation

---

## Slide 1: Introduction
- **Key point:** Why this matters
- Core insight: One takeaway the audience should remember
[Style: style_content.png, style_base_content.png]
[Reference: photos/founder.png]
[Visual: Split-screen hero; light content background. Slide number: 1]
[Speech: Conversational presenter narration for this slide]

---

## Appendix: Global Visual Requirements
- **Theme:** Two-tone deck — white/light content slides; dark curtain for cover, transitions, ending. Accents: Primary #2563EB, Accent #10B981
- **Fonts:** Title / body families and sizes
```

| Tag | Purpose |
|-----|---------|
| `[Visual: ...]` | Layout, composition, diagrams, icons, motifs |
| `[Speech: ...]` | Presenter narration (used by present + PPTX speaker notes) |
| `[Style: ...]` | Style plates for this slide — **filenames only**, looked up in `--style`; omit to inherit the plate for the slide's role |
| `[Reference: ...]` | Slide-specific image refs such as headshots or charts (place immediately before `[Visual:]`; leading `@` accepted) |
| `## Appendix: ...` | Deck-wide text constraints only (theme/hex, fonts/sizes; state two-tone backgrounds) |

Include **3–6 transition slides** (titles prefixed `Roadmap:`) with `progress bar k/total` section markers. Content slides show `Slide number: N` — the page number only, never the total. Without a `[Style: ...]` tag, render attaches dark plates to cover/transition/ending and light plates to content slides:

| Slide role | Plates attached |
|---|---|
| cover, ending | `style_cover.png`, `style_base_noncontent.png` |
| transition | `style_transition.png`, `style_base_noncontent.png` |
| content | `style_content.png`, `style_base_content.png` |

### Render Output

```
work/
├── image_YYYYMMDD_HHMMSS/
│   ├── script_16.md                     # script snapshot used for this run
│   ├── slide_p01_prompt.txt           # exact prompt used for slide 1
│   ├── slide_p01_v01.png              # Slide 1, variant 1
│   ├── slide_p01_v01.mp3              # TTS audio (after present)
│   ├── slide_p01_v02.png              # Slide 1, variant 2
│   └── slide_p02_v01.png              # Slide 2, variant 1
├── slides_YYYYMMDD.pptx                      # all slides + speaker notes in one deck
└── presentation_video_YYYYMMDD_HHMMSS.mp4    # narrated MP4
```

## Configuration

Copy `.env.example` → `.env` and fill in your keys. INI-style sections:

| Section | Used by | Key settings |
|---------|---------|-------------|
| *(preamble)* | All | `provider`, `max_concurrent`, `proxy` |
| `[openrouter]` | Write / Render (when `provider = openrouter`) | `api_key`, `management_api_key`, `img_model`, `txt_model`, `use_proxy` |
| `[volcengine]` | Design / Render (when `provider = volcengine`) | `api_key`, `img_model`, `txt_model`, `use_proxy` |
| `[minimax]` | Present (+ text/image when it is the active provider) | `api_key`, `img_model`, `txt_model`, `use_proxy`, optional `tts_model`, `tts_voice` |

- **Write** → `txt_model` from the active `provider` section (falls back across `[openrouter]`, `[volcengine]`, `[minimax]`)
- **Design / Render** → `img_model` from the active `provider` (`src.design.cli` + `src.render.cli`); OpenRouter image calls go through the unified Image API (`POST /v1/images`), so image-only models such as `openai/gpt-image-2.5-sunburst` work alongside chat-style ones like `google/gemini-3-pro-image-preview`
- **Present** → MiniMax TTS via `[minimax]` `tts_model` / `tts_voice` or `--tts-model` / `--voice` (defaults: `speech-2.8-hd`, `Chinese (Mandarin)_Lyrical_Voice`) with optional voice cloning
- Global `proxy` applies when a section's `use_proxy = true`; section-level `proxy` overrides are still supported
- `ark_api_key` in the preamble aliases `[volcengine] api_key`

## License

See LICENSE file for details.

---

**Happy Sliding! 🎨✨** Transform your markdown into beautiful presentations in minutes, not hours.
