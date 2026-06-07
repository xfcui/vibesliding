---
name: generate-slides
description: Automates the four-stage presentation slide generation pipeline (research, outline, style, and compose) to generate slide decks from a single idea with no human in the loop. Use when the user wants to generate slides from an idea, or requests end-to-end presentation generation.
---

# Autonomous Slide Generation (generate-slides)

This skill automates the end-to-end presentation creation pipeline of VibeSliding (Research → Outline → Style → Compose) with the agent acting as the autonomous designer making all necessary structural and aesthetic choices.

---

## Workflow Checklist

Follow this checklist sequentially to take a single text idea and turn it into a curated slide deck.

### [ ] 0. Preflight Checks

- Verify `work/idea.md` exists and contains at least a Title, Subtitle, and Content Focus. If the user only gave a brief prompt, draft a solid `work/idea.md` based on their input before starting.
- Verify API key configuration and connectivity by running:

  ```bash
  python3 -m src.compose.cli --balance-only
  ```

  *(Do NOT read or print `.env` file contents in chat. Respect security rules.)*

### [ ] 1. Deep Research

- Run Valyu DeepResearch on the idea:

  ```bash
  python3 -m src.research.cli
  ```

  *(Note: This is a long-running process that can take up to several minutes. Monitor progress via the progress bar.)*
- If interrupted (Ctrl+C, crash, network drop), resume without starting a duplicate task:

  ```bash
  python3 -m src.research.cli --resume
  ```

  *(Task metadata is saved to `work/research_state.json` as soon as DeepResearch starts.)*
- This produces `work/research.md` (the research report with inline citations).

### [ ] 2. Outline Generation

- Generate the outline drafts:

  ```bash
  python3 -m src.outline.cli
  ```

- This writes three outline drafts in `work/`:
  - `outline_16.md` (16 content slides — default / concise)
  - `outline_25.md` (25 content slides — standard)
  - `outline_36.md` (36 content slides — comprehensive)
- **Agent Decision:** Read the generated outlines and pick the best length based on the depth of the idea and any user constraints.

### [ ] 3. Style Reference Generation & Review

To bypass manual CLI prompts but still review style quality, follow this procedure:

1. Run style reference generation in non-interactive mode, defaulting to candidate 1 for all stages:

   ```bash
   python3 -m src.style.cli --outline work/outline_16.md --pick 1,1,1,1
   ```

   *(Substitute `work/outline_16.md` with your chosen outline file path if you selected a different length.)*
2. This creates candidate images and contact sheets in `work/style_candidates/`.
3. Use the file read or visual capability to review the generated contact sheets:
   - `work/style_candidates/style_base_choices.png`
   - `work/style_candidates/style_cover_choices.png`
   - `work/style_candidates/style_transition_choices.png`
   - `work/style_candidates/style_story_choices.png`
4. **Agent Choice & Override (If Needed):**
   - **Cover, Transition, Story:** If a candidate other than `v01` (e.g. `v03`) is clearly superior or matches the theme better, copy the preferred variant to overwrite the active reference. For example:

     ```bash
     cp work/style_candidates/style_cover_v03.png work/style_cover.png
     ```

   - **Base Plate:** If the chosen base plate (`v01`) is unstable or has low contrast, re-run style reference generation with a different base index (e.g., index 3):

     ```bash
     python3 -m src.style.cli --outline work/outline_16.md --pick 3,1,1,1
     ```

     And then repeat the review process for the newly generated matching content templates.

### [ ] 4. Slide Composition

- Run the slide image composer using the selected outline and chosen style references:

  ```bash
  python3 -m src.compose.cli --outline work/outline_16.md --style "work/style_*.png"
  ```

- This outputs a new timestamped directory, e.g., `slides_20260607_220000/`, containing all generated PNG slides and a single compiled `slide_combined.pdf`.

### [ ] 5. Quality Assurance & Selective Polishing

- Open the compiled `slide_combined.pdf` (or read individual slide PNGs) to review quality.
- If any individual slide contains layout artifacts, cut-off text, or poor alignment, regenerate that specific slide page. For example, to regenerate slides 3, 5, and 6:

  ```bash
  python3 -m src.compose.cli --outline work/outline_16.md --page "3,5-6"
  ```

- Once satisfied, rebuild the final PDF with the updated slides:

  ```bash
  python3 -m src.compose.cli --pdf-only --output slides_20260607_220000/
  ```

---

## Decision Matrix for Outline Length

When selecting which outline file to carry forward, apply the following logic:

| Topic Scope | Intended Audience | Recommended Outline |
| :--- | :--- | :--- |
| Focused/Targeted | Executives, Keynotes (15-min talk) | `outline_16.md` |
| Balanced Overview | Standard presentations (30-min talk) | `outline_25.md` |
| Deep-Dive Technical | Seminars, lectures (45-60 min talk) | `outline_36.md` |

---

## Reliability & Performance Tips

- **API Costs:** Both style reference generation and slide composition make external calls to image models. Avoid unnecessary global regenerations; prefer copying alternative candidates from `work/style_candidates/` or using selective slide regeneration (`--page`).
- **Parallel Execution:** VibeSliding automatically parallelizes calls. Maintain `max_concurrent` settings in `.env` to prevent rate-limiting while keeping generation times under 2 minutes.
