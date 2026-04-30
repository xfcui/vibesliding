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
- 🧠 **Smart Layouts** — AI auto-selects optimal layouts based on your content
- 🔄 **Multiple Variants** — Generate several design options per slide
- 🎯 **Selective Regeneration** — Redo specific slides without starting over
- ⚡ **Blazing Fast** — Parallel generation for speed
- 📄 **Auto PDF** — All slides combined into one file

## How It Works

### Step 1: Prepare Your Ingredients 📝
Gather your creative assets — an **article** for content reference, an **outline** for structure, and **style reference image(s)** (paths or a glob like `examples/style_*.png`) to set the visual tone.

### Step 2: Generate Multiple Variants ✨
Run with `--copy 4` to generate **4 unique design variants** for each slide. All variants are combined into a single PDF for easy comparison.

### Step 3: Curate Your Favorites 🎯
Browse through the variants and **keep the best version** for each slide. Simply delete the ones you don't love.

### Step 4: Perfect & Polish 🔄
Use `--page` to **regenerate just that slide** with fresh variants. Repeat until every slide is exactly how you envisioned it.

> 💡 **Pro tip:** This iterative workflow lets you achieve perfection without starting from scratch!

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your OpenRouter API key
```

## Usage

```bash
# Basic: generate slides with style references (glob matches multiple PNGs)
python3 -m src.cli --outline outline.md --style "examples/style_*.png"

# Generate 4 variants per slide (recommended!)
python3 -m src.cli --outline outline.md --style "examples/style_*.png" --copy 4

# Regenerate specific slides
python3 -m src.cli --outline outline.md --style "examples/style_*.png" --page "1,3,5-7" --copy 4

# Multiple explicit files (repeat --style) plus articles
python3 -m src.cli --outline outline.md --style cover.png --style body.png --article "docs/*.pdf"
```

### Options

| Option | Description |
|--------|-------------|
| `--outline` | Markdown outline (required) |
| `--style` | Style reference image(s): path and/or glob; repeat `--style` for multiple patterns (omit for first slide only) |
| `--copy` | Variants per slide (default: 1) |
| `--page` | Specific pages to generate (e.g., `1,3,5-7`) |
| `--article` | Reference docs (supports glob patterns) |
| `--output` | Custom output directory |
| `--api-key` | OpenRouter API key (or use `.env`) |
| `--proxy` | HTTP/HTTPS proxy URL |

## Outline Format

Each H2 heading becomes a slide:

```markdown
# My Presentation

---

## Slide 1: Introduction
Your opening content here.

- Key point one
- Key point two

[Visual: hero image of the product]

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
- Keep slides concise (~30 words max)
- Global Visual Requirements sets the overall look

## Output

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
# Optional: proxy for API requests
proxy = socks5://127.0.0.1:1080

[openrouter]
api_key = your-openrouter-api-key-here
model = google/gemini-3.1-flash-image-preview
max_concurrent = 36
```

Get your API key at [openrouter.ai](https://openrouter.ai/keys)

## Examples

Check out the `examples/` folder for sample outlines and style references to get started quickly!

## License

See LICENSE file for details.

---

**Happy Sliding! 🎨✨** Transform your markdown into beautiful presentations in minutes, not hours.
