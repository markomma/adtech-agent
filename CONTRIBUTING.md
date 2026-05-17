# Contributing

Thank you for helping grow adtech-crosswalk. Contributions fall into three categories: **data** (new taxonomies and mappings), **code** (MCP server, tooling), and **integrations** (new distribution channels).

## Prerequisites

- Python 3.11+
- `pip install -e ".[dev]"` — installs the package and dev dependencies
- `python -m adtech_crosswalk.sync_data` — populates `adtech_crosswalk/data/` for local runs

## Data Contribution Workflow

### Adding a new taxonomy provider

1. Add a provider slug to `index.json` under `providers`
2. Create the taxonomy file: `taxonomies/{type}/{provider}/{version}/taxonomy.json`
   - See existing files for the required schema (metadata + entries)
   - For unversioned providers use `latest/` as the version directory
3. Ingest from source if available:
   ```bash
   # IAB — pulls from IAB Tech Lab GitHub
   python scripts/ingest/convert_iab_tsv.py v2.0

   # Google — pulls live from google.com
   python scripts/ingest/convert_google_txt.py
   ```
4. Validate:
   ```bash
   python scripts/validate.py taxonomies/ad_product/{provider}/{version}/taxonomy.json
   ```
5. Build search index:
   ```bash
   python -m adtech_crosswalk.build_index
   ```
6. Register the new taxonomy in `index.json` under `taxonomies`

### Adding a new cross-provider mapping

1. Generate the canonical mapping (IAB-first direction) — for new providers, use the generate scripts as templates:
   ```bash
   # Examples:
   python scripts/generate/generate_iab_v2_google_mapping.py
   ```
2. Validate:
   ```bash
   python scripts/validate.py mappings/ad_product/{source}__{target}/mapping.json
   ```
3. Generate the derived reverse mapping:
   ```bash
   python scripts/invert_mapping.py \
     mappings/ad_product/iab_v2.0__provider_latest/mapping.json \
     mappings/ad_product/provider_latest__iab_v2.0/mapping.json
   ```
4. Register both mapping folders in `index.json` under `mappings`
5. Sync data and run tests:
   ```bash
   python -m adtech_crosswalk.sync_data
   pytest tests/ -v
   ```

### Naming conventions

| Thing | Pattern | Example |
|---|---|---|
| Mapping folder | `{source}_{sv}__{target}_{tv}` | `iab_v2.0__google_latest` |
| Canonical direction | IAB (integer IDs) always source | `iab_v2.0__google_latest` |
| Google version | always `latest` | — |
| IAB versions | `v1.0`, `v2.0`, etc. | — |

Double underscore separates the two providers; single underscores within each side.

## Provider Roadmap

After IAB ↔ Google, providers are prioritized by DSP/SSP market share:
1. The Trade Desk
2. Magnite
3. Microsoft Advertising / Xandr
4. Amazon DSP
5. Meta (Advantage+)

IAB v1.0 ↔ v2.0 cross-version mapping is out of scope — IAB Tech Lab publishes this directly.

## Code Contributions

The package lives in `adtech_crosswalk/`. Run tests with:

```bash
pytest tests/ -v
```

Keep a single test focused: prefer `pytest tests/test_loader.py` over running the full suite during development.

## Pull Request Guidelines

- **Data-only changes**: bump the patch version in `pyproject.toml` and commit `adtech_crosswalk/data/` alongside the source files — the CI publish job triggers on `index.json` changes on `main`
- **Code changes**: include or update tests; CI must pass before merge
- **New integrations**: see [integrations/README.md](integrations/README.md)
- Keep PRs focused; one provider addition or one bug fix per PR

## Questions

Open an issue or start a discussion. For mapping quality questions (confidence scores, match types), reference the schema in any existing `mapping.json`.
