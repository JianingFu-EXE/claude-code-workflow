---
name: research-ops-subchapter-search
description: Design and run a research-operations workflow that maps a field to subchapter resolution, validates or proposes literature-review structures, plans source-specific searches, and organizes results into Zotero collections with quality tiers. Use when Codex needs to scope a research field, turn a topic or draft outline into searchable subchapters, search ScienceDirect/Elsevier and IEEE Xplore systematically, prioritize top-tier journals and major annual reports, or build a Zotero folder architecture for a review.
---

# Research Ops Subchapter Search

## Overview

Use this skill to turn a research topic, draft outline, or seed bibliography into three outputs: an approved subchapter map, a source-aware literature search plan, and a Zotero filing hierarchy.
Lock the structure before searching. Search at the leaf subchapter level, not at the chapter or field level.

## Workflow

1. Clarify the research topic, scope limits, and any supplied outline or source packet.
2. Validate the user's structure or generate three alternatives with justification. Use [references/structure-schemes.md](references/structure-schemes.md).
3. Wait for structure approval unless the user explicitly asks for a recommended default.
4. Build the subchapter-level search plan. Use [references/search-workflow.md](references/search-workflow.md).
5. Create the Zotero collection hierarchy and filing rules. Use [references/zotero-filing.md](references/zotero-filing.md).
6. Return the structure choice, search log, source-quality decisions, and Zotero architecture.

## Phase 1: Structure Approval

If the user provides a structure, validate it for:

- coverage of the field
- separation between sibling subchapters
- queryability at the leaf level
- fitness for Zotero filing
- balance between conceptual, methodological, and evidence-oriented branches when the field requires all three

If the user does not provide a structure, generate exactly three distinct schemes. Make them materially different, such as chronological, methodological, and problem-scale, unless the field clearly calls for another trio.

For each scheme:

- write a three-sentence technical justification
- anchor the justification in the user's brief, supplied outline, seed papers, or other provided artifacts
- if the prompt references a “provided” source but none exists, state that no source artifact was supplied and justify from the topic definition alone
- expose enough leaf subchapters that each one can carry its own keyword family and Zotero collection

Always include a comparison table for the three schemes before asking for approval.

## Phase 2: Search Execution

Only start retrieval after the structure is approved.

Map every query to a specific leaf subchapter. Do not run generic field-level searches unless the user explicitly asks for scoping only.

When the user's request explicitly allows subagents, delegation, or parallel agent work:

- spawn a Search Subagent for ScienceDirect/Elsevier
- spawn a Search Subagent for IEEE Xplore
- run them in parallel with the same subchapter map, source-quality rubric, and logging format

When explicit delegation permission is absent, keep the same source split but perform the work locally instead of spawning agents.

Never claim API retrieval succeeded when access or credentials are missing. State the exact blocker and continue only with an approved fallback path.

Apply the quality filter during selection, not after the full dump. Prioritize:

- JCR Tier 1 journals, or JCR Q1 when the field does not publish a separate tier label
- major recurring reports such as IEA and IRENA when relevant to the topic
- technically significant annual or flagship reports before lower-value grey literature

## Phase 3: Zotero Filing

Create a nested Zotero collection structure that mirrors the approved subchapters.

For each subchapter, create:

- a main collection named after the subchapter
- three quality subcollections named `Top Tier`, `Mid Tier`, and `Grey Literature/Reports`

File every accepted item in two places:

- the main subchapter collection
- the matching quality subcollection under that same subchapter

Do not collapse the dual-filing rule into tags only. The collection hierarchy must make both topical browsing and quality-filtered browsing obvious.

## Output Expectations

Return concise, operational artifacts:

- the approved or proposed structure
- the comparison table when multiple schemes are presented
- a subchapter-to-query mapping
- a search log by source and subchapter
- the accepted-source list with quality category
- the Zotero hierarchy to create
- blockers, assumptions, and any access gaps
