---
name: write-script
description: Expand a deck plan and its facts into a full script with one text-model call per slide. Use when the user wants to write, rewrite, or regenerate script_N.md from plan_N.md and facts.md.
disable-model-invocation: true
---

# Write a script

Turn `plan_N.md` and `facts.md` into `script_N.md`. The CLI makes one text-model call per slide.

## Inputs

- A work directory (default `~/work`, expanded to an absolute path, or a folder the user names). Call it `WORK`.
- `WORK/plan_N.md` — required. `N` is the content-slide count.
- `WORK/facts.md` — required. The CLI stops before any API call if it is missing or empty; run the plan-deck skill to create it. Each slide's prompt gets the facts its `Evidence:` IDs cite first, then the most related other facts, within about 4,000 characters.

Both files come from the plan-deck skill. Before generating, run `python3 -m src.plan.cli --plan WORK/plan_N.md` and stop if it warns about facts: a cited ID missing from `facts.md` means the model writes that slide without its evidence.
- `WORK/idea.md` — optional. The CLI warns and continues if it is missing or empty. Tell the user before spending the API call.

## Workflow

Run every command from the repo root. Pass absolute paths. The CLI defaults (`work/`, `work/script_16.md`) are relative to the repo and do not point at `~/work`. Do not read `.env`. Keys come from config. Stop on a failed check and report it.

### 1. Generate

```bash
python3 -m src.write.cli --work WORK --plan WORK/plan_N.md
```

Add `--txt-model` or `--proxy` only when the user asks.

### 2. Retry failed slides

If the CLI prints `Failed slides:`, rerun only those pages. The script must already exist.

```bash
python3 -m src.write.cli --work WORK --plan WORK/plan_N.md --page 3,7-9
```

Use the page list the CLI printed.

### 3. Check balance and speech length

Measure every slide against the Visual/Text Balance targets and the Speech Tags lengths in `.cursor/rules/outline-standards.mdc`.

```bash
python3 -c "
from pathlib import Path
from src.core.validate import measure_slide_balance
text = Path('WORK/script_N.md').read_text()
for row in measure_slide_balance(text):
    print(f'{row.ratio:.2f}\tbullets={row.bullets}\ttext={row.text_words}\tvisual={row.visual_words}\tspeech={row.speech_seconds:.0f}s\t{row.title}')
"
```

| Role | Bullet lines | Bullet words | Visual words | Ratio | Speech |
|---|---|---|---|---|---|
| Content | 6 | 115-195 | 100-170 | 0.85-1.35 | 60-120s |
| Transition (`Roadmap:`) | 4 | 80-100 | 100-140 | under 1.0 | 20-40s |
| Cover / Ending | 3-4 | 70-100 | 100-140 | under 1.0 | 20-40s |

- **Ratio:** The band applies to content slides only. Non-content slides pass at any ratio under 1.0, meaning the visual outweighs the bullets.
- **Speech:** Speech time is estimated at 150 words, or 300 Chinese characters, per minute. The CLI prints the same balance and speech-length warnings after every run.

Report content slides outside the ratio band, non-content slides at 1.0 or above, and slides whose speech is outside its range. Offer a `--page` rewrite for those slides. Do not rewrite them unless the user asks.

### 4. Hand off

Print the design command:

```bash
python3 -m src.design.cli --work WORK --script WORK/script_N.md --brief WORK/design_brief.md
```
