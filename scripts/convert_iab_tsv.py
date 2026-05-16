import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

SOURCES = {
    "v1.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%201.0.tsv",
    "v1.1": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%201.1.tsv",
    "v2.0": "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%202.0.tsv",
}


def convert(version: str) -> dict:
    url = SOURCES[version]
    with urllib.request.urlopen(url) as resp:
        content = resp.read().decode("utf-8")

    reader = csv.DictReader(content.splitlines(), delimiter="\t")
    tier_cols = [col for col in reader.fieldnames if col.startswith("Tier ")]

    entries = []
    seen_ids: dict[str, int] = {}
    for row in reader:
        uid = row.get("Unique ID", "").strip()
        parent_id = row.get("Parent ID", "").strip() or None
        name = row.get("Name", "").strip()
        if not uid or not name:
            continue

        # Deduplicate IDs from source data quality issues (e.g. IAB v1.0 has duplicate ID 51)
        if uid in seen_ids:
            seen_ids[uid] += 1
            uid = f"{uid}_{seen_ids[uid]}"
        else:
            seen_ids[uid] = 1

        path_parts = [row.get(col, "").strip() for col in tier_cols]
        path_parts = [p for p in path_parts if p]
        full_path = " > ".join(path_parts)

        entries.append({
            "id": uid,
            "parent_id": parent_id,
            "name": name,
            "full_path": full_path,
        })

    now = datetime.now(timezone.utc)
    return {
        "metadata": {
            "provider": "iab",
            "taxonomy_type": "ad_product",
            "version": version,
            "snapshot_date": now.strftime("%Y-%m-%d"),
            "source_url": url,
            "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "entries": entries,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in SOURCES:
        print(f"Usage: python scripts/convert_iab_tsv.py <version>")
        print(f"  versions: {', '.join(SOURCES)}")
        sys.exit(1)

    version = sys.argv[1]
    data = convert(version)
    out_path = f"taxonomies/ad_product/iab/{version}/taxonomy.json"

    os.makedirs(f"taxonomies/ad_product/iab/{version}", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Written {len(data['entries'])} entries to {out_path}")
