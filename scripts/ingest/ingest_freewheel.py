"""Ingest FreeWheel MRM Industry IDs and Streaming Hub IDs."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import REPO_ROOT, detect_changes, fetch_url, parse_html_table, register_taxonomy, write_taxonomy

PREBID_URL = "https://cdn.jsdelivr.net/gh/prebid/category-mapping-file@1/freewheel-mapping.json"
API_DOCS_URL = "https://api-docs.freewheel.tv/publisher/docs/api-resources"
MIN_STREAMING_HUB = 500


def ingest_ad_product(repo_root: Path = REPO_ROOT) -> bool:
    """Extract FreeWheel MRM Industry IDs from Prebid category-mapping-file."""
    raw = json.loads(fetch_url(PREBID_URL))
    seen: dict[str, str] = {}
    for target in raw["mapping"].values():
        freewheel_id = str(target["id"])
        if freewheel_id not in seen:
            seen[freewheel_id] = target["name"]

    entries = sorted(
        [
            {"id": freewheel_id, "parent_id": None, "name": name, "full_path": name}
            for freewheel_id, name in seen.items()
        ],
        key=lambda entry: int(entry["id"]),
    )
    now = datetime.now(timezone.utc)
    metadata = {
        "provider": "freewheel",
        "taxonomy_type": "ad_product",
        "version": "latest",
        "snapshot_date": now.strftime("%Y-%m-%d"),
        "source_url": PREBID_URL,
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    data = {"metadata": metadata, "entries": entries}
    out_path = repo_root / "taxonomies" / "ad_product" / "freewheel" / "latest" / "taxonomy.json"
    changed = detect_changes(data, out_path)
    if changed:
        write_taxonomy(metadata, entries, out_path)

    index_path = repo_root / "index.json"
    if index_path.exists():
        register_taxonomy(
            index_path,
            {
                "provider": "freewheel",
                "taxonomy_type": "ad_product",
                "version": "latest",
                "path": str(out_path.relative_to(repo_root)),
                "entry_count": len(entries),
            },
        )

    return changed


def ingest_content(repo_root: Path = REPO_ROOT) -> bool:
    """Scrape FreeWheel Streaming Hub IDs from API docs."""
    html = fetch_url(API_DOCS_URL)
    rows = parse_html_table(html, "Streaming Hub IDs")
    if len(rows) < MIN_STREAMING_HUB:
        raise ValueError(f"Expected >= {MIN_STREAMING_HUB} Streaming Hub entries, got {len(rows)}")

    tier_cols = [key for key in rows[0] if key.lower().startswith("tier") or key.lower() == "name"]
    entries = []
    for row in rows:
        freewheel_id = row.get("ID", "").strip()
        name_col = next(
            (key for key in row if key.lower() in ("name", "hub name", "category")),
            None,
        )
        name = row.get(name_col, freewheel_id).strip() if name_col else freewheel_id
        tier_vals = [row.get(col, "").strip() for col in tier_cols if row.get(col, "").strip()]
        full_path = " > ".join(tier_vals) if tier_vals else name
        entries.append(
            {
                "id": freewheel_id,
                "parent_id": None,
                "name": name,
                "full_path": full_path,
            }
        )

    now = datetime.now(timezone.utc)
    metadata = {
        "provider": "freewheel",
        "taxonomy_type": "content",
        "version": "latest",
        "snapshot_date": now.strftime("%Y-%m-%d"),
        "source_url": API_DOCS_URL,
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    data = {"metadata": metadata, "entries": entries}
    out_path = repo_root / "taxonomies" / "content" / "freewheel" / "latest" / "taxonomy.json"
    changed = detect_changes(data, out_path)
    if changed:
        write_taxonomy(metadata, entries, out_path)

    index_path = repo_root / "index.json"
    if index_path.exists():
        register_taxonomy(
            index_path,
            {
                "provider": "freewheel",
                "taxonomy_type": "content",
                "version": "latest",
                "path": str(out_path.relative_to(repo_root)),
                "entry_count": len(entries),
            },
        )

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest FreeWheel taxonomies")
    parser.add_argument("--type", choices=["ad_product", "content"], dest="taxonomy_type")
    args = parser.parse_args()

    funcs = {"ad_product": ingest_ad_product, "content": ingest_content}
    targets = [args.taxonomy_type] if args.taxonomy_type else list(funcs)
    errors: list[str] = []
    any_changed = False

    for taxonomy_type in targets:
        try:
            changed = funcs[taxonomy_type]()
            print(f"{'[CHANGED]' if changed else '[UNCHANGED]'} FreeWheel {taxonomy_type}")
            any_changed = any_changed or changed
        except Exception as exc:
            errors.append(str(exc))
            print(f"[ERROR] FreeWheel {taxonomy_type}: {exc}")

    if errors:
        sys.exit(2)
    if any_changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
