# AdTech Taxonomy Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the adtech-taxonomy public repo with IAB Ad Product v1.0 and v2.0 fully mapped to Google Product Type (latest), bidirectionally, with validation and a private self-improving generation skill.

**Architecture:** Python utility scripts convert raw source taxonomies (TSV/TXT) to a canonical JSON schema; a private Claude skill orchestrates LLM-assisted mapping generation in batches, producing canonical `mapping.json` files; a separate inverter script derives the reverse direction. All committed data is validated before committing.

**Tech Stack:** Python 3 (stdlib only — no pip install needed), GitHub CLI (`gh`), Claude Code (for interactive mapping generation via private skill)

---

### Task 1: Scaffold repo structure, .gitignore, README, and CLAUDE.md

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `CLAUDE.md`
- Create: folder placeholders for `taxonomies/`, `mappings/`, `scripts/`, `tools/`

- [ ] **Step 1: Create .gitignore**

```
.claude/
__pycache__/
*.pyc
.DS_Store
```

Write to `.gitignore`.

- [ ] **Step 2: Create folder structure with .gitkeep placeholders**

```bash
mkdir -p taxonomies/ad_product/iab
mkdir -p taxonomies/ad_product/google
mkdir -p taxonomies/audience
mkdir -p taxonomies/content
mkdir -p mappings/ad_product
mkdir -p mappings/audience
mkdir -p mappings/content
mkdir -p scripts
mkdir -p tools
touch taxonomies/audience/.gitkeep
touch taxonomies/content/.gitkeep
touch mappings/audience/.gitkeep
touch mappings/content/.gitkeep
touch tools/.gitkeep
```

- [ ] **Step 3: Create README.md**

```markdown
# adtech-taxonomy

Cross-provider taxonomy mapping for AdTech — maps categories between DSPs, SSPs, and industry bodies (IAB Tech Lab, Google, and others).

## Taxonomy Types

| Type | Description |
|------|-------------|
| `ad_product` | Categories of advertised products |
| `audience` | Audience segment classifications |
| `content` | Content category classifications |

## Structure

```
taxonomies/{taxonomy_type}/{provider}/{version}/taxonomy.json
mappings/{taxonomy_type}/{source}__{target}/mapping.json
```

Provider version conventions:
- IAB Tech Lab: `v1.0`, `v2.0` (immutable snapshots)
- Google: `latest` (single folder, `snapshot_date` in metadata)

## Mappings

Mapping folders use double-underscore to separate source from target:
`iab_v2.0__google_latest` = IAB Ad Product 2.0 → Google Product Type (latest)

Each mapping pair has a **canonical** file (source of truth, indexed by the provider with stable integer IDs) and a **derived** reverse file (auto-generated, never edited directly).

## Discovery

`index.json` at the repo root lists all registered providers, taxonomies, and mappings. LLM agents should read `index.json` first to discover available paths.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/convert_iab_tsv.py` | Fetch IAB TSV → taxonomy.json |
| `scripts/convert_google_txt.py` | Fetch Google TXT → taxonomy.json |
| `scripts/validate.py` | Validate taxonomy.json and mapping.json schemas |
| `scripts/invert_mapping.py` | Generate reverse mapping from canonical |

## Sources

- IAB Tech Lab Taxonomies: https://github.com/InteractiveAdvertisingBureau/Taxonomies
- Google Product Type Taxonomy: https://www.google.com/basepages/producttype/taxonomy.en-US.txt
```

- [ ] **Step 4: Create CLAUDE.md**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mapping Sessions

**At the start of every mapping session:**
1. Read `.claude/skills/adtech-taxonomy-mapper.md` in full before generating any mappings — it contains accumulated few-shot examples and lessons learned that improve generation quality.

**At the end of every mapping session:**
1. Review any entries where confidence scores were adjusted, targets were added, or targets were removed by a human reviewer during this session.
2. Distill 2–3 of the most instructive corrections into new few-shot examples and append them to the `## Few-Shot Examples` section of `.claude/skills/adtech-taxonomy-mapper.md`.
3. If any cross-cutting patterns were observed (e.g., "IAB B2B service entries rarely have Google equivalents"), add them to the `## Lessons Learned` section.
4. Tell the user what was added or changed in the skill file.

## Scripts

Run scripts from the repo root:
```bash
python scripts/convert_iab_tsv.py <version>     # e.g. v2.0
python scripts/convert_google_txt.py
python scripts/validate.py taxonomies/ad_product/iab/v2.0/taxonomy.json
python scripts/validate.py mappings/ad_product/iab_v2.0__google_latest/mapping.json
python scripts/invert_mapping.py mappings/ad_product/iab_v2.0__google_latest/mapping.json \
  mappings/ad_product/google_latest__iab_v2.0/mapping.json
```

## Naming Conventions

- Mapping folders: `{source_provider}_{source_version}__{target_provider}_{target_version}`
- Double underscore separates the two sides; single underscores within each side
- Canonical direction: provider with stable integer IDs (IAB) always first
- Google version is always `latest`; IAB versions are `v1.0`, `v2.0`, etc.

## Adding a New Provider

1. Add a slug entry to `index.json` under `providers`
2. Create `taxonomies/{type}/{provider}/{version}/taxonomy.json` (use `latest/` for unversioned providers)
3. Generate canonical mapping via `.claude/skills/adtech-taxonomy-mapper.md`
4. Run inverter to produce derived reverse
5. Register both mapping folders in `index.json` under `mappings`
```

- [ ] **Step 5: Create the private .claude/skills/ directory**

```bash
mkdir -p .claude/skills
```

Note: `.claude/` is gitignored and will never be committed to the public repo.

- [ ] **Step 6: Commit scaffold**

```bash
git add .gitignore README.md CLAUDE.md taxonomies/ mappings/ scripts/ tools/
git commit -m "feat: scaffold repo structure, CLAUDE.md, and README"
```

Expected: 1 commit, new files listed.

---

### Task 2: IAB TSV converter script

**Files:**
- Create: `scripts/convert_iab_tsv.py`

- [ ] **Step 1: Verify expected TSV structure for both versions**

```bash
curl -s "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%201.0.tsv" | head -3
curl -s "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Ad%20Product%20Taxonomies/Ad%20Product%20Taxonomy%202.0.tsv" | head -3
```

Expected: v1.0 header = `Unique ID\tParent ID\tName\tTier 1\tTier 2\tTier 3\tTier 4\tTier 5`; v2.0 header = `Unique ID\tParent ID\tName\tTier 1\tTier 2\tTier 3`

- [ ] **Step 2: Write scripts/convert_iab_tsv.py**

```python
import csv
import json
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
    for row in reader:
        uid = row.get("Unique ID", "").strip()
        parent_id = row.get("Parent ID", "").strip() or None
        name = row.get("Name", "").strip()
        if not uid or not name:
            continue

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

    import os
    os.makedirs(f"taxonomies/ad_product/iab/{version}", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Written {len(data['entries'])} entries to {out_path}")
```

- [ ] **Step 3: Run dry validation before writing files**

```bash
python -c "
import scripts.convert_iab_tsv as c
data = c.convert('v2.0')
assert data['metadata']['provider'] == 'iab'
assert data['metadata']['version'] == 'v2.0'
assert len(data['entries']) > 100, f'Expected >100 entries, got {len(data[\"entries\"])}'
e = next(x for x in data['entries'] if x['id'] == '1004')
assert e['name'] == 'Beer'
assert e['parent_id'] == '1002'
assert e['full_path'] == 'Alcohol > Beer'
print('v2.0 validation passed:', len(data[\"entries\"]), 'entries')
"
```

Expected: `v2.0 validation passed: 4XX entries`

- [ ] **Step 4: Run for v1.0 dry validation**

```bash
python -c "
import scripts.convert_iab_tsv as c
data = c.convert('v1.0')
assert data['metadata']['version'] == 'v1.0'
assert len(data['entries']) > 50
# v1.0 uses up to 5 tiers
apps_entry = next(x for x in data['entries'] if x['name'] == 'Apps')
assert apps_entry['full_path'] == 'Apps'
print('v1.0 validation passed:', len(data['entries']), 'entries')
"
```

Expected: `v1.0 validation passed: XXX entries`

- [ ] **Step 5: Commit script**

```bash
git add scripts/convert_iab_tsv.py
git commit -m "feat: add IAB TSV to taxonomy.json converter"
```

---

### Task 3: Google TXT converter script

**Files:**
- Create: `scripts/convert_google_txt.py`

- [ ] **Step 1: Verify Google taxonomy format**

```bash
curl -s "https://www.google.com/basepages/producttype/taxonomy.en-US.txt" | head -5
```

Expected: First line is a comment `# ...`, then lines like `Animals & Pet Supplies`, `Animals & Pet Supplies > Live Animals`

- [ ] **Step 2: Write scripts/convert_google_txt.py**

```python
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
```

- [ ] **Step 3: Validate before writing**

```bash
python -c "
import scripts.convert_google_txt as g
data = g.convert()
assert data['metadata']['provider'] == 'google'
assert data['metadata']['version'] == 'latest'
assert len(data['entries']) > 4000, f'Expected >4000 entries, got {len(data[\"entries\"])}'
# Verify slug ID stability
beer_entry = next((x for x in data['entries'] if 'Alcoholic Beverages > Beer' in x['full_path']), None)
assert beer_entry is not None
assert '__' in beer_entry['id'], f'Expected __ separator in id: {beer_entry[\"id\"]}'
# Verify no duplicate IDs
ids = [e['id'] for e in data['entries']]
assert len(ids) == len(set(ids)), 'Duplicate IDs found'
print('Google validation passed:', len(data['entries']), 'entries')
print('Sample beer entry id:', beer_entry['id'])
"
```

Expected: `Google validation passed: XXXX entries` and a sample id like `food-beverages-tobacco__beverages__alcoholic-beverages__beer`

- [ ] **Step 4: Commit script**

```bash
git add scripts/convert_google_txt.py
git commit -m "feat: add Google TXT to taxonomy.json converter"
```

---

### Task 4: Schema validator script

**Files:**
- Create: `scripts/validate.py`

- [ ] **Step 1: Write scripts/validate.py**

```python
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
```

- [ ] **Step 2: Verify validator rejects a bad file**

```bash
python -c "
import json, tempfile, os
bad = {'metadata': {'provider': 'test'}, 'entries': [{'id': '', 'full_path': 'Foo'}]}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(bad, f)
    name = f.name
ret = os.system(f'python scripts/validate.py {name}')
os.unlink(name)
assert ret != 0, 'Expected non-zero exit for invalid file'
print('Rejection test passed')
"
```

Expected: `FAIL [taxonomy]` output and `Rejection test passed`

- [ ] **Step 3: Commit validator**

```bash
git add scripts/validate.py
git commit -m "feat: add taxonomy and mapping schema validator"
```

---

### Task 5: Mapping inverter script

**Files:**
- Create: `scripts/invert_mapping.py`

- [ ] **Step 1: Write scripts/invert_mapping.py**

```python
import json
import os
import sys
from datetime import datetime, timezone


def invert(canonical: dict) -> dict:
    meta = canonical["metadata"]

    # Index: target_id → reverse entry
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
```

- [ ] **Step 2: Validate inverter logic with a synthetic fixture**

```bash
python -c "
import json, scripts.invert_mapping as inv

canonical = {
  'metadata': {
    'source_provider': 'iab', 'source_version': 'v2.0',
    'target_provider': 'google', 'target_version': 'latest',
    'taxonomy_type': 'ad_product', 'canonical': True,
    'derived_from': None, 'mapping_version': '1.0.0',
    'generated_at': '2026-01-01T00:00:00Z', 'generated_by': 'test',
    'total_source_entries': 2, 'mapped_entries': 1, 'unmapped_entries': 1
  },
  'entries': [
    {
      'source_id': '1002', 'source_name': 'Alcohol', 'source_path': 'Alcohol',
      'targets': [
        {'target_id': 'food__beverages__alcohol', 'target_path': 'Food > Beverages > Alcohol',
         'confidence': 0.95, 'match_type': 'semantic', 'notes': 'strong match'}
      ]
    },
    {'source_id': '9999', 'source_name': 'Unmapped', 'source_path': 'Unmapped', 'targets': []}
  ]
}

result = inv.invert(canonical)
assert result['metadata']['source_provider'] == 'google'
assert result['metadata']['target_provider'] == 'iab'
assert result['metadata']['canonical'] == False
assert result['metadata']['derived_from'] == 'iab_v2.0__google_latest'
assert len(result['entries']) == 1  # only entries with targets appear as reverse sources
rev_entry = result['entries'][0]
assert rev_entry['source_id'] == 'food__beverages__alcohol'
assert rev_entry['targets'][0]['target_id'] == '1002'
assert rev_entry['targets'][0]['confidence'] == 0.95
print('Inverter validation passed')
"
```

Expected: `Inverter validation passed`

- [ ] **Step 3: Commit inverter**

```bash
git add scripts/invert_mapping.py
git commit -m "feat: add mapping inverter script"
```

---

### Task 6: Ingest IAB taxonomies

**Files:**
- Create: `taxonomies/ad_product/iab/v2.0/taxonomy.json`
- Create: `taxonomies/ad_product/iab/v1.0/taxonomy.json`

- [ ] **Step 1: Generate IAB v2.0 taxonomy.json**

```bash
python scripts/convert_iab_tsv.py v2.0
```

Expected: `Written 4XX entries to taxonomies/ad_product/iab/v2.0/taxonomy.json`

- [ ] **Step 2: Validate IAB v2.0**

```bash
python scripts/validate.py taxonomies/ad_product/iab/v2.0/taxonomy.json
```

Expected: `OK [taxonomy] taxonomies/ad_product/iab/v2.0/taxonomy.json — 4XX entries, 0 errors`

- [ ] **Step 3: Generate IAB v1.0 taxonomy.json**

```bash
python scripts/convert_iab_tsv.py v1.0
```

Expected: `Written XXX entries to taxonomies/ad_product/iab/v1.0/taxonomy.json`

- [ ] **Step 4: Validate IAB v1.0**

```bash
python scripts/validate.py taxonomies/ad_product/iab/v1.0/taxonomy.json
```

Expected: `OK [taxonomy] taxonomies/ad_product/iab/v1.0/taxonomy.json — XXX entries, 0 errors`

- [ ] **Step 5: Commit taxonomies**

```bash
git add taxonomies/ad_product/iab/
git commit -m "data: ingest IAB Ad Product taxonomy v1.0 and v2.0"
```

---

### Task 7: Ingest Google taxonomy

**Files:**
- Create: `taxonomies/ad_product/google/latest/taxonomy.json`

- [ ] **Step 1: Generate Google latest taxonomy.json**

```bash
python scripts/convert_google_txt.py
```

Expected: `Written XXXX entries to taxonomies/ad_product/google/latest/taxonomy.json`

- [ ] **Step 2: Validate**

```bash
python scripts/validate.py taxonomies/ad_product/google/latest/taxonomy.json
```

Expected: `OK [taxonomy] taxonomies/ad_product/google/latest/taxonomy.json — XXXX entries, 0 errors`

- [ ] **Step 3: Commit**

```bash
git add taxonomies/ad_product/google/
git commit -m "data: ingest Google Product Type taxonomy (latest snapshot)"
```

---

### Task 8: Create private generation skill

**Files:**
- Create: `.claude/skills/adtech-taxonomy-mapper.md` (gitignored)

- [ ] **Step 1: Create .claude/skills/ directory**

```bash
mkdir -p .claude/skills
```

- [ ] **Step 2: Write .claude/skills/adtech-taxonomy-mapper.md**

```markdown
# AdTech Taxonomy Mapper

Private generation skill for mapping AdTech taxonomies. Updated after each mapping session with new few-shot examples and lessons learned.

## Purpose

Generate canonical `mapping.json` files mapping one taxonomy to another using LLM-assisted semantic matching. Process entries in batches of 20-30, parents before children.

## Process

1. Read source taxonomy: `taxonomies/{type}/{provider}/{version}/taxonomy.json`
2. Read target taxonomy: `taxonomies/{type}/{provider}/{version}/taxonomy.json`
3. Load all target entries into context as a lookup reference
4. Map source entries in batches of 25, parents before children
5. For each source entry, produce a targets array with confidence scores and match_type
6. After all batches, assemble the full mapping.json with correct metadata
7. Validate: `python scripts/validate.py mappings/{type}/{pair}/mapping.json`
8. Generate reverse: `python scripts/invert_mapping.py <canonical> <reverse>`
9. Validate reverse: `python scripts/validate.py mappings/{type}/{reverse_pair}/mapping.json`

## Output Schema Per Entry

```json
{
  "source_id": "<id from source taxonomy>",
  "source_name": "<name>",
  "source_path": "<full_path>",
  "targets": [
    {
      "target_id": "<id from target taxonomy>",
      "target_path": "<full_path from target taxonomy>",
      "confidence": 0.0-1.0,
      "match_type": "exact|semantic|partial|approximate|none",
      "notes": "<brief rationale>"
    }
  ]
}
```

Use empty `targets: []` when no reasonable match exists. Never invent target paths — every target_id and target_path must exist verbatim in the target taxonomy.json.

## Match Type Guidelines

- `exact` (0.9–1.0): Term-for-term name match
- `semantic` (0.7–0.95): Same concept, different terminology  
- `partial` (0.5–0.75): One side is broader or narrower
- `approximate` (0.3–0.6): Related but imperfect
- Empty targets: No reasonable match

## Metadata Template

```json
{
  "source_provider": "",
  "source_version": "",
  "target_provider": "",
  "target_version": "",
  "taxonomy_type": "ad_product",
  "canonical": true,
  "derived_from": null,
  "mapping_version": "1.0.0",
  "generated_at": "<ISO8601>",
  "generated_by": "llm-assisted",
  "total_source_entries": 0,
  "mapped_entries": 0,
  "unmapped_entries": 0
}
```

## Few-Shot Examples

<!-- Populated after each mapping session. Format: source entry → chosen targets with rationale. -->

## Lessons Learned

<!-- Cross-cutting patterns discovered across mapping sessions. -->
```

- [ ] **Step 3: Verify .claude/ is gitignored**

```bash
git status .claude/
```

Expected: No output (directory is gitignored, not tracked)

---

### Task 9: Generate IAB v2.0 → Google latest canonical mapping

**Files:**
- Create: `mappings/ad_product/iab_v2.0__google_latest/mapping.json`

This task is LLM-assisted. Claude Code reads the skill and generates mappings in batches.

- [ ] **Step 1: Create output directory**

```bash
mkdir -p mappings/ad_product/iab_v2.0__google_latest
```

- [ ] **Step 2: Read the skill and source taxonomies**

Read `.claude/skills/adtech-taxonomy-mapper.md`, `taxonomies/ad_product/iab/v2.0/taxonomy.json`, and `taxonomies/ad_product/google/latest/taxonomy.json` into context.

- [ ] **Step 3: Generate mapping in batches of 25 (parents first)**

Process IAB entries in groups of 25, starting with entries where `parent_id` is null (top-level categories), then their children. For each batch, produce JSON entries matching the output schema in the skill. Accumulate all entries in memory.

- [ ] **Step 4: Assemble and write mapping.json**

Assemble the complete mapping.json with full metadata block. Count total_source_entries, mapped_entries (entries with at least one target), and unmapped_entries.

Write to `mappings/ad_product/iab_v2.0__google_latest/mapping.json`.

- [ ] **Step 5: Validate**

```bash
python scripts/validate.py mappings/ad_product/iab_v2.0__google_latest/mapping.json
```

Expected: `OK [mapping] ... 0 errors`

- [ ] **Step 6: Spot-check 5 known entries**

```bash
python -c "
import json
with open('mappings/ad_product/iab_v2.0__google_latest/mapping.json') as f:
    data = json.load(f)
idx = {e['source_id']: e for e in data['entries']}

# Alcohol should map to Beverages/Alcoholic
alcohol = idx.get('1002')
assert alcohol and alcohol['targets'], 'Alcohol should have targets'
assert any('lcohol' in t['target_path'] or 'everage' in t['target_path'] for t in alcohol['targets']), \
    f'Alcohol targets look wrong: {[t[\"target_path\"] for t in alcohol[\"targets\"]]}'

# Beer (child of Alcohol) should also map
beer = idx.get('1004')
assert beer and beer['targets'], 'Beer should have targets'

# Check confidence is in [0,1] for all entries
for entry in data['entries']:
    for t in entry['targets']:
        assert 0.0 <= t['confidence'] <= 1.0, f'Bad confidence: {t}'

print('Spot check passed')
print(f'Mapped: {data[\"metadata\"][\"mapped_entries\"]} / {data[\"metadata\"][\"total_source_entries\"]}')
"
```

Expected: `Spot check passed` and a mapped/total count.

- [ ] **Step 7: Commit canonical mapping**

```bash
git add mappings/ad_product/iab_v2.0__google_latest/
git commit -m "data: add IAB Ad Product v2.0 → Google Product Type (latest) canonical mapping"
```

---

### Task 10: Generate derived reverse mapping (Google latest → IAB v2.0)

**Files:**
- Create: `mappings/ad_product/google_latest__iab_v2.0/mapping.json`

- [ ] **Step 1: Create output directory**

```bash
mkdir -p mappings/ad_product/google_latest__iab_v2.0
```

- [ ] **Step 2: Run inverter**

```bash
python scripts/invert_mapping.py \
  mappings/ad_product/iab_v2.0__google_latest/mapping.json \
  mappings/ad_product/google_latest__iab_v2.0/mapping.json
```

Expected: `Written XXX reverse entries to mappings/ad_product/google_latest__iab_v2.0/mapping.json`

- [ ] **Step 3: Validate**

```bash
python scripts/validate.py mappings/ad_product/google_latest__iab_v2.0/mapping.json
```

Expected: `OK [mapping] ... 0 errors`

- [ ] **Step 4: Verify derived_from is set correctly**

```bash
python -c "
import json
with open('mappings/ad_product/google_latest__iab_v2.0/mapping.json') as f:
    data = json.load(f)
assert data['metadata']['canonical'] == False
assert data['metadata']['derived_from'] == 'iab_v2.0__google_latest'
assert data['metadata']['source_provider'] == 'google'
assert data['metadata']['target_provider'] == 'iab'
print('Reverse mapping metadata OK')
"
```

Expected: `Reverse mapping metadata OK`

- [ ] **Step 5: Commit**

```bash
git add mappings/ad_product/google_latest__iab_v2.0/
git commit -m "data: add Google Product Type → IAB Ad Product v2.0 derived reverse mapping"
```

---

### Task 11: Generate IAB v1.0 → Google latest canonical and reverse

**Files:**
- Create: `mappings/ad_product/iab_v1.0__google_latest/mapping.json`
- Create: `mappings/ad_product/google_latest__iab_v1.0/mapping.json`

- [ ] **Step 1: Create output directories**

```bash
mkdir -p mappings/ad_product/iab_v1.0__google_latest
mkdir -p mappings/ad_product/google_latest__iab_v1.0
```

- [ ] **Step 2: Read the skill (picks up any new few-shot examples from Task 9's review)**

Re-read `.claude/skills/adtech-taxonomy-mapper.md` before generating. IAB v1.0 has up to 5 tiers vs v2.0's 3 — treat deeper tier entries (Tier 4/5) as more specific `partial` matches.

- [ ] **Step 3: Generate canonical mapping in batches of 25**

Read `taxonomies/ad_product/iab/v1.0/taxonomy.json` as source and Google latest as target. Apply the same batch/parent-first strategy. Note: v1.0 categories are app-store oriented (Apps, Games) — many will have empty targets.

Write to `mappings/ad_product/iab_v1.0__google_latest/mapping.json`.

- [ ] **Step 4: Validate canonical**

```bash
python scripts/validate.py mappings/ad_product/iab_v1.0__google_latest/mapping.json
```

Expected: `OK [mapping] ... 0 errors`

- [ ] **Step 5: Generate reverse**

```bash
python scripts/invert_mapping.py \
  mappings/ad_product/iab_v1.0__google_latest/mapping.json \
  mappings/ad_product/google_latest__iab_v1.0/mapping.json
```

- [ ] **Step 6: Validate reverse**

```bash
python scripts/validate.py mappings/ad_product/google_latest__iab_v1.0/mapping.json
```

Expected: `OK [mapping] ... 0 errors`

- [ ] **Step 7: Commit**

```bash
git add mappings/ad_product/iab_v1.0__google_latest/ mappings/ad_product/google_latest__iab_v1.0/
git commit -m "data: add IAB Ad Product v1.0 ↔ Google Product Type (latest) mappings"
```

---

### Task 12: Create index.json

**Files:**
- Create: `index.json`

- [ ] **Step 1: Read actual entry counts from generated taxonomy files**

```bash
python -c "
import json
for path in [
  'taxonomies/ad_product/iab/v1.0/taxonomy.json',
  'taxonomies/ad_product/iab/v2.0/taxonomy.json',
  'taxonomies/ad_product/google/latest/taxonomy.json',
]:
    with open(path) as f:
        d = json.load(f)
    print(path, '->', len(d['entries']), 'entries', '| snapshot_date:', d['metadata'].get('snapshot_date', 'N/A'))
"
```

Note the actual snapshot_date for the google/latest entry — use it in `index.json`'s `updated_at`.

- [ ] **Step 2: Write index.json**

Use the snapshot_date from step 1 for `updated_at`. Replace `SNAPSHOT_DATE` below with the actual date from the Google taxonomy metadata.

```json
{
  "version": "1.0.0",
  "updated_at": "SNAPSHOT_DATE",
  "providers": {
    "iab": {
      "full_name": "IAB Tech Lab",
      "source_url": "https://github.com/InteractiveAdvertisingBureau/Taxonomies"
    },
    "google": {
      "full_name": "Google",
      "source_url": "https://www.google.com/basepages/producttype/taxonomy.en-US.txt"
    }
  },
  "taxonomies": [
    {
      "taxonomy_type": "ad_product",
      "provider": "iab",
      "version": "v1.0",
      "path": "taxonomies/ad_product/iab/v1.0/"
    },
    {
      "taxonomy_type": "ad_product",
      "provider": "iab",
      "version": "v2.0",
      "path": "taxonomies/ad_product/iab/v2.0/"
    },
    {
      "taxonomy_type": "ad_product",
      "provider": "google",
      "version": "latest",
      "path": "taxonomies/ad_product/google/latest/"
    }
  ],
  "mappings": [
    {
      "taxonomy_type": "ad_product",
      "source": "iab_v2.0",
      "target": "google_latest",
      "canonical": true,
      "path": "mappings/ad_product/iab_v2.0__google_latest/",
      "reverse_path": "mappings/ad_product/google_latest__iab_v2.0/"
    },
    {
      "taxonomy_type": "ad_product",
      "source": "iab_v1.0",
      "target": "google_latest",
      "canonical": true,
      "path": "mappings/ad_product/iab_v1.0__google_latest/",
      "reverse_path": "mappings/ad_product/google_latest__iab_v1.0/"
    }
  ]
}
```

- [ ] **Step 3: Validate index.json is valid JSON and has required keys**

```bash
python -c "
import json
with open('index.json') as f:
    idx = json.load(f)
assert 'providers' in idx and 'iab' in idx['providers'] and 'google' in idx['providers']
assert len(idx['taxonomies']) == 3
assert len(idx['mappings']) == 2
for m in idx['mappings']:
    assert 'path' in m and 'reverse_path' in m
print('index.json OK — providers:', list(idx['providers']), '| mappings:', len(idx['mappings']))
"
```

Expected: `index.json OK — providers: ['iab', 'google'] | mappings: 2`

- [ ] **Step 4: Commit index**

```bash
git add index.json
git commit -m "feat: add index.json root manifest for agent discovery"
```

---

### Task 13: Create GitHub repo and push

- [ ] **Step 1: Switch to markomma GitHub account**

```bash
gh auth switch --user markomma
gh auth status
```

Expected: `Logged in to github.com as markomma`

- [ ] **Step 2: Create public repo**

```bash
gh repo create adtech-taxonomy --public --description "Cross-provider taxonomy mapping for AdTech (IAB Tech Lab, Google, and others)" --source=. --remote=origin
```

- [ ] **Step 3: Push**

```bash
git push -u origin main
```

Expected: All commits pushed, branch set to track origin/main.

- [ ] **Step 4: Verify repo is live**

```bash
gh repo view markomma/adtech-taxonomy --web
```

Expected: Browser opens to the public repo on GitHub.
