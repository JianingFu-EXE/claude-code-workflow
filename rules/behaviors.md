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

**The user writes raw notes in `<RESEARCH>/Inbox/`.** These are quick captures -- no frontmatter, no structure, just ideas.

**Claude's job at end-of-day (or when asked):**
1. Read every file in `Inbox/`
2. For each note:
   a. **Add frontmatter**: title, date, tags (inferred from content), project (if identifiable)
   b. **Add Claude's comments** at the bottom under a `## Claude's Notes` section -- context, related links, important information, connections to ongoing work
   c. **Move to the proper location**:
      - Project-related -> `Projects/{Project}/`
      - Literature/paper note -> `PAPER_NOTES/`
      - General idea/knowledge -> `Notes/` (if mature) or leave in `Projects/`
      - Daily log content -> project workspace daily report
3. `Inbox/` should be empty after processing

**Do NOT modify the user's original text.** Only prepend frontmatter and append Claude's section at the bottom.

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

**XMind mind maps are the user's primary planning tool and Claude's primary instruction source for writing.**

The workflow is always: **User builds structure in XMind -> Claude reads XMind -> Claude writes output.**

### When the user asks Claude to write (paper section, thesis chapter, Obsidian note, report):
1. **Check for an existing XMind map** covering that topic (in `MindMap/` or project folder)
2. **If XMind exists**: Read it first. Treat it as the structural specification:
   - Topic hierarchy = section/subsection hierarchy
   - Topic notes = content guidance for each section
   - Labels = role (Framing/Background/Methodology/Closing) and project assignment
   - Markers = priority/ordering and completion status
   - Relationships = cross-references to honour in the writing
   - Boundaries = logical groupings to preserve
3. **If no XMind exists**: Ask the user whether to create one first or proceed freeform
4. **Never contradict the XMind structure** without flagging the deviation and getting confirmation

### When the user asks Claude to create an XMind:
- Follow the XMind Consistency Rules in PHD vault `AGENTS.md`
- The XMind becomes the SSOT for that document's structure going forward

### Writing output grounded in XMind:
- Each XMind topic at section level -> one section or subsection in output
- Topic notes -> content seed (expand, don't contradict)
- Leaf topics -> paragraph-level guidance
- Empty topics (no notes) -> Claude drafts content but flags for user review

## Daily Report Rule

**After non-trivial work on a project, write a daily report in the project workspace.**

- **Where**: `<PROJ>/{Project}/` as an Obsidian .md file
  - Meta-RL: `<PROJ>/Meta-RL-FTC/Meta-IPC/YYYY-MM-DD Daily Report.md`
  - DSAC: `<PROJ>/DSAC-WWC/YYYY-MM-DD Daily Report.md`
  - Thesis: `<PROJ>/Thesis/YYYY-MM-DD Daily Report.md`
- **When**: After each significant task, experiment analysis, or writing session
- **Format**: Obsidian markdown with frontmatter (date, tags, project)
- **Content**: What was done, key decisions, results/metrics, next steps
- **Append if exists**: If a daily report for today already exists, append a new section

This is how the user tracks progress. Claude also updates `memory/today.md` internally for its own session continuity, but the user-facing record is the daily report in the project workspace.

## Overleaf Staging Rule (temporary.tex Audit)

**Never write new content directly to `main.tex`.** All additions and deletions go through a staging file for user audit.

### Workflow:

1. **Generate `temporary.tex`** in the same Overleaf directory as `main.tex`
   - Copy the full preamble from `main.tex` (everything before `\begin{document}`) so it compiles independently
   - Add `\usepackage{xcolor}` if not already present, and define:
     ```latex
     \newcommand{\added}[1]{\textcolor{blue}{#1}}
     \newcommand{\deleted}[1]{\textcolor{red}{\sout{#1}}}
     ```
   - Add `\usepackage[normalem]{ulem}` for `\sout` if not present
   - Include only the relevant section(s) between `\begin{document}` and `\end{document}`

2. **Highlight changes**:
   - New content: wrapped in `\added{...}` (renders blue)
   - Deleted content: wrapped in `\deleted{...}` (renders red strikethrough)
   - Unchanged context lines: included as-is for readability

3. **Iterative audit loop**:
   - Present `temporary.tex` to the user
   - User reviews and requests changes ("move this paragraph", "rephrase the claim", etc.)
   - Claude updates `temporary.tex` accordingly (keeping highlights)
   - Repeat until the user says it's OK

4. **Merge on approval**: When the user explicitly says "OK to push" / "merge it" / "looks good, push":
   - Remove `\added{}`/`\deleted{}` wrappers (keep the blue text, remove the red text)
   - Merge the clean content into `main.tex` at the correct location
   - Delete `temporary.tex`
   - Confirm merge to user; git push only with separate confirmation

**Do NOT skip the staging step.** Even single-sentence additions go through `temporary.tex`.

## Paper Writing Truth Rule (NotebookLM-Grounded)

**All paper/thesis writing MUST be grounded in the project's NotebookLM notebook.**

When writing any paper section or thesis chapter:
1. **Query the project's NotebookLM** for source-grounded content before writing claims
2. **Every technical claim** must trace to either:
   - NotebookLM-verified source (cite the paper from NotebookLM's response)
   - Own simulation results (with specific run reference)
   - Mathematical derivation (shown explicitly)
3. **If NotebookLM cannot verify a claim**: flag it as `\first{[UNVERIFIED: need source]}` -- do NOT silently include it
4. **Citation keys** must match Zotero entries -- cross-check after NotebookLM provides the reference

NotebookLM URLs per project (see CLAUDE.md for full list):
- P2 DSAC: `9cfddb8e-...`
- P3 Meta-RL: `a234fe16-...`
- Thesis examples: `27e615ab-...`

## Task Routing & Auto Model Selection

**Automatically select the cheapest model that can handle the task. Save Opus tokens for what actually needs them.**

Before executing a task, classify it and dispatch accordingly. Use the Agent tool with the appropriate model tier for subagent work.

### Opus (main session) -- complex reasoning, stay in main context
Use for:
- Reward function design or modification
- Meta-RL architecture decisions (encoder, latent dim, loss functions)
- Thesis argument structure and contribution framing
- Literature synthesis and gap identification
- Simulink model changes
- Multi-step debugging requiring deep project context
- Paper writing that requires NotebookLM interaction + XMind reading
- Any task that needs cross-project knowledge or memory

### Sonnet (subagent) -- capable daily work, delegate via Agent tool
Dispatch subagent with `sonnet` for:
- Paper section drafting (when XMind + instructions are clear)
- Code review and refactoring (Python/MATLAB, non-critical)
- TensorBoard log analysis and report generation
- Obsidian note writing (daily reports, experiment logs)
- XMind mind map creation (following established rules)
- Literature search result summarisation
- Experiment configuration review
- Inbox processing (frontmatter + sorting)

### Haiku (subagent) -- quick tasks, minimal tokens
Dispatch subagent with `haiku` for:
- Citation formatting and .bib fixes
- Typo/grammar corrections in LaTeX or markdown
- File searching and listing (codebase exploration)
- Simple file moves and renames
- Frontmatter generation for notes
- Extracting specific values from logs or configs
- Generating commit messages

### Dispatch Rules
- **User override wins.** If the user specifies a model in the prompt (e.g. "use Haiku for this", "do this in Sonnet", "stay in Opus"), follow it exactly. No second-guessing.
- **Default to the cheapest tier** that can do the job when the user doesn't specify. When in doubt, try Sonnet first.
- **Escalate up** if a subagent task fails or needs context the subagent doesn't have.
- **Stay in Opus** when the task needs: memory files, cross-project context, multi-turn reasoning, or user interaction.
- **Parallel dispatch**: When multiple independent subtasks exist, dispatch multiple subagents simultaneously.
- **Inject context**: When dispatching, always inject the relevant project paths and any specific instructions the subagent needs. Don't assume subagents know the project structure.

> Detailed routing table -> `Read docs/task-routing.md`

## Debugging Protocol

No blind fixes. Four phases:
1. **Root Cause** -- Read errors, reproduce, trace data flow
2. **Pattern Analysis** -- Find working example, compare
3. **Hypothesis Testing** -- Change one variable at a time
4. **Fix & Verify** -- Test before fix, verify no regression

3 consecutive failures -> stop and reassess

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

**When discovering key metrics or results, write back to the right place immediately.**

| Fetch scenario | Write-back target | Fields |
|---------------|-------------------|--------|
| TensorBoard metrics | Project workspace daily report | Epoch, reward, KL, alpha |
| Simulation results | Project workspace daily report | Load reduction %, pitch stats |
| Literature findings | Zotero + NotebookLM | Citations, key claims |
| Reusable technical lesson | `MEMORY.md` (auto memory) | Pattern + context |
| Cross-project pattern | `patterns.md` | Lesson + example |
| Session progress (internal) | `memory/today.md` | What was done, next steps |

---

*Compact version | Full version: docs/behaviors-extended.md | Reference: docs/behaviors-reference.md*
