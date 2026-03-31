#!/usr/bin/env python3
"""Hierarchical Multi-Agent Academic Paper Grader -- Orchestrator.

Drives the full pipeline:
  Parse → Classify → Evidence Retrieval → Grade → Rewrite → Report

Usage:
    python orchestrator.py --input paper.tex --notebook meta-rl-ftc --output report.md
    python orchestrator.py --input paper.tex --skip-evidence --max-iterations 1  # dry run
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from lib.ir import (
    IR, IterationRecord, ParagraphGrade, SentenceGrade,
    SectionType, to_json, ir_from_dict, OPTIMAL_THRESHOLD,
    PARAGRAPH_CRITERIA, SENTENCE_CRITERIA,
)
from lib.parser import parse_file
from lib.scoring import (
    compute_paragraph_aggregate, compute_sentence_aggregate,
    get_weights_for_section, get_rubric_for_section,
    detect_plateau, get_below_threshold, load_phrasebank_patterns,
)
from lib.triple_query import verify_claims, QueryBudget, VerificationResult

PROJECT_ROOT = Path(__file__).resolve().parent
AGENTS_DIR = PROJECT_ROOT / "agents"
DEFAULT_MAX_ITERATIONS = 10  # iterate until Optimal or plateau
MAX_WORKERS = 3  # parallel paragraph grading threads


# ── Subagent Dispatch ────────────────────────────────────────────────


def _load_agent_prompt(agent_name: str) -> str:
    """Load an agent prompt file from agents/ directory."""
    path = AGENTS_DIR / f"{agent_name}.md"
    return path.read_text(encoding="utf-8")


def _dispatch_claude(prompt: str, model: str = "sonnet") -> str:
    """Dispatch a Claude Code subagent with --print (pure reasoning, no tools)."""
    result = subprocess.run(
        ["claude", "--print", "--model", model, "-p", prompt],
        capture_output=True, text=True, timeout=120,
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        print(f"[WARN] Subagent returned non-zero: {result.stderr[:200]}", file=sys.stderr)
    return result.stdout.strip()


def _extract_json(text: str) -> dict:
    """Extract JSON from agent output (handles markdown code fences)."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from code fence
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Last resort: find first { ... } block
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    start = None
    raise ValueError(f"Could not extract JSON from agent output:\n{text[:300]}")


def _normalize_section_type_for_grading(section_type: SectionType | str) -> str:
    """Map classifier output onto section types supported by the scoring config."""
    raw = section_type.value if isinstance(section_type, SectionType) else str(section_type)
    if raw == SectionType.ABSTRACT.value:
        return SectionType.BACKGROUND.value
    if raw == SectionType.UNKNOWN.value:
        raise ValueError("Cannot grade paragraphs with classified_type=Unknown")
    return raw


def _validate_score_map(scores: dict, expected_keys: tuple[str, ...], label: str) -> dict[str, int | float]:
    """Ensure a score map has the exact expected keys and numeric 0-5 values."""
    if not isinstance(scores, dict):
        raise ValueError(f"{label} scores must be a dict, got {type(scores).__name__}")
    if set(scores.keys()) != set(expected_keys):
        raise ValueError(
            f"{label} scores must contain exactly {list(expected_keys)}, got {sorted(scores.keys())}"
        )
    validated = {}
    for key, value in scores.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{label} score '{key}' must be numeric, got {type(value).__name__}")
        if not 0 <= value <= 5:
            raise ValueError(f"{label} score '{key}' must be between 0 and 5, got {value}")
        validated[key] = value
    return validated


def _count_expected_items(ir: IR) -> tuple[int, int]:
    """Return expected paragraph and sentence counts for the IR."""
    paragraph_count = sum(len(section.paragraphs) for section in ir.sections)
    sentence_count = sum(
        len(paragraph.sentences)
        for section in ir.sections
        for paragraph in section.paragraphs
    )
    return paragraph_count, sentence_count


def _ensure_complete_grading(
    ir: IR,
    paragraph_grades: list[ParagraphGrade],
    sentence_grades: list[SentenceGrade],
) -> None:
    """Raise if grading output does not fully cover the IR."""
    expected_paragraphs, expected_sentences = _count_expected_items(ir)
    if len(paragraph_grades) != expected_paragraphs or len(sentence_grades) != expected_sentences:
        raise RuntimeError(
            "Grading incomplete: "
            f"expected {expected_paragraphs} paragraphs/{expected_sentences} sentences, "
            f"got {len(paragraph_grades)} paragraphs/{len(sentence_grades)} sentences"
        )


def _normalize_evidence_summary_entry(value) -> dict:
    """Convert an evidence object or dict into a consistent report shape."""
    if isinstance(value, dict):
        return {
            "claim": value.get("claim", ""),
            "confidence": value.get("confidence", ""),
            "supported": value.get("supported", False),
            "note": value.get("note", ""),
        }
    confidence = getattr(value, "confidence", "")
    return {
        "claim": getattr(value, "claim", ""),
        "confidence": confidence.value if hasattr(confidence, "value") else confidence,
        "supported": getattr(value, "supported", False),
        "note": getattr(value, "note", ""),
    }


def _should_accept_sentence_rewrite(
    previous_grade: SentenceGrade,
    candidate_grade: SentenceGrade,
) -> bool:
    """Accept only rewrites that improve the sentence or reduce failing criteria."""
    if len(candidate_grade.below_threshold_criteria) < len(previous_grade.below_threshold_criteria):
        return True
    return candidate_grade.weighted_aggregate > previous_grade.weighted_aggregate


# ── Phase 1: Parse & Classify ───────────────────────────────────────


def phase_parse(input_path: str) -> IR:
    """Parse input file into IR."""
    print(f"[Phase 1] Parsing {input_path}...")
    ir = parse_file(input_path)
    print(f"  → {len(ir.sections)} sections, "
          f"{sum(len(p.sentences) for s in ir.sections for p in s.paragraphs)} sentences")
    return ir


def phase_classify(ir: IR) -> IR:
    """Classify each paragraph's section type using the classifier agent."""
    print("[Phase 1] Classifying paragraphs...")
    prompt_template = _load_agent_prompt("section_classifier_agent")
    ir_json = to_json(ir)

    prompt = f"{prompt_template}\n\n## Input IR\n\n```json\n{ir_json}\n```\n\nClassify each paragraph and return the full IR JSON with classified_type populated."
    raw = _dispatch_claude(prompt)

    try:
        classified = _extract_json(raw)
        ir = ir_from_dict(classified)
    except (ValueError, KeyError) as e:
        print(f"  [WARN] Classification failed ({e}), using positional fallback", file=sys.stderr)
        ir = _positional_classify_fallback(ir)

    classified_count = sum(
        1 for s in ir.sections for p in s.paragraphs
        if p.classified_type != SectionType.UNKNOWN
    )
    print(f"  → {classified_count} paragraphs classified")
    return ir


def _positional_classify_fallback(ir: IR) -> IR:
    """Simple positional fallback: first section = Background, etc."""
    type_order = [
        SectionType.BACKGROUND, SectionType.PROBLEM, SectionType.GAP,
        SectionType.METHODOLOGY, SectionType.CONTRIBUTION,
        SectionType.RESULTS, SectionType.DISCUSSION, SectionType.CONCLUSION,
    ]
    for i, section in enumerate(ir.sections):
        section_type = type_order[min(i, len(type_order) - 1)]
        for para in section.paragraphs:
            para.classified_type = section_type
    return ir


# ── Phase 2: Evidence Retrieval ──────────────────────────────────────


def phase_evidence(ir: IR, notebook_url: str, budget: QueryBudget) -> VerificationResult:
    """Run triple-query evidence retrieval for claims in the IR."""
    print(f"[Phase 2] Retrieving evidence (budget: {budget.remaining} queries)...")
    result = verify_claims(ir, notebook_url, budget)
    print(
        f"  → {result.verified_count}/{result.total_claims} claims verified, "
        f"{result.skipped_count} skipped, {budget.remaining} queries remaining"
    )
    if result.skipped_claims:
        skipped_types = [c.claim_type.name for c in result.skipped_claims]
        print(f"  [WARN] Skipped claims by type: {skipped_types}", file=sys.stderr)

    # Attach evidence to IR sentences
    for section in ir.sections:
        for para in section.paragraphs:
            for sent in para.sentences:
                if sent.id in result.evidence_map:
                    sent.evidence = result.evidence_map[sent.id]

    return result


# ── Phase 3: Grading ────────────────────────────────────────────────


def _grade_paragraph(
    para_json: str,
    section_type: str,
    evidence_entries: dict,
    expected_paragraph_id: str,
) -> ParagraphGrade:
    """Grade a single paragraph via the paragraph grader agent."""
    rubric = get_rubric_for_section(section_type)
    prompt_template = _load_agent_prompt("paragraph_grader_agent")

    prompt = (
        f"{prompt_template}\n\n"
        f"## Input\n\n"
        f"**Section type**: {section_type}\n\n"
        f"**Paragraph**:\n```json\n{para_json}\n```\n\n"
        f"**Rubric**:\n```json\n{json.dumps(rubric.get('paragraph_criteria', {}), indent=2)}\n```\n\n"
        f"**Evidence**:\n```json\n{json.dumps(evidence_entries, indent=2)}\n```\n\n"
        f"Grade this paragraph. Return JSON only."
    )
    raw = _dispatch_claude(prompt)
    data = _extract_json(raw)

    paragraph_id = data.get("paragraph_id")
    if paragraph_id != expected_paragraph_id:
        raise ValueError(
            f"Paragraph grader returned paragraph_id={paragraph_id!r}, expected {expected_paragraph_id!r}"
        )
    scores = _validate_score_map(
        data.get("scores", {}),
        PARAGRAPH_CRITERIA,
        f"paragraph {expected_paragraph_id}",
    )
    return ParagraphGrade(
        paragraph_id=expected_paragraph_id,
        scores=scores,
        aggregate=data.get("aggregate", compute_paragraph_aggregate(scores)),
        diagnosis=data.get("diagnosis", ""),
        below_threshold=data.get("below_threshold", [
            k for k, v in scores.items() if v < OPTIMAL_THRESHOLD
        ]),
    )


def _grade_sentence(
    sent_json: str, section_type: str, context: str, evidence_json: str,
    expected_sentence_id: str,
) -> SentenceGrade:
    """Grade a single sentence via the sentence grader agent."""
    weights = get_weights_for_section(section_type)
    phrasebank = load_phrasebank_patterns(section_type)
    # Truncate phrasebank to avoid prompt overflow
    phrasebank_excerpt = phrasebank[:3000] if len(phrasebank) > 3000 else phrasebank

    prompt_template = _load_agent_prompt("sentence_grader_agent")
    prompt = (
        f"{prompt_template}\n\n"
        f"## Input\n\n"
        f"**Section type**: {section_type}\n"
        f"**Weights**: {json.dumps(weights)}\n\n"
        f"**Sentence**:\n```json\n{sent_json}\n```\n\n"
        f"**Context** (prev/next sentences):\n{context}\n\n"
        f"**Evidence**:\n```json\n{evidence_json}\n```\n\n"
        f"**Phrasebank patterns**:\n{phrasebank_excerpt}\n\n"
        f"Grade this sentence. Return JSON only."
    )
    raw = _dispatch_claude(prompt)
    data = _extract_json(raw)

    sentence_id = data.get("sentence_id")
    if sentence_id != expected_sentence_id:
        raise ValueError(
            f"Sentence grader returned sentence_id={sentence_id!r}, expected {expected_sentence_id!r}"
        )
    scores = _validate_score_map(
        data.get("scores", {}),
        SENTENCE_CRITERIA,
        f"sentence {expected_sentence_id}",
    )
    return SentenceGrade(
        sentence_id=expected_sentence_id,
        scores=scores,
        weights_used=weights,
        weighted_aggregate=data.get("weighted_aggregate",
                                    compute_sentence_aggregate(scores, weights)),
        diagnosis=data.get("diagnosis", ""),
        suggestions=data.get("suggestions", []),
        phrasebank_matches=data.get("phrasebank_matches", []),
    )


def phase_grade(ir: IR) -> tuple[list[ParagraphGrade], list[SentenceGrade]]:
    """Grade all paragraphs (L1) and sentences (L2)."""
    print("[Phase 3] Grading...")
    paragraph_grades: list[ParagraphGrade] = []
    sentence_grades: list[SentenceGrade] = []

    # Collect grading tasks
    para_tasks = []
    for section in ir.sections:
        for para in section.paragraphs:
            section_type = _normalize_section_type_for_grading(para.classified_type)
            para_json = to_json(para)
            evidence_entries = {
                s.id: {"claim": s.evidence.claim, "confidence": s.evidence.confidence.value,
                       "supported": s.evidence.supported}
                for s in para.sentences if s.evidence
            }
            para_tasks.append((para, para_json, section_type, evidence_entries))

    # Grade paragraphs in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(
                _grade_paragraph, para_json, section_type, evidence_entries, para.id
            ): para.id
            for para, para_json, section_type, evidence_entries in para_tasks
        }
        for future in as_completed(futures):
            grade = future.result()
            paragraph_grades.append(grade)

    # Grade sentences sequentially within each paragraph (need positional context)
    for section in ir.sections:
        for para in section.paragraphs:
            section_type = _normalize_section_type_for_grading(para.classified_type)
            for i, sent in enumerate(para.sentences):
                prev_text = para.sentences[i - 1].text if i > 0 else "(start of paragraph)"
                next_text = para.sentences[i + 1].text if i < len(para.sentences) - 1 else "(end of paragraph)"
                context = f"Previous: {prev_text}\nNext: {next_text}"
                sent_json = to_json(sent)
                ev_json = json.dumps(
                    {"claim": sent.evidence.claim, "confidence": sent.evidence.confidence.value,
                     "supported": sent.evidence.supported} if sent.evidence else {}
                )
                grade = _grade_sentence(sent_json, section_type, context, ev_json, sent.id)
                sentence_grades.append(grade)

    _ensure_complete_grading(ir, paragraph_grades, sentence_grades)
    print(f"  → {len(paragraph_grades)} paragraphs, {len(sentence_grades)} sentences graded")
    return paragraph_grades, sentence_grades


# ── Phase 4: Rewrite Loop ───────────────────────────────────────────


def _rewrite_item(
    item_id: str, item_text: str, level: str, diagnosis: str,
    section_type: str, context: str, evidence_json: str,
) -> dict | None:
    """Dispatch rewriter agent for a single below-threshold item."""
    rubric = get_rubric_for_section(section_type)
    phrasebank = load_phrasebank_patterns(section_type)
    phrasebank_excerpt = phrasebank[:2000] if len(phrasebank) > 2000 else phrasebank

    prompt_template = _load_agent_prompt("rewriter_agent")
    prompt = (
        f"{prompt_template}\n\n"
        f"## Input\n\n"
        f"**Item ID**: {item_id}\n"
        f"**Level**: {level}\n"
        f"**Section type**: {section_type}\n\n"
        f"**Original text**:\n{item_text}\n\n"
        f"**Diagnosis**:\n{diagnosis}\n\n"
        f"**Context**:\n{context}\n\n"
        f"**Evidence**:\n```json\n{evidence_json}\n```\n\n"
        f"**Gold-standard patterns** (rubric):\n```json\n{json.dumps(rubric, indent=2)[:2000]}\n```\n\n"
        f"**Phrasebank suggestions**:\n{phrasebank_excerpt}\n\n"
        f"Rewrite to fix the identified deficiencies. Return JSON only."
    )
    raw = _dispatch_claude(prompt)
    try:
        return _extract_json(raw)
    except ValueError as e:
        print(f"  [WARN] Rewrite failed for {item_id}: {e}", file=sys.stderr)
        return None


def phase_rewrite_loop(
    ir: IR,
    paragraph_grades: list[ParagraphGrade],
    sentence_grades: list[SentenceGrade],
    max_iterations: int,
    verbose: bool = False,
) -> tuple[IR, list[ParagraphGrade], list[SentenceGrade], list[IterationRecord]]:
    """Iterate: rewrite below-threshold items, re-grade, until Optimal or plateau."""
    print("[Phase 4] Entering rewrite loop...")
    history: list[IterationRecord] = []

    # Record initial state
    below = get_below_threshold(paragraph_grades, sentence_grades)
    avg_p = (sum(g.aggregate for g in paragraph_grades) / len(paragraph_grades)
             if paragraph_grades else 0)
    avg_s = (sum(g.weighted_aggregate for g in sentence_grades) / len(sentence_grades)
             if sentence_grades else 0)
    history.append(IterationRecord(
        iteration=0, items_below_threshold=len(below),
        avg_paragraph_score=round(avg_p, 2), avg_sentence_score=round(avg_s, 2),
        rewrites_applied=0,
    ))
    print(f"  Iteration 0: {len(below)} items below threshold, avg ¶={avg_p:.2f}, avg S={avg_s:.2f}")

    if not below:
        print("  → Already Optimal!")
        return ir, paragraph_grades, sentence_grades, history

    # Build lookup maps
    sent_grade_map = {g.sentence_id: g for g in sentence_grades}

    for iteration in range(1, max_iterations + 1):
        print(f"\n  Iteration {iteration}:")
        rewrites = []

        # Rewrite below-threshold sentences
        for section in ir.sections:
            for para in section.paragraphs:
                section_type = _normalize_section_type_for_grading(para.classified_type)
                for i, sent in enumerate(para.sentences):
                    sg = sent_grade_map.get(sent.id)
                    if sg and not sg.is_optimal:
                        prev_text = para.sentences[i - 1].text if i > 0 else "(start)"
                        next_text = para.sentences[i + 1].text if i < len(para.sentences) - 1 else "(end)"
                        context = f"Previous: {prev_text}\nNext: {next_text}"
                        ev_json = json.dumps(
                            {"claim": sent.evidence.claim, "supported": sent.evidence.supported}
                            if sent.evidence else {}
                        )
                        result = _rewrite_item(
                            sent.id, sent.text, "sentence", sg.diagnosis,
                            section_type, context, ev_json,
                        )
                        if not result:
                            continue
                        candidate_text = str(result.get("rewritten_text", "")).strip()
                        if not candidate_text or candidate_text == sent.text:
                            continue

                        original_text = sent.text
                        sent.text = candidate_text
                        candidate_grade = _grade_sentence(
                            to_json(sent), section_type, context, ev_json, sent.id
                        )
                        if _should_accept_sentence_rewrite(sg, candidate_grade):
                            rewrites.append(result)
                            sent_grade_map[sent.id] = candidate_grade
                        else:
                            sent.text = original_text

        if not rewrites:
            print("    No accepted rewrites, stopping.")
            break

        print(f"    Applied {len(rewrites)} rewrites")

        # Re-grade
        paragraph_grades, sentence_grades = phase_grade(ir)
        sent_grade_map = {g.sentence_id: g for g in sentence_grades}

        # Record iteration
        below = get_below_threshold(paragraph_grades, sentence_grades)
        avg_p = (sum(g.aggregate for g in paragraph_grades) / len(paragraph_grades)
                 if paragraph_grades else 0)
        avg_s = (sum(g.weighted_aggregate for g in sentence_grades) / len(sentence_grades)
                 if sentence_grades else 0)
        history.append(IterationRecord(
            iteration=iteration, items_below_threshold=len(below),
            avg_paragraph_score=round(avg_p, 2), avg_sentence_score=round(avg_s, 2),
            rewrites_applied=len(rewrites),
        ))
        print(f"    {len(below)} items below threshold, avg ¶={avg_p:.2f}, avg S={avg_s:.2f}")

        # Check convergence
        if not below:
            print("  → Optimal reached!")
            break

        if detect_plateau(history, window=2):
            print("  → Plateau detected, stopping.")
            break

    return ir, paragraph_grades, sentence_grades, history


# ── Phase 5: Report ──────────────────────────────────────────────────


def phase_report(
    ir: IR,
    paragraph_grades: list[ParagraphGrade],
    sentence_grades: list[SentenceGrade],
    history: list[IterationRecord],
    evidence_result: VerificationResult,
    output_path: str,
) -> str:
    """Generate the final grade report."""
    print("[Phase 5] Generating report...")
    prompt_template = _load_agent_prompt("report_agent")
    _ensure_complete_grading(ir, paragraph_grades, sentence_grades)

    report_data = {
        "source_path": ir.source_path,
        "format": ir.format.value,
        "sections": [
            {
                "title": s.title,
                "paragraphs": [
                    {"id": p.id, "type": p.classified_type.value,
                     "sentences": [{"id": sent.id, "text": sent.text[:80]} for sent in p.sentences]}
                    for p in s.paragraphs
                ],
            }
            for s in ir.sections
        ],
        "paragraph_grades": [
            {"id": g.paragraph_id, "scores": g.scores, "aggregate": g.aggregate,
             "diagnosis": g.diagnosis, "below_threshold": g.below_threshold}
            for g in paragraph_grades
        ],
        "sentence_grades": [
            {"id": g.sentence_id, "scores": g.scores, "weights": g.weights_used,
             "weighted_aggregate": g.weighted_aggregate, "diagnosis": g.diagnosis,
             "suggestions": g.suggestions}
            for g in sentence_grades
        ],
        "convergence_log": [
            {"iteration": r.iteration, "below": r.items_below_threshold,
             "avg_para": r.avg_paragraph_score, "avg_sent": r.avg_sentence_score,
             "rewrites": r.rewrites_applied}
            for r in history
        ],
        "evidence_summary": [
            _normalize_evidence_summary_entry(v)
            for v in evidence_result.evidence_map.values()
        ],
        "evidence_skipped": [
            {"sentence_id": c.sentence_id, "claim": c.claim_text, "type": c.claim_type.name}
            for c in evidence_result.skipped_claims
        ],
    }

    # Determine final status
    below = get_below_threshold(paragraph_grades, sentence_grades)
    if not below:
        status = "Optimal"
    elif detect_plateau(history, window=2):
        status = f"Plateau at iteration {history[-1].iteration}"
    else:
        status = f"Max iterations reached ({history[-1].iteration})"
    report_data["status"] = status

    prompt = (
        f"{prompt_template}\n\n"
        f"## Input Data\n\n```json\n{json.dumps(report_data, indent=2)}\n```\n\n"
        f"Generate the full Markdown grade report."
    )
    report_md = _dispatch_claude(prompt, model="sonnet")

    # Write report
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report_md, encoding="utf-8")
    print(f"  → Report written to {output_path}")
    return report_md


# ── Main ─────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Hierarchical Multi-Agent Academic Paper Grader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python orchestrator.py --input paper.tex --notebook meta-rl-ftc
              python orchestrator.py --input paper.tex --skip-evidence --max-iterations 1
              python orchestrator.py --input structure.source.json --notebook thesis
        """),
    )
    parser.add_argument("--input", required=True, help="Path to input file (.tex, .md, .source.json)")
    parser.add_argument("--notebook", default=None, help="NotebookLM project key (from config/notebooklm_notebooks.yaml)")
    parser.add_argument("--output", default=None, help="Output report path (default: output/<input_stem>_grade.md)")
    parser.add_argument("--skip-evidence", action="store_true", help="Skip NotebookLM evidence retrieval")
    parser.add_argument("--max-iterations", type=int, default=DEFAULT_MAX_ITERATIONS,
                        help=f"Max rewrite iterations (default: {DEFAULT_MAX_ITERATIONS}, 0=grade only)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--grade-only", action="store_true", help="Grade without rewriting")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or str(
        PROJECT_ROOT / "output" / f"{input_path.stem}_grade.md"
    )

    print("=" * 60)
    print("Hierarchical Multi-Agent Academic Paper Grader")
    print("=" * 60)
    start_time = time.time()

    # Phase 1: Parse & Classify
    ir = phase_parse(str(input_path))
    ir = phase_classify(ir)

    # Phase 2: Evidence Retrieval
    evidence_result = VerificationResult()
    if not args.skip_evidence and args.notebook:
        import yaml
        nb_config = yaml.safe_load(
            (PROJECT_ROOT / "config" / "notebooklm_notebooks.yaml").read_text()
        )
        notebook_url = nb_config.get("notebooks", {}).get(args.notebook, {}).get("url", "")
        if notebook_url:
            budget = QueryBudget()
            evidence_result = phase_evidence(ir, notebook_url, budget)
        else:
            print(f"[WARN] Notebook '{args.notebook}' not found in config, skipping evidence.", file=sys.stderr)
    elif not args.skip_evidence:
        print("[INFO] No --notebook specified, skipping evidence retrieval.")

    # Phase 3: Initial Grading
    paragraph_grades, sentence_grades = phase_grade(ir)

    # Phase 4: Rewrite Loop
    history: list[IterationRecord] = []
    if not args.grade_only and args.max_iterations > 0:
        ir, paragraph_grades, sentence_grades, history = phase_rewrite_loop(
            ir, paragraph_grades, sentence_grades, args.max_iterations, args.verbose,
        )
    else:
        below = get_below_threshold(paragraph_grades, sentence_grades)
        avg_p = sum(g.aggregate for g in paragraph_grades) / max(len(paragraph_grades), 1)
        avg_s = sum(g.weighted_aggregate for g in sentence_grades) / max(len(sentence_grades), 1)
        history = [IterationRecord(
            iteration=0, items_below_threshold=len(below),
            avg_paragraph_score=round(avg_p, 2), avg_sentence_score=round(avg_s, 2),
            rewrites_applied=0,
        )]

    # Phase 5: Report
    report = phase_report(ir, paragraph_grades, sentence_grades, history, evidence_result, output_path)

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.1f}s. Report: {output_path}")


if __name__ == "__main__":
    main()
