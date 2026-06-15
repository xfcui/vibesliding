# Presentation Idea

**Title:** Reverse-Engineering NotebookLM
**Subtitle:** How Google's AI research notebook works under the hood — and how the community rebuilt it

**Speaker:** Xuefeng Cui
**Affiliation:** Shandong University

**WeChat:** xfcui0
**Email:** xfcui.uw@gmail.com

## Audience

- Software engineers and AI practitioners curious about how production RAG systems are built at Google scale
- Developers building agentic workflows who want programmatic access to NotebookLM (MCP, CLI, Python SDK)
- Researchers and tech leads evaluating source-grounded AI vs. generic chat, and open-source NotebookLM alternatives

## Hook

NotebookLM looks like a simple upload-and-chat app, but behind the UI sits a layered stack: Google's `batchexecute` RPC protocol, Discovery Engine ingestion, hybrid long-context + RAG grounding, and a Studio artifact factory (audio overviews, slide decks, deep research). By mid-2025 it handled 200M+ monthly interactions across 80M+ notebooks (Google, I/O 2025), yet the consumer tier offered no public API — driving community clients like `notebooklm-py` (~16K GitHub stars) and `notebooklm-mcp` (~5K stars) to reverse-engineer 30+ RPC methods. This talk peels back NotebookLM layer by layer: capture traffic in DevTools, decode `f.req` payloads, map the six-stage upload pipeline, and wire grounded Q&A into agent loops via MCP.

## Content Focus

1. **Why Reverse-Engineer NotebookLM?** — Launched as Project Tailwind at I/O 2023; Audio Overviews drove ~300% MoM user growth in Q4 2024 (The Verge, 2024); consumer tier had zero API until Enterprise (Dec 2024) — community SDKs collectively exceed 20K stars and prove demand for programmatic notebooks, audio generation, and agent grounding
2. **The batchexecute RPC Layer** — Every UI action POSTs to `/_/LabsTailwindUi/data/batchexecute` with triple-nested `f.req` JSON, 6-char RPC IDs (`wXbhsf` create, `izAoDd` add source, `R7cb6c` studio), session CSRF `at` token, and anti-XSSI `)]}'` response prefix (Kovatch, 2020); streaming queries use chunked transfer-encoded fragments with thinking-trace metadata
3. **Source Grounding Architecture** — Hybrid mode: full Gemini 2.5 Pro long-context injection (up to 2M tokens) for small notebooks vs. chunked RAG for large corpora; RAG path uses ~512-token adaptive chunks (64-token overlap), Gecko-class 768-dim embeddings, ScaNN vector index in Discovery Engine, hybrid dense+BM25 retrieval, and BGE-style re-ranking — yielding 90%+ verifiable citations on well-structured sources (NextLeap teardown; Onyewuchi, 2025)
4. **The Upload & Indexing Pipeline** — Six stages in under 30 s for a typical 20-page PDF: blob serialization → Spanner job queue → format-specific parsing (Document AI for PDF, Chirp ASR for audio) → adaptive chunking → TPU-backed embedding (~2–3 s for 80 chunks) → per-notebook vector upsert; limits: 50 sources/notebook, 500K words/source; 150-page papers reach `READY` in 15–25 s
5. **Studio & Streaming Features** — Artifact RPCs power audio overviews (4 formats × 3 lengths × 50+ languages), video overviews, slide decks, mind maps, quizzes; Deep Research (`QA9ei`, web-only, 5–10 min, 10–20 sub-queries) vs. Fast Research (`Ljjv0c`, <30 s); empirically observed free-tier caps: ~50 queries/day, ~3 audio/day, ~1–2 deep research/day
6. **Building on Reverse-Engineered APIs** — Capture → decode → pin golden fixtures → expose typed wrappers → test; `notebooklm-mcp` exposes create/upload/query/audio as MCP tools for Claude and Cursor agents; contrast fragile consumer RE (schema breakage risk) with NotebookLM Enterprise (SLA, official API) and open-source rebuilds (Open Notebook, NotebookLlama via LlamaIndex)

## Scope Exclusions

- Step-by-step tutorial on bypassing Google's Terms of Service or authentication — focus on architecture understanding and legitimate automation patterns
- Full reproduction of NotebookLM as a self-hosted product (covered only as landscape comparison)
- NotebookLM Enterprise pricing, procurement, or org-admin deployment guides
- Generic RAG 101 without NotebookLM-specific grounding, citation, or RPC details
