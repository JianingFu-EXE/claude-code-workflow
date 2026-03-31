# Claude Code Workflow -- Research Edition

A battle-tested workflow config for Claude Code, built for **PhD researchers and academic writers**. Context engineering, XMind-driven writing, source-grounded claims, and research-domain skills -- from daily usage across multiple research projects.

> Evolved from [runesleo/claude-code-workflow](https://github.com/runesleo/claude-code-workflow). The original targets software developers; this fork is purpose-built for academic research.

**Not a tutorial. Not a toy config. A production workflow for researchers who use Claude Code daily.**

## What This Does

| Pattern | What it does |
|---------|-------------|
| **XMind-as-Instruction** | Mind maps become structural blueprints -- Claude reads .xmind files as instructions to produce LaTeX, Obsidian notes, or reports |
| **Inbox Processing** | Drop raw notes into an inbox folder. Claude adds frontmatter, comments, and sorts them at end-of-day |
| **Overleaf Staging (temporary.tex)** | New LaTeX content goes to a staging file with highlighted additions/deletions. You audit before merging to main.tex |
| **Source-Grounded Writing** | All paper claims must trace to NotebookLM-verified sources, own experiment data, or explicit derivations. Unverified claims are flagged |
| **Per-Project Workspaces** | Each project is self-contained: code, XMind, Overleaf, reference notebook, daily reports -- all in one folder |
| **Daily Reports** | Claude writes progress reports to a centralized daily report folder in your Obsidian vault |
| **Academic Content Safety** | Never fabricate data/citations, verify claims against reference notebooks, flag uncertainty |
| **Research Skills** | Domain-specific skills: XMind generation, NotebookLM queries, Elsevier/Zotero import, paper manuscript drafting, literature atlas mapping |
| **Auto Model Selection** | Opus for reasoning, Sonnet for structured work, Haiku for mechanical tasks -- saves tokens automatically |

## Architecture: Two Layers

```
+-----------------------------------------------------------+
|  Layer 0: Auto-loaded Rules (always in context)            |
|  +--------------+ +---------------+ +----------------+    |
|  | behaviors.md | | skill-        | | memory-flush.md|    |
|  |              | | triggers.md   | |                |    |
|  +--------------+ +---------------+ +----------------+    |
|  | thesis-xmind-format.md                             |    |
|  +----------------------------------------------------+    |
+-----------------------------------------------------------+
|  Layer 1: On-demand Docs + References (loaded when needed) |
|  agents.md . content-safety.md . task-routing.md           |
|  behaviors-extended.md . behaviors-reference.md            |
|  superpowers/specs/ . references/codex-tools.md            |
+-----------------------------------------------------------+
```

**Why two layers?** Context window is expensive. Loading everything wastes tokens and degrades quality. Layer 0 rules are always present (~3K tokens). Layer 1 docs load only when relevant (~1-3K each). Memory is handled by Claude Code's built-in auto-memory system, not flat files.

## What's Inside

```
claude-code-workflow/
+-- CLAUDE.md                     # Entry point -- identity, projects, preferences
+-- AGENTS.md                     # Agent collaboration guide (for Codex and multi-agent)
+-- SETUP.md                      # Setup instructions
+-- README.md                     # You are here
+-- patterns.md                   # Cross-project lessons learned
|
+-- rules/                        # Layer 0: Always loaded
|   +-- behaviors.md              # Core rules (XMind, inbox, staging, debugging, routing)
|   +-- skill-triggers.md         # When to auto-invoke which skill
|   +-- memory-flush.md           # Auto-save triggers + inbox processing
|   +-- thesis-xmind-format.md    # XMind format spec for thesis structure files
|
+-- docs/                         # Layer 1: On-demand reference
|   +-- agents.md                 # Research agent roles & dispatch
|   +-- behaviors-extended.md     # Paper writing protocol, literature review, mind maps
|   +-- behaviors-reference.md    # LaTeX, Obsidian, experiment platform guides
|   +-- content-safety.md         # Academic integrity & hallucination prevention
|   +-- task-routing.md           # Model tier routing + cost comparison
|   +-- superpowers/specs/        # Design specs for the Superpowers skill system
|
+-- references/                   # Standalone reference docs
|   +-- codex-tools.md            # Codex tool compatibility reference
|
+-- skills/                       # Research-domain skill definitions
|   +-- xmind/                    # XMind mind map generation and manipulation
|   +-- notebooklm/               # NotebookLM browser automation for source queries
|   +-- notebook-query/           # Quick NotebookLM question + XMind integration
|   +-- paper-manuscript/         # Paper drafting with XMind + NotebookLM + Zotero
|   +-- paper-atlas/              # Literature mapping: XMind -> NotebookLM -> Zotero
|   +-- elsevier-zotero-import/   # ScienceDirect search + Zotero import pipeline
|   +-- research-ops-subchapter-search/  # Systematic literature search planning
|   +-- obsidian-markdown/        # Obsidian-flavoured markdown (wikilinks, callouts)
|   +-- obsidian-bases/           # Obsidian database views (.base files)
|   +-- json-canvas/              # Obsidian canvas files (.canvas)
|
+-- commands/                     # Custom slash commands
    +-- debug.md                  # /debug -- Start systematic debugging
```

### Where did the dev workflow skills go?

The generic development workflow skills (TDD, subagent-driven development, systematic debugging, verification-before-completion, writing plans, parallel agent dispatch, experience evolution, planning-with-files, session-end) have moved to **Superpowers** -- a separate skill system that layers on top of Claude Code. This repo now focuses exclusively on the **research workflow configuration**.

Similarly, the `agents/` folder (paper-reviewer, experiment-tracker, etc.) and `memory/` folder (today.md, projects.md, etc.) have been removed. Agent definitions are now in `AGENTS.md`, and memory is handled by Claude Code's built-in auto-memory system rather than flat files.

## Quick Start

### 1. Copy to your Claude Code config

```bash
# Clone the template
git clone https://github.com/YOUR_USERNAME/claude-code-workflow.git

# Copy to your Claude Code config directory
cp -r claude-code-workflow/* ~/.claude/

# Or symlink if you want to keep it as a git repo
ln -sf ~/claude-code-workflow/rules ~/.claude/rules
ln -sf ~/claude-code-workflow/docs ~/.claude/docs
# ... etc
```

### 2. Customise CLAUDE.md

Open `~/.claude/CLAUDE.md` and fill in:

- **User Info**: Your name, university, thesis title, tool stack
- **Key Paths**: Define `<PHD>`, `<RESEARCH>`, `<PROJ>`, `<CODE>` shorthands
- **Per-Project Workspace Map**: List each project with its paths, XMind files, NotebookLM URLs

### 3. Set up your Obsidian vault

Create the folder structure in your Research vault:

```
Inbox/              <-- Raw notes go here
Projects/           <-- Per-project workspaces
Notes/              <-- Mature, reusable knowledge
PAPER_NOTES/        <-- Literature notes on specific papers
ASSETS/             <-- Images, diagrams, attachments
DUE/                <-- Deadlines and submissions
```

### 4. Start a session

```bash
claude
```

Claude will automatically load your rules and start following the workflow. Try:

- Ask it to write a paper section -- it will look for an XMind map first
- Drop a raw note in `Inbox/` and say "sort my notes"
- Ask it to draft LaTeX -- it will write to `temporary.tex` for your review
- Say "that's all for today" and watch it process your inbox, write reports, and save state

## Key Concepts

### XMind-as-Instruction

The core writing workflow: **you build structure in XMind, Claude reads it as instructions to write LaTeX/markdown.**

```
You (XMind)          Claude reads           Claude writes
+----------+        +----------+          +----------+
| Topic     |------->| Section  |--------->| \section |
|  +- Note  |        |  Content |          |  LaTeX   |
|  +- Label |        |  Role    |          |  output  |
|  +- Marker|        |  Priority|          |          |
+----------+        +----------+          +----------+
```

No XMind? Claude asks: "Should I create the structure first?" Recommended: always XMind first.

### Overleaf Staging (temporary.tex)

Claude never writes directly to `main.tex`. Instead:

1. Generates `temporary.tex` (compiles independently -- same preamble as main.tex)
2. New content highlighted in **blue** (`\added{}`), deletions in **red** (`\deleted{}`)
3. You review in Overleaf, request changes, iterate
4. Say "merge to main" when satisfied -- highlights stripped, content merged

### Inbox Processing

During the day, drop raw notes (no frontmatter, no structure) into `Inbox/`. At end of day, Claude:

1. Adds frontmatter (title, date, tags, project)
2. Appends `## Claude's Notes` with context and connections
3. Moves to the right folder (project workspace, paper notes, permanent notes)
4. **Never modifies your original text**

### Source-Grounded Writing

Every paper claim must trace to a verifiable source. Claude queries your project's NotebookLM notebook before writing, and flags anything it can't verify as `[UNVERIFIED: need source]`.

### Auto Model Selection

Not every task needs Opus. Claude auto-routes:

| Opus (main) | Sonnet (subagent) | Haiku (subagent) |
|---|---|---|
| Algorithm design | Paper section drafting | Citation formatting |
| Architecture decisions | Code review | Typo fixes |
| Thesis framing | Experiment analysis | File searching |
| XMind + notebook writing | Daily report writing | Frontmatter generation |
| Multi-step debugging | Inbox sorting | Simple find-and-replace |

Override anytime: "use Opus for this" / "Haiku: fix the typos" / "Sonnet: rewrite the abstract"

## Customisation

### Adding a new project

1. Add workspace entry to CLAUDE.md's project map
2. Create folder in `<PROJ>/Your-Project/`
3. Add project context auto-detection keywords in `rules/behaviors.md`

### Adding domain-specific debugging hints

Edit `rules/behaviors.md` -> "Debugging Protocol" section. Add your domain's common failure modes.

### Adding research skills

Add skill files under `skills/` and trigger rules under `rules/skill-triggers.md`. Each skill has a `SKILL.md` that Claude reads when the skill is invoked.

### Adjusting model routing

Edit `rules/behaviors.md` -> "Task Routing" section, and `docs/task-routing.md` for detailed tier definitions.

## Philosophy

This config encodes principles from daily AI-assisted research:

1. **Structure > Prompting**: XMind mind maps + well-organised config beat clever one-off prompts
2. **Verification > Confidence**: Source-ground every claim. Flag what you can't verify
3. **Layered Loading > Flat Config**: Load rules always, docs on demand
4. **Auto-save > Manual Save**: Session-end triggers automatically -- close the window anytime
5. **Staging > Direct Edit**: Audit LaTeX changes before they hit main.tex
6. **Research Skills > Generic Skills**: Domain-specific tools (NotebookLM, Zotero, XMind) over generic dev patterns

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI (Claude Max or API subscription)
- Obsidian (for research vault and daily reports)
- Optional: XMind (for mind map structural blueprints)
- Optional: Overleaf (for LaTeX paper/thesis drafting)
- Optional: NotebookLM (for source-grounded writing)
- Optional: Zotero (for reference management)

## Prior Art & Credits

- Original template by [@runes_leo](https://x.com/runes_leo): [runesleo/claude-code-workflow](https://github.com/runesleo/claude-code-workflow)
- Two-layer context architecture evolved from the original three-layer design
- Research-specific patterns developed through daily PhD workflow usage

## License

MIT -- Use it, fork it, make it yours.
