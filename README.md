# VibeSliding

**Transform your ideas into stunning presentations in seconds.** Generate beautiful slide decks from simple markdown outlines using AI. No design skills required.

Stop wrestling with PowerPoint. Just write your content, pick a style, and let AI do the heavy lifting. Outputs high-quality PNG images + combined PDF ready to present.

## Why VibeSliding?

- **Save Hours** - What used to take hours now takes minutes. Focus on your message, not pixel-pushing.
- **Professional Results** - Every slide looks polished and cohesive, as if designed by a pro.
- **Zero Learning Curve** - If you can write markdown, you can create presentations.
- **Iterate Fast** - Generate multiple variants instantly and pick your favorite.

## How It Works

Creating beautiful presentations is a breeze with this simple 4-step workflow:

### Step 1: Prepare Your Ingredients 📝
Gather your creative assets — an **article** for content reference, an **outline** for structure, and a **style image** to set the visual tone. These three files are all you need to get started.

### Step 2: Generate Multiple Variants ✨
Run VibeSliding with `--copy 4` to generate **4 unique design variants** for each slide. All variants are automatically combined into a single PDF for easy side-by-side comparison. More options = more creative possibilities!

### Step 3: Curate Your Favorites 🎯
Browse through the variants and **keep the best version** for each slide. Simply delete the ones you don't love. Your presentation is already taking shape!

### Step 4: Perfect & Polish 🔄
Not 100% happy with a slide? No problem! Use `--page` to **regenerate just that slide** with fresh variants. Repeat until every slide is exactly how you envisioned it.

> **Pro tip:** This iterative workflow lets you achieve perfection without starting from scratch. Mix and match the best elements until your deck is presentation-ready!

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

### Basic Command
```bash
python3 -m src.cli --outline outline.md --style style.png --copy 4
```

### Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--outline` | Markdown outline (required) | `--outline slides.md` |
| `--style` | Style reference image | `--style corporate.png` |
| `--copy` | Variants per slide (default: 1) | `--copy 4` |
| `--page` | Specific pages to generate | `--page "1,3,5-7"` |
| `--article` | Reference doc(s) with glob support | `--article "*.pdf"` |
| `--output` | Custom output directory | `--output my_slides` |
| `--api-key` | OpenRouter API key | `--api-key sk-...` |

### Advanced Examples

#### Generate All Slides with 4 Variants Each
```bash
python3 -m src.cli \
  --outline presentation.md \
  --style brand_style.png \
  --copy 4 \
  --article "research/*.pdf"
```

#### Regenerate Specific Slides Only
```bash
# Regenerate just slide 3
python3 -m src.cli --outline outline.md --style style.png --page 3 --copy 4

# Regenerate slides 1, 3, and 5-7
python3 -m src.cli --outline outline.md --style style.png --page "1,3,5-7" --copy 4
```

#### Use Multiple Reference Articles
```bash
# Multiple explicit files
python3 -m src.cli --outline outline.md --article paper1.pdf --article notes.md

# Glob patterns
python3 -m src.cli --outline outline.md --article "articles/*.pdf"

# Combined approach
python3 -m src.cli --outline outline.md --article main.pdf --article "refs/*.md"
```

#### Custom Output Directory
```bash
# Use specific directory name (may overwrite)
python3 -m src.cli --outline outline.md --output final_presentation

# Restore old behavior (always use "output/")
python3 -m src.cli --outline outline.md --output output
```

### Output Directories

By default, each run creates a **unique timestamped directory** to prevent overwriting:

**Format**: `output_YYYYMMDD_HHMMSS`  
**Example**: `output_20260202_143045` (Feb 2, 2026 at 2:30:45 PM)

**Benefits:**
- ✅ Never lose previous results
- ✅ Compare different runs side by side
- ✅ Experiment safely without fear of overwriting
- ✅ Built-in versioning by timestamp

**Custom directories:**
```bash
# Use specific name
python3 -m src.cli --outline outline.md --output my_presentation

# Use old default behavior
python3 -m src.cli --outline outline.md --output output
```

### Multiple Articles Support

Reference multiple documents for richer, more accurate content generation:

**Features:**
- 📚 **Multiple files**: Specify `--article` multiple times
- 🔍 **Glob patterns**: Use wildcards like `*.pdf` or `docs/*.md`
- 📄 **Mixed formats**: Combine PDF and Markdown files
- 🎯 **Smart context**: All articles inform slide content generation

**Examples:**
```bash
# Single article
python3 -m src.cli --outline outline.md --article research.pdf

# Multiple articles
python3 -m src.cli --outline outline.md \
  --article paper1.pdf \
  --article paper2.md \
  --article literature_review.pdf

# All PDFs in directory
python3 -m src.cli --outline outline.md --article "references/*.pdf"

# All Markdown files
python3 -m src.cli --outline outline.md --article "notes/*.md"

# Combined patterns
python3 -m src.cli --outline outline.md \
  --article main_paper.pdf \
  --article "supplementary/*.md" \
  --article "data/*.pdf"
```

**Supported formats:**
- `.pdf` - PDF documents
- `.md` - Markdown files  
- `.markdown` - Markdown files

**Note:** Remember to quote glob patterns: `"*.pdf"` not `*.pdf`

## Outline Format

Your markdown outline defines the presentation structure. Each H2 heading becomes a slide:

```markdown
# PPT Outline: My Presentation Title

---

## Slide 1: Introduction
Welcome to the presentation! This is the opening slide.

- Key point about the topic
- Supporting detail with context
- Call to action

[Visual: hero image showing team collaboration]

---

## Slide 2: Problem Statement
What challenge are we solving?

- Current pain points
- Market gap analysis
- Customer feedback highlights

---

## Slide 3: Our Solution
Here's how we address the problem...

[Visual: product screenshot or workflow diagram]

---

## Global Visual Requirements
**DO NOT DELETE THIS SECTION - it configures the visual style**

- **Theme:** Modern tech aesthetic
- **Colors:** Primary: #2563EB (blue), Accent: #10B981 (green), Background: #F9FAFB
- **Fonts:** Headings: Inter Bold, Body: Inter Regular
- **Style:** Clean, minimal, professional with subtle gradients
- **Graphics:** Flat design with occasional depth via shadows
```

### Outline Tips

- **H2 headings** = Slides (e.g., `## Slide 1: Title`)
- **Visual hints** = Guide imagery with `[Visual: description]`
- **Global Visual Requirements** = Sets consistent styling (not rendered as a slide)
- **Bullet points** = Automatically formatted with icons
- **Keep it concise** = Max 30 words per slide unless it's a list

### Visual Hints

Use `[Visual: ...]` tags to guide AI image generation:
- `[Visual: workflow diagram with 3 steps]`
- `[Visual: team photo in modern office]`
- `[Visual: data chart showing growth trend]`
- `[Visual: product screenshot on laptop]`

## Output Structure

Each generation creates a directory with all slides and a combined PDF:

```
output_20260202_143045/
├── slide_p01_v01.png          # Slide 1, variant 1
├── slide_p01_v02.png          # Slide 1, variant 2
├── slide_p01_v03.png          # Slide 1, variant 3
├── slide_p01_v04.png          # Slide 1, variant 4
├── slide_p02_v01.png          # Slide 2, variant 1
├── slide_p02_v02.png          # Slide 2, variant 2
├── slide_p02_v03.png          # Slide 2, variant 3
├── slide_p02_v04.png          # Slide 2, variant 4
└── slide_combined.pdf         # All slides in one PDF
```

**File naming:**
- `slide_p{N:02d}_v{M:02d}.png` where N = slide number, M = variant number
- Example: `slide_p03_v02.png` = Slide 3, Variant 2

**Features:**
- All individual slides saved as high-quality PNG (1920x1080)
- Combined PDF automatically created for easy sharing
- Alphabetical sorting matches slide order

**Git ignore:** All `output*` directories are automatically ignored (see `.gitignore`).

## Configuration

### .env File

Create a `.env` file in the project root (copy from `.env.example`):

```ini
[openrouter]
api_key = your-openrouter-api-key-here
model = google/gemini-3-pro-image-preview
max_concurrent = 36
proxy = socks5://127.0.0.1:1080  # optional
```

**Configuration options:**

| Setting | Description | Default | Notes |
|---------|-------------|---------|-------|
| `api_key` | OpenRouter API key | None | **Required** - Get from openrouter.ai |
| `model` | AI model to use | `google/gemini-3-pro-image-preview` | Must support image generation |
| `max_concurrent` | Parallel requests | 36 | Higher = faster (if API allows) |
| `proxy` | SOCKS5 proxy URL | None | Optional, format: `socks5://host:port` |

**Configuration priority:**
1. CLI arguments (`--api-key`)
2. Environment variables (`OPENROUTER_API_KEY`)
3. `.env` file values

### Environment Variables

Alternative to `.env` file:

```bash
export OPENROUTER_API_KEY="your-key"
export OPENROUTER_MODEL="google/gemini-3-pro-image-preview"
export OPENROUTER_MAX_CONCURRENT="36"
export OPENROUTER_PROXY="socks5://127.0.0.1:1080"
```

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Missing API key** | Add to `.env` file or set `OPENROUTER_API_KEY` environment variable |
| **Slow generation** | Increase `max_concurrent` in `.env` (try 48 or 64) |
| **Style mismatch** | Use 1920x1080 (16:9) style image for best results |
| **Content inaccuracy** | Add reference articles with `--article` for better context |
| **No files match glob** | Check pattern is quoted: `"*.pdf"` and files exist |
| **Out of memory** | Reduce `max_concurrent` or generate fewer variants |
| **Rate limiting** | Reduce `max_concurrent` to stay within API limits |

### Debug Tips

**Check API key:**
```bash
grep api_key .env
```

**Test with single slide:**
```bash
python3 -m src.cli --outline outline.md --page 1 --copy 1
```

**Verify file paths:**
```bash
ls -la examples/outline.md examples/style.png
```

**Check glob pattern:**
```bash
# Test what files match
ls articles/*.pdf
```

### Getting Help

- **Documentation**: Check the comprehensive guides in this repo
- **Issues**: Report bugs via GitHub Issues
- **API Status**: Check OpenRouter status page
- **Examples**: See `examples/` directory for working samples

## Performance Tips

### Optimization Strategies

1. **Adjust Concurrency**
   - Start with `max_concurrent = 36`
   - Increase to 48-64 if API allows
   - Decrease to 12-24 if hitting rate limits

2. **Batch Generation**
   - Generate all slides once with `--copy 4`
   - Then regenerate only specific slides that need improvement
   - Use `--page` to target specific slides

3. **Efficient Workflow**
   ```bash
   # Step 1: Generate all with 2 variants (fast preview)
   python3 -m src.cli --outline outline.md --style style.png --copy 2
   
   # Step 2: Review, then regenerate favorites with 6 variants
   python3 -m src.cli --outline outline.md --style style.png --page "1,3,5" --copy 6
   ```

4. **Article Loading**
   - Limit articles to 5-10 moderate-sized files
   - Convert PDFs to Markdown if only text is needed
   - Use glob patterns to avoid manually listing files

### Cost Optimization

- **Fewer variants first**: Start with `--copy 2`, increase only for final slides
- **Targeted regeneration**: Use `--page` to regenerate only what needs work
- **Preview mode**: Generate first slide only (omit `--style`) to test prompts

## Advanced Usage

### Real-World Workflows

#### Academic Presentation
```bash
# Generate with research papers as context
python3 -m src.cli \
  --outline conference_talk.md \
  --style academic_theme.png \
  --article "papers/*.pdf" \
  --article literature_review.md \
  --copy 3
```

#### Business Quarterly Review
```bash
# Use multiple data sources
python3 -m src.cli \
  --outline q4_review.md \
  --style corporate_brand.png \
  --article "reports/*.pdf" \
  --article "data/*.md" \
  --copy 4 \
  --page "1-10"
```

#### Technical Documentation
```bash
# Reference API docs and guides
python3 -m src.cli \
  --outline tech_slides.md \
  --article api_spec.pdf \
  --article README.md \
  --article "docs/guides/*.md" \
  --copy 2
```

### Page Selection Examples

```bash
# Single page
--page 1

# Multiple specific pages
--page "1,3,5"

# Range
--page "1-5"

# Combined
--page "1,3-5,7,10-12"

# Just the ending slides
--page "8-10"
```

### Comparing Styles

```bash
# Style A
python3 -m src.cli --outline outline.md --style styleA.png --copy 3 --output styleA_test

# Style B
python3 -m src.cli --outline outline.md --style styleB.png --copy 3 --output styleB_test

# Compare outputs in separate directories
```

### Integration with Scripts

```bash
#!/bin/bash
# generate_and_review.sh

# Generate slides
python3 -m src.cli --outline "$1" --style "$2" --copy 4

# Find the latest output directory
latest=$(ls -t | grep "^output_" | head -n1)

# Open PDF for review
open "$latest/slide_combined.pdf"

# Print summary
echo "Generated in: $latest"
ls -1 "$latest" | wc -l | xargs echo "Total files:"
```

## Project Structure

```
vibesliding/
├── src/                      # Source code
│   ├── __init__.py          # Package initialization
│   ├── api_client.py        # OpenRouter API client with retry logic
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management
│   ├── generator.py         # Image generation orchestrator
│   ├── output.py            # Output handling and PDF creation
│   └── parser.py            # Markdown parsing
├── examples/                 # Example files
│   ├── outline.md           # Sample presentation outline
│   ├── style.png            # Sample style reference
│   ├── article.md           # Sample article
│   └── *.pdf                # Sample PDF articles
├── .env.example             # Example configuration
├── .gitignore               # Git ignore rules (includes output*)
├── requirements.txt         # Python dependencies
├── run.sh                   # Example run script
└── README.md                # This file
```

## Documentation

Comprehensive guides are available:

- **REFACTORING_SUMMARY.md** - Code quality improvements
- **REFACTORING_EXAMPLES.md** - Before/after code examples
- **MULTIPLE_ARTICLES_FEATURE.md** - Multiple articles guide
- **MULTIPLE_ARTICLES_IMPLEMENTATION.md** - Technical details
- **ARTICLES_QUICK_REFERENCE.md** - Quick reference for articles
- **TIMESTAMPED_OUTPUT_FEATURE.md** - Timestamped output guide
- **TIMESTAMPED_OUTPUT_IMPLEMENTATION.md** - Technical details
- **OUTPUT_QUICK_REFERENCE.md** - Quick reference for outputs
- **GITIGNORE_OUTPUT.md** - Git ignore configuration

## Contributing

Contributions welcome! Areas for improvement:

- PDF text extraction for `article_pdf` parameter
- Additional AI model support
- Custom layout templates
- Batch processing improvements
- UI/web interface

## License

See LICENSE file for details.

## Credits

Built with:
- **OpenRouter** - AI model API
- **httpx** - Async HTTP client
- **Pillow** - Image processing
- **img2pdf** - PDF generation
- **Click** - CLI framework

---

**Happy Sliding! 🎨✨**

Transform your markdown outlines into beautiful presentations in minutes, not hours.
