import json
import sys

VALID_MATCH_TYPES = {"exact", "semantic", "partial", "approximate", "none"}
TAXONOMY_META_FIELDS = ["provider", "taxonomy_type", "version", "snapshot_date", "source_url", "fetched_at"]
MAPPING_META_FIELDS = ["source_provider", "source_version", "target_provider", "target_version",
                       "taxonomy_type", "canonical", "mapping_version", "generated_at", "generated_by"]


def validate_taxonomy(data: dict) -> list[str]:
    errors = []
    meta = data.get("metadata", {})
    for field in TAXONOMY_META_FIELDS:
        if not meta.get(field) and meta.get(field) != 0:
            errors.append(f"metadata.{field} missing or empty")

    entries = data.get("entries", [])
    if not entries:
        errors.append("entries is empty")

    seen_ids = set()
    for i, entry in enumerate(entries):
        uid = entry.get("id")
        if not uid:
            errors.append(f"entries[{i}].id missing")
        elif uid in seen_ids:
            errors.append(f"entries[{i}].id '{uid}' is a duplicate")
        else:
            seen_ids.add(uid)
        if not entry.get("full_path"):
            errors.append(f"entries[{i}].full_path missing")
        if "name" not in entry:
            errors.append(f"entries[{i}].name missing")

    return errors


def validate_mapping(data: dict) -> list[str]:
    errors = []
    meta = data.get("metadata", {})
    for field in MAPPING_META_FIELDS:
        if meta.get(field) is None:
            errors.append(f"metadata.{field} missing")

    if meta.get("canonical") is False and not meta.get("derived_from"):
        errors.append("metadata.derived_from required when canonical=false")

    entries = data.get("entries", [])
    if not entries:
        errors.append("entries is empty")

    for i, entry in enumerate(entries):
        if not entry.get("source_id"):
            errors.append(f"entries[{i}].source_id missing")
        if "targets" not in entry:
            errors.append(f"entries[{i}].targets missing (use [] for no match)")
            continue
        for j, target in enumerate(entry["targets"]):
            if not target.get("target_id"):
                errors.append(f"entries[{i}].targets[{j}].target_id missing")
            if not target.get("target_path"):
                errors.append(f"entries[{i}].targets[{j}].target_path missing")
            conf = target.get("confidence")
            if conf is None:
                errors.append(f"entries[{i}].targets[{j}].confidence missing")
            elif not (0.0 <= conf <= 1.0):
                errors.append(f"entries[{i}].targets[{j}].confidence={conf} out of [0,1]")
            mt = target.get("match_type")
            if mt not in VALID_MATCH_TYPES:
                errors.append(f"entries[{i}].targets[{j}].match_type='{mt}' invalid")

    return errors


def main(path: str):
    with open(path) as f:
        data = json.load(f)

    if "entries" in data and "metadata" in data:
        meta = data["metadata"]
        if "source_provider" in meta:
            errors = validate_mapping(data)
            kind = "mapping"
        else:
            errors = validate_taxonomy(data)
            kind = "taxonomy"
    else:
        print(f"ERROR: Cannot determine file type for {path}")
        sys.exit(1)

    if errors:
        print(f"FAIL [{kind}] {path} — {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        entry_count = len(data["entries"])
        print(f"OK [{kind}] {path} — {entry_count} entries, 0 errors")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate.py <path/to/taxonomy.json or mapping.json>")
        sys.exit(1)
    for path in sys.argv[1:]:
        main(path)
