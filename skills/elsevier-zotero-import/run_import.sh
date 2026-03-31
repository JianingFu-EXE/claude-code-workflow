#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/scripts/import_sciencedirect_to_zotero.py"

CONFIG_FILE="$HOME/.config/elsevier-zotero-import.env"
if [[ -f "$CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

if [[ -z "${ELSEVIER_API_KEY:-}" ]]; then
  read -r -p "Elsevier API key: " ELSEVIER_API_KEY
fi

if [[ -z "${ZOTERO_LIBRARY_ID:-}" ]]; then
  read -r -p "Zotero library ID (user id): " ZOTERO_LIBRARY_ID
fi

if [[ -z "${ZOTERO_LIBRARY_TYPE:-}" ]]; then
  read -r -p "Zotero library type (user/group) [user]: " ZOTERO_LIBRARY_TYPE
  ZOTERO_LIBRARY_TYPE=${ZOTERO_LIBRARY_TYPE:-user}
fi

if [[ -z "${ZOTERO_API_KEY:-}" ]]; then
  read -r -p "Zotero API key: " ZOTERO_API_KEY
fi

read -r -p "Query: " QUERY
read -r -p "Max results [50]: " MAX_RESULTS
MAX_RESULTS=${MAX_RESULTS:-50}

read -r -p "Add date collection? (y/N): " DATE_COLLECTION
read -r -p "Classify into subcollections? (y/N): " CLASSIFY

ARGS=(
  --api-key "$ELSEVIER_API_KEY"
  --zotero-library-id "$ZOTERO_LIBRARY_ID"
  --zotero-library-type "$ZOTERO_LIBRARY_TYPE"
  --zotero-api-key "$ZOTERO_API_KEY"
  --query "$QUERY"
  --max-results "$MAX_RESULTS"
  --tag elsevier-import
)

if [[ "$DATE_COLLECTION" =~ ^[Yy]$ ]]; then
  ARGS+=(--date-collection)
fi

if [[ "$CLASSIFY" =~ ^[Yy]$ ]]; then
  ARGS+=(--classify)
fi

exec python "$PY_SCRIPT" "${ARGS[@]}"
