# Memory Flush

> Don't rely on user triggers -- auto-save. User might close the window at any time.

## Two Write Targets

1. **User-facing**: Daily report in project workspace (`<PROJ>/{Project}/YYYY-MM-DD Daily Report.md`)
   - The user reads these in Obsidian to track progress
   - Written after non-trivial work on a project
2. **Claude-internal**: `memory/today.md` + `MEMORY.md` + `patterns.md`
   - Claude reads these for session continuity and cross-session learning
   - Updated automatically by the three-layer memory system

## Two Flush Levels

### Level 1: Task Complete (after finishing a piece of work)

**Trigger**: Task/work item finished within the session.

**Action**: Update `memory/today.md` only.
- Append what was done, key decisions, results, blockers
- Keep it as a running log — multiple entries per session are fine
- Do NOT write daily reports or update MEMORY.md yet

### Level 2: Call It a Day (end of session)

**Trigger**: Exit signal from user.

**Action**: Full flush — four steps, all mandatory:

1. **Write daily report** in project workspace (`<PROJ>/{Project}/YYYY-MM-DD Daily Report.md`)
   - Consolidate from today.md entries into a coherent report
   - Include: what was done, decisions, results/metrics, next steps
   - Append if report for today already exists

2. **Update long-term memory** (MEMORY.md / patterns.md)
   - Record new technical lessons, pitfalls, tool configs
   - Update or remove stale entries
   - Add cross-project patterns to `patterns.md`

3. **Process Inbox** (`<RESEARCH>/Inbox/`)
   - Read every file
   - Add frontmatter (title, date, tags, project)
   - Append `## Claude's Notes` at the bottom
   - Move to correct folder (Projects/{Project}/, PAPER_NOTES/, Notes/)
   - Do NOT modify user's original text

4. **Empty today.md** — clear it after daily report is written. It resets for the next session.

## Other Trigger Conditions

- **Non-trivial task starts** -> Write today.md session header: `### SN (~HH:MM) [project] Working on XXX...`
- **Key literature finding** -> Record in MEMORY.md or patterns.md (don't wait for exit)
- **Reusable lesson learned** -> Record in patterns.md immediately

## Exit Signals (Execute Level 2 immediately)

"That's all for now" / "Done for today" / "I'm heading out" / "Going out" / "Talk later" / "Closing window" / "Call it a day" -> Immediately run Level 2

Banned: Waiting for manual save / Batching saves / Assuming user will end normally
