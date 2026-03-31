---
name: elsevier-zotero-import
description: Search Elsevier/ScienceDirect and add matching papers to Zotero. Use when a user asks to find papers in ScienceDirect or Elsevier and import them into Zotero, especially for bulk additions based on a natural-language description or boolean query.
---

# Elsevier Zotero Import

## Overview
Turn a user prompt into an Elsevier search (Scopus by default), fetch results, and create Zotero items for all matching papers.

## Workflow

### 1) Translate the prompt into a ScienceDirect query
- Prefer the user's words directly as the `query` value.
- If the user includes boolean logic, keep it intact (e.g., `"heart attack" AND text(liver)`).
- If the user wants a broad import, ask for a reasonable cap (`--max-results`) to avoid huge imports or API quota issues.

### 2) Ensure environment variables are set (do not hardcode keys)
- `ELSEVIER_API_KEY` (required)
- `ELSEVIER_API_BASE_URL` (optional; default is the official ScienceDirect search endpoint)
- `ZOTERO_LOCAL=true` (required for local Zotero)
- `ZOTERO_LIBRARY_ID` (optional; defaults to `0` for local)
- `ZOTERO_LIBRARY_TYPE` (optional; default `user`)

Example:
```bash
export ELSEVIER_API_KEY="YOUR_KEY"
export ZOTERO_LOCAL=true
```

### 3) Run the import script
Use `scripts/import_sciencedirect_to_zotero.py`.
Default search source is `scopus`. Use `--source sciencedirect` only if the key is authorized for ScienceDirect Search.
Use `--date-collection` to create a collection named by today’s date and add items to it.
Use `--collection-name` to create/use a specific collection name.
Use `--fetch-abstracts` to fill missing abstracts via the Scopus Abstract API.
Use `--classify` to add items into subcollections (grid-forming, grid-following, reinforcement-learning, wind).

Common patterns:
```bash
python scripts/import_sciencedirect_to_zotero.py \
  --query 'deep learning AND medical imaging' \
  --api-key 'YOUR_KEY' \
  --max-results 100 \
  --tag elsevier-import
```

If you want to skip duplicates by DOI:
```bash
python scripts/import_sciencedirect_to_zotero.py \
  --query 'graph neural networks' \
  --api-key 'YOUR_KEY' \
  --skip-existing
```

### 4) Confirm results and report summary
- Summarize how many items were created, skipped, or failed.
- If the API returns zero results, suggest query refinements or a narrower field.

## Output Expectations
- Add **all matching papers** to Zotero unless the user asks to filter or cap results.
- Prefer `journalArticle` item type.
- Capture DOI, URL, journal, date, volume/issue/pages when available.
- Store extra metadata (e.g., EID/PII) in the `extra` field.
- Apply a tag (default: `elsevier-import`) unless the user specifies otherwise.

## Resources

### scripts/
- `import_sciencedirect_to_zotero.py`: Search ScienceDirect and create Zotero items in bulk.
