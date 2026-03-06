# Research Workflow Template — Claude Code Global Memory

> Auto-loaded = rules/ (behaviors.md, skill-triggers.md, memory-flush.md)
> On-demand = docs/ (agents.md, content-safety.md, task-routing.md, ...)
> Hot data layer = memory/today.md + memory/active-tasks.json

---

## User Info

- **Name**: YOUR_NAME | **University**: YOUR_UNIVERSITY
- **Identity**: [Your role, e.g. "PhD student — reinforcement learning for robotics"]
- **Supervisor**: [Supervisor name]
- **Thesis**: "[Your thesis title]"
- **Languages**: [e.g. "MATLAB/Simulink (plant model), Python (training), C++ (firmware)"]
- **Philosophy**: [e.g. "Rigorous experimentation + systematic paper-to-thesis pipeline"]
- **Core pattern**: XMind first, then write. XMind mind maps are the structural blueprint — Claude reads them as instructions to produce LaTeX, Obsidian notes, or any written output.

### Platform & Tool Stack

<!--
  Customize this table with the tools you actually use.
  Remove rows you don't need, add your own.
-->

| Tool | Purpose | Location |
|------|---------|----------|
| Obsidian | Daily progress, research notes, mind maps | [Your vault path] |
| Overleaf | Thesis + paper drafting (git-synced) | See project paths below |
| Zotero | Reference management | [Zotero library ID or path] |
| NotebookLM | Source-grounded literature Q&A | See notebook URLs below |
| XMind | **Structural blueprint for all writing** — Claude reads .xmind as instructions | `MindMap/` in vault |

### Key Paths

<!--
  Define shorthands so rules/behaviors.md can reference paths concisely.
  Replace these with your actual paths.
-->

| Shorthand | Path |
|-----------|------|
| `<PHD>` | `/path/to/your/phd/vault` |
| `<RESEARCH>` | `/path/to/your/research/vault` |
| `<FN>` | `<RESEARCH>/FLEETING NOTES` |
| `<TEMP>` | `<RESEARCH>/TEMPORARY_NOTES` |
| `<CODE>` | `/path/to/your/code/repos` |

### Research Vault Structure

<!--
  This is an Obsidian Zettelkasten-style vault.
  Adjust folder names to match your setup.
-->

```
<RESEARCH>/
  TEMPORARY_NOTES/   <-- User's inbox. Raw notes, no frontmatter. Claude sorts at end-of-day.
  FLEETING NOTES/    <-- Project workspaces (one folder per project)
  PERMANENT_NOTES/   <-- Mature, reusable knowledge
  PAPER_NOTES/       <-- Literature notes on specific papers
  DAILY_NOTES/       <-- Date-stamped daily logs
  ASSETS/            <-- Images, diagrams
```

---

## Projects — Per-Project Workspace Map

Each project is a self-contained workspace. All its artefacts (code, XMind, Overleaf, notes, daily reports) live together under `<FN>/{Project}/`. Claude writes daily reports there and reads XMind from there.

<!--
  Replace these examples with your actual projects.
  Each project should list: status, workspace path, code path, overleaf path,
  XMind files, NotebookLM URL, and daily report location.
-->

### Project 1: [Your First Project] (STATUS)
- **Status**: [e.g. Published / Under review / Active] | **Thesis chapter**: Ch N
- **Workspace**: `<FN>/Project-1-Name/`
- **Code**: `<CODE>/project-1/`
- **Overleaf**: `<FN>/Project-1-Name/overleaf/`
- **XMind**: `<FN>/Project-1-Name/Structure.xmind`
- **NotebookLM**: `https://notebooklm.google.com/notebook/YOUR_NOTEBOOK_ID`
- **Daily reports**: write to `<FN>/Project-1-Name/`

### Project 2: [Your Second Project] (STATUS)
- **Status**: [status] | **Thesis chapter**: Ch N
- **Workspace**: `<FN>/Project-2-Name/`
- ...

### Thesis
- **Workspace**: `<FN>/Thesis/` + `<PHD>/OverLeaf/`
- **Overleaf**: `<PHD>/OverLeaf/Thesis.tex`
- **Structure**: [Your chapter mapping, e.g. Ch1 Intro, Ch2 Lit Review, Ch3-5 Projects, Ch6 Conclusion]
- **Mind maps**: `<PHD>/MindMap/`

---

## Delivery Standards

- **Truth > Speed**: Never claim completion without verification evidence
- **Small Batch**: <=15 files or <=400 lines net change per commit
- **No Secrets**: Never commit API keys/tokens (Zotero, Overleaf credentials, etc.)
- **Reproducibility**: Every experiment must log hyperparameters, random seeds, input data config
- **Self-verify**: Run lint/build/test before declaring done, read output to confirm PASS
- **Banned phrases**: "I fixed it, you try" / "Should be fine" / "Probably passes" / "Theoretically correct"

### LaTeX Standards
- Preserve Overleaf sync compatibility — no destructive renames
- Use consistent citation style (e.g. `authoryear` with biblatex + biber)
- Keep technical claims source-grounded (paper text, references, or NotebookLM)
- Do not invent references, results, or experimental details

### Handoff Checklist (before session-end)

- [ ] Code committed or progress noted
- [ ] today.md updated with progress and key decisions
- [ ] MEMORY.md updated with lessons learned
- [ ] Remaining issues and next steps noted

---

## Work Preferences

- **Language**: English (academic) | **Code**: Follow project conventions | **Commits**: Atomic, one change per commit
- **Verification**: Claude runs it | **Tests**: Must work offline where possible

---

## Collaboration Preferences

- Act as advisor, devil's advocate, mirror — proactively point out blind spots, never be a yes-man
- **Auto-execute**: Bug fixes, <=100 line refactors, Obsidian note creation, XMind generation
- **Auto-intercept**:
  * **New experiment** -> Ask: "What is the hypothesis? What are the controls?"
  * **Paper claim without evidence** -> Flag immediately
- **Require confirmation (stop and check in)**:
  * Reward/loss function changes (affects all training)
  * Simulation model modifications
  * Overleaf structural changes (chapter reordering, section deletion)
  * Training hyperparameter changes
  * Thesis structure decisions
  * Literature claims to be cited
- **Never self-decide**: Delete experiment data, push to Overleaf, modify simulation models
- **Banned**: "Is this OK?" / "Should I pick A or B?" / "Should I continue?"
- **No filler intros**: Go straight to the answer or start working

---

## Experience Recall & Evolution

**Mandatory triggers (check every turn)**:
- Encountering Bug/Error/Stuck -> First step: check memory files for related patterns
- Corrected by user -> Immediately record lesson in MEMORY.md
- Starting new task -> Check patterns.md for related pitfalls
- If executed >8 tools on a complex task -> REFLECT and record learning

---

## SSOT Ownership (Single Source of Truth)

| Info Type | SSOT File | Do NOT write to |
|-----------|-----------|-----------------|
| Daily reports (per-project) | `<FN>/{Project}/` workspace (Obsidian .md) | today.md, MEMORY.md |
| Cross-project overview | `memory/projects.md` | (summary + pointers only) |
| Technical pitfalls | `MEMORY.md` (per-project auto memory) | today.md |
| Session-level progress | `memory/today.md` | (temp layer, archived next day) |
| In-flight task registry | `memory/active-tasks.json` | (cross-session task status) |
| Experiment results | Project workspace daily reports | MEMORY.md |
| Paper/thesis structure | XMind maps in project workspace (authoritative) | Plain text notes |
| Paper LaTeX source | Overleaf repo in project workspace | Duplicate elsewhere |
| Reference notebook | Per-project NotebookLM (see URLs above) | Don't duplicate content |
| Code | `<CODE>/` repos | Obsidian notes |
| Raw notes inbox | `<TEMP>/` — user writes here, Claude sorts at end-of-day | Modify user text |

---

## Memory Write Routing

| Layer | File | What to write |
|-------|------|---------------|
| Auto Memory | Project `MEMORY.md` | Technical pitfalls, API details, tool configs |
| Pattern library | `patterns.md` | Cross-project reusable patterns |
| Hot data layer | `today.md` | Daily progress, handoff |
| Task registry | `active-tasks.json` | Cross-session in-flight tasks |

### Sub-project Memory Routes

<!--
  Map keywords to the right MEMORY.md for each project.
  Replace with your actual project keywords and paths.

  | Keywords | Memory path |
  |----------|-------------|
  | project-1/keyword-a/keyword-b | `~/.claude/projects/-path-to-project-1/memory/MEMORY.md` |
  | project-2/keyword-c/keyword-d | `~/.claude/projects/-path-to-project-2/memory/MEMORY.md` |
-->

Routes determine write targets. Unlisted projects share the main MEMORY.md.

---

## On-demand Loading Index

| Scenario | Load file |
|----------|-----------|
| Project overview | `Read memory/projects.md` |
| Agent/multi-model collaboration | `Read docs/agents.md` |
| AI content safety/quality control | `Read docs/content-safety.md` |
| Task routing details | `Read docs/task-routing.md` |
| Extended behaviors | `Read docs/behaviors-extended.md` |
| Behavior reference details | `Read docs/behaviors-reference.md` |
| Cross-day goals/todos | `Read memory/goals.md` |
| Pattern library | `Read patterns.md` |

---

*Last updated: YYYY-MM-DD*
