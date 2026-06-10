# VibeSliding ✨

**Transform ideas into stunning presentations in seconds.** Write your content, pick a style, and let AI handle the rest — no design skills required.

## Why VibeSliding? 🚀

- **Save Hours** — What used to take hours now takes minutes
- **Professional Results** — Every slide looks polished and cohesive
- **Zero Learning Curve** — If you can write markdown, you can create presentations
- **Iterate Fast** — Generate multiple variants instantly and pick your favorite

## Features

- 🧪 **DeepResearch** — Turn a one-line idea into a researched, reviewable outline via Valyu
- 🎨 **Style Transfer** — Reference images for a consistent, on-brand deck
- 🖼️ **Slide References** — Attach slide-specific photos or image globs in the outline
- 📚 **Outline Articles** — Declare source markdown/PDF references once at the top
- 🧠 **Smart Layouts** — AI auto-selects optimal layouts based on content
- 🔄 **Multiple Variants** — Generate several design options per slide
- 🎯 **Selective Regeneration** — Redo specific slides without starting over
- ⚡ **Parallel Generation** — Concurrent API calls with configurable concurrency
- 📄 **Auto PDF** — Combined slide PDF + speech-notes PDF
- 🔌 **Multi-Provider** — OpenRouter (text + images) and Volcengine/Doubao Seedream (images)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

## Pipeline

Four steps — **research → outline → style → compose**:

```bash
# 1. DeepResearch: idea.md → research.md
python3 -m src.research.cli

# 2. Outline: research.md → outline_16.md, outline_25.md, outline_36.md
python3 -m src.outline.cli

# 3. Style: interactive reference picker → style_*.png
python3 -m src.style.cli

# 4. Compose: outline + style → slide images + PDF
python3 -m src.compose.cli
```

Then **curate** (delete variants you don't love) and **polish** (`--page` to regenerate individual slides).

> 💡 Steps 1–3 share `./work/` — edit files between steps. Compose writes images to `work/image_YYYYMMDD_HHMMSS/` and PDFs to `work/`.

## Usage Examples

```bash
# Style: pick a different outline, or skip interactive prompts
python3 -m src.style.cli --outline work/outline_25.md
python3 -m src.style.cli --pick 1,2,1,3

# Compose: multiple variants per slide
python3 -m src.compose.cli --copy 4

# Compose: longer outline + selective regeneration
python3 -m src.compose.cli --outline work/outline_36.md --page "1,3,5-7"

# Compose: rebuild PDF after curating (no API calls)
python3 -m src.compose.cli --pdf-only --output work/image_20260520_220006
python3 -m src.compose.cli --pdf-only --output work/image_20260520_220006 --variant 1

# Compose: explicit style files + article references
python3 -m src.compose.cli --style cover.png --style body.png --article "docs/*.pdf"
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

### `src.style.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Outline file (default: `work/outline_16.md`) |
| `--candidates` | Candidates per stage (default: 4, max: 12) |
| `--pick` | Pre-select indices: `base,cover,transition,content` |
| `--provider` | `openrouter` or `volcengine` |
| `--api-key` | API key override |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |

### `src.compose.cli`

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
├── style_base.png                             # base plate (palette + typography)
├── style_cover.png                            # cover-slide reference
├── style_transition.png                       # transition/roadmap reference
├── style_content.png                          # content-slide reference
├── style_candidates/                          # all candidates + contact sheets
├── image_YYYYMMDD_HHMMSS/                     # compose output (slide PNGs)
├── presentation_slides_YYYYMMDD_HHMMSS.pdf    # combined slide deck
└── presentation_speech_YYYYMMDD_HHMMSS.pdf    # A4: slide image + speech notes
```

### Outline Format

```markdown
# My Presentation

[Articles: @docs/research.md, @docs/report.pdf]

---

## Slide 1: Introduction
- **Key point:** Why this matters
[Visual: hero image of the product]
[Reference: photos/founder.png]

---

## Appendix: Global Visual Requirements
- **Theme:** Modern tech aesthetic
- **Colors:** Primary: #2563EB, Accent: #10B981
```

| Tag | Purpose |
|-----|---------|
| `[Visual: ...]` | Layout, composition, diagrams, icons, motifs |
| `[Reference: ...]` | Slide-specific image refs (leading `@` accepted) |
| `[Articles: ...]` | Top-of-outline text reference declarations |
| `## Appendix: ...` | Deck-wide text styles (colors + hex, fonts + sizes) |

Include **3–6 transition slides** (titles prefixed `Roadmap:`) with `progress bar N/total` markers.

### Compose Output

```
work/
├── image_YYYYMMDD_HHMMSS/
│   ├── slide_p01_v01.png              # Slide 1, variant 1
│   ├── slide_p01_v02.png              # Slide 1, variant 2
│   └── slide_p02_v01.png              # Slide 2, variant 1
├── presentation_slides_YYYYMMDD_HHMMSS.pdf   # all slides in one PDF
└── presentation_speech_YYYYMMDD_HHMMSS.pdf   # A4: slide image + speech notes
```

## Configuration

Copy `.env.example` → `.env` and fill in your keys. INI-style sections:

| Section | Used by | Key settings |
|---------|---------|-------------|
| *(preamble)* | All | `provider`, `max_concurrent`, `proxy` |
| `[valyu]` | Research | `api_key`, `mode`, `categories`, `use_proxy`, `proxy` |
| `[openrouter]` | Outline / Style / Compose | `api_key`, `management_api_key`, `img_model`, `txt_model`, `use_proxy`, `proxy` |
| `[volcengine]` | Style / Compose | `api_key`, `img_model`, `txt_model`, `base_url`, `image_size`, `response_format`, `watermark`, `use_proxy`, `proxy` |

- **Research** → `[valyu]` for DeepResearch
- **Outline** → `txt_model` from `[openrouter]` (text only)
- **Style / Compose** → `img_model` from the active `provider`
- `ark_api_key` in the preamble aliases `[volcengine] api_key`

## License

See LICENSE file for details.

---

**Happy Sliding! 🎨✨** Transform your markdown into beautiful presentations in minutes, not hours.
