# AdTech Taxonomy Mapping Repository — Design Spec

**Date:** 2026-05-15  
**Status:** Approved  
**Scope:** Repository structure, schema definitions, generation skill, and future MCP surface for cross-provider taxonomy mapping in AdTech

---

## 1. Purpose

A public reference repository that maps taxonomy categories across DSPs, SSPs, and industry bodies. It serves as both a human-readable reference for ad ops teams and a machine-ingestible data source for developers and LLM agents. The long-term goal is to support mapping across dozens of providers and expose the data via an MCP server.

---

## 2. Taxonomy Types

Three taxonomy types are in scope:

| Type | Description |
|------|-------------|
| `ad_product` | Categories of advertised products (IAB Ad Product, Google Product Type) |
| `audience` | Audience segment classifications |
| `content` | Content category classifications |

---

## 3. Repository Structure

```
adtech-taxonomy/
├── taxonomies/
│   ├── ad_product/
│   │   ├── iab/
│   │   │   ├── v1.0/
│   │   │   │   └── taxonomy.json      ← metadata embedded
│   │   │   └── v2.0/
│   │   │       └── taxonomy.json      ← metadata embedded
│   │   └── google/
│   │       └── latest/
│   │           └── taxonomy.json      ← metadata embedded (incl. snapshot_date)
│   ├── audience/
│   └── content/
├── mappings/
│   ├── ad_product/
│   │   ├── iab_v2.0__google_latest/   ← canonical
│   │   │   └── mapping.json           ← metadata embedded
│   │   ├── google_latest__iab_v2.0/   ← derived (auto-generated)
│   │   │   └── mapping.json           ← metadata embedded
│   │   ├── iab_v1.0__google_latest/
│   │   └── google_latest__iab_v1.0/
│   ├── audience/
│   └── content/
├── index.json
├── CLAUDE.md
├── .gitignore          ← includes .claude/
├── .claude/            ← gitignored; private generation skill
│   └── skills/
│       └── adtech-taxonomy-mapper.md
├── tools/              ← future public MCP server utilities
└── README.md
```

### Naming Conventions

- **Taxonomy version folders:** IAB uses `v2.0`, `v1.0`. Single-version providers (Google) always use `latest/`.
- **Mapping folder names:** `{source_provider}_{source_version}__{target_provider}_{target_version}`. Double underscore separates the two sides.
- **Canonical direction:** Provider with stable integer IDs (IAB) always comes first. Google and other non-versioned providers come second.
- **Provider slugs:** `iab`, `google`. New providers register a lowercase slug in `index.json`.

### Versioning Policy

IAB taxonomies are immutable snapshots. Google (and any provider without distinct versioned releases) uses a single `latest/` folder updated in place. `metadata.json` inside `latest/` carries `snapshot_date` and `fetched_at` for traceability. Mapping folder names reference `google_latest` — they never embed dates — so agent lookup paths remain stable across Google updates.

---

## 4. Schema Definitions

### 4.1 `taxonomy.json`

```json
{
  "metadata": {
    "provider": "iab",
    "taxonomy_type": "ad_product",
    "version": "2.0",
    "snapshot_date": "2024-01-15",
    "source_url": "https://github.com/InteractiveAdvertisingBureau/Taxonomies/...",
    "fetched_at": "2024-01-15T10:00:00Z"
  },
  "entries": [
    {
      "id": "1002",
      "parent_id": null,
      "name": "Alcohol",
      "full_path": "Alcohol"
    },
    {
      "id": "1004",
      "parent_id": "1002",
      "name": "Beer",
      "full_path": "Alcohol > Beer"
    }
  ]
}
```

For IAB: `id` is the integer string from the source TSV. For Google and other path-based providers: `id` is a stable slug derived from the full path (e.g., `food-beverages-tobacco__beverages__alcoholic-beverages`). This gives all providers a consistent `id` field for agent lookup.

### 4.2 `mapping.json` (canonical direction)

```json
{
  "metadata": {
    "source_provider": "iab",
    "source_version": "2.0",
    "target_provider": "google",
    "target_version": "latest",
    "taxonomy_type": "ad_product",
    "canonical": true,
    "derived_from": null,
    "mapping_version": "1.0.0",
    "generated_at": "2026-05-15T10:00:00Z",
    "generated_by": "llm-assisted",
    "total_source_entries": 412,
    "mapped_entries": 398,
    "unmapped_entries": 14
  },
  "entries": [
    {
      "source_id": "1002",
      "source_name": "Alcohol",
      "source_path": "Alcohol",
      "targets": [
        {
          "target_id": "food-beverages-tobacco__beverages__alcoholic-beverages",
          "target_path": "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages",
          "confidence": 0.95,
          "match_type": "semantic",
          "notes": "Strong semantic match at category level"
        },
        {
          "target_id": "food-beverages-tobacco__beverages__alcoholic-beverages__wine",
          "target_path": "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Wine",
          "confidence": 0.60,
          "match_type": "partial",
          "notes": "Use only when IAB entry is narrowed to wine context"
        }
      ]
    },
    {
      "source_id": "1014",
      "source_name": "Employee Expense and Time Tracking Services",
      "source_path": "Business and Industrial > Business Services > Employee Expense and Time Tracking Services",
      "targets": []
    }
  ]
}
```

**`match_type` values:**

| Value | Meaning |
|-------|---------|
| `exact` | Term-for-term name match |
| `semantic` | Same concept, different terminology |
| `partial` | One side is broader or narrower than the other |
| `approximate` | Related but imperfect; expect lower confidence |
| `none` | No reasonable match exists; `targets` is empty |

### 4.3 `mapping.json` (derived/reverse direction)

Same schema as canonical but with `source` and `target` sides swapped, and:
```json
"canonical": false,
"derived_from": "iab_v2.0__google_latest"
```

Never edited directly. Regenerated by the generation skill whenever the canonical is updated.

### 4.4 `index.json` (root manifest)

```json
{
  "version": "1.0.0",
  "updated_at": "2026-05-15T10:00:00Z",
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
    }
  ]
}
```

---

## 5. Private Generation Skill

**Location:** `.claude/skills/adtech-taxonomy-mapper.md` (gitignored — never committed to the public repo)

### Responsibilities

1. **Fetch source taxonomies** — read both `taxonomy.json` files for the pair being mapped
2. **Generate canonical mapping** — send batched IAB entries to Claude with the full Google taxonomy as context; produce `mapping.json` entries with confidence scores, match types, and notes
3. **Generate derived reverse** — invert the canonical mapping programmatically; preserve confidence scores; write to the reverse folder
4. **Update `index.json`** — register the new mapping pair if not already present
5. **Self-improve** — after each session where a human reviewer adjusts confidence scores, adds targets, or removes incorrect matches, distill those corrections into the skill's `## Few-Shot Examples` section

### Batch Strategy

IAB entries are processed in groups of 20–30. Parent entries are mapped before children so child mappings can reference parent decisions for consistency.

### Self-Improvement Loop

```
Generate mapping
  → Human reviews (adjust confidence, add/remove targets)
  → Corrections distilled into 2–3 new few-shot examples
  → Skill's ## Few-Shot Examples section updated
  → Skill's ## Lessons Learned section updated with cross-cutting patterns
  → Next session starts by re-reading the skill
```

The `## Lessons Learned` section captures patterns like: "IAB tier-3 entries in B2B services rarely have Google equivalents — default to `none` unless a direct product match exists."

---

## 6. Future MCP Server (tools/)

After the first mapping is complete, a lightweight public MCP server in `tools/` will expose read-only access to the committed JSON data:

| Tool | Description |
|------|-------------|
| `list_available_mappings()` | Returns `index.json` content |
| `get_taxonomy_entry(provider, version, id)` | Returns a single taxonomy entry with full path |
| `resolve_taxonomy_mapping(source_provider, source_version, source_id, target_provider)` | Returns matching targets with confidence scores |

The MCP server reads from committed files only — no generation logic, no private skill exposure.

---

## 7. CLAUDE.md Behavior Instructions

The project `CLAUDE.md` will instruct Claude to:

1. **At the start of every mapping session:** Re-read `.claude/skills/adtech-taxonomy-mapper.md` to load accumulated learnings before generating any mappings
2. **At the end of every mapping session:** Identify entries where confidence was adjusted or targets were changed by a human reviewer; distill into 2–3 new few-shot examples; append to the skill's `## Few-Shot Examples` section; update `## Lessons Learned` with any new cross-cutting patterns observed
3. **After updating the skill:** Confirm to the user what was added/changed in the skill file

---

## 8. Scalability Considerations

- Adding a new provider requires: (a) adding a slug to `index.json providers`, (b) creating a `taxonomies/{type}/{provider}/{version}/` folder, (c) generating canonical mappings against existing providers
- The `audience/` and `content/` taxonomy types follow identical conventions — no structural changes needed to expand into them
- The MCP server tools are provider-agnostic; they resolve via `index.json` and work for any registered provider without code changes
