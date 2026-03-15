# Skill Trigger Rules

> Scenario match -> auto-trigger. Each rule has "Use when" / "NOT when" for accurate routing.

## P0 Mandatory

| Scenario | Skill | NOT when |
|----------|-------|----------|
| Error/Bug (test/build/simulation failure) | systematic-debugging | Missing env var/path error (fix directly); user already gave fix |
| Before claiming completion | verification-before-completion | Pure research/exploration/Q&A; only changed docs/comments |
| Exit signal ("that's all"/"heading out"/etc.) | session-end + memory-flush | Brief pause; mid-task looking at something else |

## Research Skill Triggers

<!--
  Add triggers for your research-specific skills here. Examples:

  | Scenario | Skill | NOT when |
  |----------|-------|----------|
  | "Create a mind map" / "structure this" / XMind | xmind | User wants plain text outline |
  | Working with .md in Obsidian / wikilinks / callouts | obsidian-markdown | Plain markdown outside Obsidian |
  | "Query NotebookLM" / "ask the notebook" / source-check | notebooklm | Question answerable from local files |
  | "Find papers" / "search ScienceDirect" / "import to Zotero" | elsevier-zotero-import | Already have the papers |
  | Paper drafting with XMind structure + NotebookLM + Zotero | paper-manuscript | Simple LaTeX editing |
  | Literature mapping: XMind -> NotebookLM -> Zotero annotations | paper-atlas | Simple reference lookup |
  | Using Claude API / Anthropic SDK | claude-api | General programming |
-->

## Development Workflow Triggers

| Scenario | Skill | NOT when |
|----------|-------|----------|
| Multi-step implementation with spec/requirements | writing-plans | User gave step-by-step instructions; single-file change |
| Executing a plan with independent tasks + subagents available | subagent-driven-development | Tasks are tightly coupled; no subagent support |
| Implementing any feature or bugfix | test-driven-development | Throwaway prototype; config files; user said skip TDD |
| 2+ independent failures / tasks with no shared state | dispatching-parallel-agents | Failures are related; agents would edit same files |

## P1-P2

| Scenario | Action | NOT when |
|----------|--------|----------|
| Stuck >15min | experience-evolution | Known issue in patterns.md |
| 3 consecutive failures | Pause, revert to debugging Phase 1 | Each failure is a different problem |
| Complex task >5 files | Suggest writing-plans | User gave step-by-step instructions |

## Skill Security Audit

**Trigger**: Adding/installing skill files, adding MCP server, or importing third-party code

**Auto-scan red flag patterns**:
- HTTP URLs (especially POST/PUT/upload)
- Network calls: `curl`, `requests.post`, `fetch(`, `axios`
- File exfiltration: `zip`/`tar` + send, `upload`
- Destructive operations: `rm -rf`, `delete`, `encrypt`
- Obfuscation/dynamic execution: `base64`, `eval`, `exec`

**Red flags found** -> List specifics + wait for user confirmation
**No red flags** -> Normal execution

## Hard Rules
- Scenario matches but doesn't trigger = process violation
- Never downgrade P0 triggers
- Never try >2 approaches on same URL (2 failures -> tell user)
