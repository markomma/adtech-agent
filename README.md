# adtech-crosswalk

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
| `scripts/ingest/convert_iab_tsv.py` | Fetch IAB TSV → taxonomy.json |
| `scripts/ingest/convert_google_txt.py` | Fetch Google TXT → taxonomy.json |
| `scripts/validate.py` | Validate taxonomy.json and mapping.json schemas |
| `scripts/invert_mapping.py` | Generate reverse mapping from canonical |

## Data Sources

Taxonomy and mapping data is sourced from the following open repositories and public taxonomy files:

| Provider | Source | License |
|---|---|---|
| IAB Tech Lab (Ad Product, Content, Audience) | [InteractiveAdvertisingBureau/Taxonomies](https://github.com/InteractiveAdvertisingBureau/Taxonomies) | Apache 2.0 |
| Google Product Type Taxonomy | [Google Product Taxonomy](https://www.google.com/basepages/producttype/taxonomy.en-US.txt) | Public taxonomy file |
| FreeWheel MRM Industry IDs | [prebid/category-mapping-file](https://github.com/prebid/category-mapping-file) | Apache 2.0 |
| Xandr / Microsoft Brand and Content Categories | [MicrosoftDocs/xandr-docs](https://github.com/MicrosoftDocs/xandr-docs) | CC BY 4.0 |

## MCP Server

`adtech-crosswalk` is available as an MCP server for any LLM agent that supports the Model Context Protocol.

### Install

```bash
# Run directly with uvx (no install required)
uvx adtech-crosswalk

# Or install globally
pip install adtech-crosswalk
```

### Configure

Add to your MCP client config (Claude Code, Cursor, Copilot, etc.):

```json
{
  "mcpServers": {
    "adtech-crosswalk": {
      "command": "uvx",
      "args": ["adtech-crosswalk"]
    }
  }
}
```

### Tools

| Tool | Description |
|------|-------------|
| `list_adtech_taxonomies` | Discover available providers, versions, and mapped pairs |
| `resolve_adtech_category` | Natural language → matching taxonomy entries (default: IAB, threshold: 0.75) |
| `get_adtech_mapping` | Category ID → cross-provider mappings, sorted by confidence |

### Example

```
# Step 1 — discover
list_adtech_taxonomies()

# Step 2 — find the right category
resolve_adtech_category(raw_category="craft beer", providers=["iab"], version="v2.0")
→ { matches: [{ category_id: "1004", category_name: "Beer", relevance_score: 0.91 }] }

# Step 3 — get cross-provider mappings
get_adtech_mapping(provider="iab", version="v2.0", category_id="1004")
→ { source: {...}, mappings: [{ target_provider: "google", confidence: 0.95, ... }] }
```
