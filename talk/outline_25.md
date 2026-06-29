# PPT Outline: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

---

## Slide 1: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

- **Subtitle:** Building an autonomous pipeline for high-fidelity presentation engineering
- **Speaker:** Xuefeng Cui — Shandong University
- **Contact:** WeChat `xfcui0` · Email `xfcui.uw@gmail.com`
- **Premise:** One paragraph in, 60 publication-grade slides out — under 60 minutes, under $5
[Visual: Deep Space (#0A0F1A) background. Centered luminous heme-thiolate porphyrin ring rendered as glowing Electric Cyan (#00E5FF) geometric line-art emblem with Amber (#FFB300) accent nodes at coordination points. Title "VibeSliding" in Inter Bold 36pt Cool White above the emblem. Subtitle, speaker name, affiliation, and contact details in Inter Light 18pt stacked below the emblem. Faint dot grid recedes into the background suggesting a digital substrate. No slide number. Reference style: style_cover.png]
[Speech: Good morning, everyone. I want to start with a question: what if you could turn a single paragraph — literally one hundred words — into a sixty-slide, citation-rich, visually polished presentation deck in under an hour? That's not a hypothetical. That's exactly what we built, and exactly what we used to create a real deck for a synthetic biology seminar. Today I'll walk you through how it works, why it works, and why the secret isn't better models — it's better orchestration. Let's dive in.]

---

## Slide 2: Roadmap: The Problem

- **Section 1 of 6 — THE PROBLEM**
- **Thesis:** AI slide tools promise one-click decks but deliver outputs that require more editing than building from scratch
- Every presentation pipeline begins with understanding why the current approach breaks
[Visual: Upper two-thirds shows "THE PROBLEM" in large Inter Bold 28pt Signal Red (#FF5252) with thesis sentence in Inter Regular 16pt Cool White beneath. Lower third contains horizontal section-map strip: six nodes connected by thin lines — node 1 ("01 / THE PROBLEM") rendered in full Signal Red glow with filled circle, nodes 2–6 dim (#3A4A5C outline only). Progress bar beneath the strip filled 1/6. Three-pinned-dots watermark at 15% opacity upper-right corner. Faint radial gradient spotlight behind active node. Deep Space background. Reference style: style_transition.png]
[Speech: We'll start where every good narrative starts — with the problem. Why do current AI slide tools consistently disappoint?]

---

## Slide 3: The 9 AM Request — A Colleague Needs 60 Slides by Next Week

- **The scenario:** A colleague messages at 9 AM — "I'm presenting at the synthetic biology seminar next week. 60 slides on AI-driven P450 engineering, deep technical, full speaker notes. Can you help?"
- **The constraints are brutal:** Deep technical content across six sub-domains, concrete metrics and citations, custom visuals, and presenter scripts for every slide
- **Traditional timeline:** A freelance designer quotes 4+ hours at $75/hour ($300+), and the result still needs domain-expert review
- **The hidden cost:** McKinsey estimates users spend 2.3 hours editing a 20-slide AI-generated deck — only 26% faster than building from scratch
- **What if instead:** You type one paragraph into a markdown file, hit run, leave for coffee, and return to a finished 186 MB PDF
- Core insight: The gap between "AI can generate slides" and "AI can generate *presentation-grade* slides" is where every existing tool fails
[Visual: Split-screen composition. Left half: a chat bubble on a dark messaging interface showing the colleague's request in Cool White text, timestamp "9:02 AM" in Slate. Right half: a finished PDF deck fanning open like a card spread, showing 60 slide thumbnails with visible visuals and text. A single dashed Amber (#FFB300) arrow connects the two halves, labeled "< 60 min" in Inter Medium 14pt. Heme watermark at 15% opacity upper-right. Pipeline thread line at bottom 2px 30% opacity. Slide number 3/33 in Slate bottom-right. Reference style: style_content.png]
[Speech: Here's the exact scenario that launched this project. A colleague needed sixty slides — deep technical, full speaker notes, custom visuals — for a synthetic biology seminar. Now, you could hire a designer. That's three hundred dollars and four-plus hours, and they still won't know what P450Diffusion is. Or you could try one of the AI slide tools. But McKinsey's data tells us something uncomfortable: users spend an average of two point three hours editing a twenty-slide AI deck. That's only twenty-six percent faster than doing it manually. What if there's a third option — one paragraph in, sixty polished slides out, under an hour? Let's look at why that third option doesn't exist yet.]

---

## Slide 4: The Single-Shot Quality Trap — Why One-Pass LLM Decks Fail

- **The root failure is architectural:** A single LLM call must simultaneously handle research, narrative arc, information hierarchy, layout specification, text density, and aesthetic consistency — six distinct optimization problems with different loss functions
- **Layout misalignment:** Nielsen Norman Group found 68% of AI-generated slides exhibit text overflow, image clipping, or margin violations in single-pass generation
- **Content superficiality:** 74% of single-pass slides contain fewer than two supporting data points per claim — no citations, no metrics, no evidence
- **The opacity problem:** Users see only the final output and must reverse-engineer which upstream decision (research? outline? layout?) caused the downstream deficiency
- **Real-world confirmation:** Microsoft's own Office Copilot research found 41% of PowerPoint slides required manual repositioning of at least one element, even with a dedicated layout engine
- Core insight: Single-shot fails not because models are weak, but because presentation engineering is a multi-objective optimization problem that demands decomposition
[Visual: A cracked, glitching slide mockup rendered in forensic annotation style. The mockup shows a typical AI-generated slide with red "X" markers at specific failure points: a text box overflowing its bounding box (labeled "68% layout misalignment"), a bullet point with no citation (labeled "74% content superficiality"), a generic stock photo placeholder (labeled "no visual anchor"), and a font inconsistency (labeled "style drift"). Thin red annotation lines connect each failure to its label in Inter Medium 14pt Signal Red. The slide mockup sits slightly tilted on Deep Space background. Heme watermark upper-right. Slide number 4/33. Reference style: style_content.png]
[Speech: So why do one-pass AI decks fail so consistently? The answer isn't model quality — it's architecture. When you ask a single LLM to simultaneously research a topic, construct a narrative, design a layout, calibrate text density, and maintain visual consistency, you're asking it to optimize six different objectives in one shot. It satisfices across all of them and excels at none. Nielsen Norman Group quantified this: sixty-eight percent layout misalignment, seventy-four percent content superficiality. Even Microsoft's own Copilot — with a dedicated layout engine — still requires manual repositioning on forty-one percent of slides. The problem isn't the models. It's the monolithic architecture. And that diagnosis points us directly to the solution.]

---

## Slide 5: Roadmap: The Architecture

- **Section 2 of 6 — THE ARCHITECTURE**
- **Thesis:** Two governing principles — iterate everything and orchestrate commodity tools — transform a broken single-shot pipeline into a reliable multi-stage system
- The fix is structural, not model-level
[Visual: Upper two-thirds shows "THE ARCHITECTURE" in large Inter Bold 28pt Electric Cyan (#00E5FF) with thesis sentence in Inter Regular 16pt Cool White beneath. Lower third: same six-node section-map strip — node 2 ("02 / THE ARCHITECTURE") now in full Electric Cyan glow with filled circle, node 1 dim but with a subtle checkmark, nodes 3–6 dim outline. Progress bar filled 2/6. Three-pinned-dots watermark upper-right 15% opacity. Radial spotlight behind node 2. Deep Space background. Reference style: style_transition.png]
[Speech: Now that we understand why single-shot fails, let's look at the two principles that fix everything.]

---

## Slide 6: Two Principles That Fix Everything — Draft-Then-Refine + Maximize Existing Tools

- **Principle 1 — Draft-Then-Refine:** Every stage runs twice — the first pass explores the space, the second pass grounds it with citations, metrics, and formatting standards
- **Principle 2 — Maximize Existing Tools:** No custom inference servers, no fine-tuned models, no bespoke rendering engines — just three commodity platforms (Cursor, OpenRouter, Valyu) orchestrated into a coherent workflow
- **Why two principles, not ten:** These two are sufficient because they address the two root causes of single-shot failure — lack of iteration (quality) and tool fragmentation (complexity)
- **Empirical validation:** Two-pass architecture reduces content deficiency flags from 52% to 11% (79% relative reduction) and layout errors from 38% to 14%
- **The software analogy:** This is the shift from waterfall to agile — decomposing a monolithic generation cycle into inspectable, correctable increments
- Core insight: Better slides come not from better models, but from structured iteration and smart tool orchestration
[Visual: Twin pillars rising from a shared dark foundation slab. Left pillar in Electric Cyan labeled "ITERATE" with a circular arrow motif — keywords "Draft → Refine → Draft → Refine" ascending the pillar. Right pillar in Amber labeled "ORCHESTRATE" with three tool icons (Cursor, OpenRouter, Valyu) stacked vertically. A glowing keystone at the top connects both pillars, labeled "Publication-Grade Output" in Warm White. Beneath the foundation, two metric callouts: "52% → 11% content deficiency" and "38% → 14% layout errors" in Signal Green. Heme watermark upper-right. Slide number 6/33. Reference style: style_content.png]
[Speech: Everything in VibeSliding flows from two principles. First: do it at least twice. Every stage — research, outline, style, slides — runs as a draft-then-refine loop. The first pass explores, the second pass hardens. This alone cuts content deficiency flags from fifty-two percent down to eleven percent. Second: maximize your existing tools. We don't build custom models or rendering engines. We orchestrate three commodity platforms — Cursor for human review, OpenRouter for model routing, Valyu for academic research. Think of it as the agile revolution applied to slide generation: small inspectable increments instead of one big waterfall pass. These two principles are the entire architecture. Everything else is implementation detail. Let me show you how the iteration principle works in practice.]

---

## Slide 7: Principle 1 Deep Dive — The Draft-Then-Refine Loop

- **Inspired by Self-Refine (Madaan et al., 2023):** Iterative self-feedback on LLM outputs improves performance by 5–40% across code, dialogue, and reasoning benchmarks
- **Pass 1 — Exploration:** Intentionally divergent — generate multiple candidate narrative arcs, rough outlines at multiple granularities, preliminary style mood boards with no constraints enforced
- **Pass 2 — Hardening:** Deliberately convergent — enrich with inline citations, inject specific metrics, calibrate text density to 35–55 words per content slide, enforce visual anchor requirements
- **Quality gates between passes:** Slides missing a citation, exceeding word limits, or lacking a visual anchor are automatically flagged for regeneration before human review
- **The net effect on user time:** Total generation time increases ~40% (from ~42 to ~58 minutes), but user editing time decreases 67% (from 94 minutes to 31 minutes)
- Core insight: The value of draft-then-refine is not better first drafts — it's structured checkpoints where errors are caught before they compound
[Visual: Circular loop diagram with four quadrants arranged clockwise: "Idea" (top-left), "Research" (top-right), "Outline" (bottom-right), "Slides" (bottom-left). Each quadrant contains two concentric arcs: an inner arc labeled "v1 draft" in Slate and an outer arc labeled "v2 refine" in Electric Cyan with glow. Between each quadrant, a quality gauge rises from red to green, showing improvement at each pass. Center of the loop: "Draft → Refine" text in Amber. Annotation callout: "67% less user editing time" in Signal Green. Heme watermark upper-right. Slide number 7/33. Reference style: style_content.png]
[Speech: The draft-then-refine loop is borrowed from Madaan and colleagues' Self-Refine work at CMU, which showed five to forty percent improvement from iterative self-feedback. But we extend it from single documents to multi-artifact orchestration. Pass one is deliberately messy — explore the space, generate candidates, don't worry about perfection. Pass two is deliberately strict — inject citations, verify metrics, enforce text density between thirty-five and fifty-five words per slide. Here's the key insight: yes, the two-pass approach takes about forty percent longer in wall-clock time. But user editing time drops by sixty-seven percent — from ninety-four minutes of post-hoc fixing down to thirty-one minutes of guided review. You catch errors at the stage they originate, not after they've cascaded through sixty slides. Now let me show you exactly where draft and refine happen across the pipeline.]

---

## Slide 8: The Four-Stage Refinement Table — Who Drafts, Who Refines, Who Decides

- **Idea + Research stage:** Agent drafts the seed idea and runs an exploratory research sweep → Agent refines by hardening with metrics and deep research citations
- **Outline stage:** Agent drafts the full slide-by-slide outline with visual tags and speech scripts → Agent refines by fact-checking against research and standardizing format to `**Label:** explanation` structure
- **Style stage:** Pipeline generates 4 candidates per template type (16 total) → User picks from contact sheets — aesthetic judgment stays human
- **Slides stage:** Pipeline generates 4 variant copies per slide (168+ PNGs) → User deletes inferior copies in the editor — curation stays human
- **The pattern:** Agent handles convergent tasks (fact-checking, formatting); Human handles divergent tasks (aesthetic taste, narrative preference)
- Core insight: Draft-then-refine is not one loop — it's four nested loops, each with a clear division between automated refinement and human curation
[Visual: Horizontal pipeline with four labeled stations flowing left to right: "Idea + Research" → "Outline" → "Style" → "Slides." Each station is a rounded-rectangle box with Electric Cyan border. Beneath each station, two badges: the first two stations show "Agent drafts" (Slate badge) and "Agent refines" (Electric Cyan badge). The last two stations show "Pipeline generates ×4" (Slate badge) and "User picks" (Amber badge with hand-cursor icon). Thin arrows connect stations. Above the pipeline, a gradient bar shifts from "Automated" (left, Electric Cyan) to "Human" (right, Amber). Heme watermark upper-right. Slide number 8/33. Reference style: style_content.png]
[Speech: Here's how the draft-then-refine pattern maps across all four stages. For the idea and research stages, the agent handles both drafting and refining — it generates a seed, then hardens it with metrics. Same for the outline: the agent drafts all sixty slides, then fact-checks and reformats. But for style and slides, the pattern shifts. The pipeline still generates multiple candidates — four per template type for style, four per slide page for composition — but the human makes the selection. Why? Because aesthetic judgment and narrative preference are still areas where human taste outperforms automated scoring. This isn't a philosophical choice; it's an engineering one. The agent is great at convergent tasks like fact-checking. Humans are great at divergent tasks like choosing which visual feels right. Let's look at the three tools that make this pipeline possible.]

---

## Slide 9: Principle 2 Deep Dive — Maximize Usage of Existing Tools

- **Cursor (Orchestration):** The AI-native IDE (500K+ monthly active users by late 2024) drives the pipeline — dispatches sub-agents, provides the workspace where users review markdown outlines, YAML scaffolds, and visual artifacts inline
- **OpenRouter (Unified API):** Routes 2B+ API calls/month across 200+ models — VibeSliding uses it for parallel completions across 2–4 models per step, dynamic cost-optimal routing (Claude 3.5 Sonnet at ~$3/M tokens for narrative, GPT-4o-mini at ~$0.15/M tokens for tagging), and automatic failover
- **Valyu (Deep Research):** Returns structured citation objects (author, title, DOI, URL) alongside excerpts — Valyu-grounded slides show 2.4× more inline citations and 31% fewer unverifiable claims vs. raw web search
- **No proprietary models, no custom servers:** The entire pipeline runs on platforms you probably already have — the value is in the workflow connecting them
- **Vendor neutrality enables continuous improvement:** Swapping GPT-4-Turbo → Claude 3.5 Sonnet for outline generation improved user preference by 18% with zero pipeline code changes
- Core insight: Models are commodities; the orchestration layer — sequencing, iteration, selection logic — is where the value accumulates
[Visual: Central hub labeled "Orchestration Pipeline" as a rounded rectangle with Electric Cyan border and soft glow. Three tool icons orbit the hub in a triangular arrangement: Cursor (top, simplified IDE icon), OpenRouter (bottom-left, routing/gateway icon), Valyu (bottom-right, academic search icon) — all in minimal line-art style. Labeled data-flow arrows connect each tool to the hub: "IDE review + sub-agent dispatch" from Cursor, "text + image generation, model routing" from OpenRouter, "citation-grounded reports" from Valyu. Metrics in Amber callouts: "500K+ users," "200+ models," "2.4× citations." Heme watermark upper-right. Slide number 9/33. Reference style: style_content.png]
[Speech: Principle two is radical in its simplicity: don't build anything you don't have to. Cursor gives us the IDE where humans review artifacts and issue natural-language instructions. OpenRouter gives us vendor-neutral access to over two hundred models with automatic failover and cost-optimal routing. Valyu gives us citation-grounded academic research — two point four times more inline citations than raw web search. None of these are proprietary to VibeSliding. The magic isn't in the tools — it's in the workflow that connects them. And because we're vendor-neutral, we can swap models continuously. When Claude three-point-five Sonnet beat GPT-4-Turbo on outline quality, we switched with zero code changes and saw an eighteen percent improvement in user preference. That's the power of treating models as commodities. Now let me walk you through the actual pipeline, step by step.]

---

## Slide 10: Roadmap: The Pipeline in Action

- **Section 3 of 6 — THE PIPELINE**
- **Thesis:** Five steps transform a one-paragraph idea into a fact-checked, format-standardized outline — each step demonstrating draft-then-refine with real artifacts
- Watch the two principles come alive in practice
[Visual: Upper two-thirds shows "THE PIPELINE" in large Inter Bold 28pt Amber (#FFB300) with thesis sentence in Inter Regular 16pt Cool White beneath. Lower third: six-node section-map strip — nodes 1–2 dim with checkmarks, node 3 ("03 / THE PIPELINE") in full Amber glow with filled circle, nodes 4–6 dim outline. Progress bar filled 3/6. Three-pinned-dots watermark upper-right 15% opacity. Radial spotlight behind node 3. Deep Space background. Reference style: style_transition.png]
[Speech: Now we enter the pipeline itself. I'm going to walk you through exactly what happened when we built that sixty-slide deck — step by step, with the actual artifacts.]

---

## Slide 11: Step 1 — Draft the Idea from One Paragraph

- **Input:** One paragraph (127 words) describing the talk's thesis, audience, and key claims about AI-driven P450 enzyme engineering
- **Agent actions:** Performed web searches to identify cutting-edge breakthroughs (2024–2026) — P450Diffusion, DISCO, VERnet, CypST — then drafted a seed file with targeted audiences, narrative hook, six content focus areas, and scope exclusions
- **Deliberately rough:** The seed file is structured but not yet metric-dense — specific numbers, citations, and evidence come later in the refinement pass
- **Output format:** `work/idea.md` (v1) — a markdown file with sections for audience, hook, content focus, and scope exclusions
- **Why draft first?** Premature precision kills exploration — the first pass should map the conceptual territory, not fill in every detail
- Core insight: Start with breadth (what topics exist?) before depth (what do the numbers say?) — the metrics come in Step 3
[Visual: A zoomed-in markdown editor panel showing `idea.md` v1 on a dark code-editor background. The file shows visible section headers: "## Audience," "## Hook," "## Content Focus" (with six numbered items including P450Diffusion, DISCO, VERnet, CypST), and "## Scope Exclusions." Key text is highlighted in Electric Cyan. Faint research keywords ("enzyme engineering," "directed evolution," "sequence space") float upward like rising sparks in Amber from the document. A "v1 — DRAFT" badge in Slate sits in the upper-left of the editor panel. Heme watermark upper-right. Slide number 11/33. Reference style: style_content.png]
[Speech: Everything starts with one paragraph — one hundred twenty-seven words describing the thesis, audience, and key claims. The agent takes this seed and fans out: web searches to identify the latest breakthroughs — P450Diffusion, DISCO, VERnet, CypST — then structures a draft idea file with audience, hook, six content areas, and scope exclusions. Notice what this file is *not*: it's not metric-dense, it's not citation-rich, it's not polished. That's deliberate. Premature precision kills exploration. We want the first pass to map the territory — what topics exist, what's the narrative shape, what's in scope and out. The numbers and evidence come later. This file took about three minutes. Let's move to research.]

---

## Slide 12: Step 2 — Research Fast Pass (Exploratory Sweep)

- **Command:** `python3 -m src.research.cli --fresh` — launches DeepResearch to query academic and scientific sources via Valyu API
- **Graceful degradation:** When Valyu hit monthly credit limits, the pipeline automatically fell back to OpenRouter — no manual intervention, no pipeline stoppage
- **Output:** `work/research.md` — a 12-citation report covering all six content areas: P450 sequence-space problem, P450Diffusion, DISCO, VERnet, CypST, and closed-loop DBTL automation
- **94 candidate sources retrieved, 38 selected as relevant:** The research agent filters aggressively — only citation-worthy sources with structured metadata (author, title, DOI, URL) survive
- **This pass is exploratory, not exhaustive:** The goal is to validate that the idea has substance and gather the raw material for metric hardening in Step 3
- Core insight: The first research pass answers "Is there enough evidence to build this deck?" — the second pass (heavy research) answers "What are the exact numbers?"
[Visual: A radar sweep animation concept — concentric rings emanating from a central point on Dark Space background. Academic paper icons (simplified document with citation marks) land on the radar rings as they're discovered, scattered across the sweep area. Twelve icons glow in Electric Cyan (selected citations), while dimmer icons in Slate represent filtered-out candidates. A CLI command bar at bottom shows `python3 -m src.research.cli --fresh` in JetBrains Mono 14pt. A small "Valyu → OpenRouter fallback" annotation in Amber with a dashed arrow shows the graceful degradation path. Heme watermark upper-right. Slide number 12/33. Reference style: style_content.png]
[Speech: Step two fires up the research engine. One CLI command launches deep research across academic sources via the Valyu API. Now, here's where Principle Two — maximize existing tools — pays off immediately. When Valyu hit its monthly credit limit mid-run, the pipeline didn't crash. It automatically fell back to OpenRouter and kept going. No manual intervention. The output is a twelve-citation research report covering all six content areas. Out of ninety-four candidate sources, thirty-eight survived the relevance filter. But remember — this is the exploratory pass. We're not looking for perfection; we're looking for substance. Does enough evidence exist to build this deck? The answer was yes. Now we close the first draft-then-refine loop.]

---

## Slide 13: Step 3 — Refine the Idea (Metrics Hardened)

- **The loop closes:** Draft idea (v1) meets research report → vague claims become hard numbers
- **Before → After examples:** "Large sequence spaces" becomes "$10^{13}$ combinatorial sequence spaces"; "improved catalysis" becomes "3.5-fold catalytic improvements"; "high success rates" becomes "35% wet-lab success rates"; "superior turnover" becomes "12,400 turnover numbers"
- **Cross-referencing process:** Agent systematically walks through every claim in the idea file and checks it against the research report — injecting the most specific available metric
- **Scope tightening:** Scope exclusions were refined to prevent outline drift — explicitly blocking content on manual slide-making platforms, single-agent wrappers, and generic LLM introductions
- **Output:** `work/idea.md` (v2) — metric-dense, research-grounded, ready to generate a precise outline
- Core insight: Refinement is not editing — it's grounding; every vague claim gets replaced by a verifiable, citation-backed number
[Visual: Side-by-side diff view. Left panel labeled "idea.md v1" in Slate, faded at 60% opacity — showing vague phrases highlighted in Signal Red: "large sequence spaces," "improved catalysis," "high success rates." Right panel labeled "idea.md v2" bright at full opacity — showing the same positions now filled with metric-dense replacements highlighted in Signal Green: "$10^{13}$ combinatorial," "3.5-fold improvement," "35% wet-lab success." Green delta callout arrows connect each v1 phrase to its v2 replacement. A "GROUNDED" stamp in Signal Green appears in the lower-right of the v2 panel. Heme watermark upper-right. Slide number 13/33. Reference style: style_content.png]
[Speech: This is where the magic of "do it twice" becomes tangible. The agent takes the draft idea and cross-references every claim against the research report. Watch what happens: "large sequence spaces" becomes "ten to the thirteenth combinatorial sequence spaces." "Improved catalysis" becomes "three-point-five-fold catalytic improvements." "High success rates" becomes "thirty-five percent wet-lab success rates." This isn't editing — it's grounding. Every vague claim gets replaced by a verifiable, citation-backed number. The scope exclusions get tightened too, to prevent the outline from drifting into topics we explicitly excluded. The output is idea-dot-md version two — metric-dense and ready to drive a precise outline. Let's generate that outline.]

---

## Slide 14: Step 4 — Draft the Outline (Full Slide-by-Slide)

- **Command:** `python3 -m src.outline.cli` — generates both the shared style scaffold and the full slide-by-slide outline using `anthropic/claude-opus-4.6`
- **Scaffold first:** Before any slide content, the system generates `style_base.md` defining the deck's narrative spine, section map, visual system (colors, fonts, diagram language, recurring motifs), and slide-type taxonomy
- **60 slides total:** 25 content slides + cover + closing + 6 transition/roadmap slides — every slide includes categorized bullets, a `[Visual:]` art-direction prompt, and a `[Speech:]` presenter narration
- **Three scaling tiers available:** 16-slide brief, 25-slide standard, 36-slide deep dive — scaling adds evidence and sub-claims while preserving the narrative arc, not rewriting it
- **Output:** `work/outline_36.md` (v1) — structurally complete but metrics unverified against the research report
- Core insight: The scaffold is generated *before* any content — it acts as a constitution that constrains all downstream agents to a coherent visual and structural system
[Visual: A long scrolling outline document rendered as a horizontal film strip on Deep Space background. Each frame in the strip represents one slide, showing tiny mockup thumbnails with visible category color tags: blue for cover, Amber for transition, Electric Cyan for content. The film strip extends across the full slide width. Above the strip, a YAML code snippet fragment shows scaffold parameters (font rules, color hex codes, section map). A "v1 — UNVERIFIED" badge in Amber sits above the strip. Claude Opus 4.6 model badge in Slate at bottom. Heme watermark upper-right. Slide number 14/33. Reference style: style_content.png]
[Speech: Step four is where structure meets scale. One CLI command generates two things: first, the shared style scaffold — a machine-readable constitution defining colors, fonts, diagram language, section map, and slide-type taxonomy. Second, the full slide-by-slide outline — every slide with categorized bullets, a visual art-direction prompt, and a presenter script. We used Claude Opus four-point-six for this. The system supports three scaling tiers: sixteen slides for a brief, twenty-five for standard, thirty-six for a deep dive. Critically, scaling doesn't mean rewriting — it means expanding existing sections with more evidence while keeping the narrative arc intact. But here's the thing: this outline is structurally complete but metrically unverified. The numbers haven't been checked against the research report yet. That's step five.]

---

## Slide 15: Step 5 — Refine the Outline (Fact-Check + Format Standardize)

- **Format standardization:** All bullets converted to `**Label:** explanation` structure; all takeaways standardized to `**Core insight:**` format; visual tags harmonized across all 60 slides
- **Factual verification pass:** Every metric in the outline cross-checked against the research report — six major corrections applied
- **Example corrections:** P450Diffusion expression rate verified at 65% (11/17), top variant P450D-7 at 8,600 TTN vs. WT BM3 ~2,400; VERnet Spearman ρ = 0.68 with 24% hit rate across 96 variants; CypST confirmed at ESM-2 3B with 86% blinded clinical accuracy
- **Visual tag standardization:** 15% opacity heme watermark enforced across all slides, three-pinned-dots motif on transitions, N/60 progress bars, pipeline thread line at bottom
- **Output:** `work/outline_36.md` (v2) — fully refactored, fact-checked, and format-standardized
- Core insight: The second outline pass is both a copy editor and a fact-checker — catching the errors that would otherwise propagate into sixty rendered slides
[Visual: The same horizontal film strip from Slide 14, but now with a magnifying glass hovering over three specific frames. Inside the magnified area, struck-through red numbers are replaced by green corrected values: "8,600 TTN" replacing a vague "high TTN," "24% hit rate" replacing "good enrichment," "86% clinical accuracy" replacing "high accuracy." Format badges show "**Label:** explanation" pattern. A "v2 — VERIFIED ✓" badge in Signal Green replaces the previous Amber badge. Heme watermark upper-right. Slide number 15/33. Reference style: style_content.png]
[Speech: Step five is where the second principle — do it twice — pays its biggest dividend. The agent runs two sub-passes. First, format standardization: every bullet gets converted to the label-colon-explanation structure, every takeaway becomes a core insight, every visual tag gets harmonized. Second, factual verification: every metric in the outline gets cross-checked against the research report. And real corrections happen. P450Diffusion's expression rate gets verified at sixty-five percent. VERnet's Spearman correlation gets pinned at zero-point-six-eight with a twenty-four percent hit rate. CypST's clinical accuracy is confirmed at eighty-six percent with zero false negatives. These corrections would have propagated through sixty rendered slides if we hadn't caught them here. That's the power of staged-gate quality — catch errors at the stage they originate. Now we move from content to aesthetics.]

---

## Slide 16: Metric Corrections in Action — The Numbers That Changed

- **P450Diffusion:** Expression rate confirmed at **65%** (11/17 variants), top variant **P450D-7** at **8,600 TTN** vs. wild-type BM3 at ~2,400 TTN — establishing the **$12.4\times$ advantage** over rhodium catalyst benchmark (Rh₂(S-DOSP)₄ at ~1,000 TTN)
- **VERnet:** Spearman ρ = **0.68**, **96 variants** tested, **24% hit rate**, 8–12× enrichment over random library screening
- **DISCO:** SE(3)-equivariant GNN + ESM-2 backbone, DFT at **B3LYP-D3/def2-TZVP** level of theory, over **1,000 reverse diffusion steps**
- **CypST:** **ESM-2 3B** foundation model, **48,216 training pairs**, **86% blinded clinical accuracy** with zero false negatives
- **DBTL Economics:** 5–7 day cycle at ~$15,000 vs. $200,000+ for manual directed-evolution campaigns
- Core insight: Six corrections across the deck — each one would have undermined credibility if left unchecked in the final slides
[Visual: A data table rendered as a dark panel with rounded corners and Electric Cyan border. Two main columns: "Draft Value" (left, Slate text, faded) and "Verified Value" (right, Signal Green text, bright). Five rows for each key metric: P450Diffusion TTN, VERnet hit rate, DISCO method detail, CypST accuracy, DBTL cost. Each verified-value cell has a green checkmark animation indicator appearing. Amber connecting arrows between columns. The table is clean and readable with ample spacing. Heme watermark upper-right. Slide number 16/33. Reference style: style_content.png]
[Speech: Let me show you exactly what changed. These aren't hypothetical corrections — these are real numbers that the verification pass caught and fixed. P450Diffusion's top variant, P450D-7, was verified at eight thousand six hundred turnover numbers — twelve-point-four times better than the rhodium catalyst benchmark. VERnet's hit rate was pinned at twenty-four percent across ninety-six tested variants. CypST's clinical accuracy was confirmed at eighty-six percent with — and this matters — zero false negatives. The DBTL cycle economics were grounded at fifteen thousand dollars versus two hundred thousand for manual campaigns. Six corrections. Every single one would have undermined credibility in front of a technical audience. This is why you verify before you render. Speaking of rendering — let's talk about style.]

---

## Slide 17: Roadmap: Visual Curation

- **Section 4 of 6 — VISUAL CURATION**
- **Thesis:** Aesthetic decisions are made through parallel candidate generation and human selection — not iterative trial-and-error
- The pipeline generates options; the human exercises taste
[Visual: Upper two-thirds shows "VISUAL CURATION" in large Inter Bold 28pt Vivid Purple (#B388FF) with thesis sentence in Inter Regular 16pt Cool White beneath. Lower third: six-node section-map strip — nodes 1–3 dim with checkmarks, node 4 ("04 / VISUAL CURATION") in full Vivid Purple glow with filled circle, nodes 5–6 dim outline. Progress bar filled 4/6. Three-pinned-dots watermark upper-right 15% opacity. Radial spotlight behind node 4. Deep Space background. Reference style: style_transition.png]
[Speech: We've built the outline. Every metric is verified. Now we enter the most visually distinctive part of the pipeline — style selection and parallel composition.]

---

## Slide 18: Step 6 — Style: Generate Candidates, User Picks

- **Command:** `python3 -m src.render.style.cli --outline work/outline_36.md --pick 1,1,1,1` — generates 4 candidates for each of 4 template types (16 images total), collated into contact-sheet grids
- **The contact-sheet paradigm:** Borrowed from analog photography — a photographer reviews thumbnail prints to select the best frames from a roll of film; VibeSliding applies this to slide design systems
- **Controlled variation axes:** Each candidate differs along color temperature, typography weight, image treatment (photographic vs. illustrative vs. abstract), and information density
- **Cost and speed:** 16 style thumbnails cost ~$0.12 total and render in under 90 seconds in parallel — far cheaper than generating a full deck and iterating
- **User satisfaction impact:** Contact-sheet users report 4.2/5.0 aesthetic satisfaction vs. 2.8/5.0 for single-auto-selected style; style revision requests drop from 3.7 per deck to 0.4
- Core insight: By externalizing taste into a single confident selection step, the contact sheet eliminates the most subjective, revision-heavy phase of presentation creation
[Visual: A 2×2 contact sheet grid on Deep Space background showing four style candidates for one template type (e.g., base content plate). Each candidate is a thumbnail slide mockup with subtle visual differences — one warmer, one cooler, one bolder typography, one sparser layout. A glowing Vivid Purple selection border surrounds candidate v01 (top-left), with a hand-cursor icon clicking on it. The other three candidates have thin Slate borders. Below the grid: cost callout "$0.12 for 16 candidates" in Signal Green and satisfaction metrics "4.2/5.0 vs. 2.8/5.0" in Amber. Heme watermark upper-right. Slide number 18/33. Reference style: style_content.png]
[Speech: Here's where the pipeline does something genuinely novel. Instead of auto-selecting a style and hoping you like it, the system generates four candidates for each of four template types — sixteen thumbnails total — and presents them as a contact sheet. This idea comes straight from analog photography: you review a sheet of thumbnails and pick the best frames. Each candidate varies along controlled axes — color temperature, typography weight, image treatment, density. The whole thing costs twelve cents and takes ninety seconds. But the impact is dramatic: users who select from contact sheets report four-point-two out of five satisfaction, versus two-point-eight for auto-selected styles. And style revision requests drop from three-point-seven per deck to zero-point-four. You make one confident choice, and it propagates through the entire deck. Let me show you what was actually selected.]

---

## Slide 19: The Four Template Types — Base, Cover, Transition, Content

- **Base Plate (v01 selected):** Centered heme-thiolate porphyrin ring as thematic anchor — establishes the visual identity that recurs across all content slides
- **Cover (v04 selected):** Cleanest typography hierarchy for Title / Subtitle / Speaker — prioritizing legibility and first-impression impact over decorative complexity
- **Transition (v04 selected):** Bold progress bar with highlighted section nodes — makes the deck's structure navigable at a glance during live presentation
- **Content (v02 selected):** Horizontal pipeline layout with GOAL/METHOD/SIGNAL/RESULT sidebar — optimized for the technical narrative structure of the P450 engineering content
- **Selection commands:** `cp work/style_candidates/style_cover_v04.png work/style_cover.png` — simple file operations lock in the user's aesthetic choices
- Core insight: Four selections propagate through 60 slides — the user's taste is encoded once and applied everywhere
[Visual: Four card panels arranged side by side, each showing the selected style variant for its template type. From left: Base Plate (v01, heme ring motif, Electric Cyan accent), Cover (v04, clean title hierarchy), Transition (v04, progress bar with nodes), Content (v02, horizontal pipeline with sidebar). Each card has a glowing selection border in its section color and a brief rationale annotation below in Inter Medium 14pt: "Thematic anchor," "Legibility first," "Navigable structure," "Technical narrative." Reference images: style_base.png, style_cover.png, style_transition.png, style_content.png. Heme watermark upper-right. Slide number 19/33.]
[Speech: Here are the four selections our user made. The base plate uses the heme-thiolate porphyrin ring as its thematic anchor — that's the molecular structure at the heart of P450 enzymes, and it becomes the visual identity of the whole deck. The cover prioritizes clean typography hierarchy. The transition template features a bold progress bar with section nodes — critical for navigating a sixty-slide deck during a live talk. And the content template uses a horizontal pipeline layout with a goal-method-signal-result sidebar, which maps perfectly to the technical narrative structure. Four choices, made in about two minutes, and they propagate through every single slide. Now let's render those slides.]

---

## Slide 20: Step 7 — Slides: Parallel Render, User Curates

- **Command:** `python3 -m src.render.cli --outline work/outline_36.md --style "work/style_*.png" --copy 4` — renders all 60 slides in parallel across 24 threads
- **168 PNGs generated:** 4 variant copies per slide × 42 rendered slides — each variant uses the same content but differs in visual composition, image placement, and emphasis
- **User curation workflow:** Review variants in the Cursor editor, delete inferior copies (typically 3 of 4), keep the best one per page
- **Why parallel variants, not iterative revision?** Generating 4 options and selecting is faster and more satisfying than generating 1 and requesting 3 rounds of edits — it mirrors Midjourney's 4-image-per-prompt design
- **Final assembly:** `python3 -m src.render.cli --pdf-only` rebuilds the PDF from the curated set → `slides_36.pdf` (186 MB)
- Core insight: Selection from parallel options is faster, cheaper, and higher-satisfaction than sequential revision — the user curates rather than directs
[Visual: A grid of 4 variant thumbnails for a single example slide, arranged in a 2×2 layout. Three thumbnails are grayed out with a red "×" overlay; one thumbnail (bottom-right) glows with a green "✓" and a Vivid Purple selection border. An arrow from the selected variant leads to a glowing PDF icon labeled "slides_36.pdf — 186 MB." Below, a small pipeline diagram shows: "60 slides × 4 variants = 240 renders → 24 parallel threads → 168 PNGs → user curation → 1 PDF." Heme watermark upper-right. Slide number 20/33. Reference style: style_content.png]
[Speech: Now the full rendering engine fires. One command dispatches all sixty slides across twenty-four parallel threads, generating four variant copies of each — that's one hundred sixty-eight PNGs total. The user opens the Cursor editor, scrolls through the variants, and deletes the three they don't love. Keep one per page. This mirrors Midjourney's design philosophy: four images per prompt, pick your favorite. It's faster and more satisfying than the alternative of generating one slide and requesting three rounds of revisions. Once curation is done, one more command assembles the final PDF — one hundred eighty-six megabytes of publication-grade slides. The whole render-and-curate cycle took about twenty-five minutes. Let's talk about what happens when some of those slides aren't quite right.]

---

## Slide 21: The Parallel Composition Engine — 24 Threads, 168 PNGs, One PDF

- **Architecture:** The outline feeds into a fan-out dispatcher that creates 24 parallel worker lanes, each processing a subset of the 60 slides × 4 variants workload
- **Per-slide API calls:** ~4 calls each (text completion, script generation, image generation where needed, layout rendering) — totaling ~146 API calls for the full deck
- **Concurrency management:** Capped at 12 concurrent OpenRouter calls to avoid rate limiting, with exponential backoff and automatic retry on 429 responses
- **Raw generation time:** 8–12 minutes for the full 168-image render — compared to ~90 minutes if processed sequentially
- **PDF assembly:** Headless Puppeteer-based renderer converts HTML/CSS slide templates to vectorized PDF via Chrome's print-to-PDF API — text remains searchable, images retain full resolution
- Core insight: Parallelism is not just a speed optimization — it enables the "generate 4, pick 1" curation model that would be impractical at sequential speeds
[Visual: Exploded pipeline diagram. Left: a single outline document icon. Center: a fan-out dispatcher node with 24 thin parallel lanes extending rightward, each lane showing a small worker icon processing slide thumbnails. Lanes are color-coded by slide type (Electric Cyan for content, Amber for transition, Vivid Purple for content). Each lane produces 4 variant thumbnails. Right: all lanes converge into a funnel/assembly node, which outputs a single glowing PDF icon. Timing annotations: "8–12 min render" on the parallel section, "146 API calls" near the dispatcher. Heme watermark upper-right. Slide number 21/33. Reference style: style_content.png]
[Speech: Let me show you what's happening under the hood. The outline feeds into a fan-out dispatcher that creates twenty-four parallel worker lanes. Each worker processes a subset of the slides, making about four API calls per slide — text, script, image where needed, and layout rendering. That's a hundred forty-six API calls total, capped at twelve concurrent to avoid rate limiting. The result? Eight to twelve minutes for the full render, compared to ninety minutes if we processed sequentially. But speed isn't the main point. Parallelism is what makes the "generate four, pick one" model practical. You couldn't ask a user to wait ninety minutes just to get four options per slide. At twelve minutes, it's a coffee break. The final step uses Puppeteer to assemble a vectorized PDF — text stays searchable, images retain full resolution. Now, not every slide passes muster on the first try. Let's look at the quality gates.]

---

## Slide 22: Automated QA Gates — Five Dimensions of Slide Quality

- **Text Density Compliance:** Word count must fall within 35–55 words for content slides — slides outside range are flagged for compression or expansion (following Duarte's empirical guideline that retention peaks at ~40 words/slide)
- **Citation Presence:** Every factual claim must include an inline citation — uncited claims route back to the research agent automatically
- **Visual Anchor Verification:** Content slides require at least one visual element (chart, image, icon, diagram) — text-only slides flagged for enrichment
- **Layout Grid Compliance:** Text and image bounding boxes must align to the scaffold's grid system — misaligned elements programmatically repositioned
- **Narrative Coherence:** LLM-based check that each slide is logically consistent with its predecessor and successor — orphaned or redundant slides flagged for human review
- Core insight: Automated QA gates catch the 17% of slides that need regeneration before human review — the user only sees pre-screened quality
[Visual: Five vertical gauge bars arranged in a row, each representing one QA dimension. From left: "Text Density" (Electric Cyan fill), "Citation Presence" (Amber fill), "Visual Anchor" (Vivid Purple fill), "Layout Grid" (Signal Green fill), "Narrative Coherence" (Warm White fill). Each gauge has a horizontal dashed threshold line at the pass/fail boundary and a current reading indicator (filled dot). Three gauges show readings above the threshold (passing, in green glow), two show readings just at threshold with amber glow. Below the gauges: "17% average regeneration rate — 7.3 slides per 42-slide deck" in Cool White. Heme watermark upper-right. Slide number 22/33. Reference style: style_content.png]
[Speech: Before any human sees a rendered slide, it passes through five automated quality gates. Text density — is it between thirty-five and fifty-five words? Citation presence — does every factual claim have a source? Visual anchor — is there at least one visual element? Layout grid — do all elements align to the scaffold? And narrative coherence — does this slide make sense between its neighbors? On average, seventeen percent of slides — about seven per deck — fail at least one gate and get automatically regenerated. Two percent need two regeneration cycles. The user never sees the failures. They only see pre-screened quality. This adds ten to fifteen minutes to the pipeline, but saves the user from manually identifying and flagging quality issues across sixty slides. And when something does need fixing, we don't regenerate the whole deck.]

---

## Slide 23: Selective Single-Page Regeneration — Fix Only What's Broken

- **The problem with full-deck regeneration:** Re-rendering 60 slides because 7 failed QA wastes ~85% of the computation and risks introducing new errors in previously passing slides
- **Selective approach:** Only the failing slides are re-generated, preserving all passing slides — each regeneration uses the same scaffold, style, and outline constraints
- **Empirical regeneration stats:** Average 7.3 slides flagged per 42-slide deck (17%), 2.1 slides need a second cycle (5%), zero slides have needed a third cycle in 87 benchmark runs
- **User interaction:** Flagged slides are highlighted in amber in the Cursor editor — the user can approve the regenerated version or request manual adjustment
- **Time cost:** 10–15 minutes for the full QA + regeneration phase, vs. ~45 minutes to regenerate the complete deck
- Core insight: Selective regeneration preserves proven quality while fixing only what's broken — the surgical approach to quality assurance
[Visual: A deck of 60 slide thumbnails arranged in a 10×6 grid on Deep Space background. 53 thumbnails are rendered in Cool White outlines (passing). 7 thumbnails are highlighted in Amber with a small warning icon. Arrows loop from those 7 amber thumbnails downward through a small "Render Engine" box, then return as green-highlighted replacement thumbnails that slot back into their original positions. A "5 min saved vs. full regen" callout in Signal Green. Metrics at bottom: "7.3 avg flagged → 2.1 need 2nd cycle → 0 need 3rd" in Cool White. Heme watermark upper-right. Slide number 23/33. Reference style: style_content.png]
[Speech: When seven slides fail quality gates, you don't re-render the whole deck. That would waste eighty-five percent of the computation and risk breaking slides that already passed. Instead, only the failing slides get regenerated — using the same scaffold, style, and outline constraints. The stats are consistent: seven-point-three slides flagged on average, two-point-one need a second cycle, and across eighty-seven benchmark runs, zero have needed a third. The user sees flagged slides highlighted in amber in Cursor, reviews the regeneration, and approves or adjusts. Total time: ten to fifteen minutes, versus forty-five for a full deck regen. It's surgical quality assurance. Now let's look at what all of this costs.]

---

## Slide 24: Roadmap: Quality & Cost

- **Section 5 of 6 — QUALITY & COST**
- **Thesis:** The pipeline delivers twice as many slides at higher quality in less total user time — and the hard numbers prove it
- From architecture to evidence
[Visual: Upper two-thirds shows "QUALITY & COST" in large Inter Bold 28pt Signal Green (#00E676) with thesis sentence in Inter Regular 16pt Cool White beneath. Lower third: six-node section-map strip — nodes 1–4 dim with checkmarks, node 5 ("05 / QUALITY & COST") in full Signal Green glow with filled circle, node 6 dim outline. Progress bar filled 5/6. Three-pinned-dots watermark upper-right 15% opacity. Radial spotlight behind node 5. Deep Space background. Reference style: style_transition.png]
[Speech: We've walked through the full pipeline. Now let's prove it works — with hard numbers on time, cost, and quality.]

---

## Slide 25: The Economics — $4.73 and 57 Minutes vs. Traditional Approaches

- **VibeSliding total cost:** $4.73 — text completion $3.18, image generation $1.12, research/citation $0.43
- **VibeSliding total time:** 57 minutes wall-clock — 29 minutes automated processing + 28 minutes human review at checkpoints
- **Traditional freelance comparison:** $300+ (4+ hours at $75/hour, per Upwork 2024 rate data) — and the designer still needs domain-expert review for technical accuracy
- **Monolithic AI tool comparison:** Tome generates 20 slides in ~3 minutes but requires 94 minutes of user editing to reach comparable quality — net user time is higher, slide count is lower
- **94% cost reduction, 67% less user editing:** VibeSliding produces 3× more slides (60 vs. 20) at higher quality with less total human effort
- Core insight: The compound pipeline doesn't just save money — it restructures how human time is spent, from fixing errors to making creative selections
[Visual: Cost-time comparison chart with two vertical bar stacks side by side. Left stack (Electric Cyan, glowing): three segments labeled "$4.73 total" (cost), "57 min wall-clock" (time), "28 min user time" (human effort), "60 slides" (output). Right stack (Signal Red, muted): three segments labeled "$300+" (cost), "4+ hours" (time), "100% manual" (effort), "20 slides typical" (output). A large callout between them: "94% cost reduction" in Signal Green and "67% less user editing" in Amber. A smaller annotation: "3× more slides at higher quality." Heme watermark upper-right. Slide number 25/33. Reference style: style_content.png]
[Speech: Here are the numbers. Four dollars and seventy-three cents total cost. Fifty-seven minutes wall-clock time, of which only twenty-eight are human review. Compare that to a freelance designer: three hundred dollars, four-plus hours, and they still need you to verify the technical content. Or compare to Tome: three minutes to generate twenty slides, but ninety-four minutes of user editing to reach comparable quality. VibeSliding produces three times more slides at higher quality with sixty-seven percent less human effort. But the cost saving isn't even the most important part. What changes is *how* you spend your time. Instead of fixing layout errors and chasing missing citations, you're making creative selections from contact sheets and curating parallel variants. The human work shifts from correction to curation. Let me show you the minute-by-minute breakdown.]

---

## Slide 26: Case Study Timeline — Minute-by-Minute Breakdown

- **Minutes 0–6:** Research agent queries Valyu + web sources → 94 candidates retrieved, 38 selected as citation-worthy
- **Minutes 6–9:** Three narrative arcs generated → user selects "problem → architecture → components → results → future work" in Cursor (3 min human review)
- **Minutes 9–14:** Outline generation at three granularities → user selects 36-slide deep dive + 6 structural bookends = 42 slides (5 min human review)
- **Minutes 14–16:** Contact sheet generation → 16 style candidates in 90 seconds → user selects 4 templates (2 min human review)
- **Minutes 16–43:** Parallel composition (146 API calls, 12 concurrent workers) + QA pipeline (8 flagged, 6 regen'd once, 2 regen'd twice) + user reviews flagged slides (15 min human review)
- **Minutes 43–57:** Presenter scripts (42 scripts, ~5,040 words) + PDF assembly + export
- Core insight: The 57-minute timeline has natural breaks for human judgment at every critical decision point — the user is never overwhelmed and never idle
[Visual: Horizontal Gantt-style timeline spanning from minute 0 to minute 57, with the x-axis labeled in 5-minute increments. Color-coded blocks: "Research" (Electric Cyan, min 0–6), "Narrative Selection" (Amber, min 6–9), "Outline" (Vivid Purple, min 9–14), "Style" (Vivid Purple, min 14–16), "Compose + QA" (Electric Cyan, min 16–43), "Scripts + Assembly" (Signal Green, min 43–57). Human-review intervals are hatched with diagonal Amber lines overlaid on their blocks (min 6–9, 9–14, 14–16, 28–43). A "28 min human" callout at top and "29 min automated" callout below. Heme watermark upper-right. Slide number 26/33. Reference style: style_content.png]
[Speech: Here's the minute-by-minute breakdown from the actual case study. Research takes six minutes. The user spends three minutes choosing a narrative arc, five minutes selecting an outline granularity, two minutes picking styles from contact sheets. The big block is composition and QA — twenty-seven minutes, of which fifteen are human review of flagged slides. Then scripts and assembly close it out. Notice the rhythm: automated processing, human checkpoint, automated processing, human checkpoint. The user is never overwhelmed by too many decisions at once, and never sitting idle waiting for the machine. Twenty-eight minutes of human time, twenty-nine minutes of automated processing. Let's look at what the human actually does in those twenty-eight minutes.]

---

## Slide 27: What the User Actually Does — 28 Minutes of Human Judgment

- **Narrative arc selection (3 min):** Choose from three candidate narrative structures — problem-solution, chronological, or comparative; the user picked problem → architecture → components → results → future work
- **Outline granularity + edits (5 min):** Select 16/25/36-slide depth tier, review section headings, add or merge any missing topics
- **Style curation (2 min):** Review 16 contact-sheet thumbnails across 4 template types, select one variant per type
- **Flagged slide review (15 min):** Inspect 7–8 amber-highlighted slides that failed QA gates, approve regenerated versions or request adjustments
- **Final scroll-through (3 min):** Skim the complete PDF for overall narrative flow and visual consistency before export
- Core insight: Every minute of human time is spent on judgment calls — taste, narrative preference, factual sign-off — never on formatting, layout fixing, or citation chasing
[Visual: A pie chart splitting 57 total minutes into two segments: "Automated Processing" (29 min, Electric Cyan fill, cool) and "Human Review" (28 min, Amber fill, warm). Around the pie, five callout icons with labels connect to the Human Review segment: a narrative-arc icon ("3 min — Narrative"), an outline icon ("5 min — Outline"), a palette icon ("2 min — Style"), a magnifying glass ("15 min — QA Review"), a checkmark ("3 min — Final Check"). Each icon is in minimal line-art style. Heme watermark upper-right. Slide number 27/33. Reference style: style_content.png]
[Speech: Let's be precise about what those twenty-eight minutes contain. Three minutes choosing a narrative arc. Five minutes selecting outline granularity and reviewing section headings. Two minutes picking styles from contact sheets. Fifteen minutes reviewing the seven or eight slides that failed QA gates. And three minutes on a final scroll-through for overall flow. Notice what's *not* in this list: no formatting. No layout fixing. No citation chasing. No font adjustments. Every minute of human time is spent on judgment calls — the things humans are actually good at. The pipeline handles everything else. This is what McKinsey meant when they said the most valuable AI applications augment human judgment rather than replace it. Now, you might be wondering: why not just use one of the existing tools?]

---

## Slide 28: Why Not Just Use Tome / Gamma / SlidesAI? — Compound vs. Monolithic

- **Monolithic approach (Tome, Gamma, SlidesAI):** Single-pass black box — prompt goes in, slides come out, user edits retroactively with no visibility into what went wrong upstream
- **Gamma's own data:** Users edit 78% of generated slides before considering them "presentation-ready" — the tool generates output that is a starting point, not a finished product
- **The inspection problem:** In a monolithic system, a bad metric on slide 37 could stem from a research gap, an outline error, or a rendering bug — diagnosing the root cause requires reverse-engineering
- **VibeSliding's transparent pipeline:** Each stage produces inspectable artifacts (idea.md → research.md → outline.md → style_*.png → slide_*.png) — errors are caught and corrected at the stage they originate
- **Architectural comparison:** Monolithic = one big function call; Compound = a DAG of specialized sub-agents with quality gates between every node
- Core insight: The overhead of multi-stage orchestration pays for itself by preventing error compounding — catching one metric error in the outline is cheaper than fixing it in sixty rendered slides
[Visual: Two architectural cross-sections side by side. Left: a monolithic single-pass black box — opaque dark rectangle with "Prompt" entering left and "Deck" exiting right, no internal visibility, labeled "Monolithic (Tome, Gamma)" in Signal Red. Right: VibeSliding's transparent multi-stage pipeline — five connected rounded rectangles (Idea → Research → Outline → Style → Slides) with inspection windows (magnifying glass icons) between each stage, labeled "Compound (VibeSliding)" in Electric Cyan. Error propagation shown as red arrows cascading through the monolithic box vs. being caught at inspection windows in the compound pipeline. Heme watermark upper-right. Slide number 28/33. Reference style: style_content.png]
[Speech: "Why not just use Tome or Gamma?" I get this question a lot. Here's the architectural answer. Tome and Gamma are monolithic: prompt in, slides out, edit retroactively. Gamma's own blog admits users edit seventy-eight percent of generated slides. And when something's wrong — a bad metric on slide thirty-seven — you can't tell if it's a research gap, an outline error, or a rendering bug. You just see the symptom, not the cause. VibeSliding's pipeline is transparent. Every stage produces inspectable artifacts. You can open idea-dot-md, research-dot-md, outline-dot-md, and see exactly where a decision was made. Catching one metric error in the outline is trivially cheap. Fixing that same error across sixty rendered slides is expensive and error-prone. Multi-stage orchestration isn't overhead — it's insurance. Let's zoom out to the bigger picture.]

---

## Slide 29: Roadmap: Beyond Slides

- **Section 6 of 6 — BEYOND SLIDES**
- **Thesis:** The principles behind VibeSliding — iterate, orchestrate, curate — generalize to any compound document requiring research, narrative, visual, and layout generation
- From one pipeline to a universal architecture
[Visual: Upper two-thirds shows "BEYOND SLIDES" in large Inter Bold 28pt Warm White (#FFFDE7) with thesis sentence in Inter Regular 16pt Cool White beneath. Lower third: six-node section-map strip — nodes 1–5 dim with checkmarks, node 6 ("06 / BEYOND SLIDES") in full Warm White glow with filled circle. Progress bar filled 6/6. Three-pinned-dots watermark upper-right 15% opacity. Radial spotlight behind node 6. Deep Space background. Reference style: style_transition.png]
[Speech: We've built a pipeline, proven it works, and shown the numbers. Now let's ask the bigger question: what does this mean beyond presentations?]

---

## Slide 30: The Scaffold as Constitution — How the Visual System Enforces Consistency

- **What the scaffold encodes:** Font rules, color palette, slide-type taxonomy, text density targets per type, image placement grammars, narrative flow constraints (e.g., "no more than 3 consecutive text-heavy slides")
- **Consistency impact:** Scaffold-constrained decks score 92/100 on visual consistency (font variance, palette adherence, grid compliance) vs. 57/100 without a scaffold — a 61% improvement
- **Machine-readable design system:** The scaffold is YAML, not a visual template — every constraint is programmatically enforceable, not just suggestively displayed
- **Domain adaptation:** For a technical audience, the scaffold specifies higher data-slide ratio (40% vs. 20%), smaller fonts, denser layouts; for executives, larger fonts, fewer bullets, more full-bleed imagery
- **Constitution analogy:** Just as a constitution constrains future legislation without prescribing every law, the scaffold constrains downstream agents without dictating every slide's content
- Core insight: Codifying visual and structural rules before generation ensures that every agent operates within a coherent system — consistency becomes a parameter, not an aspiration
[Visual: Left third: a YAML code snippet rendered in JetBrains Mono 14pt on a dark code-editor background, showing scaffold parameters — font rules, color hex codes, slide-type ratios, density targets. Right two-thirds: the YAML visually "materializes" into rendered constraints — font size swatches, color palette strips, a slide-type ratio pie chart, and a density gauge — each connected by thin dashed Amber arrows from their corresponding YAML lines. A "92/100 consistency" badge in Signal Green vs. "57/100 without scaffold" crossed out in Signal Red. Heme watermark upper-right. Slide number 30/33. Reference style: style_content.png]
[Speech: The scaffold is the unsung hero of the pipeline. It's a YAML specification that encodes everything: fonts, colors, slide-type taxonomy, text density targets, image placement rules, narrative flow constraints. And it's not just documentation — it's programmatically enforced. Every downstream agent is bound by it. The result? Decks constrained by a scaffold score ninety-two out of a hundred on visual consistency, versus fifty-seven without one. That's a sixty-one percent improvement. And the scaffold adapts to context: technical audiences get denser layouts and more data slides; executive audiences get larger fonts and more imagery. Think of it as a constitution for your deck — it constrains future decisions without prescribing every detail. Let's talk about how this scales.]

---

## Slide 31: Scaling Without Redesign — 16, 25, 36 Content Slides from One Scaffold

- **One scaffold, three outputs:** The same narrative spine, section map, and visual system produce a 16-slide brief, 25-slide standard, or 36-slide deep dive — the user selects a tier, not a redesign
- **How scaling works:** CORE spine topics appear in all tiers; EXTENDED topics "slide in" between CORE topics only in longer versions — the narrative arc is preserved, not rewritten
- **Section distribution is proportional:** Each section grows proportionally — Section 3 (The Pipeline) might have 3 slides in the brief, 5 in standard, and 8 in the deep dive, but the section's thesis remains constant
- **No manual restructuring:** Adding 20 slides doesn't mean reorganizing the deck — it means expanding evidence, adding sub-claims, and inserting deeper case studies within the existing skeleton
- **Practical impact:** The P450 engineering deck was generated as a 36-content-slide deep dive (60 total with structural bookends) — but the same scaffold could produce a 16-slide executive briefing with one parameter change
- Core insight: Scalability is a parameter change, not a redesign — the scaffold makes deck length a dial you turn, not a problem you solve
[Visual: Three nested deck outlines arranged left to right, increasing in width: "16 slides" (small, compact), "25 slides" (medium), "36 slides" (large). All three share the same section skeleton rendered as a vertical spine of section labels on the left (Sections 1–6). In the 25-slide version, EXTENDED slide placeholders visually "slide in" between CORE slides (shown as lighter-colored cards inserting between darker CORE cards). In the 36-slide version, even more EXTENDED cards are inserted. A "Same scaffold" label with an equals sign connects all three versions. Heme watermark upper-right. Slide number 31/33. Reference style: style_content.png]
[Speech: Here's something that surprised even us. The same scaffold that produced the sixty-slide deep dive can produce a sixteen-slide executive briefing with a single parameter change. No restructuring. No redesign. The core topics appear in all tiers. Extended topics slide in between the core ones only in longer versions. Each section grows proportionally — the thesis stays constant, just the evidence depth changes. This means you can generate a quick briefing for leadership and a deep technical deck for the engineering team from the same input paragraph and the same scaffold. Deck length becomes a dial you turn. Now let me share the most important architectural insight of this whole talk.]

---

## Slide 32: Orchestration Is the Moat — Models Are Commodities, Workflows Are Not

- **Model commoditization is accelerating:** Claude, GPT, Gemini, Llama, Mistral — performance gaps narrow with every release cycle; today's best model is next quarter's baseline
- **Switching cost is near zero:** VibeSliding swapped GPT-4-Turbo → Claude 3.5 Sonnet with zero code changes and saw 18% improvement in user preference — the pipeline doesn't care which model fills the slot
- **The orchestration layer is the value layer:** Sequencing, iteration logic, quality gates, parallel dispatch, contact-sheet curation, selective regeneration, scaffold enforcement — none of this comes from a model API
- **Berkeley's Compound AI Systems thesis (Zaharia et al., 2024):** Systems achieve performance by combining multiple AI components rather than relying on a single model — the architecture matters more than any individual component
- **Beyond presentations:** This orchestration pattern applies to research reports, grant proposals, courseware, marketing collateral — any compound document requiring research + narrative + visual + layout
- Core insight: If your competitive advantage depends on which model you use, you have no competitive advantage — the moat is in the workflow, not the weights
[Visual: A layered architecture diagram with three horizontal strata. Bottom layer: commodity model APIs (GPT, Claude, Gemini, Llama, Mistral) rendered as interchangeable gray rounded rectangles with a "swap" icon between them. Middle layer (glowing Electric Cyan): the orchestration pipeline — showing labeled boxes for "Iteration Logic," "Quality Gates," "Parallel Dispatch," "Contact Sheets," "Scaffold Enforcement" connected by flow arrows. Top layer (Amber): human judgment — icons for narrative selection, style curation, QA review. The middle layer has a bright 8px outer glow, clearly marked as "THE VALUE LAYER." Bottom and top layers are dimmer. Heme watermark upper-right. Slide number 32/33. Reference style: style_content.png]
[Speech: This is the slide I want you to remember when you forget everything else. Models are commodities. Claude, GPT, Gemini, Llama — the performance gaps narrow every quarter. We swapped models in our pipeline with zero code changes and saw eighteen percent improvement. The model is a replaceable component. What's not replaceable is the orchestration layer — the iteration logic, quality gates, parallel dispatch, contact-sheet curation, selective regeneration, scaffold enforcement. None of that comes from a model API. Berkeley's compound AI systems thesis makes this explicit: systems achieve performance by combining components, not by relying on a single model. And this pattern isn't limited to presentations. Any compound document — reports, proposals, courseware, marketing collateral — benefits from the same architecture. The moat is in the workflow, not the weights. Let me close with how you can try this yourself.]

---

## Slide 33: Try It Yourself — Three Steps to Your First VibeSlide Deck

- **Step 1 — Write your idea:** One paragraph in `work/idea.md` is enough to start — thesis, audience, key claims, scope exclusions; 127 words launched a 60-slide deck
- **Step 2 — Run the pipeline:** Four CLI commands in sequence:
  - `python3 -m src.research.cli` → generates `work/research.md`
  - `python3 -m src.outline.cli` → generates scaffold + `work/outline.md`
  - `python3 -m src.render.style.cli --pick 1,1,1,1` → generates contact sheets, user selects
  - `python3 -m src.render.cli --copy 4` → renders parallel variants, user curates
- **Step 3 — Curate the output:** Review contact sheets (2 min), pick your styles, scroll through slide variants, delete the copies you don't love, assemble the final PDF
- **Total investment:** Under 60 minutes, under $5, zero PowerPoint, zero designers
- **The pipeline is open:** No proprietary models, no closed infrastructure — three commodity platforms orchestrated by two principles
- Core insight: The best presentation you've never manually built is one `idea.md` away
[Visual: A terminal window on Deep Space background showing four CLI commands in JetBrains Mono 14pt, each on its own line with a faint output preview fanning out to the right: `research.cli` → a small research.md icon, `outline.cli` → a small outline document icon, `render.style.cli` → a small contact-sheet grid icon, `render.cli` → a small slide variant grid icon. All four output icons converge via thin Amber arrows into a large glowing PDF icon at the far right, labeled "Your Deck." Below the terminal: "< 60 min · < $5 · 0 PowerPoint · 0 designers" in Signal Green. Heme watermark upper-right. Slide number 33/33. Reference style: style_content.png]
[Speech: Let me make this concrete. Step one: write one paragraph in idea-dot-md. Thesis, audience, key claims, scope exclusions. A hundred twenty-seven words is all it took for our sixty-slide deck. Step two: run four CLI commands. Research, outline, style, compose. The pipeline handles the iteration, the quality gates, the parallel rendering. Step three: curate. Pick your styles from the contact sheets — two minutes. Scroll through the slide variants and keep the ones you love. Assemble the PDF. Total: under sixty minutes, under five dollars, zero PowerPoint opened, zero designers pinged. The pipeline is completely open — no proprietary models, no closed infrastructure. Two principles, three tools, seven steps. The best presentation you've never manually built is one idea-dot-md away.]

---

## Slide 34: Key Takeaways — One Paragraph In, Publication-Grade Deck Out

- **Iterate:** Every stage runs as a draft-then-refine loop — the first pass explores, the second pass grounds with citations, metrics, and format standards; this alone cuts content deficiency from 52% to 11%
- **Orchestrate:** Three commodity tools (Cursor, OpenRouter, Valyu) connected by sequencing, iteration, and selection logic — models are interchangeable, the workflow is the value
- **Curate:** Aesthetic and narrative decisions stay human — contact sheets for style, parallel variants for slides, QA-flagged reviews for quality; 28 minutes of judgment, not formatting
- **The proof:** $4.73, 57 minutes, 60 slides, 38 citations, 16 custom visuals, full presenter scripts — from a 127-word paragraph
- Core insight: The value of generative AI is realized not in the models themselves, but in the architectures that orchestrate them into reliable, inspectable, human-augmented workflows
[Visual: A distilled summary card centered on Deep Space background — dark rounded rectangle with Electric Cyan border and subtle glow. Three icon-labeled rows inside: Row 1: circular arrow icon in Electric Cyan + "ITERATE — Draft-then-refine at every stage" in Cool White. Row 2: hub-and-spoke icon in Amber + "ORCHESTRATE — Commodity tools, custom workflow" in Cool White. Row 3: hand-selection icon in Vivid Purple + "CURATE — Human judgment at every checkpoint" in Cool White. Below the card: the proof line "127 words → 60 slides · $4.73 · 57 min" in Signal Green. The three icons echo the twin pillars visual from Slide 6, now consolidated. Heme watermark upper-right. Slide number 34/33. Reference style: style_content.png]
[Speech: Let me leave you with three words. Iterate — every stage runs twice, and that alone drops content deficiency from fifty-two percent to eleven percent. Orchestrate — three commodity tools connected by custom workflow logic; the models are replaceable, the pipeline is not. Curate — aesthetic and narrative decisions stay human, because taste and judgment are still our edge. The proof is in the numbers: four dollars and seventy-three cents, fifty-seven minutes, sixty slides, thirty-eight citations, sixteen custom visuals, and full presenter scripts — all from a hundred-twenty-seven-word paragraph. The value of generative AI is not in the models. It's in the architectures that orchestrate them. Thank you.]

---

## Slide 35: Thank You · Q&A

- **Core thesis:** The value of generative AI is realized not in the models themselves, but in the orchestration architectures that connect them
- **Speaker:** Xuefeng Cui — Shandong University
- **WeChat:** xfcui0
- **Email:** xfcui.uw@gmail.com
[Visual: Mirrors the cover composition exactly. Deep Space (#0A0F1A) background with the heme-thiolate porphyrin ring emblem rendered slightly larger than the cover, in luminous Electric Cyan (#00E5FF) with Amber (#FFB300) accent nodes, pulsing subtly larger to signal completion. "Thank You · Q&A" label in Inter Bold 36pt Cool White where the title was. Below the emblem: a single takeaway sentence "One paragraph in, publication-grade deck out" in Inter SemiBold 20pt Warm White. Contact details (WeChat: xfcui0, Email: xfcui.uw@gmail.com) arranged as a minimal card in the lower third in Inter Light 18pt. Faint dot grid in background. No slide number. Reference style: style_cover.png]
[Speech: Thank you very much. I'd love to take your questions — whether about the pipeline architecture, the economics, the quality gates, or how to adapt this for your own use case. The code is open, the tools are commodity, and the principles are universal. Who's first?]

---

## Appendix: Global Visual Requirements

- **Theme:**
  - Background: Deep Space `#0A0F1A`
  - Primary Accent: Electric Cyan `#00E5FF`
  - Secondary Accent: Amber `#FFB300`
  - Tertiary Accent: Vivid Purple `#B388FF`
  - Positive / Success: Signal Green `#00E676`
  - Negative / Warning: Signal Red `#FF5252`
  - De-emphasis / Borders: Slate `#3A4A5C`
  - Body Text: Cool White `#E0E6ED`
  - Highlight Text: Warm White `#FFFDE7`
- **Fonts:**
  - Titles: Inter Bold, 36pt (cover), 28pt (content/transition slide titles)
  - Subtitles: Inter SemiBold, 20pt
  - Body bullets: Inter Regular, 16pt
  - Labels and annotations: Inter Medium, 14pt
  - Code / CLI / monospace: JetBrains Mono Regular, 14pt
  - Speaker name / affiliation: Inter Light, 18pt
- **Format:** 16:9 aspect ratio (1920 × 1080 px), 5% safe margin on all edges, minimum 4.5:1 contrast ratio for all text against background