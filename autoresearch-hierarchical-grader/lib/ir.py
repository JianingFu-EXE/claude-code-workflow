"""Internal Representation (IR) data structures for the hierarchical grader.

All data flows through these structures:
  Input → Parser → IR → Classifier → Graders → Report
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class SectionType(str, Enum):
    BACKGROUND = "Background"
    PROBLEM = "Problem"
    GAP = "Gap"
    METHODOLOGY = "Methodology"
    CONTRIBUTION = "Contribution"
    RESULTS = "Results"
    DISCUSSION = "Discussion"
    CONCLUSION = "Conclusion"
    ABSTRACT = "Abstract"
    UNKNOWN = "Unknown"


class InputFormat(str, Enum):
    LATEX = "latex"
    MARKDOWN = "markdown"
    XMIND = "xmind"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIABLE = "unverifiable"


# ── Core IR ──────────────────────────────────────────────────────────


@dataclass
class EvidenceEntry:
    """Result of triple-query verification for a single claim."""
    claim: str
    queries: list[str] = field(default_factory=list)
    responses: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.UNVERIFIABLE
    supported: bool = False
    note: str = ""


@dataclass
class Sentence:
    id: str
    text: str
    citations: list[str] = field(default_factory=list)
    evidence: Optional[EvidenceEntry] = None


@dataclass
class Paragraph:
    id: str
    sentences: list[Sentence] = field(default_factory=list)
    classified_type: SectionType = SectionType.UNKNOWN


@dataclass
class Section:
    id: str
    title: str
    paragraphs: list[Paragraph] = field(default_factory=list)


@dataclass
class IR:
    """Top-level Internal Representation of a parsed document."""
    source_path: str
    format: InputFormat
    sections: list[Section] = field(default_factory=list)


# ── Grading ──────────────────────────────────────────────────────────


PARAGRAPH_CRITERIA = ("flow", "structural_integrity", "argumentative_strength", "section_function_alignment")
SENTENCE_CRITERIA = ("linguistic_precision", "functional_context", "citation_appropriateness", "transition_quality")

OPTIMAL_THRESHOLD = 4  # All criteria must be >= this


def _is_valid_score(value) -> bool:
    """Return True when `value` is a numeric score on the 0-5 scale."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 5


def _scores_meet_threshold(scores: dict[str, int], expected_keys: tuple[str, ...]) -> bool:
    """Return True only when every expected criterion is present and passes."""
    if set(scores.keys()) != set(expected_keys):
        return False
    return all(_is_valid_score(value) and value >= OPTIMAL_THRESHOLD for value in scores.values())


def _below_threshold(scores: dict[str, int], expected_keys: tuple[str, ...]) -> list[str]:
    """Return expected criteria that are missing, invalid, or below threshold."""
    below = []
    for key in expected_keys:
        value = scores.get(key)
        if not _is_valid_score(value) or value < OPTIMAL_THRESHOLD:
            below.append(key)
    return below


@dataclass
class SentenceGrade:
    sentence_id: str
    scores: dict[str, int] = field(default_factory=dict)  # criterion → 0-5
    weights_used: dict[str, float] = field(default_factory=dict)
    weighted_aggregate: float = 0.0
    diagnosis: str = ""
    suggestions: list[str] = field(default_factory=list)
    phrasebank_matches: list[str] = field(default_factory=list)

    @property
    def is_optimal(self) -> bool:
        return _scores_meet_threshold(self.scores, SENTENCE_CRITERIA)

    @property
    def below_threshold_criteria(self) -> list[str]:
        return _below_threshold(self.scores, SENTENCE_CRITERIA)


@dataclass
class ParagraphGrade:
    paragraph_id: str
    scores: dict[str, int] = field(default_factory=dict)
    aggregate: float = 0.0
    diagnosis: str = ""
    below_threshold: list[str] = field(default_factory=list)

    @property
    def is_optimal(self) -> bool:
        return _scores_meet_threshold(self.scores, PARAGRAPH_CRITERIA)


@dataclass
class IterationRecord:
    iteration: int
    items_below_threshold: int
    avg_paragraph_score: float
    avg_sentence_score: float
    rewrites_applied: int


# ── Serialization ────────────────────────────────────────────────────


def to_json(obj) -> str:
    """Serialize any IR dataclass to JSON string."""
    def _convert(o):
        if isinstance(o, Enum):
            return o.value
        raise TypeError(f"Cannot serialize {type(o)}")
    return json.dumps(asdict(obj), default=_convert, indent=2)


def ir_from_dict(d: dict) -> IR:
    """Reconstruct an IR from a parsed JSON dict."""
    sections = []
    for s in d.get("sections", []):
        paragraphs = []
        for p in s.get("paragraphs", []):
            sentences = []
            for sent in p.get("sentences", []):
                ev = None
                if sent.get("evidence"):
                    ev = EvidenceEntry(**{
                        k: Confidence(v) if k == "confidence" else v
                        for k, v in sent["evidence"].items()
                    })
                sentences.append(Sentence(
                    id=sent["id"], text=sent["text"],
                    citations=sent.get("citations", []), evidence=ev,
                ))
            paragraphs.append(Paragraph(
                id=p["id"], sentences=sentences,
                classified_type=SectionType(p.get("classified_type", "Unknown")),
            ))
        sections.append(Section(id=s["id"], title=s["title"], paragraphs=paragraphs))
    return IR(
        source_path=d["source_path"],
        format=InputFormat(d["format"]),
        sections=sections,
    )
