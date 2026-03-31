# PhD Research Workflow -- Codex Shared Guide

> Codex counterpart to `CLAUDE.md`.
> Keep core context inline here. Load detailed procedures on demand from the shared config root.
> Shared SSOT: `rules/`, `docs/`, `patterns.md`.

If a shared file mentions Claude Code-only features such as slash commands, skill dispatch, MCP-specific flows, or Claude-specific memory paths, translate the intent into the closest Codex-native workflow. If no equivalent exists, tell the user and continue with the nearest manual path.

---

## User Info

- **Name**: Jianing Fu | **University**: University of Exeter (Renewable Energy - Cornwall)
- **Identity**: PhD student -- intelligent control of wind turbines (RL, meta-RL, PINN-based control)
- **Supervisor**: Dr. Shuyue Lin
- **Thesis**: "Intelligent load mitigation control of offshore wind turbines"
- **Languages**: MATLAB/Simulink (plant model, OpenFAST), Python (RL training, PEARL/SAC)
- **Philosophy**: Rigorous experimentation + systematic paper-to-thesis pipeline
- **Core pattern**: XMind first, then write. XMind mind maps are the structural blueprint -- read them as instructions for LaTeX, Obsidian notes, or other writing outputs.

## Platform & Tool Stack

| Tool | Purpose | Location |
|------|---------|----------|
| Obsidian | Daily progress, research notes, mind maps | OneDrive PHD vault |
| Overleaf | Thesis + paper drafting (git-synced) | See project paths below |
| Zotero | Reference management (cloud, ID 9312542) | See project context and vault config |
| NotebookLM | Source-grounded literature Q&A | See notebook URLs below |
| XMind | Structural blueprint for all writing | `MindMap/` in PHD vault |
| OpenFAST | Aeroelastic wind turbine simulation | Simulink S-Function |
| TurbSim | Turbulent wind field generation | `.bts` files |

## Key Paths

| Shorthand | macOS | Windows |
|-----------|-------|---------|
| `<SHARED>` | `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Projects/.claude-shared` | `C:\Users\jf844\OneDrive - University of Exeter\Projects\.claude-shared` |
| `<PHD>` | `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Obsidian/PHD` | `C:\Users\jf844\OneDrive - University of Exeter\Obsidian\PHD` |
| `<RESEARCH>` | `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Obsidian/Research` | `C:\Users\jf844\OneDrive - University of Exeter\Obsidian\Research` |
| `<PROJ>` | `<RESEARCH>/Projects` | `<RESEARCH>\Projects` |
| `<INBOX>` | `<RESEARCH>/Inbox` | `<RESEARCH>\Inbox` |
| `<CODE>` | `/Users/jn/Github` | `C:\Users\jf844` |
| `<PYTHON>` | _(not used on Mac)_ | `C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe` |
| `<TB>` | _(not used on Mac)_ | `C:\Users\jf844\Meta\TensorBoard` |

Detect the current platform from the environment and use the matching column.

## Projects -- Per-Project Workspace Map

Each project is a self-contained workspace. All artefacts for a project live together under `<PROJ>/{Project}/`.

### Project 1: PINN-HJB Active Structural Control (PUBLISHED)

- **Status**: Published in Ocean Engineering | **Thesis chapter**: Ch 3
- **Workspace**: `<PROJ>/OE-Paper/`
- **Paper LaTeX**: `<PHD>/Papers/OE_PINN_RV3/`
- **XMind**: `<RESEARCH>/Notes/Wind Turbine Active TMD Model Free Controller.xmind`, `<RESEARCH>/Notes/Model-free PINN Optimal with Pareto Front.xmind`
- **NotebookLM source**: `1-s2.0-S0029801825035966-main`

### Project 2: DSAC-WWC -- Distributional RL for FOWT (UNDER REVIEW)

- **Status**: Under review at IEEE Trans. Sustainable Energy | **Thesis chapter**: Ch 4
- **Workspace**: `<PROJ>/DSAC-WWC/`
- **Paper LaTeX**: `<PHD>/Papers/_TSTE_DSAC/`
- **XMind**: `<PROJ>/DSAC-WWC/DSAC-WWC.xmind`
- **NotebookLM**: `https://notebooklm.google.com/notebook/9cfddb8e-0d57-4a0b-b66f-4495054daa6a`
- **Daily reports**: write to `<PROJ>/DSAC-WWC/`

### Project 3: Meta-RL for Fault-Tolerant IPC (ACTIVE)

- **Status**: Experiments + paper drafting | **Thesis chapter**: Ch 5
- **Workspace**: `<PROJ>/Meta-RL-FTC/`
- **Code**: `<CODE>/Meta/` (Python PEARL+SAC in `rlkit-simulink/`, MATLAB in `Meta-IPC/`)
- **Overleaf**: `<PROJ>/Meta-RL-FTC/overleaf/`
- **XMind**: `<PROJ>/Meta-RL-FTC/overleaf/Structure.xmind`, `MetaFTC.xmind`, `intro_references.xmind`
- **Research notes**: `<PROJ>/Meta-RL-FTC/Meta-IPC/`
- **NotebookLM**: `https://notebooklm.google.com/notebook/a234fe16-3293-4066-bccd-c341435ad381`
- **Daily reports**: write to `<PROJ>/Meta-RL-FTC/Meta-IPC/`
- **Critical path**: `<PROJ>/Meta-RL-FTC/Meta-IPC/Critical Path.md`

### Project 4: RL-GFM (EARLY -- DESIGN PHASE)

- **Workspace**: `<PROJ>/RL-GFM/`
- **Code**: `<CODE>/GFM-RL/`
- **XMind**: `<PROJ>/RL-GFM/Hybrid GFM-GFCfor FOWTs.xmind`, `Paper Review - RL-Tuned GFM-GFL Weighting for FOWTs.xmind`

### Hierarchical Grader (TOOL)

- **Purpose**: Multi-agent pipeline for grading academic papers at paragraph + sentence level
- **Location**: `<SHARED>/autoresearch-hierarchical-grader/`
- **Entry point**: `python orchestrator.py --input <file> --notebook <key> --output <report>`
- **Architecture**: 5-phase pipeline (Parse, Classify, Evidence, Grade, Rewrite) with 7 subagents
- **Config**: `config/rubric.yaml`, `config/weights.yaml`, `config/notebooklm_notebooks.yaml`
- **Audit**: See `AUDIT_REPORT.md` for known issues

### Thesis

- **Workspace**: `<PROJ>/Thesis/` + `<PHD>/OverLeaf/`
- **Overleaf**: `<PHD>/OverLeaf/Thesis.tex`
- **Structure**: Ch1 Intro, Ch2 Lit Review, Ch3 PINN-HJB, Ch4 DSAC, Ch5 Meta-RL, Ch6 TBD, Ch7 Conclusion
- **Mind maps**: `<PHD>/MindMap/`, `<PHD>/MindMap/DissertationAnalysis/`
- **Thesis NotebookLM**: `https://notebooklm.google.com/notebook/27e615ab-dbca-445f-a29e-75306930d47a`

## Iron Laws

These are non-negotiable.

1. **NO PAPER CLAIM WITHOUT SOURCE EVIDENCE** -- NotebookLM, Zotero, or own simulation data
2. **NO EXPERIMENT WITHOUT LOGGED HYPOTHESIS** -- ask: "What is the hypothesis? What are the controls?"
3. **NO COMPLETION CLAIM WITHOUT VERIFICATION OUTPUT** -- run the command, read the output, then claim done
4. **NO FIX WITHOUT ROOT CAUSE** -- diagnose before editing

## Delivery Standards

- **Truth > Speed**: never claim completion without verification evidence
- **Small Batch**: prefer small, reviewable edits and atomic commits
- **No Secrets**: never commit API keys, tokens, or credentials
- **Reproducibility**: every experiment must log hyperparameters, random seeds, wind file, and fault config
- **Self-verify**: run lint/build/test where applicable before declaring done
- **Banned phrases**: "I fixed it, you try" / "Should be fine" / "Probably passes" / "Theoretically correct"

### LaTeX Standards

- Preserve Overleaf sync compatibility
- Use `authoryear` citation style (`biblatex`, `biber` backend)
- Keep claims source-grounded
- Do not invent references, results, or experimental details

### MATLAB/Python Standards

- Never overwrite simulation results without versioning
- Always document wind file, fault config, training epochs, and reward weights
- Follow OpenFAST signal naming conventions

## Collaboration Preferences

- Act as advisor, devil's advocate, and mirror -- proactively flag blind spots
- **Auto-execute**: bug fixes, small refactors, note creation, XMind-adjacent structuring work
- **Auto-intercept**:
  - New experiment -> ask for hypothesis and controls
  - Paper claim without evidence -> flag immediately
- **Require confirmation**:
  - Reward function changes
  - Simulink model modifications
  - Overleaf structural changes
  - Training hyperparameter changes
  - Thesis structure decisions
  - Literature claims that are about to be cited
- **Never self-decide**: delete experiment data, push to Overleaf, modify MATLAB plant models
- **No filler intros**: go straight to the answer or start working

## SSOT Ownership

| Info Type | SSOT File | Do NOT write to |
|-----------|-----------|-----------------|
| Short-term session notes | Prompt sheet in `<INBOX>/` | CLAUDE.md / AGENTS.md |
| Mid-term project reports | `<PROJ>/{Project}/` workspace (Obsidian .md) | CLAUDE.md / AGENTS.md |
| Daily reports | `<RESEARCH>/Daily Report/` | Project workspace |
| Long-term lessons | `CLAUDE.md` / `AGENTS.md` | Prompt sheets |
| Experiment results + TB reports | Project workspace daily reports | CLAUDE.md / AGENTS.md |
| Paper/thesis structure | XMind maps in the project workspace | plain text notes as authority |
| Paper LaTeX source | Overleaf repo in the project workspace | duplicate copies elsewhere |
| Code | `<CODE>/` repos | Obsidian notes |
| Raw notes inbox | `<INBOX>/` | modify user text |
| Cross-project patterns | `patterns.md` | CLAUDE.md / AGENTS.md |

## Codex-Specific Operating Notes

- Read `<SHARED>/references/codex-tools.md` before interpreting shared docs written for Claude Code.
- Treat `<SHARED>/rules/skill-triggers.md` as Claude-specific unless the user explicitly asks about that layer.
- If a shared doc asks for a Claude slash command, execute the underlying workflow directly instead of requiring the command itself.
- If a shared doc assumes unavailable tooling, skip the unavailable part, explain the constraint briefly, and continue with the nearest safe manual process.
- Use the same three-tier memory system: short-term in `<INBOX>/`, mid-term in project workspaces + `<RESEARCH>/Daily Report/`, long-term in `CLAUDE.md` / `AGENTS.md`.

## On-Demand Loading Index

| Scenario | Read |
|----------|------|
| Tool translation for shared docs | `<SHARED>/references/codex-tools.md` |
| Core behavior rules | `<SHARED>/rules/behaviors.md` |
| Session-end / flush protocol | `<SHARED>/rules/memory-flush.md` |
| XMind formatting work | `<SHARED>/rules/thesis-xmind-format.md` |
| Agent roles / multi-persona review / experiment loop | `<SHARED>/docs/agents.md` |
| Extended behavior details | `<SHARED>/docs/behaviors-extended.md` |
| Debugging techniques reference | `<SHARED>/docs/behaviors-reference.md` |
| AI content safety | `<SHARED>/docs/content-safety.md` |
| Task routing philosophy | `<SHARED>/docs/task-routing.md` |
| Cross-project reusable patterns | `<SHARED>/patterns.md` |

## Graceful Degradation

This shared config was designed for Claude Code first. Codex should preserve the research standards and memory conventions even when a Claude-specific feature does not exist.

- No skills layer available -> read the referenced file or follow the underlying written procedure
- No slash commands available -> perform the workflow manually
- No subagent support available -> work serially
- No MCP/browser integration available -> rely on local files, terminal tools, official APIs already available, or ask the user for the missing source

---

*Last updated: 2026-03-31*
