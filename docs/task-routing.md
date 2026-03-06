# Task Routing & Model Selection

> On-demand loading. Detailed routing table for automatic model dispatch.

## Principle

**Use the cheapest model that can do the job.** Opus is expensive reasoning capacity — don't burn it on formatting fixes. Dispatch subagents via the Agent tool for independent work.

## Model Tier Table

### Opus — Stay in Main Session

Reserved for tasks requiring deep reasoning, memory access, cross-project context, or user interaction.

| Task | Why Opus |
|------|----------|
| Algorithm/model design | Needs literature knowledge + experiment context |
| Architecture decisions | Cascading impact, needs full project understanding |
| Thesis contribution framing | Cross-references all projects |
| Literature synthesis / gap analysis | Requires reasoning across multiple sources |
| Simulation model changes | Complex routing, high-stakes |
| Multi-step debugging (stuck >3 attempts) | Needs memory + pattern recall |
| Paper writing with reference notebook queries | Requires tool orchestration + truth-grounding |
| XMind-driven writing (complex chapters) | Needs to read XMind + query notebook + manage structure |
| Experiment design | Hypothesis formation, control design |
| Any task needing memory/patterns.md | Subagents can't read ~/.claude/memory/ |

### Sonnet — Dispatch as Subagent

Capable model for structured work with clear instructions. Dispatch with `Agent` tool.

| Task | Context to Inject |
|------|-------------------|
| Draft a paper section (XMind already parsed by Opus) | Section outline + content seeds + citation list |
| Code review | File paths + what to look for |
| Experiment log analysis | Log path + healthy metric ranges |
| Daily report writing | Project name + what was done + metrics |
| Obsidian note creation | Vault path + frontmatter template + content |
| XMind creation (structure is clear) | Rules + content specification |
| Literature search summarisation | Search results + relevance criteria |
| Experiment config review | Config path + what to check |
| TEMPORARY_NOTES processing | Note content + project detection hints + vault paths |
| Code refactoring (non-critical, <100 lines) | File path + what to change + constraints |
| Comparing two files/configs | Both file paths + what differences matter |

### Haiku — Dispatch as Subagent

Fastest, cheapest. For mechanical tasks with no ambiguity.

| Task | Context to Inject |
|------|-------------------|
| Fix citation formatting in .bib | File path + style rules |
| Fix typos/grammar | File path + "don't change technical terms" |
| Search codebase for a function/variable | Directory + search term |
| List files matching a pattern | Directory + glob pattern |
| Extract a specific value from a log | File path + what to extract |
| Generate frontmatter for a note | Note content + tag conventions |
| Count lines / summarise file structure | File path |
| Simple find-and-replace across files | Pattern + replacement + scope |
| Generate git commit message | Diff summary |

## Decision Flowchart

```
New task arrives
  |
  +--> Needs memory/patterns/cross-project context? --> OPUS (stay in main)
  |
  +--> Needs user interaction or confirmation? --> OPUS (stay in main)
  |
  +--> Needs multi-tool orchestration (notebook + reference mgr + XMind)? --> OPUS
  |
  +--> Structured work with clear inputs/outputs?
  |      |
  |      +--> Requires reasoning or writing quality? --> SONNET subagent
  |      |
  |      +--> Mechanical / no ambiguity? --> HAIKU subagent
  |
  +--> Multiple independent subtasks? --> PARALLEL subagents (Sonnet or Haiku each)
```

## Subagent Context Injection Template

When dispatching a subagent, always provide:

```
You are helping with [user]'s research on [topic].

## Task
[Specific task description]

## Files
[Exact paths to read/write]

## Constraints
[Style rules, formatting, what NOT to do]

## Output
[Expected output format]
```

**Never assume subagents know the project structure.** Always inject the paths they need.

## Cost Awareness

- Opus: ~$15/M input, ~$75/M output — use for reasoning
- Sonnet: ~$3/M input, ~$15/M output — use for structured work
- Haiku: ~$0.25/M input, ~$1.25/M output — use for mechanical tasks

A 500-line code review in Opus costs ~60x more than in Haiku. If Haiku can spot the bug, let it.

## User Override

**If the user specifies a model in the prompt, use it. No exceptions.**

Examples:
- "use Haiku for this" -> dispatch Haiku subagent
- "do this in Sonnet" -> dispatch Sonnet subagent
- "stay in Opus" / "do this yourself" -> handle in main session
- "Haiku: fix the typos in ch3.tex, Sonnet: rewrite the abstract" -> dispatch both as specified

The user knows the task better than the routing rules. Their explicit dispatch always wins over auto-selection.

## Escalation Rules

- Haiku fails or gives low-quality output -> retry with Sonnet
- Sonnet fails or needs context it doesn't have -> escalate to Opus
- Never retry more than once at the same tier — escalate instead
- If a task was wrongly routed (user corrects), record in patterns.md for future routing
