#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from datetime import date
from typing import Any, Dict, List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None

import urllib.parse
import urllib.request


def http_get(url: str, headers: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    if requests:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code >= 400:
            try:
                detail = resp.text[:500]
            except Exception:
                detail = ""
            raise requests.HTTPError(
                f"{resp.status_code} {resp.reason} for url: {resp.url}\\n{detail}",
                response=resp,
            )
        resp.raise_for_status()
        return resp.json()

    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    req = urllib.request.Request(full_url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:  # nosec - controlled URL
        data = resp.read().decode("utf-8")
    return json.loads(data)


def extract_scopus_id(entry: Dict[str, Any]) -> Optional[str]:
    identifier = entry.get("dc:identifier", "")
    if isinstance(identifier, str) and identifier.startswith("SCOPUS_ID:"):
        return identifier.split(":", 1)[1]
    return None


def fetch_scopus_abstract(scopus_id: str, api_key: str) -> Optional[str]:
    url = f"https://api.elsevier.com/content/abstract/scopus_id/{scopus_id}"
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key,
    }
    try:
        data = http_get(url, headers=headers, params={})
    except Exception:
        return None
    core = (data.get("abstracts-retrieval-response") or {}).get("coredata", {})
    abstract = core.get("dc:description")
    if isinstance(abstract, str) and abstract.strip():
        return abstract.strip()
    return None


def normalize_name(name: str) -> Dict[str, str]:
    name = name.strip()
    if not name:
        return {}

    if "," in name:
        last, first = name.split(",", 1)
        return {"firstName": first.strip(), "lastName": last.strip()}

    parts = name.split()
    if len(parts) == 1:
        return {"name": name}

    return {"firstName": " ".join(parts[:-1]), "lastName": parts[-1]}


def parse_creators(entry: Dict[str, Any]) -> List[Dict[str, str]]:
    creators: List[Dict[str, str]] = []

    authors = entry.get("authors")
    if isinstance(authors, list):
        for author in authors:
            if isinstance(author, dict):
                name = author.get("name") or author.get("$", "")
            else:
                name = str(author)
            name_parts = normalize_name(name)
            if name_parts:
                name_parts["creatorType"] = "author"
                creators.append(name_parts)
        if creators:
            return creators

    creators_text = entry.get("dc:creator") or entry.get("author") or ""
    if isinstance(creators_text, str) and creators_text.strip():
        for raw in creators_text.replace("|", ";").split(";"):
            name_parts = normalize_name(raw)
            if name_parts:
                name_parts["creatorType"] = "author"
                creators.append(name_parts)

    return creators


def find_entry_link(entry: Dict[str, Any], ref: str) -> Optional[str]:
    links = entry.get("link") or []
    if isinstance(links, dict):
        links = [links]
    for link in links:
        if isinstance(link, dict) and link.get("@ref") == ref:
            return link.get("@href")
    return None


def build_extra(entry: Dict[str, Any]) -> str:
    lines: List[str] = []
    mappings = [
        ("eid", "EID"),
        ("pii", "PII"),
        ("prism:issn", "ISSN"),
        ("prism:isbn", "ISBN"),
        ("subtype", "Subtype"),
        ("subtypeDescription", "Subtype Description"),
        ("dc:identifier", "Identifier"),
    ]
    for key, label in mappings:
        value = entry.get(key)
        if value:
            lines.append(f"{label}: {value}")
    api_link = find_entry_link(entry, "self")
    if api_link:
        lines.append(f"API Link: {api_link}")
    return "\n".join(lines)


def entry_to_item(entry: Dict[str, Any], tags: List[str], collections: Optional[List[str]] = None) -> Dict[str, Any]:
    title = entry.get("dc:title") or entry.get("title") or "Untitled"
    doi = entry.get("prism:doi", "")
    scopus_link = find_entry_link(entry, "scopus")
    url = scopus_link or entry.get("prism:url", "")
    if doi:
        url = f"https://doi.org/{doi}"

    item: Dict[str, Any] = {
        "itemType": "journalArticle",
        "title": title,
        "creators": parse_creators(entry),
        "publicationTitle": entry.get("prism:publicationName", ""),
        "volume": entry.get("prism:volume", ""),
        "issue": entry.get("prism:issueIdentifier", ""),
        "pages": entry.get("prism:pageRange", ""),
        "date": entry.get("prism:coverDate", "") or entry.get("prism:coverDisplayDate", ""),
        "DOI": doi,
        "url": url,
        "abstractNote": entry.get("dc:description", ""),
    }

    extra = build_extra(entry)
    if extra:
        item["extra"] = extra

    if tags:
        item["tags"] = [{"tag": t} for t in tags]

    if collections:
        item["collections"] = collections

    return item


def get_zotero_client():
    from pyzotero import zotero  # type: ignore

    local = os.getenv("ZOTERO_LOCAL", "").lower() in ["1", "true", "yes"]
    library_id = os.getenv("ZOTERO_LIBRARY_ID") or ("0" if local else None)
    library_type = os.getenv("ZOTERO_LIBRARY_TYPE", "user")
    api_key = os.getenv("ZOTERO_API_KEY")

    if not local and not (library_id and api_key):
        raise SystemExit("Missing ZOTERO_LIBRARY_ID/ZOTERO_API_KEY or set ZOTERO_LOCAL=true")

    return zotero.Zotero(
        library_id=library_id,
        library_type=library_type,
        api_key=api_key,
        local=local,
    )


def zotero_has_doi(zot, doi: str) -> bool:
    if not doi:
        return False
    try:
        results = zot.items(q=doi, qmode="everything", itemType="-attachment", limit=1)
    except Exception:
        results = zot.items(q=doi, qmode="everything", limit=1)
    return bool(results)


def get_collection_key(zot, name: str, parent_key: str | None = None) -> Optional[str]:
    if parent_key:
        collections = zot.collections_sub(parent_key)
    else:
        collections = zot.collections_top()
    for coll in collections:
        data = coll.get("data", {})
        if data.get("name") == name:
            return coll.get("key")
    return None


def ensure_collection(zot, name: str, parent_key: str | None = None) -> str:
    existing = get_collection_key(zot, name, parent_key)
    if existing:
        return existing
    payload = [{"name": name}]
    if parent_key:
        payload[0]["parentCollection"] = parent_key
    created = zot.create_collections(payload)
    successful = created.get("successful", {})
    if successful:
        first = next(iter(successful.values()))
        return first.get("key")
    raise RuntimeError(f"Failed to create collection: {name}")


def classify_subcollections(entry: Dict[str, Any]) -> List[str]:
    text = " ".join(
        [
            str(entry.get("dc:title", "")),
            str(entry.get("dc:description", "")),
        ]
    ).lower()
    categories: List[str] = []
    if "grid forming" in text or "grid-forming" in text:
        categories.append("grid-forming")
    if "grid following" in text or "grid-following" in text:
        categories.append("grid-following")
    if "reinforcement learning" in text or "rl " in f"{text} ":
        categories.append("reinforcement-learning")
    if "wind turbine" in text or "wind power" in text or "wind energy" in text:
        categories.append("wind")
    return categories


def main() -> int:
    parser = argparse.ArgumentParser(description="Import ScienceDirect search results into Zotero")
    parser.add_argument("--query", required=True, help="ScienceDirect boolean query string")
    parser.add_argument("--api-key", help="Elsevier API key (overrides ELSEVIER_API_KEY)")
    parser.add_argument("--base-url", help="Elsevier API base URL (overrides ELSEVIER_API_BASE_URL)")
    parser.add_argument("--source", choices=["scopus", "sciencedirect"], default="scopus", help="Elsevier search source")
    parser.add_argument("--count", type=int, default=25, help="Results per page (10, 25, 50, 100)")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum results to import")
    parser.add_argument("--start", type=int, default=0, help="Start offset")
    parser.add_argument("--tag", action="append", default=["elsevier-import"], help="Tag to apply (can repeat)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip items that already exist (by DOI)")
    parser.add_argument("--dry-run", action="store_true", help="Print items without creating them")
    parser.add_argument("--sleep", type=float, default=0.0, help="Sleep seconds between API pages")
    parser.add_argument("--zotero-local", action="store_true", help="Use local Zotero API (overrides ZOTERO_LOCAL)")
    parser.add_argument("--zotero-library-id", help="Zotero library ID (overrides ZOTERO_LIBRARY_ID)")
    parser.add_argument("--zotero-library-type", choices=["user", "group"], help="Zotero library type")
    parser.add_argument("--zotero-api-key", help="Zotero API key (overrides ZOTERO_API_KEY)")
    parser.add_argument("--date-collection", action="store_true", help="Create a date-named collection and add items")
    parser.add_argument("--collection-name", help="Create/use a specific collection name and add items")
    parser.add_argument("--classify", action="store_true", help="Add items into subcollections by topic")
    parser.add_argument("--fetch-abstracts", action="store_true", help="Fetch missing abstracts from Scopus Abstract API")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("ELSEVIER_API_KEY")
    if not api_key:
        raise SystemExit("Missing ELSEVIER_API_KEY")

    default_url = "https://api.elsevier.com/content/search/scopus"
    if args.source == "sciencedirect":
        default_url = "https://api.elsevier.com/content/search/sciencedirect"

    base_url = args.base_url or os.getenv("ELSEVIER_API_BASE_URL", default_url)

    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key,
    }

    if args.zotero_local:
        os.environ["ZOTERO_LOCAL"] = "true"
    elif args.zotero_library_id or args.zotero_api_key or args.zotero_library_type:
        os.environ["ZOTERO_LOCAL"] = "false"
    if args.zotero_library_id:
        os.environ["ZOTERO_LIBRARY_ID"] = args.zotero_library_id
    if args.zotero_library_type:
        os.environ["ZOTERO_LIBRARY_TYPE"] = args.zotero_library_type
    if args.zotero_api_key:
        os.environ["ZOTERO_API_KEY"] = args.zotero_api_key

    zot = get_zotero_client()

    date_collection_key: Optional[str] = None
    subcollection_keys: Dict[str, str] = {}
    if args.collection_name:
        date_collection_key = ensure_collection(zot, args.collection_name, None)
    elif args.date_collection:
        date_name = date.today().isoformat()
        date_collection_key = ensure_collection(zot, date_name, None)

    created = 0
    skipped = 0
    failed = 0

    start = args.start

    while start < args.max_results:
        params = {
            "query": args.query,
            "count": args.count,
            "start": start,
            "view": "STANDARD",
            "apiKey": api_key,
        }

        payload = http_get(base_url, headers=headers, params=params)
        search_results = payload.get("search-results", {})
        entries = search_results.get("entry", [])

        if isinstance(entries, dict):
            entries = [entries]

        if not entries:
            break

        for entry in entries:
            if created + skipped + failed >= args.max_results:
                break

            if args.fetch_abstracts and not entry.get("dc:description"):
                scopus_id = extract_scopus_id(entry)
                if scopus_id:
                    abstract = fetch_scopus_abstract(scopus_id, api_key)
                    if abstract:
                        entry["dc:description"] = abstract

            collections: List[str] = []
            if date_collection_key:
                collections.append(date_collection_key)
                if args.classify:
                    for name in classify_subcollections(entry):
                        if name not in subcollection_keys:
                            subcollection_keys[name] = ensure_collection(zot, name, date_collection_key)
                        collections.append(subcollection_keys[name])

            item = entry_to_item(entry, tags=args.tag, collections=collections or None)
            doi = item.get("DOI") or ""

            if args.skip_existing and zotero_has_doi(zot, doi):
                skipped += 1
                continue

            if args.dry_run:
                title = item.get("title", "Untitled")
                print(f"[DRY-RUN] {title}")
                created += 1
                continue

            try:
                result = zot.create_items([item])
                if result.get("successful"):
                    created += 1
                else:
                    failed += 1
            except Exception as exc:
                failed += 1
                print(f"Failed to create item: {exc}")

        start += args.count
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Done. created={created} skipped={skipped} failed={failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
