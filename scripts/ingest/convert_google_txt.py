import json
import os
import re
import urllib.request
from datetime import datetime, timezone

SOURCE_URL = "https://www.google.com/basepages/producttype/taxonomy.en-US.txt"
OUT_PATH = "taxonomies/ad_product/google/latest/taxonomy.json"


def slugify(path: str) -> str:
    parts = path.split(" > ")
    slug_parts = []
    for part in parts:
        slug = part.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        slug_parts.append(slug)
    return "__".join(slug_parts)


def convert() -> dict:
    with urllib.request.urlopen(SOURCE_URL) as resp:
        content = resp.read().decode("utf-8")

    entries = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        full_path = line
        slug_id = slugify(full_path)
        name = full_path.split(" > ")[-1]

        parts = full_path.split(" > ")
        parent_path = " > ".join(parts[:-1]) if len(parts) > 1 else None
        parent_id = slugify(parent_path) if parent_path else None

        entries.append({
            "id": slug_id,
            "parent_id": parent_id,
            "name": name,
            "full_path": full_path,
        })

    now = datetime.now(timezone.utc)
    return {
        "metadata": {
            "provider": "google",
            "taxonomy_type": "ad_product",
            "version": "latest",
            "snapshot_date": now.strftime("%Y-%m-%d"),
            "source_url": SOURCE_URL,
            "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "entries": entries,
    }


if __name__ == "__main__":
    data = convert()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Written {len(data['entries'])} entries to {OUT_PATH}")
