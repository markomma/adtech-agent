"""Ingest Xandr brand and content category taxonomies."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import REPO_ROOT, detect_changes, fetch_url, parse_markdown_table, register_taxonomy, write_taxonomy

AD_PRODUCT_MD_URL = (
    "https://raw.githubusercontent.com/MicrosoftDocs/xandr-docs/main"
    "/xandr-docs/bidders/iab-content-taxonomy-support.md"
)
CONTENT_MD_URL = (
    "https://raw.githubusercontent.com/MicrosoftDocs/xandr-docs/main"
    "/xandr-docs/monetize/content-categories.md"
)
MIN_AD_PRODUCT = 50
MIN_CONTENT = 20


def ingest_ad_product(repo_root: Path = REPO_ROOT) -> bool:
    """Parse Xandr IAB support markdown into a brand category taxonomy."""
    markdown = fetch_url(AD_PRODUCT_MD_URL)
    rows = parse_markdown_table(markdown)
    columns = rows[0] if rows else {}
    id_col = next((key for key in columns if "id" in key.lower() and "iab" not in key.lower()), None)
    name_col = next((key for key in columns if "category" in key.lower() or "name" in key.lower()), None)
    if not id_col or not name_col:
        raise ValueError(f"Could not identify ID/name columns in Xandr markdown. Columns: {list(columns)}")

    entries = []
    seen_ids: set[str] = set()
    for row in rows:
        xandr_id = row.get(id_col, "").strip()
        name = row.get(name_col, "").strip()
        if not xandr_id or not name or xandr_id in seen_ids:
            continue
        try:
            int(xandr_id)
        except ValueError:
            continue
        seen_ids.add(xandr_id)
        entries.append({"id": xandr_id, "parent_id": None, "name": name, "full_path": name})

    if len(entries) < MIN_AD_PRODUCT:
        raise ValueError(f"Expected >= {MIN_AD_PRODUCT} Xandr brand category entries, got {len(entries)}")

    now = datetime.now(timezone.utc)
    metadata = {
        "provider": "xandr",
        "taxonomy_type": "ad_product",
        "version": "latest",
        "snapshot_date": now.strftime("%Y-%m-%d"),
        "source_url": AD_PRODUCT_MD_URL,
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    data = {"metadata": metadata, "entries": entries}
    out_path = repo_root / "taxonomies" / "ad_product" / "xandr" / "latest" / "taxonomy.json"
    changed = detect_changes(data, out_path)
    if changed:
        write_taxonomy(metadata, entries, out_path)

    index_path = repo_root / "index.json"
    if index_path.exists():
        register_taxonomy(
            index_path,
            {
                "provider": "xandr",
                "taxonomy_type": "ad_product",
                "version": "latest",
                "path": str(out_path.relative_to(repo_root)),
                "entry_count": len(entries),
            },
        )

    return changed


def ingest_content(repo_root: Path = REPO_ROOT) -> bool:
    """Parse Xandr Universal Content Categories from GitHub markdown."""
    markdown = fetch_url(CONTENT_MD_URL)
    rows = parse_markdown_table(markdown)
    columns = rows[0] if rows else {}
    top_col = next((key for key in columns if "top-level" in key.lower()), None)
    second_col = next((key for key in columns if "second-level" in key.lower()), None)
    if not top_col or not second_col:
        raise ValueError(f"Could not identify columns in Xandr content markdown. Columns: {list(columns)}")

    entries = []
    seen_ids: set[str] = set()
    for row in rows:
        top_name = row.get(top_col, "").strip()
        if not top_name:
            continue
        top_id = _slugify(top_name)
        if top_id not in seen_ids:
            entries.append({"id": top_id, "parent_id": None, "name": top_name, "full_path": top_name})
            seen_ids.add(top_id)

        second_level = row.get(second_col, "")
        for child_name in [name.strip() for name in second_level.split(",") if name.strip()]:
            child_id = f"{top_id}/{_slugify(child_name)}"
            if child_id in seen_ids:
                continue
            entries.append(
                {
                    "id": child_id,
                    "parent_id": top_id,
                    "name": child_name,
                    "full_path": f"{top_name} > {child_name}",
                }
            )
            seen_ids.add(child_id)

    if len(entries) < MIN_CONTENT:
        raise ValueError(f"Expected >= {MIN_CONTENT} Xandr content category entries, got {len(entries)}")

    now = datetime.now(timezone.utc)
    metadata = {
        "provider": "xandr",
        "taxonomy_type": "content",
        "version": "latest",
        "snapshot_date": now.strftime("%Y-%m-%d"),
        "source_url": CONTENT_MD_URL,
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    data = {"metadata": metadata, "entries": entries}
    out_path = repo_root / "taxonomies" / "content" / "xandr" / "latest" / "taxonomy.json"
    changed = detect_changes(data, out_path)
    if changed:
        write_taxonomy(metadata, entries, out_path)

    index_path = repo_root / "index.json"
    if index_path.exists():
        register_taxonomy(
            index_path,
            {
                "provider": "xandr",
                "taxonomy_type": "content",
                "version": "latest",
                "path": str(out_path.relative_to(repo_root)),
                "entry_count": len(entries),
            },
        )

    return changed


def _slugify(value: str) -> str:
    normalized = value.lower().replace("&", "and")
    chars = [char if char.isalnum() else "-" for char in normalized]
    return "-".join(part for part in "".join(chars).split("-") if part)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Xandr taxonomies")
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
            print(f"{'[CHANGED]' if changed else '[UNCHANGED]'} Xandr {taxonomy_type}")
            any_changed = any_changed or changed
        except Exception as exc:
            errors.append(str(exc))
            print(f"[ERROR] Xandr {taxonomy_type}: {exc}")

    if errors:
        sys.exit(2)
    if any_changed and args.fail_on_change:
        sys.exit(1)


if __name__ == "__main__":
    main()
