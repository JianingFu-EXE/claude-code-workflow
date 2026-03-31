# Audit Report

Scope: full repo audit against `AUDIT_PROMPT.md`, including Python modules, agent prompts, configs, and tests.

Validation performed:
- Read every tracked source/config/test/agent file in the repo.
- Ran `python tests/test_parser.py` and `python -m compileall orchestrator.py lib tests`.
- Ran targeted repros for the parser, grading, rewrite loop, evidence/report serialization, and type handling.

## Executive Summary

- Total findings: 26
- Severity mix: 2 Critical, 7 High, 12 Medium, 5 Low
- Known-issue verification: 15 confirmed, 4 partially confirmed, 2 refuted
- Additional issues found beyond the prompt: 5

The two release-blocking defects are:
1. The pipeline can report `"Optimal"` even when grading silently failed or produced zero grades.
2. `Abstract` and `Unknown` are valid classifier outputs and IR section types, but they are not supported by the scoring configs.

The highest-leverage structural fix is to make the orchestrator fail closed:
- validate every agent payload against an expected schema
- reject mismatched IDs and unsupported section types
- refuse to generate a success report when expected grades are missing

## Recommended Fix Order

### Phase 1: Stop false-success outputs
1. Fix partial-grading handling so missing grades cannot yield `"Optimal"` (`orchestrator.py`).
2. Resolve the `Abstract` / `Unknown` config mismatch (`lib/ir.py`, `config/*.yaml`, classifier contract).
3. Make empty or malformed score maps non-optimal and schema-invalid (`lib/ir.py`, grader wrappers).

### Phase 2: Stabilize agent integration
4. Add schema validation and ID checks for paragraph/sentence/report/rewrite payloads.
5. Bring agent prompts in sync with the payloads the orchestrator actually sends.
6. Normalize evidence serialization in one place.

### Phase 3: Improve rewrite safety and parser fidelity
7. Add score-gated rewrite acceptance and rejected-rewrite tracking.
8. Implement paragraph-level rewrites or remove the dead paragraph rewrite path.
9. Fix Markdown citations, abstract handling, float skipping, and list-item parsing in `lib/parser.py`.

### Phase 4: Scale and harden
10. Add integration tests and edge-case parser tests.
11. Add skipped-claim reporting and subagent response caching.
12. Parallelize sentence grading at the paragraph level.

## Quick Wins

- Remove unused imports and dead prompt/docs that are not currently invoked.
- Change the plateau guard to `if len(history) <= window:` for readability, even though it is not currently buggy.
- Add a packaging file documenting `pyyaml` and the `claude` CLI requirement.

## Findings

### Issue #1: Plateau detection off-by-one
**Severity**: Low
**File(s)**: `lib/scoring.py:191-217`
**Status**: Refuted
**Evidence**: `len(history) < window + 1` is equivalent to `len(history) <= window`. With `window=2`, `len(history)==2` returns `False` before any negative out-of-range index is used. Repro: `detect_plateau([r0, r1], window=2) -> False`; `detect_plateau([r0, r1, r2], window=2) -> True`.
**Fix**: None required for correctness. Optional clarity patch: change the guard to `if len(history) <= window:` to match the prose and avoid re-raising the same concern.
**Test**: Add `test_detect_plateau_short_history()` asserting `False` for `len(history) < window + 1`.

### Issue #2: LaTeX environment stripping is overbroad and leaves malformed content
**Severity**: Medium
**File(s)**: `lib/parser.py:188-205`
**Status**: Partially confirmed
**Evidence**: The code removes every `\begin{...}` and `\end{...}` token with `re.sub(r"\\(begin|end)\{[^}]+\}", "", raw)`. Equation content survives, but environment-aware parsing does not happen. Repro:
- `equation` becomes plain paragraph text (`E = mc^2`).
- `itemize` leaves raw `\item` markers in sentence text.
- `figure` bodies are not skipped and are parsed as prose.
**Fix**: Replace the blanket environment-token removal with explicit handling:
```python
text = re.sub(r"\\begin\{document\}|\\end\{document\}", "", text)
text = re.sub(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", "", text, flags=re.DOTALL)
text = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", "", text, flags=re.DOTALL)
```
Then parse `itemize`/`enumerate` by splitting on `\item` instead of letting `\item` leak into sentence text.
**Test**: Add LaTeX fixtures covering `equation`, `itemize`, and `figure` environments.

### Issue #3: `is_optimal` is vacuously true for empty score maps
**Severity**: High
**File(s)**: `lib/ir.py:104-123`
**Status**: Confirmed
**Evidence**: `SentenceGrade('s').is_optimal` and `ParagraphGrade('p').is_optimal` both return `True`. That is reachable because `_grade_paragraph()` and `_grade_sentence()` default missing agent output to `scores = {}` (`orchestrator.py:184`, `orchestrator.py:220`).
**Fix**: Fail closed:
```python
EXPECTED_PARAGRAPH = set(PARAGRAPH_CRITERIA)
EXPECTED_SENTENCE = set(SENTENCE_CRITERIA)

return bool(self.scores) and set(self.scores) == EXPECTED_SENTENCE and all(
    isinstance(v, (int, float)) and v >= OPTIMAL_THRESHOLD for v in self.scores.values()
)
```
Do the same for `ParagraphGrade`.
**Test**: Add tests asserting empty scores are not optimal and incomplete score maps are rejected.

### Issue #4: Rewrite loop never backtracks or score-gates rewrites
**Severity**: High
**File(s)**: `orchestrator.py:374-426`
**Status**: Confirmed
**Evidence**: Every rewrite result is appended, `_apply_rewrites()` mutates the IR immediately, and only then is the whole document re-graded. There is no comparison against the pre-rewrite grade for the rewritten sentence.
**Fix**: Change the loop to tentative acceptance:
```python
original = sent.text
candidate = result["rewritten_text"]
sent.text = candidate
new_grade = _grade_sentence(...)
if new_grade.weighted_aggregate >= sg.weighted_aggregate and set(new_grade.below_threshold_criteria) <= set(sg.below_threshold_criteria):
    accept
else:
    sent.text = original
```
Store accepted/rejected rewrites in iteration history.
**Test**: Mock `_rewrite_item()` and `_grade_sentence()` so one rewrite regresses and assert the original text is preserved.

### Issue #5: Evidence normalization in report generation is incomplete
**Severity**: Medium
**File(s)**: `orchestrator.py:479-483`
**Status**: Partially confirmed
**Evidence**: The live pipeline passes `EvidenceEntry` objects from `phase_evidence()`, so mixed evidence types are not produced by `main()`. However, `phase_report()` pretends to support dicts with `hasattr()` checks while still unconditionally reading `v.claim`; passing dict evidence crashes with `AttributeError: 'dict' object has no attribute 'claim'`.
**Fix**: Normalize once:
```python
def _normalize_evidence(v):
    if isinstance(v, EvidenceEntry):
        return {"claim": v.claim, "confidence": v.confidence.value, "supported": v.supported, "note": v.note}
    return {"claim": v.get("claim", ""), "confidence": v.get("confidence", ""), "supported": v.get("supported", False), "note": v.get("note", "")}
```
Use that helper everywhere evidence is serialized.
**Test**: Add a report-generation test for both `EvidenceEntry` and dict inputs.

### Issue #6: Agent-returned grade IDs are never validated against the IR
**Severity**: High
**File(s)**: `orchestrator.py:184-193`, `orchestrator.py:220-230`, `orchestrator.py:367-406`
**Status**: Confirmed
**Evidence**: `_grade_paragraph()` trusts `data.get("paragraph_id", "unknown")`; `_grade_sentence()` trusts `data.get("sentence_id", "unknown")`. The rewrite loop later keys off `sentence_id`/`paragraph_id` maps. Wrong IDs are silently dropped from those maps.
**Fix**: Pass the expected ID into each grader and reject mismatches:
```python
if data.get("sentence_id") != expected_sentence_id:
    raise ValueError(f"grader returned wrong sentence_id: {data.get('sentence_id')} != {expected_sentence_id}")
```
Apply the same to paragraphs.
**Test**: Mock a grader response with a wrong ID and assert the phase raises or records an explicit failure.

### Issue #7: Optimal threshold is duplicated across code and config
**Severity**: Medium
**File(s)**: `lib/ir.py:91`, `config/rubric.yaml:7`, `agents/paragraph_grader_agent.md:121`, `agents/report_agent.md:20`
**Status**: Confirmed
**Evidence**: Threshold `4` appears in Python, YAML, and prompt prose. Changing one location will desynchronize grading, rewrite triggers, and reporting.
**Fix**: Move threshold ownership into one config loader, e.g. `lib/scoring.get_optimal_threshold()`, and interpolate it into prompts rather than hardcoding.
**Test**: Add a config consistency test that asserts the loaded threshold matches every prompt/template placeholder source.

### Issue #8: Global config caches are unsynchronized but not corrupting state
**Severity**: Low
**File(s)**: `lib/scoring.py:34-68`, `orchestrator.py:252-258`
**Status**: Partially confirmed
**Evidence**: Multiple grading threads can race on `_weights_cache is None` / `_rubric_cache is None` and load the same YAML more than once. That wastes I/O but does not appear to corrupt data because assignment is idempotent.
**Fix**: Replace mutable globals with `functools.lru_cache` or guard initialization with a `threading.Lock`.
**Test**: Add a threaded test that calls `get_weights_for_section()` concurrently and asserts stable results.

### Issue #9: Shell injection via `subprocess.run()` in evidence retrieval
**Severity**: Low
**File(s)**: `lib/triple_query.py:147-158`
**Status**: Refuted
**Evidence**: `execute_query()` uses `subprocess.run([...])` with a list of args and does not use `shell=True`, so shell metacharacters in `question` are not evaluated by a shell.
**Fix**: None required for shell injection. Keep the argv list form and avoid moving to `shell=True`.
**Test**: Add a regression test that passes shell metacharacters in a question and asserts they remain literal in the spawned argv.

### Issue #10: File paths are trusted user input
**Severity**: Low
**File(s)**: `lib/parser.py:465-500`, `orchestrator.py:536-543`
**Status**: Partially confirmed
**Evidence**: `parse_file()` and the CLI accept arbitrary readable paths. In the current local-CLI model that is expected behavior, not a sandbox escape, but it should be documented as a trust assumption.
**Fix**: If the tool is ever exposed as a service, resolve paths under an allowed workspace root or require explicit `--allow-outside-workspace`.
**Test**: Add a CLI test that documents current behavior and another for any future workspace restriction.

### Issue #11: XMind parsing is untested
**Severity**: Medium
**File(s)**: `lib/parser.py:311-459`, `tests/test_parser.py:16-74`
**Status**: Confirmed
**Evidence**: No XMind fixture or test exists, despite `_parse_xmind()`, `_walk_xmind_topic()`, and `_collect_sentences()` being the most specialized parser code in the repo.
**Fix**: Add `tests/sample_xmind.source.json` and coverage for:
- section discovery
- direct sentence children
- paragraph-title fallback
- nested subsection recursion
**Test**: The new XMind fixture suite.

### Issue #12: Markdown citations are never extracted
**Severity**: High
**File(s)**: `lib/parser.py:94-107`, `agents/parser_agent.md:80-85`
**Status**: Confirmed
**Evidence**: `_extract_citations()` only matches LaTeX `\cite...{}`. Repro: parsing `This claim is supported [@smith2024] and [@jones2023; @lee2022].` yields `[]`.
**Fix**: Extend extraction with a Markdown pattern:
```python
_MD_CITE_RE = re.compile(r"\[@([^\]]+)\]")
for match in _MD_CITE_RE.finditer(text):
    for key in re.split(r"[;,]", match.group(1)):
        ...
```
Also remove inline markdown citation markup from `Sentence.text` if that is the intended canonical display form.
**Test**: Add Markdown citation tests for single-key and multi-key cites.

### Issue #13: Malformed-input and edge-case parser tests are missing
**Severity**: Medium
**File(s)**: `tests/test_parser.py:16-74`
**Status**: Confirmed
**Evidence**: Current tests cover only happy-path LaTeX/Markdown parsing and serialization.
**Fix**: Add fixtures for:
- empty file
- preamble-only LaTeX
- no headers
- malformed JSON XMind
- deeply nested subsections
**Test**: The edge-case suite itself.

### Issue #14: There is no full-pipeline integration test
**Severity**: Medium
**File(s)**: `orchestrator.py:98-597`, `tests/`
**Status**: Confirmed
**Evidence**: The repo has parser tests only. No test exercises classify -> evidence -> grade -> rewrite -> report interfaces together.
**Fix**: Add a mocked integration test that monkeypatches `_dispatch_claude()` and `execute_query()` to deterministic responses and asserts:
- IDs remain stable
- below-threshold items trigger rewrite attempts
- report status is correct
**Test**: `tests/test_orchestrator_integration.py`.

### Issue #15: Sentence-grader prompt duplicates weight values
**Severity**: Medium
**File(s)**: `agents/sentence_grader_agent.md:54-124`, `config/weights.yaml:6-53`
**Status**: Confirmed
**Evidence**: The prompt hardcodes weights in section headings such as `Background (functional_context 0.35, transition 0.30)`. `weights.yaml` is also authoritative.
**Fix**: Remove the numeric literals from the prompt and replace them with prose such as "use the provided weights to stress these criteria."
**Test**: Add a prompt consistency test that fails if numeric weight literals appear outside generated examples.

### Issue #16: Rubric descriptors are qualitative and hard to score consistently
**Severity**: Medium
**File(s)**: `config/rubric.yaml:11`
**Status**: Confirmed
**Evidence**: Many score bands are relative and subjective (`"one jump feels abrupt"`, `"mostly convincing"`, `"minor gaps"`), which makes reproducibility weak across agent calls.
**Fix**: Add observable anchors per criterion, e.g. citation count ranges, required structural elements, allowed red flags, or explicit pattern counts.
**Test**: Add prompt/fixture-based evals that check score stability for representative paragraphs.

### Issue #17: Agent output parsing is heuristic and unvalidated
**Severity**: High
**File(s)**: `orchestrator.py:62-92`
**Status**: Confirmed
**Evidence**: `_extract_json()` guesses at fenced JSON or the first `{...}` block. There is no schema validation after parse, so malformed-but-JSON agent output can still poison later stages.
**Fix**: Add per-agent validators and retry-on-invalid:
```python
data = _extract_json(raw)
validate_sentence_grade(data)
```
At minimum, assert required keys, score key sets, numeric ranges, and matching IDs.
**Test**: Add parser tests for outputs with preambles, code fences, missing keys, and wrong score types.

### Issue #18: `GradeReport` is dead code
**Severity**: Low
**File(s)**: `lib/ir.py:135-142`, `orchestrator.py:23-26`
**Status**: Confirmed
**Evidence**: `GradeReport` is imported into `orchestrator.py` but never instantiated. `phase_report()` builds a plain dict instead.
**Fix**: Either delete `GradeReport` and its import, or use it as the canonical reporting DTO.
**Test**: None needed if removed. If retained, add a report serialization test.

### Issue #19: Sentence grading is fully sequential
**Severity**: Medium
**File(s)**: `orchestrator.py:268-285`
**Status**: Confirmed
**Evidence**: Paragraph grading uses `ThreadPoolExecutor`; sentence grading nests loops and makes one blocking agent call per sentence.
**Fix**: Parallelize at least at the paragraph level while preserving in-paragraph context. A simple first step is one worker per paragraph with bounded pool size.
**Test**: Add a concurrency test that uses mocked graders and asserts wall-clock reduction with multiple paragraphs.

### Issue #20: Budget exhaustion silently drops lower-priority claims
**Severity**: Medium
**File(s)**: `lib/triple_query.py:333-350`
**Status**: Confirmed
**Evidence**: `verify_claims()` breaks when the budget is exhausted and returns no record of skipped claims. The orchestrator cannot report what was omitted.
**Fix**: Return a richer result:
```python
@dataclass
class VerificationResult:
    evidence_map: dict[str, EvidenceEntry]
    verified_claim_ids: list[str]
    skipped_claim_ids: list[str]
```
**Test**: Add a low-budget test asserting skipped claims are reported.

### Issue #21: There is no caching of repeated subagent calls
**Severity**: Medium
**File(s)**: `orchestrator.py:50-59`, `orchestrator.py:167-230`, `orchestrator.py:294-323`
**Status**: Confirmed
**Evidence**: Re-grading and repeated rewrites call Claude again even if the prompt inputs are unchanged.
**Fix**: Add a content-hash cache keyed by agent name + normalized payload. For rewrites, cache by item text, diagnosis, evidence, and section type.
**Test**: Add a mock call-count test proving unchanged content is not re-sent.

### Issue #22: Paragraph-level rewrites are never attempted
**Severity**: High
**File(s)**: `orchestrator.py:366-406`, `agents/rewriter_agent.md:32-33`
**Status**: Confirmed
**Evidence**: `para_grade_map` is built and then never used for rewrite selection. The loop rewrites only sentences. That makes the L1 paragraph-grading phase advisory only.
**Fix**: Add a paragraph-rewrite branch before or after sentence rewrites, pass paragraph text plus neighboring paragraph context, and teach `_apply_rewrites()` how to replace paragraph bodies safely.
**Test**: Add a test with a below-threshold paragraph and no below-threshold sentences; assert a paragraph rewrite is attempted.

### Issue #23: `Abstract` and `Unknown` section types are ungradable
**Severity**: Critical
**File(s)**: `lib/ir.py:15-25`, `agents/section_classifier_agent.md:19`, `config/weights.yaml:6-53`, `config/rubric.yaml:9`, `orchestrator.py:169-170`, `orchestrator.py:200-201`
**Status**: Confirmed
**Evidence**: `SectionType` and the classifier prompt both include `Abstract`; configs do not. Minimal repro with an `Abstract` paragraph produces:
- warning: no rubric for `Abstract`
- warning: no weight profile for `Abstract`
- `phase_grade()` returns `0 paragraphs, 0 sentences graded`
**Fix**: Either:
- add `Abstract` and `Unknown` entries to `weights.yaml` and `rubric.yaml`, or
- normalize `Abstract -> Background` and reject `Unknown` before grading, or
- treat unclassified paragraphs as a hard failure instead of dropping them.
**Test**: Add grading tests for `Abstract` and `Unknown`.

### Issue #24: Phase failures are silently dropped and can produce false "Optimal" output
**Severity**: Critical
**File(s)**: `orchestrator.py:261-266`, `orchestrator.py:281-285`, `orchestrator.py:487-495`, `orchestrator.py:579-590`
**Status**: Confirmed
**Evidence**: Paragraph and sentence grading catch all exceptions, log warnings, and continue. `phase_report()` computes `below = get_below_threshold(...)`; if the grade lists are empty, `below` is empty and status becomes `"Optimal"`. The `Abstract` repro above demonstrates the pipeline continuing with zero grades.
**Fix**: Track expected item counts and fail closed:
```python
if len(paragraph_grades) != expected_paragraphs or len(sentence_grades) != expected_sentences:
    raise RuntimeError("grading incomplete; refusing to report Optimal")
```
Add a partial-failure status if the product needs resumability.
**Test**: Add a test where one grade call fails and assert report generation aborts or reports `"Partial failure"` rather than `"Optimal"`.

### Issue #25: Most agent prompts do not match the orchestrator payloads they are supposed to describe
**Severity**: High
**File(s)**:
- `agents/paragraph_grader_agent.md:7-27`
- `agents/sentence_grader_agent.md:7-34`
- `agents/rewriter_agent.md:7-22`
- `agents/report_agent.md:7-20`
- `orchestrator.py:172-180`
- `orchestrator.py:206-215`
- `orchestrator.py:304-316`
- `orchestrator.py:497-500`
**Status**: Confirmed
**Evidence**:
- Paragraph grader prompt documents structured JSON fields like `paragraph_id`, `classified_type`, `gold_patterns`; the orchestrator sends free-form markdown plus paragraph JSON, rubric subset, and an evidence dict keyed by sentence ID.
- Sentence grader prompt expects structured `context.prev_sentence`, `position_in_paragraph`, and section label inside the sentence object; the orchestrator sends a plain context string.
- Rewriter prompt expects structured diagnosis objects, context fields, and phrasebank arrays; the orchestrator sends raw strings.
- Report prompt expects `source_file`, `rewrite_history`, `evidence_verification`, and different sentence criterion names (`factual_correctness`, `citation_accuracy`, `technical_quality`); the orchestrator sends none of those.
**Fix**: Make one schema source of truth. The cleanest patch is to define Python payload builders plus validators per agent and update prompt docs to exactly match them.
**Test**: Add a schema snapshot test that asserts prompt examples and payload builders stay in sync.

### Issue #26: Parser implementation does not match documented parser-agent behavior
**Severity**: Medium
**File(s)**: `lib/parser.py:143-177`, `lib/parser.py:180-218`, `agents/parser_agent.md:63-93`
**Status**: Confirmed
**Evidence**:
- The parser-agent doc says abstract text should become an `"Abstract"` section; the Python parser emits `"Preamble"`.
- The doc says `figure`/`table` environments should be skipped; the Python parser includes figure text as prose.
- The doc says `itemize` items should be treated structurally; the Python parser leaves `\item` in sentences.
**Fix**: Align `lib/parser.py` with the documented contract or rewrite the prompt to match the implementation. The better direction is to implement abstract detection, float skipping, and list-item handling in code.
**Test**: Add explicit fixtures for abstract, figure/table, and itemize/enumerate behavior.

## Dependency Audit

- Missing imports: none found. `python -m compileall orchestrator.py lib tests` passes.
- Unused imports found by AST pass:
  - `orchestrator.py`: `GradeReport`, `is_optimal`
  - `lib/triple_query.py`: `field`
- External runtime dependencies:
  - `pyyaml` (`import yaml`)
  - `claude` CLI binary on `PATH`
- Packaging gap: there is no `requirements.txt` or `pyproject.toml`, so the Python dependency (`pyyaml`) and non-Python runtime dependency (`claude`) are undocumented.

## Type Consistency Audit

Trace:
1. `_extract_json()` (`orchestrator.py:62-92`) returns arbitrary Python data with no schema validation.
2. `_grade_paragraph()` and `_grade_sentence()` read `data.get("scores", {})` directly (`orchestrator.py:184`, `orchestrator.py:220`).
3. `ParagraphGrade`/`SentenceGrade` annotations say `dict[str, int]`, but no coercion or validation enforces that.
4. `compute_sentence_aggregate()` accepts floats fine; `compute_paragraph_aggregate()` also accepts floats.
5. `is_optimal()` compares raw values to `OPTIMAL_THRESHOLD`, so strings crash and floats can silently pass.

Observed behavior:
- `ParagraphGrade('p', scores={'flow': 4.5}).is_optimal -> True`
- `SentenceGrade('s', scores={'linguistic_precision': '5'}).is_optimal` raises `TypeError`
- `compute_sentence_aggregate({'a': 1.5, 'b': 2.0}, {'a': 0.5, 'b': 0.5}) -> 1.75`

Conclusion: the effective type is currently "whatever JSON parsed into", not `dict[str, int]`.

Recommended patch:
- Add `validate_score_map(scores, expected_keys)` and call it in both grader wrappers.
- Coerce numeric strings only if that behavior is explicitly desired; otherwise reject.
- Require exact criterion key sets before constructing grade objects.

## Config Consistency Audit

Consistent:
- Paragraph criteria names match across `lib/ir.py`, `config/rubric.yaml`, and the paragraph grading code.
- Sentence criteria names match across `lib/ir.py`, `config/weights.yaml`, `config/rubric.yaml`, and the sentence grading code.

Inconsistent:
- Threshold `4` is duplicated across Python/YAML/prompts.
- `SectionType` includes `Abstract` and `Unknown`; configs do not.
- `agents/report_agent.md` uses different sentence criterion names from the rest of the system.
- `agents/parser_agent.md` promises Markdown `[@key]` citation extraction and abstract handling that `lib/parser.py` does not implement.
- `agents/section_classifier_agent.md` can emit `Abstract`, which the grader configs cannot handle.

## Agent Prompt Audit

| Agent file | Invoked by code | Schema match | Notes |
|---|---|---|---|
| `agents/parser_agent.md` | No | No | The parser agent is documented but never dispatched by `orchestrator.py`. Its documented behavior also exceeds the Python parser's behavior. |
| `agents/section_classifier_agent.md` | Yes | Partial | The full-IR JSON flow matches, but it can emit `Abstract`, which the grading configs cannot score. |
| `agents/evidence_retriever_agent.md` | No | No | Evidence retrieval is implemented directly in `lib/triple_query.py`; this prompt is dead documentation today. |
| `agents/paragraph_grader_agent.md` | Yes | No | The orchestrator sends free-form markdown + embedded JSON, not the structured payload the prompt describes. |
| `agents/sentence_grader_agent.md` | Yes | No | Context and evidence shapes do not match the prompt's declared schema. |
| `agents/rewriter_agent.md` | Yes | No | Diagnosis/context/evidence/phrasebank shapes do not match, and paragraph rewrites are never used. |
| `agents/report_agent.md` | Yes | No | The report payload differs substantially from the documented schema and criterion names. |

## Error Propagation Audit

| Phase | Failure mode | Current behavior | Assessment |
|---|---|---|---|
| Parse | bad path | exits early in `main()` | Acceptable |
| Parse | parser exception / malformed XMind JSON | uncaught, process crashes | Acceptable if CLI-only, but should be user-friendly |
| Classify | invalid JSON or missing keys | falls back to positional classification | Good fallback |
| Classify | `claude` missing / timeout | uncaught exception from `subprocess.run()` | Risky |
| Evidence | Notebook key missing | warns and skips evidence | Acceptable |
| Evidence | Notebook query returns nonzero | warning only; empty/partial output treated as evidence absence | Risky but tolerable if surfaced |
| Grade | any paragraph or sentence grading error | warning only; item dropped | High risk |
| Rewrite | invalid rewrite JSON | warning; rewrite skipped | Acceptable |
| Rewrite | malformed rewrite dict missing keys | uncaught in `_apply_rewrites()` | Risky |
| Rewrite | worse rewrite | accepted anyway | High risk |
| Report | dict evidence instead of objects | crashes with `AttributeError` | Bug |
| Report | empty or partial grades | may report `"Optimal"` | Critical bug |

Conclusion: parsing/classification mostly fail loud enough, but grading/reporting fail open. The pipeline should not emit a success status when expected grades are missing.

## Missing Tests To Add

1. `test_detect_plateau_short_history`
2. `test_is_optimal_empty_scores_false`
3. `test_markdown_citation_extraction`
4. `test_latex_abstract_becomes_abstract_section`
5. `test_latex_figure_environment_skipped`
6. `test_latex_itemize_items_do_not_leak_backslashes`
7. `test_parse_xmind_nested_sections`
8. `test_grade_id_mismatch_rejected`
9. `test_report_rejects_partial_grading`
10. `test_rewrite_rejected_on_score_regression`
11. `test_budget_reports_skipped_claims`
12. `test_agent_output_schema_validation`
13. `test_abstract_section_has_rubric_or_normalization`
14. `test_full_pipeline_with_mocked_agents`

## Architectural Recommendations

1. Replace free-form prompt contracts with typed payload builders and validators in Python.
2. Treat missing grades, unsupported section types, and invalid agent JSON as hard failures or explicit partial-failure states.
3. Make the rewrite loop acceptance-based, not mutation-first, and cache repeated grader calls by normalized content hash.
4. Consolidate configuration ownership: threshold, section types, and criterion names should come from one canonical module.
5. Reduce doc drift by generating agent prompt schema examples from the same dataclasses used in the orchestrator.

## Verification Summary

- Existing tests: `python tests/test_parser.py` -> 5 passed, 0 failed.
- Syntax/import sanity: `python -m compileall orchestrator.py lib tests` -> passed.
- High-confidence confirmed issues: #3, #4, #6, #12, #17, #22, #23, #24, #25, #26.
