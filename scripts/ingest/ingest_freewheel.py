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

    entries = _streaming_hub_entries(rows)
    _assert_meaningful_names(entries)

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


def _streaming_hub_entries(rows: list[dict]) -> list[dict]:
    name_col = next(
        (key for key in rows[0] if key.lower() in ("category name", "name", "hub name", "category")),
        None,
    )
    if name_col is None:
        raise ValueError(f"Could not identify FreeWheel Streaming Hub name column. Columns: {list(rows[0])}")

    tier_col = next((key for key in rows[0] if key.lower() == "tier"), None)
    tier_path_cols = [
        key
        for key in rows[0]
        if key.lower().startswith("tier ") and key.lower() != "tier"
    ]

    active_id_by_depth: dict[int, str] = {}
    active_path_by_depth: dict[int, str] = {}
    seen_id_counts: dict[str, int] = {}
    entries = []

    for row in rows:
        source_id = row.get("ID", "").strip()
        name = row.get(name_col, "").strip()
        if not source_id or not name:
            continue
        seen_id_counts[source_id] = seen_id_counts.get(source_id, 0) + 1
        freewheel_id = source_id if seen_id_counts[source_id] == 1 else f"{source_id}_{seen_id_counts[source_id]}"

        depth = _tier_depth(row.get(tier_col, "")) if tier_col else None
        if depth is None:
            tier_vals = [row.get(col, "").strip() for col in tier_path_cols if row.get(col, "").strip()]
            parent_id = None
            full_path = " > ".join(tier_vals) if tier_vals else name
        else:
            parent_id = active_id_by_depth.get(depth - 1) if depth > 1 else None
            parent_path = active_path_by_depth.get(depth - 1)
            full_path = f"{parent_path} > {name}" if parent_path else name
            active_id_by_depth[depth] = freewheel_id
            active_path_by_depth[depth] = full_path
            for existing_depth in list(active_id_by_depth):
                if existing_depth > depth:
                    active_id_by_depth.pop(existing_depth, None)
                    active_path_by_depth.pop(existing_depth, None)

        entries.append(
            {
                "id": freewheel_id,
                "parent_id": parent_id,
                "name": name,
                "full_path": full_path,
            }
        )
    return entries


def _tier_depth(value: str) -> int | None:
    parts = value.strip().split()
    if len(parts) == 2 and parts[0].lower() == "tier" and parts[1].isdigit():
        return int(parts[1])
    return None


def _assert_meaningful_names(entries: list[dict]) -> None:
    if not entries:
        return
    numeric_name_count = sum(1 for entry in entries if entry["name"] == entry["id"])
    if numeric_name_count / len(entries) > 0.05:
        raise ValueError(
            "Parsed FreeWheel content taxonomy has too many numeric names "
            f"({numeric_name_count}/{len(entries)}); check Streaming Hub column detection"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest FreeWheel taxonomies")
    parser.add_argument("--type", choices=["ad_product", "content"], dest="taxonomy_type")
    parser.add_argument(
        "--fail-on-change",
        action="store_true",
        help="Exit 1 when taxonomy data changed; default exits 0 unless an error occurs.",
    )
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
    if any_changed and args.fail_on_change:
        sys.exit(1)


if __name__ == "__main__":
    main()
