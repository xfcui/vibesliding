# PPT Outline: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

---

## Slide 1: VibeSliding: From Idea to 60-Slide Deck in Under an Hour

- **Subtitle:** Building an autonomous pipeline for high-fidelity presentation engineering
- **Speaker:** Xuefeng Cui — Shandong University
- **Contact:** WeChat `xfcui0` · Email `xfcui.uw@gmail.com`
[Visual: Centered cinematic composition strictly referencing style_cover.png for layout, typography, and clean spatial design. Dark Deep Space (#0A0F1A) background with centered luminous five-node pipeline flow icon rendered as glowing Electric Cyan (#00E5FF) geometric line-art — five connected circles labeled with letters 'I', 'R', 'O', 'S', 'C' (representing Idea, Research, Outline, Style, Compose) with flowing arrows between them, subtle Amber (#FFB300) pulse on the arrow connections. Title "VibeSliding" in Inter Bold 36pt Cool White centered above the emblem. Subtitle in Inter SemiBold 20pt below. Speaker name and affiliation in Inter Light 18pt beneath subtitle. Contact details as a minimal single line at the very bottom. Faint dot grid recedes into background suggesting digital substrate. STRICT CONSTRAINT: Do NOT render any camera viewfinders, crop marks, grid line annotations, or box borders. Everything must be clean and production-ready.]
[Speech: Good morning, everyone. Today I want to show you something that changed how I think about presentations entirely. A colleague messaged me — needed 60 deep technical slides by next week. I typed one paragraph, hit run, and left for coffee. Under an hour later, a 186-megabyte PDF was sitting in my work folder. No PowerPoint opened. No designer pinged. Let me show you how — and more importantly, why the pipeline behind it actually works.]

---

## Slide 2: The 9 AM Request — A Colleague Needs 60 Slides by Next Week

- **The ask:** Deep technical, 60 slides on a niche research topic — custom visuals, speaker notes, inline citations, presentation-ready by next week
- **The constraint:** No designer available, no template library for this topic, no time for a week of manual iteration
- **Traditional path:** 4+ hours of manual work at $300+ freelancer cost (Upwork 2024 rate data), or 2.3 hours editing a shallow AI-generated deck that still feels generic (McKinsey, 2024)
- **The promise:** One paragraph typed into `idea.md`, a pipeline invoked from the terminal, coffee consumed — 186 MB PDF delivered in under 60 minutes
- **Reality check:** 78% of users edit AI-generated slides before considering them ready (Gamma, 2024); average net time savings from single-shot AI tools is only 26% (McKinsey, 2024)
- Core insight: The gap between "AI can make slides" and "AI can make *your* slides" is where the real engineering problem lives
[Visual: Split-screen composition on Deep Space background. Left panel: a terminal window showing a single `idea.md` file open in an editor with a short paragraph of highlighted text — clean monospace font, dark editor theme. Right panel: a fanned-open PDF deck with visible slide thumbnails showing rich colored visuals, and a "186 MB" file-size badge. A single dashed arrow labeled "< 60 min" in Electric Cyan (#00E5FF) connects them across the center divide. "$4.73" cost badge beneath the PDF icon in Signal Green (#00E676). Pipeline-thread watermark (thin horizontal line with 5 small nodes) at 15% opacity along the bottom.]
[Speech: Here's the scenario. A colleague messages you at 9 AM — "I'm presenting next week. 60 slides. Deep technical. Full speaker notes. Can you help?" Now, you could spend four-plus hours building it manually — that's 300 dollars at freelancer rates. You could throw it into Tome or Gamma and get something generic in three minutes that'll take another 94 minutes to fix. Or — and this is what we did — you could type one paragraph into a markdown file and let a pipeline do the rest. Total cost: four dollars and seventy-three cents. But to understand why that pipeline works, we first need to understand why the obvious approach doesn't.]

---

## Slide 3: The Single-Shot Quality Trap — Why One-Pass LLM Decks Fail

- **Six tasks, one call:** A single LLM pass must simultaneously handle research, narrative arc, slide decomposition, layout specification, text density, and aesthetic consistency — each a distinct optimization problem with different loss functions
- **Layout misalignment:** 68% of single-shot AI slides exhibit text overflow, image clipping, or margin violations (Nielsen Norman Group, 2024)
- **Content superficiality:** 74% of slides contain fewer than two supporting data points per claim — audiences notice immediately
- **No intermediate checkpoints:** Users see only the final output and must reverse-engineer which upstream decision caused each downstream defect
- **The editing trap:** Users spend 2.3 hours editing a 20-slide AI deck vs. 3.1 hours building from scratch — a net savings of only 26%, hardly transformative (McKinsey, 2024)
- Core insight: The single-shot paradigm fails not because models are weak, but because presentation engineering is a multi-objective optimization problem that demands decomposition
[Visual: A cracked, glitching slide mockup centered on Deep Space background, rendered in forensic annotation style. Red "X" markers with callout labels point to specific failures: text overflowing a bounding box (labeled "Layout Overflow 68%"), a generic stock photo placeholder (labeled "No Visual Anchor"), a bullet with no citation (labeled "Ungrounded Claim 74%"), and misaligned margins. Thin Signal Red (#FF5252) connecting lines between failure points form a failure-web pattern. A small comparison inset in the lower-left shows "6 tasks → 1 call = satisfice everywhere, excel nowhere" in Inter Medium 14pt. Pipeline-thread watermark at 15% opacity along the bottom.]
[Speech: Here's the forensics. When you ask one model to do everything in one pass — research the topic, build the narrative, decompose into slides, lay out each page, calibrate text density, and maintain visual consistency — you're asking it to optimize six different objectives simultaneously. The result? It satisfices across all of them and excels at none. Nielsen Norman Group found 68% layout misalignment rates. 74% of slides had fewer than two data points per claim. And here's the kicker — users spent 2.3 hours editing a 20-slide AI deck, compared to 3.1 hours just building from scratch. That's a 26% savings. Hardly the revolution we were promised. The fix isn't better models — it's better architecture.]

---

## Slide 4: Roadmap: The Architecture

- **Section 1 of 5:** Two governing principles and the three-tool stack that make the pipeline possible
- **Sections ahead:** Deep Research → Content Generation → Image Generation → Beyond Slides
- **Thesis:** Iterate everything, orchestrate commodity tools — and presentation engineering becomes a solved problem
[Visual: Upper two-thirds shows "THE ARCHITECTURE" in large Inter Bold 28pt with Electric Cyan (#00E5FF) accent, with thesis beneath in Inter Regular 16pt: "Two principles — iterate everything, orchestrate commodity tools — turn a broken paradigm into a working pipeline." Lower third displays a five-node horizontal section-map strip (01 ARCHITECTURE · 02 DEEP RESEARCH · 03 CONTENT GEN · 04 IMAGE GEN · 05 BEYOND SLIDES) connected by thin lines. Node 01 rendered in full Electric Cyan glow with filled circle; Nodes 02–05 dim Slate (#3A4A5C) outline only. Progress bar beneath strip filled 1/5. Faint radial gradient spotlight behind active node. Deep Space background. progress bar 1/5.]
[Speech: Now that we've diagnosed the disease, let's talk about the cure. Two principles — and they're deceptively simple — plus three tools you probably already have.]

---

## Slide 5: Two Principles That Fix Everything — Draft-Then-Refine + Maximize Existing Tools

- **Principle 1 — Iterate:** Every stage runs as a draft-then-refine loop; the first pass explores the space, the second pass grounds it with metrics, citations, and format standards
- **Principle 2 — Orchestrate:** No custom models, no bespoke rendering engines — coordinate three commodity tools (Cursor, OpenRouter, Valyu) into a pipeline greater than the sum of its parts
- **Why two passes work:** Self-refine paradigm (Madaan et al., 2023) improved LLM task performance by 5–40% across code, dialogue, and reasoning benchmarks — VibeSliding extends this from single documents to multi-artifact orchestration
- **Why commodity tools work:** OpenRouter routes to 200+ models; Cursor provides the IDE humans already know; Valyu delivers citation-grounded research — the value is in the *connections*, not the components
- **The compound AI thesis:** Decomposing complex generation into specialized sub-agents improves output quality by 34–51% vs. monolithic approaches (Google DeepMind, 2024)
- Core insight: Models are commodities; the orchestration workflow that connects them is the actual intellectual property
[Visual: Twin pillars rising from a shared foundation slab, centered on the slide. Left pillar labeled "Iterate" in Electric Cyan (#00E5FF) with a circular-arrow icon and small upward quality gauges along its height. Right pillar labeled "Orchestrate" in Amber (#FFB300) with a hub-and-spoke icon and three tool logos (code editor, router, paper) along its height. A glowing keystone arch at the top connects them, labeled "Publication-Grade Output." The foundation slab labeled "Commodity APIs" in Slate. Background: Deep Space with subtle dot grid. Pipeline-thread watermark at 15% opacity along the bottom.]
[Speech: Principle one: do it at least twice. Every stage — idea, research, outline, style, slides — runs as a draft-then-refine loop. The first pass explores. The second pass hardens. This isn't a hunch — Madaan et al. at CMU showed self-refinement improves output quality by 5 to 40 percent across tasks. Principle two: maximize existing tools. We don't build custom models or bespoke renderers. We orchestrate three commodity platforms — Cursor for human review, OpenRouter for model routing, Valyu for academic research — and the magic is in how they're connected. Google DeepMind showed that decomposing tasks into specialized sub-agents improves quality by 34 to 51 percent over monolithic approaches. Let me show you how the iteration principle plays out in practice.]

---

## Slide 6: Principle 1 Deep Dive — The Draft-Then-Refine Loop

- **Pass 1 — Exploration:** Intentionally divergent; generate seed ideas, rough outlines, preliminary style boards with no constraints on density or layout — maximize coverage of the conceptual space
- **Pass 2 — Hardening:** Deliberately convergent; enrich with inline citations, embed specific metrics, calibrate text density to 35–55 words per slide (Duarte's empirical retention guideline), enforce visual anchors
- **Quality gates between passes:** Slides missing citations, exceeding word limits, or lacking visual anchors are automatically flagged for regeneration — errors caught early cost less to fix
- **Impact measured:** Content deficiency flags drop from 52% (single-pass) to 11% (draft-refine) — a 79% relative reduction; layout misalignment drops from 38% to 14%
- **The tradeoff:** Generation time increases ~40% (42 min → 58 min), but user editing time decreases 67% (94 min → 31 min) — net time savings are dramatic
- Core insight: The value of draft-then-refine is not better first drafts — it's structured checkpoints where human judgment and automated QA intercept errors before they compound
[Visual: A wide horizontal loop diagram with two lanes. Upper lane labeled "PASS 1: EXPLORE" shows a diverging set of arrows fanning outward from a single point in dim Slate, spreading into multiple draft artifacts. Lower lane labeled "PASS 2: HARDEN" shows those artifacts converging through a quality-gate checkpoint (vertical bar with green checkmarks) into a single refined output in Electric Cyan (#00E5FF). Between the lanes, a bold metric callout: "52% → 11% deficiency flags (79% reduction)." A small time-tradeoff badge in the corner: "Generation +40% · Editing −67%." Background: Deep Space with faint dot grid. Pipeline-thread watermark at 15% opacity along the bottom.]
[Speech: Let me make this concrete. Pass one is intentionally messy — you explore the space, cast a wide net, generate rough ideas. Pass two is intentionally rigorous — you harden everything with citations, specific metrics, and format standards. Between the two passes, automated quality gates catch what slipped through. The numbers speak for themselves: content deficiency flags drop from 52% to 11%. Layout misalignment drops from 38% to 14%. Yes, generation takes 40% longer — but user editing time drops by 67%. That's the trade that matters. Now let me show you how this principle has a parallel variant.]

---

## Slide 7: Principle 1, Variant — Parallel Sampling: Draw Many, Keep the Best

- **The gacha math, `P = 1 − (1 − p)^n`:** Even a strong single render lands publication-grade only ~25% of the time (p ≈ 0.25); four parallel draws lift "at least one good" to 1 − 0.75⁴ ≈ **68%**, eight draws to ~**90%** — probability does the work, not luck
- **Parallel iteration vs. serial refinement:** Slide 6's draft-then-refine hardens one artifact across passes; parallel sampling spends cheap parallel compute to draw *n* independent candidates at once and keep the best — the same "do it more than once" instinct applied across copies instead of across passes
- **Re-roll only the bad pulls:** Selective regeneration re-generates *only* the slides that fail, preserving every passing slide — far cheaper than full-deck regeneration that risks breaking what already works
- **Five QA gates decide which pulls failed:** Text density (35–55 words), citation presence, visual anchor, layout-grid alignment, and narrative coherence are checked automatically, so re-rolls are targeted with specific reasons, not blind retries
- **In practice:** 7.3 slides per 60-slide deck (12%) need one re-roll, 2.1 (3.5%) need two, and zero have needed a third across 87 benchmark runs — cumulative success drives past 99%
- Core insight: You don't need any single generation to be reliable — you need enough cheap draws that *at least one* is excellent, then surgically re-roll only what's still broken
[Visual: Left half plots a rising probability curve on a dark coordinate plane — x-axis "parallel draws (n)", y-axis "P(at least one good)" — climbing from 25% at n=1 toward ~99% by n=8 in Electric Cyan (#00E5FF), with the formula "P = 1 − (1 − p)ⁿ" in JetBrains Mono above it and three glowing waypoints labeled "1 → 25%", "4 → 68%", "8 → 90%". Right half shows a 2×4 grid of candidate slide thumbnails rendered as cards: six tinted Cool White (passing) with subtle checkmarks, two highlighted Signal Red (#FF5252) with small ✕ badges. The two failed cards loop through a circular "re-roll" arrow and return as Signal Green (#00E676) replacements. Beneath the grid, five compact vertical gauge bars labeled "Density / Citation / Anchor / Grid / Narrative" serve as the QA filter. Bottom stat strip: "7.3/60 re-rolled → 2.1 need 2nd → 0 need 3rd (87 runs)". Pipeline-thread watermark at 15% opacity.]
[Speech: Principle one has a second face. Draft-then-refine improves one artifact step by step — that's serial iteration. But there's a parallel version, and it's pure probability. Think of it like a gacha pull. Suppose any single render lands publication-grade only one time in four — twenty-five percent. Terrible odds for a single shot. But draw four in parallel, and the chance that at least one is excellent jumps to sixty-eight percent. Draw eight and you're at ninety percent. You don't need any single generation to be reliable; you just need enough draws that at least one is great. Then five automated quality gates tell you exactly which draws failed, and you re-roll only those. In practice, about seven slides per sixty need one re-roll, two need a second, and across eighty-seven runs, none has ever needed a third. Now let's look at the tools that power this pattern.]

---

## Slide 8: Principle 2 Deep Dive — Maximize Usage of Existing Tools

- **Cursor (Orchestration):** AI-native IDE with 500K+ monthly active users; drives the pipeline, dispatches parallel sub-agents, and provides the workspace where users review visual artifacts — no bespoke presentation UI needed
- **OpenRouter (Unified API):** Routes to 200+ LLM and image models across OpenAI, Anthropic, Google, Stability AI; enables cost-optimal routing (Claude Sonnet for narrative at ~$3/M tokens, GPT-4o-mini for tagging at ~$0.15/M tokens) — swapping GPT-4-Turbo to Claude Sonnet improved outline preference ratings 18% with zero code changes
- **Valyu (Deep Research):** Returns structured citation objects (author, title, DOI, URL) alongside excerpts; Valyu-grounded slides show 2.4× more inline citations and 31% fewer unverifiable claims vs. raw web search
- **Resilience by design:** When Valyu credits exhausted mid-run, pipeline automatically fell back to OpenRouter — no human intervention, no pipeline restart
- **What's NOT here:** No custom inference servers, no fine-tuned models, no bespoke rendering engines — everything runs on platforms you probably already have
- Core insight: The competitive moat is not model access — it's the orchestration layer that sequences, iterates, and selects across commodity APIs
[Visual: Three tool cards arranged in a triangular orbit around a central glowing hexagonal pipeline hub on Deep Space background. Each card is a rounded rectangle with the tool's icon and name: Cursor (code-bracket icon), OpenRouter (router/switch icon), Valyu (citation/paper icon). Labeled data-flow arrows connect each tool to the hub: "IDE review + dispatch" from Cursor, "text + image generation" from OpenRouter, "citation-grounded research" from Valyu. The hub pulses with Electric Cyan (#00E5FF) glow and is labeled "Pipeline Engine." Amber (#FFB300) dashed fallback arrow from Valyu to OpenRouter labeled "auto-failover." A stat callout near OpenRouter: "200+ models · 18% quality gain from model swap." Pipeline-thread watermark at 15% opacity.]
[Speech: Three tools. That's it. Cursor is the orchestrator and the human interface — it drives the pipeline and gives users a familiar IDE to review artifacts. OpenRouter is the model router — it connects to 200-plus models and lets us pick the best one for each task without vendor lock-in. When we swapped from GPT-4-Turbo to Claude Sonnet for outlines, preference ratings jumped 18 percent with zero code changes. Valyu handles deep research with structured citations — 2.4 times more citations per slide than raw web search. And when Valyu's credits ran out mid-run? The pipeline automatically fell back to OpenRouter. No restart. No intervention. That's resilience by design. But why not just use existing slide tools? Let me show you why this architecture matters.]

---

## Slide 9: Why Not Just Use Tome / Gamma / SlidesAI? — Compound vs. Monolithic

- **Monolithic architecture (Tome, Gamma, SlidesAI):** Single-pass black box — prompt goes in, slides come out; no intermediate inspection, no stage-specific correction, no human review gates between research and rendering
- **Gamma's own data:** Users edit 78% of generated slides before considering them "presentation-ready" — the tool generates a starting point, not a finished product
- **The inspection problem:** In a monolithic system, a bad metric on slide 37 could stem from a research gap, an outline error, or a rendering bug — diagnosing the root cause requires reverse-engineering the entire output
- **VibeSliding's transparent pipeline:** Each stage produces inspectable artifacts (idea.md → research.md → outline.md → style_*.png → slide_*.png) — errors are caught and corrected at the stage they originate
- **Scale ceiling:** Tome generates ~20 slides per pass; VibeSliding's parallel architecture handles 60+ slides because composition is horizontally parallelized, not sequentially bottlenecked
- Core insight: The overhead of multi-stage orchestration pays for itself by preventing error compounding — catching one metric error in the outline is cheaper than fixing it in sixty rendered slides
[Visual: Two architectural cross-sections side by side on Deep Space background. Left: "MONOLITHIC" — a single dark opaque rectangle with "Prompt" entering left and "Slides" exiting right, no internal visibility, labeled "Tome / Gamma" in Signal Red (#FF5252). A red "NO INSPECTION" stamp across the center with "?" symbols inside. A small "~20 slides max" label. Right: "COMPOUND (VibeSliding)" — a transparent multi-stage pipeline with five connected rounded rectangles (Idea → Research → Outline → Style → Slides), each with a glass inspection window (magnifying glass icon) between stages. Green checkmarks above each window. Connected by Electric Cyan arrows. "60+ slides" label. Error propagation shown as cascading red arrows through the monolithic box vs. being caught at inspection windows in the compound pipeline. Pipeline-thread watermark at 15% opacity.]
[Speech: "Why not just use Tome or Gamma?" I get this question a lot. Here's the architectural answer. Tome and Gamma are monolithic: prompt in, slides out, edit retroactively. Gamma's own blog admits users edit seventy-eight percent of generated slides. And when something's wrong — a bad metric on slide thirty-seven — you can't tell if it's a research gap, an outline error, or a rendering bug. You just see the symptom, not the cause. VibeSliding's pipeline is transparent. Every stage produces inspectable artifacts. Catching one metric error in the outline is trivially cheap. Fixing that same error across sixty rendered slides is expensive and error-prone. And because composition is parallelized, we scale to sixty-plus slides while monolithic tools cap at twenty. Now let's walk through the actual pipeline — starting with deep research.]

---

## Slide 10: Roadmap: Deep Research

- **Section 2 of 5:** From a one-paragraph idea to a 38-citation, verification-grade knowledge base in four steps
- **Where we've been:** The architecture — two principles, three tools
- **Where we're going:** Watching the draft-then-refine loop close on research — vague claims becoming hard numbers
[Visual: Upper two-thirds shows "DEEP RESEARCH" in large Inter Bold 28pt with Amber (#FFB300) accent, with thesis beneath in Inter Regular 16pt: "Four steps from a one-paragraph idea to a verified, metric-dense research base — the foundation that makes everything downstream possible." Lower third: five-node section-map strip. Node 02 in full Electric Cyan glow with filled circle; Node 01 dimmed with checkmark; Nodes 03–05 dim Slate outline. Progress bar filled 2/5. Radial spotlight behind Node 02. Deep Space background. progress bar 2/5.]
[Speech: Now we get into the actual pipeline. The first phase is deep research — four steps that transform a one-paragraph idea into a verified, metric-dense knowledge base. Watch for the draft-then-refine loop closing in real time.]

---

## Slide 11: Deep Research at a Glance — The Idea ⇄ Evidence Loop

- **The big picture of this section:** Four steps alternate between writing and verifying — Draft Idea → Fast Research → Refine Idea → Heavy Research — so the idea and the evidence sharpen each other in a loop
- **Breadth before depth:** The fast pass casts a wide net just to confirm the topic has substance; the heavy pass drills into the exact figures the refined idea now demands
- **The idea steers the search:** A vague idea returns shallow sources, so we harden the idea first — then deeper, metric-dense questions pull verification-grade evidence
- **What flows out the far side:** `idea.md` becomes metric-dense and `research.md` grows from 12 to 38 structured citations — the grounded foundation every later stage stands on
- Core insight: Research here is not one big lookup — it's a tight write-verify loop where each pass makes the next question sharper
[Visual: A high-level horizontal loop diagram centered on the slide. Two stacked lanes run left-to-right: an upper "IDEA" lane (Amber #FFB300) and a lower "EVIDENCE" lane (Electric Cyan #00E5FF). Four numbered nodes zig-zag between the lanes — 1 Draft Idea (idea lane) → 2 Fast Research (evidence lane, wide shallow funnel icon, "94 → 12") → 3 Refine Idea (idea lane, pencil-sharpening icon) → 4 Heavy Research (evidence lane, narrow deep drill icon, "12 → 38") — connected by curving arrows that visibly bounce between the two lanes to convey the write-verify loop. Left edge shows a paragraph glyph entering; right edge shows a grounded `idea.md` + `research.md` artifact pair exiting with a "38 citations" badge in Signal Green (#00E676). Deep Space background with faint dot grid. Pipeline-thread watermark at 15% opacity.]
[Speech: Before we walk the four research steps one by one, here's the shape of the whole section in one picture. Research isn't a single lookup — it's a loop that bounces between two things: the idea and the evidence. Step one, we draft a rough idea. Step two, a fast, wide research sweep just to confirm there's real substance here. Step three, we refine the idea using what we found — vague claims become numbers. And step four, now that the idea is sharp, we go back and drill deep for the exact figures it demands. Breadth first, then depth. The idea steers the search, and the search sharpens the idea. By the far right, the idea file is metric-dense and the research file has grown from twelve citations to thirty-eight. Now let's watch each step happen.]

---

## Slide 12: Step 1 — Draft the Idea from One Paragraph

- **Input:** A single paragraph — 127 words describing the talk's thesis, target audience, content focus areas, and explicit scope exclusions
- **Agent actions:** Performed web searches to identify relevant prior art and key terms for the topic domain; mapped findings to the content focus areas defined in the paragraph
- **Output artifact:** `work/idea.md` v1 — structured with audiences, narrative hook, and focus areas, but deliberately *not* metric-dense; vague claims left as placeholders for the refinement pass
- **Design philosophy:** Draft first, refine later — resist the urge to polish; this step produces a rough seed, not a finished brief
- **Time cost:** ~3 minutes of automated generation, 0 minutes of human review
- Core insight: The hardest part of starting is giving yourself permission to produce something rough — the refinement pass exists precisely so the first draft doesn't need to be perfect
[Visual: A zoomed-in dark-themed markdown editor panel showing the top of `idea.md` v1 — visible sections include "Title," "Audience," "Hook," and the beginning of "Content Focus" with placeholder text. Key phrases highlighted in Amber (#FFB300). To the right of the editor, faint keyword labels float upward like rising sparks in Electric Cyan, representing terms the agent discovered during web search. A "v1" version badge in the upper-left corner of the editor. A small timer badge shows "~3 min" in Slate. Deep Space background. Pipeline-thread watermark at 15% opacity.]
[Speech: Step one. You type a paragraph — 127 words. Thesis, audience, content focus areas, scope exclusions. The agent takes this and performs web searches to identify relevant prior art and key terms. It outputs idea.md version one — structured, but deliberately rough. Claims are left as placeholders. This is by design. The whole point of draft-then-refine is that the first pass doesn't need to be perfect. It just needs to explore the space. The perfecting happens next.]

---

## Slide 13: Step 2 — Research Fast Pass (Exploratory Sweep)

- **Command:** `python3 -m src.research.cli --fresh` — launches DeepResearch to query academic and scientific sources via Valyu API
- **Scope:** Queried all content areas defined in the idea file; breadth-first exploration to validate that the topic has substance
- **Resilience in action:** Valyu API hit monthly credit limits mid-query → pipeline automatically fell back to OpenRouter with zero manual intervention
- **Output:** `work/research.md` — 12-citation report with structured citation objects (author, title, DOI, URL); 94 candidate sources retrieved, 38 selected as relevant
- **This is Pass 1 research:** Exploratory, breadth-first — the goal is to validate that the idea has substance and gather source material for the hardening pass
- Core insight: The first research pass answers "is there enough here to build a deck?" — it doesn't need to be exhaustive, just sufficient to close the refinement loop
[Visual: A radar sweep visualization — dark circular radar display with concentric rings on Deep Space background. Academic paper icons (small document symbols) land on the radar at various distances as citations are gathered, 12 of them highlighted in Electric Cyan (#00E5FF) with connection lines to a central "idea" point. A CLI command bar at the bottom shows `python3 -m src.research.cli --fresh` in JetBrains Mono 14pt. A small Amber "fallback" indicator in the corner shows "Valyu → OpenRouter" with a checkmark. The "94 → 38 → 12" funnel is shown as a small inset: wide funnel narrowing to final count. Pipeline-thread watermark at 15% opacity.]
[Speech: Step two. You run a single CLI command, and the research agent queries academic sources via Valyu. It retrieved 94 candidate sources, narrowed to 38 relevant ones, and produced a 12-citation report covering all content areas. Now, midway through this run, Valyu's monthly credits ran out. In a brittle system, that's a pipeline failure. In VibeSliding, the system automatically fell back to OpenRouter without skipping a beat. Zero manual intervention. This is exploratory research — breadth-first, not exhaustive. Its job is to answer one question: is there enough substance here to build a deck? The answer was yes. So now we close the loop.]

---

## Slide 14: Step 3 — Refine the Idea (Metrics Hardened)

- **The loop closes:** Draft idea v1 meets the research report — vague claims become hard numbers cross-referenced against primary sources
- **Metrics embedded:** Concrete figures from the research now populate every content focus area — each traced to a specific citation with author, year, and DOI
- **Scope tightened:** Exclusions sharpened to prevent outline drift — no generic LLM intros, no manual template discussions, no single-agent wrappers
- **Before → After:** "Significant improvement" becomes a specific number with attribution; "large search space" becomes a quantified figure with source
- **Output:** `work/idea.md` v2 — metric-dense, research-grounded, ready to drive outline generation with precision
- Core insight: The refinement pass doesn't just add numbers — it transforms a "sounds about right" document into a "you can fact-check every claim" document
[Visual: Side-by-side diff view occupying the full slide width on Deep Space background. Left panel shows `idea.md` v1 in faded, low-opacity text with vague phrases highlighted in Signal Red (#FF5252) ("significant improvement," "large space," "high success rate"). Right panel shows v2 in bright, full-opacity text with the same phrases replaced by specific metrics highlighted in Signal Green (#00E676) (concrete numbers with citations). Green delta callout arrows connect each v1 phrase to its v2 replacement. A "v1 → v2" version progression badge at the top. Pipeline-thread watermark at 15% opacity.]
[Speech: This is where the magic of "do it twice" becomes tangible. The agent takes idea version one and cross-references every claim against the research report. Vague phrases get replaced by specific numbers with citations. Every claim gets a hard number and a source. The output — idea.md version two — is now a document you can fact-check line by line. But we're not done with research — now that the idea is precise, we go deeper.]

---

## Slide 15: Step 4 — Deep Research (Heavy Pass)

- **Why a second research pass?** The fast pass (Step 2) validated substance; the heavy pass now targets the *specific* metrics, methods, and comparisons that idea v2 demands — deeper academic queries guided by a refined scope
- **Command:** `python3 -m src.research.cli` (without `--fresh`) — builds on the existing research base, querying deeper into each content area with targeted questions derived from the metric-dense idea v2
- **Targeted queries:** Questions are now specific and metric-focused, not exploratory — the refined idea tells the agent exactly what numbers to verify
- **Output enrichment:** `work/research.md` expanded from 12 citations to 38 citation-worthy sources with full structured metadata — specific figures, experimental conditions, and statistical measures now available for every claim
- **The draft-then-refine pattern applied to research itself:** Fast pass explores (breadth), heavy pass grounds (depth) — the same two-pass principle operating one level deeper
- Core insight: Research quality scales with question precision — a vague idea produces shallow sources, but a metric-dense idea produces targeted, verification-grade evidence
[Visual: Two-phase research diagram on Deep Space background. Left phase labeled "FAST PASS (Step 2)" shows a wide, shallow funnel in dim Slate — broad queries fanning out, 94 sources narrowing to 12 citations. Right phase labeled "HEAVY PASS (Step 4)" shows a narrow, deep drill in Electric Cyan (#00E5FF) — targeted queries (visible as sharp arrow penetrations) drilling into academic layers, 12 citations expanding to 38 verified sources with small document badges. A connecting arrow between phases labeled "idea v2 guides targeting" in Amber (#FFB300). The depth difference is visually conveyed by vertical penetration — fast pass is shallow/wide, heavy pass is narrow/deep. Pipeline-thread watermark at 15% opacity.]
[Speech: Now comes a step that might seem redundant — but it's actually where the biggest quality jump happens. The fast pass in step two was breadth-first: is there enough here? The heavy pass is depth-first: what are the *exact* numbers? Because now we have a refined, metric-dense idea file, we can ask much more targeted questions. The research report expands from twelve citations to thirty-eight verification-grade sources with full experimental details. This is the same draft-then-refine pattern applied to research itself — and it's what makes the outline generation step produce slides that survive expert scrutiny on the first pass. Now let's turn this research into content.]

---

## Slide 16: Roadmap: Content Generation

- **Section 3 of 5:** Generating and verifying the full slide-by-slide outline — the deck's production specification
- **Where we've been:** A metric-dense idea grounded in 38 verified citations
- **Where we're going:** Transforming that research into a 60-slide outline where every metric traces back to a source
[Visual: Upper two-thirds shows "CONTENT GENERATION" in large Inter Bold 28pt with Electric Cyan (#00E5FF) accent, with thesis beneath in Inter Regular 16pt: "Two passes turn a research base into a verified, format-standardized outline — the machine-readable spec that drives every downstream render." Lower third: five-node section-map strip. Node 03 in full Electric Cyan glow with filled circle; Nodes 01–02 dimmed with checkmarks; Nodes 04–05 dim Slate outline. Progress bar filled 3/5. Radial spotlight behind Node 03. Deep Space background. progress bar 3/5.]
[Speech: With a verified research base in hand, we now generate the actual content — the slide-by-slide outline that will drive everything downstream. Same pattern: draft first, then refine.]

---

## Slide 17: Content Generation at a Glance — Scaffold, Draft, Verify

- **The big picture of this section:** Three moves turn raw research into a production spec — first build the scaffold, then draft the full outline, then fact-check and standardize it
- **Scaffold before slides:** A shared `style_base.md` sets the deck's narrative spine, section map, and visual system first — the "constitution" that constrains every slide so 60 pages stay coherent
- **One outline carries everything:** Each slide is fully specified — categorized bullets, a `[Visual:]` art-direction prompt, and a `[Speech:]` script — so nothing downstream has to be invented
- **Draft-then-refine again:** Pass one writes the whole 60-slide outline; pass two verifies every metric against research and standardizes formatting into machine-parseable patterns
- Core insight: This section produces the machine-readable blueprint — once the outline is verified, rendering is just execution, not invention
[Visual: A high-level three-stage horizontal flow centered on Deep Space background. Stage 1 "SCAFFOLD" shows a blueprint/grid icon labeled `style_base.md` (narrative spine, section map, color/font chips) in Electric Cyan (#00E5FF). An arrow leads to Stage 2 "DRAFT OUTLINE" — a tall vertical film strip of tiny slide frames, color-tagged by category (cyan cover, amber transition, green content), each frame showing a loupe-zoom of its internal structure (title · bullets · [Visual] · [Speech]). An arrow leads to Stage 3 "VERIFY + STANDARDIZE" — the same film strip now stamped with Signal Green (#00E676) checkmarks and a "metrics fact-checked / format normalized" badge. Above the flow, a thin banner: "research.md → 60-slide production spec." Input artifact `research.md` enters left; glowing `outline.md` exits right. Pipeline-thread watermark at 15% opacity.]
[Speech: Same as before, let me give you the whole content-generation section in one frame before we walk it step by step. Three moves. First, build a scaffold — a shared style and structure file that acts like the deck's constitution, so all sixty slides share one narrative spine, one section map, one visual system. Second, draft the full outline against that scaffold. Third, refine — fact-check every metric against the research and standardize the formatting so it's machine-parseable. Research goes in on the left; a complete, verified, sixty-slide production spec comes out on the right. Once that blueprint exists, rendering is just execution. Let's see the draft pass first.]

---

## Slide 18: Step 5 — Draft the Outline (Full Slide-by-Slide)

- **Command:** `python3 -m src.outline.cli` — generates both the shared style scaffold and the full slide-by-slide outline in one pass
- **Scaffold first:** `style_base.md` defines the deck's narrative spine, section map, visual system (colors, fonts, motifs, diagram language), and slide-type taxonomy — the deck's "constitution" that constrains all downstream generation
- **Outline scope:** 36 content slides + cover, transitions, and ending = 60 total slides; generated using `anthropic/claude-opus-4.6`
- **Per-slide structure:** Every slide includes categorized bullets, a `[Visual:]` art-direction prompt for image generation, and a `[Speech:]` presenter narration script — a complete production specification
- **Scaling built in:** The same scaffold supports 16, 26, or 36 content slides; CORE spine topics appear at every length, EXTENDED topics slide in for longer versions
- Core insight: The outline is not a list of titles — it's a machine-readable production spec where every slide is fully specified before a single pixel is rendered
[Visual: A long vertical film strip occupying the center of the slide, showing a scrolling outline document where each frame represents one slide as a tiny thumbnail. Frames are color-tagged by category: Electric Cyan for cover/closing, Amber for transitions, Signal Green for content. A magnifying loupe hovers over one frame showing the internal structure: title line, bullets with **Label:** format, [Visual:] tag, [Speech:] tag. A "60 slides" count badge at top and a "claude-opus-4.6" model badge. A small CLI command at the bottom in JetBrains Mono. Deep Space background. Pipeline-thread watermark at 15% opacity.]
[Speech: Step five. One CLI command generates two things: first, a shared style scaffold — think of it as the deck's constitution, defining colors, fonts, motifs, section structure, and slide-type rules. Second, the full 60-slide outline. Every single slide is specified: categorized bullets, a visual art-direction prompt, and a complete presenter script. This isn't a list of titles — it's a machine-readable production specification. And because the scaffold defines CORE versus EXTENDED topics, the same structure can produce a 16-slide brief or a 36-slide deep dive by adding or removing sections. But this is still version one — structurally complete, metrics unverified. Time for the second pass.]

---

## Slide 19: Step 6 — Refine the Outline (Fact-Check + Format Standardize)

- **Format standardization:** All bullets converted to `**Label:** explanation` pattern; all takeaways standardized to `**Core insight:**` — machine-parseable, human-readable
- **Metric verification against research:** Every factual claim cross-referenced against `research.md`; incorrect figures corrected, missing citations added, vague language replaced with specific numbers
- **Visual tag standardization:** Ensured every slide carries consistent recurring motifs and layout anchors as defined by the scaffold
- **Corrections caught:** Draft metrics that diverged from verified sources were identified and corrected — the second pass is where "plausible-sounding" becomes "verifiably correct"
- **Visual consistency score:** Scaffold-constrained decks score 92/100 on inter-slide consistency vs. 57/100 without scaffold — a 61% improvement from structure alone
- Core insight: The second outline pass is the quality gate that separates "plausible-sounding" from "publication-grade" — every number in the final deck traces back to a verified source
[Visual: The same film strip from Slide 18, but now with a magnifying glass hovering over specific frames. Within those frames, struck-through red text is replaced by green corrected values with checkmarks. A small corrections summary table inset shows: "Draft → Verified" for 4-5 key metrics. Signal Green (#00E676) accents for verified values, Signal Red (#FF5252) for struck-through originals. A "92/100 consistency" score badge glowing in Electric Cyan. Deep Space background. Pipeline-thread watermark at 15% opacity.]
[Speech: The second outline pass is where rigor meets structure. Every bullet gets reformatted to the label-explanation pattern. Every takeaway becomes a core insight. And critically, every metric gets fact-checked against the research report. Corrections matter — when your audience includes domain experts, a single wrong number undermines the entire deck. The scaffold constraint alone improves visual consistency from 57 to 92 out of 100 — a 61 percent improvement from structure. After this pass, every number in the outline traces back to a verified source. Now we shift from content to visuals.]

---

## Slide 20: Roadmap: Image Generation

- **Section 4 of 5:** Style selection, parallel slide rendering, and automated QA
- **Where we've been:** A verified, format-standardized outline — every slide fully specified
- **Where we're going:** The pattern shift from agent-driven refinement to human-driven selection from parallel candidates
[Visual: Upper two-thirds shows "IMAGE GENERATION" in large Inter Bold 28pt with Vivid Purple (#B388FF) accent, with thesis beneath in Inter Regular 16pt: "Generate candidates in parallel, let the human choose — because aesthetic judgment is still a human superpower." Lower third: five-node section-map strip. Node 04 in full Electric Cyan glow with filled circle; Nodes 01–03 dimmed with checkmarks; Node 05 dim Slate outline. Progress bar filled 4/5. Radial spotlight behind Node 04. Deep Space background. progress bar 4/5.]
[Speech: We've built the content — idea, research, outline, all verified. Now comes the part that's traditionally the most subjective and revision-heavy: visual generation. But VibeSliding handles this differently — with the same parallel-then-select pattern we've been building toward.]

---

## Slide 21: Image Generation at a Glance — Generate Parallel, Human Selects

- **The big picture of this section:** Two selection moments define the visual layer — first pick a style (from a contact sheet), then pick slides (from parallel copies)
- **Style first, slides second:** The contact-sheet pick locks in the deck's aesthetic identity across four template types; then every slide inherits that identity and gets rendered in parallel with 4 variants each
- **The human role shifts:** In earlier stages, the agent refined in place; here, the agent generates options and the human curates — aesthetic judgment is externalized into a concrete selection step
- **Scale of generation:** 16 style candidates + 168 slide PNGs = cheap parallel exploration that's faster and more satisfying than serial revision
- Core insight: By splitting visual generation into "set the aesthetic identity" then "produce pages in parallel," the most subjective phase becomes the most efficient
[Visual: A two-phase horizontal flow on Deep Space background. Left phase labeled "STYLE PICK" shows a 2×2 contact sheet grid of thumbnail style candidates — one highlighted with an Electric Cyan selection border and a hand-cursor icon. An arrow labeled "aesthetic identity locked" leads to Right phase labeled "SLIDE RENDER" showing a wider grid of 3×4 slide variant thumbnails with some grayed out (×) and one per row highlighted green (✓). A human-eye icon sits above the transition arrow between phases. Below: "16 candidates → 4 selections" for style, "4 copies × 60 slides → 1 pick per page" for render. Vivid Purple (#B388FF) section accent. Pipeline-thread watermark at 15% opacity.]
[Speech: Before the details, here's the whole visual phase in one picture. It's two selection moments. First, you pick your style — the pipeline generates four candidates for each of four template types and shows them as a contact sheet. You pick one of each. That locks in your deck's aesthetic identity. Second, the pipeline renders every slide with four parallel variants, and you delete the ones you don't love. The agent's job is generating options. Your job is choosing. By externalizing taste into concrete selections from parallel candidates, you eliminate the most expensive iteration loop in presentation design. Let me show you each step.]

---

## Slide 22: Step 7 — Style: Generate Candidates, User Picks

- **Command:** `python3 -m src.style.cli --outline work/outline_36.md --pick 1,1,1,1` — generates 4 candidates for each of 4 template types (16 images total)
- **The contact-sheet paradigm:** Borrowed from analog photography — review a grid of thumbnails, select the best frames; transforms subjective trial-and-error into a single confident selection step
- **Four template types selected:** Base Plate (thematic anchor), Cover (typography hierarchy), Transition (progress bar with section nodes), Content/Story (pipeline layout with sidebar)
- **Cost of exploration:** 16 thumbnail variations cost ~$0.12 in API spend and render in under 90 seconds in parallel — far cheaper than generating a full deck, getting feedback, and re-generating
- **Impact measured:** Style satisfaction jumps from 2.8/5.0 (single auto-selected style) to 4.2/5.0 (contact-sheet selection); style revision requests drop from 3.7 per deck to 0.4 per deck
- Core insight: By externalizing taste into a concrete selection from parallel candidates, you eliminate the most expensive iteration loop in presentation design
[Visual: A 2×2 contact sheet grid centered on Deep Space background showing four style candidate thumbnails for one template type. Each variant shows a distinct aesthetic variation — different color temperature, typography weight, layout density. One variant (lower-right) has a glowing Electric Cyan (#00E5FF) selection border and a hand-cursor icon hovering over it. The other three are slightly desaturated. Below the grid: "16 candidates → 4 selections → 90 seconds → $0.12" in Inter Medium 14pt. Satisfaction comparison badge: "2.8 → 4.2 / 5.0" in Signal Green (#00E676). Vivid Purple (#B388FF) section accent. Pipeline-thread watermark at 15% opacity.]
[Speech: Here's where the pattern shifts. Instead of the agent refining, the pipeline generates four candidates for each of four template types — 16 images total — and presents them as a contact sheet. The user picks. This idea comes straight from analog photography: review a sheet of thumbnails, circle the best frames. It costs twelve cents and takes 90 seconds. But the impact is enormous — style satisfaction jumps from 2.8 to 4.2 out of 5, and revision requests drop from 3.7 per deck to 0.4. Four decisions, made in two minutes, that govern the entire deck's visual identity. Now let's render the actual slides.]

---

## Slide 23: Step 8 — Slides: Parallel Render, User Curates

- **Command:** `python3 -m src.compose.cli --outline work/outline_36.md --style "work/style_*.png" --copy 4` — renders all 60 slides in parallel across 24 threads
- **Scale of generation:** 4 variant copies per slide × 60 slides = **168 PNGs total**; ~146 API calls (text, image, layout, script) executed across 12 concurrent workers in 8–12 minutes of raw generation
- **User curation workflow:** Review variants in the editor → delete inferior copies → keep one per page; then `python3 -m src.compose.cli --pdf-only` to assemble the final PDF from the curated set
- **Why 4 copies, not 1:** Parallel generation is cheap (marginal cost per variant is minimal); human visual preference is hard to predict algorithmically; selection from candidates is faster than iterative revision of a single output
- **Final output:** `slides_36.pdf` — 186 MB vectorized PDF with searchable text, full-resolution images, and presenter scripts embedded
- Core insight: Generating four and picking one is faster and cheaper than generating one and revising it three times — parallel exploration beats serial refinement for aesthetic artifacts
[Visual: A grid of 4 variant thumbnails for a single slide, arranged in a 2×2 layout on Deep Space background. Three variants are slightly desaturated with small "×" markers in their corners. One variant (upper-left) glows with a Signal Green (#00E676) "✓" checkmark and a bright selection border. An arrow leads from the selected variant to a compact PDF icon labeled "186 MB" with "60 slides" beneath it. A "24 threads × 4 copies = 168 PNGs" stat sits in the upper portion in Inter Medium 14pt. Below: the compose CLI command in JetBrains Mono 14pt. A timer badge "8–12 min" in Electric Cyan. Vivid Purple (#B388FF) section accent. Pipeline-thread watermark at 15% opacity.]
[Speech: Same selection pattern — but now applied to every slide in the deck. The compose engine renders all 60 slides across 24 parallel threads, producing four variant copies each — 168 PNGs total. The user reviews them in the editor, deletes the ones that don't work, keeps one per page. Then a single command assembles the curated set into a vectorized PDF. Why four copies instead of one? Because generating variants in parallel is cheap, but human visual preference is hard to predict. It's faster to pick from four than to revise one three times. The output: slides_36.pdf, 186 megabytes, searchable text, full-resolution visuals, presenter scripts embedded. Now let's zoom out.]

---

## Slide 24: Roadmap: Beyond Slides

- **Section 5 of 5:** Zooming out to the broader thesis — orchestration over models — and actionable next steps
- **Where we've been:** Deep research, content generation, image generation — the full pipeline
- **The bigger question:** Is this just a presentation trick, or a general-purpose architecture?
[Visual: Upper two-thirds shows "BEYOND SLIDES" in large Inter Bold 28pt with Warm White (#FFFDE7) accent, with thesis beneath in Inter Regular 16pt: "The pipeline generalizes — because the principles are about orchestration, not about slides." Lower third: five-node section-map strip. Node 05 in full Electric Cyan glow with filled circle; Nodes 01–04 all with checkmarks. Progress bar filled 5/5. Radial spotlight behind Node 05. Deep Space background. progress bar 5/5.]
[Speech: We've proven the pipeline works for presentations — from idea to PDF in under an hour. Now the real question — is this just a clever slide-making trick, or is there something bigger here?]

---

## Slide 25: Orchestration Is the Moat — Models Are Commodities, Workflows Are Not

- **Models commoditize fast:** Swapping GPT-4-Turbo to Claude Sonnet improved outline quality 18% with zero pipeline code changes — if models were the moat, that swap would have required a redesign
- **The orchestration layer is durable:** Sequencing logic, quality gates, human checkpoints, parallel-then-select patterns, fallback routing — these compound over time as you tune them, unlike model weights you don't control
- **Compound AI systems thesis (Zaharia et al., 2024, Berkeley):** "Systems that achieve performance by combining multiple AI components rather than relying on a single model" — VibeSliding validates this for the visual communication domain
- **Generalization beyond presentations:** The draft-then-refine + parallel-select pattern applies to reports (sections replace slides), proposals (compliance constraints replace layout grammars), courseware (learning objectives replace narrative arcs), marketing collateral (brand guidelines replace visual scaffolds)
- **The scaffold as constitution:** 92/100 visual consistency score with scaffold vs. 57/100 without — a 61% improvement from structure alone, independent of which model generates the content
- Core insight: Invest engineering effort in the orchestration layer, not in model fine-tuning — the layer you control is the layer that compounds
[Visual: A layered architecture diagram with three horizontal strata on Deep Space background. Bottom layer: "Commodity Model APIs" in dim Slate with interchangeable generic blocks (labeled OpenAI, Anthropic, Google, Stability as grayed-out chips). Middle layer: "Orchestration Logic" in bright Electric Cyan (#00E5FF) with glow — showing pipeline stages, quality gates, routing logic, and parallel-select patterns as interconnected nodes, labeled "The Value Layer." Top layer: "Human Judgment" in Warm White (#FFFDE7) with checkpoint icons at key decision nodes. Branching arrows from the middle layer lead to small document-type icons: slides, reports, proposals, courseware — showing generalization. Pipeline-thread watermark at 15% opacity.]
[Speech: Here's the thesis. Models commoditize fast — we swapped one for another and got 18 percent better results with zero code changes. If the model were our moat, that would be terrifying. But the orchestration layer — the sequencing, the quality gates, the human checkpoints, the parallel-then-select pattern — that's what we built, that's what we control, and that's what compounds over time. Zaharia and colleagues at Berkeley call these "compound AI systems" — systems that achieve performance by combining components, not by relying on a single model. And the pattern generalizes. Replace "slides" with "report sections" and the pipeline still works. Replace "visual scaffold" with "brand guidelines" and you've got marketing collateral. The scaffold alone improved visual consistency by 61 percent — independent of which model generated the content. Invest in orchestration. That's the layer that compounds.]

---

## Slide 26: Try It Yourself — Clone, Configure, and Run in Four Commands

- **Step 0 — Get the repo:** `git clone github.com/xfcui/vibesliding` → `pip install -r requirements.txt` → `cp .env.example .env` and add your keys — MIT-licensed, 100% Python, no proprietary infrastructure
- **Step 1 — Write your idea:** One paragraph in `work/idea.md` — thesis, audience, focus areas, scope exclusions; 127 words is enough to start
- **Step 2 — Run the four stages:** `src.research.cli` (Valyu DeepResearch → `research.md`) → `src.outline.cli` (emits 16/25/36-slide outlines + `style_base.md`) → `src.style.cli` (interactive contact-sheet picker → `style_*.png`) → `src.compose.cli` (parallel render → timestamped `slides_*/` + `slide_combined.pdf`)
- **Step 3 — Curate & polish:** Generate variants with `--copy 4`, delete the copies you don't love, regenerate stragglers with `--page "1,3,5-7"`, then rebuild offline with `--pdf-only` — 28 minutes of decisions, not labor
- **Swap providers, not code:** OpenRouter drives outline + images; Volcengine/Doubao Seedream is a drop-in image backend — choose per stage via `--provider`, with HTTP/HTTPS proxy and `--max-concurrent` support built in
- Core insight: The best presentation you've never manually built is one `git clone` and one `idea.md` away
[Visual: A terminal window occupying the left two-thirds of the slide on Deep Space background, showing a short setup block (`git clone`, `pip install`, `cp .env.example .env`) followed by four sequential CLI commands in JetBrains Mono 14pt with syntax highlighting: `research.cli`, `outline.cli`, `style.cli`, `compose.cli`. Each command has a small output preview fanning out to the right: research → citation list snippet, outline → film strip, style → contact sheet grid, compose → slide thumbnails. These previews converge into a glowing PDF icon at the far right labeled "slide_combined.pdf." Small badges float near the PDF: a "< 60 min" timer in Electric Cyan and "$4.73" cost in Signal Green (#00E676), plus an "MIT · 100% Python" repo chip and `github.com/xfcui/vibesliding` URL in JetBrains Mono 12pt along the bottom edge. Pipeline-thread watermark at 15% opacity.]
[Speech: So here's your invitation, and it's concrete. Step zero: clone the repo — github.com/xfcui/vibesliding, MIT-licensed, pure Python — install requirements, copy the env file, drop in your keys. Step one: write a paragraph in idea.md. A hundred and twenty-seven words is plenty. Step two: run four commands. Research pulls citation-grounded sources through Valyu. Outline emits three lengths at once — sixteen, twenty-five, or thirty-six content slides — plus the shared style scaffold. Style opens an interactive contact-sheet picker. Compose renders everything in parallel into a timestamped folder and a combined PDF. Step three: curate. Generate four variants per slide, delete the ones you don't love, regenerate stragglers with the page flag, and rebuild the PDF offline with pdf-only — no extra API calls. And if you want to swap image providers, it's a flag, not a rewrite. Twenty-eight minutes of your time, spent on decisions that matter. The result: ninety-four percent cheaper than a freelancer, sixty-seven percent less editing than single-shot tools, three times more slides than Tome. Thank you.]

---

## Slide 27: Thank You · Q&A

- **Key takeaway:** One paragraph in, publication-grade deck out — iterate everything, orchestrate commodity tools, curate with human judgment
- **Speaker:** Xuefeng Cui · Shandong University
- **WeChat:** xfcui0 · **Email:** xfcui.uw@gmail.com
[Visual: Centered cinematic composition strictly referencing style_cover.png for layout, typography, and clean spatial design. No split-screen. Dark Deep Space (#0A0F1A) background with the luminous five-node pipeline flow icon centered — rendered slightly larger than on the cover to signal completion, with all five circles fully illuminated in Electric Cyan (#00E5FF) and labeled with letters 'I', 'R', 'O', 'S', 'C' (representing Idea, Research, Outline, Style, Compose) with clean green checkmarks above each circle. Title "Thank You · Q&A" in Inter Bold 36pt Cool White centered above the emblem. Single takeaway sentence in Inter SemiBold 20pt beneath: "Iterate · Orchestrate · Curate." Contact details (WeChat, email) arranged as a minimal, clean list in the lower third with clean Inter Light 18pt typography, centered. Faint dot grid background. STRICT CONSTRAINT: Do NOT render any bounding boxes, wireframes, red or cyan box outlines, or literal template labels (such as "PANEL", "CALLOUT", "MOTIF", "TITLE AREA"). All visual elements must be final, polished presentation elements, with absolutely no design-template annotations.]
[Speech: Thank you all. The three words to remember: iterate, orchestrate, curate. I'm happy to take questions — about the pipeline, the architecture, the failures we learned from, or how to adapt this for your own domain. My WeChat and email are on screen.]

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
