import json
import os
import sys
from datetime import datetime, timezone


def invert(canonical: dict) -> dict:
    meta = canonical["metadata"]

    reverse_index: dict[str, dict] = {}

    for entry in canonical["entries"]:
        for target in entry["targets"]:
            tid = target["target_id"]
            if tid not in reverse_index:
                reverse_index[tid] = {
                    "source_id": tid,
                    "source_name": target["target_path"].split(" > ")[-1],
                    "source_path": target["target_path"],
                    "targets": [],
                }
            reverse_index[tid]["targets"].append({
                "target_id": entry["source_id"],
                "target_path": entry["source_path"],
                "confidence": target["confidence"],
                "match_type": target["match_type"],
                "notes": target.get("notes", ""),
            })

    reverse_entries = list(reverse_index.values())
    mapped = sum(1 for e in reverse_entries if e["targets"])
    canonical_folder = (
        f"{meta['source_provider']}_{meta['source_version']}"
        f"__{meta['target_provider']}_{meta['target_version']}"
    )
    now = datetime.now(timezone.utc)

    return {
        "metadata": {
            "source_provider": meta["target_provider"],
            "source_version": meta["target_version"],
            "target_provider": meta["source_provider"],
            "target_version": meta["source_version"],
            "taxonomy_type": meta["taxonomy_type"],
            "canonical": False,
            "derived_from": canonical_folder,
            "mapping_version": meta["mapping_version"],
            "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generated_by": "invert_mapping.py",
            "total_source_entries": len(reverse_entries),
            "mapped_entries": mapped,
            "unmapped_entries": len(reverse_entries) - mapped,
        },
        "entries": reverse_entries,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/invert_mapping.py <canonical_mapping.json> <output_mapping.json>")
        sys.exit(1)

    canonical_path, output_path = sys.argv[1], sys.argv[2]
    with open(canonical_path) as f:
        canonical = json.load(f)

    reverse = invert(canonical)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(reverse, f, indent=2)

    print(f"Written {len(reverse['entries'])} reverse entries to {output_path}")
