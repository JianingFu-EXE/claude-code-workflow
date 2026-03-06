# Behaviors Reference

> On-demand loading. Detailed operation guides for specific scenarios.

<!--
  Add domain-specific operation guides here.
  Below are examples for common research tool stacks.
  Replace or extend with your own tools.
-->

## Overleaf/LaTeX Operations

### Thesis Compilation
- Backend: biber (not bibtex) — or your project's backend
- Citation style: authoryear — or your project's style
- Chapter files: `ch1/introduction.tex` through `chN/conclusion.tex`
- Bibliography: `refs.bib`

### Staging (temporary.tex)
- **All new/modified content goes to `temporary.tex`**, never directly to `main.tex`
- `temporary.tex` copies the full preamble from `main.tex` so it compiles independently
- Additions highlighted with `\added{}` (blue), deletions with `\deleted{}` (red strikethrough)
- User audits iteratively until satisfied, then says "merge" / "push to main"
- On merge: strip highlighting commands, apply changes to `main.tex`, delete `temporary.tex`

### Git Sync
- Always pull before editing, push only with user confirmation
- Never force push to shared Overleaf repos

## Obsidian Operations

### Vault Structure
- Project workspaces under `FLEETING NOTES/{Project}/`
- Each workspace contains: research notes, XMind files, daily reports, overleaf subfolder
- `TEMPORARY_NOTES/` is the inbox — processed at end-of-day

### Note Lifecycle
```
TEMPORARY_NOTES/ (raw capture)
  -> FLEETING NOTES/{Project}/ (sorted, structured)
  -> PERMANENT_NOTES/ (mature, reusable)
```

## Reference Manager Operations

<!--
  Example for Zotero:
  - Library ID: [your library ID], type: user
  - Credentials: [path to credentials file]
  - Use import skill for bulk import from academic databases
-->

## Experiment Platform Operations

<!--
  Add guides for your simulation/training tools. Examples:

  ### MATLAB/Simulink
  - Check signal dimensions first (most common error)
  - S-Function interface: inputs are commands, outputs are states
  - Key outputs: [list your important signals]

  ### Python ML Training
  - Config: `config.yaml` in project root
  - Key params: [list important hyperparameters]
  - Common failure modes: device mismatch, data loader issues, gradient issues
-->

## Memory Search — Scope Routing

| Keywords | Search scope |
|----------|-------------|
| Project-specific keywords | Project MEMORY.md |
| Memory / patterns / recall / pitfalls | `memory/` or `patterns.md` |
| Notes / vault content | Obsidian vault |
| Not sure | Start with `memory/`, expand if needed |

### Code/Project Search: Two-stage
1. First locate candidate directories/files
2. Then search within candidates

Banned: Unscoped full-text search across entire project.

---

*Split from rules/behaviors.md for on-demand loading*
