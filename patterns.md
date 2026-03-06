# Patterns Library

<!--
  Cross-project reusable patterns discovered through experience.
  Update: When a lesson applies beyond a single project.

  Seed this with your own domain-specific patterns.
  Examples below show the format — replace with your actual lessons.
-->

## LaTeX/Academic Writing Patterns

### Overleaf Git Sync
- **Lesson**: Always `git pull` before editing, `git push` only with user confirmation
- **Risk**: Force push overwrites collaborator changes

### Citation Style
- **Convention**: Use consistent style across all papers (e.g. authoryear with biblatex + biber)
- **Gotcha**: Check `maxcitenames` setting — affects "et al." threshold in text

### temporary.tex Staging
- **Lesson**: Always stage new content in temporary.tex with highlights before merging to main.tex
- **Benefit**: User can audit changes visually, iterate before committing

## Reference Management Patterns

### Source Grounding
- **Lesson**: Reference notebook (NotebookLM) answers are grounded in uploaded sources only
- **Use**: Ideal for verifying claims against specific papers before citing
- **Limit**: Cannot find papers not uploaded to the notebook

<!--
  Add your domain-specific patterns here. Examples:

  ## ML Training Patterns

  ### Learning Rate Scheduling
  - **Lesson**: [what you discovered]
  - **Impact**: [what goes wrong if ignored]
  - **Fix**: [what to do]

  ## Simulation Patterns

  ### Signal Dimension Mismatch
  - **Lesson**: [most common error in your domain]
  - **Check**: [what to verify]
-->
