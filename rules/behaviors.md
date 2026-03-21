# Behavior Rules

## Experiment Reproducibility Rule

**Every simulation/training run must be traceable.** Before starting:
- Log: wind file, fault config, random seed, reward weights, key hyperparameters
- After: record TensorBoard path, checkpoint path, key metrics

**Never overwrite results.** Version with date suffix or commit hash.
Violating this = lost weeks of compute. **No exceptions.**

**Never delete files unless explicitly asked.** Even tiny files (e.g. 88-byte TB events) may belong to an active process. Do not assume files are stale, spurious, or safe to remove. If a file looks suspicious, ask the user — do not delete it.

## Research Vault Structure

The Obsidian Research vault at `<RESEARCH>` follows a note lifecycle:

```
Inbox/             <-- User drops raw notes here. No frontmatter, no sorting.
Projects/          <-- Project workspaces (Meta-RL-FTC, DSAC-WWC, RL-GFM, Thesis, OE-Paper).
Notes/             <-- Mature, reusable knowledge (200+ concept notes).
PAPER_NOTES/       <-- Literature notes on specific papers.
ASSETS/            <-- Images, diagrams, attachments.
DUE/               <-- Deadlines and submissions.
```

## Inbox Rule
User drops raw notes in `<RESEARCH>/Inbox/`. Claude sorts at end-of-day: add frontmatter, append `## Claude's Notes`, move to proper folder. Do NOT modify user's original text.
> Full procedure → Read docs/behaviors-extended.md § Inbox Processing Protocol

## Per-Project Workspace Rule

Each project lives in `<PROJ>/{Project}/` (see CLAUDE.md for full paths). A project workspace contains:
- **Code**: in `<CODE>/` repos (MATLAB + Python)
- **XMind**: structural blueprints (.xmind files) -- Claude reads these as writing instructions
- **Overleaf**: paper LaTeX (git-synced subfolder)
- **NotebookLM**: references uploaded to the project's notebook -- Claude queries these for truth
- **Daily reports**: Obsidian .md notes -- Claude writes these here for the user to track progress

**Daily reports go in the project workspace, NOT in `~/.claude/memory/today.md`.** The `today.md` is Claude's internal session scratchpad. The user tracks progress via daily reports in each project's folder.

## Documentation Structure

- Project-level: Obsidian notes in `<PROJ>/{Project}/` workspace
- Thesis-level: `AGENTS.md` in PHD vault (workspace guide)
- Status SSOT: cross-project -> `memory/projects.md`

## XMind-as-Instruction Rule (CORE WORKFLOW)
**XMind = structural blueprint. Workflow: User builds XMind → Claude reads XMind → Claude writes output.**
- Writing task? Check for XMind first. No XMind? Ask user whether to create one.
- Never contradict the XMind structure without flagging and confirming.
> Full procedure → Read docs/behaviors-extended.md § Paper Writing Protocol

## Daily Report Rule
After non-trivial work, write daily report in `<PROJ>/{Project}/` as Obsidian .md. Append if exists.
> Full format → Read docs/behaviors-extended.md § Daily Report Format

## Overleaf Staging Rule
**Never write directly to `main.tex`.** All changes go through `temporary.tex` with `\added{}`/`\deleted{}` highlighting. Merge only on explicit user approval.
> Full procedure → Read docs/behaviors-extended.md § Overleaf Staging Rule

## Paper Writing Truth Rule
All paper/thesis claims MUST be NotebookLM-grounded or own-simulation-grounded. Unverified claims flagged as `[UNVERIFIED]`.
> Full procedure → Read docs/behaviors-extended.md § Paper Writing Truth Rule

## Task Routing
Auto-select cheapest model: Opus (reasoning/memory/cross-project), Sonnet (structured work), Haiku (mechanical). User override wins.
> Full routing table → Read docs/task-routing.md

## Iron Laws (non-negotiable, no rationalizations)

1. **NO PAPER CLAIM WITHOUT SOURCE EVIDENCE** — NotebookLM, Zotero, or own simulation data
2. **NO EXPERIMENT WITHOUT LOGGED HYPOTHESIS** — auto-intercept: "What is the hypothesis? What are the controls?"
3. **NO COMPLETION CLAIM WITHOUT VERIFICATION OUTPUT** — run the command, read the output, THEN claim done
4. **NO FIX WITHOUT ROOT CAUSE** — four phases, no shortcuts

## Debugging Protocol

No blind fixes. Four phases:
1. **Root Cause** — Read errors, reproduce, trace data flow
2. **Pattern Analysis** — Find working example, compare
3. **Hypothesis Testing** — Change one variable at a time
4. **Fix & Verify** — Test before fix, verify no regression

3 consecutive failures → stop and reassess. 7 investigation techniques available:
- Binary Search | Differential Debugging | Minimal Reproduction | Trace Execution | Pattern Search | Working Backwards | Rubber Duck
> Full technique details → Read docs/behaviors-reference.md § Investigation Techniques

### MATLAB/Simulink-Specific
- Check signal dimensions first (most common Simulink error)
- Check normalization references are consistent across reward.m and normalize_inputs.m
- Check fault mode indexing (blade 1 has 7 modes, blades 2/3 have 4)

### Python RL-Specific
- Check device (CPU/GPU) consistency in tensors
- Check replay buffer sampling (cross-boundary contamination)
- Check context encoder input dimensions after obs_index changes
- Verify z is actually being updated during rollouts (not frozen at zero)

## Quality Control + AI Content Safety

**Core triggers**:
- Processing external URLs / citing others -> must annotate source, warn if unverifiable
- Paper claims -> must be source-grounded (paper text, simulation data, or NotebookLM)
- >20 conversation turns / >50 tool calls -> suggest fresh session
- Discovered error/hallucination -> immediately isolate context, don't write to memory
- Literature claims -> cross-check with NotebookLM when possible

## Real-time Experience Recording (Mandatory)

**Trigger immediately, don't wait for session-end**:

1. **Corrected by user** -> Record immediately in MEMORY.md
2. **3 consecutive failures** -> Pause and record what was tried
3. **Counter-intuitive discovery** -> Record immediately
4. **Experiment insight** -> Record: what config produced what result

**Output**: Record note in appropriate MEMORY.md

## Memory Search Rules

- When encountering an error, check MEMORY.md and patterns.md first
- When starting work on a project, read the project's Obsidian notes for context
- Code search: locate directory first, then precise search

## Project Context Auto-detection

When conversation involves a specific project, load from its workspace:
- Meta-RL / PEARL / FTC / IPC -> workspace: `<PROJ>/Meta-RL-FTC/`, code: `<CODE>/Meta/`
- DSAC / distributional / WWC / TSTE -> workspace: `<PROJ>/DSAC-WWC/`
- PINN / HJB / TMD / Ocean Engineering -> workspace: `<PROJ>/OE-Paper/`, paper: `<PHD>/Papers/OE_PINN_RV3/`
- RL-GFM / grid-forming / GFM-RL / converter -> workspace: `<PROJ>/RL-GFM/`, code: `<CODE>/GFM-RL/`
- thesis / chapter / dissertation -> `<PHD>/OverLeaf/` + `<PHD>/AGENTS.md`

When loading a project context, also:
- Read the project's XMind files (for structural reference)
- Note the project's NotebookLM URL (for source-grounded queries)
- Check the project's recent daily reports (for progress context)
- **If a Critical Path exists**: read it and flag open blockers to the user before starting work
  - Meta-RL: `<PROJ>/Meta-RL-FTC/Meta-IPC/Critical Path.md` (has open issues 1-6)
  - Other projects: check for `Critical Path.md` or `TODO.md` in workspace root

## Parallel Processing

Suitable: multiple independent tasks/failures. Not suitable: interconnected simulation configs.

## Atomic Commits

Each commit does one thing. Types: `fix/feat/refactor/docs/test/chore`.
Banned: mixed changes, meaningless messages, >100 lines without splitting.

## Data Write-back Rules
Write metrics/results to the right place immediately: TB metrics → daily report, lessons → MEMORY.md, patterns → patterns.md.
> Full table → Read docs/behaviors-extended.md § Data Write-back Rules

---

*Compact version | Full version: docs/behaviors-extended.md | Reference: docs/behaviors-reference.md*
