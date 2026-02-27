# PPT Outline: Programming at the Speed of Thought

---

## Slide 1: Title & Abstract
- **Title:** Programming at the Speed of Thought
- **Sub-Title:** Cursor and AI-Native Development Revolution
- **Presenter:** Xuefeng Cui, Shandong University
- Core insight: We are moving from the era of typing code to the era of programming at the speed of thought.
[Visual: Minimalist title slide with a large, glowing Cursor logo in the center; subtle, dark-themed background with floating code snippets; professional university branding at the bottom.]
[Speech: Welcome everyone. Today we're going to talk about a fundamental shift in how we write software. We're moving from the era of typing code to the era of programming at the speed of thought, driven by AI-native tools like Cursor.]

---

## Slide 2: Hook: Clawdbot's iPhone Moment
- **Solo Scale:** Peter Steinberger (PSPDFKit, $119M exit) built Clawdbot entirely solo
- **Swarm Architecture:** Orchestrated 3-8 parallel AI agents for atomic commits
- **Velocity:** Achieved 8,400+ commits and 116,000+ GitHub stars in just ~11 days
- Core insight: One developer can now output the work of an entire engineering team.
[Visual: A split-screen layout. Left side: A terminal window showing a "swarm" of parallel agent logs. Right side: A large, glowing GitHub star icon with the number "116k+" next to it. Professional, high-contrast design.]
[Speech: Let's start with a story. Peter Steinberger, a veteran founder, built Clawdbot alone. But he didn't just write code; he conducted a symphony of AI agents. In 11 days, he generated over 8,000 commits. This is our "iPhone moment" for software development.]

---

## Slide 3: Crisis: Sidecar Limits (Copilot/VS Code)
- **Traditional Model:** Developer types syntax manually at typing speed
- **Context Isolation:** Tools like Copilot operate as "sidecars" — separate assistants that sit beside your editor but lack full access to your codebase state, terminal, or file system
- **Mechanical Latency:** Constant copy-pasting creates context-switching friction
- **Reactive Nature:** Tools wait for prompts instead of predicting intent
- Anti-pattern: We are limited by the speed of typing, not the speed of thought.
[Visual: A "friction" diagram. A developer silhouette is blocked by a series of walls labeled "Copy-Paste", "Context Switch", and "Waiting for Prompt". The background is a cluttered, messy code editor.]
[Speech: The problem with current tools like Copilot is that they are just "sidecars." They sit next to your code but don't really understand it. You're still stuck copy-pasting, switching contexts, and waiting. It's faster than manual typing, but it's not a paradigm shift.]

---

## Slide 4: AI-Native Rupture: Cursor Forks VS Code
- **Deep Integration:** Not an extension, but a modified runtime intervening in rendering
- **File System Events:** Custom handling of file changes for immediate AI awareness
- **Window Management:** AI controls the window layout for diffs and chats
- **Vector Embedding:** Continuous codebase indexing for instant semantic retrieval
- **Action Prediction:** Predicts next *action* via cursor trajectory, not just text
- Core logic: Deep integration allows the AI to intervene at the kernel level of the IDE.
[Visual: A clean, modern flowchart showing the VS Code core at the center, with new "AI Native" layers for Rendering, File System, and Window Management built directly into it. Use glowing blue accents.]
[Speech: Cursor didn't just build a plugin; they forked VS Code. This allows them to intervene at the rendering level, the file system level, and even predict your next cursor movement. It's the difference between bolting an electric motor onto a bicycle and building a Tesla.]

---

## Slide 5: Vibe Coding: Syntax Abstraction
- **Intent Focus:** Developers focus on architecture ("secure login page")
- **AI Translation:** AI handles the syntax; planning and coding collapse into one
- **Multi-file Scope:** Refactors happen across the entire codebase via natural language
- **Friction Removal:** "Speed of thought" means zero latency between idea and execution
- Core insight: You are no longer a typist; you are an architect.
[Visual: A conceptual diagram showing a "Brain" icon on the left and a "Codebase" icon on the right, connected by a single, thick, glowing arrow labeled "Intent". No intermediate "Syntax" step.]
[Speech: This leads us to "Vibe Coding." You describe the intent—"make a secure login page"—and the AI handles the syntax. You're not worrying about semicolons; you're worrying about flow and security. It's architecture at the speed of conversation.]

---

## Slide 6: Lecture Objectives
- **Evolution:** Crisis → AI-Native Rupture → Vibe Coding
- **Foundations:** RAG → Shadow Workspace → Speculative Edits
- **Capabilities:** Tab → Composer → Plan → Terminal
- **Context:** @ Symbols → .cursorrules → .cursorignore
- **Nervous System:** MCP & Skills → Clawdbot Deep-Dive
- **Conclusions:** The New Developer Skills
[Visual: A vertical timeline diagram with icons for each section. A progress bar at the bottom shows "progress bar 6/31". Use the Cursor dark theme colors.]
[Speech: So here is our roadmap. We've covered the evolution. Now we're going to dive deep into the technical foundations that make this possible: RAG, the Shadow Workspace, and Speculative Edits.]

---

## Slide 7: Foundation 1: RAG Context Engine
- **LLM Constraints:** Models have a hard limit of 128k-200k tokens
- **Semantic Chunking:** Code is broken into classes/functions and converted to vectors
- **Merkle Trees:** Syncs only changes (hash diffs) to keep index fresh
- **Efficiency:** Retrieval happens in seconds even for massive repositories
- Core logic: Relevant context is retrieved instantly, bypassing token limits.
[Visual: A RAG pipeline diagram. Code files flow into a "Chunker", then into an "Embedding Engine", and finally into a "Vector Database". A Merkle Tree icon sits above the database to show sync efficiency.]
[Speech: First up is RAG, or Retrieval-Augmented Generation. LLMs have limited memory. Cursor solves this by chunking your code into semantic pieces and using Merkle Trees to sync only what changes. It's how Cursor knows about that function you wrote three months ago.]

---

## Slide 8: Foundation 2: Shadow Workspace
- **Hallucination Fix:** A hidden background editor runs code to verify it
- **Verification Loop:** Proposal → LSP/linter validation → Correction → Apply
- **Agent Concurrency:** Future kernel-level folder proxy for parallel agents
- Core insight: The AI checks its own work before you ever see it.
[Visual: A split-screen layout. Left: "Main Editor" with a code proposal. Right: "Shadow Workspace" (dimmed) showing a linter running and fixing an error. An arrow loops back to the Main Editor.]
[Speech: Next is the Shadow Workspace. Ever had an AI suggest code that doesn't compile? Cursor runs a hidden instance of VS Code to lint and check the AI's code *before* showing it to you. It's like having a pair programmer who double-checks their work.]

---

## Slide 9: Foundation 3: Speculative Edits
- **High Speed:** Fireworks AI partnership delivers 1,000 tokens/sec (~3,500 chars/sec)
- **Deterministic Fill:** Uses n-grams + file state for unchanged sequences
- **Parallel Verification:** Multiple possibilities are checked in parallel
- **Fast Apply:** Powers the instant "Apply" feature for large diffs
- Core insight: Speed matters because latency breaks flow.
[Visual: A high-speed speedometer graphic pointing to "1,000 tokens/sec". Next to it, a bar chart comparing "Standard AI (50 tps)" vs "Cursor (1,000 tps)". Use high-contrast colors.]
[Speech: Finally, Speculative Edits. Through a partnership with Fireworks AI, Cursor generates code at 1,000 tokens per second. It predicts the next chunk of code deterministically, so you're never waiting for the bot to type. It feels instant.]

---

## Slide 10: Meta-Skill: Architect & Contractor
- **Objection:** "Just use it—no need to understand how it works"
- **Risks:** RAG irrelevance, Shadow syntax-only, no logic check
- **Truth:** Powerful AI amplifies expertise (computational thinking)
- **Model:** Human architects design; AI contractors execute
- Core insight: You must understand the tool to master the craft.
[Visual: A balance scale. On one side, a "Human Brain" (Architect). On the other side, an "AI Robot" (Contractor). The scale is perfectly balanced. Professional, minimalist icons.]
[Speech: Some say, "Just use the tool, don't worry about how it works." That's wrong. If you don't understand RAG or the Shadow Workspace, you can't troubleshoot when things go wrong. You need to be the architect who understands the materials, not just the contractor laying bricks.]

---

## Slide 11: Lecture Objectives
- **Evolution:** Crisis → AI-Native Rupture → Vibe Coding
- **Foundations:** RAG → Shadow Workspace → Speculative Edits
- **Capabilities:** Tab → Composer → Plan → Terminal
- **Context:** @ Symbols → .cursorrules → .cursorignore
- **Nervous System:** MCP & Skills → Clawdbot Deep-Dive
- **Conclusions:** The New Developer Skills
[Visual: A vertical timeline diagram with icons for each section. A progress bar at the bottom shows "progress bar 11/31". Current section "Capabilities" is highlighted.]
[Speech: Now that we understand the engine, let's look at the controls. We'll cover Cursor Tab, Composer, Plan Mode, and the Terminal integration.]

---

## Slide 12: Cursor Tab: Predictive Intent
- **Beyond Ghost Text:** Cursor jumps to where you want to edit, diff-awareness
- **Training Data:** Trained on diff histories (delete/rewrite) to predict edits
- **Smart Paste:** Automatically adjusts indentation and variable names
- Core insight: The editor predicts your *intent*, not just your next character.
[Visual: A "Smart Paste" demo graphic. A messy code snippet on the left is transformed into a clean, perfectly indented snippet on the right. A "Predictive Cursor" icon shows it jumping between lines.]
[Speech: Cursor Tab isn't just autocomplete. It predicts where your cursor wants to go next. It's trained on millions of diffs, so it knows that if you change a function signature here, you likely need to update the call site there. It's predictive editing.]

---

## Slide 13: Composer Workflow: Multi-File Magic
- **Cmd+I Orchestrator:** The bridge from Chat to actual Software
- **1. Describe:** "Dashboard w/ sidebar @Folders/ui + React Query"
- **2. AI Scans:** Checks dependencies (@Codebase), generates files (Layout.tsx)
- **3. Visual Plan:** Dependency graph preview → Approve/Edit
- **4. Execute:** Create/integrate/verify → Diff view
- Core insight: You're editing the project, not just a file.
[Visual: A "Composer" interface mockup showing a natural language prompt at the top and a file dependency graph below with files like "Layout.tsx", "Sidebar.tsx", and "api.ts" being created.]
[Speech: Composer is the magic wand. You hit Cmd+I and describe a feature affecting multiple files. It scans your codebase, proposes a plan, and then executes it across the entire project. You're editing the project, not just a file.]

---

## Slide 14: Plan Mode Workflow: Think → Build
- **Shift+Tab:** Decouple Planning from Typing
- **1. Agent Mode:** Shift+Tab: "Design user dashboard API"
- **2. Research:** Scans @Codebase/@Docs → Asks: "REST or GraphQL?"
- **3. Draft MD Plan:** Steps/files/APIs → Edit directly
- **4. Review:** Refine architecture → Approve
- **5. Build:** Auto-triggers Composer → Code generated
- Core logic: Test-driven development for architecture.
[Visual: A 5-phase stepper diagram: Research → Ask → Draft → Review → Build. Each step has a clean icon. Use the Cursor dark theme colors.]
[Speech: Plan Mode is for when you need to think before you code. You hit Shift+Tab, and instead of writing code, the AI writes a markdown plan. You iterate on the plan, and only when it's perfect do you hit "Build." It's test-driven development for architecture.]

---

## Slide 15: Terminal: CLI Agent
- **Output Monitor:** Monitors terminal output for errors automatically
- **Auto-Fix:** "Add to Chat" button instantly fixes stack traces
- **Natural Language:** "Zip files >10MB" → `find -size +10M | zip`
- Core insight: The terminal is no longer a black box; it's a conversation partner.
[Visual: A terminal window showing a red error message. A glowing "Auto-Fix" button appears next to it. Below, a natural language query "Fix this" results in a corrected command.]
[Speech: The terminal is often where beginners get stuck. Cursor watches your terminal. If you get an error, one click fixes it. You can also just ask it to "zip all files larger than 10MB" and it writes the bash command for you.]

---

## Slide 16: Lecture Objectives
- **Evolution:** Crisis → AI-Native Rupture → Vibe Coding
- **Foundations:** RAG → Shadow Workspace → Speculative Edits
- **Capabilities:** Tab → Composer → Plan → Terminal
- **Context:** @ Symbols → .cursorrules → .cursorignore
- **Nervous System:** MCP & Skills → Clawdbot Deep-Dive
- **Conclusions:** The New Developer Skills
[Visual: A vertical timeline diagram with icons for each section. A progress bar at the bottom shows "progress bar 16/31". Current section "Context" is highlighted.]
[Speech: Capabilities are great, but context is king. How do we tell the AI what matters? We use the @ symbols, .cursorrules, and .cursorignore.]

---

## Slide 17: Context: @ Taxonomy
- **@Files:** Reference specific files for focused refactoring
- **@Codebase:** RAG Search for broad questions like "Where's auth?"
- **@Web:** Live Internet access for latest docs (e.g., Next.js 14)
- **@Docs:** Indexed documentation sets for libraries like Stripe
- **@Git:** Access commit history to understand recent changes
- Core insight: Precision context prevents hallucination.
[Visual: A circular "Context Wheel" with the @ symbol in the center. Spokes point to icons for Files, Codebase, Web, Docs, and Git. Clean, professional icons.]
[Speech: The @ symbol is your precision tool. Don't just say "fix the bug." Say "fix the bug in @auth.ts using patterns from @docs." The more specific your context, the better the result.]

---

## Slide 18: .cursorrules: Prompt the IDE
- **System Prompt:** A persistent prompt (.mdc + globs) for the whole project
- **Tech Stack:** Enforce React, Tailwind, or Vitest standards globally
- **Consistency:** Commit to repo to ensure team-wide alignment
- Core insight: Codify your best practices so the AI never forgets them.
[Visual: A screenshot of a `.cursorrules` file on the left, and a "Team Alignment" icon on the right. An arrow shows the rules being applied to all AI interactions.]
[Speech: .cursorrules is your project's constitution. You define your coding standards once—"always use functional components"—and the AI follows them forever. It ensures that every line of code generated matches your team's style.]

---

## Slide 19: .cursorignore: Strategic Ignorance
- **Security:** Block secrets, PII, and binaries from being indexed
- **Performance:** Use .cursorindexingignore to skip auto-indexing large files
- **Control:** You decide what the AI sees and what it doesn't
- Core insight: Better boundaries mean faster, safer AI.
[Visual: A "Shield" icon protecting a folder labeled "Secrets". Next to it, a "Speed" icon next to a folder labeled "Large Binaries". Both are marked with a red "Ignore" sign.]
[Speech: Just as important as what you show the AI is what you hide. Use .cursorignore to keep secrets safe and .cursorindexingignore to keep the AI from wasting time on massive binary files. It's about signal-to-noise ratio.]

---

## Slide 20: Lecture Objectives
- **Evolution:** Crisis → AI-Native Rupture → Vibe Coding
- **Foundations:** RAG → Shadow Workspace → Speculative Edits
- **Capabilities:** Tab → Composer → Plan → Terminal
- **Context:** @ Symbols → .cursorrules → .cursorignore
- **Nervous System:** MCP & Skills → Clawdbot Deep-Dive
- **Conclusions:** The New Developer Skills
[Visual: A vertical timeline diagram with icons for each section. A progress bar at the bottom shows "progress bar 20/31". Current section "Nervous System" is highlighted.]
[Speech: Now we enter the nervous system of the AI agent: the Model Context Protocol and Skills. This is how we connect the brain to the world and teach it new capabilities.]

---

## Slide 21: MCP & Skills: USB-C for AI
- **MCP Protocol:** Host (Cursor) → Client (AI) → Server (data)
- **Skills:** Packaged capabilities for domain-specific workflows
- **Connectivity:** Bridges data access (MCP) and procedural knowledge (Skills)
- **Standardization:** One protocol and one skill format to rule them all
- Core insight: AI can now "do" things with context.
[Visual: A "USB-C" plug diagram connecting three blocks: "Cursor (Host)", "AI (Brain)", and "External Systems (Data/APIs)". Use glowing blue connection lines.]
[Speech: Think of MCP and Skills as the USB-C port for AI. MCP is the physical connection — it lets AI plug into your database, calendar, and production environment. Skills are the software drivers — they teach AI how to actually use those connections effectively.]

---

## Slide 22: MCP Servers & Skill Marketplace
- **MCP Servers:** Integrations like GitHub, Sentry, Notion, and Slack
- **Skills Library:** Packages for code review, testing, and deployment
- **Installation:** Simple `npx` commands or community repository downloads
- **Ecosystem:** Combine hundreds of servers and skills like Lego blocks
- Core insight: Compose existing capabilities through data and knowledge.
[Visual: An "App Store" style grid showing icons for GitHub, Sentry, Notion, and various "Skill" icons like a magnifying glass (Review) and a rocket (Deploy).]
[Speech: And just like the App Store, there's a marketplace for both. MCP servers give you the connectors — GitHub, Sentry, Notion, Slack. Skills give you the know-how — how to conduct code reviews, write tests, deploy safely.]

---

## Slide 23: Clawdbot Real-World Wins
- **Negotiation:** Research car prices and email dealers automatically
- **Porting:** Ported CUDA code to ROCm in 30 minutes
- **Optimization:** Analyzed WHOOP data to optimize smart home settings
- **Automation:** Filled out complex insurance claims forms
- Core insight: Agents are force multipliers for human intent.
[Visual: A 4-panel grid showing icons for a Car (Negotiation), a Chip (Porting), a Smart Home (Optimization), and a Form (Automation). Each panel has a "Success" checkmark.]
[Speech: What does this look like in the real world? Clawdbot has negotiated car prices, ported complex GPU code, and even optimized health data. These aren't toy examples; they are real tasks that used to take humans hours or days.]

---

## Slide 24: Local-First: Mac Mini Stack
- **Unified Memory:** High bandwidth for running local models efficiently
- **Efficiency:** <10W idle power consumption for always-on agents
- **Privacy:** Keep your data local; use Tailscale for remote access
- Core insight: The future of AI is personal, private, and local.
[Visual: A photograph of a stack of Mac Minis in a clean, professional rack. A "Privacy Shield" icon and a "Low Power" leaf icon are overlaid on the image.]
[Speech: To run all this, you might want a local stack. A Mac Mini with unified memory is perfect. It sips power, keeps your data private, and is always on. It's your personal AI server farm in a closet.]

---

## Slide 25: Lecture Objectives
- **Evolution:** Crisis → AI-Native Rupture → Vibe Coding
- **Foundations:** RAG → Shadow Workspace → Speculative Edits
- **Capabilities:** Tab → Composer → Plan → Terminal
- **Context:** @ Symbols → .cursorrules → .cursorignore
- **Nervous System:** MCP & Skills → Clawdbot Deep-Dive
- **Conclusions:** The New Developer Skills
[Visual: A vertical timeline diagram with icons for each section. A progress bar at the bottom shows "progress bar 25/31". Current section "Conclusions" is highlighted.]
[Speech: We've covered a lot. Let's wrap up by defining what this means for you. What are the new skills you need to survive and thrive?]

---

## Slide 26: The New Developer Skills
- **Orchestration:** Mastering Composer to direct multi-file changes
- **Planning:** Thinking in systems and architecture (Plan Mode)
- **Context:** Knowing exactly what to feed the AI (@ Symbols)
- **Guidance:** Writing effective rules (.cursorrules) to constrain the AI
- **Integration:** Connecting tools and data via MCP
- Core insight: Shift from "Code Typing" to "Vibe Coding".
[Visual: A "Skill Pyramid". The base is "Integration", the middle is "Context & Guidance", and the top is "Orchestration & Planning". Professional, high-contrast colors.]
[Speech: The new skills aren't about typing faster. They're about orchestration, planning, and context management. You need to be good at guiding the AI, writing rules, and integrating tools. You are moving from a writer to an editor-in-chief.]

---

## Slide 27: Agent Best Practices
- **One Task, One Agent:** Each agent should handle a single, focused task
- **Atomic Commits:** Small, verifiable changes beat monolithic rewrites
- **Avoid Context Overload:** Long conversations degrade output quality
- **Reset When Full:** Start a new agent when context becomes cluttered
- **Parallel Isolation:** Multiple agents can work simultaneously on separate tasks
- Core insight: AI agents perform best with clear boundaries and fresh context.
[Visual: A "Lanes" diagram. Each lane shows a single agent working on a single task (e.g., "Fix Bug", "Add Test", "Update Docs"). A "Context Meter" shows them all in the green zone.]
[Speech: To succeed, you need discipline. Give each agent one task. Keep your commits small. If the context gets too long, reset. Treat your agents like junior developers: give them clear, manageable tasks, and they will shine.]

---

## Slide 28: Responsibility in AI Collaboration
- **Programmer Mindset:** Code error → "I wrote it wrong" → Fix the code
- **Leader Mindset:** Task failure → "Were my instructions clear?" → Refine directive
- **AI Mindset Shift:** AI error → Not "AI is stupid" → Optimize the prompt
- **Prompt Engineering:** Prompt = Code + Instruction; bugs need fixing
- Core insight: AI errors often stem from suboptimal inputs.
[Visual: A "Mirror" icon. A developer is looking into the mirror and seeing a "Prompt" instead of their face. The caption reads: "The prompt is the reflection of your intent."]
[Speech: Finally, take responsibility. If the AI fails, don't blame the tool. Ask yourself: "Was my prompt clear?" "Did I provide the right context?" You are the leader. If the team fails, it's on you to provide better direction.]

---

## Slide 29: Vibe Coding Done Right
- **Misconception:** "One sentence → AI does everything" is unrealistic
- **True Goal:** Focus on top-level architecture; delegate implementation
- **Spec First:** Complex tasks require complete design specs before execution
- **Workflow:** Write "Architecture Encyclopedia" → Create .cursorrules → Check
- Anti-pattern: Patching page-by-page leads to an endless loop of fixes.
- Core logic: **We architect, AI implements**.
[Visual: A "Top-Down" flow diagram. Top: "Human Architecture" (Large Block). Bottom: "AI Implementation" (Many small blocks). A red "X" over a "Patch-by-Patch" spiral diagram.]
[Speech: Vibe coding isn't magic. You can't just say "build an app" and walk away. You need to spec it out. Write the architecture docs first. Then let the AI implement. If you skip the design phase, you'll just get a mess faster.]

---

## Slide 30: Agent Workflow: Learn → Act → Update
- **Learn Design Docs:** Agent reads architecture, specs, and context before coding
- **Act — Coding Cycle:** Plan → Implement → Test
- **Update Design Docs:** If implementation deviates, sync back to docs
- **Loop:** Each agent iteration improves both code and documentation
- Anti-pattern: Coding without reading specs leads to drift.
- Core insight: Documentation is the source of truth for the AI.
[Visual: A circular "Sync Loop" diagram. Three icons: "Docs", "Plan", and "Code". Arrows show them constantly updating each other. Use glowing blue accents.]
[Speech: The workflow is a cycle. Learn the docs, act on the code, update the docs. If you change the code, update the docs. This keeps the AI aligned with your vision. It's a continuous loop of improvement.]

---

## Slide 31: Questions?
- **Thank You:** Open floor for Q&A
- **Contact:** xfcui.uw@gmail.com
- **Resources:** cursor.com, docs.cursor.com
[Visual: A minimalist "Open Mic" icon in the center. Contact info and resource links are neatly arranged at the bottom. Professional university branding.]
[Speech: Thank you for your time. I'm happy to take any questions you might have about Cursor, AI-native development, or how to get started.]

---

## Appendix: Global Visual Requirements
- **Theme:** Cursor dark mode (#0D1117 background, #58A6FF accents, #C9D1D9 text)
- **Fonts:** JetBrains Mono (titles, 48-60pt bold), Inter (body, 24-32pt)
- **Layout:** 35/65 title/body split (left title+icon, right content); 16:9 aspect
- **Animations:** Subtle fade-ins (bullets sequential, 0.5s); no spins/transitions
- **Icons:** Feather icons (e.g., code, brain, rocket) in #58A6FF, 64px
- **Diagrams:** Excalidraw-style (simple lines/boxes, monochromatic + accents)
- **Balance:** Max 5 bullets/slide; tables striped (#161B22/#0D1117); 40% visual space
