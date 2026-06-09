---
name: generate-slides
description: Automates the four-stage presentation slide generation pipeline (research, outline, style, and compose) to generate slide decks from a single idea with no human in the loop. Use when the user wants to generate slides from an idea, or requests end-to-end presentation generation.
---

# Autonomous Slide Generation (generate-slides) ✨

This skill automates the end-to-end presentation creation pipeline of VibeSliding (Research → Outline → Style → Compose) with the agent acting as the autonomous designer making all necessary structural and aesthetic choices.

---

## Workflow Checklist

Follow this checklist sequentially to take a single text idea and turn it into a curated slide deck.

### [ ] 0. Preflight Checks

- Verify `work/idea.md` exists and contains at least a Title, Subtitle, and Content Focus. If the user only gave a brief prompt, draft a solid `work/idea.md` based on their input before starting.
- Verify API key configuration, connectivity, and OpenRouter account balances by running:

  ```bash
  python3 -m src.compose.cli --balance-only
  ```

  *(Do NOT read or print `.env` file contents in chat. Respect security rules.)*

### [ ] 1. Deep Research

- Run Valyu DeepResearch on the idea in the desired mode:

  ```bash
  # Fast mode (takes ~2 minutes, highly efficient)
  python3 -m src.research.cli --mode fast --fresh

  # Heavy/Standard/Max modes (takes 2-5 minutes, exhaustive scientific/academic coverage)
  python3 -m src.research.cli --mode heavy --fresh
  ```

  *(Note: This is a long-running process that can take up to several minutes. Monitor progress via the CLI progress bar.)*
- If interrupted (Ctrl+C, crash, network drop), resume without starting a duplicate task:

  ```bash
  python3 -m src.research.cli --resume
  ```

  *(Task metadata is saved to `work/research_state.json` as soon as DeepResearch starts.)*
- This produces `work/research.md` (the research report with inline citations).

### [ ] 2. Outline Generation

- Generate the outline drafts based on your refined idea and research report:

  ```bash
  # Generate standard lengths: 16, 25, and 36 content slides
  python3 -m src.outline.cli

  # Or specify custom content slide counts
  python3 -m src.outline.cli --slides 16,25,36
  ```

- This writes three outline drafts in `work/`:
  - `outline_16.md` (16 content slides — default / concise)
  - `outline_25.md` (25 content slides — standard)
  - `outline_36.md` (36 content slides — comprehensive)
- **Agent Decision:** Read the generated outlines and pick the best length based on the depth of the idea, target talk duration, and any user constraints.

### [ ] 3. Style Reference Generation & Review

To bypass manual CLI prompts but still review style quality, follow this procedure:

1. Run style reference generation in non-interactive mode, pre-selecting candidates for all stages (defaulting to candidate 1):

   ```bash
   python3 -m src.style.cli --outline work/outline_16.md --pick 1,1,1,1
   ```

   *(Substitute `work/outline_16.md` with your chosen outline file path if you selected a different length.)*
2. This creates candidate images and contact sheets in `work/style_candidates/`.
3. Use the file read or visual capability to review the generated contact sheets:
   - `work/style_candidates/style_base_choices.png`
   - `work/style_candidates/style_cover_choices.png`
   - `work/style_candidates/style_transition_choices.png`
   - `work/style_candidates/style_content_choices.png`
4. **Agent Choice & Override (If Needed):**
   - **Cover, Transition, Content:** If a candidate other than `v01` (e.g. `v03` or `v04`) is clearly superior or matches the theme better, copy the preferred variant to overwrite the active reference. For example:

     ```bash
     cp work/style_candidates/style_cover_v04.png work/style_cover.png
     ```

   - **Base Plate:** If the chosen base plate (`v01`) is unstable or has low contrast, re-run style reference generation with a different base index (e.g., index 3):

     ```bash
     python3 -m src.style.cli --outline work/outline_16.md --pick 3,1,1,1
     ```

     And then repeat the review process for the newly generated matching content templates.

### [ ] 4. Slide Composition

- Run the slide image composer using the selected outline and chosen style references:

  ```bash
  # Compose 1 variant per slide page
  python3 -m src.compose.cli --outline work/outline_16.md --style "work/style_*.png"

  # Or compose N variants (parallel copies) per slide to let the user choose the best layout
  python3 -m src.compose.cli --outline work/outline_16.md --style "work/style_*.png" --copy 4
  ```

- This outputs a new timestamped directory, e.g., `work/slides_20260609_164000/`, containing all generated PNG slides and a single compiled `slide_combined.pdf`.

### [ ] 5. Quality Assurance & Selective Polishing

- Open the compiled `slide_combined.pdf` (or read individual slide PNGs) to review quality.
- If any individual slide contains layout artifacts, cut-off text, or poor alignment, regenerate that specific slide page. For example, to regenerate slides 3, 5, and 6:

  ```bash
  python3 -m src.compose.cli --outline work/outline_16.md --page "3,5-6"
  ```

- If you generated multiple parallel copies with `--copy N`, delete the inferior variants in the output directory, keeping only the best copy per slide (numbered as `_v01.png`, `_v02.png`, etc.).
- Once satisfied, rebuild the final PDF from the curated set of slide images without making new API calls:

  ```bash
  python3 -m src.compose.cli --pdf-only --output work/slides_20260609_164000/
  ```

  *(Use `--variant` option to specify only a particular set of variant numbers if desired.)*

---

## Decision Matrix for Outline Length

When selecting which outline file to carry forward, apply the following logic:

| Topic Scope | Intended Audience | Recommended Outline |
| :--- | :--- | :--- |
| Focused/Targeted | Executives, Keynotes (20-24 min talk) | `outline_16.md` |
| Balanced Overview | Standard presentations (30-35 min talk) | `outline_25.md` |
| Deep-Dive Technical | Seminars, lectures (42-48 min talk) | `outline_36.md` |

---

## Reliability & Performance Tips

- **API Costs:** Both style reference generation and slide composition make external calls to image models. Avoid unnecessary global regenerations; prefer copying alternative candidates from `work/style_candidates/` or using selective slide regeneration (`--page`).
- **Parallel Execution:** VibeSliding automatically parallelizes calls. Maintain `max_concurrent` settings in `.env` to prevent rate-limiting while keeping generation times under 2 minutes.
