# Extended Behaviors

> On-demand loading. Additional behavior rules for specific research scenarios.

## Experiment Logging Protocol

When a training run completes or is analysed:

1. **Record in Obsidian** (project daily report):
   - Date, run name, log path
   - Config snapshot (key hyperparams that differ from baseline)
   - Key metrics: final performance, loss curves, per-condition results
   - Verdict: success / partial / failed, with reasoning

2. **Update Critical Path** if an issue is resolved:
   - Mark status as closed with commit hash
   - Note any new issues discovered

3. **Update MEMORY.md** if a reusable pattern is discovered

## Paper Writing Protocol (XMind-Driven)

**The XMind mind map is the authoritative structural blueprint. All writing follows it.**

### Full pipeline:

1. **Read the XMind structure first** — this is mandatory, not optional
   - Parse topic hierarchy as section/subsection outline
   - Read topic notes as content specifications for each section
   - Check labels for section role (Framing/Background/Methodology/Closing)
   - Check markers for priority ordering and completion status (`task-done` = skip)
   - Check relationships for cross-references to honour
2. **For each section topic in the XMind**:
   - Use topic notes as the content seed
   - Query reference notebook for source-grounded supporting content
   - Cross-reference manager for proper citations
   - Expand leaf topics into paragraphs
   - If a topic has no notes, draft content but mark with `[TODO: user review]`
3. **Ground every technical claim** in either:
   - Own experiment results (with run reference)
   - Published literature (with citation key)
   - Reference-notebook-verified source content
4. **Use consistent terminology** from project conventions
5. **Flag gaps**: If a claim needs data you don't have, mark with `[TODO: data needed]`
6. **After writing**: report which XMind topics were covered and which remain

### Staging via temporary.tex:

All LaTeX output from the paper writing pipeline goes to `temporary.tex`, NOT directly to `main.tex`. See the **Overleaf Staging Rule** in `rules/behaviors.md` for the full protocol. The pipeline becomes:

1. Read XMind -> Query reference notebook -> Draft LaTeX
2. Write to `temporary.tex` with `\added{}` highlighting on all new content
3. User audits and iterates
4. Merge to `main.tex` only on explicit approval

### When no XMind exists:

Ask the user: "There's no XMind structure for this yet. Should I create one first, or proceed freeform?" Creating the XMind first is the recommended path — it gives the user control over structure before Claude fills in content.

### Updating XMind after writing:

If the writing process reveals structural issues (a section needs splitting, reordering, or a new subsection), propose the XMind update to the user rather than silently deviating.

## Literature Review Protocol

1. **Start with reference notebook** (e.g. NotebookLM) for source-grounded answers from uploaded papers
2. **Use reference import skills** for discovering new papers (e.g. Scopus/ScienceDirect search)
3. **Use paper-atlas** for systematic literature mapping (XMind outline -> reference notebook -> citation manager)
4. **Cross-reference** citation collections with reference notebook
5. **Never cite a paper you haven't verified** exists in your reference manager or notebook

## Mind Map Protocol

Follow XMind Consistency Rules:
- Layout: `org.xmind.ui.logic.right` for structure maps
- Priority markers for chapter ordering (1-9)
- Role labels: Framing, Background, Methodology, Closing
- Project labels: Project 1, Project 2, Project 3 (for thesis chapters spanning projects)
- Notes on every chapter-level and section-level topic

## Post-Compression Recovery

After context compression, if current task details are fuzzy:
1. Check today.md for recent progress
2. Check relevant project notes in Obsidian
3. Only re-read full project context if truly needed
