# PhD Research Workflow -- Claude Code Global Memory

> Auto-loaded = rules/ (behaviors.md, skill-triggers.md, memory-flush.md)
> On-demand = docs/ (agents.md, content-safety.md, task-routing.md, ...)
> Hot data layer = memory/today.md + memory/active-tasks.json (cloud-synced via OneDrive symlinks)

---

## User Info

- **Name**: Jianing Fu | **University**: University of Exeter (Renewable Energy - Cornwall)
- **Identity**: PhD student -- intelligent control of wind turbines (RL, meta-RL, PINN-based control)
- **Supervisor**: Dr. Shuyue Lin
- **Thesis**: "Intelligent load mitigation control of offshore wind turbines"
- **Languages**: MATLAB/Simulink (plant model, OpenFAST), Python (RL training, PEARL/SAC)
- **Philosophy**: Rigorous experimentation + systematic paper-to-thesis pipeline
- **Core pattern**: XMind first, then write. XMind mind maps are the structural blueprint -- Claude reads them as instructions to produce LaTeX, Obsidian notes, or any written output.

### Platform & Tool Stack

| Tool | Purpose | Location |
|------|---------|----------|
| Obsidian | Daily progress, research notes, mind maps | OneDrive PHD vault |
| Overleaf | Thesis + paper drafting (git-synced) | See project paths below |
| Zotero | Reference management (cloud, ID 9312542) | See elsevier-zotero-import skill config |
| NotebookLM | Source-grounded literature Q&A | See notebook URLs below |
| XMind | **Structural blueprint for all writing** -- Claude reads .xmind as instructions | `MindMap/` in PHD vault |
| OpenFAST | Aeroelastic wind turbine simulation | Simulink S-Function |
| TurbSim | Turbulent wind field generation | `.bts` files |

### Key Paths

| Shorthand | macOS | Windows |
|-----------|-------|---------|
| `<PHD>` | `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Obsidian/PHD` | `C:\Users\jf844\OneDrive - University of Exeter\Obsidian\PHD` |
| `<RESEARCH>` | `/Users/jn/Library/CloudStorage/OneDrive-UniversityofExeter/Obsidian/Research` | `C:\Users\jf844\OneDrive - University of Exeter\Obsidian\Research` |
| `<PROJ>` | `<RESEARCH>/Projects` | `<RESEARCH>\Projects` |
| `<INBOX>` | `<RESEARCH>/Inbox` | `<RESEARCH>\Inbox` |
| `<CODE>` | `/Users/jn/Github` | `C:\Users\jf844` |
| `<PYTHON>` | _(not used on Mac)_ | `C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe` |
| `<TB>` | _(not used on Mac)_ | `C:\Users\jf844\Meta\TensorBoard` |

> Claude: detect the current platform from the environment and use the matching column.

### Research Vault Structure
> See rules/behaviors.md § Research Vault Structure

---

## Projects -- Per-Project Workspace Map

Each project is a self-contained workspace. All its artefacts (code, XMind, Overleaf, notes, daily reports) live together under `<PROJ>/{Project}/`. Claude writes daily reports there and reads XMind from there.

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
- **Research notes**: `<PROJ>/Meta-RL-FTC/Meta-IPC/` (Architecture, Critical Path, TB reports, etc.)
- **NotebookLM**: `https://notebooklm.google.com/notebook/a234fe16-3293-4066-bccd-c341435ad381`
- **Daily reports**: write to `<PROJ>/Meta-RL-FTC/Meta-IPC/`
- **Critical path**: `<PROJ>/Meta-RL-FTC/Meta-IPC/Critical Path.md`

### Project 4: RL-GFM (EARLY — DESIGN PHASE)
- **Workspace**: `<PROJ>/RL-GFM/`
- **Code**: `<CODE>/GFM-RL/`
- **XMind**: `<PROJ>/RL-GFM/Hybrid GFM-GFCfor FOWTs.xmind`, `Paper Review - RL-Tuned GFM-GFL Weighting for FOWTs.xmind`

### Thesis
- **Workspace**: `<PROJ>/Thesis/` + `<PHD>/OverLeaf/`
- **Overleaf**: `<PHD>/OverLeaf/Thesis.tex`
- **Structure**: Ch1 Intro, Ch2 Lit Review, Ch3 PINN-HJB, Ch4 DSAC, Ch5 Meta-RL, Ch6 TBD, Ch7 Conclusion
- **Mind maps**: `<PHD>/MindMap/` (thesis-level), `<PHD>/MindMap/DissertationAnalysis/` (reference analysis)
- **Thesis NotebookLM** (examples): `https://notebooklm.google.com/notebook/27e615ab-dbca-445f-a29e-75306930d47a`

---

## Delivery Standards

- **Truth > Speed**: Never claim completion without verification evidence
- **Small Batch**: <=15 files or <=400 lines net change per commit
- **No Secrets**: Never commit API keys/tokens (Zotero, Elsevier, Overleaf credentials)
- **Reproducibility**: Every experiment must log hyperparameters, random seeds, wind file, fault config
- **Self-verify**: Run lint/build/test before declaring done, read output to confirm PASS
- **Banned phrases**: "I fixed it, you try" / "Should be fine" / "Probably passes" / "Theoretically correct"

### LaTeX Standards
- Preserve Overleaf sync compatibility -- no destructive renames
- Use `authoryear` citation style (biblatex, biber backend)
- Keep technical claims source-grounded (paper text, references, or NotebookLM)
- Do not invent references, results, or experimental details

### MATLAB/Python Standards
- Never overwrite simulation results without versioning
- Always document: wind file, fault config, training epochs, reward weights
- Signal naming follows OpenFAST conventions (e.g., `RootMxc1`, `RotSpeed`, `BldPitch1`)

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

- Act as advisor, devil's advocate, mirror -- proactively point out blind spots, never be a yes-man
- **Auto-execute**: Bug fixes, <=100 line refactors, Obsidian note creation, XMind generation
- **Auto-intercept**:
  * **New experiment** -> Ask: "What is the hypothesis? What are the controls?"
  * **Paper claim without evidence** -> Flag immediately
- **Require confirmation (stop and check in)**:
  * Reward function changes (affects all training)
  * Simulink model modifications
  * Overleaf structural changes (chapter reordering, section deletion)
  * Training hyperparameter changes (beta, alpha, latent_dim, learning rates)
  * Thesis structure decisions
  * Literature claims to be cited
- **Never self-decide**: Delete experiment data, push to Overleaf, modify MATLAB plant models
- **Banned**: "Is this OK?" / "Should I pick A or B?" / "Should I continue?"
- **No filler intros**: Go straight to the answer or start working

---

## Experience Recall & Evolution
> See rules/behaviors.md § Real-time Experience Recording + Memory Search Rules

---

## SSOT Ownership (Single Source of Truth)

| Info Type | SSOT File | Do NOT write to |
|-----------|-----------|-----------------|
| Daily reports (per-project) | `<PROJ>/{Project}/` workspace (Obsidian .md) | today.md, MEMORY.md |
| Cross-project overview | `memory/projects.md` | (summary + pointers only) |
| Technical pitfalls | `MEMORY.md` (per-project auto memory) | today.md |
| Session-level progress | `memory/today.md` → `<RESEARCH>/today.md` (cloud-synced) | (running log, cleared on Level 2 flush) |
| In-flight task registry | `memory/active-tasks.json` → `<RESEARCH>/active-tasks.json` (cloud-synced) | (cross-session, cross-device task status) |
| Experiment results + TB reports | Project workspace daily reports | MEMORY.md |
| Paper/thesis structure | XMind maps in project workspace (authoritative) | Plain text notes |
| Paper LaTeX source | Overleaf repo in project workspace | Duplicate elsewhere |
| NotebookLM references | Per-project notebook (see URLs above) | Don't duplicate content |
| Zotero/NotebookLM config | PHD vault `AGENTS.md` | Duplicate elsewhere |
| Code | `<CODE>/` repos (MATLAB + Python) | Obsidian notes |
| Raw notes inbox | `<INBOX>/` -- user writes here, Claude sorts at end-of-day | Modify user text |
| Key data points | `MEMORY.md` (Key Data Points section) | today.md |

---

## Memory Write Routing

| Layer | File | What to write |
|-------|------|---------------|
| Auto Memory | Project `MEMORY.md` | Technical pitfalls, API details, tool configs |
| Pattern library | `patterns.md` | Cross-project reusable patterns |
| Hot data layer | `today.md` | Daily progress, handoff |
| Task registry | `active-tasks.json` | Cross-session in-flight tasks |

### Sub-project Memory Routes

> Claude: use the path matching the current platform (detect from environment).

| Keywords | macOS memory path | Windows memory path |
|----------|-------------------|---------------------|
| thesis/chapter/overleaf/dissertation | `~/.claude/projects/-Users-jn-Library-CloudStorage-OneDrive-UniversityofExeter-Obsidian-PHD/memory/MEMORY.md` | `~/.claude/projects/C--Users-jf844-OneDrive---University-of-Exeter-Obsidian-PHD/memory/MEMORY.md` |
| meta-rl/PEARL/FTC/fault/IPC/Meta-IPC | `~/.claude/projects/-Users-jn-Library-CloudStorage-OneDrive-UniversityofExeter-Obsidian-Research/memory/MEMORY.md` | `~/.claude/projects/C--Users-jf844-OneDrive---University-of-Exeter-Obsidian-Research/memory/MEMORY.md` |
| PINN/HJB/Ocean Engineering/active TMD | `~/.claude/projects/-Users-jn-Library-CloudStorage-OneDrive-UniversityofExeter-Obsidian-PHD/memory/MEMORY.md` | `~/.claude/projects/C--Users-jf844-OneDrive---University-of-Exeter-Obsidian-PHD/memory/MEMORY.md` |
| DSAC/distributional/TSTE/WWC | `~/.claude/projects/-Users-jn-Library-CloudStorage-OneDrive-UniversityofExeter-Obsidian-PHD/memory/MEMORY.md` | `~/.claude/projects/C--Users-jf844-OneDrive---University-of-Exeter-Obsidian-PHD/memory/MEMORY.md` |

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
| Debugging (7 investigation techniques) | `Read docs/behaviors-reference.md § Investigation Techniques` |
| Experiment iteration loop | `Read docs/agents.md § Constraint-Driven Experiment Loop` |
| Multi-persona paper review | `Read docs/agents.md § Multi-Persona Review` |
| Debugging command | `/debug` |
| Paper/thesis review | `/review` |
| Research direction challenge | `/exploration` |
| TensorBoard report | `/tb-report` |

---

*Last updated: 2026-03-21*
