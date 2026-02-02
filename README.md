# VibeSliding

Generate slide decks from markdown outlines using AI. Outputs PNG images + combined PDF.

## Features

- **Style Transfer** - Apply a reference image to maintain consistent design across slides
- **Smart Layouts** - Auto-selects optimal layouts (title, split-screen, bento grid, data focus)
- **Parallel Generation** - Generate multiple slides/variants concurrently
- **Multiple Variants** - Generate several design options per slide for comparison
- **Selective Pages** - Generate specific pages or ranges
- **Context-Aware** - Include reference articles for content accuracy
- **Auto PDF** - Combines all slides into a presentation deck

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
