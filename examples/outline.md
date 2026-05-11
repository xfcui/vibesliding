# PPT Outline: Programming at the Speed of Thought

---

## Slide 1: Title & Abstract
- **Title:** Programming at the Speed of Thought
- **Sub-Title:** Cursor and AI-Native Development Revolution
- **Presenter:** Xuefeng Cui, Shandong University
- Core insight: We are moving from the era of typing code to the era of programming at the speed of thought.
[Visual: Cinematic 16:9 title slide matching the generated reference; upper-left white title stack with generous negative space; foreground oversized Cursor pointer on the left projecting a cyan beam through dense code-noise toward translucent IDE panels and a glowing AI-brain network on the right; bottom-left presenter lockup only; dark navy gradient, violet network sparks, no watermark or fake UI text.]
[Speech: Welcome everyone. Today I want to frame software development as a change in interface. For decades, programming meant translating an idea in your head into syntax one keystroke at a time. The editor helped with highlighting, autocomplete, and debugging, but the center of gravity was still the human typing. Cursor and the broader agentic toolchain change that center of gravity. The developer increasingly describes intent, supplies context, reviews plans, and steers execution, while the machine handles more of the mechanical translation. That is what I mean by programming at the speed of thought. It does not mean the AI magically replaces engineering judgment. It means the slowest part of the workflow is shifting from typing to thinking clearly. In this talk, we will move from the problem with old AI sidecars, into Cursor's AI-native architecture, and then into the practical discipline required to use agents safely and effectively.]

---

## Slide 2: Hook: Clawdbot's iPhone Moment
- **Solo Scale:** Peter Steinberger (PSPDFKit, $119M exit) built Clawdbot entirely solo
- **Swarm Architecture:** Orchestrated 3-8 parallel AI agents for atomic commits
- **Velocity:** Achieved 8,400+ commits and 116,000+ GitHub stars in just ~11 days
- Core insight: One developer can now output the work of an entire engineering team.
[Visual: Three-panel cinematic storyboard on a dark neon background; left panel shows a solo developer silhouette at a laptop, center panel shows 3-8 glowing agent lanes as terminal panes producing small commit cards, right panel shows a star counter, compact Mac Mini stack, and abstract lobster mascot energy burst; connect panels with one cyan cursor beam; minimal readable labels, no real brand logos.]
[Speech: To make this concrete, start with the Clawdbot story. Peter Steinberger was not an unknown beginner; he had already built PSPDFKit and sold it for a major exit. Yet when he returned to building, the striking part was not that an experienced engineer wrote a lot of code. The striking part was how he changed the shape of the work. He ran multiple agents in parallel, each with a narrow job, each producing small commits, while he acted more like a director than a typist. The project went viral because people saw an AI assistant that actually did things: it used the shell, drove a browser, remembered sessions, and operated on a local machine. That is why people called it an iPhone moment. Not because every detail was perfect, but because the interaction model suddenly felt different. One person, with disciplined agent orchestration, could create the visible output of a small team.]

---

## Slide 3: Crisis: Sidecar Limits (Copilot/VS Code)
- **Traditional Model:** Developer types syntax manually at typing speed
- **Context Isolation:** Tools like Copilot operate as "sidecars" — separate assistants that sit beside your editor but lack full access to your codebase state, terminal, or file system
- **Mechanical Latency:** Constant copy-pasting creates context-switching friction
- **Reactive Nature:** Tools wait for prompts instead of predicting intent
- Anti-pattern: We are limited by the speed of typing, not the speed of thought.
[Visual: Split-screen workflow bottleneck diagram; left side contains a conventional editor window and detached chat sidecar linked by many thin copy-paste arrows, with a red latency meter and tired cursor trail; right side is mostly dark empty space reserved for the coming AI-native reveal; cyan accents are muted here to make the friction feel constrained.]
[Speech: Before we celebrate the new model, we need to understand the old ceiling. Early AI coding assistants were powerful, but they mostly behaved like sidecars. They sat beside the editor, waiting for you to copy a stack trace, highlight a function, paste a snippet, or explain project context that the tool could not see by itself. That creates two kinds of latency. Mechanical latency is the visible friction: selecting text, moving between windows, applying diffs, and fixing imports. Cognitive latency is quieter but more expensive: every context switch forces you to reload the problem in your head. The result is that the AI may be faster than typing, but the workflow is still organized around manual handoffs. You are not yet programming at the speed of thought; you are programming at the speed of copying enough context into a separate assistant. Cursor's core claim is that this boundary is the real bottleneck.]

---

## Slide 4: AI-Native Rupture: Cursor Forks VS Code
- **Deep Integration:** Not an extension, but a modified runtime intervening in rendering
- **File System Events:** Custom handling of file changes for immediate AI awareness
- **Window Management:** AI controls the window layout for diffs and chats
- **Vector Embedding:** Continuous codebase indexing for instant semantic retrieval
- **Action Prediction:** Predicts next *action* via cursor trajectory, not just text
- Core logic: Deep integration allows the AI to intervene at the kernel level of the IDE.
[Visual: Layered architecture cutaway in dark neon style; bottom layer is a generic code editor foundation, middle layer is an AI-native host glowing cyan, top layer fans into four channels: rendering, file events, terminal, semantic index; the sidecar bubble from the previous slide dissolves into the host layer; use translucent panels and connector lines, not dense text.]
[Speech: Cursor's important design choice was to stop treating AI as a guest and start treating it as part of the host environment. By forking VS Code, Cursor gained control over the places where an extension is usually constrained: rendering, file-system awareness, window management, diffs, and terminal interaction. That means the assistant can see more of the same state the developer sees. It can know that a file changed, that a linter complained, that the cursor moved, or that a multi-file edit is underway. This is why the phrase AI-native matters. It is not just a branding term for a smarter autocomplete. It means the editor itself has been rebuilt around continuous context and action. The analogy I like is not "a chatbot inside an IDE." It is closer to an IDE whose nervous system includes a model. Once the model is inside the loop, it can predict actions, verify changes, and coordinate work across the project.]

---

## Slide 5: Vibe Coding: Syntax Abstraction
- **Intent Focus:** Developers focus on architecture ("secure login page")
- **AI Translation:** AI handles the syntax; planning and coding collapse into one
- **Multi-file Scope:** Refactors happen across the entire codebase via natural language
- **Friction Removal:** "Speed of thought" means zero latency between idea and execution
- Core insight: You are no longer a typist; you are an architect.
[Visual: Horizontal intent-to-software pipeline; left side shows a glowing human thought cloud and prompt bubble, center shows a plan card and diff preview, right side shows a polished app screen emerging from the cyan beam; faded code texture stays in the background as noise being abstracted away; include a small caution tag "clarity still matters" as the only extra text.]
[Speech: This is where the phrase vibe coding enters the story, but I want to use it carefully. The best version of vibe coding is not laziness. It is not "say one sentence and hope the machine builds a company." It is a change in abstraction level. Instead of spending most of your attention on syntax, you spend more attention on intent, architecture, constraints, and review. You might say, "Build a secure login flow using the existing auth helpers, add tests, and follow the patterns in this folder." The AI translates that into files, imports, handlers, and edge cases. In Clawdbot's world, Peter called this "just talk to it," but the hidden discipline was that he used small prompts, narrow tasks, screenshots, and rapid feedback. So the job changes. You become less of a typist and more of an editor, architect, and reviewer. The quality of the output depends on the quality of your direction.]

---

## Slide 6: Lecture Objectives
- **Evolution:** Understand why sidecar assistants hit a ceiling and why AI-native IDEs change the workflow.
- **Foundations:** **Study the machinery that makes Cursor feel aware, safer, and fast: RAG, Shadow Workspace, and speculative edits.**
- **Capabilities:** Connect technical foundations to the daily controls developers actually use: Tab, Composer, Plan, Browser, and Terminal.
- **Context:** Learn how explicit references, rules, and ignore files shape what the AI knows.
- **Nervous System:** See how MCP and Skills turn a coding assistant into a tool-using agent.
- **Conclusions:** Translate the technology shift into new developer habits and responsibilities.
[Visual: Six-station roadmap on a single cyan beam crossing a dark navy grid; stations are Evolution, Foundations, Capabilities, Context, Nervous System, Conclusions, with Foundations enlarged and bracketed by a bright glow; progress bar 6/32 in the lower right; use tiny memory icons from earlier slides and keep all secondary labels subdued.]
[Speech: Here is the map for the rest of the session. We have started with the evolution: why sidecar assistants hit a ceiling, why Cursor's fork of VS Code matters, and why vibe coding is really an abstraction shift. Now we move into the machinery that makes the experience feel possible. The next three ideas are the technical foundation: retrieval-augmented generation, the Shadow Workspace, and speculative edits. They answer three practical questions. First, how does the AI know enough about a large codebase without stuffing the entire repository into the prompt? Second, how does it reduce hallucinated code that looks plausible but does not type-check? Third, how does it apply big changes quickly enough that you stay in flow? Keep those questions in mind. The goal is not to memorize implementation trivia. The goal is to understand the failure modes, because once you know how the engine works, you can steer it much more effectively.]

---

## Slide 7: Foundation 1: RAG Context Engine
- **LLM Constraints:** Models have a hard limit of 128k-200k tokens
- **Semantic Chunking:** Code is broken into classes/functions and converted to vectors
- **Merkle Trees:** Syncs only changes (hash diffs) to keep index fresh
- **Efficiency:** Retrieval happens in seconds even for massive repositories
- Core logic: Relevant context is retrieved instantly, bypassing token limits.
[Visual: Codebase retrieval system diagram; left side shows a wall of files breaking into function and class cards, center converts cards into a constellation of vector dots, right side shows only selected cards entering a model context window through a cyan query beam; add a small Merkle tree sidebar with only changed leaves glowing violet.]
[Speech: The first foundation is the context engine, usually described as RAG: retrieval-augmented generation. A model cannot simply hold every file in a serious repository in its active context. Even with very large context windows, dumping everything into the prompt is slow, expensive, and noisy. Cursor's answer is to index the codebase. It breaks code into meaningful chunks like functions, classes, and modules, turns those chunks into embeddings, and stores them in a searchable semantic space. Then when you ask, "Where is authentication handled?" Cursor can retrieve the relevant pieces even if the exact word authentication does not appear everywhere. The Merkle tree idea matters because projects are constantly changing. Instead of re-indexing the whole repository after every edit, Cursor can detect which chunks changed and sync only those. The practical takeaway is simple: the AI is only as good as the context it retrieves, so precise questions and healthy project structure improve the answer.]

---

## Slide 8: Foundation 2: Shadow Workspace
- **Hallucination Fix:** A hidden background editor runs code to verify it
- **Verification Loop:** Proposal → LSP/linter validation → Correction → Apply
- **Agent Concurrency:** Future kernel-level folder proxy for parallel agents
- Core insight: The AI checks its own work before you ever see it.
[Visual: Dark theater metaphor for verification; foreground main editor is a clean lit stage, background backstage Shadow Workspace applies a proposed diff against three gates: LSP, type checker, linter; red error sparks turn green before the diff steps into the spotlight; use translucent curtains and cyan backstage glow.]
[Speech: The second foundation is the Shadow Workspace. Anyone who has used AI coding tools has seen confident wrong code: a variable that does not exist, a type that does not match, an import path that almost sounds right. The Shadow Workspace is Cursor's answer to that class of problem. Before a proposed edit becomes visible in the main editor, Cursor can apply it in a hidden workspace and let the language server, linter, and type checker react. If the code violates the local rules of the project, that feedback can be sent back into the model before the user ever sees the final proposal. This does not prove the logic is correct. A linter cannot tell you whether the business requirement was misunderstood. But it removes a huge amount of syntax-level noise. Think of it as backstage rehearsal. The AI tries the change, hears the compiler complain, adjusts the line, and only then brings the performance onto the main stage.]

---

## Slide 9: Foundation 3: Speculative Edits
- **High Speed:** Fireworks AI partnership delivers 1,000 tokens/sec (~3,500 chars/sec)
- **Deterministic Fill:** Uses n-grams + file state for unchanged sequences
- **Parallel Verification:** Multiple possibilities are checked in parallel
- **Fast Apply:** Powers the instant "Apply" feature for large diffs
- Core insight: Speed matters because latency breaks flow.
[Visual: Two-lane latency comparison; upper lane shows slow typewriter-style token streaming crawling across a dim timeline, lower lane shows Fast Apply jumping from proposed diff to completed file through a bright cyan warp line; unchanged code regions appear as stable ghost blocks, edited regions pulse violet; one small callout explains that most code stays the same.]
[Speech: The third foundation is speed. This sounds superficial until you notice how fragile flow state is. If the model takes too long to apply an edit, your brain starts doing something else: checking messages, second-guessing, or losing the thread of the design. Cursor's speculative edit strategy is built around a coding-specific observation: when editing software, most of the file usually stays the same. You are not generating a novel from a blank page; you are changing a few regions while preserving a lot of surrounding structure. Cursor can use the current file state and deterministic patterns to speculate long unchanged sequences, then ask the stronger model to verify them in parallel. That is how Fast Apply can feel almost instant for large diffs. The point is not only benchmark bragging. Low latency changes behavior. When edits arrive quickly, you are more willing to iterate, review, and keep the architecture in your head.]

---

## Slide 10: Meta-Skill: Architect & Contractor
- **Objection:** "Just use it—no need to understand how it works"
- **Risks:** RAG irrelevance, Shadow syntax-only, no logic check
- **Truth:** Powerful AI amplifies expertise (computational thinking)
- **Model:** Human architects design; AI contractors execute
- Core insight: You must understand the tool to master the craft.
[Visual: Futuristic construction site inside an IDE grid; human architect silhouette holds a glowing blueprint while AI contractor drones assemble code modules with cranes; three small warning cones mark bad retrieval, syntax-only validation, and wrong objective; blueprint is the brightest shared object, reinforcing human direction over machine motion.]
[Speech: At this point, someone might reasonably ask: why do we need to understand any of this? Why not just use the tool and move faster? My answer is that powerful tools amplify both skill and confusion. If you understand RAG, you know that a bad answer may come from bad retrieval, not a stupid model. If you understand the Shadow Workspace, you know that passing type checks does not mean the feature is logically correct. If you understand speculative edits, you know why fast feedback encourages small iteration rather than giant blind rewrites. The right mental model is architect and contractor. The human is responsible for goals, constraints, tradeoffs, and final acceptance. The AI can execute at astonishing speed, but it needs a well-defined job site. In Clawdbot's story, the magic was not that Peter abandoned expertise. It was that expertise let him direct many fast workers without losing control of the design.]

---

## Slide 11: Lecture Objectives
- **Evolution:** Understand why sidecar assistants hit a ceiling and why AI-native IDEs change the workflow.
- **Foundations:** Use RAG, Shadow Workspace, and speculative edits as the technical vocabulary for understanding Cursor's behavior.
- **Capabilities:** **Map Cursor's core controls to different scales of work: Tab, Composer, Plan, Browser, and Terminal.**
- **Context:** Learn how explicit references, rules, and ignore files shape what the AI knows.
- **Nervous System:** See how MCP and Skills turn a coding assistant into a tool-using agent.
- **Conclusions:** Translate the technology shift into new developer habits and responsibilities.
[Visual: Roadmap slide continuing the cyan beam language; Capabilities station is highlighted and expands into a translucent control dashboard with five clean tiles: Tab, Composer, Plan, Browser, Terminal; each tile has one icon and one short label; progress bar 11/32 lower right; background keeps the AI-brain network faint and unobtrusive.]
[Speech: Now that we have looked under the hood, we can move from the engine to the controls. This section is about the daily interface: the features you actually touch while building software. Cursor Tab is about prediction at the edit level. Composer is about moving from a single file to a project-wide change. Plan Mode is about separating thinking from building when the task is too risky to improvise. The internal browser closes the loop between code and user-visible behavior. Terminal integration brings command-line failures into the same feedback loop as code. Notice how these correspond to different levels of work. A tab completion might save seconds. A Composer run might save half an hour. A browser check might catch the bug that static analysis missed. A good plan might save days by preventing the wrong architecture. The theme of this section is choosing the right control for the scale of the problem.]

---

## Slide 12: Cursor Tab: Predictive Intent
- **Beyond Ghost Text:** Cursor jumps to where you want to edit, diff-awareness
- **Training Data:** Trained on diff histories (delete/rewrite) to predict edits
- **Smart Paste:** Automatically adjusts indentation and variable names
- Core insight: The editor predicts your *intent*, not just your next character.
[Visual: Three-frame micro-demo in a single IDE canvas; frame 1 shows a function signature changing, frame 2 shows the cursor beam jumping to a related call site, frame 3 shows a rename suggestion appearing as glowing diff text; faint diff-history trails arc behind the frames to show learned edit patterns; keep code snippets abstract and readable.]
[Speech: Cursor Tab is the smallest unit of this new workflow, but it reveals the philosophy clearly. Traditional autocomplete predicts text after the cursor. Cursor Tab tries to predict the next edit in the developer's intent. That might mean filling in a line, but it might also mean jumping to another location, deleting stale code, renaming a variable, or updating a call site after a function signature changes. The key training signal is not just source code; it is diff history. Real programming is full of edits, reversals, and coordinated changes, so the model learns patterns of transformation. Smart Paste is a good example because it solves a tiny but common pain: pasted code rarely matches the destination context perfectly. Indentation, names, imports, and local conventions need adjustment. Cursor Tab turns that cleanup into a prediction. This is not glamorous, but it is important. Many small frictions disappearing throughout the day can matter as much as one dramatic agent demo.]

---

## Slide 13: Composer Workflow: Multi-File Magic
- **Cmd+I Orchestrator:** The bridge from Chat to actual Software
- **1. Describe:** "Dashboard w/ sidebar @Folders/ui + React Query"
- **2. AI Scans:** Checks dependencies (@Codebase), generates files (Layout.tsx)
- **3. Visual Plan:** Dependency graph preview → Approve/Edit
- **4. Execute:** Create/integrate/verify → Diff view
- Core insight: You're editing the project, not just a file.
[Visual: Composer cockpit interface in dark mode; top prompt bar contains a short natural-language task, center shows a dependency graph of file cards moving through scan, create, modify, verify, diff states, right side shows a human approval checkpoint before execution; cyan beam links prompt to graph, with violet pulses on modified files.]
[Speech: Composer is where the interaction stops feeling like editing a file and starts feeling like directing a project. Imagine asking for a dashboard layout that uses the existing design system, adds a sidebar, wires a route, and fetches data with the project's normal query library. In a conventional workflow, you would create files, search for examples, copy imports, update routing, and run the app. In Composer, the assistant can scan the codebase, identify reusable components, create the missing pieces, and show you a plan or graph of what it intends to touch. The important word is review. Multi-file magic is useful only if you keep visibility into the blast radius. This is one lesson from the Clawdbot story: speed came from parallel work, but safety came from atomic commits and narrow tasks. Use Composer when the change has project shape, but still insist on a readable plan and a diff you can reason about.]

---

## Slide 14: Plan Mode Workflow: Think → Build
- **Shift+Tab:** Decouple Planning from Typing
- **1. Agent Mode:** Shift+Tab: "Design user dashboard API"
- **2. Research:** Scans @Codebase/@Docs → Asks: "REST or GraphQL?"
- **3. Draft MD Plan:** Steps/files/APIs → Edit directly
- **4. Review:** Refine architecture → Approve
- **5. Build:** Auto-triggers Composer → Code generated
- Core logic: Test-driven development for architecture.
[Visual: Plan Mode workspace as a calm design review surface; left column shows research notes and referenced files, center shows a markdown implementation plan with editable checkboxes, right column shows a locked Build button awaiting review; a bridge labeled Think to Build crosses from notes to execution; use less glow and more negative space to signal deliberation.]
[Speech: Plan Mode is the antidote to the most common failure in AI coding: letting the agent start implementing before the problem is understood. In Plan Mode, the assistant researches first. It scans code, reads docs, and should ask clarifying questions when the architecture has real choices. Then it produces a markdown plan: files to touch, APIs to change, tests to run, and risks to watch. You can edit that plan directly before any code is written. This is valuable because natural language is cheaper to correct than a messy implementation. If the plan says REST and you need GraphQL, fix it there. If it missed authorization, add it there. Only after the plan matches your intent do you move into build. I think of this as design-review discipline compressed into the editor. Vibe coding without planning can become faster chaos; Plan Mode turns speed into directed motion.]

---

## Slide 15: Browser: Visual Feedback Loop
- **In-IDE Preview:** Run and inspect the application without leaving the coding workspace
- **Page Evidence:** DOM snapshots, screenshots, console logs, and network requests become debugging context
- **Interaction Testing:** Click, type, navigate, and verify flows the way a user actually experiences them
- **Design Alignment:** Compare generated UI against the intended layout before accepting the implementation
- Core insight: The browser turns user-visible behavior into agent-readable evidence.
[Visual: Three-panel feedback loop with editor, browser preview, and agent chat; the browser panel is the focal object, showing a highlighted UI region plus small evidence overlays for screenshot, console, and network; cyan arrows cycle through change code, inspect page, capture evidence, fix; keep the panels translucent and aligned on one workspace grid.]
[Speech: The internal browser is easy to underestimate because it looks like a convenience feature, but it changes the feedback loop. Many software bugs are not visible in a code diff. A component may compile and still render incorrectly. A button may exist and still be hidden behind a modal. A flow may pass unit tests and still fail because a browser event, network request, or layout constraint behaves differently in the real page. When the browser lives inside the development loop, the agent can reason from evidence closer to what the user sees: screenshots, DOM structure, console messages, network failures, and interaction results. This is especially powerful for front-end work, where correctness is partly visual and partly behavioral. The safety habit is the same as before: use deliberate checks. Ask the agent to open the page, inspect the relevant region, click the actual control, and explain what evidence proves the fix. The browser becomes a test surface, not just a preview window.]

---

## Slide 16: Terminal: CLI Agent
- **Output Monitor:** Monitors terminal output for errors automatically
- **Auto-Fix:** "Add to Chat" button instantly fixes stack traces
- **Natural Language:** "Zip files >10MB" → `find -size +10M | zip`
- Core insight: The terminal is no longer a black box; it's a conversation partner.
[Visual: Terminal-to-agent diagnostic flow; left terminal panel shows a failing test block with one highlighted error line, center chat panel extracts the stack trace, right editor panel points to the source location and suggested fix; below, a mini natural-language command becomes a safe command preview with an approval gate; dark console green plus cyan accents.]
[Speech: The terminal matters because many real software problems are not visible in the editor. They appear as test failures, dependency conflicts, permission errors, migration logs, or confusing shell syntax. Cursor's terminal integration closes that loop. When a command fails, the output can be sent back into chat with the relevant stack trace and project context, so the assistant can connect the failure to the source code. This is especially helpful for beginners, but it is not only a beginner feature. Senior engineers also waste time translating noisy build logs into the one line that matters. Natural-language shell is the other side of the same idea. You can describe an operation, such as finding large files or staging a specific set of changes, and ask for the command. The safety habit is to preview before running. The terminal agent is powerful because it touches the operating system; that power should be paired with explicit approval and clear intent.]

---

## Slide 17: Lecture Objectives
- **Evolution:** Understand why sidecar assistants hit a ceiling and why AI-native IDEs change the workflow.
- **Foundations:** Use RAG, Shadow Workspace, and speculative edits as the technical vocabulary for understanding Cursor's behavior.
- **Capabilities:** Map Cursor's core controls to different scales of work: Tab, Composer, Plan, Browser, and Terminal.
- **Context:** **Learn how to steer the AI's attention with references, standing rules, and explicit exclusions.**
- **Nervous System:** See how MCP and Skills turn a coding assistant into a tool-using agent.
- **Conclusions:** Translate the technology shift into new developer habits and responsibilities.
[Visual: Roadmap slide with Context highlighted; a wide noisy repository cloud narrows through a cyan spotlight into four crisp cards: files, docs, git history, rules; progress bar 17/32 lower right; background repeats the title-slide code wall but dimmed, showing context selection as attention control.]
[Speech: We have now seen powerful controls, but controls alone do not guarantee good output. The decisive ingredient is context. A brilliant model with the wrong files is like an expert consultant dropped into a meeting with no background. It will sound confident and still miss the point. This section is about steering attention: what to show the AI, what to hide from it, and what standing instructions it should carry across the project. Cursor gives us three major levers. The @ symbols let us point at files, folders, docs, web pages, codebase search, and git history. Rules let us encode team standards so we do not repeat the same instructions every time. Ignore files let us protect secrets and reduce noise. If the earlier sections were about speed, this one is about signal. Good context management is the difference between an agent that guesses and an agent that works inside your actual system.]

---

## Slide 18: Context: @ Taxonomy
- **@Files:** Reference known files when the task needs precise local evidence, such as refactoring one module or explaining a specific test.
- **@Codebase:** Ask broad discovery questions when you do not know where behavior lives, letting semantic search find relevant chunks.
- **@Web:** Pull current external information when framework behavior or API syntax may have changed since the model was trained.
- **@Docs:** Use indexed library documentation when you need stable vendor guidance without leaving the IDE.
- **@Git:** Bring commit history into the prompt when the reason for a design choice is likely hidden in past changes.
- Core insight: Precision context prevents hallucination.
[Visual: Context wheel on dark navy background; @ symbol sits at the center with six neon spokes to Files, Folders, Codebase, Docs, Web, Git; right side compares a vague prompt as gray noise against a precise prompt as a glowing cyan card; use beam focus and fading particles to show hallucination risk dropping as context becomes explicit.]
[Speech: The @ symbol is a small interface detail with a large behavioral effect. It lets you move from vague prompting to explicit context stuffing. Instead of saying, "fix the auth bug," you can say, "look at @auth.ts, compare it with @tests/auth.test.ts, and use the API contract in @Docs." That changes the problem the model is solving. @Files is for known targets. @Codebase is for discovery when you do not know where the logic lives. @Docs is for stable library guidance. @Web is for current information beyond the model's training cutoff. @Git is underrated because history often explains why strange code exists. The practical discipline is to match the context source to the question. If you need a local convention, use files or folders. If you need the latest framework syntax, use web or docs. Precision context does not just improve accuracy; it also reduces hallucination because the model has less need to invent missing facts.]

---

## Slide 19: .cursorrules: Prompt the IDE
- **System Prompt:** Rules act like a persistent project prompt, so the assistant starts each task with the team's conventions already loaded.
- **Scoped Standards:** `.mdc` files and globs let frontend, backend, tests, and docs receive different guidance instead of one generic rule.
- **Tech Stack Discipline:** Rules can enforce choices such as React patterns, Tailwind usage, Vitest style, logging wrappers, and forbidden legacy APIs.
- **Team Consistency:** Committing rules to the repository makes AI behavior more repeatable across teammates and future agents.
- Core insight: Codify your best practices so the AI never forgets them.
[Visual: Project constitution metaphor rendered as a glowing rules document hovering over the repository; scoped glob rings send different cyan instruction beams to frontend, backend, tests, and docs file clusters; several teammate silhouettes receive the same guidance; use minimal code labels and a clean stamped approval mark.]
[Speech: Rules are how you stop repeating yourself. Every project has conventions that are obvious to the team but invisible to a generic model: use functional React components, prefer React Query for server state, write Vitest tests next to components, never hardcode secrets, use this logging wrapper, avoid that legacy module. If those instructions live only in human memory or scattered chat prompts, the AI will drift. A `.cursorrules` or `.mdc` rule file turns those conventions into persistent guidance. The glob support matters because different parts of a system need different rules. Frontend files, migration scripts, tests, and infrastructure code should not all receive the same advice. The deeper idea is that rules convert taste into infrastructure. When a new teammate or agent enters the project, the standards are already present. This is especially important for agentic workflows because the faster code is generated, the more expensive inconsistency becomes if you catch it late.]

---

## Slide 20: .cursorignore: Strategic Ignorance
- **Security Boundary:** Ignore secrets, credentials, PII, and private exports so tool-using agents do not accidentally expose sensitive data.
- **Performance Boundary:** Exclude generated files, binaries, logs, and large outputs so retrieval focuses on source material instead of noise.
- **Indexing Control:** Use `.cursorignore` and `.cursorindexingignore` deliberately because the index shapes what the assistant treats as relevant context.
- **Human Ownership:** The developer decides what the AI can see, which makes context boundaries part of the system design.
- Core insight: Better boundaries mean faster, safer AI.
[Visual: Two-gate boundary diagram; first gate is Security, blocking secrets, credentials, PII, and private exports with red shield icons; second gate is Performance, filtering generated files, binaries, logs, and output folders; after both gates, only clean source cards enter the cyan retrieval beam; visual tone should feel controlled and protective.]
[Speech: Context management also includes strategic ignorance. Not every file in a repository deserves to be visible to the AI. Some files are dangerous: secrets, credentials, customer data, private exports, or anything that could create compliance risk. Other files are simply noisy: build artifacts, generated code, binaries, huge logs, and output folders. `.cursorignore` and related indexing controls give you a way to draw boundaries. This is not only about performance, although performance matters. It is also about shaping what the model believes the project is. If the index is full of generated files, the assistant may retrieve irrelevant patterns. If secrets are available, an agent connected to tools has a larger blast radius. The Clawdbot security story makes this concrete: once agents can read files, send messages, and run commands, the boundary around what they can see becomes a real security control. Better boundaries produce faster, safer, more relevant assistance.]

---

## Slide 21: Lecture Objectives
- **Evolution:** Understand why sidecar assistants hit a ceiling and why AI-native IDEs change the workflow.
- **Foundations:** Use RAG, Shadow Workspace, and speculative edits as the technical vocabulary for understanding Cursor's behavior.
- **Capabilities:** Map Cursor's core controls to different scales of work: Tab, Composer, Plan, Browser, and Terminal.
- **Context:** Learn how to steer the AI's attention with references, standing rules, and explicit exclusions.
- **Nervous System:** **Understand how MCP and Skills connect the agent to external systems and repeatable workflows.**
- **Conclusions:** Translate the technology shift into new developer habits and responsibilities.
[Visual: Roadmap slide with Nervous System highlighted; central glowing AI brain sends cyan and violet nerve lines to tool nodes for database, browser, shell, GitHub, Slack, and skill cards; progress bar 21/32 lower right; keep labels tiny and let the network structure communicate connection and risk.]
[Speech: Up to now, we have mostly talked about how the AI understands and changes code. The next layer is broader: how the agent connects to the world. This is where MCP and Skills matter. A model by itself is mostly a reasoning engine. It can propose text, but it cannot query your database, inspect a GitHub issue, read a Sentry error, or operate a browser unless we provide controlled interfaces. MCP gives us a standardized way to expose those interfaces. Skills give the agent procedural knowledge: not just access to a tool, but guidance on how to use it well for a particular workflow. This is the nervous system metaphor. The brain is not enough; it needs senses and muscles. But every new nerve also adds risk. As we enter this section, keep both sides in mind: connectivity is what turns AI from chat into action, and governance is what keeps action from becoming chaos.]

---

## Slide 22: MCP & Skills: USB-C for AI
- **MCP Protocol:** Cursor hosts the agent, the agent discovers tool schemas, and MCP servers expose controlled access to external data or actions.
- **Skills:** Skills package workflow knowledge, so the agent knows how to use tools responsibly for a specific domain.
- **Connectivity:** MCP provides the data-access layer while Skills provide the operating procedure for turning access into useful work.
- **Standardization:** A shared protocol reduces one-off integrations and makes capabilities easier to compose, inspect, and govern.
- Core insight: AI can now "do" things with context.
[Visual: USB-C for AI metaphor with three clean layers; left layer is Cursor host, middle is agent client discovering tool schemas, right layer is MCP servers for GitHub, Postgres, Sentry, and Browser; skill cards snap onto the cable as operating instructions; use a single glowing connector cable across the slide and avoid crowded labels.]
[Speech: MCP is often described as USB-C for AI, and the analogy is useful. Before standards, every integration required a custom adapter: one-off code for a database, another for GitHub, another for Slack, another for a browser. MCP creates a shared protocol for discovering tools, describing inputs, and returning structured results. In Cursor, the host is the IDE, the client is the agent, and the server is the bridge to a data source or capability. Skills solve a slightly different problem. Having a database tool does not mean the agent knows your organization's safe query workflow. Having a browser tool does not mean it knows how to test a checkout flow responsibly. Skills package that procedural knowledge. Together, MCP and Skills let the AI do work with real context: fetch a schema, inspect an issue, run a diagnostic, or draft a PR. But because these tools touch real systems, permissions and review are not optional decoration; they are part of the architecture.]

---

## Slide 23: MCP Servers & Skill Marketplace
- **MCP Servers:** Connectors such as GitHub, Sentry, Notion, Slack, Postgres, and browsers give agents real senses and hands.
- **Skills Library:** Reusable packages for review, testing, deployment, release notes, and incident response encode proven workflows.
- **Installation:** Simple commands and community repositories lower the setup cost, but every install should be treated as a permission decision.
- **Ecosystem:** Servers and skills combine like modular capabilities, letting teams assemble workflows instead of rebuilding integrations.
- Core insight: Compose existing capabilities through data and knowledge.
[Visual: Modular capability marketplace wall; left half contains connector tiles for GitHub, Sentry, Postgres, Notion, Slack, and Browser, right half contains skill tiles for code review, CI fixing, release notes, testing, and deployment; center shows tiles snapping together like glowing blocks; include a subtle permission lock icon on each install path.]
[Speech: Once you have a standard connection layer, an ecosystem naturally appears. MCP servers become connectors: GitHub for issues and PRs, Sentry for production errors, Notion for documentation, Slack for team context, Postgres for data, browser automation for user-facing flows. Skills become reusable operating procedures: how to review code, how to triage CI, how to write tests, how to prepare a release, how to debug a production incident. This resembles an app store, but the more accurate mental model is composable capability. A connector gives access. A skill gives method. Together they let an agent perform a workflow that would otherwise require switching between many tools. The Clawdbot/OpenClaw ecosystem showed this pattern at community scale with hundreds of skills forming around local agents. The opportunity is huge, but so is the need for curation. Installing a random skill or server is like giving a plugin hands. Trust, scope, and permissions should be part of the installation decision.]

---

## Slide 24: Clawdbot Real-World Wins
- **Negotiation:** Research car prices and email dealers automatically
- **Porting:** Ported CUDA code to ROCm in 30 minutes
- **Optimization:** Analyzed WHOOP data to optimize smart home settings
- **Automation:** Filled out complex insurance claims forms
- Core insight: Agents are force multipliers for human intent.
[Visual: Four cinematic case-study cards arranged in a 2x2 grid; cards show dealer email negotiation, CUDA-to-ROCm code port, health-to-smart-home dashboard, and insurance form automation; each card uses the same mini flow: human intent, agent actions, verified outcome; connect all cards to one human approval node in the center.]
[Speech: The reason Clawdbot went viral was not only its architecture; it was the stories people told about outcomes. One story involved researching car prices, emailing dealerships, and negotiating while the user was doing something else. Another involved porting CUDA code to ROCm, a specialized engineering task that normally requires careful API knowledge. Others connected health data from WHOOP to smart-home adjustments, or automated the tedious work of collecting invoices and filing insurance claims. These examples are memorable because they cross the boundary from "AI helped me write text" to "AI completed a multi-step task in the world." They also reveal the pattern behind useful agents. The user gives intent and constraints. The agent gathers context, uses tools, takes actions, and reports back. The human still owns judgment and approval, especially when money, health, or credentials are involved. Real-world wins are force multipliers, not responsibility erasers.]

---

## Slide 25: Local-First: Mac Mini Stack
- **Unified Memory:** High bandwidth for running local models efficiently
- **Efficiency:** <10W idle power consumption for always-on agents
- **Privacy:** Keep your data local; use Tailscale for remote access
- Core insight: The future of AI is personal, private, and local.
[Visual: Local-first home-lab hero scene; compact Mac Mini stack glows in a dark closet rack beside a local data vault icon and low-power meter, while a secure tunnel line reaches a phone outside the home; place a small caution triangle at the network exit point; palette stays cinematic cyan with restrained violet highlights.]
[Speech: One surprising part of the Clawdbot story was hardware. People started buying Mac Minis because they wanted a local, always-on agent. The appeal is easy to understand. Apple Silicon gives efficient unified memory, low idle power, and enough local compute for many assistant workflows. A machine in your home can hold private data, run local services, keep sessions alive, and respond through secure tunnels like Tailscale. That feels very different from uploading everything to a cloud chatbot. It is the dream of sovereign AI: the model or agent comes to your data instead of your data going everywhere else. But the caution is just as important. The moment you expose a local agent through a tunnel, you have created a doorway into a system that may have shell access and personal credentials. Local-first is not automatically safe. It gives you control, but you must design authentication, tool permissions, and network boundaries with the same seriousness as any server.]

---

## Slide 26: Lecture Objectives
- **Evolution:** Understand why sidecar assistants hit a ceiling and why AI-native IDEs change the workflow.
- **Foundations:** Use RAG, Shadow Workspace, and speculative edits as the technical vocabulary for understanding Cursor's behavior.
- **Capabilities:** Map Cursor's core controls to different scales of work: Tab, Composer, Plan, Browser, and Terminal.
- **Context:** Learn how to steer the AI's attention with references, standing rules, and explicit exclusions.
- **Nervous System:** Understand how MCP and Skills connect the agent to external systems and repeatable workflows.
- **Conclusions:** **Turn speed, context, and tool access into practical developer habits instead of undirected hype.**
[Visual: Final roadmap slide with Conclusions highlighted; earlier section nodes collapse along the cyan beam into three large takeaway cards: speed, context, responsibility; progress bar 26/32 lower right; reduce visual noise, use calmer glow, and leave extra negative space to signal synthesis.]
[Speech: We are entering the final section, so let us compress what we have covered. The story began with a bottleneck: traditional tools forced developers to translate thought into syntax through slow manual loops. Cursor attacks that bottleneck by making AI part of the editor itself. Its foundations, from RAG to Shadow Workspace to speculative edits, explain why it can feel aware, safer, and fast. Its capabilities, from Tab to Composer to Plan Mode, Browser, and Terminal, give us controls at different scales of work. Context tools and rules remind us that output quality depends on what the AI sees and what instructions persist. MCP and Skills show how agents move from code generation into action. Now the question becomes personal and professional: what should a developer practice in this new environment? The answer is not "stop learning engineering." It is the opposite. The more leverage the agent has, the more valuable your judgment, taste, and responsibility become.]

---

## Slide 27: The New Developer Skills
- **Orchestration:** Break work into small agent-sized tasks, then use Composer and parallel agents without losing control of the design.
- **Planning:** Use Plan Mode and architecture thinking when the cost of building the wrong thing is higher than the cost of thinking first.
- **Context:** Choose the files, folders, docs, web references, and git history that make the model reason inside the real project.
- **Guidance:** Write rules that turn team standards into persistent constraints instead of repeating them in every prompt.
- **Integration:** Connect tools and data through MCP only when the workflow benefits from real external context and the permissions are justified.
- Core insight: The scarce skill shifts from code typing to judgment, context design, and review.
[Visual: Developer skill pyramid on a dark grid; foundation layer is Review, then Context, Guidance, Planning, and Orchestration at the top; on the left, an old typing-speed gauge fades into gray, while on the right a decision-quality gauge lights cyan; add subtle human silhouette overseeing agent lanes in the background.]
[Speech: The new developer skills are not replacements for programming; they are a re-weighting of what matters. Typing speed becomes less central. Decision quality becomes more central. Orchestration means decomposing work so agents can operate in parallel without stepping on each other. Planning means describing architecture before implementation when the task has real risk. Context management means knowing which files, docs, histories, and examples the model needs. Guidance means writing rules so good taste becomes repeatable. Integration means connecting the IDE to the systems where work actually happens: databases, issue trackers, CI, observability, and documents. Underneath all of that is review. You must be able to read diffs, recognize design drift, question assumptions, and decide whether the result is acceptable. In a world where code is cheap to generate, understanding becomes the scarce resource. The best developers will not be those who abdicate to AI, but those who can direct it with precision.]

---

## Slide 28: Agent Best Practices
- **One Task, One Agent:** Give each agent a narrow, testable assignment so it can finish with a readable diff and clear success criteria.
- **Atomic Commits:** Small commits make review, rollback, and parallel work safer than one large generated rewrite.
- **Avoid Context Overload:** Long conversations accumulate stale assumptions, failed attempts, and unrelated details that can distort later output.
- **Reset When Full:** Start a fresh agent when the existing chat stops helping the task more than it confuses it.
- **Parallel Isolation:** Multiple agents can work simultaneously when their folders, goals, and acceptance checks do not overlap.
- Core insight: AI agents perform best with clear boundaries and fresh context.
[Visual: Parallel agent runway diagram; four glowing lanes labeled bug fix, tests, docs, refactor move toward small atomic commit cards, while an overhead human control tower monitors context meters and collision boundaries; use clean lane separation and cyan approval lights at each lane endpoint.]
[Speech: Agent best practices sound simple because they are borrowed from good engineering management. Give one agent one clear task. Keep the blast radius small. Ask for atomic commits or isolated diffs. Avoid letting a single conversation accumulate every decision, every failed attempt, and every unrelated idea until the context becomes polluted. Reset when the agent's working memory is no longer helping. This is exactly why the Clawdbot development story matters. The velocity came from swarm programming, but the swarm was not random. Multiple terminal agents worked on separate pieces, and the human orchestrator kept the boundaries clear. You can think of agents as enthusiastic junior developers with perfect stamina and imperfect judgment. If you give them a vague mandate like "make everything better," they will create a mess with confidence. If you give them a narrow target, relevant context, success criteria, and a review loop, they can be extraordinarily useful.]

---

## Slide 29: Responsibility in AI Collaboration
- **Programmer Mindset:** When code fails, engineers inspect inputs, assumptions, and logic instead of blaming the computer.
- **Leader Mindset:** When delegated work fails, the first question is whether the goal, constraints, and acceptance criteria were clear.
- **AI Mindset Shift:** When an agent fails, treat the prompt, context, rules, and permissions as debuggable parts of the system.
- **Prompt Engineering:** A prompt is executable instruction plus context, so ambiguity and missing evidence behave like bugs.
- **Governance:** Tool access, credentials, and review checkpoints define how much damage a mistaken instruction can cause.
- Core insight: AI errors often stem from suboptimal inputs.
[Visual: Sober responsibility mirror scene; developer silhouette faces a reflective surface showing three layers: prompt, context, permissions; behind the mirror an AI agent waits at an approval gate with tool icons dimmed until authorized; use darker navy, less sparkle, and one cyan line to emphasize accountability.]
[Speech: A useful mindset shift is to treat an AI failure as a systems failure, not just a model failure. Sometimes the model is wrong. But often the prompt was ambiguous, the context was incomplete, the rules were missing, or the task was too large. A programmer who sees a bug in their own code does not only say, "the computer is stupid." They inspect the inputs, assumptions, and logic. Agent collaboration deserves the same maturity. This is even more important when tools have real permissions. In the OpenClaw security story, the danger was not that the model could talk. The danger was that it could act with the user's credentials, read files, use the browser, and operate when the human was not present. Responsibility means designing prompts, permissions, and review checkpoints so the agent's power is bounded by your intent. You are not merely chatting with software. You are delegating work to a system that can change things.]

---

## Slide 30: Vibe Coding Done Right
- **Misconception:** "One vague sentence makes the AI build everything" works for demos but collapses under real system complexity.
- **True Goal:** Humans should own architecture, constraints, and acceptance criteria while AI accelerates implementation details.
- **Spec First:** Complex tasks need design specs before execution because natural language is cheaper to correct than generated code.
- **Workflow:** Write an architecture encyclopedia, encode stable rules, delegate narrow implementation tasks, then verify with tests and review.
- Anti-pattern: Patching page by page creates a fast loop of fixes without a stable design.
- Core logic: **We architect, AI implements**.
[Visual: Split comparison with strong contrast; left side shows one vague prompt falling into a chaotic spiral of patch cards and red regression sparks, right side shows a top-down architecture spec feeding orderly implementation cards through tests, docs, and review checkpoints; use the cyan beam only on the disciplined right side.]
[Speech: Vibe coding done right is top-down. The misconception is that the best prompt is a single sentence that causes a finished product to appear. That can work for demos, but it does not scale to serious systems. The healthier pattern is to specify architecture, constraints, interfaces, and acceptance criteria first, then delegate implementation in pieces. For complex apps, this might mean writing an architecture encyclopedia, defining rules, describing data models, and deciding how tests should prove behavior. Once that structure exists, agents can fill in components, routes, tests, and migrations with much less drift. The anti-pattern is patch-by-patch development: ask for a page, fix a bug, ask for another page, fix three regressions, and slowly lose the design. AI makes that loop faster, which can feel productive while making the system worse. The core logic is simple: humans should own architecture; AI can accelerate implementation. When those roles are confused, speed becomes a liability.]

---

## Slide 31: Agent Workflow: Learn → Act → Update
- **Learn Design Docs:** The agent should read architecture, specs, rules, and relevant code before proposing changes.
- **Act — Coding Cycle:** The implementation loop should move from plan to code to tests, with evidence attached to each step.
- **Update Design Docs:** When implementation changes an assumption, the docs must be updated so future agents inherit the new truth.
- **Loop:** Each iteration should improve both the software and the written context that controls future AI work.
- Anti-pattern: Coding without reading specs leads to drift.
- Core insight: Documentation is the source of truth for the AI.
[Visual: Continuous Learn-Act-Update loop; circular flow moves from Docs to Plan to Code to Tests to Updated Docs, with an agent entering at Learn and exiting with both a commit card and documentation patch; source-of-truth document glows at the top of the loop; use cyan arrows with violet update pulses.]
[Speech: The operational workflow I recommend is Learn, Act, Update. First, the agent learns: it reads the design docs, rules, relevant files, and recent history. This prevents it from treating the codebase as a blank canvas. Second, it acts: it proposes a plan, implements the change, and runs the appropriate checks. Third, it updates: if the implementation changed an assumption, introduced a new convention, or revealed that the docs were stale, the documentation must be brought back into alignment. This loop matters more with AI than with purely human coding because agents depend heavily on written context. If the docs are wrong, you are feeding future agents bad instructions. If the docs are fresh, every new agent starts closer to the truth. Think of documentation not as a bureaucratic artifact, but as part of the control system for agentic development. Good docs are how your intent survives beyond a single chat.]

---

## Slide 32: Questions?
- **Thank You:** Open floor for Q&A
- **Contact:** xfcui.uw@gmail.com
- **Resources:** cursor.com, docs.cursor.com
[Visual: Minimal closing slide in the same cinematic style; large empty dark space for audience attention, open mic silhouette near center, faint Cursor beam sweeping behind small icons for code, context, agents, and safety; contact and resources sit cleanly at the bottom; no watermark, no extra decoration, calm cyan glow.]
[Speech: Thank you. The message I want to leave you with is balanced. Cursor and agentic tools are not just faster autocomplete; they point toward a new interface for software work, where intent, context, and review become the main levers. The Clawdbot/OpenClaw story shows both sides of that future. On one side, a single experienced developer and a swarm of agents can create astonishing momentum. Agents can negotiate, refactor, automate, and connect systems in ways that feel genuinely new. On the other side, autonomy introduces real risk: prompt injection, credential boundaries, insecure tunnels, and responsibility for actions taken on your behalf. So the goal is not blind hype and not defensive rejection. The goal is mastery. Learn the tools, understand their architecture, constrain them with rules, give them precise context, and review their work like an engineer. With that, I am happy to take questions.]

---

## Appendix: Global Visual Requirements
- **Theme:** Cinematic Cursor dark mode: deep navy/black gradient background, cyan beam accents, violet/magenta network highlights, and high-contrast white text.
- **Reference Style:** Match the generated title slide: code/noise on the left, intent beam through a large cursor, translucent IDE panels, and glowing AI cognition imagery on the right.
- **Typography:** Large white title hierarchy with bold geometric sans for titles (48-60pt), clean sans body text (24-32pt), and monospace only for code labels.
- **Layout:** 16:9 aspect with generous negative space; keep title and key text in the upper-left safe area; reserve 35-45% of the slide for the main visual.
- **Visual Motifs:** Reuse cursor beam, code wall, AI-brain network, translucent UI panels, roadmap nodes, and glowing connector lines as recurring memory anchors.
- **Animations:** Subtle fade-ins, beam glows, and sequential bullet reveals; avoid spins, busy transitions, or motion that distracts from narration.
- **Icons:** Minimal line icons for code, brain, browser, terminal, rules, and safety; use cyan as the primary accent and violet only for secondary highlights.
- **Diagrams:** Clean dark-mode diagrams with simple boxes, arrows, and Excalidraw-style structure; do not overload diagrams with small text.
- **Image Hygiene:** No watermarks, AI-generation stamps, fake logos, or decorative text outside intentional slide content.
- **Balance:** Max 5 content bullets per slide where possible; prioritize visual explanation over dense text; tables should use dark striped rows only when comparison is essential.
- **Speech Timing:** Each `[Speech:]` block is written for roughly 1-2 minutes of natural delivery, targeting about 1.5 minutes with room for pauses.
