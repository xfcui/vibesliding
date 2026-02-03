# PPT Outline: Programming at the Speed of Thought

---

## Slide 1: Title & Abstract
- **Title:** Programming at the Speed of Thought
- **Sub-Title:** Cursor and AI-Native Development Revolution
- Presented by Xuefeng Cui, Shandong University

---

## Slide 2: Hook: Clawdbot's iPhone Moment
- Peter Steinberger (PSPDFKit, $119M exit): Built Clawdbot solo
- Swarm Programming: 3-8 parallel AI agents, atomic commits
- Results: 8,400+ commits, 116,000+ GitHub stars in ~11 days
- Poll: "Who's tried multi-agent coding?"
[Visual: GIF of Clawdbot swarm terminals (github.com/petersteinberger/clawdbot); exploding stars chart; Excalidraw agent swarm diagram]

---

## Slide 3: Crisis: Sidecar Limits (Copilot/VS Code)
- Traditional: Developer types syntax at typing speed
- Sidecar Friction:
  | Friction | Issue |
  |----------|-------|
  | Context Isolation | No full state/terminal access |
  | Mechanical Latency | Copy-paste context-switch |
  | Reactive Nature | Waits for prompts, no intent prediction |
- Result: Speed of typing, not thought
[Visual: Side-by-side screenshot Copilot sidebar vs. empty editor; friction icons (barrier, clock, wait); striped table]

---

## Slide 4: AI-Native Rupture: Cursor Forks VS Code
- Not extension: Modified runtime intervenes in:
  - Rendering pipeline
  - File system events
  - Window management
- Continuous codebase vector embedding
- Predicts next *action* via cursor trajectory
[Visual: Excalidraw diagram (VS Code fork → AI layers: rendering/files/windows); Cursor vs. VS Code screenshot diff]

---

## Slide 5: Vibe Coding: Syntax Abstraction
- Focus on intent/architecture ("secure login page")
- AI translates to syntax; planning/coding collapses
- Multi-file refactors via natural language
- "Speed of thought"—friction removed
[Visual: GIF Vibe Coding demo (natural lang → multi-file edit in Cursor); brain→code flow diagram]

---

## Slide 6: Lecture Objectives
- Evolution: Crisis → AI-Native Rupture → Vibe Coding
- **Foundations: RAG → Shadow Workspace → Speculative Edits**
- Capabilities: Tab → Composer → Plan → Terminal
- Context: @ Symbols → .cursorrules → .cursorignore
- Nervous System: MCP → Clawdbot Deep-Dive
- Conclutions: The New Developer Skills
- **Hands-On: 4 Workflows from Vibe to Swarm**
[Visual: Vertical timeline diagram (Excalidraw, icons per section); progress bar 6/33]

---

## Slide 7: Foundation 1: RAG Context Engine
- LLM limit: 128k-200k tokens
- Semantic chunking: Classes/functions → vectors
- Merkle Trees: Sync only changes (hash diffs)
- Efficiency: Seconds for large repos
[Visual: Excalidraw RAG pipeline (code→chunks→embeddings→Merkle tree); vector space scatterplot]

---

## Slide 8: Foundation 2: Shadow Workspace
- Fixes hallucinations: Hidden background editor
- Flow: Proposal → LSP/linter validation → Correction → Apply
- Future: Kernel-level folder proxy for agent concurrency
[Visual: Diagram (main editor → shadow instance loop); before/after hallucination screenshot]

---

## Slide 9: Foundation 3: Speculative Edits
- Fireworks AI partnership: 1,000 tokens/sec (~3,500 chars/sec)
- Deterministic: n-grams + file state for unchanged seqs
- Parallel verification; Powers "Fast Apply"
[Visual: Speed chart (Cursor 1k tps vs. standard 50 tps); typewriter vs. instant GIF]

---

## Slide 10: Meta-Skill: Architect & Contractor
- Objection: "Just use it—no need to understand"
- Risks: RAG irrelevance, Shadow syntax-only, no logic check
- Truth: Powerful AI amplifies expertise (computational thinking)
- Model: Human architects; AI executes
[Visual: Balance scale icon (human brain vs. AI code); expertise amplification curve chart]

---

## Slide 11: Lecture Objectives
- Evolution: Crisis → AI-Native Rupture → Vibe Coding
- Foundations: RAG → Shadow Workspace → Speculative Edits
- **Capabilities: Tab → Composer → Plan → Terminal**
- Context: @ Symbols → .cursorrules → .cursorignore
- Nervous System: MCP → Clawdbot Deep-Dive
- Conclutions: The New Developer Skills
- **Hands-On: 4 Workflows from Vibe to Swarm**
[Visual: Vertical timeline diagram (Excalidraw, icons per section); progress bar 11/33]

---

## Slide 12: Cursor Tab: Predictive Intent
- Beyond ghost text: Cursor jumps, diff-awareness
- Trained on diff histories (delete/rewrite)
- Smart Paste: Auto-indent/vars
[Visual: GIF Cursor Tab jumps + Smart Paste (cursor.com); before/after paste screenshot]

---

## Slide 13: Composer: Agentic Orchestrator
- Cmd+I: Multi-file agent (dependency → create → integrate → verify)
- Visual Plan: File graph preview
- From chat → direct software creation
[Visual: Composer screenshot (plan graph); Excalidraw dependency flow]

---

## Slide 14: Composer Workflow: Multi-File Magic
- **Cmd+I Agent Orchestrator: From Chat to Software**
- 1. Cmd+I → Describe: "Dashboard w/ sidebar @Folders/ui + React Query"
- 2. AI Scans: Dependencies (@Codebase), generates files (Layout.tsx, etc.)
- 3. Visual Plan: Dependency graph preview → Approve/Edit
- 4. Execute: Create/integrate/verify → Diff view
- 5. Pro Tip: Chain "@Web Next.js hooks" for latest patterns
[Visual: Composer plan graph GIF showing approval flow]

---

## Slide 15: Plan Mode: Architecture of Thought
- Shift+Tab: Decouples think/type
- Workflow: Research → Clarify → Draft → Review → Build
- Mimics design docs; cuts arch errors
[Visual: Stepper diagram (5 phases); Plan Mode toggle GIF]

---

## Slide 16: Plan Mode Workflow: Think → Build
- **Shift+Tab: Decouple Planning from Typing**
- 1. Agent Mode → Shift+Tab: "Design user dashboard API"
- 2. Research: Scans @Codebase/@Docs → Asks: "REST or GraphQL?"
- 3. Draft MD Plan: Steps/files/APIs → Edit directly
- 4. Review: Refine architecture → Approve
- 5. Build: Auto-triggers Composer → Code generated
[Visual: 5-phase stepper diagram (Excalidraw: research→draft→build)]

---

## Slide 17: Terminal: CLI Agent
- Monitors output; "Add to Chat" fixes stack traces
- NL to shell: "Zip files >10MB" → find -size +10M | zip
[Visual: Terminal error → fix GIF; NL CLI examples table]

---

## Slide 18: Lecture Objectives
- Evolution: Crisis → AI-Native Rupture → Vibe Coding
- Foundations: RAG → Shadow Workspace → Speculative Edits
- Capabilities: Tab → Composer → Plan → Terminal
- **Context: @ Symbols → .cursorrules → .cursorignore**
- Nervous System: MCP → Clawdbot Deep-Dive
- Conclutions: The New Developer Skills
- **Hands-On: 4 Workflows from Vibe to Swarm**
[Visual: Vertical timeline diagram (Excalidraw, icons per section); progress bar 18/33]

---

## Slide 19: Context: @ Taxonomy
| @Symbol | Scope | Use |
|---------|-------|-----|
| @Files | Specific | Refactor module |
| @Codebase | RAG Search | "Where's auth?" |
| @Web | Live Net | Next.js 14 syntax |
| @Docs | Indexed | Stripe API |
| @Git | History | Last PR changes |
| @Folders | Bulk | Rewrite @/ui |
| @Definitions | Types | User interface |
[Visual: Striped table full-width; @ icon wheel diagram]

---

## Slide 20: .cursorrules: Prompt the IDE
- Persistent system prompt (.mdc + globs)
- Ex: React: Functional comps, React Query, Tailwind, Vitest tests
- Team consistency: Commit to repo
[Visual: .cursorrules file screenshot; glob scoping diagram]

---

## Slide 21: .cursorignore: Strategic Ignorance
- .cursorignore: Block (secrets/PII/binaries)
- .cursorindexingignore: No auto-index, manual OK
- Boosts perf/security
[Visual: Ignore file examples; lock/shield icons; perf chart (before/after index time)]

---

## Slide 22: Lecture Objectives
- Evolution: Crisis → AI-Native Rupture → Vibe Coding
- Foundations: RAG → Shadow Workspace → Speculative Edits
- Capabilities: Tab → Composer → Plan → Terminal
- Context: @ Symbols → .cursorrules → .cursorignore
- **Nervous System: MCP → Clawdbot Deep-Dive**
- Conclutions: The New Developer Skills
- **Hands-On: 4 Workflows from Vibe to Swarm**
[Visual: Vertical timeline diagram (Excalidraw, icons per section); progress bar 22/33]

---

## Slide 23: MCP: USB-C for AI
- Anthropic protocol: Host (Cursor) → Client (AI) → Server (data)
- Ends LLM isolation: DB/wiki/prod access
[Visual: USB-C plug diagram (3 components connected); MCP logo]

---

## Slide 24: ClawdHub: MCP Marketplace
| Category | Skills |
|----------|--------|
| Development | claude-team, sentry-fixer |
| Productivity | notion-sync, calendar-agent |
| Health | whoop-bio, testosterone-opt |
| Family | huckleberry |
| System | apple-mail, mole-cleanup |
- 700+ skills: `npx clawdhub install <slug>`
[Visual: Striped table; App Store-style grid mockup]

---

## Slide 25: Clawdbot Real-World Wins
- Car negotiation: Research → Email dealers
- CUDA → ROCm port: 30 mins
- WHOOP + smart home: Bio-optimize
- Insurance claims: Auto-forms
[Visual: 4-panel icons/screenshots (car/email/code/health/form); "force multiplier" badge]

---

## Slide 26: Local-First: Mac Mini Stack
- Why: Unified mem, <10W idle, privacy
- Headless closets; Tailscale tunnel remote
[Visual: Mac Mini photo stack; power chart (Mac vs. PC); tunnel diagram]

---

## Slide 27: Lecture Objectives
- Evolution: Crisis → AI-Native Rupture → Vibe Coding
- Foundations: RAG → Shadow Workspace → Speculative Edits
- Capabilities: Tab → Composer → Plan → Terminal
- Context: @ Symbols → .cursorrules → .cursorignore
- Nervous System: MCP → Clawdbot Deep-Dive
- **Conclutions: The New Developer Skills**
- **Hands-On: 4 Workflows from Vibe to Swarm**
[Visual: Vertical timeline diagram (Excalidraw, icons per section); progress bar 27/33]

---

## Slide 28: The New Developer Skills
- 1. Composer orchestration
- 2. Plan mode thinking
- 3. Context mastery (@ symbols)
- 4. Rule crafting (.cursorrules)
- 5. Tool integration (MCP)
- Shift: Code typing → Vibe coding
[Visual: Skill pyramid graphic]

---

## Slide 29: Agent Best Practices
- **Atomic Tasks:** Small, verifiable changes beat monolithic rewrites
- **One Task, One Agent:** Each agent should handle a single, focused task
- **Avoid Context Overload:** Long conversations degrade output quality
- **Reset When Full:** Start a new agent when context becomes cluttered
- **Parallel Isolation:** Multiple agents can work simultaneously on separate tasks
- Core insight: AI agents perform best with clear boundaries and fresh context
[Visual: Diagram showing single-task agents vs. overloaded agent (clean boxes vs. tangled mess); context meter (green→yellow→red); parallel agent lanes]

---

## Slide 30: Responsibility in AI Collaboration
- Programmer mindset: Code error → "I wrote it wrong" → Fix the code
- Leader mindset: Task failure → "Were my instructions clear?" → Refine the directive
- AI mindset shift: AI error → Not "AI is stupid" → Optimize the prompt
- Prompt = Code + Instruction: Bugs need fixing, unclear orders need rewriting
- Core insight: AI errors often stem from suboptimal inputs, not tool limitations
- Action: Refine prompts, anticipate risks → Unlock AI's true potential
[Visual: Flow diagram (Human→Prompt→AI→Output→Feedback loop); responsibility shift icon (finger pointing outward → inward mirror)]

---

## Slide 31: Vibe Coding Done Right
- Misconception: "One sentence → AI does everything" — Is this expectation realistic?
- True goal: Focus on top-level architecture; delegate implementation to AI
- Complex tasks require complete design specs before AI execution
- Workflow: Write "Architecture Encyclopedia" → Create .cursorrules referencing it → When output diverges, check the encyclopedia first
- Anti-pattern: Multi-page site with inconsistent styles → Fixing page-by-page = endless patch loop
- Correct approach: Return to top-level → Add unified style spec → Update encyclopedia → Regenerate from new rules
- Core logic: **We architect, AI implements**
[Visual: Pyramid diagram (Top: Human Architecture / Bottom: AI Implementation); patch spiral vs. top-down flow comparison]

---

## Slide 32: Agent Workflow: Learn → Act → Update
- **Learn Design Docs:** Agent reads architecture, specs, and context before coding
- **Act — Coding Cycle:**
  - *Plan:* Break down task into steps; confirm approach
  - *Implement:* Write code following design constraints
  - *Test:* Validate changes; fix issues before moving on
- **Update Design Docs:** If implementation deviates or reveals gaps, sync back to docs
- Loop: Each agent iteration improves both code and documentation
- Anti-pattern: Coding without reading specs → drift from architecture
[Visual: Circular flow diagram (Learn→Plan→Implement→Test→Update→Learn); Excalidraw loop arrows; doc icons syncing with code icons]

---

## Slide 33: Questions?
- Thank you for your attention!
[Visual: Open mic icon]

---

## Appendix: Global Visual Requirements
- **Theme:** Cursor dark mode (#0D1117 background, #58A6FF accents, #C9D1D9 text)
- **Fonts:** JetBrains Mono (titles, 48-60pt bold), Inter (body, 24-32pt)
- **Layout:** 35/65 title/body split (left title+icon, right content); 16:9 aspect
- **Animations:** Subtle fade-ins (bullets sequential, 0.5s); no spins/transitions
- **Icons:** Feather icons (e.g., code, brain, rocket) in #58A6FF, 64px
- **Diagrams:** Excalidraw-style (simple lines/boxes, monochromatic + accents)
- **Balance:** Max 5 bullets/slide; tables striped (#161B22/#0D1117); 40% visual space
