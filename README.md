# VibeSliding ✨

**Transform ideas into stunning presentations in seconds.** Generate beautiful slide decks from markdown outlines using AI — no design skills required.

Stop wrestling with PowerPoint. Write your content, pick a style, and let AI handle the rest.

## Why VibeSliding? 🚀

- **Save Hours** — What used to take hours now takes minutes
- **Professional Results** — Every slide looks polished and cohesive
- **Zero Learning Curve** — If you can write markdown, you can create presentations
- **Iterate Fast** — Generate multiple variants instantly and pick your favorite

## Features

- 🧪 **Valyu DeepResearch** — Turn a one-line idea into a researched, reviewable outline
- 🎨 **Style Transfer** — One or more reference images for a consistent, on-brand deck
- 🖼️ **Slide References** — Attach slide-specific photos or image globs directly in the outline
- 📚 **Outline Articles** — Declare source markdown/PDF references once in the outline
- 🧠 **Smart Layouts** — AI auto-selects optimal layouts based on your content
- 🔄 **Multiple Variants** — Generate several design options per slide
- 🎯 **Selective Regeneration** — Redo specific slides without starting over
- ⚡ **Blazing Fast** — Parallel generation with configurable concurrency
- 📄 **Auto PDF** — All slides combined into one file
- 🔌 **Multiple Providers** — OpenRouter and Volcengine (Doubao/Seedream)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

## How It Works

Four steps — **research**, **outline**, **style**, **compose**:

```bash
# 1. DeepResearch from work/idea.md → work/research.md
python3 -m src.research.cli

# 2. Generate outlines (16/25/36 content slides) → work/outline_*.md
python3 -m src.outline.cli

# 3. Generate style references (interactive picker) → work/style_*.png
python3 -m src.style.cli

# 4. Compose slide images → slides_YYYYMMDD_HHMMSS/
python3 -m src.compose.cli
```

Then **curate** (delete variants you don't love) and **polish** (`--page` to regenerate individual slides).

> 💡 **Pro tip:** Steps 1–3 share `./work/` — edit files between steps. Compose reads `work/` and writes a fresh timestamped output folder.

## Usage

### Style

```bash
# Pick a different outline length
python3 -m src.style.cli --outline work/outline_25.md

# Non-interactive: pre-select base,cover,transition,story indices
python3 -m src.style.cli --pick 1,2,1,3
```

### Compose

```bash
# Generate multiple variants per slide
python3 -m src.compose.cli --copy 4

# Use a longer outline
python3 -m src.compose.cli --outline work/outline_36.md

# Regenerate specific slides
python3 -m src.compose.cli --page "1,3,5-7"

# Rebuild PDF after curating variants (no API calls)
python3 -m src.compose.cli --pdf-only --output slides_20260520_220006
python3 -m src.compose.cli --pdf-only --output slides_20260520_220006 --variant 1

# Explicit style files plus articles
python3 -m src.compose.cli --style cover.png --style body.png --article "docs/*.pdf"
```

## CLI Options

### `python3 -m src.research.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--mode` | Valyu mode: `fast` / `standard` / `heavy` / `max` |
| `--categories` | Comma-separated Valyu datasource categories |
| `--valyu-api-key` | Valyu API key override |
| `--resume` | Resume polling an in-progress task from `research_state.json` |
| `--task-id` | Resume a specific Valyu task ID (optional with `--resume`) |
| `--fresh` | Start a new task even if a resume state file exists |

### `python3 -m src.outline.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--slides` | Content slide counts (default: `16,25,36`) |
| `--api-key` | OpenRouter API key override |
| `--txt-model` | Text model override |
| `--proxy` | HTTP/HTTPS proxy for OpenRouter |

### `python3 -m src.style.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Outline file (default: `work/outline_16.md`) |
| `--candidates` | Candidates per stage (default: 4, max: 12) |
| `--pick` | Pre-select indices: `base,cover,transition,story` |
| `--provider` | `openrouter` or `volcengine` |
| `--api-key` | API key override |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |

### `python3 -m src.compose.cli`

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Outline file (default: `work/outline_16.md`) |
| `--style` | Style image(s)/glob (default: `work/style_*.png`) |
| `--copy` | Variants per slide (default: 1) |
| `--page` | Pages to generate, e.g. `1,3,5-7` |
| `--article` | Reference docs/globs, e.g. `"docs/*.pdf"` |
| `--output` | Output dir (default: `slides_YYYYMMDD_HHMMSS/`) |
| `--provider` | `openrouter` or `volcengine` |
| `--api-key` | API key override |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |
| `--balance-only` | Print OpenRouter credits and exit |
| `--no-balance` | Skip credits line after a run |
| `--pdf-only` | Rebuild PDF from existing PNGs (no API) |
| `--variant` | With `--pdf-only`: variant filter, e.g. `1` or `1,2` |

> **Credits:** After each OpenRouter run, remaining credits are printed unless `--no-balance` is passed. Requires an OpenRouter **Management API key** — set `OPENROUTER_MANAGEMENT_API_KEY` or `[openrouter] management_api_key` ([create one here](https://openrouter.ai/settings/management-keys)). Volcengine runs skip this.

## Input/Output

### Work Directory (`work/`)

```
work/
├── idea.md                # presentation seed (title, audience, core message)
├── research.md            # Valyu DeepResearch report (with inline citations)
├── style_base.md          # shared style + narrative scaffold
├── outline_16.md          # 16 content-slide outline
├── outline_25.md          # 25 content-slide outline
├── outline_36.md          # 36 content-slide outline
├── style_base.png         # chosen base plate (palette + typography)
├── style_cover.png        # chosen cover-slide reference
├── style_transition.png   # chosen transition/roadmap reference
├── style_story.png        # chosen content/story-slide reference
└── style_candidates/      # all candidates + numbered contact sheets
```

### Outline Format

Each `## Slide N: Title` heading becomes a slide. See `examples/outline.md` for a full sample.

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

- `[Visual: ...]` — layout, composition, diagrams, icons, motifs
- `[Reference: ...]` — slide-specific image refs (leading `@` accepted)
- `[Articles: ...]` — attach text references at the top of the outline
- Include **3-6 transition slides** (titles prefixed `Roadmap:`) with `progress bar N/total` markers
- `## Appendix: Global Visual Requirements` — text styles only (colors + hex, fonts + sizes)

### Compose Output

```
slides_YYYYMMDD_HHMMSS/
├── slide_p01_v01.png     # Slide 1, variant 1
├── slide_p01_v02.png     # Slide 1, variant 2
├── slide_p02_v01.png     # Slide 2, variant 1
└── slide_combined.pdf    # all slides in one PDF
```

## Configuration

Copy `.env.example` to `.env` and fill in your keys. The file uses INI-style sections:

| Section | Used by | Key settings |
|---------|---------|-------------|
| *(preamble)* | All steps | `provider`, `max_concurrent`, optional `proxy` |
| `[valyu]` | Research | `api_key`, `mode`, `categories` |
| `[openrouter]` | Outline / Style / Compose | `api_key`, `img_model`, `txt_model`, `use_proxy` |
| `[volcengine]` | Outline / Style / Compose | `api_key`, `img_model`, `txt_model`, `use_proxy` |

- **Research** uses `[valyu]` for DeepResearch
- **Outline** uses `txt_model` from `[openrouter]` or `[volcengine]`
- **Style** and **Compose** use `img_model` from the active `provider`
- Each step is independent — configure each backend separately

## Examples

Check out the `examples/` folder for sample outlines and style references to get started quickly!

## License

See LICENSE file for details.

---

**Happy Sliding! 🎨✨** Transform your markdown into beautiful presentations in minutes, not hours.
