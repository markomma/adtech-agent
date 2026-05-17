# Installing adtech-crosswalk MCP Server

## Quick Setup

Add to your MCP client configuration:

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

No API key or account required. Runs fully locally from bundled taxonomy data.

## Configuration File Locations

| Client | Config Path |
|--------|-------------|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |
| Claude Code | `~/.claude/settings.json` or run `claude mcp add adtech-crosswalk -- uvx adtech-crosswalk` |
| Cursor | `.cursor/mcp.json` in your project root |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Cline | MCP settings in Cline UI (Settings → MCP Servers → Add) |
| OpenAI Codex CLI | `~/.codex/config.toml` |
| Gemini CLI | `~/.gemini/settings.json` (global) or `.gemini/settings.json` in project root |

### Claude Code (CLI)

```bash
claude mcp add adtech-crosswalk -- uvx adtech-crosswalk
```

### OpenAI Codex CLI

Add manually to `~/.codex/config.toml`:

```toml
[mcp_servers.adtech-crosswalk]
command = "uvx"
args = ["adtech-crosswalk"]
```

### Gemini CLI

```bash
gemini mcp add --transport stdio adtech-crosswalk uvx adtech-crosswalk
```

Or add to `~/.gemini/settings.json`:

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

### Alternative: pip install

If `uvx` is not available:

```bash
pip install adtech-crosswalk
```

Then use `"command": "adtech-crosswalk"` with no `args` in the config above.

## Verification

After adding the configuration, restart your MCP client and verify by asking:

> "What AdTech taxonomy providers are available?"

The `list_adtech_taxonomies` tool should return available providers and mapped pairs.

## Tools

### `list_adtech_taxonomies`

Discovery — no inputs required. Returns all available taxonomy providers, versions, and cross-provider mapping pairs.

Call this first to understand what's available before resolving or mapping.

### `resolve_adtech_category`

Natural language → matching taxonomy entries. Use this when you have a concept, campaign topic, or product description and need the canonical taxonomy ID.

```
resolve_adtech_category(
  raw_category="craft beer",
  providers=["iab"],        # optional — defaults to iab
  version="v2.0",           # optional
  min_confidence=0.75       # optional — default 0.75, range 0.0–1.0
)
→ matches: [{ category_id: "1004", category_name: "Beer", relevance_score: 0.91, full_path: "..." }]
```

Use cases:
- **Campaign intent**: "I'm running a campaign for running shoes — what IAB category?"
- **Bulk categorization**: resolve a list of advertiser verticals to taxonomy IDs

### `get_adtech_mapping`

Category ID → cross-provider mappings, sorted by confidence. Use this when you have a taxonomy ID from one provider and need the equivalent in another.

```
get_adtech_mapping(
  provider="iab",
  version="v2.0",
  category_id="1004",
  min_confidence=0.75       # optional — default 0.75
)
→ source: { id, name, full_path }, mappings: [{ target_provider, target_id, target_path, confidence, match_type }]
```

Confidence thresholds:
- `exact` (1.0): identical or near-identical category
- `semantic` (0.85–0.99): same concept, different label
- `partial` (0.75–0.84): overlapping concept, broader/narrower
- `approximate` (<0.75): loose match — excluded by default threshold

## Typical Agent Workflow

```
# 1. Discover what's available
list_adtech_taxonomies()

# 2. Resolve natural language to a taxonomy ID
resolve_adtech_category(raw_category="craft beer", providers=["iab"], version="v2.0")
→ category_id: "1004"

# 3. Get cross-provider mappings for that ID
get_adtech_mapping(provider="iab", version="v2.0", category_id="1004")
→ google target: "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer & Ale"
```

## Data Coverage

Current mappings (as of latest release):

| Source | Target | Entries mapped |
|--------|--------|----------------|
| IAB Ad Product v2.0 | Google Product Type | 583 source entries |
| IAB Ad Product v1.0 | Google Product Type | 863 source entries |
| Google Product Type | IAB Ad Product v2.0 | derived (reverse) |
| Google Product Type | IAB Ad Product v1.0 | derived (reverse) |

Audience and content taxonomy mappings are in progress. See `index.json` at the repo root for the current state.
