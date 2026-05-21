# VibeSliding ✨

**Transform ideas into stunning presentations in seconds.** Generate beautiful slide decks from markdown outlines using AI. No design skills required.

Stop wrestling with PowerPoint. Just write your content, pick a style, and let AI do the heavy lifting.

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
- ⚡ **Blazing Fast** — Parallel generation for speed
- 📄 **Auto PDF** — All slides combined into one file
- 🔌 **Multiple Providers** — Support for Volcengine (Doubao) and OpenRouter

## How It Works

1. **Prepare Your Ingredients** — Gather your creative assets: an **article** for content reference, an **outline** for structure, and **style reference image(s)** (paths or a glob like `examples/style_*.png`) to set the visual tone.
2. **Generate Multiple Variants** — Run with `--copy 4` to generate **4 unique design variants** for each slide. All variants are combined into a single PDF for easy comparison.
3. **Curate Your Favorites** — Browse through the variants and **keep the best version** for each slide. Simply delete the ones you don't love.
4. **Perfect & Polish** — Use `--page` to **regenerate just that slide** with fresh variants. Repeat until every slide is exactly how you envisioned it.

> 💡 **Pro tip:** This iterative workflow lets you achieve perfection without starting from scratch!

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your API key (OpenRouter by default)
```

## Usage

```bash
# Basic: generate slides with style references (glob matches multiple PNGs)
python3 -m src.cli --outline outline.md --style "examples/style_*.png"

# Generate 4 variants per slide (recommended!)
python3 -m src.cli --outline outline.md --style "examples/style_*.png" --copy 4

# Regenerate specific slides
python3 -m src.cli --outline outline.md --style "examples/style_*.png" --page "1,3,5-7" --copy 4

# Rebuild slide_combined.pdf after deleting unwanted variants (no API calls)
python3 -m src.cli --pdf-only --output output_20260520_220006
python3 -m src.cli --pdf-only --output output_20260520_220006 --variant 1

# Multiple explicit files (repeat --style) plus articles
python3 -m src.cli --outline outline.md --style cover.png --style body.png --article "docs/*.pdf"
```

### Options

| Option | Description |
|--------|-------------|
| `--outline` | Markdown outline (required for generation; omit with `--balance-only`) |
| `--style` | Style reference image(s): path and/or glob; repeat `--style` for multiple patterns (omit for first slide only) |
| `--copy` | Variants per slide (default: 1) |
| `--page` | Specific pages to generate (e.g., `1,3,5-7`) |
| `--article` | Reference docs (supports glob patterns) |
| `--output` | Custom output directory |
| `--provider` | Image API provider (`openrouter` or `volcengine`; required if not in `IMAGE_PROVIDER` or `.env`) |
| `--api-key` | API key for the selected provider (or use `.env`) |
| `--proxy` | HTTP/HTTPS proxy URL for OpenRouter only |
| `--balance-only` | Print OpenRouter credits from the API and exit (OpenRouter only; no `--outline`) |
| `--no-balance` | Skip the OpenRouter credits line after a normal run |
| `--pdf-only` | Rebuild `slide_combined.pdf` from existing `slide_p##_v##.png` in `--output` (no `--outline`, no API) |
| `--variant` | With `--pdf-only`: variant numbers to include (e.g. `1` or `1,2`); default: all PNGs in the folder |

After each successful run with **OpenRouter**, the CLI prints remaining credits (from `GET /api/v1/credits`) unless you pass `--no-balance`. That endpoint expects an OpenRouter **Management API key**; add `OPENROUTER_MANAGEMENT_API_KEY` or `[openrouter] management_api_key` alongside your normal `api_key`. Volcengine runs never fetch or print this.

## Input/Output Format

### Outline Format

Each H2 heading becomes a slide:

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
- Use `[Visual: description]` to guide AI imagery
- Use `[Reference: path/or/glob.png]` for slide-specific image references; a leading `@` is accepted, e.g. `[Reference: @examples/data.png]`
- Use `[Article: path.md]` or `[Articles: path1.md, path2.pdf]` near the top of the outline to attach text references automatically
- Keep slides concise (~30 words max)
- Global Visual Requirements sets the overall look

### Output

Each run creates a timestamped directory:

```
output_20260202_143045/
├── slide_p01_v01.png    # Slide 1, variant 1
├── slide_p01_v02.png    # Slide 1, variant 2
├── slide_p02_v01.png    # Slide 2, variant 1
└── slide_combined.pdf   # All slides in one PDF
```

## Configuration

Create `.env` from the example:

```ini
# Default backend: openrouter or volcengine (Ark, no proxy unless use_proxy below)
provider = openrouter

# Shared settings (apply before first [section])
max_concurrent = 36

[volcengine]
api_key = your-ark-api-key-here
model = doubao-seedream-5-0-260128
use_proxy = false

[openrouter]
api_key = your-openrouter-api-key-here
# Optional: Management API key for balance line only — https://openrouter.ai/settings/management-keys
# management_api_key = sk-or-v1-mgmt-...
model = google/gemini-3-pro-image-preview
use_proxy = true
```

## Examples

Check out the `examples/` folder for sample outlines and style references to get started quickly!

## License

See LICENSE file for details.

---

**Happy Sliding! 🎨✨** Transform your markdown into beautiful presentations in minutes, not hours.
