# VibeSliding

**Transform your ideas into stunning presentations in seconds.** Generate beautiful slide decks from simple markdown outlines using AI. No design skills required.

Stop wrestling with PowerPoint. Just write your content, pick a style, and let AI do the heavy lifting. Outputs high-quality PNG images + combined PDF ready to present.

## Why VibeSliding?

- **Save Hours** - What used to take hours now takes minutes. Focus on your message, not pixel-pushing.
- **Professional Results** - Every slide looks polished and cohesive, as if designed by a pro.
- **Zero Learning Curve** - If you can write markdown, you can create presentations.
- **Iterate Fast** - Generate multiple variants instantly and pick your favorite.

## Features

- **Style Transfer** - Apply any reference image to maintain consistent, on-brand design across all slides
- **Smart Layouts** - AI auto-selects optimal layouts (title, split-screen, bento grid, data focus) based on your content
- **Blazing Fast** - Parallel generation creates multiple slides and variants concurrently
- **Multiple Variants** - Generate several design options per slide to find the perfect look
- **Selective Pages** - Regenerate specific pages or ranges without redoing the entire deck
- **Context-Aware** - Include reference articles to ensure content accuracy and depth
- **Auto PDF** - Automatically combines all slides into a presentation-ready PDF

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your OpenRouter API key
```

## Usage

```bash
python3 -m src.cli --outline outline.md --style style.png --copy 4
```

| Option | Description |
|--------|-------------|
| `--outline` | Markdown outline (required) |
| `--style` | Style reference image |
| `--copy` | Variants per slide (default: 1) |
| `--page` | Pages to generate: `1`, `1,3,5`, `1-5` |
| `--article` | Reference doc for accuracy |
| `--output` | Output dir (default: `./output`) |

## Outline Format

```markdown
# PPT Outline: Title

---

## Slide 1: Introduction
- Key point
- Supporting detail
[Visual: diagram showing workflow]

---

## Global Visual Requirements
- **Theme:** #hex colors
- **Fonts:** Font family
```

Use `[Visual: ...]` hints to guide imagery. "Global Visual Requirements" sets consistent styling (not rendered as slide).

## Output

```
output/
├── slide_p01_v01.png
├── slide_p01_v02.png
└── slide_combined.pdf
```

## Config (.env)

```ini
[openrouter]
api_key = your-key
model = google/gemini-3-pro-image-preview
max_concurrent = 36
proxy = socks5://127.0.0.1:1080  # optional
```

Priority: CLI args > env vars > .env file

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Missing API key | Set in `.env` or `OPENROUTER_API_KEY` |
| Slow generation | Increase `max_concurrent` |
| Style mismatch | Use 1920x1080 style image |
| Content errors | Add `--article` reference |
