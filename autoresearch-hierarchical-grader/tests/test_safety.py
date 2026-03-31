"""Safety and orchestration regression tests."""

import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import orchestrator
from lib.ir import (
    EvidenceEntry,
    Confidence,
    IR,
    InputFormat,
    IterationRecord,
    Paragraph,
    ParagraphGrade,
    Section,
    SectionType,
    Sentence,
    SentenceGrade,
)
from lib.triple_query import VerificationResult


def _single_sentence_ir(section_type: SectionType = SectionType.BACKGROUND) -> IR:
    return IR(
        source_path="dummy.tex",
        format=InputFormat.LATEX,
        sections=[
            Section(
                id="sec-1",
                title="Intro",
                paragraphs=[
                    Paragraph(
                        id="par-1",
                        classified_type=section_type,
                        sentences=[Sentence(id="sent-1", text="A sentence.")],
                    )
                ],
            )
        ],
    )


def test_empty_scores_are_not_optimal():
    assert not SentenceGrade("sent-1").is_optimal
    assert not ParagraphGrade("par-1").is_optimal


def test_phase_report_rejects_partial_grading():
    ir = _single_sentence_ir()
    try:
        orchestrator.phase_report(
            ir,
            [],
            [],
            [IterationRecord(0, 1, 0.0, 0.0, 0)],
            VerificationResult(),
            "output/should_not_exist.md",
        )
    except RuntimeError as exc:
        assert "Grading incomplete" in str(exc)
    else:
        raise AssertionError("phase_report should fail closed on partial grading")


def test_phase_report_accepts_dict_evidence_entries():
    ir = _single_sentence_ir()
    paragraph_grades = [
        ParagraphGrade(
            paragraph_id="par-1",
            scores={
                "flow": 4,
                "structural_integrity": 4,
                "argumentative_strength": 4,
                "section_function_alignment": 4,
            },
            aggregate=4.0,
            diagnosis="",
            below_threshold=[],
        )
    ]
    sentence_grades = [
        SentenceGrade(
            sentence_id="sent-1",
            scores={
                "linguistic_precision": 4,
                "functional_context": 4,
                "citation_appropriateness": 4,
                "transition_quality": 4,
            },
            weights_used={
                "linguistic_precision": 0.25,
                "functional_context": 0.25,
                "citation_appropriateness": 0.25,
                "transition_quality": 0.25,
            },
            weighted_aggregate=4.0,
            diagnosis="",
            suggestions=[],
        )
    ]

    evidence = VerificationResult(
        evidence_map={
            "sent-1": EvidenceEntry(
                claim="A sentence.",
                confidence=Confidence.HIGH,
                supported=True,
                note="",
            )
        },
        total_claims=1,
    )
    original_dispatch = orchestrator._dispatch_claude
    try:
        orchestrator._dispatch_claude = lambda prompt, model="sonnet": "# report\n"
        report = orchestrator.phase_report(
            ir,
            paragraph_grades,
            sentence_grades,
            [IterationRecord(0, 0, 4.0, 4.0, 0)],
            evidence,
            "output/test_report.md",
        )
        assert report.strip() == "# report"
    finally:
        orchestrator._dispatch_claude = original_dispatch


def test_phase_grade_normalizes_abstract_to_background():
    ir = _single_sentence_ir(SectionType.ABSTRACT)

    original_dispatch = orchestrator._dispatch_claude
    try:
        def fake_dispatch(prompt: str, model: str = "sonnet") -> str:
            if "Grade this paragraph" in prompt:
                return (
                    '{"paragraph_id":"par-1","scores":{"flow":4,"structural_integrity":4,'
                    '"argumentative_strength":4,"section_function_alignment":4},'
                    '"aggregate":4.0,"diagnosis":"","below_threshold":[]}'
                )
            return (
                '{"sentence_id":"sent-1","scores":{"linguistic_precision":4,"functional_context":4,'
                '"citation_appropriateness":4,"transition_quality":4},'
                '"weights_used":{"linguistic_precision":0.25,"functional_context":0.25,'
                '"citation_appropriateness":0.25,"transition_quality":0.25},'
                '"weighted_aggregate":4.0,"diagnosis":"","suggestions":[],"phrasebank_matches":[]}'
            )

        orchestrator._dispatch_claude = fake_dispatch
        paragraph_grades, sentence_grades = orchestrator.phase_grade(ir)
        assert len(paragraph_grades) == 1
        assert len(sentence_grades) == 1
        assert paragraph_grades[0].paragraph_id == "par-1"
        assert sentence_grades[0].sentence_id == "sent-1"
    finally:
        orchestrator._dispatch_claude = original_dispatch


def test_rewrite_loop_rejects_regression():
    ir = _single_sentence_ir()
    paragraph_grades = [
        ParagraphGrade(
            paragraph_id="par-1",
            scores={
                "flow": 4,
                "structural_integrity": 4,
                "argumentative_strength": 4,
                "section_function_alignment": 4,
            },
            aggregate=4.0,
            diagnosis="",
            below_threshold=[],
        )
    ]
    sentence_grades = [
        SentenceGrade(
            sentence_id="sent-1",
            scores={
                "linguistic_precision": 3,
                "functional_context": 3,
                "citation_appropriateness": 4,
                "transition_quality": 4,
            },
            weights_used={
                "linguistic_precision": 0.25,
                "functional_context": 0.25,
                "citation_appropriateness": 0.25,
                "transition_quality": 0.25,
            },
            weighted_aggregate=3.5,
            diagnosis="Needs work",
            suggestions=["Improve it"],
        )
    ]

    original_rewrite_item = orchestrator._rewrite_item
    original_grade_sentence = orchestrator._grade_sentence
    try:
        orchestrator._rewrite_item = lambda *args, **kwargs: {
            "original_id": "sent-1",
            "rewritten_text": "A worse sentence.",
        }
        orchestrator._grade_sentence = lambda *args, **kwargs: SentenceGrade(
            sentence_id="sent-1",
            scores={
                "linguistic_precision": 2,
                "functional_context": 2,
                "citation_appropriateness": 4,
                "transition_quality": 4,
            },
            weights_used={
                "linguistic_precision": 0.25,
                "functional_context": 0.25,
                "citation_appropriateness": 0.25,
                "transition_quality": 0.25,
            },
            weighted_aggregate=3.0,
            diagnosis="Worse",
            suggestions=[],
        )
        updated_ir, _, _, history = orchestrator.phase_rewrite_loop(
            ir,
            paragraph_grades,
            sentence_grades,
            max_iterations=1,
        )
        assert updated_ir.sections[0].paragraphs[0].sentences[0].text == "A sentence."
        assert history[-1].rewrites_applied == 0
    finally:
        orchestrator._rewrite_item = original_rewrite_item
        orchestrator._grade_sentence = original_grade_sentence


if __name__ == "__main__":
    tests = [
        test_empty_scores_are_not_optimal,
        test_phase_report_rejects_partial_grading,
        test_phase_report_accepts_dict_evidence_entries,
        test_phase_grade_normalizes_abstract_to_background,
        test_rewrite_loop_rejects_regression,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL: {test.__name__}: {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
