# Behaviors Reference

> On-demand loading. Detailed operation guides for specific scenarios.

## MATLAB/Simulink Operations

### Reading Simulink Models
- Export to JSON/XML for inspection when .slx direct read isn't possible
- Check signal routing via From/Goto tags
- Verify block parameter values match documentation

### OpenFAST Integration
- S-Function interface: inputs are pitch commands (3), outputs are turbine states
- Sampling time: 0.0125s (80 Hz)
- Key outputs: RotSpeed, BldPitch1-3, RootMxc1-3, Azimuth, GenPwr
- Fault model: effectiveness factor eta in [0, 1] applied to actuator transfer function

### MATLAB Function Blocks
- `reward.m`: Computes RL reward from Mtilt, Myaw, pitch rates
- `normalize_inputs.m`: Scales raw states to [-1, 1] range
- `FaultSelection.m`: Maps subtask index to per-blade fault modes
- `ActionSelectionSwitch.m`: Coleman transform for IPC
- `fcn_SymmetryIndicator.m`: Monitoring metric

## Investigation Techniques (for Debugging Protocol Phase 1-3)

Seven structured techniques — pick the one that fits the symptom:

1. **Binary Search** — Bisect the problem space. Comment out half the code, test. Narrow to the half that breaks. Repeat. Best for: "it broke somewhere in this large change."

2. **Differential Debugging** — Compare working vs broken state. `git diff` between last-good and first-bad. Inspect every changed line. Best for: "it worked yesterday."

3. **Minimal Reproduction** — Strip everything down to the smallest case that still fails. Remove variables, simplify inputs, reduce scope until only the bug remains. Best for: complex system failures.

4. **Trace Execution** — Follow data flow step by step. Print intermediate values, check tensor shapes, verify signal dimensions at each stage. Best for: silent corruption (wrong output, no error).

5. **Pattern Search** — Grep for similar bugs in git history, MEMORY.md, patterns.md. Someone (including past-you) may have hit this before. Best for: recurring errors.

6. **Working Backwards** — Start from the symptom (wrong reward, bad pitch angle) and trace backwards through the call chain to the root input that caused it. Best for: known-bad output, unknown cause.

7. **Rubber Duck** — Explain the problem out loud (or in writing). The act of articulating forces you to notice the gap in your understanding. Best for: "I have no idea what's wrong."

### When to use which

| Symptom | Start with |
|---------|-----------|
| "It broke after my last change" | Differential Debugging |
| "Wrong output, no error" | Trace Execution |
| "Complex crash, many variables" | Minimal Reproduction |
| "Seen something like this before" | Pattern Search |
| "Totally lost" | Rubber Duck → then Binary Search |

## Experiment Iteration Logging (autoresearch pattern)

When running iterative experiments (reward tuning, hyperparameter search, architecture ablation), log every iteration in TSV format in the project workspace:

**File**: `<PROJ>/{Project}/autoresearch-results.tsv`

```
iteration	commit	metric	delta	guard	status	description
0	a1b2c3d	85.2	0.0	pass	baseline	initial state — DEL reduction 85.2%
1	b2c3d4e	87.1	+1.9	pass	keep	increased J_load weight from 40 to 50
2	-	86.5	-0.6	-	discard	reduced alpha lr (regression)
```

**Rules**:
- Commit BEFORE verification (enables clean `git revert` on failure)
- Revert (don't reset) on discard — preserves failed experiment in history for learning
- Read git history at start of each iteration to learn from prior results
- Guard command must always pass (regression check) — separate from metric improvement

### Noise handling for simulation metrics
- Fix random seed + wind file for reproducibility
- Run 3+ seeds, report median ± std
- Minimum improvement threshold (>2%) to filter noise
- If metric oscillates: suspect environment issue, not code issue

## Python RL Operations

### PEARL Training
- Config: `meta.yaml` in project root
- Key params: `latent_dim`, `num_train_tasks`, `context_size`, `beta_lr`, `target_kl`
- Encoder: TCN + LSTM -> Product of Gaussians -> latent z
- Policy: TanhGaussianPolicy conditioned on [obs, z]
- Training: SAC with automatic alpha tuning

### Common Failure Modes
- z frozen at zero: `infer_posterior()` not called during rollouts
- Posterior collapse: KL divergence -> 0, all tasks produce same z
- Buffer corruption: cross-episode sequences at buffer boundary
- Device mismatch: CPU/GPU tensor mixing

## Overleaf/LaTeX Operations

### Thesis Compilation
- Backend: biber (not bibtex)
- Citation style: authoryear
- Chapter files: `ch1/introduction.tex` through `ch7/summaryconclusion.tex`
- Bibliography: `refs.bib`
- Custom commands: `\first{}` (red), `\second{}` (blue), `\third{}` (green)

### Staging (temporary.tex)
- **All new/modified content goes to `temporary.tex`**, never directly to `main.tex`
- `temporary.tex` copies the full preamble from `main.tex` so it compiles independently
- Additions highlighted with `\added{}` (blue), deletions with `\deleted{}` (red strikethrough)
- User audits iteratively until satisfied, then says "merge" / "push to main"
- On merge: strip highlighting commands, apply changes to `main.tex`, delete `temporary.tex`

### Git Sync
- Thesis repo: `<PHD_VAULT>/OverLeaf/`
- Meta-RL paper repo: separate Overleaf project
- Always pull before editing, push only with user confirmation

## Obsidian Operations

### PHD Vault Structure
- `Papers/`: Own published/submitted papers (LaTeX source)
- `Examples/`: Reference dissertations
- `MindMap/`: XMind files for structure planning
- `OverLeaf/`: Thesis files (git-synced)
- `Daily Notes/`: Session progress reports

### Research Vault
- `Projects/Meta-RL-FTC/Meta-IPC/`: Active research notes
- Contains: Architecture, Critical Path, Training Diagnosis, TB reports, daily reports

## Zotero Operations

- Library ID: 9312542, type: user
- Credentials: See elsevier-zotero-import skill config
- `Thesis-Background` collection: 88+ papers
- Use elsevier-zotero-import skill for bulk import from Scopus/ScienceDirect
