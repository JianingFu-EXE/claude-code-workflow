# Agent Configuration & Research Collaboration

> On-demand loading. Agent assignment and subagent dispatch for research workflow.

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
| **literature-scout** | Reference discovery | Reference manager import, NotebookLM queries, gap identification |
| **code-reviewer** | Code review | Algorithm correctness, simulation integrity |

### Quick Tier

| Agent | Scope | Core Duty |
|-------|-------|-----------|
| **note-taker** | Obsidian notes | Daily reports, experiment logs, meeting notes |

### Implementation Tier (subagent-driven-development)

| Agent | Scope | Core Duty |
|-------|-------|-----------|
| **implementer** | Task execution | Implement one plan task, self-review, commit |
| **spec-reviewer** | Spec compliance | Verify implementation matches requirements (nothing more, nothing less) |
| **quality-reviewer** | Code quality | Review clean code, tests, maintainability (only after spec passes) |

### Coordinator (Main Agent = Claude)

| Duty | Description |
|------|-------------|
| **Orchestrate** | Dispatch tasks to skills and subagents |
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
You are working on [project-name] for [user]'s research.

## Context Loading (must read first)
1. ~/.claude/memory/today.md — Today's work context
2. Relevant project notes in Obsidian vault

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
| Literature review | notebooklm | reference-import, paper-atlas |
| Paper structure | xmind | paper-manuscript, notebooklm |
| Paper drafting | paper-manuscript | notebooklm, xmind |
| Quick lit question | notebook-query | xmind (for capturing answers) |
| Thesis chapter | obsidian-markdown + LaTeX | notebooklm, xmind |
| Experiment analysis | Direct (code) | obsidian-markdown (for reports) |

---

## Sensitive Operations (Never auto-execute)

- Overleaf git push (thesis or paper repos)
- Reference manager collection deletion or bulk modification
- Simulation model changes
- Training hyperparameter changes that affect running experiments
- Deleting experiment data or checkpoints

---

*Customize agent assignments as your workflow evolves.*
