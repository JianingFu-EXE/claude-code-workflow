# Codex CLI Compatibility for .claude-shared

**Date**: 2026-03-31
**Status**: Approved
**Scope**: Add OpenAI Codex CLI support to the existing cross-platform Claude Code configuration

---

## Problem

The `.claude-shared` project is a cross-platform PhD research workflow configuration that currently only works with Claude Code (Anthropic's CLI). The user wants Codex CLI (OpenAI) to also read from this shared config, acting as a lightweight assistant that shares the same core context — identity, project map, rules, memory — without attempting full feature parity with Claude Code's skill/superpowers infrastructure.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Feature level | Lightweight assistant (not full parity) | Codex lacks skills, superpowers, MCP. Forcing parity creates brittle duplicates. |
| File structure | Hybrid: inline core + on-demand references | Codex gets enough context immediately; detailed rules loaded when relevant. Avoids duplicating SSOT. |
| Location | Single `AGENTS.md` in `.claude-shared/` root | Symlinked like `CLAUDE.md`. One file to maintain. Codex inherits via parent directory lookup. |

## Deliverables

### 1. `AGENTS.md` (NEW — project root)

Codex CLI's instruction file. Hybrid structure:

**Inline sections** (available immediately):
- Header identifying this as the Codex counterpart to CLAUDE.md
- User info: name, university, research focus, supervisor, thesis title
- Platform & tool stack table
- Key paths table (macOS/Windows)
- Project map: all 4 projects + thesis with workspace paths, status, code, XMind, NotebookLM URLs
- Iron laws (4 non-negotiable rules, copied verbatim from behaviors.md since they're short and critical)
- Delivery standards (truth > speed, small batch, no secrets, reproducibility, self-verify, banned phrases)
- Collaboration preferences (auto-execute, auto-intercept, require confirmation, never self-decide)
- SSOT ownership table
- Tool mapping note directing Codex to `references/codex-tools.md`

**On-demand references** (Codex reads when relevant):
- `rules/behaviors.md` — debugging protocol, project context auto-detection, atomic commits, experiment reproducibility
- `rules/memory-flush.md` — session end protocol (Level 1/Level 2 flush)
- `docs/agents.md` — agent roles, multi-persona review, experiment loop
- `docs/task-routing.md` — model selection guidance (Codex adapts to its own models)
- `patterns.md` — cross-project reusable patterns
- `rules/thesis-xmind-format.md` — only when doing XMind work
- Other `docs/` files as contextually needed

**Explicitly excluded** (noted as Claude Code-only):
- Skills system / superpowers — no Codex equivalent
- `rules/skill-triggers.md` — skill dispatch doesn't apply to Codex
- MCP server integrations

**Graceful degradation**: Where shared docs reference unavailable features (Agent tool, Skill tool, WebFetch, MCP), AGENTS.md instructs Codex to skip those instructions and use the closest available alternative or flag to the user.

### 2. `references/codex-tools.md` (NEW)

Tool name mapping so Codex can interpret shared docs written for Claude Code:

| Claude Code Tool | Codex Equivalent | Notes |
|---|---|---|
| `Read` | `read_file` | Same purpose |
| `Write` | `write_file` | Same purpose |
| `Edit` | `patch` | Codex uses patch-style edits |
| `Glob` | `shell` + `find`/`ls` | No dedicated glob tool |
| `Grep` | `shell` + `grep`/`rg` | No dedicated search tool |
| `Bash` | `shell` | Same purpose |
| `Agent` (subagent) | N/A | Not available in Codex |
| `Skill` | N/A | Not available in Codex |
| `TaskCreate/Update` | N/A | Track manually or via comments |
| `WebFetch/WebSearch` | N/A | Not available |

Short file. Read once at session start.

### 3. `SETUP.md` (UPDATE)

Add a new section for Codex CLI setup:
- Symlink `AGENTS.md` to wherever Codex expects it (project root or `~/.codex/`)
- Same OneDrive sync pattern as Claude Code
- Note which files are shared vs local-only

### 4. `autoresearch-hierarchical-grader/AGENTS.md` (NEW)

Project-specific AGENTS.md for the hierarchical grader tool, now located within `.claude-shared/`. Contains:

- **Inline**: Pipeline architecture (5 phases, 7 subagents), key files table, IR dataclass structure, section type enum, config file purposes, known audit issues (26 findings, 2 critical), development rules, quick reference commands
- **Reference to global**: Points to parent `AGENTS.md` / `CLAUDE.md` for user identity and research rules
- **Reference to local**: Points to `AUDIT_REPORT.md` for full issue details

This serves as the entry point for any AI agent (Claude Code or Codex) working on the grader codebase.

## What Is NOT Changing

- `CLAUDE.md` — untouched
- `rules/` — shared as-is, no modifications
- `docs/` — shared as-is, no modifications
- `memory/` — shared read/write by both tools
- `patterns.md` — shared as-is
- `skills/` — remains Claude Code-only

## Maintenance Model

- **CLAUDE.md** and **AGENTS.md** share the same source data (user info, project map, delivery standards). When these change, both files need updating.
- **Rules and docs** are SSOT — referenced by both files, maintained once.
- **Iron laws** are duplicated inline in both files (4 short rules, critical enough to justify duplication for immediate availability).
- **Tool mapping** (`references/codex-tools.md`) only changes if Claude Code or Codex rename their tools.

## Success Criteria

1. Codex CLI reads `AGENTS.md` and has full context about the user, projects, and research workflow
2. Codex can read shared `rules/` and `docs/` files and interpret Claude Code tool references via the mapping
3. Codex reads/writes the same `memory/` system (today.md, active-tasks.json, MEMORY.md)
4. No duplication of rule content between CLAUDE.md and AGENTS.md (iron laws excepted)
5. Graceful handling of unavailable features (skills, MCP, subagents)
6. Grader project has its own AGENTS.md with architecture context, referencing the global config
7. Grader project listed in the global AGENTS.md project map
