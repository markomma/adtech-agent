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
