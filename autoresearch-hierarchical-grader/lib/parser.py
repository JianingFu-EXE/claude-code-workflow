"""Parser module: auto-detect input format and parse into IR.

Supports LaTeX (.tex), Markdown (.md), and XMind source JSON (.source.json).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from lib.ir import IR, Section, Paragraph, Sentence, InputFormat


# ── Format Detection ────────────────────────────────────────────────


def detect_format(path: str) -> InputFormat:
    """Detect input format from file extension.

    Args:
        path: File path to inspect.

    Returns:
        InputFormat enum value.

    Raises:
        ValueError: If the file extension is not recognised.
    """
    p = Path(path)
    if p.suffixes[-2:] == [".source", ".json"] or p.name.endswith(".source.json"):
        return InputFormat.XMIND
    ext = p.suffix.lower()
    if ext == ".tex":
        return InputFormat.LATEX
    if ext == ".md":
        return InputFormat.MARKDOWN
    raise ValueError(
        f"Unsupported file extension '{ext}' for '{path}'. "
        f"Expected .tex, .md, or .source.json"
    )


# ── Sentence Splitting ─────────────────────────────────────────────

# Abbreviations that should NOT trigger sentence boundaries.
_ABBREVS = (
    r"et al\.|Fig\.|Figs\.|Eq\.|Eqs\.|Ref\.|Refs\.|"
    r"Dr\.|Prof\.|Mr\.|Mrs\.|Ms\.|Jr\.|Sr\.|"
    r"vs\.|viz\.|approx\.|resp\.|"
    r"i\.e\.|e\.g\.|cf\.|"
    r"no\.|No\.|vol\.|Vol\.|pp\."
)

# Two-pass approach: protect abbreviation dots, split on sentence
# boundaries, then restore.  Variable-length lookbehinds are not supported
# in Python's re module, so we use placeholder substitution instead.
_ABBREV_PROTECT = re.compile(
    r"\b("
    r"et al|Fig|Figs|Eq|Eqs|Ref|Refs|"
    r"Dr|Prof|Mr|Mrs|Ms|Jr|Sr|"
    r"vs|viz|approx|resp|"
    r"i\.e|e\.g|cf|"
    r"no|No|vol|Vol|pp"
    r")\."
)

_PLACEHOLDER = "\x00DOT\x00"


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling common abbreviations."""
    if not text.strip():
        return []

    # Protect abbreviation dots
    protected = _ABBREV_PROTECT.sub(lambda m: m.group(1) + _PLACEHOLDER, text)

    # Split on sentence-ending punctuation followed by space + uppercase
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\[])", protected)

    # Restore dots and strip
    sentences = []
    for part in parts:
        restored = part.replace(_PLACEHOLDER, ".").strip()
        if restored:
            sentences.append(restored)

    return sentences


# ── Citation Extraction ─────────────────────────────────────────────

# Matches \cite{key}, \citep{key1, key2}, \citet{key}, and bracket forms
_CITE_RE = re.compile(r"\\cite[pt]?\{([^}]+)\}")
_MD_CITE_RE = re.compile(r"\[@([^\]]+)\]")
_ABSTRACT_RE = re.compile(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
    re.DOTALL | re.IGNORECASE,
)
_SKIP_ENV_RE = re.compile(
    r"\\begin\{(figure\*?|table\*?)\}.*?\\end\{\1\}",
    re.DOTALL | re.IGNORECASE,
)
_STRIPPABLE_ENV_RE = re.compile(
    r"\\(?:begin|end)\{(?:document|itemize|enumerate|equation\*?|align\*?)\}",
    re.IGNORECASE,
)


def _extract_citations(text: str) -> list[str]:
    """Extract citation keys from LaTeX and Markdown citation syntax."""
    keys = []
    for match in _CITE_RE.finditer(text):
        raw_keys = match.group(1)
        for key in raw_keys.split(","):
            key = key.strip()
            if key:
                keys.append(key)
    for match in _MD_CITE_RE.finditer(text):
        raw_keys = match.group(1)
        for key in re.split(r"[;,]", raw_keys):
            key = key.strip().lstrip("@")
            if key:
                keys.append(key)
    return keys


def _strip_citations(text: str) -> str:
    """Remove citation markup from the sentence display text."""
    clean_text = _CITE_RE.sub("", text)
    clean_text = _MD_CITE_RE.sub("", clean_text)
    return re.sub(r"\s{2,}", " ", clean_text).strip()


# ── LaTeX Parser ────────────────────────────────────────────────────

_SECTION_RE = re.compile(
    r"\\(section|subsection)\{([^}]+)\}"
)


def _parse_latex(text: str, source_path: str) -> IR:
    """Parse a LaTeX document into IR."""

    # Strip preamble and postamble
    begin = re.search(r"\\begin\{document\}", text)
    end = re.search(r"\\end\{document\}", text)
    if begin:
        text = text[begin.end():]
    if end:
        text = text[:end.start()]

    # Remove common LaTeX commands that are not content
    text = re.sub(r"\\maketitle", "", text)
    text = re.sub(r"\\tableofcontents", "", text)
    text = _SKIP_ENV_RE.sub("", text)

    sections: list[Section] = []
    sec_counter = 0
    para_counter = 0
    sent_counter = 0

    abstract_match = _ABSTRACT_RE.search(text)
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        text = _ABSTRACT_RE.sub("", text, count=1)
        if abstract_text:
            sec_counter += 1
            abstract = Section(id=f"sec-{sec_counter}", title="Abstract")
            paragraphs = _split_paragraphs_latex(
                abstract_text, sec_counter, para_counter, sent_counter
            )
            para_counter += len(paragraphs)
            for p in paragraphs:
                sent_counter += len(p.sentences)
            abstract.paragraphs = paragraphs
            if paragraphs:
                sections.append(abstract)

    # Split by section/subsection commands
    parts = _SECTION_RE.split(text)

    # parts[0] is text before the first section header (if any)
    # Then groups of 3: (level, title, text_until_next)

    # Handle text before first section (e.g., abstract)
    preamble_text = parts[0].strip() if parts else ""
    if preamble_text:
        sec_counter += 1
        section = Section(id=f"sec-{sec_counter}", title="Preamble")
        paragraphs = _split_paragraphs_latex(
            preamble_text, sec_counter, para_counter, sent_counter
        )
        para_counter += len(paragraphs)
        for p in paragraphs:
            sent_counter += len(p.sentences)
        section.paragraphs = paragraphs
        if paragraphs:
            sections.append(section)

    # Process each section
    i = 1
    while i < len(parts):
        # level = parts[i]  # "section" or "subsection"
        title = parts[i + 1]
        body = parts[i + 2] if i + 2 < len(parts) else ""
        i += 3

        sec_counter += 1
        section = Section(id=f"sec-{sec_counter}", title=title.strip())
        paragraphs = _split_paragraphs_latex(
            body, sec_counter, para_counter, sent_counter
        )
        para_counter += len(paragraphs)
        for p in paragraphs:
            sent_counter += len(p.sentences)
        section.paragraphs = paragraphs
        sections.append(section)

    return IR(source_path=source_path, format=InputFormat.LATEX, sections=sections)


def _split_paragraphs_latex(
    text: str, sec_num: int, para_offset: int, sent_offset: int
) -> list[Paragraph]:
    """Split LaTeX body text into Paragraphs, then into Sentences."""
    # Split on double newlines or \par
    raw_paragraphs = re.split(r"\n\s*\n|\\par\b", text)
    paragraphs: list[Paragraph] = []

    for raw in raw_paragraphs:
        raw = raw.strip()
        # Remove LaTeX comments
        raw = re.sub(r"%.*$", "", raw, flags=re.MULTILINE).strip()
        raw = raw.replace("\\item", "\n")
        raw = _STRIPPABLE_ENV_RE.sub("", raw).strip()
        if not raw:
            continue

        para_offset += 1
        para = Paragraph(id=f"par-{para_offset}")

        sentence_texts = _split_sentences(raw)
        for st in sentence_texts:
            sent_offset += 1
            citations = _extract_citations(st)
            # Clean citation commands from display text
            clean_text = _strip_citations(st)
            para.sentences.append(
                Sentence(
                    id=f"sent-{sent_offset}",
                    text=clean_text if clean_text else st,
                    citations=citations,
                )
            )

        if para.sentences:
            paragraphs.append(para)

    return paragraphs


# ── Markdown Parser ─────────────────────────────────────────────────

_MD_HEADER_RE = re.compile(r"^(#{1,2})\s+(.+)$", re.MULTILINE)


def _parse_markdown(text: str, source_path: str) -> IR:
    """Parse a Markdown document into IR."""
    sections: list[Section] = []
    sec_counter = 0
    para_counter = 0
    sent_counter = 0

    # Split by headers
    parts = _MD_HEADER_RE.split(text)

    # parts[0] is text before first header
    preamble_text = parts[0].strip() if parts else ""
    if preamble_text:
        sec_counter += 1
        section = Section(id=f"sec-{sec_counter}", title="Preamble")
        paragraphs = _split_paragraphs_plain(
            preamble_text, para_counter, sent_counter
        )
        para_counter += len(paragraphs)
        for p in paragraphs:
            sent_counter += len(p.sentences)
        section.paragraphs = paragraphs
        if paragraphs:
            sections.append(section)

    # Groups of 3: (hashes, title, body)
    i = 1
    while i < len(parts):
        # hashes = parts[i]  # "#" or "##"
        title = parts[i + 1]
        body = parts[i + 2] if i + 2 < len(parts) else ""
        i += 3

        sec_counter += 1
        section = Section(id=f"sec-{sec_counter}", title=title.strip())
        paragraphs = _split_paragraphs_plain(body, para_counter, sent_counter)
        para_counter += len(paragraphs)
        for p in paragraphs:
            sent_counter += len(p.sentences)
        section.paragraphs = paragraphs
        sections.append(section)

    return IR(source_path=source_path, format=InputFormat.MARKDOWN, sections=sections)


def _split_paragraphs_plain(
    text: str, para_offset: int, sent_offset: int
) -> list[Paragraph]:
    """Split plain text into Paragraphs and Sentences."""
    raw_paragraphs = re.split(r"\n\s*\n", text)
    paragraphs: list[Paragraph] = []

    for raw in raw_paragraphs:
        raw = raw.strip()
        if not raw:
            continue

        para_offset += 1
        para = Paragraph(id=f"par-{para_offset}")

        sentence_texts = _split_sentences(raw)
        for st in sentence_texts:
            sent_offset += 1
            citations = _extract_citations(st)
            para.sentences.append(
                Sentence(
                    id=f"sent-{sent_offset}",
                    text=_strip_citations(st) or st,
                    citations=citations,
                )
            )

        if para.sentences:
            paragraphs.append(para)

    return paragraphs


# ── XMind Source JSON Parser ────────────────────────────────────────

_SECTION_TITLE_RE = re.compile(r"^§[\d.]+\s+")
_PARAGRAPH_TITLE_RE = re.compile(r"^¶\d+:\s*")
_SENTENCE_TITLE_RE = re.compile(r"^S\d+:\s*")


def _parse_xmind(data: dict | list, source_path: str) -> IR:
    """Parse an XMind .source.json export into IR.

    Expected structure: a list of sheets, each with a rootTopic.
    We walk the topic tree looking for §/¶/S patterns.
    """
    sections: list[Section] = []
    sec_counter = 0
    para_counter = 0
    sent_counter = 0

    # Normalise: handle both list-of-sheets and single-sheet
    if isinstance(data, dict):
        sheets = [data]
    elif isinstance(data, list):
        sheets = data
    else:
        return IR(source_path=source_path, format=InputFormat.XMIND, sections=[])

    for sheet in sheets:
        root = sheet.get("rootTopic", sheet)
        # Walk children looking for section-level nodes
        children = root.get("children", {})
        if isinstance(children, dict):
            topics = children.get("attached", [])
        elif isinstance(children, list):
            topics = children
        else:
            topics = []

        for topic in topics:
            result = _walk_xmind_topic(
                topic, sec_counter, para_counter, sent_counter
            )
            if result:
                new_sections, sec_counter, para_counter, sent_counter = result
                sections.extend(new_sections)

    return IR(source_path=source_path, format=InputFormat.XMIND, sections=sections)


def _walk_xmind_topic(
    topic: dict,
    sec_counter: int,
    para_counter: int,
    sent_counter: int,
) -> tuple[list[Section], int, int, int] | None:
    """Recursively walk an XMind topic tree.

    Returns (sections_found, updated_sec_counter, updated_para_counter,
             updated_sent_counter) or None.
    """
    title = topic.get("title", "")
    children = topic.get("children", {})
    if isinstance(children, dict):
        child_topics = children.get("attached", [])
    elif isinstance(children, list):
        child_topics = children
    else:
        child_topics = []

    sections: list[Section] = []

    # Case 1: This is a §-section node
    if _SECTION_TITLE_RE.match(title):
        sec_counter += 1
        section = Section(id=f"sec-{sec_counter}", title=title.strip())

        for child in child_topics:
            child_title = child.get("title", "")

            # Direct ¶ paragraph children
            if _PARAGRAPH_TITLE_RE.match(child_title):
                para_counter += 1
                para = Paragraph(id=f"par-{para_counter}")
                para.sentences = _collect_sentences(child, sent_counter)
                sent_counter += len(para.sentences)
                if para.sentences:
                    section.paragraphs.append(para)

            # Nested subsections (§N.M.K)
            elif _SECTION_TITLE_RE.match(child_title):
                result = _walk_xmind_topic(
                    child, sec_counter, para_counter, sent_counter
                )
                if result:
                    sub_sections, sec_counter, para_counter, sent_counter = result
                    sections.extend(sub_sections)

        sections.insert(0, section)
        return sections, sec_counter, para_counter, sent_counter

    # Case 2: Not a section -- recurse into children looking for sections
    for child in child_topics:
        result = _walk_xmind_topic(child, sec_counter, para_counter, sent_counter)
        if result:
            sub_sections, sec_counter, para_counter, sent_counter = result
            sections.extend(sub_sections)

    if sections:
        return sections, sec_counter, para_counter, sent_counter
    return None


def _collect_sentences(
    para_topic: dict, sent_offset: int
) -> list[Sentence]:
    """Collect S-pattern sentence nodes from a paragraph topic's children."""
    sentences: list[Sentence] = []

    children = para_topic.get("children", {})
    if isinstance(children, dict):
        child_topics = children.get("attached", [])
    elif isinstance(children, list):
        child_topics = children
    else:
        child_topics = []

    for child in child_topics:
        child_title = child.get("title", "")
        if _SENTENCE_TITLE_RE.match(child_title):
            sent_offset += 1
            # Strip the "SN: " prefix
            text = _SENTENCE_TITLE_RE.sub("", child_title).strip()
            citations = _extract_citations(text)
            sentences.append(
                Sentence(
                    id=f"sent-{sent_offset}",
                    text=_strip_citations(text) or text,
                    citations=citations,
                )
            )

    # If no S-pattern children, treat the paragraph title itself as a sentence
    if not sentences:
        title = para_topic.get("title", "")
        text = _PARAGRAPH_TITLE_RE.sub("", title).strip()
        if text:
            sent_offset += 1
            citations = _extract_citations(text)
            sentences.append(
                Sentence(
                    id=f"sent-{sent_offset}",
                    text=_strip_citations(text) or text,
                    citations=citations,
                )
            )

    return sentences


# ── Public API ──────────────────────────────────────────────────────


def parse_file(path: str) -> IR:
    """Parse an academic document into the IR.

    Auto-detects input format from the file extension, reads the file,
    and returns a fully populated IR tree.

    Args:
        path: Path to the input file (.tex, .md, or .source.json).

    Returns:
        IR dataclass with sections, paragraphs, and sentences populated.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the format cannot be detected.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    fmt = detect_format(path)

    if fmt == InputFormat.XMIND:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _parse_xmind(data, source_path=path)

    text = p.read_text(encoding="utf-8")

    if fmt == InputFormat.LATEX:
        return _parse_latex(text, source_path=path)
    if fmt == InputFormat.MARKDOWN:
        return _parse_markdown(text, source_path=path)

    # Should not reach here due to detect_format validation
    raise ValueError(f"Unsupported format: {fmt}")
