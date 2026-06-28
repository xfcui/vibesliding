---
name: polish-visuals
description: Polish existing PPT outline markdown files focusing on visuals — improving visual tags, reference image tags, appendix, and visual structure. Use when the user wants to improve, polish, refine, review, or optimize the visual prompts, layouts, diagrams, style references, or appendix of one or more outline files. When multiple outlines are given, launches one subagent per file for parallel visual optimization.
disable-model-invocation: true
---

# Polish Visuals

Improve the visual tags, reference image tags, appendix, and visual structure of existing outline markdown files so every slide has production-ready art direction and is ready for style reference generation and slide composition.

## Inputs

The user provides one or more outline file paths (e.g. `work/outline_16.md`). If none given, glob for `work/outline_*.md` and optimize every match.

## Workflow

### Step 1: Collect targets and context

```text
targets = user-provided paths  OR  glob("work/outline_*.md")
```

If no outlines found, stop and tell the user to generate outlines first.

### Step 2: Read the outline standards

Read `.cursor/rules/outline-standards.mdc` — the single source of truth for structure, visuals, reference images, and appendix rules.

### Step 3: Dispatch optimization

**Single file** — optimize directly in the current agent.

**Multiple files** — launch one `generalPurpose` subagent per file using the Task tool so all outlines are optimized in parallel. Each subagent receives:

- The file path to optimize
- The full visual optimization checklist below

### Visual Optimization Checklist

Apply in order. **Do not rewrite slides that are already strong** — preserve working content and fix only what needs fixing.

#### A. Visual Structure & Integrity

- [ ] `## Appendix: Global Visual Requirements` is present after the last slide.
- [ ] Every slide has exactly one `[Visual:]` tag.
- [ ] Transition slides include a visual progress marker such as `progress bar N/total` in their `[Visual:]` tag.
- [ ] Two-tone backgrounds: Content slides use the primary background color; non-content slides (cover, transitions, ending) use a slightly deeper/darker variant (~4–6 units darker in lightness) to create a visual "curtain" that distinguishes structural pauses from teaching slides.

#### B. Reference Image Tags

If a slide mentions or uses specific reference images (such as a presenter's headshot, a specific diagram/chart reference, or a photo reference):

- [ ] Explicitly declare them using a `[Reference: path/to/image.png]` or `[Refs: path/to/image.png]` tag.
- [ ] Position the reference tag immediately before the slide's `[Visual:]` tag.
- [ ] Verify that the referenced file exists in the workspace (e.g., `projects/cv/headshot.jpg`).
- [ ] Ensure multiple references are separated by commas (e.g., `[Reference: path/1.png, path/2.jpg]`).

#### C. Visual Tags (Art Direction)

Ensure every slide's `[Visual:]` tag reads as **production-ready art direction**, not a vague description. Check:

- [ ] Specifies the **focal object** and **foreground/background structure**.
- [ ] Names a **layout pattern**: split-screen, grid, pipeline, roadmap, system diagram, film strip, etc.
- [ ] Shows the **narrative visually** through contrast, sequence, hierarchy, cause/effect, before/after, or workflow movement.
- [ ] Includes **concrete style cues**: specific hex colors from the appendix, font names and sizes, opacity percentages for watermarks/motifs.
- [ ] Contains **slide number** in the format `Slide number: N/total` or `N/total` (content/transition slides only; not on cover/ending).
- [ ] References style images where appropriate: `Reference style: style_base.png`, `style_cover.png`, `style_transition.png`, `style_content.png`.
- [ ] Transition slides reuse **one consistent section-map composition** with `progress bar N/total`, highlighting only the current section.
- [ ] Cover and ending slides specify the same motif (e.g. "heme porphyrin ring emblem"), with ending rendered slightly larger to signal closure.
- [ ] No dense generated-text labels, watermarks, fake logos, or AI-generation stamps.
- [ ] Preserves deck-wide **recurring motifs** (watermark, thread line, pinned dots, etc.) that appear across the existing outline.

#### D. Appendix

- [ ] Contains `**Theme:**` with named colors and hex codes.
- [ ] Contains `**Fonts:**` with font families, weights, and point sizes for each hierarchy level.
- [ ] Optionally contains `**Format:**` with aspect ratio, safe margins, contrast ratio.
- [ ] Does NOT contain layout, composition, diagram, icon, or motif direction (those belong in `[Visual:]` tags).

### Step 4: Post-optimization validation

After rewriting, re-check:

```python
from src.outline.writer import validate_outline
result = validate_outline(outline_text)
```

If warnings remain, fix them in a second pass.

### Step 5: Report

Summarize per file:

- Visual tags corrected or enhanced
- Reference image tags added or fixed
- Appendix corrections applied
- Visual structure/background fixes applied
- Any remaining warnings

---

## Preserve, Don't Rewrite

The goal is surgical improvement, not wholesale rewriting. Specifically:

- **Keep the deck's identity**: title, narrative arc, section structure, and written/textual content.
- **Keep strong slides intact**: if a slide already has a detailed, production-ready visual tag and correct style references — leave it alone.
- **Match the existing visual theme**: maintain consistency with the colors, fonts, and motifs defined in the original outline and appendix.
