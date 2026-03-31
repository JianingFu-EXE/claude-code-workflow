"""Tests for the parser module."""

import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.ir import InputFormat, SectionType
from lib.parser import detect_format, parse_file


TESTS_DIR = Path(__file__).resolve().parent


def test_detect_format_latex():
    assert detect_format(str(TESTS_DIR / "sample_background.tex")) == InputFormat.LATEX


def test_detect_format_markdown():
    assert detect_format(str(TESTS_DIR / "sample_problem.md")) == InputFormat.MARKDOWN


def test_parse_latex():
    ir = parse_file(str(TESTS_DIR / "sample_background.tex"))
    assert ir.format == InputFormat.LATEX
    assert len(ir.sections) >= 1
    # Should have at least "Introduction" and "Load Mitigation Approaches"
    titles = [s.title for s in ir.sections]
    assert any("Introduction" in t for t in titles), f"Sections: {titles}"
    # Check paragraphs exist
    total_paras = sum(len(s.paragraphs) for s in ir.sections)
    assert total_paras >= 2, f"Expected >= 2 paragraphs, got {total_paras}"
    # Check sentences extracted
    total_sents = sum(len(p.sentences) for s in ir.sections for p in s.paragraphs)
    assert total_sents >= 4, f"Expected >= 4 sentences, got {total_sents}"
    # Check citations extracted
    all_citations = [
        c for s in ir.sections for p in s.paragraphs
        for sent in p.sentences for c in sent.citations
    ]
    assert len(all_citations) >= 1, "Expected at least 1 citation extracted"


def test_parse_markdown():
    ir = parse_file(str(TESTS_DIR / "sample_problem.md"))
    assert ir.format == InputFormat.MARKDOWN
    assert len(ir.sections) >= 1
    titles = [s.title for s in ir.sections]
    assert any("Challenge" in t or "Problem" in t for t in titles), f"Sections: {titles}"
    total_sents = sum(len(p.sentences) for s in ir.sections for p in s.paragraphs)
    assert total_sents >= 3, f"Expected >= 3 sentences, got {total_sents}"


def test_ir_serialization():
    from lib.ir import to_json, ir_from_dict
    import json
    ir = parse_file(str(TESTS_DIR / "sample_background.tex"))
    json_str = to_json(ir)
    data = json.loads(json_str)
    ir2 = ir_from_dict(data)
    assert ir2.source_path == ir.source_path
    assert ir2.format == ir.format
    assert len(ir2.sections) == len(ir.sections)


def test_markdown_citation_extraction():
    tmp = TESTS_DIR / "tmp_markdown_citations.md"
    try:
        tmp.write_text(
            "# Intro\n\nThis claim is supported [@smith2024] and extended by [@jones2023; @lee2022].\n",
            encoding="utf-8",
        )
        ir = parse_file(str(tmp))
        sentence = ir.sections[0].paragraphs[0].sentences[0]
        assert sentence.citations == ["smith2024", "jones2023", "lee2022"]
        assert "[@" not in sentence.text
    finally:
        if tmp.exists():
            tmp.unlink()


def test_parse_latex_abstract_and_skip_figure():
    tmp = TESTS_DIR / "tmp_abstract_figure.tex"
    try:
        tmp.write_text(
            "\\begin{document}\n"
            "\\begin{abstract}\n"
            "This is the abstract sentence.\n"
            "\\end{abstract}\n"
            "\\section{Intro}\n"
            "\\begin{figure}\n"
            "This should be skipped.\n"
            "\\end{figure}\n"
            "\n"
            "Real text here.\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        ir = parse_file(str(tmp))
        assert ir.sections[0].title == "Abstract"
        abstract_sentences = [sent.text for p in ir.sections[0].paragraphs for sent in p.sentences]
        intro_sentences = [sent.text for p in ir.sections[1].paragraphs for sent in p.sentences]
        assert abstract_sentences == ["This is the abstract sentence."]
        assert intro_sentences == ["Real text here."]
    finally:
        if tmp.exists():
            tmp.unlink()


def test_parse_latex_itemize_cleans_item_markers():
    tmp = TESTS_DIR / "tmp_itemize.tex"
    try:
        tmp.write_text(
            "\\begin{document}\n"
            "\\section{Intro}\n"
            "\\begin{itemize}\n"
            "\\item First item. Second sentence.\n"
            "\\item Second item.\n"
            "\\end{itemize}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        ir = parse_file(str(tmp))
        sentences = [sent.text for p in ir.sections[0].paragraphs for sent in p.sentences]
        assert all("\\item" not in sentence for sentence in sentences)
        assert "First item." in sentences
        assert "Second item." in sentences
    finally:
        if tmp.exists():
            tmp.unlink()


if __name__ == "__main__":
    tests = [
        test_detect_format_latex,
        test_detect_format_markdown,
        test_parse_latex,
        test_parse_markdown,
        test_ir_serialization,
        test_markdown_citation_extraction,
        test_parse_latex_abstract_and_skip_figure,
        test_parse_latex_itemize_cleans_item_markers,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
