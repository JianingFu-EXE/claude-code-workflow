# Patterns Library

<!--
  Cross-project reusable patterns discovered through experience.
  Update: When a lesson applies beyond a single project.
-->

## PEARL/Meta-RL Patterns

### Posterior Collapse Detection
- **Symptom**: KL divergence drops to ~0, all tasks produce identical z
- **Causes**: KL sign error, beta too high, encoder too weak, insufficient task diversity
- **Check**: TensorBoard KL curve + per-task reward separation

### z Must Be Updated During Rollouts
- **Lesson**: If `infer_posterior()` is never called during data collection, z stays at zero
- **Impact**: Policy cannot condition on task embedding -> behaves like vanilla SAC
- **Fix**: Call `agent.infer_posterior(agent.context)` inside collection loop

### Replay Buffer Cross-Boundary Sequences
- **Lesson**: When sampling sequences from circular buffer, sequences can cross episode boundaries
- **Fix**: Reject sequences that span `_top` boundary; add bounded retry with fallback

## Simulink/OpenFAST Patterns

### Normalization Reference Consistency
- **Lesson**: reward.m and normalize_inputs.m must use the same M_ref values
- **Impact**: Observation clips before reward saturates, or vice versa
- **Check**: Compare reference values in both files before any reward redesign

### Fault Mode Indexing Asymmetry
- **Lesson**: Blade 1 has 7 fault modes (eta: 1.0, 0.4-0.9), Blades 2/3 have only 4 (eta: 1.0, 0.55, 0.7, 0.85)
- **Impact**: Same subtask index maps to different effectiveness on different blades
- **Consideration**: Must handle when `fault_any_blade: true`

## LaTeX/Academic Writing Patterns

### Overleaf Git Sync
- **Lesson**: Always `git pull` before editing, `git push` only with user confirmation
- **Risk**: Force push overwrites collaborator changes

### Citation Style
- **Convention**: authoryear (biblatex + biber), `\citep{}` and `\citet{}`
- **Gotcha**: `maxcitenames=3` means 4+ authors become "et al." in text

## Zotero/NotebookLM Patterns

### Elsevier Import
- **Config**: Credentials in `/Users/jn/.config/elsevier-zotero-import.env`
- **Library**: ID 9312542, type user
- **Lesson**: Use skill for bulk Scopus import; manually verify key papers after

### NotebookLM Source Grounding
- **Lesson**: NotebookLM answers are grounded in uploaded sources only
- **Use**: Ideal for verifying claims against specific papers before citing
- **Limit**: Cannot find papers not uploaded to the notebook
