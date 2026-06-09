---
name: optimize-outline
description: Optimize existing PPT outline markdown files against outline-standards — strengthening bullets, grounding metrics, improving visual/speech tags, and fixing structural issues. Use when the user wants to improve, polish, refine, review, or optimize one or more outline files. When multiple outlines are given, launches one subagent per file for parallel optimization.
disable-model-invocation: true
---

# Optimize Outline

Improve existing outline markdown files so every slide is presentation-grade and ready for style reference generation and slide composition.

## Inputs

The user provides one or more outline file paths (e.g. `work/outline_16.md`). If none given, glob for `work/outline_*.md` and optimize every match.

## Workflow

### Step 1: Collect targets and context

```
targets = user-provided paths  OR  glob("work/outline_*.md")
```

If no outlines found, stop and tell the user to generate outlines first.

Also read the source materials that the outlines were built from — these are needed for metric grounding:
- `work/idea.md` — the presentation idea
- `work/research.md` — the research report with citations
- `work/source.md` — the user's source document (if it exists)

### Step 2: Read the outline standards

Read `.cursor/rules/outline-standards.mdc` — the single source of truth for structure, writing, visuals, speech, and appendix rules.

### Step 3: Dispatch optimization

**Single file** — optimize directly in the current agent.

**Multiple files** — launch one `generalPurpose` subagent per file using the Task tool so all outlines are optimized in parallel. Each subagent receives:
- The file path to optimize
- The full optimization checklist below
- The content of `work/idea.md`, `work/research.md`, and `work/source.md` (inline in the prompt) so it can ground metrics

### Optimization Checklist

Apply in order. **Do not rewrite slides that are already strong** — preserve working content and fix only what needs fixing.

#### A. Structural integrity

- [ ] First line is `# PPT Outline: [Title]`
- [ ] `---` separators between every slide and after the title
- [ ] Sequential `## Slide N: [Title]` numbering with no gaps
- [ ] `## Appendix: Global Visual Requirements` after the last slide
- [ ] 3-6 transition slides: title prefixed `Roadmap:`, `progress bar N/total` in `[Visual:]`

#### B. Metric grounding (highest-value pass)

Cross-reference every factual claim against `research.md` and `source.md`:

- [ ] Replace vague claims ("significant improvement," "high accuracy," "large space") with specific verified numbers from the research report
- [ ] Format as: "P450D-7 achieved 8,600 TTN vs. wild-type BM3 ~2,400 — a 3.6x improvement (Chen et al., 2025)"
- [ ] Add missing citations where the research report provides them
- [ ] Do NOT fabricate numbers — if no source exists, keep the claim qualitative

#### C. Bullet quality

Content slides (5-6 bullets):
- [ ] Every bullet uses `**Label:** explanation` format where the explanation is self-contained (makes sense without reading the slide title)
- [ ] Every content slide ends with an explicit takeaway: `Core insight:`, `Core logic:`, or `Anti-pattern:`
- [ ] Cut bullets that merely restate what the visual already conveys
- [ ] Replace thin bullets ("Performance: Fast") with substantive ones that explain *why it matters*

Cover/ending slides (2-4 bullets):
- [ ] Premise or closing takeaway is immediately legible
- [ ] Ending mirrors the cover thematically

Transition slides (2-4 bullets):
- [ ] Show the full section map with current section bolded
- [ ] Include a one-line thesis for the upcoming section

#### D. Visual tags

Every slide must have exactly one `[Visual:]` tag that reads as **production-ready art direction**, not a vague description. Check:

- [ ] Specifies the **focal object** and **foreground/background structure**
- [ ] Names a **layout pattern**: split-screen, grid, pipeline, roadmap, system diagram, film strip, etc.
- [ ] Shows the **narrative visually** through contrast, sequence, hierarchy, cause/effect, before/after, or workflow movement
- [ ] Includes **concrete style cues**: specific hex colors from the appendix, font names and sizes, opacity percentages for watermarks/motifs
- [ ] Contains **slide number** in the format `Slide number: N/total` or `N/total` (content/transition slides only; not on cover/ending)
- [ ] References style images where appropriate: `Reference style: style_base.png`, `style_cover.png`, `style_transition.png`, `style_content.png`
- [ ] Transition slides reuse **one consistent section-map composition** with `progress bar N/total`, highlighting only the current section
- [ ] Cover and ending slides specify the same motif (e.g. "heme porphyrin ring emblem"), with ending rendered slightly larger to signal closure
- [ ] No dense generated-text labels, watermarks, fake logos, or AI-generation stamps
- [ ] Preserves deck-wide **recurring motifs** (watermark, thread line, pinned dots, etc.) that appear across the existing outline

#### E. Speech tags

Every slide must have exactly one `[Speech:]` tag that reads as **natural presenter narration**:

- [ ] Content slides: 60-90 seconds (roughly 3-6 sentences); expands on bullets with context, emphasis, or examples not visible on the slide
- [ ] Content slides: end with a **bridge sentence** that leads into the next slide's topic (e.g. "Now let's look at the tools that power this pipeline.")
- [ ] Transition slides: 15-30 seconds; set up what the upcoming section covers
- [ ] Cover: establish the hook and promise of the talk
- [ ] Ending: recap the key thesis and invite questions
- [ ] Never just restate the bullets verbatim — add the "why it matters" context the audience needs to hear

#### F. Appendix

- [ ] Contains `**Theme:**` with named colors and hex codes
- [ ] Contains `**Fonts:**` with font families, weights, and point sizes for each hierarchy level
- [ ] Optionally contains `**Format:**` with aspect ratio, safe margins, contrast ratio
- [ ] Does NOT contain layout, composition, diagram, icon, or motif direction (those belong in `[Visual:]` tags)

### Step 4: Post-optimization validation

After rewriting, re-check:

```python
from src.outline.writer import validate_outline
result = validate_outline(outline_text)
```

If warnings remain, fix them in a second pass.

### Step 5: Report

Summarize per file:
- Metrics grounded (count of vague → specific replacements)
- Bullets rewritten or added
- Visual/speech tags corrected
- Structural fixes applied
- Any remaining warnings

---

## Preserve, Don't Rewrite

The goal is surgical improvement, not wholesale rewriting. Specifically:

- **Keep the deck's identity**: title, narrative arc, section structure, appendix theme
- **Keep strong slides intact**: if a slide already has 5-6 substantive bullets, specific metrics, a detailed visual tag, and natural speech — leave it alone
- **Match the existing voice**: if the outline uses a particular tone (technical, conversational, formal), maintain it
- **Match the language**: if the outline is in Chinese, optimize in Chinese; if English, stay English
