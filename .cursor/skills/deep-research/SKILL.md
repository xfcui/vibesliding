---
name: deep-research
description: Run the deep-research stage of the VibeSliding pipeline — turn a raw idea (paragraph or file) into a metric-dense idea.md plus a citation-rich research.md, via web search, a fast Valyu pass, an idea refine, and a heavy Valyu pass. Use when starting a new deck or when asked to research, develop, ground, or expand a presentation idea or topic before outlining.
disable-model-invocation: true
---

# Deep Research

Transform a raw idea into the two grounded artifacts every later stage depends on: a metric-dense `idea.md` and a citation-rich `research.md`. This is the loop from `talk/outline.md` slides 11–15: Draft Idea → Fast Research → Refine Idea → Heavy Research.

## Inputs

A raw idea, given as either a paragraph in the chat or a path to a notes file.

## Work directory

Pick `<dir>` once and reuse it for every step:

- If the user names a directory, use it.
- Else glob for an existing `idea.md` (`talk/idea.md`, `work/idea.md`, `projects/*/idea.md`) and use that directory.
- Else default to `work/`.

`research.md` is **overwritten** on every CLI run — each pass replaces the file, so the depth gain comes from a sharper `idea.md` driving a deeper query, not from appending.

## Workflow

Copy this checklist and track progress:

```text
- [ ] 1. Web-search backgrounds
- [ ] 2. Draft idea.md
- [ ] 3. Fast research  (Valyu fast pass → research.md)
- [ ] 4. Refine idea.md (ground every claim in research.md)
- [ ] 5. Heavy research (Valyu heavy pass → research.md)
```

### 1. Web-search backgrounds

Run a few `WebSearch` queries for prior art, key terms, named tools, and recent benchmarks in the idea's domain. Keep findings in context for the next step.

### 2. Draft idea.md

Write `<dir>/idea.md` from the raw input + search findings, using this exact structure:

```markdown
# Presentation Idea

**Title:** ...
**Subtitle:** ...
**Speaker:** ...
**Affiliation:** ...
**WeChat:** ...
**Email:** ...

## Audience
- ...

## Hook
<one paragraph: the problem, the approach, the payoff>

## Content Focus
1. **<Theme>** — what this section proves
... (5-6 items)

## Scope Exclusions
- ...
```

Keep this pass deliberately rough: state claims qualitatively or leave bracketed placeholders (e.g. `[X% faster]`, `[benchmark name]`) for research to resolve. Carry over real speaker/contact details if the user gave them; otherwise leave the fields as placeholders.

### 3. Fast research

Validate that the topic has substance and pull initial sources:

```bash
python3 -m src.research.cli --work <dir> --mode fast --fresh
```

Writes `<dir>/research.md`. Fast mode polls up to ~10 min. If Valyu credits are exhausted it auto-fails over to OpenRouter — no action needed.

### 4. Refine idea.md

Read the fresh `<dir>/research.md`, then edit `<dir>/idea.md` in place:

- Replace every vague claim / placeholder with a specific verified number and inline attribution, e.g. `8,600 TTN vs. ~2,400 wild-type — a 3.6x gain (Chen et al., 2025)`.
- Ensure each `Content Focus` item is grounded in a metric from `research.md`.
- Tighten `Scope Exclusions` to prevent later outline drift.
- Never invent numbers: if `research.md` lacks a figure, do one targeted `WebSearch` or keep the claim qualitative.

### 5. Heavy research

Now that `idea.md` is metric-dense, run the deep pass so its specific claims get publication-grade evidence:

```bash
python3 -m src.research.cli --work <dir> --mode heavy --fresh
```

Heavy mode can run a long time (poll budget up to ~2 h). Start it in the background with a generous timeout and check on it, rather than blocking. The result overwrites `research.md` with a deeper, citation-rich report ready for outline generation.

## Notes

- `--fresh` avoids the "incomplete run detected" error from any leftover `research_state.json`; if a real run was interrupted, use `--resume` instead to continue it.
- `--mode` overrides `[valyu] mode` in `.env`. Other useful flags: `--categories research,healthcare`, `--valyu-api-key`.
- When this skill completes, the natural next step is outline generation: `python3 -m src.outline.cli --work <dir>`.
