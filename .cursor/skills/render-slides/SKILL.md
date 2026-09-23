---
name: render-slides
description: Render slide PNGs and a PPTX from a script and style plates. Use when the user wants to generate, rerender, or rebuild slides, slide images, or the deck file.
disable-model-invocation: true
---

# Render slides

Compose one PNG per slide from the script and the style plates, and write a PPTX with speaker notes.

## Inputs

- A work directory (default `~/work`, expanded to an absolute path, or a folder the user names). Call it `WORK`.
- `WORK/script_N.md` — required.
- `WORK/style/` — the five plates. The generate command passes `--style`, so a missing or empty directory stops the run. Omit `--style` only when the intent is to generate slide 1 with no plates.

## Workflow

Run every command from the repo root. Pass absolute paths. The CLI defaults are relative to the repo and do not point at `~/work`. Do not read `.env`. Keys come from config. Stop on a failed check and report it.

### 1. Generate

```bash
python3 -m src.render.cli --work WORK --script WORK/script_N.md --style WORK/style
```

Optional flags, only when the user asks:

- `--copy 2` — variants per slide (`slide_p##_v01.png`, `slide_p##_v02.png`).
- `--page 3,7-9` — only those slides.
- `--provider openrouter` or `--provider volcengine`.
- `--no-balance` — skip the OpenRouter credits line.
- `--output WORK/image_YYYYMMDD_HHMMSS` — write into a named directory. The default is a new `WORK/image_YYYYMMDD_HHMMSS/`.

### 2. Rerender

Pass `--page` and either a new `--output` or the existing image directory the user wants updated.

```bash
python3 -m src.render.cli --work WORK --script WORK/script_N.md --style WORK/style --page 4,8 --output WORK/image_TS
```

### 3. Rebuild the PPTX

Use this when the PNGs already exist and no image API call is needed.

```bash
python3 -m src.render.cli --work WORK --script WORK/script_N.md --pptx-only --output WORK/image_TS --variant 1
```

`--output` is required with `--pptx-only`. `--variant` limits which `v##` files go into the deck. Speaker notes come from `[Speech:]` in the script.

### 4. Show the result

Output:

- `WORK/image_YYYYMMDD_HHMMSS/slide_p##_v##.png`
- `WORK/slides_YYYYMMDD.pptx`

Read and embed a few slide PNGs (cover, one content slide, one roadmap).

### 5. Hand off

Print the record command, using the image directory this run wrote:

```bash
python3 -m src.present.cli --work WORK --script WORK/script_N.md --output WORK/image_TS
```
