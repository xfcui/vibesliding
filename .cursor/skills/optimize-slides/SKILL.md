---
name: optimize-slides
description: Co-optimize a script and its rendered slides against the outline standards — logical flow, self-consistency across title, bullets, visual, speech, and PNG, density (too crowded or too sparse), and fidelity to references (facts.md sources, [Reference:] images, design brief). Reviews script_N.md beside its slide PNGs, verifies facts against their cited sources, fixes the script, and rerenders only the changed slides. Use when the user wants to optimize, polish, review, verify, or fix a rendered deck's script and slides together.
disable-model-invocation: true
---

# Optimize slides

Improve `script_N.md` and its rendered slides together. The script is the source of truth: fix problems in the script, then rerender. Never edit PNGs by hand.

## Inputs

- A work directory (default `~/work`, expanded to an absolute path, or a folder the user names). Call it `WORK`.
- `WORK/script_N.md` — required.
- `WORK/image_TS/` — the rendered slides (`slide_p##_v##.png`). Use the directory the user names, otherwise the newest `WORK/image_*/`. If none exists, review the script only and hand off to the render-slides skill.
- `WORK/facts.md`, `WORK/plan_N.md`, `WORK/idea.md`, `WORK/design_brief.md` — read when present, for grounding and intent.
- Every `[Reference: ...]` image the script declares — the render stage sends these to the model, so the slide should agree with them.
- Hand-finished slides — a PNG with a sibling such as `slide_p38_v01_noqr.png` was edited after rendering (a real QR code pasted in). Never rerender these; report issues instead.

## Workflow

Run every command from the repo root with absolute paths. Do not read `.env`. Stop on a failed check and report it.

The user may edit the script, plan, or facts while you work. Re-read a slide block right before editing it. If an edit reports "string not found", grep for both the old and new text before retrying — the edit may have landed, or the user may have changed the text.

### 1. Read the standards, the script, every slide, and every reference

Read `.cursor/rules/outline-standards.mdc`. Read the script end to end, then view every slide PNG (`v01` unless the user names a variant) next to its script block. View each `[Reference:]` image beside the slide that declares it. Note the design brief's **Avoid** list.

### 2. Measure

```bash
PYTHONIOENCODING=utf-8 python3 -c "
from pathlib import Path
from src.core.validate import validate_outline, balance_warnings, speech_warnings, measure_slide_balance
text = Path('WORK/script_N.md').read_text(encoding='utf-8')
for row in measure_slide_balance(text):
    print(f'{row.ratio:.2f}\t{row.role}\tbullets={row.bullets}\ttext={row.text_words}\tvisual={row.visual_words}\tspeech={row.speech_seconds:.0f}s\t{row.title}')
for w in validate_outline(text).warnings + balance_warnings(text) + speech_warnings(text):
    print('WARN', w)
"
```

Keep Python inline with `-c`; a heredoc on stdin breaks on Chinese text. The warnings check only the ratio and speech time. Also compare each row with the word ranges in the Targets table: a slide can sit inside the ratio band and still be crowded (both counts over the maximum) or sparse (both under the minimum).

### 3. Review: one issue list per slide

**Logical flow (deck level)**

- Read the titles alone, in order: they should form one argument, from the hook's question to the ending's answer.
- Each section moves setup → mechanism → evidence → implication, with no duplicated slide and no missing step.
- Each content slide's bridge sentence previews the next slide's actual message.
- Callbacks name slides that really came earlier and restate them accurately — including callbacks inside `[Visual:]` ("echoes the ball on slide 10" is wrong if slide 10 has no ball).
- Roadmap bullets, transition titles, and section contents use the same section names and order. An overview slide that lists a section's stops lists all of them, in the order the section teaches them.

**Self-consistency**

- Within a slide, the title, bullets, `[Visual:]`, and `[Speech:]` carry one message and one metaphor.
- Across the deck, terms, names, numbers, and units match `facts.md` and each other. One concept, one word: do not alternate synonyms (`盒子` on one slide, `箱子` on another).
- Recurring motifs keep one color code everywhere: entity or stage capsules, section colors, the colors assigned to the deck's core components. An overview slide uses the same colors as the detail slides.

**Script against PNG**

- The rendered title keeps the script's wording, on-slide labels match the bullets, numbers render correctly, and there is no garbled, misspelled, or invented text. Content slides show only `Slide number: N`, and the two-tone background matches the slide's role.
- Speech words that point at the image match it: color names (`青色`, not `绿色`, for #7FB8A8), left/right, and direction of motion (a ball "rolling to the valley" must point downhill).
- The PNG breaks nothing on the design brief's Avoid list: no fake logos or event branding, no English labels the script didn't ask for, no realistic faces except the presenter, no fake QR codes.
- The `[Visual:]` prose describes what is actually drawn. When the PNG differs from the prose but is faithful to the bullets, sync the prose to the PNG instead of rerendering.

**References**

- A slide that declares a `[Reference:]` image should carry its content, but the deck's own structure wins. If the reference shows a different sequence or set of stages than the deck teaches (four boxes where the deck has five stops), follow the deck and keep only the reference's style and icons.
- Every declared path exists (`ls`), and no path appears only inside `[Visual:]` — the render never loads those.

**Density: too crowded or too sparse**

| Signal | Too crowded | Too sparse |
|---|---|---|
| Script | More than 6 bullet lines, words over the Targets maximum, a `[Visual:]` with more than about 4 panels or many labeled parts | Thin or one-clause bullets, words under the Targets minimum, a one-line `[Visual:]`, a visual that only repeats the title |
| PNG | Small or cramped text, overlapping labels, text touching the edges, no whitespace | Large empty regions, a lone icon, a composition that says nothing the title doesn't |

- **Crowded:** Use the text-heavy fixes in the standards: fold into the takeaway, move elaboration to `[Speech:]`, cut panels. Splitting a slide changes the content-slide count, so ask the user first with AskQuestion.
- **Sparse:** Use the visual-heavy fixes: add the reasoning the image can't show, anchor the visual's focal parts in the bullets, and bring in a concrete fact (step 4). Never pad.

### 4. Verify facts against their sources

**Spot-check what is already cited.** For each high-risk detail — dates, counts, percentages, distances, quotes — WebFetch the URL that `facts.md` cites and confirm the exact figure and unit on the page. Large pages are saved to a file; grep it for the number instead of reading it whole. If the page lacks the figure, try the fact's other cited source, then WebSearch. Facts sourced to the presenter's own experience or local files are the user's call; do not "correct" them.

**Search for what is missing.** Use WebSearch, then WebFetch on the primary source, when:

- A claim has no matching fact in `facts.md`, or its number conflicts with another slide.
- A vague phrase ("much faster", "widely used") needs a verified figure.
- A sparse slide needs a concrete example, date, or number.

Add new facts to `facts.md` in the same pass as `- **F## Short name.** The fact — [source](URL)`, using the next unused ID, and add the ID to that slide's `Evidence:` line in `plan_N.md`. Write it in the deck's language, using the same wording everywhere it appears. If no source states it, keep the claim qualitative. Never invent a number.

### 5. Fix the script

- Make surgical edits. Leave strong slides alone, and keep the deck's title, arc, voice, and language.
- When one part of a slide changes, update the others so title, bullets, visual, and speech still agree.
- Do not change slide count, section order, or `[Style:]` tags without asking.
- Mirror changed titles, claims, flows, and visual hooks into `plan_N.md` so a later write rerun doesn't revert them.
- Render-only glitches (a one-off misspelling on an otherwise faithful slide) need a rerender, not an edit. Recurring garbled text means the slide asks for too much on-image text, so shorten the labels.
- To stop the model inventing content, state the constraint concretely in `[Visual:]`: "舞台背景留白，不画会议标志、logo 或任何英文字", "空白对话气泡，气泡内不写字".
- Added art direction raises the visual word count. If a slide drops below the ratio band, trim other visual wording (repeated layout reminders, restated colors) rather than padding bullets.

Measure again (step 2). Repeat until no warnings remain, for at most two rounds.

### 6. Rerender the changed slides

Rerendering spends image API calls. List only slides whose PNG must change — not text-only fixes or prose synced to the existing PNG — with the reason for each, and ask with AskQuestion before running. Exclude hand-finished slides.

Archive the old PNGs first without overwriting earlier archives: copy each to `WORK/image_TS_before/slide_p##_v01.png`, or `slide_p##_v01_roundK.png` with the next free `K` if that name exists. Then render and rebuild the deck:

```bash
python3 -m src.render.cli --work WORK --script WORK/script_N.md --style WORK/style --page 4,8 --output WORK/image_TS --no-balance
python3 -m src.render.cli --work WORK --script WORK/script_N.md --pptx-only --output WORK/image_TS --variant 1
```

A `--page` render also writes a partial `WORK/slides_<run date>.pptx` holding only the new pages. The `--pptx-only` rebuild names the full deck after the image directory's date. If the two names differ, delete the partial file before the rebuild.

Then check:

- View each new PNG and repeat the step-3 checks on it. Rerender a slide at most twice more; if it still fails, report it.
- The rebuild reports the deck's full slide count.
- `cmp WORK/script_N.md WORK/image_TS/script_N.md` — the render snapshots the script. If they differ, someone edited after the render: diff them, and if the change touches on-image text (a title, a label, a number), ask whether to rerender those slides. Speaker notes come from the live script at rebuild time, so rebuild once more if the script changed after the last rebuild.

### 7. Report

- Per changed slide: the problem (flow, consistency, reference, crowded, or sparse) and the fix, in one line.
- Facts verified, added, or corrected, with their source URLs — report verified facts even when nothing changed.
- Reference images checked, and any slide that departs from its reference on purpose.
- Before/after images for the two or three biggest changes, any warnings that remain, and any mismatch the user chose to keep.
- Hand off to recording:

```bash
python3 -m src.present.cli --work WORK --script WORK/script_N.md --output WORK/image_TS
```
