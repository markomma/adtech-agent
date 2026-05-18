"""Ingest IAB taxonomies from IAB Tech Lab GitHub."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import REPO_ROOT, detect_changes, fetch_url, parse_tsv, register_taxonomy, write_taxonomy

SOURCES = {
    "ad_product": {
        "v1.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%201.0.tsv",
        "v1.1": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%201.1.tsv",
        "v2.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%202.0.tsv",
    },
    "content": {
        "v1.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Content%20Taxonomies/Content%20Taxonomy%201.0.tsv",
        "v2.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Content%20Taxonomies/Content%20Taxonomy%202.0.tsv",
        "v3.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Content%20Taxonomies/Content%20Taxonomy%203.0.tsv",
    },
    "audience": {
        "v1.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Audience%20Taxonomies/Audience%20Taxonomy%201.0.tsv",
        "v1.1": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Audience%20Taxonomies/Audience%20Taxonomy%201.1.tsv",
    },
}

MIN_ENTRIES: dict[tuple[str, str], int] = {
    ("ad_product", "v1.0"): 400,
    ("ad_product", "v1.1"): 400,
    ("ad_product", "v2.0"): 400,
    ("content", "v1.0"): 300,
    ("content", "v2.0"): 300,
    ("content", "v3.0"): 300,
    ("audience", "v1.0"): 100,
    ("audience", "v1.1"): 100,
}


def ingest(taxonomy_type: str, version: str, repo_root: Path = REPO_ROOT) -> bool:
    """Fetch and write one IAB taxonomy. Returns True when file content changed."""
    url = SOURCES[taxonomy_type][version]
    entries = parse_tsv(fetch_url(url))
    floor = MIN_ENTRIES.get((taxonomy_type, version), 10)
    if len(entries) < floor:
        raise ValueError(
            f"Expected >= {floor} entries for IAB {taxonomy_type} {version}, got {len(entries)}"
        )

    now = datetime.now(timezone.utc)
    metadata = {
        "provider": "iab",
        "taxonomy_type": taxonomy_type,
        "version": version,
        "snapshot_date": now.strftime("%Y-%m-%d"),
        "source_url": url,
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    data = {"metadata": metadata, "entries": entries}
    out_path = repo_root / "taxonomies" / taxonomy_type / "iab" / version / "taxonomy.json"
    changed = detect_changes(data, out_path)
    if changed:
        write_taxonomy(metadata, entries, out_path)

    index_path = repo_root / "index.json"
    if index_path.exists():
        register_taxonomy(
            index_path,
            {
                "provider": "iab",
                "taxonomy_type": taxonomy_type,
                "version": version,
                "path": str(out_path.relative_to(repo_root)),
                "entry_count": len(entries),
            },
        )

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest IAB taxonomies")
    parser.add_argument("--type", choices=list(SOURCES), dest="taxonomy_type")
    parser.add_argument("--version")
    args = parser.parse_args()

    types = [args.taxonomy_type] if args.taxonomy_type else list(SOURCES)
    errors: list[str] = []
    any_changed = False

    for taxonomy_type in types:
        versions = [args.version] if args.version else list(SOURCES[taxonomy_type])
        for version in versions:
            try:
                changed = ingest(taxonomy_type, version)
                print(f"{'[CHANGED]' if changed else '[UNCHANGED]'} IAB {taxonomy_type} {version}")
                any_changed = any_changed or changed
            except Exception as exc:
                errors.append(f"IAB {taxonomy_type} {version}: {exc}")
                print(f"[ERROR] IAB {taxonomy_type} {version}: {exc}")

    if errors:
        sys.exit(2)
    if any_changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
