---
name: design-style
description: Generate the deck style in WORK/style/ from a script and a design brief. Use when the user wants a visual style, style plates, or design_brief.md turned into images.
disable-model-invocation: true
---

# Design a style

Generate five style images from a script and a design brief: `style_base_noncontent.png`, `style_base_content.png`, `style_cover.png`, `style_transition.png`, `style_content.png`. Each image gets a `<name>_prompt.txt` sidecar.

## Inputs

- A work directory (default `~/work`, expanded to an absolute path, or a folder the user names). Call it `WORK`.
- `WORK/script_N.md` — required.
- `WORK/design_brief.md` — required, unless the user names another brief.

## Workflow

Run every command from the repo root. Pass absolute paths. The CLI defaults are relative to the repo and do not point at `~/work`. Do not read `.env`. Keys come from config. Stop on a failed check and report it.

### 1. Generate

Default to one candidate per image, which skips picking.

```bash
python3 -m src.design.cli --work WORK --script WORK/script_N.md --brief WORK/design_brief.md
```

Pass `--style DIR` when the images should go somewhere other than `WORK/style/`. Add `--provider` or `--proxy` only when the user asks.

### 2. Pick among candidates

There is no TTY, so a run with `--candidates` greater than 1 and no `--pick` keeps candidate 1 for every stage. It still writes every candidate and a contact sheet under `WORK/style/style_candidates/`.

```bash
python3 -m src.design.cli --work WORK --script WORK/script_N.md --brief WORK/design_brief.md --candidates 4
```

Show the contact sheets, in this order:

- `style_base_noncontent_choices.png`
- `style_base_content_choices.png`
- `style_cover_choices.png`
- `style_transition_choices.png`
- `style_content_choices.png`

Ask for one index per stage with AskQuestion. Then rerun with `--pick` in that same order (`base_noncontent,base_content,cover,transition,content`):

```bash
python3 -m src.design.cli --work WORK --script WORK/script_N.md --brief WORK/design_brief.md --candidates 4 --pick 1,1,2,1,3
```

`--pick` generates a new batch and selects within that batch. Indices from the sheets already shown do not refer to those files. To keep a cover, transition, or content candidate the user already saw, install it with `install_style_candidate`. A raw copy skips the 1280×720 downscale the CLI applies to plates.

```bash
python3 -c "
from pathlib import Path
from src.design.plates import install_style_candidate
install_style_candidate(
    Path('WORK/style/style_candidates/style_cover_v02.png'),
    Path('WORK/style/style_cover.png'),
)
"
```

Leave the two base images as candidate 1 unless you rerun: cover, transition, and content are generated from the chosen bases.

### 3. Show the style

Read and embed the five images from `WORK/style/`. Mention the prompt sidecars.

### 4. Hand off

Print the render command:

```bash
python3 -m src.render.cli --work WORK --script WORK/script_N.md --style WORK/style
```
