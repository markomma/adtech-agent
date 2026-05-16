# adtech-agent

Open-source AdTech agent toolkit — cross-provider taxonomy mappings, conversion utilities, and LLM-assisted tooling for the advertising technology ecosystem.

## Taxonomy Mappings

Bidirectional mappings between AdTech category taxonomies from industry bodies and major platforms.

### Taxonomy Types

| Type | Description |
|------|-------------|
| `ad_product` | Categories of advertised products |
| `audience` | Audience segment classifications |
| `content` | Content category classifications |

### Structure

```
taxonomies/{taxonomy_type}/{provider}/{version}/taxonomy.json
mappings/{taxonomy_type}/{source}__{target}/mapping.json
```

Provider version conventions:
- IAB Tech Lab: `v1.0`, `v2.0` (immutable snapshots)
- Google: `latest` (single folder, `snapshot_date` in metadata)

### Mappings

Mapping folders use double-underscore to separate source from target:
`iab_v2.0__google_latest` = IAB Ad Product 2.0 → Google Product Type (latest)

Each mapping pair has a **canonical** file (source of truth, indexed by the provider with stable integer IDs) and a **derived** reverse file (auto-generated, never edited directly).

### Discovery

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
