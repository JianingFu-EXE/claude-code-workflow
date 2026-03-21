# Extended Behaviors

> On-demand loading. Additional behavior rules for specific research scenarios.

## Experiment Logging Protocol

When a training run completes or is analysed:

1. **Record in Obsidian** (project daily report):
   - Date, run name, TensorBoard path
   - Config snapshot (key hyperparams that differ from baseline)
   - Key metrics: final reward, KL divergence, alpha, per-task performance
   - Verdict: success / partial / failed, with reasoning

2. **Update Critical Path** if an issue is resolved:
   - Mark status as closed with commit hash
   - Note any new issues discovered

3. **Update MEMORY.md** if a reusable pattern is discovered:
   - E.g., "TCN receptive field of 31 steps ~= 3.9s is sufficient for fault detection"

## Paper Writing Protocol (XMind-Driven)

**The XMind mind map is the authoritative structural blueprint. All writing follows it.**

### Full pipeline:

1. **Read the XMind structure first** -- this is mandatory, not optional
   - Parse topic hierarchy as section/subsection outline
   - Read topic notes as content specifications for each section
   - Check labels for section role (Framing/Background/Methodology/Closing)
   - Check markers for priority ordering and completion status (`task-done` = skip)
   - Check relationships for cross-references to honour
2. **For each section topic in the XMind**:
   - Use topic notes as the content seed
   - Query NotebookLM for source-grounded supporting content
   - Cross-reference Zotero for proper `\citep{}` / `\citet{}` citations
   - Expand leaf topics into paragraphs
   - If a topic has no notes, draft content but mark with `\first{[TODO: user review]}`
3. **Ground every technical claim** in either:
   - Own simulation results (with run reference)
   - Published literature (with Zotero citation key)
   - NotebookLM-verified source content
4. **Use consistent terminology** from AGENTS.md conventions
5. **Flag gaps**: If a claim needs data you don't have, mark with `\first{[TODO: data needed]}`
6. **After writing**: report which XMind topics were covered and which remain

### When no XMind exists:

Ask the user: "There's no XMind structure for this yet. Should I create one first, or proceed freeform?" Creating the XMind first is the recommended path -- it gives the user control over structure before Claude fills in content.

### Staging via temporary.tex:

All LaTeX output from the paper writing pipeline goes to `temporary.tex`, NOT directly to `main.tex`. See the **Overleaf Staging Rule** below for the full protocol. The pipeline becomes:

1. Read XMind -> Query NotebookLM -> Draft LaTeX
2. Write to `temporary.tex` with `\added{}` highlighting on all new content
3. User audits and iterates
4. Merge to `main.tex` only on explicit approval

### Updating XMind after writing:

If the writing process reveals structural issues (a section needs splitting, reordering, or a new subsection), propose the XMind update to the user rather than silently deviating.

## Literature Review Protocol

1. **Start with NotebookLM** for source-grounded answers from uploaded papers
2. **Use elsevier-zotero-import** for discovering new papers on Scopus/ScienceDirect
3. **Use paper-atlas** for systematic literature mapping (XMind outline -> NotebookLM -> Zotero)
4. **Cross-reference** Zotero collections with NotebookLM notebooks
5. **Never cite a paper you haven't verified** exists in Zotero or NotebookLM

## Mind Map Protocol

Follow the XMind Consistency Rules in `AGENTS.md`:
- Layout: `org.xmind.ui.logic.right` for structure maps
- Priority markers for chapter ordering (1-9)
- Role labels: Framing, Background, Methodology, Closing
- Project labels: Project 1, Project 2, Project 3
- Notes on every chapter-level and section-level topic

## Post-Compression Recovery

After context compression, if current task details are fuzzy:
1. Check today.md for recent progress
2. Check relevant project notes in Obsidian
3. Only re-read full project context if truly needed

---

## Inbox Processing Protocol

**The user writes raw notes in `<RESEARCH>/Inbox/`.** These are quick captures -- no frontmatter, no structure, just ideas.

**Claude's job at end-of-day (or when asked):**
1. Read every file in `Inbox/`
2. For each note:
   a. **Add frontmatter**: title, date, tags (inferred from content), project (if identifiable)
   b. **Add Claude's comments** at the bottom under a `## Claude's Notes` section -- context, related links, important information, connections to ongoing work
   c. **Move to the proper location**:
      - Project-related → `Projects/{Project}/`
      - Literature/paper note → `PAPER_NOTES/`
      - General idea/knowledge → `Notes/` (if mature) or leave in `Projects/`
      - Daily log content → project workspace daily report
3. `Inbox/` should be empty after processing

**Do NOT modify the user's original text.** Only prepend frontmatter and append Claude's section at the bottom.

## Daily Report Format

**After non-trivial work on a project, write a daily report in the project workspace.**

- **Where**: `<PROJ>/{Project}/` as an Obsidian .md file
  - Meta-RL: `<PROJ>/Meta-RL-FTC/Meta-IPC/YYYY-MM-DD Daily Report.md`
  - DSAC: `<PROJ>/DSAC-WWC/YYYY-MM-DD Daily Report.md`
  - Thesis: `<PROJ>/Thesis/YYYY-MM-DD Daily Report.md`
- **When**: After each significant task, experiment analysis, or writing session
- **Format**: Obsidian markdown with frontmatter (date, tags, project)
- **Content**: What was done, key decisions, results/metrics, next steps
- **Append if exists**: If a daily report for today already exists, append a new section

This is how the user tracks progress. Claude also updates `memory/today.md` internally for its own session continuity, but the user-facing record is the daily report in the project workspace.

## Overleaf Staging Rule (Full Procedure)

**Never write new content directly to `main.tex`.** All additions and deletions go through a staging file for user audit.

### Workflow:

1. **Generate `temporary.tex`** in the same Overleaf directory as `main.tex`
   - Copy the full preamble from `main.tex` (everything before `\begin{document}`) so it compiles independently
   - Add `\usepackage{xcolor}` if not already present, and define:
     ```latex
     \newcommand{\added}[1]{\textcolor{blue}{#1}}
     \newcommand{\deleted}[1]{\textcolor{red}{\sout{#1}}}
     ```
   - Add `\usepackage[normalem]{ulem}` for `\sout` if not present
   - Include only the relevant section(s) between `\begin{document}` and `\end{document}`

2. **Highlight changes**:
   - New content: wrapped in `\added{...}` (renders blue)
   - Deleted content: wrapped in `\deleted{...}` (renders red strikethrough)
   - Unchanged context lines: included as-is for readability

3. **Iterative audit loop**:
   - Present `temporary.tex` to the user
   - User reviews and requests changes
   - Claude updates `temporary.tex` accordingly (keeping highlights)
   - Repeat until the user says it's OK

4. **Merge on approval**: When the user explicitly says "OK to push" / "merge it" / "looks good, push":
   - Remove `\added{}`/`\deleted{}` wrappers (keep the blue text, remove the red text)
   - Merge the clean content into `main.tex` at the correct location
   - Delete `temporary.tex`
   - Confirm merge to user; git push only with separate confirmation

**Do NOT skip the staging step.** Even single-sentence additions go through `temporary.tex`.

## Paper Writing Truth Rule (NotebookLM-Grounded)

**All paper/thesis writing MUST be grounded in the project's NotebookLM notebook.**

When writing any paper section or thesis chapter:
1. **Query the project's NotebookLM** for source-grounded content before writing claims
2. **Every technical claim** must trace to either:
   - NotebookLM-verified source (cite the paper from NotebookLM's response)
   - Own simulation results (with specific run reference)
   - Mathematical derivation (shown explicitly)
3. **If NotebookLM cannot verify a claim**: flag it as `[UNVERIFIED: need source]` -- do NOT silently include it
4. **Citation keys** must match Zotero entries -- cross-check after NotebookLM provides the reference

NotebookLM URLs per project (see CLAUDE.md for full list):
- P2 DSAC: `9cfddb8e-...`
- P3 Meta-RL: `a234fe16-...`
- Thesis examples: `27e615ab-...`

## Data Write-back Rules

**When discovering key metrics or results, write back to the right place immediately.**

| Fetch scenario | Write-back target | Fields |
|---------------|-------------------|--------|
| TensorBoard metrics | Project workspace daily report | Epoch, reward, KL, alpha |
| Simulation results | Project workspace daily report | Load reduction %, pitch stats |
| Literature findings | Zotero + NotebookLM | Citations, key claims |
| Reusable technical lesson | `MEMORY.md` (auto memory) | Pattern + context |
| Cross-project pattern | `patterns.md` | Lesson + example |
| Session progress (internal) | `memory/today.md` | What was done, next steps |
