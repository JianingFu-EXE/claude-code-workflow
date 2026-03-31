# Search Workflow

Use this reference during Phase 2.

## Core Rule

Search at the leaf subchapter level. Each leaf should have its own keyword family, synonym set, exclusion terms, and source-quality expectations.

## Search Orchestration

After structure approval:

1. Build a query sheet with one row per leaf subchapter.
2. Split the retrieval work by source family.
3. Keep the same subchapter IDs and logging format across sources.

If the user's request explicitly allows subagents or parallel agent work:

- run ScienceDirect/Elsevier and IEEE Xplore as parallel workstreams
- give each workstream the approved structure, the quality rubric, and the same output schema

If explicit delegation permission is absent:

- keep the same workstreams
- run them locally or sequentially

## Query Construction

Each subchapter query should include:

- the exact subchapter label
- 3 to 8 domain synonyms
- method or technology terms when applicable
- one exclusion clause for nearby but irrelevant topics
- optional time, geography, or sector filters when the structure calls for them

Avoid:

- field-wide umbrella terms without leaf-level qualifiers
- mixing multiple subchapters into one search string
- collecting records before the structure is stable

## Quality Filter

Prioritize selection in this order:

1. JCR Tier 1 journals, or JCR Q1 if Tier 1 is not formally used in the field
2. Important recurring reports such as IEA and IRENA when relevant
3. Strong peer-reviewed journals, major conferences, and standards documents
4. Other grey literature only when it adds unique evidence

Use these Zotero quality categories:

- `Top Tier`
- `Mid Tier`
- `Grey Literature/Reports`

Recommended mapping:

- `Top Tier`: JCR Tier 1 or Q1 journals; flagship reports with field-defining value
- `Mid Tier`: solid peer-reviewed journals, conferences, and standards that are not top-tier anchors
- `Grey Literature/Reports`: institutional reports, white papers, market studies, and other non-peer-reviewed sources

## Search Log Template

Track at least:

- subchapter
- source
- query string
- filters used
- result count
- selected items
- rejected items
- short reason for each kept item

## Blockers

Never imply live API retrieval happened if credentials, network access, or tool support are missing. State the blocker explicitly and ask for the minimum missing input needed to continue.
