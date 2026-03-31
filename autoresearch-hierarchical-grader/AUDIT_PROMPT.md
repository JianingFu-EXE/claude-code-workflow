# Comprehensive Audit Prompt -- Hierarchical Multi-Agent Academic Paper Grader

> Feed this to Codex (or any code review agent) targeting `/Users/jn/Github/autoresearch-hierarchical-grader/`.

---

## System Under Audit

A 5-phase multi-agent pipeline that grades academic papers at paragraph (L1) and sentence (L2) levels, verifies claims against NotebookLM, rewrites below-threshold text, and iterates until convergence.

**Pipeline**: Parse → Classify → Evidence Retrieval → Grade (L1+L2) → Rewrite Loop → Report

**Files** (19 source files, ~3200 LOC):
- `orchestrator.py` -- main entry point, dispatches Claude Code subagents via subprocess
- `lib/ir.py` -- IR dataclasses (Sentence, Paragraph, Section, IR, grades, enums)
- `lib/parser.py` -- 3-format parser (LaTeX, Markdown, XMind .source.json)
- `lib/scoring.py` -- score aggregation, config loading, plateau detection, phrasebank loading
- `lib/triple_query.py` -- triple-query evidence retrieval against NotebookLM
- `agents/*.md` -- 7 subagent prompt files (parser, classifier, evidence, L1 grader, L2 grader, rewriter, report)
- `config/*.yaml` -- rubric (400 lines, 8 section types), weights, phrasebank index, notebook URLs
- `tests/` -- 3 test files (parser unit tests + 2 sample fixtures)

---

## Audit Scope

Evaluate every file for correctness, robustness, consistency, security, and extensibility. The audit should produce:

1. **A categorized issue list** (Critical / High / Medium / Low) with file:line references
2. **Concrete fix proposals** for each issue (code patches, not vague suggestions)
3. **Missing test cases** that should be added
4. **Architectural recommendations** for the next iteration

---

## Known Issues to Verify and Expand

The following issues have been identified during initial review. **Verify each one, confirm or refute with evidence, and identify any additional issues in the same area.**

### A. Correctness Bugs

1. **Plateau detection off-by-one** (`lib/scoring.py` ~L209)
   - `detect_plateau()` checks `len(history) < window + 1` but should check `<= window`
   - With `window=2` and `len(history)==2`, accessing `history[-(window+1)]` = `history[-3]` raises IndexError
   - Verify: trace the exact index arithmetic and confirm whether this crashes

2. **LaTeX environment stripping overbroad** (`lib/parser.py` ~L193)
   - `re.sub(r"\\(begin|end)\{[^}]+\}", "", raw)` removes ALL `\begin{}`/`\end{}` including `\begin{equation}`, `\begin{itemize}`, etc.
   - This strips valid content markers. Should it only strip `\begin{document}`/`\end{document}`?
   - Verify: parse a LaTeX file with equations and itemize blocks -- does content survive?

3. **SentenceGrade.is_optimal vacuously true on empty scores** (`lib/ir.py` ~L107)
   - `all(v >= 4 for v in {}.values())` returns True
   - A grade with no scores would incorrectly be considered Optimal
   - Verify: can empty scores reach `is_optimal`? Trace from orchestrator.py grading phases.

4. **Rewrite loop never backtracks** (`orchestrator.py` ~L370-430)
   - If a rewrite makes a sentence worse, the loop applies it anyway and moves on
   - Only plateau detection (2 consecutive no-improvement rounds) stops the loop
   - A single bad rewrite can poison the IR permanently
   - Propose: score-gated acceptance (only apply rewrite if re-graded score improves)

### B. Data Flow Inconsistencies

5. **Evidence object mixed types in report generation** (`orchestrator.py` ~L480-483)
   - Evidence is attached to IR sentences as `EvidenceEntry` objects (L156-159)
   - But `phase_report()` builds `evidence_summary` by calling `.claim`, `.confidence.value` on objects that may be plain dicts
   - The `hasattr()` checks (L480-483) are a code smell -- evidence should be normalized to one type
   - Verify: trace the evidence_map lifecycle from `phase_evidence()` through `phase_report()`

6. **Grade IDs never validated against IR** (`orchestrator.py`)
   - `_grade_paragraph()` returns a `ParagraphGrade` with `paragraph_id` set from the agent's JSON output
   - If the agent returns a wrong ID, the lookup maps (`sent_grade_map`, `para_grade_map`) silently lose data
   - Verify: does any code path validate that returned grade IDs match the IR?

7. **Rubric threshold duplicated** (`lib/ir.py` L91 + `config/rubric.yaml` L7)
   - `OPTIMAL_THRESHOLD = 4` hardcoded in ir.py
   - `threshold: 4` in rubric.yaml
   - If someone changes one without the other, grading and reporting disagree
   - Propose: single source of truth (load from YAML, or remove YAML duplicate)

### C. Thread Safety

8. **Global mutable caches in scoring.py** (~L35-37)
   - `_weights_cache`, `_rubric_cache`, `_phrasebank_index_cache` are module-level globals
   - `orchestrator.py` uses `ThreadPoolExecutor(max_workers=3)` for parallel paragraph grading
   - Multiple threads call `get_weights_for_section()` / `get_rubric_for_section()` concurrently
   - Verify: is there a race condition? Can two threads both see `_weights_cache is None` and both load?
   - Note: Python GIL makes this unlikely for pure Python dict assignment, but verify the `_load_yaml` path

### D. Security

9. **Shell injection via subprocess** (`lib/triple_query.py` ~L153-158)
   - `execute_query()` passes user-provided `question` text into a `subprocess.run()` call
   - If question contains shell metacharacters and subprocess uses `shell=True`, this is exploitable
   - Verify: does the current code use `shell=True` or a list of args? If list, is it safe?

10. **No input validation on file paths** (`lib/parser.py`, `orchestrator.py`)
    - `parse_file()` opens whatever path is given without sanitization
    - Could read arbitrary files if path comes from user input
    - Assess: is this a concern given the CLI-only usage pattern?

### E. Missing Features / Test Coverage

11. **No XMind parsing tests** (`tests/test_parser.py`)
    - XMind parser (`_parse_xmind`, `_walk_xmind_topic`, `_collect_sentences`) is untested
    - This is the most complex parser (recursive tree walker, 3 naming conventions)
    - Propose: create a `tests/sample_xmind.source.json` fixture and add tests

12. **No Markdown citation extraction** (`lib/parser.py`)
    - `agents/parser_agent.md` mentions `[@key]` citation format
    - `_extract_citations()` only handles LaTeX `\cite{}` commands
    - Markdown files will have zero citations extracted, breaking citation density scoring
    - Propose: add `[@key]` regex to `_extract_citations()`

13. **No malformed input tests**
    - What happens with: empty file, file with only preamble, file with no sections, file with 1000 nested subsections?
    - Propose: add edge case tests for each parser

14. **No integration test for full pipeline**
    - Current tests only cover parsing
    - No test that exercises classify → grade → rewrite → report flow
    - Even a mock-based integration test would catch interface mismatches

### F. Agent Prompt Quality

15. **Weights documented in two places**
    - `agents/sentence_grader_agent.md` embeds weight values inline
    - `config/weights.yaml` is the authoritative source
    - If weights.yaml changes, the agent prompt becomes stale
    - Propose: agent prompt should say "use the weights provided in the input" not hardcode them

16. **Rubric score descriptors are qualitative** (`config/rubric.yaml`)
    - Score 5: "Perfect funnel: broad domain → quantified trend → specific technology"
    - Score 3: "Progression visible but one jump feels abrupt"
    - An LLM grader will interpret these subjectively -- scores may not be reproducible
    - Assess: should rubric include concrete, countable criteria? (e.g., "3+ domain applications listed = score 5")

17. **Agent output format fragility**
    - All 7 agents are told "Return JSON only" but nothing prevents them from adding explanatory text
    - `_extract_json()` has fallbacks but they're heuristic
    - Propose: structured output mode or JSON schema enforcement

### G. Architecture / Design

18. **`GradeReport` class is dead code** (`lib/ir.py` ~L136)
    - Defined but never instantiated anywhere
    - Report generation in `phase_report()` builds a plain dict instead
    - Propose: either use it or remove it

19. **No backpressure on sentence grading** (`orchestrator.py` ~L265-285)
    - Paragraph grading is parallel (ThreadPoolExecutor), but sentence grading is fully sequential
    - A document with 200 sentences means 200 sequential Claude CLI calls (~120s each max = 6.7 hours worst case)
    - Propose: batch sentences by paragraph and parallelize across paragraphs

20. **Claim priority sorting may skip important claims** (`lib/triple_query.py` ~L335-348)
    - Claims sorted by priority, processed until budget exhausted, rest silently dropped
    - No feedback to orchestrator about which claims were verified vs. skipped
    - Propose: return a `VerificationResult` with both verified and skipped claim lists

21. **No caching of Claude subagent responses**
    - Same paragraph graded multiple times across rewrite iterations (initial + N rewrites)
    - Each grading call makes a fresh Claude CLI call
    - Propose: cache grades by content hash; only re-grade if text actually changed

---

## Audit Deliverables

For each issue above (and any new ones discovered):

```markdown
### Issue #{N}: {Title}
**Severity**: Critical | High | Medium | Low
**File(s)**: {file:line}
**Status**: Confirmed | Refuted | Partially confirmed
**Evidence**: {trace, test result, or code excerpt}
**Fix**: {concrete code patch or design change}
**Test**: {test case to prevent regression}
```

Additionally provide:

1. **Dependency audit**: Are there missing `import` statements? Unused imports? Missing pip dependencies beyond `pyyaml`?
2. **Type consistency audit**: Trace the `scores` dict from agent JSON output → `_extract_json()` → `ParagraphGrade`/`SentenceGrade` → `compute_*_aggregate()` → `is_optimal()`. Are the types always `dict[str, int]` as expected, or could they be `dict[str, float]` or `dict[str, str]`?
3. **Config consistency audit**: For each value that appears in multiple files (threshold, weights, section types, criteria names), list all locations and flag any mismatches.
4. **Agent prompt audit**: For each agent `.md` file, verify that the input schema described matches what `orchestrator.py` actually sends, and the output schema matches what `orchestrator.py` expects to parse.
5. **Error propagation audit**: Starting from `main()`, trace what happens when each phase fails. Does the pipeline crash, silently continue, or produce a partial result? Which failure modes are acceptable?

---

## How to Run

```bash
cd /Users/jn/Github/autoresearch-hierarchical-grader

# Run existing tests
python tests/test_parser.py

# Verify scoring module
python -c "from lib.scoring import get_weights_for_section; print(get_weights_for_section('Background'))"

# Dry-run orchestrator (parse + classify only, no Claude calls)
python -c "
from orchestrator import phase_parse, _positional_classify_fallback
ir = phase_parse('tests/sample_background.tex')
ir = _positional_classify_fallback(ir)
print(f'{len(ir.sections)} sections parsed')
"
```
