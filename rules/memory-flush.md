# Memory Flush

> Three-tier memory system. Don't rely on user triggers -- auto-save. User might close the window at any time.

## Three Tiers

| Tier | Where | What | Lifecycle |
|------|-------|------|-----------|
| **Short term** | Prompt sheet in `<INBOX>/` | Session progress, decisions, blockers | Updated during work. Cleared on `/clear`, `/compact`, `/exit` — promote important bits first |
| **Mid term** | Project workspace `<PROJ>/{Project}/` + `<RESEARCH>/Daily Report/` | Project reports, daily reports, conclusions | Written when work reaches a milestone or on "call it a day" |
| **Long term** | `CLAUDE.md` / `AGENTS.md` | Persistent lessons, workflow changes, config updates | Updated when something matters across all future sessions |

## Short Term: Prompt Sheet

During a session, maintain a prompt sheet in `<INBOX>/` as an Obsidian .md file.

- Update with progress notes after finishing a piece of work
- On `/clear`, `/compact`, or `/exit`: promote anything important to the appropriate tier before the context is lost

## Mid Term: Project Reports + Daily Reports

### Project Report (milestone-driven)

When work on a project reaches a reportable conclusion, write a report in the project workspace (`<PROJ>/{Project}/`).

### Daily Report (end-of-session)

**Trigger**: "Call it a day" / exit signal from user.

Write a daily report to `<RESEARCH>/Daily Report/YYYY-MM-DD Daily Report.md`:
- Summarize what was achieved across all projects worked on
- Include decisions, results/metrics, next steps
- Append if a report for today already exists

## Long Term: CLAUDE.md / AGENTS.md

When a session produces an important, persistent lesson — update `CLAUDE.md` (for Claude Code) and/or `AGENTS.md` (for Codex). These are the long-term memory.

Examples: new workflow rule, tool config discovery, project status change, path change.

## "Call It a Day" Protocol

**Trigger**: "That's all for now" / "Done for today" / "I'm heading out" / "Going out" / "Talk later" / "Closing window" / "Call it a day"

Three mandatory steps:

1. **Write daily report** to `<RESEARCH>/Daily Report/YYYY-MM-DD Daily Report.md`
   - Consolidate session work into a coherent report
   - Include: what was done, decisions, results/metrics, next steps

2. **Process Inbox** (`<RESEARCH>/Inbox/`)
   - Read every file
   - Add frontmatter (title, date, tags, project)
   - Append `## Claude's Notes` at the bottom
   - Move to correct folder (Projects/{Project}/, PAPER_NOTES/, Notes/)
   - Do NOT modify user's original text

3. **Update long-term memory** if warranted
   - Record new technical lessons or workflow changes in `CLAUDE.md` / `AGENTS.md`
   - Add cross-project patterns to `patterns.md`

## Other Trigger Conditions

- **Key literature finding** -> Record in `patterns.md` or long-term memory (don't wait for exit)
- **Reusable lesson learned** -> Record in `patterns.md` immediately

## Exit Signals (Execute "Call It a Day" immediately)

"That's all for now" / "Done for today" / "I'm heading out" / "Going out" / "Talk later" / "Closing window" / "Call it a day" -> Immediately run the protocol above

Banned: Waiting for manual save / Batching saves / Assuming user will end normally
