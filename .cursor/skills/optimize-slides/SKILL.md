---
name: optimize-slides
description: Co-optimize a script and its rendered slides against the outline standards — logical flow, self-consistency, and density (too crowded or too sparse). Reviews script_N.md beside its slide PNGs, uses web search to verify or sharpen facts, fixes the script, and rerenders only the changed slides. Use when the user wants to optimize, polish, review, or fix a rendered deck's script and slides together.
disable-model-invocation: true
---

# Optimize slides

Improve `script_N.md` and its rendered slides together. The script is the source of truth: fix problems in the script, then rerender. Never edit PNGs by hand.

## Inputs

- A work directory (default `~/work`, expanded to an absolute path, or a folder the user names). Call it `WORK`.
- `WORK/script_N.md` — required.
- `WORK/image_TS/` — the rendered slides (`slide_p##_v##.png`). Use the directory the user names, otherwise the newest `WORK/image_*/`. If none exists, review the script only and hand off to the render-slides skill.
- `WORK/facts.md`, `WORK/plan_N.md`, `WORK/idea.md`, `WORK/design_brief.md` — read when present, for grounding and intent.

## Workflow

Run every command from the repo root with absolute paths. Do not read `.env`. Stop on a failed check and report it.

### 1. Read the standards, the script, and every slide

Read `.cursor/rules/outline-standards.mdc`. Read the script end to end, then view every slide PNG (`v01` unless the user names a variant) next to its script block.

### 2. Measure

```bash
python3 -c "
from pathlib import Path
from src.core.validate import validate_outline, balance_warnings, speech_warnings, measure_slide_balance
text = Path('WORK/script_N.md').read_text()
for row in measure_slide_balance(text):
    print(f'{row.ratio:.2f}\t{row.role}\tbullets={row.bullets}\ttext={row.text_words}\tvisual={row.visual_words}\tspeech={row.speech_seconds:.0f}s\t{row.title}')
for w in validate_outline(text).warnings + balance_warnings(text) + speech_warnings(text):
    print('WARN', w)
"
```

The warnings check only the ratio and speech time. Also compare each row with the word ranges in the Targets table: a slide can sit inside the ratio band and still be crowded (both counts over the maximum) or sparse (both under the minimum).

### 3. Review: one issue list per slide

**Logical flow (deck level)**

- Read the titles alone, in order: they should form one argument, from the hook's question to the ending's answer.
- Each section moves setup → mechanism → evidence → implication, with no duplicated slide and no missing step.
- Each content slide's bridge sentence previews the next slide's actual message.
- Callbacks name slides that really came earlier and restate them accurately.
- Roadmap bullets, transition titles, and section contents use the same section names and order.

**Self-consistency**

- Within a slide, the title, bullets, `[Visual:]`, and `[Speech:]` carry one message and one metaphor.
- Across the deck, terms, names, numbers, and units match `facts.md` and each other.
- Script against PNG: the rendered title keeps the script's wording, the on-slide labels match the bullets, numbers render correctly, and there is no garbled, misspelled, or invented text. Content slides show only `Slide number: N`, and the two-tone background matches the slide's role.

**Density: too crowded or too sparse**

| Signal | Too crowded | Too sparse |
|---|---|---|
| Script | More than 6 bullet lines, words over the Targets maximum, a `[Visual:]` with more than about 4 panels or many labeled parts | Thin or one-clause bullets, words under the Targets minimum, a one-line `[Visual:]`, a visual that only repeats the title |
| PNG | Small or cramped text, overlapping labels, text touching the edges, no whitespace | Large empty regions, a lone icon, a composition that says nothing the title doesn't |

- **Crowded:** Use the text-heavy fixes in the standards: fold into the takeaway, move elaboration to `[Speech:]`, cut panels. Splitting a slide changes the content-slide count, so ask the user first with AskQuestion.
- **Sparse:** Use the visual-heavy fixes: add the reasoning the image can't show, anchor the visual's focal parts in the bullets, and bring in a concrete fact (step 4). Never pad.

### 4. Web search to ground and sharpen

Use WebSearch, then WebFetch on the primary source, when:

- A claim has no matching fact in `facts.md`, or its number conflicts with another slide.
- A vague phrase ("much faster", "widely used") needs a verified figure.
- A sparse slide needs a concrete example, date, or number.

Confirm the exact figure and unit on the fetched page. Add it to `facts.md` in the same pass as `- **F## Short name.** The fact — [source](URL)`, using the next unused ID, and add the ID to that slide's `Evidence:` line in `plan_N.md`. Write it in the deck's language, using the same wording everywhere it appears. If no source states it, keep the claim qualitative. Never invent a number.

### 5. Fix the script

- Make surgical edits. Leave strong slides alone, and keep the deck's title, arc, voice, and language.
- When one part of a slide changes, update the others so title, bullets, visual, and speech still agree.
- Do not change slide count, section order, or `[Style:]` tags without asking.
- Mirror changed titles and claims into `plan_N.md` so a later write rerun doesn't revert them.
- Render-only glitches (a one-off misspelling on an otherwise faithful slide) need a rerender, not an edit. Recurring garbled text means the slide asks for too much on-image text, so shorten the labels.

Measure again (step 2). Repeat until no warnings remain, for at most two rounds.

### 6. Rerender the changed slides

Rerendering spends image API calls. Show the page list and ask before running. First copy the old PNGs of those pages into `WORK/image_TS_before/`, then:

```bash
python3 -m src.render.cli --work WORK --script WORK/script_N.md --style WORK/style --page 4,8 --output WORK/image_TS
python3 -m src.render.cli --work WORK --script WORK/script_N.md --pptx-only --output WORK/image_TS --variant 1
```

View each new PNG and repeat the step-3 checks on it. Rerender a slide at most twice more. If it still fails, report it.

### 7. Report

- Per changed slide: the problem (flow, consistency, crowded, or sparse) and the fix, in one line.
- Facts added or corrected, with their source URLs.
- Before/after images for the two or three biggest changes, and any warnings that remain.
- Hand off to recording:

```bash
python3 -m src.present.cli --work WORK --script WORK/script_N.md --output WORK/image_TS
```
