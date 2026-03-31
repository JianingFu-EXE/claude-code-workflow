"""Score aggregation, convergence detection, and config loading for the hierarchical grader.

Functions:
    compute_paragraph_aggregate  -- simple mean of 4 paragraph criteria
    compute_sentence_aggregate   -- weighted mean of 4 sentence criteria
    get_weights_for_section      -- loads dynamic weight profile from config/weights.yaml
    get_rubric_for_section       -- loads rubric criteria from config/rubric.yaml
    is_optimal                   -- checks whether all grades meet the optimal threshold
    detect_plateau               -- detects score stagnation across iterations
    get_below_threshold          -- returns IDs of items with any criterion < 4
    load_phrasebank_patterns     -- loads Phrasebank .md content for a section type
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import yaml

from lib.ir import (
    IterationRecord,
    OPTIMAL_THRESHOLD,
    ParagraphGrade,
    SectionType,
    SentenceGrade,
)

# Project root: two levels up from this file (lib/scoring.py -> project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"
_REFERENCE_DIR = _PROJECT_ROOT / "reference"

# Cache loaded configs to avoid repeated disk reads within a session
_weights_cache: dict | None = None
_rubric_cache: dict | None = None
_phrasebank_index_cache: dict | None = None


def _load_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_weights_config() -> dict:
    """Load and cache weights.yaml."""
    global _weights_cache
    if _weights_cache is None:
        data = _load_yaml(_CONFIG_DIR / "weights.yaml")
        _weights_cache = data.get("weights", data)
    return _weights_cache


def _get_rubric_config() -> dict:
    """Load and cache rubric.yaml."""
    global _rubric_cache
    if _rubric_cache is None:
        _rubric_cache = _load_yaml(_CONFIG_DIR / "rubric.yaml")
    return _rubric_cache


def _get_phrasebank_index() -> dict:
    """Load and cache phrasebank_index.yaml."""
    global _phrasebank_index_cache
    if _phrasebank_index_cache is None:
        _phrasebank_index_cache = _load_yaml(_CONFIG_DIR / "phrasebank_index.yaml")
    return _phrasebank_index_cache


def _normalize_section_type(section_type: Union[str, SectionType]) -> str:
    """Convert SectionType enum or string to the canonical string key used in configs."""
    if isinstance(section_type, SectionType):
        return section_type.value
    return section_type


# ── Score Aggregation ────────────────────────────────────────────────


def compute_paragraph_aggregate(scores: dict[str, int]) -> float:
    """Compute the simple arithmetic mean of the 4 paragraph criteria.

    Args:
        scores: dict mapping criterion name to integer score (0-5).
                Expected keys: flow, structural_integrity,
                argumentative_strength, section_function_alignment.

    Returns:
        Mean score rounded to 1 decimal place.

    Raises:
        ValueError: If scores dict is empty.
    """
    if not scores:
        raise ValueError("scores dict must not be empty")
    return round(sum(scores.values()) / len(scores), 1)


def compute_sentence_aggregate(
    scores: dict[str, int], weights: dict[str, float]
) -> float:
    """Compute the weighted mean of the 4 sentence criteria.

    Args:
        scores: dict mapping criterion name to integer score (0-5).
        weights: dict mapping criterion name to float weight (should sum to 1.0).

    Returns:
        Weighted mean score rounded to 2 decimal places.

    Raises:
        ValueError: If scores and weights have mismatched keys.
    """
    if set(scores.keys()) != set(weights.keys()):
        raise ValueError(
            f"Mismatched keys: scores={set(scores.keys())}, "
            f"weights={set(weights.keys())}"
        )
    weighted_sum = sum(scores[k] * weights[k] for k in scores)
    return round(weighted_sum, 2)


# ── Config Loading ───────────────────────────────────────────────────


def get_weights_for_section(section_type: Union[str, SectionType]) -> dict[str, float]:
    """Load the dynamic weight profile for a given section type.

    Args:
        section_type: Section type string or SectionType enum value.

    Returns:
        Dict mapping criterion name to weight (floats summing to 1.0).

    Raises:
        KeyError: If section_type is not found in weights.yaml.
    """
    key = _normalize_section_type(section_type)
    config = _get_weights_config()
    if key not in config:
        raise KeyError(
            f"No weight profile for section type '{key}'. "
            f"Available: {list(config.keys())}"
        )
    return dict(config[key])


def get_rubric_for_section(section_type: Union[str, SectionType]) -> dict:
    """Load the rubric criteria for a given section type.

    Args:
        section_type: Section type string or SectionType enum value.

    Returns:
        Dict with 'paragraph_criteria' and 'sentence_criteria' sub-dicts,
        each containing the full rubric descriptors for scoring.

    Raises:
        KeyError: If section_type is not found in rubric.yaml.
    """
    key = _normalize_section_type(section_type)
    config = _get_rubric_config()
    sections = config.get("sections", {})
    if key not in sections:
        raise KeyError(
            f"No rubric for section type '{key}'. "
            f"Available: {list(sections.keys())}"
        )
    return dict(sections[key])


# ── Convergence Logic ────────────────────────────────────────────────


def is_optimal(
    grades: list[Union[ParagraphGrade, SentenceGrade]],
) -> bool:
    """Check whether all grades meet the optimal threshold (all criteria >= 4).

    Args:
        grades: List of ParagraphGrade and/or SentenceGrade objects.

    Returns:
        True if every criterion of every grade is >= OPTIMAL_THRESHOLD.
        Returns True for an empty list (vacuously true).
    """
    return all(grade.is_optimal for grade in grades)


def detect_plateau(
    history: list[IterationRecord], window: int = 2
) -> bool:
    """Detect whether scores have plateaued (no improvement for `window` rounds).

    A plateau is detected when the last `window` iterations show no
    decrease in items_below_threshold compared to the iteration before
    the window.

    Args:
        history: List of IterationRecord objects in chronological order.
        window: Number of consecutive rounds without improvement to
                trigger plateau detection. Default is 2.

    Returns:
        True if a plateau is detected. False if history is too short
        or improvement is still occurring.
    """
    if len(history) < window + 1:
        return False

    # Compare the last `window` records against the record just before them
    baseline = history[-(window + 1)].items_below_threshold
    recent = history[-window:]

    # Plateau = none of the recent iterations improved over the baseline
    return all(r.items_below_threshold >= baseline for r in recent)


def get_below_threshold(
    paragraph_grades: list[ParagraphGrade],
    sentence_grades: list[SentenceGrade],
) -> list[str]:
    """Return IDs of all items with any criterion scoring below the optimal threshold.

    Args:
        paragraph_grades: List of ParagraphGrade objects.
        sentence_grades: List of SentenceGrade objects.

    Returns:
        List of paragraph_id and sentence_id strings for items that
        have at least one criterion < OPTIMAL_THRESHOLD.
    """
    below: list[str] = []

    for pg in paragraph_grades:
        if any(v < OPTIMAL_THRESHOLD for v in pg.scores.values()):
            below.append(pg.paragraph_id)

    for sg in sentence_grades:
        if any(v < OPTIMAL_THRESHOLD for v in sg.scores.values()):
            below.append(sg.sentence_id)

    return below


# ── Phrasebank Loading ───────────────────────────────────────────────


def load_phrasebank_patterns(section_type: Union[str, SectionType]) -> str:
    """Load and concatenate relevant Academic Phrasebank .md content for a section type.

    Reads phrasebank_index.yaml to determine which .md files are relevant
    (both primary and supporting), then concatenates their content.

    Args:
        section_type: Section type string or SectionType enum value.

    Returns:
        Concatenated string of all relevant Phrasebank .md file contents,
        separated by section headers. Returns empty string if no files found.
    """
    key = _normalize_section_type(section_type)
    index = _get_phrasebank_index()

    section_config = index.get("section_phrasebank", {}).get(key, {})
    universal_files = index.get("universal", [])

    # Collect all relevant filenames: primary first, then supporting, then universal
    primary_files = section_config.get("primary", [])
    supporting_files = section_config.get("supporting", [])

    # Deduplicate while preserving order
    all_files: list[str] = []
    seen: set[str] = set()
    for f in primary_files + supporting_files + universal_files:
        if f not in seen:
            all_files.append(f)
            seen.add(f)

    # Read and concatenate
    phrasebank_dir = _REFERENCE_DIR / "phrasebank"
    parts: list[str] = []

    for filename in all_files:
        filepath = phrasebank_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            parts.append(f"--- {filename} ---\n{content}")

    return "\n\n".join(parts)
