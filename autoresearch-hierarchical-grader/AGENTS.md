# Hierarchical Multi-Agent Academic Paper Grader

> Project-specific instructions for AI agents working on this codebase.
> For user identity, research context, and global rules, see `<SHARED>/AGENTS.md` (Codex) or `<SHARED>/CLAUDE.md` (Claude Code), where `<SHARED>` is the parent directory of this project.

---

## What This Project Does

A 5-phase multi-agent pipeline that grades academic papers at two levels (paragraph and sentence), verifies claims against NotebookLM, and iteratively rewrites below-threshold text.

**Pipeline**: Parse -> Classify -> Evidence Retrieval -> Grade (L1 paragraph + L2 sentence) -> Rewrite Loop -> Report

**Entry point**:
```bash
python orchestrator.py --input paper.tex --notebook meta-rl-ftc --output report.md
python orchestrator.py --input paper.tex --skip-evidence --max-iterations 1  # dry run
```

**External dependency**: `claude` CLI must be on PATH (subagents are dispatched via `claude --print -p`).

---

## Architecture

### Key Files

| File | Purpose | LOC |
|------|---------|-----|
| `orchestrator.py` | Main pipeline orchestrator | ~705 |
| `lib/ir.py` | Internal Representation dataclasses (Sentence, Paragraph, Section, IR, grades) | ~196 |
| `lib/parser.py` | 3-format input parser (LaTeX, Markdown, XMind) | ~543 |
| `lib/scoring.py` | Score aggregation, rubric/weight loading, plateau detection | ~291 |
| `lib/triple_query.py` | Evidence verification via NotebookLM triple-query | ~371 |

### Subagent Prompts (agents/)

| Agent | Role |
|-------|------|
| `parser_agent.md` | Fallback parser for ambiguous input |
| `section_classifier_agent.md` | Classifies paragraphs by section type (8 types) |
| `evidence_retriever_agent.md` | Extracts claims for NotebookLM verification |
| `paragraph_grader_agent.md` | Level 1 grading (4 paragraph-level criteria) |
| `sentence_grader_agent.md` | Level 2 grading (4 sentence-level criteria, weighted by section) |
| `rewriter_agent.md` | Improves below-threshold text iteratively |
| `report_agent.md` | Synthesizes final grading report |

### Configuration (config/)

| File | Purpose |
|------|---------|
| `rubric.yaml` | Section-specific grading criteria (8 section types, ~20+ criteria each) |
| `weights.yaml` | Dynamic weight profiles for sentence-level criteria per section type |
| `notebooklm_notebooks.yaml` | NotebookLM notebook URLs/IDs for 3 projects |
| `phrasebank_index.yaml` | Maps section types to phrasebank .md pattern files |

### Reference Materials (reference/)

- `Literature Review Level.md` — Gold-standard paper samples
- `Academic-Phrasebank-MD/` — 37 phrasebank pattern files for linguistic validation

---

## Internal Representation (IR)

Immutable dataclass pipeline:

```
Sentence -> Paragraph -> Section -> IR
                |              |
          SentenceGrade   ParagraphGrade -> IterationRecord
```

**Section types** (enum): Background, Problem, Gap, Methodology, Contribution, Results, Discussion, Conclusion, Abstract, Unknown

**Confidence levels**: HIGH, MEDIUM, LOW, UNVERIFIABLE

**Input formats**: LATEX, MARKDOWN, XMIND

---

## Known Issues (AUDIT_REPORT.md)

**26 issues documented** (2 Critical, 7 High, 12 Medium, 5 Low)

### Critical (release-blocking)

1. **False-success outputs**: Pipeline can report "Optimal" when grading silently failed or produced zero grades
2. **Abstract/Unknown config mismatch**: Valid classifier outputs but not in scoring configs

### Recommended Fix Order

1. **Phase 1**: Stop false-success outputs (fix partial-grading, Abstract/Unknown config, empty score maps)
2. **Phase 2**: Stabilize agent integration (schema validation, ID checks, prompt-payload sync)
3. **Phase 3**: Improve rewrite safety and parser fidelity (score-gated rewrites, citation parsing)
4. **Phase 4**: Scale and harden (integration tests, subagent caching, parallel grading)

Read `AUDIT_REPORT.md` for full details before making changes.

---

## Development Rules

- **Read `AUDIT_REPORT.md` first** before any code changes — understand what's broken and the fix order
- **Agent prompts and orchestrator must stay in sync** — if you change the IR schema or payload format, update both
- **YAML configs are authoritative** — rubric.yaml and weights.yaml define grading behavior; don't hardcode criteria
- **Test after changes**: `python tests/test_parser.py` and `python -m compileall orchestrator.py lib tests`
- **Subagent dispatch**: All subagents are invoked via `claude --print -p` subprocess. Changes to this mechanism affect the entire pipeline.
- **No silent failures**: The core audit finding is that the pipeline swallows errors. Any fix should fail closed, not open.

---

## Quick Reference

```bash
# Run grader
python orchestrator.py --input paper.tex --notebook meta-rl-ftc --output report.md

# Dry run (skip evidence, 1 iteration)
python orchestrator.py --input paper.tex --skip-evidence --max-iterations 1

# Run tests
python tests/test_parser.py
python tests/test_safety.py

# Compile check
python -m compileall orchestrator.py lib tests
```

---

*Last updated: 2026-03-31*
