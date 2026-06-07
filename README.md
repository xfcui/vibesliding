# VibeSliding ✨

**Transform ideas into stunning presentations in seconds.** Generate beautiful slide decks from markdown outlines using AI — no design skills required.

Stop wrestling with PowerPoint. Write your content, pick a style, and let AI handle the rest.

## Why VibeSliding? 🚀

- **Save Hours** — What used to take hours now takes minutes
- **Professional Results** — Every slide looks polished and cohesive
- **Zero Learning Curve** — If you can write markdown, you can create presentations
- **Iterate Fast** — Generate multiple variants instantly and pick your favorite

## Features

- 🎨 **Style Transfer** — One or more reference images for a consistent, on-brand deck
- 🖼️ **Slide References** — Attach slide-specific photos or image globs directly in the outline
- 📚 **Outline Articles** — Declare source markdown/PDF references once in the outline
- 🧠 **Smart Layouts** — AI auto-selects optimal layouts based on your content
- 🔄 **Multiple Variants** — Generate several design options per slide
- 🎯 **Selective Regeneration** — Redo specific slides without starting over
- ⚡ **Blazing Fast** — Parallel generation with configurable concurrency
- 📄 **Auto PDF** — All slides combined into one file
- 🔌 **Multiple Providers** — OpenRouter and Volcengine (Doubao/Seedream)
- 🧪 **Valyu DeepResearch** — Turn a one-line idea into a researched, reviewable outline

## How It Works

Four steps — **research**, **outline**, **style**, **compose**:

1. **Research** — Write your topic in `work/idea.md`, run `python3 -m src.research.cli`, review `work/research.md`
2. **Outline** — Run `python3 -m src.outline.cli` to produce `outline_16.md`, `outline_25.md`, and `outline_36.md` in `work/` (same visual style; longer versions add slides)
3. **Style** — Run `python3 -m src.style.cli` to generate base-plate candidates, pick one (or type `r` to regenerate), then pick cover/transition/story references into `work/`
4. **Compose** — Run `python3 -m src.compose.cli` to produce one image per slide into `slides_YYYYMMDD_HHMMSS/`, combined into one PDF

Then **curate** (delete variants you don't love) and **polish** (`--page` to regenerate individual slides).

> 💡 **Pro tip:** Steps 1–3 share `./work/` — edit files between steps. Compose reads `work/` and writes a fresh timestamped output folder.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your API key (OpenRouter by default)
```

## Usage

### Research → Outline → Style → Compose

```bash
# Step 1: DeepResearch from work/idea.md
python3 -m src.research.cli

# Step 2: Generate three outline versions (16/25/36 content slides)
python3 -m src.outline.cli

# Step 3: Generate style references (4 candidates per stage)
python3 -m src.style.cli
# Interactive picker: enter 1-4 to pick, or r to regenerate that stage

# Pick a different outline length
python3 -m src.style.cli --outline work/outline_25.md

# Non-interactive: pre-select base,cover,transition,story indices
python3 -m src.style.cli --pick 1,2,1,3

# Step 4: Compose slide images (default outline: work/outline_16.md)
python3 -m src.compose.cli
```

### Compose

```bash
# Basic: compose slides with style references from work/ (1 variant per slide)
python3 -m src.compose.cli

# Generate multiple variants per slide
python3 -m src.compose.cli --copy 4

# Use a longer outline version
python3 -m src.compose.cli --outline work/outline_36.md

# Regenerate specific slides
python3 -m src.compose.cli --page "1,3,5-7"

# Rebuild slide_combined.pdf after curating variants (no API calls)
python3 -m src.compose.cli --pdf-only --output slides_20260520_220006
python3 -m src.compose.cli --pdf-only --output slides_20260520_220006 --variant 1

# Multiple explicit style files plus articles
python3 -m src.compose.cli --style cover.png --style body.png --article "docs/*.pdf"
```

### Research CLI Options (`python3 -m src.research.cli`)

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--mode` | Valyu DeepResearch mode: `fast`, `standard`, `heavy`, `max` |
| `--valyu-api-key` | Valyu API key (or `VALYU_API_KEY` / `[valyu] api_key`) |

### Outline CLI Options (`python3 -m src.outline.cli`)

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--slides` | Comma-separated content slide counts (default: `16,25,36`) |
| `--api-key` | OpenRouter API key for outline text generation |
| `--txt-model` | Text model (or `OPENROUTER_TXT_MODEL` / `[openrouter] txt_model`) |
| `--proxy` | HTTP/HTTPS proxy for OpenRouter text calls |

### Style CLI Options (`python3 -m src.style.cli`)

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Outline markdown file (default: `work/outline_16.md`) |
| `--candidates` | Style candidates per stage (default: 4) |
| `--pick` | Pre-select indices: `base,cover,transition,story` (e.g. `1,2,1,3`) |
| `--provider` | `openrouter` or `volcengine` (required if not in `.env`) |
| `--api-key` | API key for the selected provider |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |

### Compose CLI Options (`python3 -m src.compose.cli`)

| Option | Description |
|--------|-------------|
| `--work` | Work directory (default: `work/`) |
| `--outline` | Markdown outline (default: `work/outline_16.md`) |
| `--style` | Style reference image(s): path/glob (default: `work/style_*.png`; none found → first slide only) |
| `--copy` | Variants per slide (default: 1) |
| `--page` | Pages to generate (e.g., `1,3,5-7`) |
| `--article` | Reference docs, supports globs (e.g., `"docs/*.pdf"`) |
| `--output` | Output directory (default: `slides_YYYYMMDD_HHMMSS/`) |
| `--provider` | `openrouter` or `volcengine` (required if not in `.env`) |
| `--api-key` | API key for the selected provider |
| `--proxy` | HTTP/HTTPS proxy (OpenRouter only) |
| `--balance-only` | Print OpenRouter credits and exit |
| `--no-balance` | Skip credits line after a run |
| `--pdf-only` | Rebuild PDF from existing PNGs in `--output` (no API) |
| `--variant` | With `--pdf-only`: variant numbers to include (e.g. `1` or `1,2`) |

> **Credits:** After each OpenRouter run, remaining credits are printed unless `--no-balance` is passed. This requires an OpenRouter **Management API key** — set `OPENROUTER_MANAGEMENT_API_KEY` or `[openrouter] management_api_key`. Volcengine runs skip this.

## Input/Output Format

### Idea Input (`work/idea.md`)

Plain markdown with your presentation seed — title, audience, and core message.

### Work Directory (`work/`)

```
work/
├── idea.md              # presentation seed
├── research.md          # Valyu DeepResearch report
├── sources.md           # formatted bibliography for outline generation
├── style_base.md        # shared style + narrative scaffold for all outline versions
├── outline_16.md        # 16 content-slide outline (same style)
├── outline_25.md        # 25 content-slide outline (same style)
├── outline_36.md        # 36 content-slide outline (same style)
```

After the style step, `work/` also contains:

```
├── style_base.png       # chosen blank base plate (palette + typography moodboard)
├── style_cover.png      # chosen cover-slide style reference
├── style_transition.png # chosen transition/roadmap style reference
├── style_story.png      # chosen content/story-slide style reference
└── style_candidates/    # all candidates + numbered contact sheets
    ├── style_base.png           # copy of chosen base plate
    ├── style_base_v01..v04.png  # base candidates
    ├── style_base_choices.png   # numbered 2x2 contact sheet
    ├── style_cover_v01..v04.png
    ├── style_cover_choices.png
    └── ... (transition/story candidates + choices)
```

### Outline Format

Each `##` heading becomes a slide:

```markdown
# My Presentation

[Articles:
@examples/research-notes.md,
@examples/market-report.pdf
]

---

## Slide 1: Introduction
Your opening content here.

- Key point one
- Key point two

[Visual: hero image of the product]
[Reference: examples/founder_photo.png]

---

## Slide 2: The Problem
What challenge are we solving?

---

## Global Visual Requirements
**DO NOT DELETE** - configures visual style

- **Theme:** Modern tech aesthetic
- **Colors:** Primary: #2563EB, Accent: #10B981
- **Style:** Clean, minimal, professional
```

**Tips:**
- `[Visual: description]` — layout, composition, diagrams, icons, motifs (visual styles)
- `[Reference: path/or/glob.png]` — slide-specific image refs (leading `@` accepted)
- `[Articles: path1.md, path2.pdf]` — attach text references at the top of the outline
- Keep slides concise (~30 words max)
- Include **3-6 transition slides** (titles prefixed `Roadmap:`, each with a `progress bar N/total` marker) to split the deck into sections — added on top of the cover, ending, and requested content-slide count
- `## Appendix: Global Visual Requirements` — **text styles only** (colors + hex, fonts + sizes); do not duplicate layout/graphics here — those live in `[Visual:]` tags and style reference images

### Compose Output (`slides_YYYYMMDD_HHMMSS/`)

```
slides_20260202_143045/
├── slide_p01_v01.png    # Slide 1, variant 1
├── slide_p01_v02.png    # Slide 1, variant 2
├── slide_p02_v01.png    # Slide 2, variant 1
└── slide_combined.pdf   # All slides in one PDF
```

## Configuration

Create `.env` from the example:

```ini
# Default backend: openrouter or volcengine
provider = openrouter

# Shared settings (before first [section])
max_concurrent = 36

[volcengine]
api_key = your-ark-api-key-here
img_model = doubao-seedream-5-0-260128
txt_model = doubao-1-5-pro-32k-250115
use_proxy = false

[openrouter]
api_key = your-openrouter-api-key-here
# management_api_key = sk-or-v1-mgmt-...
img_model = google/gemini-3-pro-image-preview
txt_model = anthropic/claude-opus-4.6
use_proxy = true

[valyu]
api_key = your-valyu-api-key-here
# mode = standard
```

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
