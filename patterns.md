# Cross-Project Patterns

> Quick-reference for recurring patterns across all PhD projects.
> Check this file before debugging, before writing, before experimenting.
> Write back here whenever a new cross-project pattern emerges.

---

## Debugging

**Protocol: no blind fixes. Four phases — always in order.**
1. Root Cause — read the error, reproduce it, trace the data flow
2. Pattern Analysis — find a working example, compare
3. Hypothesis Testing — change one variable at a time
4. Fix & Verify — test before the fix, verify no regression after

**Why:** Skipping to "fix" without root cause wastes hours and introduces new bugs.

**When to stop:** 3 consecutive failures on the same issue -> pause, revert to Phase 1, reassess.

---

## MATLAB / Simulink

**Signal dimensions are the #1 source of Simulink errors.**
- Check dimensions first before any other hypothesis.
- Mux/demux mismatches and bus signal width changes are the most common culprits.

**Normalization must be consistent across all files.**
- `reward.m` and `normalize_inputs.m` must use the same reference values.
- A silent normalization mismatch causes training to appear to run but produce garbage rewards.

**Fault mode indexing is asymmetric — check before modifying.**
- Blade 1: 7 fault modes
- Blades 2 and 3: 4 fault modes each
- Any code that iterates over fault modes must handle blade 1 as a special case.

**Never overwrite simulation results.**
- Version with date suffix or commit hash.
- Even a small change in wind file or fault config produces a different result — they are not interchangeable.

**Signal naming: follow OpenFAST conventions.**
- Use names like `RootMxc1`, `RotSpeed`, `BldPitch1` consistently.
- Deviating from convention breaks compatibility with log parsers and post-processing scripts.

---

## Python RL (PEARL / SAC / DSAC)

**Device consistency: CPU/GPU mismatch silently corrupts tensor operations.**
- Check that all tensors (observations, actions, context z) are on the same device before any operation.
- Most common site: context encoder output vs. policy network input.

**Replay buffer cross-boundary contamination.**
- When sampling, verify that episode boundaries are respected.
- PEARL's context buffer especially: contaminated context = wrong task encoding = failed adaptation.

**Context encoder input dimensions must match `obs_index` configuration.**
- After any change to `obs_index`, recheck: context encoder input dim, policy input dim, buffer storage dim.
- These three must all be updated together — changing one silently breaks the others.

**Verify z is actually updated during rollouts.**
- z frozen at zero is a common silent failure. The policy runs, rewards look plausible, but the agent is not adapting.
- Add a z-norm log during rollout to catch this early.

**Never delete files without explicit instruction.**
- Even tiny files (e.g. 88-byte TensorBoard events) may belong to an active process.
- If a file looks suspicious or stale, ask — do not delete it.

---

## LaTeX / Overleaf

**Never write directly to `main.tex`. Use `temporary.tex` staging.**
- All additions and deletions go into `temporary.tex` first.
- Use `\added{...}` (blue) and `\deleted{...}` (red strikethrough) to highlight changes.
- Merge into `main.tex` only after explicit user approval ("OK to push" / "merge it").
- Why: Overleaf is the paper SSOT. Unreviewed edits directly to `main.tex` risk losing work and breaking compilation.

**Citation style: `authoryear` (biblatex, biber backend).**
- All projects use this style. Never switch to `numeric` or `footnote` without confirmation.
- Citation keys must match Zotero entries — cross-check after NotebookLM provides a reference.

**Every technical claim must be source-grounded.**
- Trace to: NotebookLM-verified source, own simulation results (with run reference), or explicit mathematical derivation.
- Unverified claims: flag as `\first{[UNVERIFIED: need source]}` — never silently include them.

**Preamble must be copied into `temporary.tex` so it compiles independently.**
- Include `\usepackage{xcolor}`, `\usepackage[normalem]{ulem}`, and the `\added`/`\deleted` command definitions.

---

## XMind / Writing Workflow

**XMind-first: always read the mind map before writing.**
- Workflow: User builds structure in XMind -> Claude reads XMind -> Claude writes output.
- Never start writing a paper section, thesis chapter, or structured note without checking for an existing XMind.

**Treat XMind as a structural specification, not a suggestion.**
- Topic hierarchy = section/subsection hierarchy
- Topic notes = content seed (expand, do not contradict)
- Labels = role (Framing/Background/Methodology/Closing)
- Markers = priority/ordering
- Relationships = cross-references to honour

**If no XMind exists for the requested output:** ask the user whether to create one first or proceed freeform.

**Never contradict XMind structure** without flagging the deviation and getting confirmation.

---

## Experiment Reproducibility

**Every run must be fully traceable. Log before starting:**
- Wind file (.bts path)
- Fault configuration (blade, mode, severity)
- Random seed
- Reward weights
- Key hyperparameters (beta, alpha, latent_dim, learning rates, batch size)

**After the run, record:**
- TensorBoard path
- Checkpoint path
- Key metrics (reward, KL divergence, alpha)

**Versioning rule:** date suffix or commit hash on all result files. No exceptions.

**Before starting a new experiment, Claude auto-intercepts:**
- "What is the hypothesis?"
- "What are the controls?"

---

## Memory / Session Management

**Before debugging, check MEMORY.md and patterns.md first.**
- Most errors are recurring. Reading memory takes 10 seconds. Reinventing the fix takes hours.

**Record lessons immediately when corrected, not at session end.**
- Trigger: corrected by user -> write to MEMORY.md before the next tool call.
- Trigger: 3 consecutive failures -> pause and record what was tried.
- Trigger: counter-intuitive discovery -> record immediately.

**Write-back targets:**
| What you discovered | Where to write |
|---------------------|----------------|
| Project-specific pitfall | Project `MEMORY.md` |
| Cross-project reusable lesson | This file (`patterns.md`) |
| Session progress | `memory/today.md` |
| Experiment result | Project workspace daily report |

**Session end: always flush all three layers.**
- Long-term: MEMORY.md + patterns.md
- Mid-term: today.md + project daily reports
- Inbox: process `<RESEARCH>/Inbox/` (frontmatter + sort + Claude's Notes)

---

## Obsidian / Vault Workflow

**Inbox (`<RESEARCH>/Inbox/`) is the user's raw capture zone.**
- Do NOT modify the user's original text.
- Only prepend frontmatter (title, date, tags, project) and append `## Claude's Notes` at the bottom.
- Move to the correct folder after adding frontmatter.

**Daily reports go in the project workspace, not in `today.md`.**
- `today.md` is Claude's internal scratchpad.
- The user tracks progress via project workspace daily reports (`<PROJ>/{Project}/YYYY-MM-DD Daily Report.md`).

**Vault structure (post-March 2026 restructure):**
- `Inbox/` (raw captures) -> `Projects/{Project}/` (sorted, structured) -> `Notes/` (mature knowledge)
- `PAPER_NOTES/` for literature notes, `DAILY_NOTES/` for date-stamped logs (if applicable)

---

## Git / Code Commits

**Atomic commits: one change per commit.**
- Types: `fix/feat/refactor/docs/test/chore`
- Banned: mixed changes, vague messages, >100 lines without splitting

**Never commit secrets.**
- API keys, Zotero credentials, Elsevier tokens, Overleaf credentials — never in git history.

---

*Last updated: 2026-03-16*
