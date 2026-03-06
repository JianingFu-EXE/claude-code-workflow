---
name: session-end
description: Auto wrap-up at end of session. Save progress, update memory, record lessons.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
---

# Session End Protocol

When triggered (exit signal detected or user says done):

## 1. Process TEMPORARY_NOTES inbox
- Read every file in `<RESEARCH>/TEMPORARY_NOTES/`
- For each note:
  - **Prepend frontmatter**: `title`, `date`, `tags` (inferred from content), `project` (if identifiable)
  - **Append `## Claude's Notes`** at the bottom: context, related links to ongoing work, important connections, anything Claude noticed
  - **Move** to the correct folder based on content:
    - Project-related -> `FLEETING NOTES/{Project}/`
    - Literature/paper note -> `PAPER_NOTES/`
    - General knowledge -> `PERMANENT_NOTES/`
    - Daily log -> `DAILY_NOTES/`
  - **Never modify** the user's original text — only add above (frontmatter) and below (Claude's Notes)
- `TEMPORARY_NOTES/` should be empty after processing

## 2. Write project daily reports
- For each project worked on today, write/append a daily report in `<FN>/{Project}/`

## 3. Update today.md
- Append session summary with what was done, key decisions, next steps
- Format: `### SN (~HH:MM) [Project] Description`

## 4. Update MEMORY.md
- Add any new technical pitfalls or patterns discovered
- Update any existing entries that were refined

## 5. Update active-tasks.json
- Mark completed tasks
- Update context/next_action for in-progress tasks
- Add new multi-session tasks if discovered

## 6. Update goals.md
- Check off completed goals
- Add newly discovered goals

## 7. Final Summary
Output to user:
- What was accomplished
- TEMPORARY_NOTES processed: list what was sorted where
- What's pending for next session
- Any blockers or decisions needed
