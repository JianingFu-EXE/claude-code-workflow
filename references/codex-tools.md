# Codex Tool Translation for Shared Claude Docs

Use this file when a shared rule or doc was written for Claude Code and names tools or capabilities that may differ in Codex.

## Principle

Translate by capability, not by exact tool name. Codex surfaces differ across CLI, desktop, and hosted environments.

## Mapping Table

| Claude Code concept | Codex-compatible interpretation | Notes |
|---------------------|---------------------------------|-------|
| `Read` | Inspect files with the available file-reading or shell tools | `sed`, `cat`, `rg`, or file-open tools are all acceptable |
| `Write` / `Edit` | Use the available edit workflow | Prefer patch-style edits when supported |
| `Glob` | Use shell listing tools | Prefer `find`, `ls`, or `rg --files` |
| `Grep` | Use shell search tools | Prefer `rg`; fall back to `grep` |
| `Bash` | Use the terminal / shell tool | Same intent |
| `Agent` / subagent | Use Codex delegation only if this surface supports it | Otherwise do the work serially |
| `Skill` | Use a local skill only if Codex supports skills in this environment | Otherwise read the referenced instructions directly |
| `TaskCreate` / `TaskUpdate` | Use planning tools if present | Otherwise track progress inline |
| `WebFetch` / `WebSearch` | Use Codex web tools if present | Otherwise rely on local sources or ask for the missing artifact |
| MCP server | Use only when this Codex environment exposes that integration | Otherwise skip and note the limitation |

## Translation Rules

- Preserve the intent of the instruction even if the exact tool is different.
- Prefer the simplest native Codex workflow over recreating Claude-specific machinery.
- If a file mentions a slash command, run the underlying steps directly.
- If a file assumes a feature that is unavailable, state that plainly and continue with the nearest safe alternative.
- Do not invent missing capabilities.

## Examples

- "Use `Read` on `rules/behaviors.md`" -> open the file with shell or file tools and read the relevant section.
- "Dispatch a Sonnet subagent" -> if Codex delegation exists, use it; otherwise perform the subtask locally.
- "Use the skill to import papers" -> if no skill layer exists, read the skill instructions or ask the user for the missing manual path.
