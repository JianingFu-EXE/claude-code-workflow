"""Triple-query evidence retrieval protocol.

Verifies academic claims against NotebookLM sources using three query
variations per claim: Direct, Contextual, and Adversarial.  Responses are
synthesised with an intersection rule to assign confidence levels.

Usage:
    from lib.triple_query import verify_claims, QueryBudget
    evidence_map = verify_claims(ir, notebook_url, QueryBudget())
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

from lib.ir import IR, EvidenceEntry, Confidence


# ── Claim extraction ────────────────────────────────────────────────


class ClaimType(IntEnum):
    """Claim types ordered by verification priority (lower value = higher)."""
    QUANTITATIVE = 1
    GAP_STATEMENT = 2
    METHOD_JUSTIFICATION = 3
    BACKGROUND_CONTEXT = 4


@dataclass
class Claim:
    sentence_id: str
    claim_text: str
    claim_type: ClaimType
    priority: int  # 1-4, mirrors ClaimType value


# Patterns that indicate quantitative content
_QUANT_RE = re.compile(
    r"""
    \d+\.?\d*\s*%          |  # percentages
    \d+\.?\d*\s*(?:kW|MW|GW|m/s|rpm|Hz|kN|MN|Nm|Pa|MPa|kg|m|s|deg) |  # units
    \d{4}                  |  # years
    \d+\.?\d*\s*(?:×|x)\s*10  # scientific notation
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Patterns for gap / limitation language
_GAP_RE = re.compile(
    r"\b(?:however|gap|limitation|lacks?|insufficient|few studies|no existing|remains? "
    r"unclear|poorly understood|open question|unresolved)\b",
    re.IGNORECASE,
)

# Patterns for methodology justification
_METHOD_RE = re.compile(
    r"\b(?:we (?:propose|adopt|employ|use|design|develop)|this (?:paper|study|work) "
    r"(?:proposes|adopts|employs|uses)|is chosen because|is selected due to|"
    r"the rationale|justified by)\b",
    re.IGNORECASE,
)


def _classify_claim(text: str, has_citation: bool) -> Optional[ClaimType]:
    """Return the claim type if the sentence warrants verification, else None."""
    if _QUANT_RE.search(text):
        return ClaimType.QUANTITATIVE
    if _GAP_RE.search(text):
        return ClaimType.GAP_STATEMENT
    if _METHOD_RE.search(text):
        return ClaimType.METHOD_JUSTIFICATION
    if has_citation:
        return ClaimType.BACKGROUND_CONTEXT
    return None


def extract_claims(ir: IR) -> list[Claim]:
    """Walk every sentence in the IR and return verifiable claims.

    A sentence is considered a claim if it contains citations, quantitative
    data, gap language, or methodology justification.  Claims are returned
    sorted by priority (quantitative first).
    """
    claims: list[Claim] = []
    for section in ir.sections:
        for paragraph in section.paragraphs:
            for sentence in paragraph.sentences:
                has_citation = bool(sentence.citations)
                claim_type = _classify_claim(sentence.text, has_citation)
                if claim_type is not None:
                    claims.append(Claim(
                        sentence_id=sentence.id,
                        claim_text=sentence.text,
                        claim_type=claim_type,
                        priority=int(claim_type),
                    ))
    claims.sort(key=lambda c: c.priority)
    return claims


# ── Query generation (deterministic, no LLM) ───────────────────────


_DIRECT_TEMPLATE = 'Is it true that {claim}? Answer yes or no with a brief explanation.'
_CONTEXTUAL_TEMPLATE = (
    'What does the literature say about the context surrounding this claim: '
    '"{claim}"? Summarise relevant evidence from the sources.'
)
_ADVERSARIAL_TEMPLATE = (
    'Is there any evidence that contradicts or challenges the following claim: '
    '"{claim}"? If so, summarise the contradicting evidence.'
)


def generate_triple_queries(claim: Claim) -> list[str]:
    """Produce three wording variations for a single claim.

    Returns [Q1_direct, Q2_contextual, Q3_adversarial].
    """
    text = claim.claim_text.rstrip(".")
    return [
        _DIRECT_TEMPLATE.format(claim=text),
        _CONTEXTUAL_TEMPLATE.format(claim=text),
        _ADVERSARIAL_TEMPLATE.format(claim=text),
    ]


# ── Query execution via NotebookLM skill ────────────────────────────


_QUERY_DELAY_SECONDS = 2.0


def execute_query(question: str, notebook_url: str) -> str:
    """Send a single question to NotebookLM via the Claude CLI.

    Invokes ``claude --print -p <prompt>`` as a subprocess.  The prompt
    instructs Claude to use the notebooklm skill to query the given
    notebook.  Returns the raw stdout text.
    """
    prompt = (
        f'Use the notebooklm skill to query the following notebook: {notebook_url}\n'
        f'Question: {question}\n'
        f'Return ONLY the answer from the notebook sources. '
        f'Do not add commentary outside what the sources say.'
    )
    result = subprocess.run(
        ["claude", "--print", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.stdout.strip()


def _execute_triple(queries: list[str], notebook_url: str) -> list[str]:
    """Execute three queries with a delay between each."""
    responses: list[str] = []
    for i, q in enumerate(queries):
        resp = execute_query(q, notebook_url)
        responses.append(resp)
        if i < len(queries) - 1:
            time.sleep(_QUERY_DELAY_SECONDS)
    return responses


# ── Response synthesis ──────────────────────────────────────────────


_AGREE_KEYWORDS = re.compile(r"\b(?:yes|confirms?|supports?|consistent|agree)\b", re.I)
_CONTRADICT_KEYWORDS = re.compile(r"\b(?:no|contradicts?|inconsistent|disagree|refute|challenge)\b", re.I)
_SILENT_KEYWORDS = re.compile(
    r"\b(?:no (?:information|evidence|mention)|not (?:found|mentioned|addressed)|"
    r"unclear|cannot (?:confirm|determine)|insufficient)\b",
    re.I,
)


def _response_stance(response: str) -> str:
    """Classify a response as 'agree', 'contradict', or 'silent'."""
    if not response:
        return "silent"
    has_agree = bool(_AGREE_KEYWORDS.search(response))
    has_contra = bool(_CONTRADICT_KEYWORDS.search(response))
    has_silent = bool(_SILENT_KEYWORDS.search(response))

    if has_agree and not has_contra:
        return "agree"
    if has_contra and not has_agree:
        return "contradict"
    if has_silent:
        return "silent"
    # When both agree and contradict signals appear, treat as contradict
    if has_contra:
        return "contradict"
    # Default: treat as silent (ambiguous)
    return "silent"


def synthesize_responses(queries: list[str], responses: list[str]) -> EvidenceEntry:
    """Apply intersection rules to three query responses.

    Rules:
        3/3 agree           -> HIGH confidence, supported
        2/3 agree, 1 silent -> MEDIUM confidence, supported
        2/3 agree, 1 contra -> LOW confidence, supported but flagged
        all disagree/mixed  -> UNVERIFIABLE, flagged
    """
    stances = [_response_stance(r) for r in responses]
    agree_count = stances.count("agree")
    contra_count = stances.count("contradict")
    silent_count = stances.count("silent")

    if agree_count == 3:
        confidence = Confidence.HIGH
        supported = True
        note = "All three queries agree: claim is well-supported by sources."
    elif agree_count == 2 and silent_count >= 1 and contra_count == 0:
        confidence = Confidence.MEDIUM
        supported = True
        note = "Two queries support the claim; one returned no relevant information."
    elif agree_count >= 2 and contra_count >= 1:
        confidence = Confidence.LOW
        supported = True
        note = "Majority supports the claim but contradicting evidence was found. Manual review recommended."
    else:
        confidence = Confidence.UNVERIFIABLE
        supported = False
        note = (
            f"Responses are inconclusive (agree={agree_count}, contradict={contra_count}, "
            f"silent={silent_count}). Manual verification required."
        )

    return EvidenceEntry(
        claim="",  # filled by caller
        queries=list(queries),
        responses=list(responses),
        confidence=confidence,
        supported=supported,
        note=note,
    )


# ── Budget management ───────────────────────────────────────────────


@dataclass
class QueryBudget:
    """Track daily query usage against a hard limit.

    Default budget: 50 queries per day.  Each triple-query consumes 3.
    When fewer than 3 remain, falls back to single-query mode.
    """
    daily_limit: int = 50
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.daily_limit - self.used)

    @property
    def can_triple(self) -> bool:
        return self.remaining >= 3

    @property
    def can_single(self) -> bool:
        return self.remaining >= 1

    def consume(self, n: int = 1) -> None:
        self.used += n

    def reset(self) -> None:
        self.used = 0


# ── Top-level verification entry point ──────────────────────────────


def _verify_single_query(claim: Claim, notebook_url: str) -> EvidenceEntry:
    """Fallback: verify with a single direct query when budget is low."""
    queries = [generate_triple_queries(claim)[0]]  # Direct query only
    responses = [execute_query(queries[0], notebook_url)]
    stance = _response_stance(responses[0])

    if stance == "agree":
        confidence = Confidence.MEDIUM
        supported = True
        note = "Single-query fallback: source appears to support the claim."
    elif stance == "contradict":
        confidence = Confidence.LOW
        supported = False
        note = "Single-query fallback: source appears to contradict the claim."
    else:
        confidence = Confidence.UNVERIFIABLE
        supported = False
        note = "Single-query fallback: no clear evidence found."

    return EvidenceEntry(
        claim=claim.claim_text,
        queries=queries,
        responses=responses,
        confidence=confidence,
        supported=supported,
        note=note,
    )


@dataclass
class VerificationResult:
    """Outcome of verify_claims(): verified evidence + metadata on skipped claims."""
    evidence_map: dict[str, EvidenceEntry] = field(default_factory=dict)
    skipped_claims: list[Claim] = field(default_factory=list)
    total_claims: int = 0
    budget_used: int = 0

    @property
    def verified_count(self) -> int:
        return len(self.evidence_map)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_claims)


def verify_claims(
    ir: IR,
    notebook_url: str,
    budget: Optional[QueryBudget] = None,
) -> VerificationResult:
    """Verify all extractable claims in an IR against a NotebookLM notebook.

    Args:
        ir: The parsed internal representation of the document.
        notebook_url: URL of the NotebookLM notebook to query.
        budget: Optional query budget tracker.  Defaults to 50/day.

    Returns:
        VerificationResult containing the evidence map for verified claims
        and a list of claims that were skipped due to budget exhaustion.
    """
    if budget is None:
        budget = QueryBudget()

    claims = extract_claims(ir)
    result = VerificationResult(total_claims=len(claims))
    budget_start = budget.used

    for claim in claims:
        if budget.can_triple:
            queries = generate_triple_queries(claim)
            responses = _execute_triple(queries, notebook_url)
            entry = synthesize_responses(queries, responses)
            entry.claim = claim.claim_text
            budget.consume(3)
        elif budget.can_single:
            entry = _verify_single_query(claim, notebook_url)
            budget.consume(1)
        else:
            result.skipped_claims.append(claim)
            continue

        result.evidence_map[claim.sentence_id] = entry

    result.budget_used = budget.used - budget_start
    return result
