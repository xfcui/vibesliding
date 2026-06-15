# Reverse-Engineering NotebookLM: How Google's AI Research Notebook Works Under the Hood — and How the Community Rebuilt It

**Author context:** This report accompanies a technical presentation by Xuefeng Cui (Shandong University) and is intended for software engineers, AI practitioners, and researchers evaluating source-grounded AI systems at production scale.

---

## 1. Why Reverse-Engineer NotebookLM?

**Claim:** NotebookLM is one of the most widely used consumer RAG products in the world, yet until the 2025 Enterprise launch it offered zero programmatic access — creating a gap that the open-source community filled with clients collectively exceeding 20,000 GitHub stars.

Google launched NotebookLM (originally codenamed "Project Tailwind") at I/O 2023 as a personal AI research assistant that lets users upload PDFs, Google Docs, web pages, YouTube videos, and audio files, then ask questions grounded exclusively in those sources [[1]](https://blog.google/technology/ai/notebooklm-google-ai/). By mid-2025 it supported over 200 million monthly interactions across more than 80 million notebooks, according to figures shared at I/O 2025 [[2]](https://blog.google/technology/google-labs/notebooklm-update-io-2025/). The product's Audio Overview feature — which generates a two-host podcast-style discussion from uploaded sources — went viral in late 2024, driving a reported 300% month-over-month growth in unique users during Q4 2024 [[3]](https://www.theverge.com/2024/12/11/24318587/google-notebooklm-business-enterprise).

Despite this traction, Google provided no public REST or gRPC API for NotebookLM's consumer tier. Developers who wanted to programmatically create notebooks, upload sources, trigger Audio Overviews, or integrate grounded Q&A into agent loops had only one option: reverse-engineer the web client. The community responded aggressively:

- **`notebooklm-py`** (Python, teng-lin) — ~16,400 GitHub stars as of June 2026, wrapping the full lifecycle of notebook CRUD, source upload, query, and artifact generation into a pip-installable SDK with MCP/CLI/REST surfaces [[4]](https://github.com/teng-lin/notebooklm-py).
- **`notebooklm-mcp`** (Python, jacob-bd) — ~5,000 GitHub stars, exposing NotebookLM as a Model Context Protocol (MCP) tool server so that Claude, GPT-4, and Cursor agents can call it as a grounding oracle [[5]](https://github.com/jacob-bd/notebooklm-mcp).
- **`notebooklm-go`** (Go, LocalKinAI) — pure-Go client and CLI for batchexecute RPC without browser automation [[6]](https://github.com/LocalKinAI/notebooklm-go).
- **`notebooklm-client`** (TypeScript, icebear0828) — 220+ stars; supports browser and pure HTTP transport modes [[7]](https://github.com/icebear0828/notebooklm-client).

These projects collectively demonstrate that the demand for programmatic, source-grounded notebooks is real and that the community is willing to invest substantial reverse-engineering effort to meet it.

The arrival of **NotebookLM Enterprise** on Google Cloud in early 2025, offering organizational admin controls and an official API surface through Vertex AI, partially addressed this gap [[3]](https://www.theverge.com/2024/12/11/24318587/google-notebooklm-business-enterprise). However, the Enterprise tier requires a Google Cloud billing account and carries per-query pricing, leaving individual developers, academics, and hobbyists reliant on the reverse-engineered consumer interface.

**Takeaway:** NotebookLM's explosive adoption combined with the absence of a consumer API created a rich ecosystem of community-built clients — making the product's internal architecture one of the most actively reverse-engineered Google surfaces since the Search AJAX API.

---

## 2. The `batchexecute` RPC Layer

**Claim:** Every action in NotebookLM's web UI — from creating a notebook to generating an Audio Overview — passes through Google's proprietary `batchexecute` RPC envelope, a protocol that has remained undocumented for over a decade yet underlies virtually every Google Labs and consumer product frontend.

When a user clicks "New Notebook" in the browser, the request does not hit a clean REST endpoint. Instead, it is serialized into a POST to `/_/LabsTailwindUi/data/batchexecute` with a content type of `application/x-www-form-urlencoded`. The body contains a parameter named `f.req` whose value is a triple-nested JSON array encoding the RPC method ID, the payload, and routing metadata [[8]](https://kovatch.medium.com/deciphering-google-batchexecute-74991e4e446c).

Key structural elements that every unofficial client must implement:

| Element | Description | Example |
|---|---|---|
| **RPC ID** | A 6-character alphanumeric string identifying the server method | `wXbhsf` (list notebooks), `izAoDd` (add source), `R7cb6c` (create studio artifact) |
| **`f.req` payload** | Triple-nested JSON array: outer envelope → method array → argument array | `[[["wXbhsf","[...]",null,"generic"]]]` |
| **CSRF `at` token** | Session-bound anti-CSRF token (`SNlM0e` value) extracted from page HTML | Rotates per session |
| **Anti-XSSI prefix** | Response body begins with `)]}'\n`; clients must strip before JSON-parsing | `)]}'\n` |
| **`reqid` counter** | Monotonically increasing request ID for ordering within a session | Starts at random large integer |

The `batchexecute` protocol allows *batching* — multiple RPC calls can be packed into a single HTTP POST. Community clients generally issue one RPC per HTTP call for simplicity, but `notebooklm-py` supports batching for bulk source uploads [[4]](https://github.com/teng-lin/notebooklm-py).

Reverse-engineering the RPC IDs follows a DevTools-first workflow: Chrome DevTools → Network tab → filter `batchexecute` → perform UI action → inspect `f.req` form data → extract the 6-character ID and argument array structure. The community has cataloged 30+ distinct RPC methods for NotebookLM, ranging from notebook lifecycle to source management, query execution, and Studio artifact generation [[9]](https://github.com/teng-lin/notebooklm-py/blob/main/docs/rpc-reference.md).

A notable subtlety is the **streaming query endpoint**. While standard queries use a single `batchexecute` POST, the streaming variant opens a chunked transfer-encoded response where each chunk is a `batchexecute`-formatted fragment containing partial tokens and thinking-trace metadata ("Analyzing sources...", "Found relevant passages in [Source Name]") [[5]](https://github.com/jacob-bd/notebooklm-mcp/blob/main/docs/API_REFERENCE.md).

**Takeaway:** Understanding `batchexecute` is the skeleton key to every Google Labs product — once you can decode the RPC envelope, the rest is mapping method IDs to UI actions and argument schemas.

---

## 3. Source Grounding Architecture

**Claim:** NotebookLM employs a hybrid grounding strategy that dynamically switches between full long-context injection (for small notebooks) and chunked RAG retrieval (for large corpora), unified under Google's Discovery Engine / Vertex AI Search infrastructure.

The grounding design was partially disclosed by Google and further analyzed in independent teardowns [[10]](https://chinwendu.medium.com/how-notebooklm-handles-file-uploads-8e0f9a34c7ac) [[11]](https://assets.nextleap.app/submissions/NotebookLLMTeardown2-c41bf90d-2c8e-4618-b73e-fd4e124b9c4c.pdf). The two-mode architecture works as follows:

### 3a. Long-Context Injection Mode

When the total token count of all sources in a notebook falls within Gemini's context window (2 million tokens for Gemini 2.5 Pro), NotebookLM can inject the *entire* source corpus directly into the prompt. This avoids retrieval losses entirely — every sentence is visible to the model, enabling precise citation and cross-document synthesis. A 50-source notebook of short articles (~2K tokens each) totals ~100K tokens, well within range.

### 3b. Chunked RAG Mode

When the corpus exceeds injection budget, NotebookLM falls back to a RAG pipeline:

1. **Parsing** — format-specific extractors: PDFs (Cloud Document AI), Google Docs (native API), web pages (headless rendering), YouTube (transcript API), audio (Chirp ASR).
2. **Adaptive Chunking** — structural segmentation respecting section headers and paragraph boundaries; ~512-token chunks with ~64-token overlap for prose; tables chunked as atomic units [[11]](https://assets.nextleap.app/submissions/NotebookLLMTeardown2-c41bf90d-2c8e-4618-b73e-fd4e124b9c4c.pdf).
3. **Embedding** — Gecko-class models (`textembedding-gecko@003` or successor), 768-dimensional dense vectors [[10]](https://chinwendu.medium.com/how-notebooklm-handles-file-uploads-8e0f9a34c7ac).
4. **Vector Indexing** — ScaNN-based ANN index within Discovery Engine (Vertex AI Vector Search) [[12]](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction).
5. **Hybrid Search** — dense vector retrieval + sparse keyword matching (BM25-equivalent) at query time [[11]](https://assets.nextleap.app/submissions/NotebookLLMTeardown2-c41bf90d-2c8e-4618-b73e-fd4e124b9c4c.pdf).
6. **Re-ranking** — BGE-style cross-encoder re-ranker scores top-K candidates; system prompt enforces citation-only generation with inline source IDs [[11]](https://assets.nextleap.app/submissions/NotebookLLMTeardown2-c41bf90d-2c8e-4618-b73e-fd4e124b9c4c.pdf).

Discovery Engine ranking signals (from related Google AI Mode reverse-engineering) include Gecko embedding similarity, Jetstream cross-attention for negation handling, BM25 keyword matching, and freshness boosts [[13]](https://metehan.ai/blog/reverse-engineering-google-ai-mode).

Independent evaluations find NotebookLM produces verifiable, source-grounded citations in approximately 90%+ of responses when sources are well-structured [[10]](https://chinwendu.medium.com/how-notebooklm-handles-file-uploads-8e0f9a34c7ac).

**Takeaway:** NotebookLM's grounding quality stems from the dynamic interplay of long-context injection and chunked RAG, selected per-notebook based on corpus size.

---

## 4. The Upload & Indexing Pipeline

**Claim:** A single "Add Source" click triggers a six-stage pipeline spanning blob storage, Spanner-based job queues, format-specific parsing, adaptive chunking, embedding, and vector indexing — completing in under 30 seconds for a typical 20-page PDF.

The pipeline, as reconstructed from network traces and Google Cloud documentation [[10]](https://chinwendu.medium.com/how-notebooklm-handles-file-uploads-8e0f9a34c7ac) [[12]](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction):

1. **Blob Serialization** — Client base64-encodes binary files or extracts text (Google Docs via Drive API), sent via `izAoDd` batchexecute RPC. Limits: 500K words per source, 50 sources per notebook.

2. **Spanner Queue** — Backend writes a job record to Cloud Spanner as a durable work queue; UI polls `getSourceStatus` RPC returning `PROCESSING`, `READY`, or `FAILED`.

3. **Format-Specific Parsing** — PDFs → Document AI (OCR + layout); Google Docs → Docs API export; Web URLs → headless Chrome + readability; YouTube → transcript API; Audio → Chirp v2 ASR (100+ languages).

4. **Adaptive Chunking** — ~512-token chunks with heading preservation and overlap.

5. **Embedding** — Gecko-class model; ~80 chunks from a 20-page PDF embed in ~2–3 seconds on TPU-backed service.

6. **Vector Indexing** — Embeddings upserted into per-notebook ScaNN index within Discovery Engine.

Benchmark: a 150-page academic paper (~60K tokens, ~120 chunks) transitions from `PROCESSING` to `READY` within 15–25 seconds. `notebooklm-py` exposes this as async `wait_for_source_ready()` polling at 2-second intervals [[4]](https://github.com/teng-lin/notebooklm-py).

**Takeaway:** NotebookLM's upload pipeline is a textbook example of production ingestion engineering — durable queuing, format-aware parsing, and sub-30-second end-to-end latency.

---

## 5. Studio & Streaming Features

**Claim:** NotebookLM's Studio panel has evolved from a single Audio Overview in 2024 to a full artifact generation suite in 2025 — podcasts, briefing docs, study guides, mind maps, slide decks, video overviews, quizzes, flashcards, infographics, and data tables — each backed by distinct RPC methods.

The Audio Overview pipeline: (1) Gemini generates a podcast script from sources, (2) multi-speaker TTS (SoundStorm/AudioPaLM variant), (3) MP3 streamed via signed Cloud Storage URL [[2]](https://blog.google/technology/google-labs/notebooklm-update-io-2025/). I/O 2025 added tone/length/language customization and Video Overviews with auto-generated visuals [[2]](https://blog.google/technology/google-labs/notebooklm-update-io-2025/).

Key Studio RPC methods (community catalog):

| RPC ID | Function | Notes |
|---|---|---|
| `R7cb6c` | Create Studio Content | Type codes: 1=Audio, 2=Report, 3=Video, 5=Mind Map, 7=Infographic, 8=Slide Deck, 9=Data Table |
| `QA9ei` | Deep Research (web-augmented) | Web-only; 5–10 min; 10–20 sub-queries [[14]](https://blog.google/products/gemini/google-gemini-deep-research/) |
| `Ljjv0c` | Fast Research | Source-grounded only; <30 sec |
| `LBwxtb` | Import Research Sources | Bulk import discovered sources |

Audio formats: Deep Dive, Brief, Critique, Debate; lengths: Short/Default/Long; 50+ languages. `notebooklm-py` v0.7.1 documents golden-test-pinned payloads for all artifact types [[9]](https://github.com/teng-lin/notebooklm-py/blob/main/docs/rpc-reference.md).

Free-tier rate limits (empirically observed, not officially published): ~50 standard queries/day, ~3 Audio Overviews/day, ~1–2 Deep Research runs/day [[5]](https://github.com/jacob-bd/notebooklm-mcp/blob/main/docs/API_REFERENCE.md).

**Takeaway:** Each Studio artifact type maps to a specific RPC method — community clients can programmatically generate podcasts, slide decks, and deep-research reports without opening the browser.

---

## 6. Building on Reverse-Engineered APIs

**Claim:** The most robust community integrations follow a "capture → pin → expose → test" workflow that treats reverse-engineered RPC payloads as golden test fixtures.

### 6a. The DevTools Capture Workflow

1. **Capture** — Chrome DevTools (filter `batchexecute`) or `mitmproxy` to record requests/responses.
2. **Decode** — Strip anti-XSSI prefix, parse outer JSON, identify RPC ID and argument positions.
3. **Pin** — Save raw request/response as golden test fixture for CI schema-change detection.
4. **Expose** — Wrap in typed functions with human-readable parameter names.
5. **Test** — Integration tests against live NotebookLM (sparingly) + unit tests against fixtures.

`notebooklm-py` pins CREATE_ARTIFACT payloads against live builders in `_artifact/payloads.py`, re-verified 2026-06-11 [[9]](https://github.com/teng-lin/notebooklm-py/blob/main/docs/rpc-reference.md).

### 6b. MCP and Agent Integration

`notebooklm-mcp` exposes NotebookLM as an MCP tool server: create notebooks, upload documents, ask grounded questions, trigger Audio Overviews, run Deep Research [[5]](https://github.com/jacob-bd/notebooklm-mcp). `notebooklm-py` ships agentic skills for Claude Code, Codex, and OpenClaw [[4]](https://github.com/teng-lin/notebooklm-py).

### 6c. Open-Source Alternatives

| Dimension | Reverse-Engineered Consumer API | NotebookLM Enterprise | Open-Source Rebuild |
|---|---|---|---|
| **Cost** | Free (rate-limited) | Per-query pricing | Self-hosted compute |
| **Reliability** | Fragile (schema changes) | SLA-backed | Self-managed |
| **Features** | Full consumer feature set | Full + admin controls | Varies |
| **Programmatic Access** | Community SDKs | Official API | Full control |
| **ToS Compliance** | Gray area | Fully compliant | Fully compliant |

Notable rebuilds:
- **Open Notebook** (lfnovo) — self-hosted, 18+ AI providers, multi-speaker podcasts, full REST API [[15]](https://github.com/lfnovo/open-notebook).
- **NotebookLlama** (run-llama) — LlamaIndex-backed, Streamlit UI, LlamaCloud pipeline [[16]](https://github.com/run-llama/notebookllama).
- **Vertex AI Search + Gemini API** — official production path; what Enterprise uses internally [[12]](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction).

**Takeaway:** Reverse-engineered APIs are viable for prototyping and internal tooling; production systems should plan migration to Enterprise or open-source rebuilds.

---

## 7. Landscape and Forward Look

**Claim:** Reverse-engineering NotebookLM has produced a detailed public map of Google's production RAG architecture that benefits the entire AI engineering community.

Architectural patterns revealed — hybrid long-context/RAG switching, adaptive structural chunking, Spanner ingestion queues, multi-artifact generation from shared grounding — represent battle-tested solutions cited in LlamaIndex and LangChain RAG frameworks. I/O 2025 signals continued expansion: video overviews, interactive study tools, deeper Google ecosystem integration (Drive, Gmail, Calendar) [[2]](https://blog.google/technology/google-labs/notebooklm-update-io-2025/).

Until a full consumer API ships, the `batchexecute` decoder ring remains the most productive way to understand how Google builds production-grade, source-grounded AI systems.

**Takeaway:** Reverse-engineering NotebookLM is a masterclass in how Google architects RAG at scale — lessons that generalize far beyond a single product.

---

## Sources

[1] Google. "NotebookLM: A New AI-First Notebook." *The Keyword*, 2023. https://blog.google/technology/ai/notebooklm-google-ai/

[2] Google. "NotebookLM Update at I/O 2025." *The Keyword*, 2025. https://blog.google/technology/google-labs/notebooklm-update-io-2025/

[3] Pierce, D. "Google's NotebookLM Launches Enterprise Tier." *The Verge*, Dec 2024. https://www.theverge.com/2024/12/11/24318587/google-notebooklm-business-enterprise

[4] teng-lin. "notebooklm-py." *GitHub*, 2026. https://github.com/teng-lin/notebooklm-py

[5] jacob-bd. "notebooklm-mcp." *GitHub*, 2025. https://github.com/jacob-bd/notebooklm-mcp

[6] LocalKinAI. "notebooklm-go." *GitHub*, 2026. https://github.com/LocalKinAI/notebooklm-go

[7] icebear0828. "notebooklm-client." *GitHub*, 2026. https://github.com/icebear0828/notebooklm-client

[8] Kovatch, S. "Deciphering Google's batchexecute Protocol." *Medium*, 2020. https://kovatch.medium.com/deciphering-google-batchexecute-74991e4e446c

[9] teng-lin. "RPC Reference." *notebooklm-py docs*, 2026. https://github.com/teng-lin/notebooklm-py/blob/main/docs/rpc-reference.md

[10] Onyewuchi, C. "How NotebookLM Handles File Uploads." *Medium*, 2025. https://chinwendu.medium.com/how-notebooklm-handles-file-uploads-8e0f9a34c7ac

[11] NextLeap. "NotebookLM RAG Architecture Teardown." *PDF*, 2025. https://assets.nextleap.app/submissions/NotebookLLMTeardown2-c41bf90d-2c8e-4618-b73e-fd4e124b9c4c.pdf

[12] Google Cloud. "Discovery Engine / Vertex AI Search." *Google Cloud Docs*, 2025. https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction

[13] Metehan. "Reverse-Engineering Google AI Mode." *metehan.ai*, 2025. https://metehan.ai/blog/reverse-engineering-google-ai-mode

[14] Google. "Gemini Deep Research." *The Keyword*, 2024. https://blog.google/products/gemini/google-gemini-deep-research/

[15] lfnovo. "Open Notebook." *GitHub*, 2025. https://github.com/lfnovo/open-notebook

[16] run-llama. "NotebookLlama." *GitHub*, 2025. https://github.com/run-llama/notebookllama
