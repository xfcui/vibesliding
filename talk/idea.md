# Presentation Idea

**Title:** VibeSliding: From Idea to 60-Slide Deck in Under an Hour
**Subtitle:** Building an autonomous pipeline for high-fidelity presentation engineering

**Speaker:** Xuefeng Cui
**Affiliation:** Shandong University

**WeChat:** xfcui0
**Email:** xfcui.uw@gmail.com

## Audience

- Software engineers and AI practitioners building autonomous multi-agent pipelines and workflows
- Product designers and presentation creators interested in programmatic, AI-driven visual curation
- Researchers exploring compound AI systems that integrate search, outline, style, and composition engines

## Hook

The majority of AI-generated presentations suffer from a "single-shot" quality trap—yielding superficial slides with misaligned text, generic layouts, and missing factual depth. VibeSliding breaks this paradigm by wrapping commodity APIs in a strict draft-then-refine loop: treating research, outline, style, and slide composition as highly iterative, human-curated stages. By running parallel completions and rendering up to 4 candidate variations per slide page, VibeSliding delivers a metric-dense, visually striking 60-slide deck (complete with presenter scripts and custom visuals) in under 60 minutes, proving that the value of generative AI is not in the models themselves, but in the orchestrations that connect them.

## Content Focus

1. **The Single-Shot Presentation Failure** — Why direct LLM-to-deck pipelines fail to produce presentation-grade results, and why compound AI systems are required to handle layout, narrative, and factual constraints
2. **Principle of Iterative Refinement (Draft-then-Refine)** — The two-pass pipeline architecture where the first pass explores the problem space and the second pass hardens outlines with citations, metrics, and visual standards
3. **Orchestrating Commodity Tools** — How to coordinate Cursor for IDE-driven user reviews, OpenRouter for vendor-neutral text/image model routing, and Valyu for citation-grounded deep academic research
4. **Scaffolding and Outline Generation** — Defining a shared visual system (scaffold) and programmatically scaling content length from concise 16-slide briefs to comprehensive 36-slide deep dives
5. **Aesthetic Choice via Contact Sheets** — Empowering the user to make aesthetic decisions by generating parallel style candidates (base, cover, transition, story) and presenting them as standard contact sheets
6. **Parallel Slide Composition & QA** — Techniques for rendering dozens of high-fidelity slides in parallel, performing selective single-page regeneration, and assembling the final vectorized PDF

## Scope Exclusions

- High-level templates or manual slide-making platforms (e.g., PowerPoint, Canva, Keynote)
- Basic single-agent text-to-slide wrappers that do not employ multi-stage loops
- General introduction to LLMs or image diffusion models without workflow orchestration context
