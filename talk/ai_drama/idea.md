# Presentation Idea

**Title:** AI Drama Generation
**Subtitle:** From one-sentence prompts to industrial-scale short-form video — pipelines, models, and the China boom

**Speaker:** Xuefeng Cui
**Affiliation:** Shandong University

**WeChat:** xfcui0
**Email:** xfcui.uw@gmail.com

## Audience

- AI practitioners and product builders exploring multi-agent video pipelines, short-form drama automation, and production-as-code workflows
- Content strategists and media-tech leaders tracking the shift from one-off AI clips to serialized vertical drama at scale
- Researchers interested in narrative coherence, cross-clip consistency benchmarks, and agentic long-horizon video generation

## Hook

Generative video has crossed from demo clips to an industrial production system. China's short-drama market exceeded ¥50 billion (~$7B) in 2025 (Pandaily, 2025), and by early 2026 studios were releasing an average of **470 AI short dramas per day** (DataEye / MIT Technology Review, 2026) — compressing traditional 3–4 month shoots into **under 5 days** at **$6K–$15K** per series vs. **$105K–$230K** live-action (93–96% cost reduction). The technical unlock is not a single model but a **multi-agent production pipeline**: LLM screenwriters enforce short-drama pacing (3-second hooks, cliffhanger endings); Character DNA and first-frame locking preserve identity across shots; Seedance 2.0 and Kling 3.0 render multi-shot sequences with native audio; reviewer loops and BGM planners close the quality gap. Breakout remains brutally rare — only **0.117%** of AI dramas cross 100M views — but volume economics ("spray and pray" at 10+ series/day) make the hit rate statistically sustainable. This talk maps the stack from research frameworks like "One Sentence, One Drama" to open-source pipelines (Wind Comic, Showrunner) and the ByteDance/Kuaishou platform wars driving the boom.

## Content Focus

1. **The Short-Drama Format** — Vertical 1–3 min episodes × 60–100 per series; "dopamine scripting" (humiliation → power reveal → cliffhanger) makes trope-driven revenge/romance arcs structurally compatible with LLM generation; ReelShort topped U.S. iOS entertainment charts and generated $100M+ annual revenue (TechCrunch, 2024)
2. **Multi-Agent Production Pipelines** — Seven-stage production-as-code: Screenwriter → Character DNA → Storyboard → First-Frame Lock (T2I + IP-Adapter/LoRA) → I2V clip (Seedance/Kling) → Lip-sync/BGM → Reviewer QC loop; typed artifacts flow between agents (Showrunner, Wind Comic, "One Sentence, One Drama")
3. **The Model Layer: Seedance vs. Kling vs. Sora** — Seedance 2.0: multi-shot storyboard + native audio + Douyin integration; Kling 3.0: ~$300M ARR, character-lock API at $0.02–0.05/5s clip (36Kr, 2026); Sora de-prioritized for lacking storyboard mode, character lock, and native audio (The Information, 2026)
4. **Three Hard Problems** — Narrative pacing: one-shot LLM scripts produce flat tension; hierarchical planning + human script doctors on 60–70% of releases; spatial consistency: Character Identity Score ~0.82 same-episode but ~0.64 cross-episode (Short-Drama-Bench); automated QC catches only 40–50% of issues a human would flag
5. **Industrial Scale & Economics** — 470/day release rate; case study "Reborn as the CEO's Secret Wife": 4.5 days, $9,200 cost, 230M views, ~$180K revenue (MIT Technology Review, 2026); 30–40% displacement of entry-level scriptwriting roles offset by new "AI director" and "character architect" roles (DataEye, 2026)
6. **Regulation, IP, and What's Next** — CAC mandates AI watermarking and celebrity likeness bans; Seedance global rollout suspended Q1 2026; pipeline systems outperform end-to-end by 35–50% on CIS and 20–30% on emotional arc coherence (Short-Drama-Bench); frontier: real-time generation from viewer signals, branching narratives, cross-lingual dubbing

## Scope Exclusions

- Generic prompt-engineering tips for single 5-second clips without narrative structure
- Deep film theory or traditional TV production workflows unrelated to AI automation
- Hands-on tutorial for one specific vendor UI (focus on transferable pipeline architecture)
- Uncritical hype about "replacing Hollywood" without breakout-rate and QC evidence
