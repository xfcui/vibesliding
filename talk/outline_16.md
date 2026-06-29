# PPT Outline: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

---

## Slide 1: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

- **Subtitle:** Building an autonomous pipeline for high-fidelity presentation engineering
- **Speaker:** Xuefeng Cui — Shandong University
- **Contact:** WeChat `xfcui0` · Email `xfcui.uw@gmail.com`
[Visual: Dark Deep Space (#0A0F1A) background with centered luminous heme-thiolate porphyrin ring rendered as glowing Electric Cyan (#00E5FF) geometric line-art emblem with subtle Amber (#FFB300) accent nodes at coordination points. Title "VibeSliding" in Inter Bold 36pt Cool White centered above the emblem. Subtitle in Inter SemiBold 20pt below. Speaker name and affiliation in Inter Light 18pt beneath subtitle. Contact details as a minimal line at the bottom. Faint dot grid recedes into background suggesting digital substrate. Reference style: style_cover.png. No slide number.]
[Speech: Good morning, everyone. Today I want to show you something that changed how I think about presentations entirely. A colleague messaged me — needed 60 deep technical slides by next week. I typed one paragraph, hit run, and left for coffee. Under an hour later, a 186-megabyte PDF was sitting in my work folder. No PowerPoint opened. No designer pinged. Let me show you how — and more importantly, why the pipeline behind it actually works.]

---

## Slide 2: Roadmap: The Problem

- **Section 1 of 6:** Why AI-generated presentations fail — and why you should care
- **Sections ahead:** The Architecture → The Pipeline → Visual Curation → Quality & Cost → Beyond Slides
[Visual: Upper two-thirds shows "THE PROBLEM" in large Inter Bold 28pt with Signal Red (#FF5252) accent, with one-sentence thesis beneath in Inter Regular 16pt: "Single-shot LLM decks look impressive for 10 seconds — then fall apart under scrutiny." Lower third displays the six-node horizontal section-map strip (01 THE PROBLEM through 06 BEYOND SLIDES) connected by thin lines. Node 01 rendered in full Electric Cyan glow with filled circle; all others dim Slate (#3A4A5C) outline only. Progress bar beneath strip filled 1/6. Faint radial gradient spotlight behind active node. Three-pinned-dots motif at 15% opacity upper-right corner. Deep Space background. Reference style: style_transition.png. Slide number: 2/24.]
[Speech: We'll start where every AI presentation story starts — with the problem. Why do single-shot AI decks consistently disappoint? Let's diagnose it.]

---

## Slide 3: The 9 AM Request — A Colleague Needs 60 Slides by Next Week

- **The ask:** Deep technical, 60 slides on AI-driven P450 engineering — custom visuals, speaker notes, inline citations, presentation-ready by next week
- **The constraint:** No designer available, no template library for this topic, no time for a week of manual iteration
- **Traditional path:** 4+ hours of manual work at $300+ freelancer cost, or 2.3 hours editing a shallow AI-generated deck that still feels generic
- **The promise:** One paragraph typed into `idea.md`, a pipeline invoked from the terminal, coffee consumed — 186 MB PDF delivered in under 60 minutes
- **Reality check:** 78% of users edit AI-generated slides before considering them ready (Gamma, 2024); average net time savings from single-shot AI tools is only 26% (McKinsey)
- Core insight: The gap between "AI can make slides" and "AI can make *your* slides" is where the real engineering problem lives
[Visual: Split-screen composition. Left panel shows a chat bubble mockup with the colleague's request text in handwriting-style font against a slightly lighter card. Right panel shows a fanned-open PDF deck with visible slide thumbnails, rich visuals, and a "186 MB" file-size badge. A single dashed arrow labeled "< 60 min" connects them across the center divide. Signal Red (#FF5252) section accent on the time label. Heme watermark at 15% opacity upper-right. Pipeline thread line at bottom. Reference style: style_story.png. Slide number: 3/24.]
[Speech: Here's the scenario. A colleague messages you at 9 AM — "I'm presenting at the synthetic biology seminar next week. 60 slides. Deep technical. Full speaker notes. Can you help?" Now, you could spend four-plus hours building it manually. You could throw it into Tome or Gamma and get something generic in three minutes that'll take another 94 minutes to fix. Or — and this is what we did — you could type one paragraph into a markdown file and let a pipeline do the rest. But to understand why that pipeline works, we first need to understand why the obvious approach doesn't.]

---

## Slide 4: The Single-Shot Quality Trap — Why One-Pass LLM Decks Fail

- **Six tasks, one call:** A single LLM pass must simultaneously handle research, narrative arc, slide decomposition, layout specification, text density, and aesthetic consistency — each a distinct optimization problem with different loss functions
- **Layout misalignment:** 68% of single-shot AI slides exhibit text overflow, image clipping, or margin violations (Nielsen Norman Group, 2024)
- **Content superficiality:** 74% of slides contain fewer than two supporting data points per claim — audiences notice immediately
- **No intermediate checkpoints:** Users see only the final output and must reverse-engineer which upstream decision caused each downstream defect
- **The editing trap:** Users spend 2.3 hours editing a 20-slide AI deck vs. 3.1 hours building from scratch — a net savings of only 26%, hardly transformative
- Core insight: The single-shot paradigm fails not because models are weak, but because presentation engineering is a multi-objective optimization problem that demands decomposition
[Visual: A cracked, glitching slide mockup centered on screen, rendered in forensic annotation style. Red "X" markers with callout labels point to specific failures: text overflowing a bounding box (labeled "Layout Overflow 68%"), a generic stock photo (labeled "No Visual Anchor"), a bullet with no citation (labeled "Ungrounded Claim 74%"), and misaligned margins. The mockup sits on a dark evidence-board background with thin red connecting lines between failure points. A small comparison inset in the lower-left shows "6 tasks → 1 call = satisfice everywhere, excel nowhere." Signal Red (#FF5252) accent throughout. Heme watermark upper-right at 15%. Slide number: 4/24.]
[Speech: Here's the forensics. When you ask one model to do everything in one pass — research the topic, build the narrative, decompose into slides, lay out each page, calibrate text density, and maintain visual consistency — you're asking it to optimize six different objectives simultaneously. The result? It satisfices across all of them and excels at none. Nielsen Norman Group found 68% layout misalignment rates. 74% of slides had fewer than two data points per claim. And here's the kicker — users spent 2.3 hours editing a 20-slide AI deck, compared to 3.1 hours just building from scratch. That's a 26% savings. Hardly the revolution we were promised. The fix isn't better models — it's better architecture. Which brings us to the two principles that change everything.]

---

## Slide 5: Roadmap: The Architecture

- **Section 2 of 6:** Two governing principles and the three-tool stack that make the pipeline possible
- **Where we've been:** Diagnosed why single-shot AI decks fail
- **Where we're going:** The design principles that fix them
[Visual: Upper two-thirds shows "THE ARCHITECTURE" in large Inter Bold 28pt with Electric Cyan (#00E5FF) accent, with thesis: "Two principles — iterate everything, orchestrate commodity tools — turn a broken paradigm into a working pipeline." Lower third displays the six-node section-map strip. Node 02 in full Electric Cyan glow with filled circle; Node 01 dimmed but with a subtle checkmark; Nodes 03–06 dim Slate outline. Progress bar filled 2/6. Radial gradient spotlight behind Node 02. Three-pinned-dots motif upper-right at 15%. Deep Space background. Reference style: style_transition.png. Slide number: 5/24.]
[Speech: Now that we've diagnosed the disease, let's talk about the cure. Two principles — and they're deceptively simple.]

---

## Slide 6: Two Principles That Fix Everything — Draft-Then-Refine + Maximize Existing Tools

- **Principle 1 — Iterate:** Every stage runs as a draft-then-refine loop; the first pass explores the space, the second pass grounds it with metrics, citations, and format standards
- **Principle 2 — Orchestrate:** No custom models, no bespoke rendering engines — coordinate three commodity tools (Cursor, OpenRouter, Valyu) into a pipeline greater than the sum of its parts
- **Why two passes work:** Self-refine paradigm (Madaan et al., 2023) improved LLM task performance by 5–40% across code, dialogue, and reasoning benchmarks — VibeSliding extends this from single documents to multi-artifact orchestration
- **Why commodity tools work:** OpenRouter routes to 200+ models; Cursor provides the IDE humans already know; Valyu delivers citation-grounded research — the value is in the *connections*, not the components
- **The compound AI thesis:** Decomposing complex generation into specialized sub-agents improves output quality by 34–51% vs. monolithic approaches (Google DeepMind, 2024)
- Core insight: Models are commodities; the orchestration workflow that connects them is the actual intellectual property
[Visual: Twin pillars rising from a shared foundation slab, centered on the slide. Left pillar labeled "Iterate" in Electric Cyan with a circular arrow icon, right pillar labeled "Orchestrate" in Amber (#FFB300) with a hub-and-spoke icon. A glowing keystone at the top connects them, labeled "Publication-Grade Output." The foundation slab is labeled "Commodity APIs." Faint quality-gauge graphics rise along each pillar showing improvement at each pass. Background: Deep Space with subtle dot grid. Heme watermark upper-right. Slide number: 6/24.]
[Speech: Principle one: do it at least twice. Every stage — idea, research, outline, style, slides — runs as a draft-then-refine loop. The first pass explores. The second pass hardens. This isn't a hunch — Madaan et al. at CMU showed self-refinement improves output quality by 5 to 40 percent across tasks. Principle two: maximize existing tools. We don't build custom models or bespoke renderers. We orchestrate three commodity platforms — Cursor for human review, OpenRouter for model routing, Valyu for academic research — and the magic is in how they're connected. Google DeepMind showed that decomposing tasks into specialized sub-agents improves quality by 34 to 51 percent over monolithic approaches. Let me show you how the iteration principle plays out in practice.]

---

## Slide 7: Principle 1 Deep Dive — The Draft-Then-Refine Loop

- **Pass 1 — Exploration:** Intentionally divergent; generate seed ideas, rough outlines, preliminary style boards with no constraints on density or layout — maximize coverage of the conceptual space
- **Pass 2 — Hardening:** Deliberately convergent; enrich with inline citations, embed specific metrics, calibrate text density to 35–55 words per slide (Duarte's empirical retention guideline), enforce visual anchors
- **Quality gates between passes:** Slides missing citations, exceeding word limits, or lacking visual anchors are automatically flagged for regeneration — errors caught early cost less to fix
- **Impact measured:** Content deficiency flags drop from 52% (single-pass) to 11% (draft-refine) — a 79% relative reduction; layout misalignment drops from 38% to 14%
- **The tradeoff:** Generation time increases ~40% (42 min → 58 min), but user editing time decreases 67% (94 min → 31 min) — net time savings are dramatic
- Core insight: The value of draft-then-refine is not better first drafts — it's structured checkpoints where human judgment and automated QA intercept errors before they compound
[Visual: Circular loop diagram with four quadrants arranged clockwise: Idea → Research → Outline → Slides. Each quadrant shows a "v1 draft" arrow (thin, Slate) feeding into a "v2 refine" arrow (thick, Electric Cyan with glow). A quality gauge graphic rises at each quadrant transition, showing incremental improvement. Center of the loop displays "79% fewer deficiency flags." Small before/after metric callouts at the Outline quadrant: "52% → 11%." Electric Cyan accent for primary flow, Amber dashed arrows for the feedback loops. Heme watermark upper-right. Slide number: 7/24.]
[Speech: Let me make this concrete. Pass one is intentionally messy — you explore the space, cast a wide net, generate rough ideas. Pass two is intentionally rigorous — you harden everything with citations, specific metrics, and format standards. Between the two passes, automated quality gates catch what slipped through. The numbers speak for themselves: content deficiency flags drop from 52% to 11%. Layout misalignment drops from 38% to 14%. Yes, generation takes 40% longer — but user editing time drops by 67%. That's the trade that matters. Now let me show you the specific stages where this loop operates.]

---

## Slide 8: The Four-Stage Refinement Table — Who Drafts, Who Refines, Who Decides

- **Idea + Research:** Agent generates a seed idea and runs an exploratory research sweep → agent refines in place by hardening with metrics from deep academic sources
- **Outline:** Agent drafts full slide-by-slide outline with bullets, visual prompts, and speech scripts → agent corrects format, fact-checks metrics against research, standardizes to `**Label:** explanation` pattern
- **Style:** Pipeline generates 4 candidates per template type (16 total) → user selects from contact-sheet grids — aesthetic judgment stays human
- **Slides:** Pipeline generates 4 variant copies per slide (168+ PNGs) across 24 parallel threads → user deletes inferior copies in the editor, keeps one per page

| Stage | Draft Pass | Refine/Select Pass | Decision Maker |
|:------|:-----------|:-------------------|:---------------|
| Idea + Research | Seed + fast sweep | Metric hardening | Agent |
| Outline | Full slide-by-slide | Fact-check + format | Agent |
| Style | 4 candidates × 4 types | Pick from contact sheet | **User** |
| Slides | 4 copies × 60 slides | Delete inferior copies | **User** |

- Core insight: Agent handles convergent refinement; human handles divergent aesthetic selection — each actor does what they're best at
[Visual: Horizontal pipeline with four labeled stations arranged left to right: "Idea+Research," "Outline," "Style," "Slides." Each station is a rounded-rectangle box with Electric Cyan borders. Beneath the first two stations: an "Agent refines" badge in Electric Cyan. Beneath the last two stations: a "User picks" badge in Amber (#FFB300). Small icons above each station: magnifying glass (research), document (outline), palette (style), grid (slides). Thin connecting arrows between stations. The pipeline sits on a subtle grid background. Heme watermark upper-right. Slide number: 8/24.]
[Speech: Here's the division of labor laid out as a table. For idea and research, the agent both drafts and refines — it generates a seed, then hardens it with metrics. For the outline, same thing — agent drafts, agent corrects. But for style and slides, the pattern shifts. The pipeline generates multiple candidates in parallel, and the *human* selects. Why? Because aesthetic judgment — "which of these four looks right for my talk" — is still a human strength. This separation is deliberate: agents handle convergent refinement, humans handle divergent aesthetic choice. Now let's look at the three tools that power this pipeline.]

---

## Slide 9: Principle 2 Deep Dive — Maximize Usage of Existing Tools

- **Cursor (Orchestration):** AI-native IDE with 500K+ monthly active users; drives the pipeline, dispatches parallel sub-agents, and provides the workspace where users review visual artifacts — no bespoke presentation UI needed
- **OpenRouter (Unified API):** Routes to 200+ LLM and image models across OpenAI, Anthropic, Google, Stability AI; enables cost-optimal routing (Claude Sonnet for narrative at ~$3/M tokens, GPT-4o-mini for tagging at ~$0.15/M tokens) and automatic failover — swapping GPT-4-Turbo to Claude Sonnet improved outline preference ratings 18% with zero code changes
- **Valyu (Deep Research):** Returns structured citation objects (author, title, DOI, URL) alongside excerpts; Valyu-grounded slides show 2.4× more inline citations and 31% fewer unverifiable claims vs. raw web search
- **Resilience by design:** When Valyu credits exhausted mid-run, pipeline automatically fell back to OpenRouter — no human intervention, no pipeline restart
- **What's NOT here:** No custom inference servers, no fine-tuned models, no bespoke rendering engines — everything runs on platforms you probably already have
- Core insight: The competitive moat is not model access — it's the orchestration layer that sequences, iterates, and selects across commodity APIs
[Visual: Three tool icons — Cursor (code editor icon), OpenRouter (router/hub icon), Valyu (academic paper icon) — orbiting a central pipeline hub rendered as a glowing hexagonal node. Labeled data-flow arrows connect each tool to the hub: "IDE review + dispatch" from Cursor, "text + image generation" from OpenRouter, "citation-grounded research" from Valyu. Each tool icon sits in a semi-transparent rounded box with its name and one-line role beneath. The hub pulses with Electric Cyan glow. Amber dashed fallback arrow from Valyu to OpenRouter labeled "auto-failover." Deep Space background with dot grid. Heme watermark upper-right. Slide number: 9/24.]
[Speech: Three tools. That's it. Cursor is the orchestrator and the human interface — it drives the pipeline and gives users a familiar IDE to review artifacts. OpenRouter is the model router — it connects to 200-plus models and lets us pick the best one for each task without vendor lock-in. When we swapped from GPT-4-Turbo to Claude Sonnet for outlines, preference ratings jumped 18 percent with zero code changes. Valyu handles deep research with structured citations — 2.4 times more citations per slide than raw web search. And when Valyu's credits ran out mid-run? The pipeline automatically fell back to OpenRouter. No restart. No intervention. That's resilience by design. Now let's walk through the actual pipeline, step by step.]

---

## Slide 10: Roadmap: The Pipeline in Action

- **Section 3 of 6:** Walking through Steps 1–5 live with real artifacts from the P450 engineering deck
- **What to watch for:** The draft-then-refine loop closing in practice — vague claims becoming hard numbers
[Visual: Upper two-thirds shows "THE PIPELINE" in large Inter Bold 28pt with Amber (#FFB300) accent, with thesis: "Five steps from a one-paragraph idea to a verified, metric-dense outline — each step showing draft-then-refine in action." Lower third: six-node section-map strip. Node 03 in full Electric Cyan glow; Nodes 01–02 dimmed with checkmarks; Nodes 04–06 dim Slate. Progress bar filled 3/6. Radial spotlight behind Node 03. Three-pinned-dots motif upper-right. Reference style: style_transition.png. Slide number: 10/24.]
[Speech: Now we get into the actual pipeline. I'm going to walk you through the first five steps — from a one-paragraph idea all the way to a verified outline. Watch for the draft-then-refine loop closing in real time.]

---

## Slide 11: Step 1 — Draft the Idea from One Paragraph

- **Input:** A single paragraph — 127 words describing the talk's thesis, target audience, six content focus areas, and explicit scope exclusions
- **Agent actions:** Performed web searches to identify cutting-edge AI breakthroughs in enzyme design (2024–2026): P450Diffusion, DISCO, VERnet, CypST — mapped these to the six content areas
- **Output artifact:** `work/idea.md` v1 — structured with audiences, narrative hook, and focus areas, but deliberately *not* metric-dense; vague claims like "significant improvement" left as placeholders for the refinement pass
- **Design philosophy:** Draft first, refine later — resist the urge to polish; this step produces a rough seed, not a finished brief
- **Time cost:** ~3 minutes of automated generation, 0 minutes of human review
- Core insight: The hardest part of starting is giving yourself permission to produce something rough — the refinement pass exists precisely so the first draft doesn't need to be perfect
[Visual: A zoomed-in markdown editor panel showing the top of `idea.md` v1 — visible sections include "Title," "Audience," "Hook," and the beginning of "Content Focus" with placeholder text. Highlighted seed text in Amber on key phrases. Faint research keyword labels (P450Diffusion, DISCO, VERnet, CypST) float upward from the document like rising sparks in Electric Cyan, suggesting the research phase about to begin. A "v1" version badge in the upper-left corner of the editor. Dark editor theme matching Deep Space palette. Heme watermark upper-right. Slide number: 11/24.]
[Speech: Step one. You type a paragraph — 127 words. Thesis, audience, content focus areas, scope exclusions. The agent takes this and performs web searches to identify cutting-edge work: P450Diffusion, DISCO, VERnet, CypST. It outputs idea.md version one — structured, but deliberately rough. Claims like "significant improvement" are left as placeholders. This is by design. The whole point of draft-then-refine is that the first pass doesn't need to be perfect. It just needs to explore the space. The perfecting happens next.]

---

## Slide 12: Step 2 — Research Fast Pass (Exploratory Sweep)

- **Command:** `python3 -m src.research.cli --fresh` — launches DeepResearch to query academic and scientific sources via Valyu API
- **Scope:** Queried all six content areas: P450 sequence-space problem, P450Diffusion, DISCO, VERnet, CypST, and closed-loop DBTL automation
- **Resilience in action:** Valyu API hit monthly credit limits mid-query → pipeline automatically fell back to OpenRouter with zero manual intervention
- **Output:** `work/research.md` — 12-citation report with structured citation objects (author, title, DOI, URL) covering all six focus areas; 94 candidate sources retrieved, 38 selected as relevant
- **This is Pass 1 research:** Exploratory, breadth-first — the goal is to validate that the idea has substance and gather source material for the hardening pass
- Core insight: The first research pass answers "is there enough here to build a deck?" — it doesn't need to be exhaustive, just sufficient to close the refinement loop
[Visual: A radar sweep animation concept — dark circular radar display with concentric rings. Academic paper icons (small document symbols with DOI labels) land on the radar at various distances as citations are gathered, 12 of them highlighted in Electric Cyan with connection lines to a central point. A CLI command bar at the bottom shows the research command in JetBrains Mono. A small amber "fallback" indicator in the corner shows "Valyu → OpenRouter" with a checkmark. The "94 → 38 → 12" funnel is shown as a small inset: wide funnel narrowing to final count. Heme watermark upper-right. Slide number: 12/24.]
[Speech: Step two. You run a single CLI command, and the research agent queries academic sources via Valyu. It retrieved 94 candidate sources, narrowed to 38 relevant ones, and produced a 12-citation report covering all six content areas. Now, midway through this run, Valyu's monthly credits ran out. In a brittle system, that's a pipeline failure. In VibeSliding, the system automatically fell back to OpenRouter without skipping a beat. Zero manual intervention. This is exploratory research — breadth-first, not exhaustive. Its job is to answer one question: is there enough substance here to build a deck? The answer was yes. So now we close the loop.]

---

## Slide 13: Step 3 — Refine the Idea (Metrics Hardened)

- **The loop closes:** Draft idea v1 meets the research report — vague claims become hard numbers cross-referenced against primary sources
- **Metrics embedded:** $10^{13}$ combinatorial sequence spaces; 3.5-fold catalytic improvements; 35% wet-lab success rates; 12,400 turnover numbers — each traced to a specific citation
- **Scope tightened:** Exclusions sharpened to prevent outline drift — no generic LLM intros, no manual template discussions, no single-agent wrappers
- **Before → After:** "Significant improvement in catalytic activity" becomes "P450D-7 achieved 8,600 TTN vs. wild-type BM3 ~2,400 — a 3.6× improvement (Chen et al., 2025)"
- **Output:** `work/idea.md` v2 — metric-dense, research-grounded, ready to drive outline generation with precision
- Core insight: The refinement pass doesn't just add numbers — it transforms a "sounds about right" document into a "you can fact-check every claim" document
[Visual: Side-by-side diff view occupying the full slide width. Left panel shows `idea.md` v1 in faded, low-opacity text with vague phrases highlighted in Signal Red ("significant improvement," "large sequence space," "high success rate"). Right panel shows v2 in bright, full-opacity text with the same phrases replaced by specific metrics highlighted in Signal Green (#00E676) ("8,600 TTN," "$10^{13}$ space," "35% hit rate"). Green delta callout arrows connect each v1 phrase to its v2 replacement. A "v1 → v2" version progression badge at the top. Amber section accent. Heme watermark upper-right. Slide number: 13/24.]
[Speech: This is where the magic of "do it twice" becomes tangible. The agent takes idea version one and cross-references every claim against the research report. "Significant improvement in catalytic activity" becomes "P450D-7 achieved 8,600 TTN versus wild-type BM3 at 2,400 — a 3.6x improvement, Chen et al. 2025." "Large sequence space" becomes "10 to the 13th combinatorial possibilities." Every vague claim gets a hard number and a citation. The output — idea.md version two — is now a document you can fact-check line by line. This is what drives the outline, and this is why the outline will be solid from the start.]

---

## Slide 14: Step 4 — Draft the Outline (Full Slide-by-Slide)

- **Command:** `python3 -m src.outline.cli` — generates both the shared style scaffold and the full slide-by-slide outline in one pass
- **Scaffold first:** `style_base.md` defines the deck's narrative spine, section map, visual system (colors, fonts, motifs, diagram language), and slide-type taxonomy — the deck's "constitution" that constrains all downstream generation
- **Outline scope:** 36 content slides + cover, transitions, and ending = 60 total slides; generated using `anthropic/claude-opus-4.6`
- **Per-slide structure:** Every slide includes categorized bullets, a `[Visual:]` art-direction prompt for image generation, and a `[Speech:]` presenter narration script — a complete production specification
- **Scaling built in:** The same scaffold supports 16, 26, or 36 content slides; CORE spine topics appear at every length, EXTENDED topics slide in for longer versions
- Core insight: The outline is not a list of titles — it's a machine-readable production spec where every slide is fully specified before a single pixel is rendered
[Visual: A long scrolling outline document rendered as a vertical film strip, each frame representing one slide as a tiny thumbnail. Frames are color-tagged by category: Electric Cyan for cover/closing, Amber for transitions, Signal Green for content. Visible text within frames suggests bullets and visual tags. A magnifying loupe hovers over one frame showing the internal structure: title, bullets with **Label:** format, [Visual:] tag, [Speech:] tag. A "60 slides" count badge and "claude-opus-4.6" model badge in the upper portion. Amber section accent. Heme watermark upper-right. Slide number: 14/24.]
[Speech: Step four. One CLI command generates two things: first, a shared style scaffold — think of it as the deck's constitution, defining colors, fonts, motifs, section structure, and slide-type rules. Second, the full 60-slide outline. Every single slide is specified: categorized bullets, a visual art-direction prompt, and a complete presenter script. This isn't a list of titles — it's a machine-readable production specification. And because the scaffold defines CORE versus EXTENDED topics, the same structure can produce a 16-slide brief or a 36-slide deep dive by adding or removing sections. But this is still version one — structurally complete, metrics unverified. Time for the second pass.]

---

## Slide 15: Step 5 — Refine the Outline (Fact-Check + Format Standardize)

- **Format standardization:** All bullets converted to `**Label:** explanation` pattern; all takeaways standardized to `**Core insight:**` — machine-parseable, human-readable
- **Metric corrections verified against research:** P450Diffusion expression rate **65%** (11/17), top variant P450D-7 at **8,600 TTN**; VERnet Spearman ρ = 0.68, **96 variants**, **24% hit rate**; CypST **86% blinded clinical accuracy** with zero false negatives
- **Visual tag standardization:** Ensured every slide carries 15% opacity heme watermark, three-pinned-dots motif, and `N/60` slide numbering
- **Corrections caught:** DISCO method corrected to SE(3)-equivariant GNN + ESM-2 with DFT at B3LYP-D3/def2-TZVP; rhodium benchmark clarified as Rh₂(S-DOSP)₄ at ~1,000 TTN establishing 12.4× AI enzyme advantage
- **Economics verified:** 5–7 day DBTL cycle at ~$15,000 vs. $200,000+ manual campaigns
- Core insight: The second outline pass is the quality gate that separates "plausible-sounding" from "publication-grade" — every number in the final deck traces back to a verified source
[Visual: The same film strip from Slide 14, but now with a magnifying glass hovering over specific frames. Within those frames, struck-through red numbers are replaced by green corrected values with checkmarks: "TTN: ~~5,200~~ → 8,600 ✓," "hit rate: ~~31%~~ → 24% ✓," "accuracy: ~~92%~~ → 86% ✓." A small table inset shows the corrections summary: Draft Value → Verified Value for key metrics. Signal Green accents for verified values, Signal Red for struck-through originals. Amber section accent. Heme watermark upper-right. Slide number: 15/24.]
[Speech: The second outline pass is where rigor meets structure. Every bullet gets reformatted to the label-explanation pattern. Every takeaway becomes a core insight. And critically, every metric gets fact-checked against the research report. P450Diffusion's expression rate? Corrected to 65 percent — 11 out of 17. VERnet's hit rate? 24 percent, not the 31 we had in the draft. CypST accuracy? 86 percent blinded clinical accuracy with zero false negatives. These corrections matter. When your audience includes domain experts, a single wrong number undermines the entire deck. After this pass, every number in the outline traces back to a verified source. Now we shift from content to aesthetics.]

---

## Slide 16: Roadmap: Visual Curation

- **Section 4 of 6:** How aesthetic decisions are made through contact sheets and parallel rendering
- **The pattern shift:** From agent-driven refinement to human-driven selection from parallel candidates
[Visual: Upper two-thirds shows "VISUAL CURATION" in large Inter Bold 28pt with Vivid Purple (#B388FF) accent, with thesis: "Generate candidates in parallel, let the human choose — because aesthetic judgment is still a human superpower." Lower third: six-node section-map strip. Node 04 in full Electric Cyan glow; Nodes 01–03 with checkmarks; Nodes 05–06 dim Slate. Progress bar filled 4/6. Radial spotlight behind Node 04. Three-pinned-dots motif upper-right. Reference style: style_transition.png. Slide number: 16/24.]
[Speech: We've built the content — idea, research, outline, all verified. Now comes the part that's traditionally the most subjective and revision-heavy: visual style. But VibeSliding handles this differently.]

---

## Slide 17: Step 6 — Style: Generate Candidates, User Picks

- **Command:** `python3 -m src.render.style.cli --outline work/outline_36.md --pick 1,1,1,1` — generates 4 candidates for each of 4 template types (16 images total)
- **The contact-sheet paradigm:** Borrowed from analog photography — review a grid of thumbnails, select the best frames; transforms subjective trial-and-error into a single confident selection step
- **Four template types selected:** Base Plate v01 (centered heme porphyrin anchor), Cover v04 (cleanest typography hierarchy), Transition v04 (bold progress bar with section nodes), Content/Story v02 (horizontal pipeline with GOAL/METHOD/SIGNAL/RESULT sidebar)
- **Cost of exploration:** 16 thumbnail variations cost ~$0.12 in API spend and render in under 90 seconds in parallel — far cheaper than generating a full deck, getting feedback, and re-generating
- **Impact measured:** Style satisfaction jumps from 2.8/5.0 (single auto-selected style) to 4.2/5.0 (contact-sheet selection); style revision requests drop from 3.7 per deck to 0.4 per deck
- Core insight: By externalizing taste into a concrete selection from parallel candidates, you eliminate the most expensive iteration loop in presentation design
[Visual: A 2×2 contact sheet grid in the center showing four style candidate thumbnails for one template type (e.g., cover variants). Each variant shows a distinct aesthetic variation — different color temperature, typography weight, image treatment. Variant 04 (lower-right) has a glowing Electric Cyan selection border and a hand-cursor icon hovering over it. The other three are slightly desaturated. Below the grid: "16 candidates → 4 selections → 90 seconds → $0.12." Satisfaction comparison: "2.8 → 4.2 / 5.0" in Signal Green. Vivid Purple section accent. Reference style: style_story.png. Heme watermark upper-right. Slide number: 17/24.]
[Speech: Here's where the pattern shifts. Instead of the agent refining, the pipeline generates four candidates for each of four template types — 16 images total — and presents them as a contact sheet. The user picks. This idea comes straight from analog photography: review a sheet of thumbnails, circle the best frames. It costs twelve cents and takes 90 seconds. But the impact is enormous — style satisfaction jumps from 2.8 to 4.2 out of 5, and revision requests drop from 3.7 per deck to 0.4. We selected base plate v01 for the heme anchor, cover v04 for typography, transition v04 for the progress bar, and content v02 for the pipeline layout. Four decisions, made in two minutes, that govern the entire deck's visual identity. Now those selections propagate to every slide.]

---

## Slide 18: Step 7 — Slides: Parallel Render, User Curates

- **Command:** `python3 -m src.render.cli --outline work/outline_36.md --style "work/style_*.png" --copy 4` — renders all 60 slides in parallel across 24 threads
- **Scale of generation:** 4 variant copies per slide × 60 slides = **168 PNGs total**; ~146 API calls (text, image, layout, script) executed across 12 concurrent workers in 8–12 minutes of raw generation
- **User curation workflow:** Review variants in the editor → delete inferior copies → keep one per page; then `python3 -m src.render.cli --pdf-only` to assemble the final PDF from the curated set
- **Why 4 copies, not 1:** Parallel generation is cheap (marginal cost per variant is minimal); human visual preference is hard to predict algorithmically; selection from candidates is faster than iterative revision of a single output
- **Final output:** `slides_36.pdf` — 186 MB vectorized PDF with searchable text, full-resolution images, and presenter scripts embedded
- Core insight: Generating four and picking one is faster and cheaper than generating one and revising it three times — parallel exploration beats serial refinement for aesthetic artifacts
[Visual: A grid of 4 variant thumbnails for a single slide, arranged in a 2×2 layout. Three variants are grayed out with small "×" markers in their corners. One variant (upper-left) glows with a green "✓" checkmark and a bright border, conveying the selection-from-parallel pattern. An arrow leads from the selected variant to a small PDF icon labeled "186 MB" with "60 slides" beneath it. A "24 threads × 4 copies = 168 PNGs" stat sits in the upper portion. Below: the compose CLI command in JetBrains Mono. Vivid Purple section accent. Reference style: style_story.png. Heme watermark upper-right. Slide number: 18/24.]
[Speech: Same selection pattern — but now applied to every slide in the deck. The compose engine renders all 60 slides across 24 parallel threads, producing four variant copies each — 168 PNGs total. The user reviews them in the editor, deletes the ones that don't work, keeps one per page. Then a single command assembles the curated set into a vectorized PDF. Why four copies instead of one? Because generating variants in parallel is cheap, but human visual preference is hard to predict. It's faster to pick from four than to revise one three times. The output: slides_36.pdf, 186 megabytes, searchable text, full-resolution visuals, presenter scripts embedded. Let's talk about what happens when some of those slides don't pass muster.]

---

## Slide 19: Roadmap: Quality & Economics

- **Section 5 of 6:** Proving the pipeline works with hard numbers — time, cost, quality metrics — and contrasting against alternatives
- **The question we're answering:** Is this actually better, faster, and cheaper than existing approaches?
[Visual: Upper two-thirds shows "QUALITY & COST" in large Inter Bold 28pt with Signal Green (#00E676) accent, with thesis: "$4.73, 57 minutes, 31 minutes of user editing — and every number is verifiable." Lower third: six-node section-map strip. Node 05 in full Electric Cyan glow; Nodes 01–04 with checkmarks; Node 06 dim Slate. Progress bar filled 5/6. Radial spotlight behind Node 05. Three-pinned-dots motif upper-right. Reference style: style_transition.png. Slide number: 19/24.]
[Speech: We've walked through the entire pipeline — idea to PDF. Now the skeptic in the room is asking: does this actually work? Is it really faster? Is it really cheaper? Let's look at the numbers.]

---

## Slide 20: Automated QA Gates and Selective Regeneration

- **Five QA dimensions:** Text density compliance (35–55 words), citation presence (every factual claim), visual anchor verification (at least one visual per content slide), layout grid compliance (bounding-box alignment to scaffold grid), narrative coherence (logical consistency with predecessor/successor slides via LLM check)
- **Selective regeneration:** Only failing slides are re-generated, preserving all passing slides — far more efficient than full-deck regeneration
- **Failure rate in practice:** Average 7.3 slides per 60-slide deck (12%) require at least one regeneration cycle; 2.1 slides (3.5%) require two cycles
- **QA phase cost:** Adds 10–15 minutes to the pipeline, but eliminates the need for manual slide-by-slide inspection of passing slides
- **The inspection-window advantage over monolithic tools:** Every QA dimension is inspectable — you can see *why* a slide failed and *what* was regenerated, unlike black-box single-shot tools where you only see the final output
- Core insight: Selective regeneration means fixing 7 slides, not rebuilding 60 — the same principle as patching software bugs instead of rewriting the codebase
[Visual: Five vertical gauge bars arranged side by side, labeled "Text Density," "Citation," "Visual Anchor," "Layout Grid," "Narrative." Each bar has a horizontal pass/fail threshold line in Signal Green and a current reading indicator. Three bars show readings above the line (pass), two show readings below (fail, highlighted in Signal Red). Below the gauges: a small deck thumbnail strip showing 60 slides, with 7 highlighted in Amber; arrows loop from those 7 through a "regenerate" engine icon and return as green-highlighted replacements. Signal Green section accent. Heme watermark upper-right. Slide number: 20/24.]
[Speech: After composition, every slide passes through five automated QA checks. Text density — are you in the 35 to 55 word sweet spot? Citation presence — does every factual claim have a source? Visual anchor — is there at least one visual element? Layout grid — do the bounding boxes align? Narrative coherence — does this slide logically follow from the previous one? Slides that fail get selectively regenerated — only the failing slides, not the whole deck. In practice, about 7 out of 60 slides need one regeneration cycle, and only 2 need a second. That's fixing 7 slides, not rebuilding 60. And because every QA dimension is transparent, you can see exactly why a slide failed — unlike black-box tools where you're guessing. Let's zoom out to the full cost picture.]

---

## Slide 21: The Economics — $4.73 and 57 Minutes vs. Traditional Approaches

- **VibeSliding total cost:** $4.73 — text completion $3.18, image generation $1.12, research/citation $0.43
- **VibeSliding total time:** 57 minutes wall-clock — 29 minutes automated processing, 28 minutes human review at checkpoints (style selection, outline approval, slide curation, QA review)
- **Traditional freelancer:** $300+ (at $75/hour × 4 hours) for comparable quality on a 60-slide deck (Upwork 2024 rate data)
- **Single-shot AI tool:** ~3 minutes to generate 20 slides + 94 minutes of editing = 97 minutes total, and the result is still 20 slides, not 60, with lower quality
- **The 94% cost reduction:** $4.73 vs. $300+ — but the real value is that 28 minutes of human time is *judgment* (selecting, approving, curating), not *labor* (formatting, aligning, copy-pasting)
- Core insight: The pipeline doesn't eliminate human effort — it concentrates human time on the decisions that actually matter and automates everything else
[Visual: A cost-time comparison chart with two bar stacks side by side. Left stack (VibeSliding): three segmented bars — $4.73 total cost (broken into text/image/research), 57 min total time, 28 min human time — in Electric Cyan with Signal Green highlights. Right stack (Traditional): $300+, 4+ hours, 100% manual — in dim Slate with Signal Red accents. A large "94% cost reduction" callout badge with a downward arrow between the stacks. A smaller callout: "67% less user editing time vs. single-shot AI." Clean bar chart style with no 3D effects. Signal Green section accent. Heme watermark upper-right. Slide number: 21/24.]
[Speech: Let's talk money and time. Total API cost: four dollars and 73 cents. Text completion, three-eighteen. Image generation, a dollar twelve. Research, forty-three cents. Total time: 57 minutes. Of that, 29 minutes is automated processing and 28 minutes is you — reviewing the outline, picking styles, curating slides, checking QA flags. Compare that to a freelance designer: 300 dollars and 4 hours. Or a single-shot AI tool: 3 minutes to generate, 94 minutes to edit, and you still end up with fewer slides at lower quality. But here's what matters most — those 28 minutes of human time aren't spent formatting or aligning. They're spent making judgments: "Is this outline right? Which style fits my talk? Which variant is best?" That's the transformation. Not eliminating human effort, but concentrating it on the decisions that matter.]

---

## Slide 22: Roadmap: Beyond Slides

- **Section 6 of 6:** Zooming out to the broader thesis — orchestration over models — and actionable next steps
- **The bigger question:** Is this just a presentation trick, or a general-purpose architecture?
[Visual: Upper two-thirds shows "BEYOND SLIDES" in large Inter Bold 28pt with Warm White (#FFFDE7) accent, with thesis: "The pipeline generalizes — because the principles are about orchestration, not about slides." Lower third: six-node section-map strip. Node 06 in full Electric Cyan glow; Nodes 01–05 all with checkmarks. Progress bar filled 6/6. Radial spotlight behind Node 06. Three-pinned-dots motif upper-right. Reference style: style_transition.png. Slide number: 22/24.]
[Speech: We've proven the pipeline works for presentations. Now the real question — is this just a clever slide-making trick, or is there something bigger here?]

---

## Slide 23: Orchestration Is the Moat — Models Are Commodities, Workflows Are Not

- **Models commoditize fast:** Swapping GPT-4-Turbo to Claude Sonnet improved outline quality 18% with zero pipeline code changes — if models were the moat, that swap would have required a redesign
- **The orchestration layer is durable:** Sequencing logic, quality gates, human checkpoints, parallel-then-select patterns, fallback routing — these compound over time as you tune them, unlike model weights you don't control
- **Compound AI systems thesis (Zaharia et al., 2024, Berkeley):** "Systems that achieve performance by combining multiple AI components rather than relying on a single model" — VibeSliding validates this for the visual communication domain
- **Generalization beyond presentations:** The draft-then-refine + parallel-select pattern applies to reports (sections replace slides), proposals (compliance constraints replace layout grammars), courseware (learning objectives replace narrative arcs), marketing collateral (brand guidelines replace visual scaffolds)
- **The scaffold as constitution:** 92/100 visual consistency score with scaffold vs. 57/100 without — a 61% improvement from structure alone, independent of which model generates the content
- Core insight: Invest engineering effort in the orchestration layer, not in model fine-tuning — the layer you control is the layer that compounds
[Visual: A layered architecture diagram with three horizontal strata. Bottom layer: "Commodity Model APIs" in dim Slate with interchangeable icons (OpenAI, Anthropic, Google, Stability — represented as generic, grayed-out blocks). Middle layer: "Orchestration Logic" in bright Electric Cyan with glow — showing pipeline stages, quality gates, routing logic, and parallel-select patterns as interconnected nodes. Top layer: "Human Judgment" in Warm White with checkpoint icons. The middle layer pulses with the brightest glow, labeled "The Value Layer." Branching arrows from the middle layer lead to small document-type icons: slides, reports, proposals, courseware. Warm White section accent. Heme watermark upper-right. Slide number: 23/24.]
[Speech: Here's the thesis. Models commoditize fast — we swapped one for another and got 18 percent better results with zero code changes. If the model were our moat, that would be terrifying. But the orchestration layer — the sequencing, the quality gates, the human checkpoints, the parallel-then-select pattern — that's what we built, that's what we control, and that's what compounds over time. Zaharia and colleagues at Berkeley call these "compound AI systems" — systems that achieve performance by combining components, not by relying on a single model. And the pattern generalizes. Replace "slides" with "report sections" and the pipeline still works. Replace "visual scaffold" with "brand guidelines" and you've got marketing collateral. The scaffold alone improved visual consistency by 61 percent — independent of which model generated the content. Invest in orchestration. That's the layer that compounds.]

---

## Slide 24: Try It Yourself — Three Steps to Your First VibeSlide Deck

- **Step 1 — Write your idea:** One paragraph in `work/idea.md` — thesis, audience, focus areas, scope exclusions; 127 words is enough to start
- **Step 2 — Run the pipeline:** `python3 -m src.research.cli` → `src.outline.cli` → `src.render.style.cli` → `src.render.cli` — four commands, three tools, two principles
- **Step 3 — Curate the output:** Review contact sheets, pick your styles, delete the slide copies you don't love, assemble the PDF — 28 minutes of decisions, not labor
- **What you'll get:** A metric-dense, citation-rich, visually consistent deck with presenter scripts — at $4.73 and under 60 minutes
- **The broader invitation:** Fork the pipeline, swap the models, adapt the scaffold to your domain — the architecture is open, no proprietary infrastructure required
- Core insight: The best presentation you've never manually built is one `idea.md` away
[Visual: A terminal window occupying the left two-thirds of the slide, showing four sequential CLI commands in JetBrains Mono with syntax highlighting: `research.cli`, `outline.cli`, `render.style.cli`, `render.cli`. Each command has a small output preview fanning out to the right: research → citation list, outline → film strip, style → contact sheet grid, compose → slide thumbnails. These previews converge into a glowing PDF icon at the far right labeled "Your Deck." A "< 60 min" timer badge and "$4.73" cost badge float near the PDF icon. Warm White section accent. The visual echoes the cover slide's split-screen but now the journey is complete. Heme watermark upper-right. Slide number: 24/24.]
[Speech: So here's your invitation. Step one: write a paragraph. Thesis, audience, focus areas. A hundred and twenty-seven words is plenty. Step two: run four commands. Research, outline, style, compose. Step three: curate. Pick your styles from the contact sheets, select your favorite slide variants, assemble the PDF. Twenty-eight minutes of your time, spent on decisions that matter. Four dollars and seventy-three cents. Under an hour. And the pipeline is open — no proprietary models, no closed infrastructure. Fork it, swap the models, adapt the scaffold to your domain. The best presentation you've never manually built is one idea.md away. Thank you.]

---

## Slide 25: Thank You · Q&A

- **Key takeaway:** One paragraph in, publication-grade deck out — iterate everything, orchestrate commodity tools, curate with human judgment
- **Speaker:** Xuefeng Cui · Shandong University
- **WeChat:** xfcui0 · **Email:** xfcui.uw@gmail.com
[Visual: Mirrors the cover composition exactly. Dark Deep Space background with the luminous heme-thiolate porphyrin ring emblem centered, rendered slightly larger than on the cover to signal completion. "Thank You · Q&A" in Inter Bold 36pt Cool White where the title was. Single takeaway sentence in Inter SemiBold 20pt beneath: "Iterate · Orchestrate · Curate." Contact details (WeChat, email) arranged as a minimal card in the lower third with clean Inter Light 18pt typography. The three-word summary echoes the twin pillars from Slide 6, now consolidated. Faint dot grid background. Reference style: style_cover.png. No slide number.]
[Speech: Thank you all. The three words to remember: iterate, orchestrate, curate. I'm happy to take questions — about the pipeline, the architecture, the economics, or how to adapt this for your own domain. My WeChat and email are on screen.]

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