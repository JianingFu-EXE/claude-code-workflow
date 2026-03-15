# Claude Code Workflow — Research Edition

A battle-tested workflow template for Claude Code, customised for **PhD researchers and academic writers**. Memory management, context engineering, XMind-driven writing, and automatic model routing — from daily usage across multiple research projects.

> Forked from [runesleo/claude-code-workflow](https://github.com/runesleo/claude-code-workflow) and extended with research-specific patterns.

**Not a tutorial. Not a toy config. A production workflow for researchers who use Claude Code daily.**

## What This Fork Adds

The original template targets software developers and indie hackers. This fork adds patterns specifically for **academic research workflows**:

| Pattern | What it does |
|---------|-------------|
| **XMind-as-Instruction** | Mind maps become structural blueprints — Claude reads .xmind files as instructions to produce LaTeX, Obsidian notes, or reports |
| **TEMPORARY_NOTES Inbox** | Drop raw notes into an inbox folder. Claude adds frontmatter, comments, and sorts them at end-of-day |
| **Overleaf Staging (temporary.tex)** | New LaTeX content goes to a staging file with highlighted additions/deletions. You audit before merging to main.tex |
| **Source-Grounded Writing** | All paper claims must trace to NotebookLM-verified sources, own experiment data, or explicit derivations. Unverified claims are flagged |
| **Per-Project Workspaces** | Each project is self-contained: code, XMind, Overleaf, reference notebook, daily reports — all in one folder |
| **Daily Reports in Workspace** | Claude writes progress reports to each project's Obsidian folder (not internal memory), so you track progress in your vault |
| **Academic Content Safety** | Never fabricate data/citations, verify claims against reference notebooks, flag uncertainty |
| **Research-Specific Agents** | paper-reviewer, experiment-tracker, literature-scout (alongside the original pr-reviewer, security-reviewer) |
| **Auto Model Selection** | Opus for reasoning, Sonnet subagents for daily work, Haiku for mechanical tasks — saves tokens automatically |
| **Test-Driven Development** | RED-GREEN-REFACTOR enforced for all features and bugfixes — no production code without a failing test |
| **Subagent-Driven Development** | Fresh subagent per task + two-stage review (spec compliance then code quality) for high-quality autonomous execution |
| **Implementation Plans** | Bite-sized task plans with exact file paths, complete code, TDD structure, and verification steps |
| **Parallel Agent Dispatch** | Independent problems solved concurrently — N problems in time of 1 |

## Architecture: Three Layers

```
┌─────────────────────────────────────────────────────────┐
│  Layer 0: Auto-loaded Rules (always in context)         │
│  ┌─────────────┐ ┌────────────┐ ┌───────────────┐     │
│  │ behaviors.md │ │skill-      │ │memory-flush.md│     │
│  │              │ │triggers.md │ │               │     │
│  └─────────────┘ └────────────┘ └───────────────┘     │
├─────────────────────────────────────────────────────────┤
│  Layer 1: On-demand Docs (loaded when needed)           │
│  agents.md · content-safety.md · task-routing.md        │
│  behaviors-extended.md · behaviors-reference.md ...     │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Hot Data (your working memory)                │
│  today.md · projects.md · goals.md · active-tasks.json  │
└─────────────────────────────────────────────────────────┘
```

**Why three layers?** Context window is expensive. Loading everything wastes tokens and degrades quality. This system loads rules always (~2K tokens), docs only when relevant (~1-3K each), and keeps your daily state hot for instant recall.

## What's Inside

```
claude-code-workflow/
├── CLAUDE.md                     # Entry point — identity, projects, preferences
├── README.md                     # You are here
├── patterns.md                   # Cross-project lessons learned
│
├── rules/                        # Layer 0: Always loaded
│   ├── behaviors.md              # Core rules (XMind, inbox, staging, debugging, routing)
│   ├── skill-triggers.md         # When to auto-invoke which skill
│   └── memory-flush.md           # Auto-save triggers + inbox processing
│
├── docs/                         # Layer 1: On-demand reference
│   ├── agents.md                 # Research agent roles & dispatch
│   ├── behaviors-extended.md     # Paper writing protocol, literature review, mind maps
│   ├── behaviors-reference.md    # LaTeX, Obsidian, experiment platform guides
│   ├── content-safety.md         # Academic integrity & hallucination prevention
│   ├── scaffolding-checkpoint.md # "Do you really need to self-host?" checklist
│   └── task-routing.md           # Model tier routing + cost comparison
│
├── memory/                       # Layer 2: Your working state (templates)
│   ├── today.md                  # Daily session log
│   ├── projects.md               # Cross-project status (with thesis chapter mapping)
│   ├── goals.md                  # Week/month/quarter goals
│   └── active-tasks.json         # Cross-session task registry
│
├── skills/                       # Reusable skill definitions
│   ├── session-end/              # End-of-session: inbox processing + save + commit
│   ├── verification-before-completion/  # "Run it. Read output. THEN claim done."
│   ├── systematic-debugging/     # 4-phase debugging protocol
│   ├── planning-with-files/      # File-based planning for complex tasks
│   ├── experience-evolution/     # Auto-accumulate project knowledge
│   ├── test-driven-development/  # RED-GREEN-REFACTOR cycle
│   ├── writing-plans/            # Bite-sized implementation plans with TDD structure
│   ├── subagent-driven-development/  # Fresh subagent per task + two-stage review
│   └── dispatching-parallel-agents/  # Parallel agent dispatch for independent tasks
│
├── agents/                       # Custom agent definitions
│   ├── paper-reviewer.md         # Academic paper/thesis review
│   ├── experiment-tracker.md     # Training log analysis & reporting
│   ├── literature-scout.md       # Literature search & relevance assessment
│   ├── pr-reviewer.md            # Code review (from original template)
│   ├── security-reviewer.md      # Security scanning (from original template)
│   └── performance-analyzer.md   # Performance analysis (from original template)
│
└── commands/                     # Custom slash commands
    ├── debug.md                  # /debug — Start systematic debugging
    ├── deploy.md                 # /deploy — Pre-deployment checklist
    ├── exploration.md            # /exploration — Challenge a research direction
    └── review.md                 # /review — Academic paper review
```

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
- **Key Paths**: Define `<PHD>`, `<RESEARCH>`, `<FN>`, `<TEMP>`, `<CODE>` shorthands
- **Per-Project Workspace Map**: List each project with its paths, XMind files, NotebookLM URLs
- **Sub-project Memory Routes**: Map keywords to the right MEMORY.md
- **Thesis Chapter Mapping**: Which chapter maps to which project

### 3. Set up your Obsidian vault

Create the folder structure in your Research vault:

```
TEMPORARY_NOTES/
FLEETING NOTES/
  Project-1/
  Project-2/
  Thesis/
PERMANENT_NOTES/
PAPER_NOTES/
DAILY_NOTES/
ASSETS/
```

### 4. Start a session

```bash
claude
```

Claude will automatically load your rules and start following the workflow. Try:

- Ask it to write a paper section — it will look for an XMind map first
- Drop a raw note in `TEMPORARY_NOTES/` and say "sort my notes"
- Ask it to draft LaTeX — it will write to `temporary.tex` for your review
- Say "that's all for today" and watch it process your inbox, write reports, and save state

## Key Concepts (Research-Specific)

### XMind-as-Instruction

The core writing workflow: **you build structure in XMind, Claude reads it as instructions to write LaTeX/markdown.**

```
You (XMind)          Claude reads           Claude writes
┌──────────┐        ┌──────────┐          ┌──────────┐
│ Topic     │───────>│ Section  │─────────>│ \section │
│  ├ Note   │        │  Content │          │  LaTeX   │
│  ├ Label  │        │  Role    │          │  output  │
│  └ Marker │        │  Priority│          │          │
└──────────┘        └──────────┘          └──────────┘
```

No XMind? Claude asks: "Should I create the structure first?" Recommended: always XMind first.

### Overleaf Staging (temporary.tex)

Claude never writes directly to `main.tex`. Instead:

1. Generates `temporary.tex` (compiles independently — same preamble as main.tex)
2. New content highlighted in **blue** (`\added{}`), deletions in **red** (`\deleted{}`)
3. You review in Overleaf, request changes, iterate
4. Say "merge to main" when satisfied — highlights stripped, content merged

### TEMPORARY_NOTES Inbox

During the day, drop raw notes (no frontmatter, no structure) into `TEMPORARY_NOTES/`. At end of day, Claude:

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
| Multi-step debugging | TEMPORARY_NOTES sorting | Simple find-and-replace |

Override anytime: "use Opus for this" / "Haiku: fix the typos" / "Sonnet: rewrite the abstract"

## Customisation

### Adding a new project

1. Add workspace entry to CLAUDE.md's project map
2. Create folder in `<FN>/Your-Project/`
3. Add memory route in CLAUDE.md's sub-project memory routes
4. Update `memory/projects.md`

### Adding domain-specific debugging hints

Edit `rules/behaviors.md` → "Debugging Protocol" section. Add your domain's common failure modes (commented examples provided).

### Adding research skills

If you use tools like NotebookLM, Zotero, or XMind, add skill files under `skills/` and trigger rules under `rules/skill-triggers.md`. The template includes commented examples.

### Adjusting model routing

Edit `rules/behaviors.md` → "Task Routing" section, and `docs/task-routing.md` for detailed tier definitions.

## Philosophy

This template encodes principles from daily AI-assisted research:

1. **Structure > Prompting**: XMind mind maps + well-organised config beat clever one-off prompts
2. **Memory > Intelligence**: An AI that remembers past experiment failures is more valuable than a smarter AI starting fresh
3. **Verification > Confidence**: Source-ground every claim. Flag what you can't verify
4. **Layered Loading > Flat Config**: Load rules always, docs on demand, data when needed
5. **Auto-save > Manual Save**: Session-end triggers automatically — close the window anytime
6. **Staging > Direct Edit**: Audit LaTeX changes before they hit main.tex
7. **Test-First > Test-After**: Watch the test fail before writing code — proves the test works
8. **Subagent Isolation > Context Pollution**: Fresh agent per task, never inherit session history

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI (Claude Max or API subscription)
- Obsidian (for research vault and daily reports)
- Optional: XMind (for mind map structural blueprints)
- Optional: Overleaf (for LaTeX paper/thesis drafting)
- Optional: NotebookLM (for source-grounded writing)
- Optional: Zotero (for reference management)

## Prior Art & Credits

- Original template by [@runes_leo](https://x.com/runes_leo): [runesleo/claude-code-workflow](https://github.com/runesleo/claude-code-workflow)
- Three-layer context architecture from the original template
- Research-specific patterns developed through daily PhD workflow usage

## License

MIT — Use it, fork it, make it yours.
