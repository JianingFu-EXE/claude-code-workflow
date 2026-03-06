# Behavior Rules

## Experiment Reproducibility Rule

**Every simulation/training run must be traceable.** Before starting:
- Log: input data config, random seed, key hyperparameters, model version
- After: record log path, checkpoint path, key metrics

**Never overwrite results.** Version with date suffix or commit hash.
Violating this = lost weeks of compute. **No exceptions.**

## Research Vault Structure

The Obsidian Research vault at `<RESEARCH>` follows a note lifecycle:

```
TEMPORARY_NOTES/   <-- User drops raw notes here. No frontmatter, no sorting.
FLEETING NOTES/    <-- Project workspaces. Sorted, structured notes.
PERMANENT_NOTES/   <-- Mature, reusable knowledge.
PAPER_NOTES/       <-- Literature notes on specific papers.
DAILY_NOTES/       <-- Date-stamped daily logs.
ASSETS/            <-- Images, diagrams, attachments.
```

## TEMPORARY_NOTES Inbox Rule

**The user writes raw notes in `<RESEARCH>/TEMPORARY_NOTES/`.** These are quick captures — no frontmatter, no structure, just ideas.

**Claude's job at end-of-day (or when asked):**
1. Read every file in `TEMPORARY_NOTES/`
2. For each note:
   a. **Add frontmatter**: title, date, tags (inferred from content), project (if identifiable)
   b. **Add Claude's comments** at the bottom under a `## Claude's Notes` section — context, related links, important information, connections to ongoing work
   c. **Move to the proper location**:
      - Project-related -> `FLEETING NOTES/{Project}/`
      - Literature/paper note -> `PAPER_NOTES/`
      - General idea/knowledge -> `PERMANENT_NOTES/` (if mature) or leave in `FLEETING NOTES/`
      - Daily log content -> `DAILY_NOTES/`
3. `TEMPORARY_NOTES/` should be empty after processing

**Do NOT modify the user's original text.** Only prepend frontmatter and append Claude's section at the bottom.

## Per-Project Workspace Rule

Each project lives in `<FN>/{Project}/` (see CLAUDE.md for full paths). A project workspace contains:
- **Code**: in `<CODE>/` repos
- **XMind**: structural blueprints (.xmind files) — Claude reads these as writing instructions
- **Overleaf**: paper LaTeX (git-synced subfolder)
- **Reference notebook**: sources uploaded to the project's NotebookLM — Claude queries these for truth
- **Daily reports**: Obsidian .md notes — Claude writes these here for the user to track progress

**Daily reports go in the project workspace, NOT in `~/.claude/memory/today.md`.** The `today.md` is Claude's internal session scratchpad. The user tracks progress via daily reports in each project's folder.

## Documentation Structure

- Project-level: Obsidian notes in `<FN>/{Project}/` workspace
- Thesis-level: `AGENTS.md` or similar guide in thesis vault
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
- Follow consistency rules: layout, markers, labels, notes on every section-level topic
- The XMind becomes the SSOT for that document's structure going forward

### Writing output grounded in XMind:
- Each XMind topic at section level -> one section or subsection in output
- Topic notes -> content seed (expand, don't contradict)
- Leaf topics -> paragraph-level guidance
- Empty topics (no notes) -> Claude drafts content but flags for user review

## Daily Report Rule

**After non-trivial work on a project, write a daily report in the project workspace.**

- **Where**: `<FN>/{Project}/` as an Obsidian .md file, named `YYYY-MM-DD Daily Report.md`
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

## Paper Writing Truth Rule (Source-Grounded)

**All paper/thesis writing MUST be grounded in verifiable sources.**

When writing any paper section or thesis chapter:
1. **Query the project's reference notebook** (e.g. NotebookLM) for source-grounded content before writing claims
2. **Every technical claim** must trace to either:
   - Verified source (cite the paper from the reference notebook's response)
   - Own experiment results (with specific run reference)
   - Mathematical derivation (shown explicitly)
3. **If a claim cannot be verified**: flag it as `[UNVERIFIED: need source]` — do NOT silently include it
4. **Citation keys** must match reference manager entries — cross-check after verification

## Task Routing & Auto Model Selection

**Automatically select the cheapest model that can handle the task. Save Opus tokens for what actually needs them.**

Before executing a task, classify it and dispatch accordingly. Use the Agent tool with the appropriate model tier for subagent work.

### Opus (main session) — complex reasoning, stay in main context
Use for:
- Core algorithm design or modification
- Architecture decisions with cascading impact
- Thesis argument structure and contribution framing
- Literature synthesis and gap identification
- Simulation model changes
- Multi-step debugging requiring deep project context
- Paper writing that requires reference notebook + XMind reading
- Any task that needs cross-project knowledge or memory

### Sonnet (subagent) — capable daily work, delegate via Agent tool
Dispatch subagent with `sonnet` for:
- Paper section drafting (when XMind + instructions are clear)
- Code review and refactoring (non-critical)
- Experiment log analysis and report generation
- Obsidian note writing (daily reports, experiment logs)
- XMind mind map creation (following established rules)
- Literature search result summarisation
- Experiment configuration review
- TEMPORARY_NOTES processing (frontmatter + sorting)

### Haiku (subagent) — quick tasks, minimal tokens
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
1. **Root Cause** — Read errors, reproduce, trace data flow
2. **Pattern Analysis** — Find working example, compare
3. **Hypothesis Testing** — Change one variable at a time
4. **Fix & Verify** — Test before fix, verify no regression

3 consecutive failures -> stop and reassess

<!--
  Add domain-specific debugging hints here. Examples:

  ### MATLAB/Simulink-Specific
  - Check signal dimensions first (most common Simulink error)
  - Check normalization references are consistent across files

  ### Python ML-Specific
  - Check device (CPU/GPU) consistency in tensors
  - Check data loader sampling (cross-boundary contamination)
  - Check encoder input dimensions after feature changes
-->

## Quality Control + AI Content Safety

**Core triggers**:
- Processing external URLs / citing others -> must annotate source, warn if unverifiable
- Paper claims -> must be source-grounded (paper text, experiment data, or reference notebook)
- >20 conversation turns / >50 tool calls -> suggest fresh session
- Discovered error/hallucination -> immediately isolate context, don't write to memory
- Literature claims -> cross-check with reference notebook when possible

## Real-time Experience Recording (Mandatory)

**Trigger immediately, don't wait for session-end**:

1. **Corrected by user** -> Record immediately in MEMORY.md
2. **3 consecutive failures** -> Pause and record what was tried
3. **Counter-intuitive discovery** -> Record immediately
4. **Experiment insight** -> Record: what config produced what result

**Output**: Record note in appropriate MEMORY.md

## Memory Search Rules

- When encountering an error, check MEMORY.md and patterns.md first
- When starting work on a project, read the project's notes for context
- Code search: locate directory first, then precise search

## Project Context Auto-detection

<!--
  When conversation involves a specific project, load from its workspace.
  Map keywords to project paths. Example:

  - project-1 / keyword-a / keyword-b -> workspace: `<FN>/Project-1/`, code: `<CODE>/project-1/`
  - project-2 / keyword-c / keyword-d -> workspace: `<FN>/Project-2/`
  - thesis / chapter / dissertation -> `<PHD>/OverLeaf/`
-->

When loading a project context, also note:
- The project's XMind files (for structural reference)
- The project's reference notebook URL (for source-grounded queries)
- The project's recent daily reports (for progress context)

## Parallel Processing

Suitable: multiple independent tasks/failures. Not suitable: interconnected simulation configs.

## Atomic Commits

Each commit does one thing. Types: `fix/feat/refactor/docs/test/chore`.
Banned: mixed changes, meaningless messages, >100 lines without splitting.

## Data Write-back Rules

**When discovering key metrics or results, write back to the right place immediately.**

| Fetch scenario | Write-back target | Fields |
|---------------|-------------------|--------|
| Experiment metrics | Project workspace daily report | Epoch, key metrics |
| Simulation results | Project workspace daily report | Performance stats |
| Literature findings | Reference manager + notebook | Citations, key claims |
| Reusable technical lesson | `MEMORY.md` (auto memory) | Pattern + context |
| Cross-project pattern | `patterns.md` | Lesson + example |
| Session progress (internal) | `memory/today.md` | What was done, next steps |

---

*Compact version | Full version: docs/behaviors-extended.md | Reference: docs/behaviors-reference.md*
