---
name: plan-deck
description: Plan a presentation from an idea and references, with no model API calls. Writes facts.md (fact IDs the plan cites), asks the user to pick a content-slide count, then writes plan_N.md and design_brief.md. Use when the user wants a deck plan, talk plan, or outline skeleton from notes and references.
disable-model-invocation: true
---

# Plan a deck

Turn an idea and references into a deck plan. Do not call a text or image model. You write the files.

## Inputs

- A work directory (default `~/work`, expanded to an absolute path, or a folder the user names). Call it `WORK`.
- `idea.md` — audience, language, thesis, and what to leave out
- Optional `source.md`, plus any references the user lists (markdown or PDF)

## Workflow

### 1. Read the idea and the references

Read `idea.md` and every reference. Pull only facts you can point at.

### 2. Write `facts.md`

`WORK/facts.md` is a required output: the write stage refuses to run without it and sends each slide the facts its plan cites.

One bullet per fact, in the form `- **F3 Short name.** The fact — citation or URL`. Number IDs `F1`, `F2`, … once each and never reuse an ID; group bullets under `##` headings by topic. Do not invent numbers. Write each figure once, with its unit, so every slide that cites it uses the same wording. Facts from the user rather than a source are cited as such (for example `— presenter's experience`).

### 3. Ask for the content-slide count

Propose 2-3 counts with a one-line reason for each (for example 16, 25, 36). Ask the user to pick one with AskQuestion. The count is content slides only: hook, teaching, and an optional call to action. Cover, roadmap, and ending slides are extra.

### 4. Write `plan_N.md` and `design_brief.md`

Follow the Plan format in `.cursor/rules/outline-standards.mdc`.

- `plan_N.md` gives every slide a message title, a `Role:`, 2-4 `Point:` lines, an `Evidence:` line of fact IDs (`- Evidence: F3, F7`), and exactly one `Visual hook:`. Every hook, content, and call-to-action slide cites at least one fact; cite every fact a point relies on, because the write stage only guarantees the cited ones reach the model.
- When a plan edit adds a claim, add or update its fact in `facts.md` in the same pass.
- Divide the body into 3-6 sections, with one `Roadmap:` slide before each section and none before the hook or the call to action.
- Every roadmap slide has `Section: k/total`, counting 1 to total in order, where total is the number of roadmap slides. A content slide that names its section uses the number of the roadmap slide it follows.
- `design_brief.md` uses `- **Field:** value` lines: topic family, mood, signature motif, avoid, language, footer, cover eyebrow, cover title, cover support, content eyebrow, content title, and content stages.

### 5. Keep the plan balanced and self-consistent

Before validating, read the plan end to end:

- **Balance:** each slide's `Point:` lines and its `Visual hook:` carry the same idea. The write stage expands points into bullets and the hook into the `[Visual:]` tag.
  - **Content slides:** Give the points and the hook comparable weight. Rich points with a vague hook (or the reverse) turn into a slide that is mainly text or mainly visual.
  - **Cover, roadmap, and ending slides:** These lean visual. Keep the points short and make the hook the richer line, so the `[Visual:]` outweighs the bullets.
- **Same facts everywhere:** terms, names, numbers, and units match `facts.md` and each other on every slide.
- **Same sections everywhere:** roadmap titles, section names in points, and `Section: k/total` numbers agree.
- **Real callbacks:** a point that refers back names a slide that really came earlier.
- **No contradictions:** no slide contradicts another, and the design brief's motif and mood fit the deck's story.

### 6. Validate

Run from the repo root. `WORK` is the absolute path of the work directory. The CLI default is a repo-relative `work/` and does not point at `~/work`.

```bash
python3 -m src.plan.cli --plan WORK/plan_N.md
```

The CLI reads `facts.md` beside the plan and warns when it is missing, when an `Evidence:` ID is not defined there, when an ID is defined twice, or when a content slide cites nothing. Fix any warnings, then run it again.

### 7. Hand off

Print the write command:

```bash
python3 -m src.write.cli --work WORK --plan WORK/plan_N.md
```

The write stage reads `plan_N.md` and `facts.md` from `WORK`, gives content slides `Slide number: N` (page only, no total), and checks the finished script for balance and speech length, so the plan does not need page numbers or speech.
