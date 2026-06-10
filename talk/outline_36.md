# PPT Outline: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

---

## Slide 1: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

- **Subtitle:** Building an autonomous pipeline for high-fidelity presentation engineering
- **Speaker:** Xuefeng Cui · Shandong University
- **Contact:** WeChat xfcui0 · xfcui.uw@gmail.com
[Visual: Dark Deep Space (#0A0F1A) background with a centered luminous heme-thiolate porphyrin ring rendered as glowing Electric Cyan (#00E5FF) geometric line-art emblem with subtle Amber (#FFB300) accent nodes at coordination points. Title "VibeSliding" in Inter Bold 36pt Cool White centered above the emblem. Subtitle in Inter SemiBold 20pt below. Speaker name and affiliation in Inter Light 18pt beneath subtitle. Contact details (WeChat, email) as a minimal single line at bottom. Faint dot grid recedes into background suggesting digital substrate. Reference: style_cover.png for typography hierarchy and spatial composition. No slide number.]
[Speech: Good morning, everyone. Today I want to share a narrative about a presentation — specifically, this presentation. What you're looking at right now was not built in PowerPoint. No designer touched it. No template was dragged. It started as a single paragraph of text and became a sixty-slide, publication-grade deck in under one hour. My name is Xuefeng Cui from Shandong University, and I'm going to show you exactly how that happened — and why the pipeline behind it matters far more than any individual AI model.]

---

## Slide 2: Roadmap: The Problem

- **Section 1 of 6:** Why AI-generated presentations still fail
- **Thesis:** The dominant single-shot paradigm produces slides that are generically structured, factually shallow, and visually broken
[Visual: Upper two-thirds shows "THE PROBLEM" in large Inter Bold 28pt Signal Red (#FF5252) text, with one-sentence thesis beneath in Inter Regular 16pt Cool White. Lower third contains the six-node horizontal section-map strip: nodes labeled 01/THE PROBLEM through 06/BEYOND SLIDES connected by thin lines. Node 01 rendered in full Electric Cyan glow with filled circle; all others dim (#3A4A5C outline only). Progress bar beneath strip filled 1/6. Faint radial gradient brightens behind active node. Three-pinned-dots watermark at 15% opacity upper-right corner. Reference: style_transition.png for progress bar and node layout. progress bar 1/6]
[Speech: Let's start with the problem. And it's a problem every one of you has probably experienced firsthand.]

---

## Slide 3: The 9 AM Request — A Colleague Needs 60 Slides by Next Week

- **The Scenario:** A colleague messages at 9 AM — "I'm presenting at the synthetic biology seminar next week, 60 slides on AI-driven P450 engineering, deep technical, full speaker notes"
- **The Constraint:** Publication-grade quality with custom visuals, fact-checked metrics, and presenter scripts for every slide
- **The Traditional Path:** 4+ hours of manual work across research, writing, design, and revision — or $300+ for a freelance designer at $75/hour
- **The Hidden Cost:** Even AI-assisted tools like Tome or Gamma require users to edit 78% of generated slides before they're presentation-ready
- **The Real Question:** Can we go from a one-paragraph idea to a finished 60-slide PDF without ever opening PowerPoint?
- Core insight: The gap isn't "can AI make slides" — it's "can AI make slides you'd actually present without rewriting them"
[Visual: Split-screen composition. Left half shows a chat bubble interface with the colleague's message in Cool White on a slightly lighter panel (#111827), timestamp "9:03 AM" in Slate. Right half shows a finished PDF deck fanning open — multiple slide thumbnails cascading diagonally with visible custom visuals and text. A single dashed Amber (#FFB300) arrow connects left to right, labeled "< 60 min" in Inter Medium 14pt. Bottom-left corner shows a crossed-out clock icon with "4+ hrs" in Signal Red. Pipeline thread line at bottom, heme watermark upper-right at 15% opacity. Slide number 1/60 in Slate bottom-right.]
[Speech: This actually happened. A colleague pinged me — sixty slides on AI-driven P450 enzyme engineering, deep technical, full speaker notes, custom visuals. The traditional approach? You're looking at four-plus hours minimum, or three hundred dollars for a freelance designer. And even if you use one of the existing AI slide tools — Tome, Gamma, SlidesAI — the data shows users still end up editing nearly eighty percent of the output. So here's the real question: can we close this gap entirely? Can a single paragraph become a deck you'd actually stand up and present? Let's look at why existing tools can't do this.]

---

## Slide 4: The Single-Shot Quality Trap — Why One-Pass LLM Decks Fail

- **The Trap Defined:** Single-shot tools collapse six distinct optimization problems — research, narrative design, slide decomposition, layout computation, text calibration, and aesthetic consistency — into one inference pass
- **Layout Misalignment:** 68% of AI-generated slides exhibit text overflow, image clipping, or margin violations (Nielsen Norman Group, 2024)
- **Content Superficiality:** 74% of single-pass slides contain fewer than two supporting data points per claim — audiences notice the emptiness
- **The Edit Tax:** Users spend an average of 2.3 hours editing a 20-slide AI deck vs. 3.1 hours building from scratch — a net savings of only 26% (McKinsey, 2024)
- **Microsoft's Own Admission:** Even Office Copilot's dedicated layout engine still requires manual repositioning on 41% of generated slides
- Core insight: The failure isn't model quality — it's architectural. Presentation engineering is a multi-objective optimization problem that demands decomposition, not a bigger prompt
[Visual: A single slide mockup rendered in forensic annotation style against Deep Space background. The mockup shows a clearly broken AI-generated slide: title text overflows its bounding box (highlighted with a red dashed outline and "OVERFLOW" label), a stock photo clips the right margin (red "CLIP" marker), bullet points contain vague placeholder text like "AI is transforming..." with red "NO DATA" flags, and a generic gradient background clashes with mismatched fonts (red "INCONSISTENT" callout). Five red "X" markers annotate each failure. Small stat callouts in Signal Red around the mockup: "68% layout errors," "74% shallow content," "41% need repositioning." Pipeline thread line at bottom. Heme watermark upper-right at 15% opacity. 2/60.]
[Speech: Here's why those tools fail. When you ask a single model to simultaneously research your topic, build a narrative, decompose it into slides, compute layouts, calibrate text density, AND maintain visual consistency — you're asking it to optimize six different objectives in one pass. It satisfices across all of them and excels at none. Nielsen Norman Group measured this: sixty-eight percent layout misalignment, seventy-four percent content superficiality. Microsoft's own Copilot team admits forty-one percent of their generated slides need manual repositioning. The net time savings? A measly twenty-six percent. The failure is architectural, not about model intelligence. And that's exactly what we're going to fix. Let me show you the two principles that change everything.]

---

## Slide 5: Roadmap: The Architecture

- **Section 2 of 6:** Two governing principles and the three-tool stack
- **Thesis:** Draft-then-refine loops plus commodity tool orchestration produce what single-shot systems cannot
[Visual: Upper two-thirds shows "THE ARCHITECTURE" in large Inter Bold 28pt Electric Cyan (#00E5FF) text, with thesis sentence beneath in Inter Regular 16pt Cool White. Lower third contains the six-node horizontal section-map strip. Node 02 rendered in full Electric Cyan glow with filled circle; node 01 is dimmed but retains a faint completed checkmark; nodes 03–06 dim (#3A4A5C outline only). Progress bar filled 2/6. Faint radial gradient behind active node. Three-pinned-dots watermark upper-right at 15% opacity. Reference: style_transition.png. progress bar 2/6]
[Speech: Now that we've diagnosed the problem, let's look at the architecture that solves it. Two principles and three tools — that's the entire foundation.]

---

## Slide 6: Two Principles That Fix Everything — Draft-Then-Refine + Maximize Existing Tools

- **Principle 1 — Iterate:** Every stage runs at least twice — the first pass explores the space, the second pass grounds it with metrics, citations, and standards
- **Principle 2 — Orchestrate:** No custom models, no bespoke engines — coordinate three commodity platforms (Cursor, OpenRouter, Valyu) into a pipeline greater than its parts
- **Why Two Passes Matter:** Self-refine paradigm reduces content deficiency flags from 52% to 11% — a 79% relative improvement (Madaan et al., 2023)
- **Why Commodity Tools Win:** Swapping GPT-4-Turbo for Claude 3.5 Sonnet improved outline quality by 18% with zero pipeline code changes — because the orchestration layer is model-agnostic
- **The Keystone Insight:** Human judgment is injected at every stage boundary — the system proposes, the human disposes
- Core insight: Models are commodities that improve on their own; the orchestration workflow that connects them is where the durable value lives
[Visual: Twin pillars rising from a shared foundation slab rendered as a glowing architectural diagram. Left pillar in Electric Cyan labeled "ITERATE" with icons for draft→refine loop at each level. Right pillar in Amber labeled "ORCHESTRATE" with three tool icons (Cursor, OpenRouter, Valyu) stacked vertically. A glowing keystone at the top connects both pillars, labeled "Human Judgment." The foundation slab is labeled "Compound AI Pipeline." Stat callouts flank each pillar: "79% fewer deficiencies" (left), "18% quality gain, zero code changes" (right). Reference: style_content.png for layout direction. Pipeline thread line at bottom. 3/60.]
[Speech: Two principles. That's all you need. First: iterate. Every stage of the pipeline runs at least twice. The first pass explores — brainstorms, researches, generates rough drafts. The second pass hardens — injects metrics, verifies citations, standardizes formatting. Research from Carnegie Mellon shows this self-refine pattern cuts content deficiencies by seventy-nine percent. Second: orchestrate commodity tools. We don't build custom models. We don't fine-tune anything. We wire together three platforms that already exist and let the workflow create the value. When we swapped one model for another, quality jumped eighteen percent without changing a single line of pipeline code. That's the proof that orchestration, not any individual model, is where the moat lives. Now let me take you deeper into each principle.]

---

## Slide 7: Principle 1 Deep Dive — The Draft-Then-Refine Loop

- **Inspired By:** Self-Refine paradigm (Madaan et al., 2023) — iterative self-feedback improves LLM output by 5–40% across code, dialogue, and reasoning tasks
- **Pass 1 — Exploration:** Intentionally divergent — maximize coverage of the conceptual space without enforcing constraints on density, format, or layout
- **Pass 2 — Hardening:** Deliberately convergent — enrich with inline citations, specific metrics, visual annotations, and text density calibration (targeting 35–55 words per slide per Duarte's research)
- **The Software Analogy:** Just as agile sprints replaced waterfall with inspectable increments, draft-then-refine replaces monolithic generation with staged checkpoints
- **Empirical Results:** Layout misalignment drops from 38% → 14%; total user editing time drops by 67% (from 94 min to 31 min post-generation)
- Core insight: The value isn't better first drafts — it's structured checkpoints where human judgment and automated QA intercept errors before they compound downstream
[Visual: Circular loop diagram with four quadrants arranged clockwise: IDEA (top-left), RESEARCH (top-right), OUTLINE (bottom-right), SLIDES (bottom-left). Each quadrant contains two concentric arcs: an inner "v1 DRAFT" arc in dim Slate and an outer "v2 REFINE" arc in bright Electric Cyan. Small arrows show flow from inner to outer arc within each quadrant. A central quality gauge (semicircular meter) rises from yellow to green as the loop progresses. Between quadrants, small checkpoint icons (magnifying glass, checkmark) indicate human review gates. Stat callouts: "38%→14% layout errors" and "94→31 min editing." Pipeline thread line at bottom. 4/60.]
[Speech: Let's unpack Principle 1. The draft-then-refine loop comes from research by Madaan and colleagues showing that when you let an LLM critique and revise its own output, quality jumps by up to forty percent. We apply this at every stage. Pass one is deliberately messy — explore widely, generate rough ideas, don't worry about formatting. Pass two is surgical — inject hard numbers, verify every citation, calibrate text density to Duarte's guideline of thirty-five to fifty-five words per slide. Think of it like agile versus waterfall. Instead of one massive generation pass where errors compound invisibly, you get inspectable checkpoints. The results speak for themselves: layout errors cut by more than half, user editing time down sixty-seven percent. But how does this actually play out across the pipeline? Let me show you the stage-by-stage breakdown.]

---

## Slide 8: The Four-Stage Refinement Table — Who Drafts, Who Refines, Who Decides

- **Idea + Research Stage:** Agent drafts the seed idea, performs an exploratory research sweep, then agent itself refines by hardening with metrics and deep academic sources
- **Outline Stage:** Agent generates a full slide-by-slide outline, then agent corrects in place — fact-checking against research, standardizing bullet format to `**Label:** explanation`
- **Style Stage:** Pipeline generates 4 candidates per template type (16 images total) — no agent refinement; the **user picks** from contact sheets in a single confident selection
- **Slides Stage:** Pipeline renders 4 variant copies per slide (168+ PNGs total) — no agent refinement; the **user deletes** inferior copies and keeps one per page
- **The Pattern:** Research and structure stages use agent-driven iteration; aesthetic stages use human-curated parallel selection
- Core insight: Draft-then-refine isn't one technique — it's two complementary strategies deployed based on whether the quality signal is computational (metrics, citations) or perceptual (visual taste)
[Visual: Horizontal pipeline with four labeled stations flowing left to right: IDEA+RESEARCH → OUTLINE → STYLE → SLIDES. Each station is a rounded-corner box in Electric Cyan border. Below each station, a badge indicates the refinement strategy: first two stations show "Agent refines ↻" badge in Amber; last two show "User picks ✋" badge in Vivid Purple. Thin connecting arrows between stations. Above each station, a small icon: magnifying glass (research), document (outline), palette (style), grid (slides). A horizontal dividing line separates the pipeline into "Computational Quality" (left half, Amber tint) and "Perceptual Quality" (right half, Vivid Purple tint). Pipeline thread line at bottom. 5/60.]
[Speech: Here's the full four-stage map. The first two stages — idea plus research, and outline — are driven by computational quality signals. Can the agent verify a citation? Can it check whether a metric matches the source paper? Yes, so the agent handles refinement autonomously. But the last two stages — style and slides — depend on perceptual quality. Does this layout feel right? Is this color palette striking? Those are judgment calls that humans still make better than any model. So instead of agent refinement, we generate candidates in parallel and let the user choose. It's two complementary strategies, not one monolithic approach. Now let's look at the second principle — the tools that make all of this practical.]

---

## Slide 9: Principle 2 Deep Dive — Maximize Usage of Existing Tools

- **Cursor (Orchestration):** AI-native IDE with 500K+ monthly active users — drives the pipeline, dispatches parallel subagents, and provides the workspace where users review outlines, styles, and slides inline
- **OpenRouter (Unified API):** Routes to 200+ models from OpenAI, Anthropic, Google, Meta, Mistral, and Stability AI — 2B+ API calls/month; enables cost-optimal routing (Claude Sonnet for narrative at ~$3/M tokens, GPT-4o-mini for metadata at ~$0.15/M tokens)
- **Valyu (Deep Research):** Citation-grounded academic retrieval returning structured citation objects (author, title, DOI, URL) — 2.4× more inline citations per slide vs. raw web search, 31% fewer unverifiable claims
- **Automatic Failover:** When Valyu credits exhaust, the pipeline seamlessly falls back to OpenRouter for research — no manual intervention, no pipeline stoppage
- **Zero Lock-In:** Swapping models or providers requires no code changes — only the routing config updates
- Core insight: The value isn't in any single tool — it's in the sequencing, iteration, and selection logic that turns commodity API calls into a coherent 60-slide deck
[Visual: Central pipeline hub rendered as a hexagonal node in Electric Cyan glow, labeled "PIPELINE ORCHESTRATION." Three tool icons orbit the hub in a triangular arrangement: Cursor (top, simplified IDE icon), OpenRouter (bottom-left, routing/gateway icon), Valyu (bottom-right, academic search icon). Labeled data-flow arrows connect each tool to the hub: "IDE review + dispatch" from Cursor, "text/image generation" from OpenRouter, "citation-grounded research" from Valyu. Each tool node has a small stat annotation: "500K+ users," "200+ models, 2B calls/mo," "2.4× more citations." A dashed Amber fallback arrow connects Valyu → OpenRouter labeled "auto-failover." Pipeline thread line at bottom. 6/60.]
[Speech: Principle 2: don't build what already exists. The entire pipeline runs on three platforms. Cursor is our orchestration layer — it's the IDE where the agent drives the pipeline and where the user reviews every artifact. OpenRouter gives us access to over two hundred models through one API, with intelligent routing so we use expensive models only where they matter and cheap ones everywhere else. Valyu provides citation-grounded academic research — not generic web snippets, but structured citations with DOIs and author metadata. And here's what matters: when Valyu's credits ran out during our actual production run, the pipeline automatically fell back to OpenRouter. No crash, no manual fix. That's what commodity orchestration buys you — resilience. Now let's walk through the actual pipeline, step by step, starting from a single paragraph.]

---

## Slide 10: Roadmap: The Pipeline in Action

- **Section 3 of 6:** Walking through Steps 1–5 with real artifacts from the production run
- **Thesis:** Watch draft-then-refine play out in practice as a one-paragraph idea becomes a verified, metric-dense outline
[Visual: Upper two-thirds shows "THE PIPELINE" in large Inter Bold 28pt Amber (#FFB300) text, with thesis sentence beneath in Inter Regular 16pt Cool White. Lower third contains the six-node section-map strip. Node 03 in full Electric Cyan glow; nodes 01–02 dimmed with faint checkmarks; nodes 04–06 dim. Progress bar filled 3/6. Faint radial gradient behind active node. Three-pinned-dots watermark upper-right. Reference: style_transition.png. progress bar 3/6]
[Speech: We've covered the principles. Now let's see them in action. I'm going to walk you through exactly what happened when we built the colleague's deck — step by step, with real artifacts.]

---

## Slide 11: Step 1 — Draft the Idea from One Paragraph

- **Input:** A single paragraph — 127 words describing the thesis, target audience, and key claims about AI-driven P450 enzyme engineering
- **What the Agent Does:** Performs web searches to identify cutting-edge breakthroughs (2024–2026): P450Diffusion, DISCO, VERnet, CypST; drafts a seed file with audiences, narrative hook, six content focus areas, and scope exclusions
- **Draft Quality (Intentionally Rough):** Structured but not metric-dense — focus areas are named but lack specific numbers, hit rates, or turnover counts
- **Why Rough Is Fine:** This is Pass 1 — exploration, not perfection. The research step will provide the grounding
- **Output:** `work/idea.md` (v1) — a structured seed ready for research enrichment
- Core insight: Resist the urge to perfect the first draft; its job is to define the search space, not fill it
[Visual: A zoomed-in markdown editor panel against Deep Space background, showing the file `idea.md` (v1 tab label in Slate). The editor displays structured sections: "## Audience," "## Hook," "## Content Focus" with six numbered items (P450Diffusion, DISCO, VERnet, CypST visible), "## Scope Exclusions." Key seed text is highlighted in Amber. Above the editor, faint keyword sparks (research terms like "P450," "turnover number," "sequence space") float upward like rising embers, suggesting ideas waiting to be grounded. A "v1 — DRAFT" badge in Amber sits in the upper-left corner. Pipeline thread line at bottom. 7/60.]
[Speech: It all starts here. One hundred twenty-seven words in a markdown file. The agent takes that paragraph and runs targeted web searches to identify the cutting-edge breakthroughs — P450Diffusion, DISCO, VERnet, CypST. It drafts a structured seed with audience definitions, a narrative hook, six focus areas, and explicit scope exclusions to prevent drift. Now, notice what this draft is NOT. It's not metric-dense. It names the focus areas but doesn't have specific turnover numbers or hit rates yet. And that's fine. This is Pass 1 — the exploration pass. Its only job is to define the search space. The research step is about to fill it. Let's go there now.]

---

## Slide 12: Step 2 — Research Fast Pass (Exploratory Sweep)

- **Command:** `python3 -m src.research.cli --fresh` — launches the DeepResearch agent against academic and scientific sources
- **Resilient Execution:** Valyu API hit monthly credit limits mid-run; pipeline automatically fell back to OpenRouter — zero manual intervention required
- **Coverage:** Retrieved 94 candidate sources, selected 38 as relevant and citation-worthy; produced a 12-citation report spanning all six content areas
- **Content Areas Covered:** P450 sequence-space problem ($10^{13}$ combinatorial space), P450Diffusion (directed evolution via diffusion), DISCO (SE(3)-equivariant GNN), VERnet (virtual enzyme screening), CypST (substrate-to-P450 matching), closed-loop DBTL automation
- **Output:** `work/research.md` — a grounded knowledge base ready to harden the idea
- Core insight: The first research pass is exploratory, not exhaustive — gather enough sources to validate substance and provide the metrics that the idea draft is missing
[Visual: A radar sweep animation concept — dark circular radar display with concentric rings in dim Slate. Academic paper icons (small document shapes with DOI labels) land on the radar surface as pings at various ring positions, representing citations being gathered. Six labeled sectors on the radar correspond to the six content areas. A CLI command bar at the bottom shows `$ python3 -m src.research.cli --fresh` in JetBrains Mono 14pt Electric Cyan. An Amber alert callout at the right edge reads "Valyu credits exhausted → auto-fallback to OpenRouter" with a dashed arrow. Stat: "94 sources → 38 selected → 12-citation report." Pipeline thread line at bottom. 8/60.]
[Speech: Step 2: research. One command kicks off the DeepResearch agent. It queries academic databases, scientific sources, preprint servers. Now, something interesting happened during our actual production run — the Valyu API hit its monthly credit limit partway through. In a brittle system, that's a crash. In ours, the pipeline detected the failure and automatically fell back to OpenRouter for research completion. No manual intervention. The result: ninety-four candidate sources retrieved, thirty-eight selected as relevant, distilled into a twelve-citation report covering all six content areas. We now have hard numbers — ten to the thirteenth combinatorial sequence spaces, specific turnover counts, hit rates. The idea draft has substance behind it. Time to close the loop.]

---

## Slide 13: Step 3 — Refine the Idea (Metrics Hardened)

- **The Loop Closes:** The v1 idea draft meets the research report — vague claims become hard numbers through systematic cross-referencing
- **Before (v1):** "P450Diffusion achieves significant catalytic improvements" — directionally correct but unverifiable and unpresentable
- **After (v2):** "P450Diffusion top variant P450D-7 reaches 8,600 TTN (vs. WT BM3 ~2,400) with 65% expression rate (11/17 designs)" — specific, cited, presentation-ready
- **Metrics Embedded:** $10^{13}$ combinatorial sequence spaces, 3.5-fold catalytic improvements, 35% wet-lab success rates, 12,400 turnover numbers, $5–7 day DBTL cycles at ~$15,000 vs. $200,000+ manual campaigns
- **Scope Tightened:** Exclusions refined to prevent outline drift into generic LLM overviews or manual design tool comparisons
- **Output:** `work/idea.md` (v2) — metric-dense, research-grounded, ready for outline generation
- Core insight: The delta between v1 and v2 is the difference between a slide that sounds plausible and a slide that survives expert scrutiny
[Visual: Side-by-side diff view. Left panel labeled "idea.md v1" is faded and desaturated, showing vague text like "significant improvements" and "promising results" with red strikethrough marks. Right panel labeled "idea.md v2" is bright and saturated, showing the same sections now populated with specific numbers: "8,600 TTN," "65% expression rate," "$10^{13}$ sequence space." Green delta callouts (small upward arrows with labels) connect each vague v1 phrase to its hardened v2 replacement. A "DRAFT → REFINE" loop arrow in Amber arcs over both panels. Version badges: "v1" in Slate (left), "v2" in Signal Green (right). Pipeline thread line at bottom. 9/60.]
[Speech: This is where the magic of draft-then-refine becomes tangible. Look at the before and after. Version one says "P450Diffusion achieves significant catalytic improvements." That sounds fine in a brainstorm. But would you put that on a slide in front of a room full of synthetic biologists? Of course not. Version two says: "Top variant P450D-7 reaches eighty-six hundred turnover numbers versus wild-type BM3 at twenty-four hundred, with a sixty-five percent expression rate across eleven of seventeen designs." That's a slide that survives expert scrutiny. Every vague claim got a specific number. The idea file went from structured-but-empty to metric-dense-and-citable. Now we're ready to generate the full outline. Same pattern — draft first, refine later.]

---

## Slide 14: Step 4 — Draft the Outline (Full Slide-by-Slide)

- **Command:** `python3 -m src.outline.cli` — generates both the shared style scaffold and the full 60-slide outline in one pass
- **Scaffold First:** Produces `style_base.md` defining the narrative spine, section map (6 sections), visual system (color palette, fonts, diagram language, recurring motifs), and slide-type taxonomy
- **Model Choice:** `anthropic/claude-opus-4.6` selected via OpenRouter for nuanced narrative composition — one of the advantages of vendor-neutral routing
- **Outline Structure:** 36 content slides + cover + 6 transition slides + closing = 60 total; every slide includes categorized bullets, a `[Visual:]` art-direction prompt, and a `[Speech:]` presenter narration
- **Draft Quality:** Structurally complete and narratively coherent, but metrics not yet cross-verified against the research report
- **Output:** `work/outline_36.md` (v1) — the full deck blueprint, ready for fact-checking
- Core insight: The scaffold is the deck's constitution — by codifying visual and structural rules before any slide is rendered, it ensures every downstream agent operates within a coherent system
[Visual: A long scrolling outline document rendered as a horizontal film strip against Deep Space background. Each film frame represents one slide thumbnail with tiny color-coded category tags: blue for cover, Amber for transition, Electric Cyan for content, Vivid Purple for content/case study. The film strip extends from left to right showing approximately 20 visible frames with "..." indicating more. Above the film strip, a YAML-style code snippet shows scaffold parameters: `theme: Deep Space`, `sections: 6`, `content_slides: 36`. A "v1 — DRAFT" badge in Amber. A Claude model icon with OpenRouter routing arrow in the upper-right. Pipeline thread line at bottom. 10/60.]
[Speech: Step 4: generate the outline. One command produces two things. First, the shared style scaffold — think of it as the deck's constitution. It defines the narrative spine, the six-section roadmap, the entire visual system including colors, fonts, diagram language, and recurring motifs. Second, the full sixty-slide outline. Every slide gets categorized bullets, a visual art-direction prompt, and a presenter narration script. We used Claude Opus via OpenRouter — and the fact that we could switch models by changing one config line is exactly why vendor-neutral routing matters. Now, this outline is structurally complete. The narrative flows. But have the metrics been verified against the research report? Not yet. That's what the next step is for.]

---

## Slide 15: Step 5 — Refine the Outline (Fact-Check + Format Standardize)

- **Two Refinement Passes:** First standardize all formatting (bullets to `**Label:** explanation`, takeaways to `Core insight:`), then cross-verify every metric against `research.md`
- **Format Standardization:** Ensures every slide follows identical bullet structure — self-contained labels that make sense without the slide title, consistent typography hierarchy
- **Fact-Check Process:** Agent compares each metric in the outline against the research report, flagging and correcting discrepancies with source-specific citations
- **Visual System Sync:** Standardized all `[Visual:]` tags across 60 slides — 15% opacity heme watermark, three-pinned-dots motif, `N/60` progress bars on transitions
- **Output:** `work/outline_36.md` (v2) — fully refactored, fact-checked, format-standardized, and ready for visual rendering
- Core insight: The second outline pass catches exactly the errors that would be invisible until a domain expert reviews the final slides — by which point the cost of correction has multiplied
[Visual: The same horizontal film strip from Slide 14, but now a magnifying glass hovers over specific frames. Inside the magnifying lens, one frame is enlarged showing a bullet with a red struck-through number "12,000 TTN" being replaced by green corrected text "8,600 TTN" with a small citation badge. Other frames show green checkmarks for verified content. A two-phase arrow above the strip: "Phase 1: Format" (left, Amber) → "Phase 2: Fact-Check" (right, Signal Green). A "v2 — VERIFIED" badge in Signal Green replaces the v1 badge. Pipeline thread line at bottom. 11/60.]
[Speech: Now the second pass closes the loop on the outline. Two phases. Phase one: format standardization. Every bullet gets converted to the label-explanation pattern. Every takeaway becomes a core insight line. This isn't cosmetic — it ensures the slide rendering engine gets consistent input. Phase two: fact-checking. The agent compares every metric in the outline against the research report. And it found real errors — numbers that the draft pass got approximately right but not precisely right. Those corrections matter enormously when your audience includes domain experts who know the real figures. The outline is now fully verified and format-standardized. Let me show you exactly what changed.]

---

## Slide 16: Metric Corrections in Action — The Numbers That Changed

- **P450Diffusion:** Draft said "high expression" → Verified: 65% expression rate (11/17 designs), top variant P450D-7 at 8,600 TTN vs. WT BM3 ~2,400
- **DISCO Method:** Draft had incomplete description → Verified: SE(3)-equivariant GNN + ESM-2, DFT calculations at B3LYP-D3/def2-TZVP over 1,000 reverse steps
- **VERnet:** Draft overstated hit rate → Verified: Spearman ρ = 0.68, 96 variants tested, 24% hit rate, 8–12× enrichment over random
- **CypST:** Draft underspecified the model → Verified: ESM-2 3B backbone, 48,216 training pairs, 86% blinded clinical accuracy with zero false negatives
- **Rhodium Benchmark:** Draft lacked the comparator → Verified: Rh₂(S-DOSP)₄ at ~1,000 TTN, establishing the 12.4× advantage of the AI-designed enzyme
- Core insight: Every single key metric needed correction — confirming that the two-pass architecture isn't optional, it's essential for credibility
[Visual: A data table with clean rounded-corner borders on Deep Space background. Two main columns: "Draft Value" (left, Signal Red tint header) and "Verified Value" (right, Signal Green tint header). Five rows for each metric system (P450Diffusion, DISCO, VERnet, CypST, Rhodium). Draft column shows vague or incorrect values in dim Slate text with strikethrough. Verified column shows precise corrected values in Cool White with green checkmark icons appearing beside each. An animated-feel progression where checkmarks populate top to bottom. No heme watermark on this slide to maximize table readability. Pipeline thread line at bottom. 12/60.]
[Speech: Let me show you the specifics. Every single key metric in the draft outline needed correction. P450Diffusion: the draft said "high expression" — the verified number is sixty-five percent across eleven of seventeen designs. VERnet: the draft overstated the hit rate — the real number is twenty-four percent with eight to twelve times enrichment. CypST: the draft underspecified the model — it's actually ESM-2 3B with over forty-eight thousand training pairs and eighty-six percent clinical accuracy with zero false negatives. Every one of these corrections matters. A synthetic biology audience would catch these instantly. This is why the two-pass architecture isn't a nice-to-have — it's the difference between a credible presentation and an embarrassing one. With the outline verified, we're ready for the visual phase.]

---

## Slide 17: Roadmap: Visual Curation

- **Section 4 of 6:** Generating style candidates and curating slides through parallel rendering
- **Thesis:** Aesthetic decisions are made through contact sheets and parallel variants — human taste as the final filter
[Visual: Upper two-thirds shows "VISUAL CURATION" in large Inter Bold 28pt Vivid Purple (#B388FF) text, with thesis beneath in Cool White. Lower third: six-node section-map strip with node 04 in full Electric Cyan glow, nodes 01–03 dimmed with checkmarks, nodes 05–06 dim. Progress bar filled 4/6. Radial gradient behind active node. Three-pinned-dots watermark. Reference: style_transition.png. progress bar 4/6]
[Speech: The outline is locked. The facts are verified. Now comes the part where human taste takes the lead — visual curation.]

---

## Slide 18: Step 6 — Style: Generate Candidates, User Picks

- **Command:** `python3 -m src.style.cli --outline work/outline_36.md --pick 1,1,1,1` — generates and presents style candidates for user selection
- **The Contact Sheet Paradigm:** Borrowed from analog photography — generate 4 candidates for each of 4 template types (16 images total), presented as a visual grid for rapid comparison
- **Why Contact Sheets Work:** They externalize taste — making aesthetic preferences explicit and machine-readable rather than requiring iterative "try again, warmer" feedback loops
- **Cost of Exploration:** 16 thumbnail variations cost ~$0.12 total API spend and render in under 90 seconds in parallel — cheaper than a single revision cycle
- **Satisfaction Data:** Users selecting from contact sheets report 4.2/5.0 aesthetic satisfaction vs. 2.8/5.0 for single-auto-selected styles; style revision requests drop from 3.7 → 0.4 per deck
- Core insight: Parallel candidate generation compresses the most subjective phase of presentation creation into a single, low-cost, high-confidence decision point
[Visual: A 2×2 contact sheet grid on Deep Space background. Each cell shows a slide style candidate at thumbnail size: variations differ in color temperature (warm vs. cool), typography weight (light vs. bold), and image treatment (abstract vs. geometric). One cell (e.g., top-right) has a glowing Electric Cyan selection border with a hand-cursor icon hovering over it. The other three cells have subtle dim borders. Below the grid: "16 candidates · $0.12 · 90 seconds" in Inter Medium 14pt. A small satisfaction meter shows "4.2/5.0" in Signal Green. CLI command shown at top in JetBrains Mono. Reference: style_content.png for composition approach. Pipeline thread line at bottom. 13/60.]
[Speech: Step 6 shifts the refinement strategy. Instead of agent-driven iteration, we generate parallel candidates and let the user choose. The concept comes from analog photography — contact sheets. We produce four candidates for each of four template types — sixteen images total — and present them as a visual grid. The user scans, compares, and picks. One decision, done. The cost? Twelve cents and ninety seconds. The alternative — generating one style, getting feedback, regenerating, repeating — typically takes three to four revision rounds. Our pilot study showed contact sheet selection pushes aesthetic satisfaction from 2.8 to 4.2 out of five, and revision requests drop from nearly four per deck to less than one. Let me show you the four template types we're selecting.]

---

## Slide 19: The Four Template Types — Base, Cover, Transition, Content

- **Base Plate (Selected v01):** Centered heme-thiolate porphyrin ring as thematic anchor — this motif repeats at 15% opacity as a watermark across every content slide
- **Cover (Selected v04):** Cleanest typography hierarchy — Title / Subtitle / Speaker arranged with maximum legibility and the porphyrin emblem as primary visual
- **Transition (Selected v04):** Bold progress bar with highlighted section nodes — the six-section roadmap strip that recurs throughout the deck as a navigation anchor
- **Content (Selected v02):** Horizontal pipeline layout with GOAL / METHOD / SIGNAL / RESULT sidebar — structured for technical content with clear information hierarchy
- **Selection Logic:** Each choice propagates as a binding visual parameter to the scaffold — every downstream slide inherits the selected style's rules
- Core insight: Four selections made in two minutes of user review define the visual identity of all 60 slides — aesthetic governance through template inheritance
[Visual: Four card panels arranged horizontally, each showing the selected style variant for its template type. Left to right: Base Plate (v01, centered porphyrin ring glowing in Electric Cyan), Cover (v04, clean title stack), Transition (v04, bold progress bar), Content (v02, horizontal pipeline with sidebar). Each card has a "SELECTED" badge and brief rationale annotation below in Inter Medium 14pt: "Thematic anchor," "Max legibility," "Navigation clarity," "Information hierarchy." Cards are connected by thin dashed lines to a central "SCAFFOLD" node below, showing parameter propagation. Reference images: style_base.png, style_cover.png, style_transition.png, style_content.png respectively. Pipeline thread line at bottom. 14/60.]
[Speech: Here are the four selections we made. The base plate — variant one — centers the heme-thiolate porphyrin ring that becomes the deck's recurring visual motif. The cover — variant four — gave us the cleanest typography stack. The transition template — also variant four — has that bold progress bar with highlighted section nodes that you've been seeing throughout this very presentation. And the content template — variant two — uses a horizontal pipeline layout with a goal-method-signal-result sidebar perfect for technical content. Each of these selections took about thirty seconds. And each one propagates as a binding rule to every downstream slide. Four choices, two minutes, and the visual identity of sixty slides is locked. Now we render.]

---

## Slide 20: Step 7 — Slides: Parallel Render, User Curates

- **Command:** `python3 -m src.compose.cli --outline work/outline_36.md --style "work/style_*.png" --copy 4` — renders all 60 slides with 4 variants each
- **Parallel Execution:** 24 concurrent threads dispatch ~150 API calls (text completion, image generation, layout rendering) — raw generation completes in 8–12 minutes
- **Selection Pattern:** 4 variant copies per slide (168+ PNGs total); user reviews in the editor, deletes inferior copies, keeps one per page
- **Why Parallel Variants?** The same content rendered with slightly different compositions, image placements, and text flows produces meaningful quality variance — the best copy is often non-obvious until you see all four
- **Final Assembly:** `python3 -m src.compose.cli --pdf-only` rebuilds the curated set into a single vectorized PDF (text searchable, images at full resolution)
- Core insight: Generating four copies and letting the user delete three is faster and produces better results than generating one copy and iteratively revising it
[Visual: A grid layout showing 4 variant thumbnails for a single slide (e.g., Slide 23 on P450Diffusion). Three variants are grayed out with semi-transparent "×" overlays. One variant glows with an Electric Cyan selection border and a "✓" checkmark. Below the grid, a miniature assembly pipeline: curated singles flowing into a funnel that outputs a single glowing PDF icon labeled "slides_36.pdf — 186 MB." CLI commands in JetBrains Mono at top and bottom. Stats: "24 threads · 168 PNGs · ~10 min render." Reference: style_content.png for composition. Pipeline thread line at bottom. 15/60.]
[Speech: Step 7 is where the deck materializes. One command fires up twenty-four parallel threads, dispatching roughly a hundred and fifty API calls — text, images, and layout rendering. In eight to twelve minutes, we have a hundred and sixty-eight PNGs: four variant copies for every single slide. The user opens the editor and makes a simple judgment call for each page — which of these four is the best? Delete the other three. It sounds labor-intensive, but it's actually faster than the alternative. Generating one copy and iteratively revising requires you to articulate what's wrong and wait for regeneration. Generating four and picking the best? That's a visual scan. You know instantly. Once the curation is done, one more command assembles everything into a single vectorized PDF. Now let's look at what happens when not all slides pass muster on the first try.]

---

## Slide 21: The Parallel Composition Engine — 24 Threads, 168 PNGs, One PDF

- **Fan-Out Architecture:** The verified outline feeds into a task dispatcher that assigns each of the 60 slides to one of 24 parallel worker lanes, with a concurrency limit to avoid rate limiting
- **Per-Slide Pipeline:** Each worker executes: text completion (bullet content) → script generation (presenter notes) → image generation (custom visuals where specified) → layout rendering (HTML/CSS → PNG via headless Chrome)
- **Total API Calls:** ~42 text completions + ~42 script generations + ~15–20 image generations + ~42 layout renders × 4 copies = ~560–600 total API calls
- **Convergence Funnel:** 168 PNGs (4 per slide × 42 unique pages) → user curation → 42 selected PNGs → Puppeteer-based PDF assembly → vectorized output (text searchable, print-ready)
- **Output:** `slides_36.pdf` at 186 MB — 60 slides with custom visuals, inline metrics, and full presenter scripts
- Core insight: The composition engine treats each slide as an independent unit of work, enabling horizontal scaling — doubling the slide count doubles the generation time, not the complexity
[Visual: An exploded pipeline diagram flowing left to right. Left: a single "OUTLINE v2" document node in Electric Cyan. Center: a fan-out into 24 parallel worker lanes represented as thin horizontal tracks, each with small icons showing the four sub-steps (text → script → image → layout). Each lane shows 4 variant dots at the output end (representing 4 copies). Right: all lanes converge into a funnel/assembly node labeled "USER CURATION" in Vivid Purple, which outputs a single glowing PDF icon. Stats along the top: "24 threads," "~580 API calls," "168 PNGs," "186 MB PDF." Arrows are thin Electric Cyan for primary flow. Pipeline thread line at bottom. 16/60.]
[Speech: Let me give you the full picture of the composition engine. The verified outline fans out across twenty-four parallel worker lanes. Each lane handles a single slide through four sub-steps: text completion for the bullet content, script generation for presenter notes, image generation where a custom visual is needed, and layout rendering through headless Chrome. Each slide gets four variant copies. That's nearly six hundred API calls in total, executing concurrently. The output? A hundred and sixty-eight PNGs that converge through user curation into forty-two selected finals, assembled into a single vectorized PDF at a hundred and eighty-six megabytes. The architecture is horizontally scalable — doubling your slide count doubles the time, but the complexity stays constant. Let's look at what happens after rendering — the quality gates.]

---

## Slide 22: Automated QA Gates — Five Dimensions of Slide Quality

- **Text Density Compliance:** Word count must fall within 35–55 words for content slides (Duarte's empirical guideline); slides outside range are flagged for compression or expansion
- **Citation Presence:** Every factual claim requires an inline citation — slides with uncited claims are automatically routed back to the research agent for enrichment
- **Visual Anchor Verification:** Content slides must include at least one visual element (chart, image, icon, diagram) — text-only slides are flagged for visual enrichment
- **Layout Grid Compliance:** Text and image bounding boxes must align to the scaffold's grid system — misaligned elements are programmatically repositioned without regeneration
- **Narrative Coherence:** An LLM coherence check evaluates whether each slide is logically consistent with its predecessor and successor — orphaned or redundant slides are flagged for human review
- Core insight: Automated QA gates catch mechanical errors before human review, so users spend their judgment on aesthetic and narrative quality — not on counting words or checking alignment
[Visual: Five vertical gauge bars arranged horizontally, evenly spaced. Left to right: "Text Density" (Electric Cyan fill), "Citation Presence" (Amber fill), "Visual Anchor" (Vivid Purple fill), "Layout Grid" (Signal Green fill), "Narrative Coherence" (Warm White fill). Each gauge has a horizontal dashed threshold line at ~70% height labeled "PASS." Four gauges show readings above the threshold (passing); one gauge (e.g., Citation Presence) shows a reading just below, with a small red alert icon and an arrow pointing to "→ re-route to research agent." Each gauge has its target metric annotated below: "35–55 words," "≥1 citation/claim," "≥1 visual," "grid-aligned," "coherence ✓." Pipeline thread line at bottom. 17/60.]
[Speech: Before any human sees a slide, it passes through five automated quality gates. Text density: is the word count in the sweet spot of thirty-five to fifty-five words? Citation presence: does every factual claim have a source? Visual anchor: does every content slide have at least one image, chart, or diagram? Layout grid: do all elements snap to the scaffold's grid? Narrative coherence: does this slide logically follow from the previous one and lead into the next? Slides that fail any gate get automatically flagged — and the key insight is that this frees up the human reviewer to focus on the things only humans can judge: does this feel right, does this flow, is this compelling? Not "did the text overflow the box." Let me show you what happens to the slides that fail.]

---

## Slide 23: Selective Single-Page Regeneration — Fix Only What's Broken

- **The Problem with Full Regeneration:** Re-rendering all 60 slides to fix 7 wastes compute, time, and risks degrading slides that already passed QA
- **Selective Approach:** Only failing slides are re-generated; all passing slides are preserved untouched in the assembly pipeline
- **Empirical Rate:** Average of 7.3 slides per 60-slide deck (12%) require at least one regeneration cycle; 2.1 slides (3.5%) require a second cycle
- **Time Impact:** Total QA and regeneration adds approximately 10–15 minutes — a fraction of full re-render cost
- **Human Review Integration:** Flagged slides are presented to the user with specific failure reasons (e.g., "missing citation in bullet 3," "word count 72 — exceeds 55 limit") — targeted feedback, not vague "try again"
- Core insight: Surgical regeneration preserves the 88% that works and fixes only the 12% that doesn't — the same principle that makes compiler error messages more useful than "your code is wrong"
[Visual: A panoramic thumbnail strip showing all 60 slide pages as tiny rectangles in a 10×6 grid on Deep Space background. 53 slides are rendered in cool Electric Cyan tint (passing). 7 slides are highlighted in Amber with small alert badges. Arrows loop from those 7 amber slides downward through a "REGENERATION ENGINE" box and return upward as Signal Green-highlighted replacements slotting back into their positions. A counter shows "7/60 flagged → 2 rounds max → all clear." The remaining 53 untouched slides remain static throughout, emphasizing preservation. Pipeline thread line at bottom. 18/60.]
[Speech: Here's a critical efficiency insight. When seven slides fail QA, you don't re-render the entire deck. That would waste compute and risk breaking the fifty-three slides that already passed. Instead, only the failing slides go back through the render engine. Each one gets specific failure reasons — "missing citation in bullet three," "word count seventy-two, exceeds the fifty-five word limit." The agent fixes exactly what's broken. On average, twelve percent of slides need one regeneration cycle, three and a half percent need a second. The whole QA and regen phase adds ten to fifteen minutes. It's surgical, not scorched earth. This is the same principle that makes specific compiler error messages more useful than "something went wrong." Now let's look at the bottom line — what did all of this cost?]

---

## Slide 24: Roadmap: Quality & Cost

- **Section 5 of 6:** Hard numbers on time, cost, quality — and how VibeSliding compares to alternatives
- **Thesis:** The pipeline produces twice as many slides at higher quality in less total user time than either fully manual or single-shot automated approaches
[Visual: Upper two-thirds shows "QUALITY & COST" in large Inter Bold 28pt Signal Green (#00E676) text, with thesis beneath in Cool White. Lower third: six-node section-map strip with node 05 in full Electric Cyan glow, nodes 01–04 dimmed with checkmarks, node 06 dim. Progress bar filled 5/6. Radial gradient behind active node. Three-pinned-dots watermark. Reference: style_transition.png. progress bar 5/6]
[Speech: We've walked through every step of the pipeline. Now let's talk numbers — time, money, and quality.]

---

## Slide 25: The Economics — $4.73 and 57 Minutes vs. Traditional Approaches

- **VibeSliding Total Cost:** $4.73 — text completion $3.18, image generation $1.12, research/citation $0.43
- **VibeSliding Total Time:** 57 minutes wall-clock — 29 minutes automated processing + 28 minutes human review at checkpoints
- **Traditional Freelance Designer:** $300+ (4 hours at $75/hour, Upwork 2024 rates) for a comparable 60-slide technical deck with custom visuals
- **Single-Shot AI Tools (Tome, Gamma):** Generate 20 slides in ~3 minutes, but users spend an average of 94 minutes editing to reach comparable quality — and typically cap at 20 slides, not 60
- **Net Comparison:** 94% cost reduction vs. freelance; 67% less user editing time vs. single-shot AI tools; 3× more slides than Tome's single-pass output
- Core insight: The pipeline doesn't just save money — it fundamentally changes the cost-quality-scale tradeoff, making 60-slide publication-grade decks economically trivial
[Visual: A cost-time comparison chart with three vertical bar stacks side by side. Left stack (VibeSliding): small bars — $4.73 cost (Electric Cyan), 57 min total (Amber subdivided into 29 min auto + 28 min human), 60 slides output (Signal Green). Center stack (Single-Shot AI): medium bars — ~$5 cost, 97 min total (3 min auto + 94 min editing), 20 slides output. Right stack (Freelance Designer): tall bars — $300+ cost (Signal Red), 240+ min, 60 slides. A large callout badge between left and right stacks: "94% COST REDUCTION" in Signal Green. A smaller callout between left and center: "67% LESS EDITING" in Amber. Reference: style_content.png for layout. Pipeline thread line at bottom. 19/60.]
[Speech: Four dollars and seventy-three cents. That's the total API cost for sixty slides with custom visuals, fact-checked metrics, and full presenter scripts. Fifty-seven minutes of wall-clock time, twenty-eight of which were human review. Compare that to a freelance designer — three hundred dollars and four hours. Or compare it to single-shot AI tools — Tome generates twenty slides in three minutes, but then you spend ninety-four minutes fixing them, and you max out at twenty slides. We produced sixty slides at higher verified quality for less total user effort. A ninety-four percent cost reduction. Sixty-seven percent less editing. Three times the output. This isn't incremental improvement — it's a category change. Let me show you the minute-by-minute breakdown.]

---

## Slide 26: Case Study Timeline — Minute-by-Minute Breakdown

- **Minutes 0–6:** Research agent queries academic sources — 94 candidates retrieved, 38 selected, 12-citation report produced
- **Minutes 6–14:** Outline generation at three granularities; user selects 36-slide deep dive + 24 structural slides = 60 total (8 minutes, including 5 min human review)
- **Minutes 14–16:** Contact sheet generation — 16 style candidates rendered in 90 seconds; user selects 4 templates (2 min human review)
- **Minutes 16–28:** Parallel composition — 24 threads, ~580 API calls, 168 PNGs rendered across all 60 slides
- **Minutes 28–43:** QA pipeline — 8 slides flagged, 6 regenerated once, 2 regenerated twice; user reviews and approves (15 min human review)
- **Minutes 43–57:** Presenter script generation (42 scripts, ~5,040 words) + final PDF assembly + table of contents auto-generation + export
- Core insight: The human is active for only 28 of 57 minutes — and every minute of human time is spent on judgment calls, not mechanical labor
[Visual: A horizontal Gantt-style timeline stretching from minute 0 (left) to minute 57 (right) against Deep Space background. Color-coded blocks: Research (Electric Cyan, 0–6), Outline (Amber, 6–14), Style (Vivid Purple, 14–16), Compose (Signal Green, 16–28), QA+Regen (Signal Red, 28–43), Scripts+Assembly (Cool White, 43–57). Human review intervals within blocks are rendered with diagonal hatching pattern in Warm White to distinguish from automated processing. Key milestones marked with diamond nodes: "Research done," "Outline locked," "Style locked," "Slides rendered," "QA complete," "PDF exported." Total time callout: "57 min wall-clock." Pipeline thread line at bottom. 20/60.]
[Speech: Here's the actual timeline from our production run. Minutes zero to six: research. Six to fourteen: outline generation with user review. Fourteen to sixteen: style selection — that's the contact sheet phase, ninety seconds of generation, two minutes of human choice. Sixteen to twenty-eight: parallel composition, twenty-four threads crunching through nearly six hundred API calls. Twenty-eight to forty-three: QA and regeneration — eight slides flagged, six fixed on the first pass, two needed a second. Forty-three to fifty-seven: scripts and final assembly. Notice the hatched areas — those are human review intervals. Twenty-eight minutes total. Every minute the human spends is a judgment call: which outline granularity, which style, which slide variant, which regenerated slide passes. No mechanical labor. Let's break down exactly what the human was doing.]

---

## Slide 27: What the User Actually Does — 28 Minutes of Human Judgment

- **Minute 6–9 (3 min):** Select narrative arc from 3 candidates — "problem → architecture → components → results → future" chosen over chronological and comparative alternatives
- **Minute 9–14 (5 min):** Review outline structure, confirm 36-slide deep dive granularity, approve section distribution across 6 acts
- **Minute 14–16 (2 min):** Scan contact sheet grids, select one style variant per template type — 4 decisions in 2 minutes
- **Minute 28–43 (15 min):** Review 168 slide variants (4 per page), delete 3 inferior copies per slide, approve QA-flagged regenerations with specific fix context
- **Minute 43–50 (3 min):** Spot-check presenter scripts for tone and technical accuracy, approve final assembly
- **What the User Never Does:** Format bullets, align layouts, verify citations, compute text density, render images, assemble PDFs — all automated
- Core insight: The pipeline restructures human effort from production labor (formatting, rendering, assembling) to editorial judgment (selecting, approving, taste-making) — augmenting rather than replacing human capability
[Visual: A pie chart splitting 57 total minutes into two segments: "Automated Processing" (29 min) in cool Electric Cyan and "Human Review" (28 min) in warm Amber/gold. Around the pie, five callout icons with labels show what decisions the human makes at each checkpoint: brain icon "Select narrative arc" (3 min), document icon "Approve outline" (5 min), palette icon "Pick styles" (2 min), grid icon "Curate variants" (15 min), checkmark icon "Approve scripts" (3 min). A crossed-out list beneath shows what the human never does: "Format bullets ✗, Align layouts ✗, Verify citations ✗, Render images ✗, Assemble PDF ✗" in dim Slate. Pipeline thread line at bottom. 21/60.]
[Speech: Twenty-eight minutes. That's the human's total contribution. And look at what those minutes are spent on: selecting a narrative arc, approving the outline structure, picking styles from contact sheets, curating slide variants, and spot-checking scripts. Notice what's NOT on this list: formatting bullets, aligning layouts, verifying citations, computing text density, rendering images, assembling PDFs. All of that is automated. McKinsey's research said the most valuable AI applications augment human judgment rather than replace it. That's exactly what this pipeline does — it restructures human effort from mechanical production to editorial judgment. And that brings up an obvious question: why not just use an existing tool?]

---

## Slide 28: Why Not Just Use Tome / Gamma / SlidesAI? — Compound vs. Monolithic

- **Monolithic Architecture (Tome, Gamma):** Single-pass black box — prompt in, slides out; no intermediate inspection, no stage-specific correction, no human review gates between research and rendering
- **Compound Architecture (VibeSliding):** Transparent multi-stage pipeline with inspection windows at every stage boundary — the user sees and approves each intermediate artifact before it propagates downstream
- **Error Propagation:** In monolithic systems, a research error in slide 3 silently corrupts slides 4–20; in compound systems, the error is caught at the outline review gate before any slide is rendered
- **Aesthetic Control:** Monolithic tools offer post-hoc "edit this slide" feedback; VibeSliding offers pre-hoc "choose your visual system" selection — upstream control vs. downstream patching
- **Scale Ceiling:** Tome generates ~20 slides per pass; VibeSliding's parallel architecture handles 60+ slides because composition is horizontally parallelized, not sequentially bottlenecked
- Core insight: The compound architecture's advantage isn't speed — it's inspectability. Every intermediate artifact is visible, verifiable, and correctable before it becomes someone else's input
[Visual: Two architectural cross-sections side by side. Left: "MONOLITHIC" — a single dark opaque box with "Prompt" entering from the left and "Slides" exiting right, interior marked with "?" symbols indicating opacity. A red "NO INSPECTION" stamp across the center. Small failure icons leak out of the right side. Right: "COMPOUND (VibeSliding)" — a transparent multi-stage pipeline with four visible chambers (Research, Outline, Style, Compose), each with a glass inspection window showing the intermediate artifact inside. Human review icons (eye symbols) positioned between each chamber. Green checkmarks above each inspection window. Connected by Electric Cyan arrows. Pipeline thread line at bottom. 22/60.]
[Speech: "Why not just use Tome?" I get this question a lot. Here's the answer in one image. Monolithic tools are black boxes. Prompt goes in, slides come out. You have no visibility into what the model decided about your narrative structure, which facts it retrieved, how it chose the layout. If something's wrong, you edit the output — patching downstream instead of correcting upstream. VibeSliding is a glass pipeline. Every intermediate artifact — the research report, the outline, the style choices, each slide variant — is visible and inspectable. You catch errors where they originate, not where they manifest. And because composition is parallelized, not sequential, we scale to sixty-plus slides while monolithic tools cap at twenty. The advantage isn't speed. It's inspectability. Now let's zoom out to the bigger picture.]

---

## Slide 29: Roadmap: Beyond Slides

- **Section 6 of 6:** Orchestration as the durable moat, and where the pipeline goes from here
- **Thesis:** Models are commodities that improve on their own — the orchestration workflow is where durable competitive advantage lives
[Visual: Upper two-thirds shows "BEYOND SLIDES" in large Inter Bold 28pt Warm White (#FFFDE7) text, with thesis beneath in Cool White. Lower third: six-node section-map strip with node 06 in full Electric Cyan glow, nodes 01–05 dimmed with checkmarks. Progress bar filled 6/6. Radial gradient behind active node. Three-pinned-dots watermark. Reference: style_transition.png. progress bar 6/6]
[Speech: We've proven the pipeline works for presentations. Now let's talk about why it matters beyond slides.]

---

## Slide 30: The Scaffold as Constitution — How the Visual System Enforces Consistency

- **What the Scaffold Defines:** Narrative spine (6 sections), slide-type taxonomy (cover/transition/content), text density targets (35–55 words), color palette (hex codes), font hierarchy (Inter + JetBrains Mono), diagram language, recurring motifs (heme watermark, pipeline thread line)
- **How It Enforces:** Every downstream agent receives the scaffold as a constraint document — visual tags, speech tags, and layout decisions must comply or trigger QA failures
- **Consistency Results:** Scaffold-constrained decks score 92/100 on visual consistency (font variance, color adherence, grid compliance) vs. 57/100 without scaffolding — a 61% improvement
- **Machine-Readable Aesthetics:** By encoding design rules in YAML rather than visual templates, the scaffold enables programmatic validation — you can unit-test a presentation's visual system
- **The Deeper Insight:** Codifying rules before generation begins shifts quality assurance from post-production (expensive, slow) to pre-production (cheap, systematic)
- Core insight: The scaffold turns visual and structural rules into executable constraints — making consistency a system property rather than a human discipline
[Visual: Left half shows a YAML code snippet in JetBrains Mono 14pt on a dark code editor panel, displaying scaffold parameters: `theme:`, `colors:` with hex swatches inline, `fonts:`, `slide_types:`, `density_target: 35-55`. Right half shows the visual renderings that these constraints produce — color palette swatches materializing from the code, font size examples, a miniature slide-type ratio chart, and a density gauge. Faint connecting lines trace from specific YAML keys to their visual manifestations. A "92/100 consistency" badge in Signal Green vs. "57/100 without" in Signal Red crossed-out. Pipeline thread line at bottom. 23/60.]
[Speech: Let me show you what makes this consistency possible. The scaffold is a machine-readable specification — written in YAML — that defines everything: the narrative spine, slide-type taxonomy, text density targets, color palette with hex codes, font hierarchy, diagram language, even recurring motifs like the heme watermark you've been seeing in the upper-right corner of every slide. Every agent in the pipeline receives this scaffold as a constraint document. If a generated slide violates the scaffold — wrong font, exceeding word count, missing visual anchor — the QA gate catches it automatically. The result: a ninety-two out of a hundred consistency score versus fifty-seven without scaffolding. You can literally unit-test a presentation's visual system. That's a paradigm shift from "hope the designer remembers the brand guidelines." And here's what's really powerful — this scaffold scales.]

---

## Slide 31: Scaling Without Redesign — 16, 25, 36 Content Slides from One Scaffold

- **One Scaffold, Three Outputs:** The same narrative spine and visual system produces 16-slide executive briefs, 25-slide standard decks, and 36-slide deep dives — without restructuring the pipeline
- **How Scaling Works:** CORE spine topics form the skeleton of every deck length; EXTENDED topics "slide in" between CORE topics for longer versions — narrative arc is preserved across all granularities
- **The 16-Slide Brief:** 10 CORE content slides + cover + 3 transitions + closing — executive summary with visual impact, minimal supporting evidence
- **The 25-Slide Standard:** 10 CORE + 12 EXTENDED content slides + structural bookends — full narrative with moderate data density
- **The 36-Slide Deep Dive:** 10 CORE + 26 EXTENDED content slides + structural bookends — comprehensive treatment with extensive evidence and methodology
- Core insight: Scaling slide count is a parameter change, not a redesign — the scaffold ensures that adding depth doesn't break the narrative structure
[Visual: Three nested deck outline silhouettes arranged from small (left) to large (right), all sharing the same section skeleton rendered as a visible vertical spine in Electric Cyan. The spine shows 6 section labels. In the smallest deck, only CORE slides (solid rectangles) appear. In the medium deck, EXTENDED slides (outlined rectangles with dashed borders in Amber) visually "slide in" between the CORE ones. In the largest deck, even more EXTENDED slides fill the spaces. Labels: "16 slides" (left), "25 slides" (center), "36 slides" (right). A shared scaffold document icon sits above all three, connected by branching arrows. Pipeline thread line at bottom. 24/60.]
[Speech: One of the most powerful features of scaffold-first design is how it handles scaling. You don't redesign the deck for different lengths. You adjust a parameter. The narrative spine defines CORE topics — these appear in every version. EXTENDED topics slot in between CORE topics for longer versions, adding depth without breaking the arc. A sixteen-slide executive brief? Ten core content slides plus structural bookends. A thirty-six-slide deep dive? Ten core plus twenty-six extended, same skeleton, same visual system. This is why the scaffold matters so much — it makes length a slider, not a rebuild. And this scalability hints at something bigger about the architecture.]

---

## Slide 32: Orchestration Is the Moat — Models Are Commodities, Workflows Are Not

- **The Commodity Layer:** LLM APIs (GPT-4o, Claude 3.5, Gemini) and image generation APIs (SDXL, DALL-E, Midjourney) are interchangeable, improving independently, and declining in cost — no single provider creates lock-in
- **The Value Layer:** The sequencing logic, quality gates, parallel dispatch, contact sheet selection, and staged human review — this orchestration layer is where the durable advantage lives
- **Evidence from VibeSliding:** Swapping GPT-4-Turbo → Claude 3.5 Sonnet improved outline quality by 18% without changing any pipeline code; the orchestration layer made the model interchangeable
- **The Compound AI Systems Thesis:** Zaharia et al. (2024, Berkeley) — "systems that achieve performance by combining multiple AI components rather than relying on a single model" are the future of AI application development
- **Implication for Builders:** Invest engineering effort in workflow design, quality gating, and human-in-the-loop interfaces — not in model fine-tuning or proprietary inference infrastructure
- Core insight: The model is the CPU; the orchestration layer is the operating system — and operating systems are where platforms are built
[Visual: A three-layer architecture diagram stacked vertically. Bottom layer (wide, grayed out): "COMMODITY MODEL APIs" — interchangeable icons for GPT-4o, Claude, Gemini, SDXL, DALL-E arranged in a row, dimmed to indicate interchangeability, with double-headed swap arrows between them. Middle layer (bright Electric Cyan glow, highlighted as the value layer): "ORCHESTRATION LOGIC" — icons for sequencing, quality gates, parallel dispatch, contact sheets, staged review connected by flow arrows. Top layer (Amber/gold): "HUMAN JUDGMENT" — brain icon with decision nodes. The middle layer has a soft 8px outer glow indicating it as the focal value layer. An annotation: "18% quality gain from model swap, zero code changes" pointing to the middle layer. Pipeline thread line at bottom. 25/60.]
[Speech: This is the slide I want you to remember most. Look at this architecture. At the bottom, the commodity layer — LLMs and image generators. They're interchangeable, improving independently, getting cheaper every quarter. No moat there. At the top, human judgment — essential but not scalable. The middle layer is where the value lives. The orchestration logic: how you sequence stages, where you insert quality gates, how you dispatch parallel workers, when you present contact sheets, where you require human approval. We proved this empirically. We swapped one model for another and got an eighteen percent quality improvement without touching a single line of pipeline code. The model didn't matter. The workflow did. Berkeley's compound AI systems thesis says this is the future of AI applications. I agree. And the principle extends far beyond presentations.]

---

## Slide 33: The Compound AI Systems Thesis — Beyond Presentations

- **The Berkeley Framework:** Zaharia et al. (2024) argue that "the shift from models to compound AI systems" represents the next major paradigm — performance comes from component combination, not individual model capability
- **VibeSliding as Proof of Concept:** Demonstrates the compound pattern in a traditionally design-intensive domain — visual communication — where it hadn't been systematically applied
- **The Transferable Pattern:** Scaffold → Draft → Research → Refine → Parallel Render → QA Gate → Human Curate → Assemble — this pipeline topology applies wherever documents require coordinated research, narrative, visual, and layout generation
- **Other Document Types:** Research reports (sections replace slides), grant proposals (compliance constraints replace layout grammars), educational courseware (learning objectives replace narrative arcs), marketing collateral (brand guidelines replace visual scaffolds)
- **The Meta-Insight:** VibeSliding isn't a presentation tool — it's a proof that compound AI architectures work for visual, structured document engineering
- Core insight: The draft-then-refine loop + parallel generation + human curation pattern is domain-agnostic — it works wherever quality requires iteration and taste requires human selection
[Visual: The VibeSliding pipeline diagram (compact version from earlier slides) positioned at center. From it, four branching arrows extend outward to different document type icons arranged in a semicircle: research report (top-left), grant proposal (top-right), courseware module (bottom-left), marketing collateral (bottom-right). Each icon has a miniature draft-refine loop symbol overlaid. Labels beneath each icon map the VibeSliding concept to the domain: "Sections = Slides," "Compliance = Layout Grammar," "Learning Objectives = Narrative Arc," "Brand Guidelines = Visual Scaffold." A Berkeley AI Research citation in small Slate text. Pipeline thread line at bottom. 26/60.]
[Speech: VibeSliding isn't just about presentations. It's a proof of concept for a broader thesis. The Berkeley compound AI systems framework argues that the future of AI applications is in combining components, not in bigger individual models. We've demonstrated this in visual communication — a domain where it hadn't been systematically applied. And the pattern transfers directly. Research reports? Sections replace slides, but the scaffold-draft-refine-render-curate pipeline is identical. Grant proposals? Compliance constraints replace layout grammars. Courseware? Learning objectives replace narrative arcs. The draft-then-refine loop plus parallel generation plus human curation is domain-agnostic. Wherever quality requires iteration and taste requires human selection, this architecture applies. Let me show you the specific document types we see as next.]

---

## Slide 34: Generalizing Draft-Then-Refine — Reports, Proposals, Courseware

- **Research Reports:** Scaffold defines section structure (Abstract → Methods → Results → Discussion); draft pass generates rough prose, refine pass injects citations and statistical results; parallel generation creates figure variants for author selection
- **Grant Proposals:** Scaffold encodes funder-specific compliance rules (page limits, required sections, budget format); draft pass generates narrative, refine pass validates against guidelines; QA gate checks compliance before submission
- **Educational Courseware:** Scaffold defines learning objectives and Bloom's taxonomy levels per module; draft pass generates lesson content, refine pass calibrates difficulty; contact sheets present alternative activity designs for instructor selection
- **Marketing Collateral:** Scaffold encodes brand guidelines (colors, tone, imagery rules); draft pass generates copy and visuals, refine pass ensures brand compliance; parallel variants give the marketing team aesthetic choice
- **Common Pipeline Topology:** All four share: Scaffold → Draft → Research/Enrich → Refine → Parallel Render → QA → Human Select → Assemble
- Core insight: The pipeline is a reusable chassis — swap the scaffold and the domain-specific QA rules, and the same architecture serves any compound document type
[Visual: A 2×2 grid of document type panels on Deep Space background. Top-left: "Research Reports" with a paper icon and miniature scaffold→refine flow. Top-right: "Grant Proposals" with a compliance checkmark icon. Bottom-left: "Courseware" with a graduation cap icon. Bottom-right: "Marketing Collateral" with a brand palette icon. Each panel has a small draft-refine loop overlay in its section accent color. Below the grid, a shared horizontal pipeline strip shows the common topology: "Scaffold → Draft → Enrich → Refine → Render → QA → Select → Assemble" in Electric Cyan, with interchangeable "DOMAIN RULES" nodes highlighted in Amber at the Scaffold and QA positions. Pipeline thread line at bottom. 27/60.]
[Speech: Let me make this concrete. Research reports: the scaffold defines section structure, the draft pass generates rough prose, the refine pass injects citations and statistics. Grant proposals: the scaffold encodes funder-specific compliance rules — page limits, required sections, budget templates — and the QA gate validates compliance before the researcher ever submits. Courseware: the scaffold defines learning objectives, the refine pass calibrates difficulty, and contact sheets let the instructor choose between alternative activity designs. Marketing: brand guidelines become the scaffold, and the marketing team gets aesthetic choice through parallel variants. The common topology is identical. Swap the scaffold and the domain-specific QA rules, and the same chassis serves all of them. Now let me give you the practical starting point.]

---

## Slide 35: Try It Yourself — Three Steps to Your First VibeSlide Deck

- **Step 1 — Write Your Idea:** One paragraph in `work/idea.md` — describe your topic, audience, and key claims; this is the only human-authored input the pipeline needs
- **Step 2 — Run the Pipeline:** Four CLI commands execute the full workflow:
  - `python3 -m src.research.cli` → generates `work/research.md` with citation-grounded findings
  - `python3 -m src.outline.cli` → generates `work/outline_36.md` with scaffold and slide-by-slide structure
  - `python3 -m src.style.cli --pick 1,1,1,1` → generates style contact sheets, user selects templates
  - `python3 -m src.compose.cli --copy 4` → renders parallel variants, assembles curated PDF
- **Step 3 — Curate the Output:** Review contact sheets (2 min), pick styles, scan slide variants (15 min), delete inferior copies — your editorial judgment is the final quality filter
- **Total Time Investment:** ~30 minutes of human attention spread across 57 minutes of wall-clock time
- **Total Cost:** Under $5 in API credits for a 60-slide publication-grade deck
- Core insight: The best presentation you've never manually built is one `idea.md` away
[Visual: A terminal window on Deep Space background showing four CLI commands stacked vertically in JetBrains Mono 14pt Electric Cyan. Each command has a small output preview fanning out to the right: research.cli → research document icon, outline.cli → film strip icon, style.cli → contact sheet grid thumbnail, compose.cli → PDF icon with "186 MB" label. The four previews cascade diagonally from top-left to bottom-right, ending with the PDF glowing brightest. A "START HERE" badge points to a minimal `idea.md` file icon at the top-left. Stats at bottom: "~30 min human · < $5 · 60 slides." Pipeline thread line at bottom. 28/60.]
[Speech: You can do this yourself. Step one: write one paragraph in a markdown file. Describe your topic, your audience, your key claims. Step two: run four commands. Research, outline, style, compose. Each one produces a reviewable artifact. Step three: curate. Scan the contact sheets — two minutes. Review the slide variants — fifteen minutes. Delete the copies you don't love. That's it. Thirty minutes of your attention, under five dollars in API costs, and you have a sixty-slide publication-grade deck with custom visuals, verified metrics, and full presenter scripts. The pipeline is open. No proprietary models. No closed infrastructure. The best presentation you've never manually built is one idea.md away. Now let me share what we learned the hard way.]

---

## Slide 36: Lessons Learned — What Broke, What Surprised, What We'd Change

- **What Broke (Signal Red):** Valyu credit limits hit mid-research with no warning — required automatic failover design; early QA gates were too strict, flagging 30%+ of slides and creating a regeneration bottleneck; image generation for data-heavy slides produced hallucinated chart values
- **What Surprised (Amber):** Contact sheet selection was faster than expected — users averaged 30 seconds per template type vs. our estimated 2 minutes; the scaffold's consistency enforcement was the single highest-ROI component; model-swapping produced larger quality jumps than prompt engineering
- **What We'd Change (Signal Green):** Add real-time cost tracking per API call (we only calculated costs post-hoc); implement streaming preview during composition so users don't wait for full render; add a "narrative coherence score" to the scaffold that auto-adjusts section weights based on content density
- **The Honest Assessment:** The pipeline works remarkably well for technical/data-driven decks; it struggles more with narrative-driven presentation decks where emotional pacing matters more than information density
- Core insight: The biggest lesson is that orchestration design — not model selection or prompt engineering — was the lever that moved quality the most
[Visual: Three columns side by side on Deep Space background. Left column: "BROKE" header in Signal Red, with 3 icon+label entries stacked vertically — credit limit icon, bottleneck icon, hallucinated chart icon, each with a brief label in Cool White. Center column: "SURPRISED" header in Amber, with 3 entries — speed icon, scaffold ROI icon, model-swap icon. Right column: "NEXT" header in Signal Green, with 3 entries — cost tracker icon, streaming preview icon, coherence score icon. Each entry uses minimal line-art icons at 24px. The honest retrospective feel is reinforced by a slight tilt/informal angle to each column. Pipeline thread line at bottom. 29/60.]
[Speech: Let me be honest about what didn't work perfectly. Three things broke. Valyu credits hit their limit mid-run with no warning — that's why we built automatic failover. Our early QA gates were too strict, flagging over thirty percent of slides and creating a regeneration bottleneck — we had to tune the thresholds. And image generation for data-heavy slides sometimes hallucinated chart values — those need human verification. Three things surprised us. Contact sheet selection was blazingly fast — thirty seconds per template, not the two minutes we budgeted. The scaffold's consistency enforcement was the single highest-ROI component we built. And swapping models produced bigger quality jumps than any amount of prompt engineering. Three things we'd change: real-time cost tracking, streaming previews during composition, and an automatic narrative coherence score. But the meta-lesson? Orchestration design was the lever that moved quality the most. Not models. Not prompts. Workflow. Let's look at where this goes next.]

---

## Slide 37: The Future Pipeline — Real-Time Collaboration, Voice-Driven Curation, Live Audience Adaptation

- **Real-Time Collaboration:** Multiple users reviewing and curating slide variants simultaneously — conflict resolution through version branches, not file locks; imagine a team of three curating 60 slides in 10 minutes instead of one person in 15
- **Voice-Driven Curation:** "Show me the second variant for slide 23" — "Make the title bolder" — "Swap the cover to a warmer palette" — voice commands replacing mouse clicks during the review phase, leveraging real-time speech-to-action models
- **Live Audience Adaptation:** The deck detects audience engagement signals (gaze tracking, poll responses, Q&A density) during the actual presentation and dynamically reorders or expands slides in real-time — the scaffold's section-weight system makes this architecturally possible
- **Persistent Knowledge Graphs:** Research from one deck enriches future decks in the same domain — citations, verified metrics, and narrative patterns accumulate, reducing cold-start research time
- Core insight: The pipeline's staged architecture makes each of these extensions a module swap, not a redesign — the scaffold absorbs new capabilities without breaking existing ones
[Visual: A forward-looking roadmap ribbon extending from the left edge to the right, rendered in Electric Cyan on Deep Space. Three milestone nodes sit along the ribbon, each showing a concept sketch: Node 1 — "Collaborative Curation" with multiple user avatars around a shared slide grid. Node 2 — "Voice Commands" with a microphone icon and speech waveform connected to slide actions. Node 3 — "Live Adaptation" with a presentation screen connected to audience signal icons (eye, polling bar, chat bubble). The ribbon glows brighter as it moves right, suggesting increasing ambition. A small "MODULE SWAP" annotation connects each node back to the central pipeline diagram via dashed Amber lines. Pipeline thread line at bottom. 30/60.]
[Speech: Where does this go next? Three directions. First, real-time collaboration — multiple people curating slide variants simultaneously. The scaffold's version control makes this architecturally straightforward. Second, voice-driven curation. Instead of clicking through variants, you say "show me the second variant for slide twenty-three" and the system responds. Third — and this is the ambitious one — live audience adaptation. The deck detects engagement signals during the actual presentation and dynamically reorders slides. The scaffold's section-weight system already supports this structurally. And here's the key: none of these extensions require a pipeline redesign. Each one is a module swap. The scaffold absorbs new capabilities without breaking existing ones. Let me bring it all together.]

---

## Slide 38: Key Takeaways — One Paragraph In, Publication-Grade Deck Out

- **Iterate:** Every stage runs at least twice — the first pass explores, the second pass grounds with metrics, citations, and standards; visual stages use parallel generation with human selection instead of agent refinement
- **Orchestrate:** Three commodity tools (Cursor, OpenRouter, Valyu) coordinated by a transparent multi-stage pipeline with inspection windows at every boundary — no proprietary models, no vendor lock-in, no bespoke infrastructure
- **Curate:** Human judgment is the final quality filter at every stage — 28 minutes of editorial decisions transform automated output into presentation-grade artifacts; the pipeline augments taste, it doesn't replace it
- **The Numbers:** $4.73 total cost, 57 minutes wall-clock, 60 slides with custom visuals, verified metrics, and full presenter scripts — a 94% cost reduction vs. traditional approaches
- **The Thesis:** The value of generative AI is realized not in the models themselves, but in the architectures that orchestrate them into reliable, inspectable, human-augmented workflows
- Core insight: VibeSliding proves that one paragraph, two principles, and three tools can produce a deck that no single-shot system — and no individual working alone — could match in under an hour
[Visual: A distilled summary card rendered as a rounded-corner panel with a subtle Electric Cyan border glow on Deep Space background. Three icon-labeled rows stack vertically: Row 1 — loop icon in Electric Cyan + "ITERATE" label + one-line summary. Row 2 — hub icon in Amber + "ORCHESTRATE" label + one-line summary. Row 3 — hand/eye icon in Vivid Purple + "CURATE" label + one-line summary. These three rows echo the twin pillars from Slide 6, now consolidated into a single frame. Below the card: the key stat line "$4.73 · 57 min · 60 slides" in large Inter SemiBold. The heme-thiolate porphyrin ring appears at full (not watermark) opacity behind the card as a callback to the cover, creating narrative closure. Pipeline thread line at bottom. 31/60.]
[Speech: Three words. Iterate: every stage runs twice. The first pass explores, the second pass grounds. For visuals, generate candidates and let the human choose. Orchestrate: three commodity tools, one transparent pipeline, zero proprietary infrastructure. The workflow creates the value, not any individual model. Curate: twenty-eight minutes of human judgment transforms automated output into something you'd proudly present. The numbers show the impact: four dollars and seventy-three cents, fifty-seven minutes, sixty publication-grade slides. Ninety-four percent cheaper than a freelance designer. But the real takeaway isn't the numbers. It's the thesis: the value of generative AI lives in the orchestration layer. Models are commodities. Workflows are moats. And one paragraph is all you need to start.]

---

## Slide 39: Thank You & Q&A

- **Key Thesis:** The value of generative AI lives in the orchestration, not the models
- **Contact:** Xuefeng Cui · Shandong University
- **WeChat:** xfcui0 · **Email:** xfcui.uw@gmail.com
[Visual: Mirrors the cover composition exactly on Deep Space (#0A0F1A) background. The heme-thiolate porphyrin ring emblem is rendered at full luminous scale — slightly larger than the cover version, signaling completion. Electric Cyan glow with Amber accent nodes. "Thank You / Q&A" in Inter Bold 36pt where the title was. A single takeaway sentence "One paragraph in, publication-grade deck out — orchestration is the moat" replaces the subtitle in Inter SemiBold 20pt. Contact details (WeChat: xfcui0, Email: xfcui.uw@gmail.com) arranged as a minimal card in the lower third with Inter Light 18pt. Faint dot grid recedes into background. Visual callback to cover creates narrative closure. No slide number.]
[Speech: Thank you. The pipeline is open, the principles are simple, and one idea.md is all you need. I'd love to hear your questions — about the architecture, the economics, the failures, or where this goes next. Who wants to go first?]

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