---
name: optimize-idea
description: Refactor, optimize, and improve the VibeSliding presentation seed (work/idea.md) using web search. Use when the user asks to refactor, optimize, or improve the presentation idea, or when working with work/idea.md.
disable-model-invocation: true
---

# Optimize Idea Skill 🚀

This skill guides the agent through refactoring, optimizing, and enriching the presentation seed (`work/idea.md`) using web search, while ensuring safety, schema preservation, and automatic backups.

## Workflow Checklist

Follow these steps systematically when asked to optimize or refactor a presentation idea:

- [ ] **Step 1: Read the Presentation Seed**
  - Locate the target idea file (default: `work/idea.md`).
  - Read the file. If the file is missing or empty, report an error.
  
- [ ] **Step 2: Analyze the Seed & Identify Claims**
  - Identify claims that need verification (e.g., market size, dollar amounts, timelines, specific tools/methods, or scientific facts).
  - Identify gaps where adding current, reputable data would strengthen the presentation's hook or content focus.

- [ ] **Step 3: Formulate Search Queries**
  - Create 2-3 precise, atomic search queries (3-6 words each) focused on the identified claims or gaps.

- [ ] **Step 4: Execute Web Searches**
  - Perform web searches to gather fresh, accurate, and reputable information.
  - **Tool**: Use `CallMcpTool` with server `user-Valyu` and tool `search_valyu`. Pass a natural-language `query` (one focused question per call). Use `search_type: "all"` (default) to search both web and proprietary academic/scientific sources, or `search_type: "proprietary"` for research-heavy queries. Set `max_num_results` to 5-10.
  - Run multiple `search_valyu` calls in parallel when verifying independent claims.
  - Do not fall back to other search tools.

- [ ] **Step 5: Refactor and Optimize the Content**
  - Refine the text to be punchy, professional, and clear, following the existing structure.
  - Keep the seed concise (do not turn it into a full research report; that is `research.md`'s job).
  - **Preserve the Schema**:
    - **Title & Subtitle**: Keep or refine for impact.
    - **Contact Block**: Keep the contact block (Speaker, Affiliation, WeChat, Email) **completely unchanged** (byte-for-byte).
    - `## Audience`: Tighten and clarify the target audience.
    - `## Hook`: Sharpen with verified, compelling statistics and figures from your search results.
    - `## Content Focus`: Validate, modernize, and enrich the numbered items. Ensure each item has a bold label.
    - `## Scope Exclusions`: Confirm and refine exclusions to set clear boundaries.

- [ ] **Step 6: Create a Timestamped Backup**
  - Before making any changes, copy the original file to a timestamped backup in the same directory (e.g., `work/idea.20260607_221000.bak.md`).

- [ ] **Step 7: Overwrite the Idea File**
  - Write the optimized content back to the target idea file (e.g., `work/idea.md`), preserving the exact schema and headings.

- [ ] **Step 8: Present a Concise Changelog**
  - Summarize the key optimizations made.
  - List the verified facts/statistics and cite their source URLs.

## Schema to Preserve

The presentation seed must strictly adhere to the following structure:

```markdown
# Presentation Idea

**Title:** [Title]
**Subtitle:** [Subtitle]

**Speaker:** [Speaker Name]
**Affiliation:** [Affiliation]

**WeChat:** [WeChat ID]
**Email:** [Email Address]

## Audience

- [Audience point 1]
- [Audience point 2]

## Hook

[A compelling, data-driven hook paragraph]

## Content Focus

1. **[Bold Label]** — [Description]
2. **[Bold Label]** — [Description]
...

## Scope Exclusions

- [Exclusion point 1]
- [Exclusion point 2]
```

## Guardrails & Rules

1. **No Hallucinations**: Do not invent or guess statistics. Every number, timeline, or factual claim in the optimized idea must be backed by search results.
2. **Contact Block Safety**: Never alter, delete, or rewrite the contact block. It must remain byte-for-byte identical to the original.
3. **Keep it a Seed**: Do not bloat the file. The presentation seed is a high-level guide, not a detailed report.
4. **Support Custom Paths**: If the user specifies a custom work directory or a custom idea file path, respect it and adjust paths accordingly.
5. **No Emojis**: Do not use emojis in the optimized markdown file unless explicitly requested by the user.

## Examples

### Example 1: Hook Optimization

**Before:**

```markdown
## Hook
The average drug takes a long time and a lot of money to reach market, but AI-guided pipelines can make this much faster.
```

**After (optimized with web search):**

```markdown
## Hook
The average drug takes 10–15 years and $2.6B+ to reach market — yet AI-guided pipelines are compressing target identification, lead optimization, and preclinical validation into months, with virtual cells predicting outcomes before a single wet-lab experiment runs.
```

### Example 2: Content Focus Optimization

**Before:**

```markdown
## Content Focus
1. Generative models for drug design.
2. Simulation of cells.
```

**After (optimized with web search):**

```markdown
## Content Focus
1. **AI for drug design** — generative models for molecular generation, protein structure prediction (AlphaFold and beyond), binding affinity estimation, and ADMET property optimization
2. **Virtual cell simulation** — whole-cell modeling, digital twins for pathway perturbation, and in-silico screening at biological-system scale
```
