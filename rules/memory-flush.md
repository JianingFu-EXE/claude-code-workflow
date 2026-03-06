# Memory Flush

> Don't rely on user triggers — auto-save. User might close the window at any time.

## Two Write Targets

1. **User-facing**: Daily report in project workspace (`<FN>/{Project}/YYYY-MM-DD Daily Report.md`)
   - The user reads these in Obsidian to track progress
   - Written after non-trivial work on a project
2. **Claude-internal**: `memory/today.md` + `MEMORY.md` + `patterns.md`
   - Claude reads these for session continuity and cross-session learning
   - Updated automatically by the three-layer memory system

## Trigger Conditions

- **Non-trivial task starts** -> Write today.md session header: `### SN (~HH:MM) [project] Working on XXX...`
- **Task completed on a project** -> Write/append daily report in project workspace + update today.md
- **Experiment result discovered** -> Write to project daily report (primary) + today.md (internal)
- **Code commit** -> Note in today.md
- **Architecture/strategy decision** -> Record in today.md + project daily report
- **Key literature finding** -> Record in MEMORY.md or patterns.md
- **Reusable lesson learned** -> Record in patterns.md (cross-project) or MEMORY.md (project-specific)

## TEMPORARY_NOTES Processing (End-of-Day)

On exit signal or when asked, process `<RESEARCH>/TEMPORARY_NOTES/`:
1. Read every file in the folder
2. Add frontmatter (title, date, tags, project) — inferred from content
3. Append `## Claude's Notes` at the bottom with context, links, related info
4. Move to the correct folder (FLEETING NOTES/{Project}/, PAPER_NOTES/, PERMANENT_NOTES/, DAILY_NOTES/)
5. Do NOT modify the user's original text — only prepend frontmatter and append at the bottom

## Exit Signals (Execute full Flush immediately)

"That's all for now" / "Done for today" / "I'm heading out" / "Going out" / "Talk later" / "Closing window" -> Immediately run session-end

Session-end includes TEMPORARY_NOTES processing.

Banned: Waiting for manual save / Batching saves / Assuming user will end normally
