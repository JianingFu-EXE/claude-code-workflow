# Agent Configuration & Research Collaboration

> On-demand loading. Agent assignment and subagent dispatch for PhD research workflow.

---

## Agent Roles

### Critical Tier (careful reasoning required)

| Agent | Scope | Core Duty |
|-------|-------|-----------|
| **thesis-architect** | Thesis structure | Chapter flow, contribution framing, argument coherence |
| **experiment-designer** | Simulation/training setup | Hypothesis validation, control design, statistical rigour |

### Standard Tier (daily research work)

| Agent | Scope | Core Duty |
|-------|-------|-----------|
| **paper-drafter** | Paper/chapter writing | LaTeX drafting, literature integration, claims grounding |
| **literature-scout** | Reference discovery | Zotero import, NotebookLM queries, gap identification |
| **code-reviewer** | Python/MATLAB review | RL algorithm correctness, Simulink signal integrity |

### Quick Tier

| Agent | Scope | Core Duty |
|-------|-------|-----------|
| **note-taker** | Obsidian notes | Daily reports, experiment logs, meeting notes |

### Coordinator (Main Agent = Claude)

| Duty | Description |
|------|-------------|
| **Orchestrate** | Dispatch tasks to skills (NotebookLM, Zotero, XMind, etc.) |
| **Decide** | Final judgment on research direction, paper claims |
| **Memory** | Maintain hot data layer (today.md, MEMORY.md) |
| **Challenge** | Devil's advocate on experimental design and paper claims |

---

## Subagent Dispatch Rules

> Default parallel for independent tasks

**Trigger conditions**:
- >=2 independent tasks (e.g., literature search + code fix)
- Complex task can be split (e.g., draft two sections simultaneously)

**Memory injection protocol (mandatory when dispatching)**:
```
You are working on [project-name] for Jianing Fu's PhD.

## Context Loading (must read first)
1. ~/.claude/memory/today.md -- Today's work context
2. Relevant project notes in Obsidian PHD/Research vaults

## Task
[Specific task description]

## Completion Requirements
1. Verify output quality
2. Report results with evidence
```

---

## Cross-Tool Orchestration

| Research Task | Primary Skill | Supporting Tools |
|---------------|--------------|------------------|
| Literature review | notebooklm | elsevier-zotero-import, paper-atlas |
| Paper structure | xmind | paper-manuscript, notebooklm |
| Paper drafting | paper-manuscript | notebooklm, xmind |
| Quick lit question | notebook-query | xmind (for capturing answers) |
| Thesis chapter | obsidian-markdown + LaTeX | notebooklm, xmind |
| Experiment analysis | Direct (Python/MATLAB) | obsidian-markdown (for reports) |

---

## Sensitive Operations (Never auto-execute)

- Overleaf git push (thesis or paper repos)
- Zotero collection deletion or bulk modification
- MATLAB plant model changes (Simulink .slx)
- Training hyperparameter changes that affect running experiments
- Deleting experiment data or checkpoints

---

## Multi-Persona Review (pre-submission paper audit)

Before submitting a paper, run a reviewer swarm — 3 independent Sonnet subagents critique the paper from different angles, then synthesize:

| Persona | Focus | Challenge style |
|---------|-------|----------------|
| **Reviewer 1: Methodology Expert** | Statistical rigour, experiment design, reproducibility | "Is the comparison fair? Are the baselines appropriate? Is N sufficient?" |
| **Reviewer 2: Domain Skeptic** | Wind turbine physics, control theory assumptions, practical feasibility | "Would this work on a real turbine? What about [physical constraint]?" |
| **Reviewer 3: Devil's Advocate** | Overclaiming, missing limitations, alternative explanations | "Could this result be explained by [simpler mechanism]? What's the weakest claim?" |

### Protocol:
1. Each persona reads the paper independently (parallel subagents)
2. Each produces structured feedback: Major Issues / Minor Issues / Questions
3. Coordinator (Opus) synthesizes: consensus findings, conflicting views, recommended actions
4. User reviews synthesized feedback before revising

### Anti-groupthink:
- Devil's Advocate is mandatory — must disagree with at least one finding from the other reviewers
- If all three agree on everything, flag as suspicious (real reviewers rarely agree completely)

> Invoke: Dispatch 3 Sonnet subagents with the paper text + persona instructions. Synthesize in main context.

---

## Constraint-Driven Experiment Loop (autoresearch pattern)

For iterative experiment optimization (reward tuning, hyperparameter search):

```
Goal:       [what to improve]
Scope:      [files Claude can modify]
Metric:     [what number to track] (higher/lower is better)
Verify:     [shell command that outputs the metric]
Guard:      [command that must always pass — regression check]
Iterations: [N or unlimited]
```

**Loop**: Review git history → Ideate one change → Modify → Commit → Verify → Keep/Revert → Log to TSV → Repeat

**Rules**: One atomic change per iteration. Commit BEFORE verify. `git revert` (not reset) on discard. Read prior iterations to avoid repeating failures.

> See docs/behaviors-reference.md § Experiment Iteration Logging for TSV format.

---

*Customize as your workflow evolves.*
