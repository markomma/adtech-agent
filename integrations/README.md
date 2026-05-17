# Integrations

adtech-crosswalk is designed to be consumed through multiple distribution channels.

## Available

### Python / PyPI (MCP server)

Install via pip and wire into any MCP-compatible host:

```bash
pip install adtech-crosswalk
```

See the root [README](../README.md) for Claude, Cursor, and ChatGPT configuration.

## Planned

### Docker

A `Dockerfile` that runs the MCP server over HTTP/SSE transport, suitable for hosted or containerized deployments. Target: v0.2.

### Cursor Plugin

A Cursor extension that auto-loads adtech-crosswalk as an MCP server in any workspace. Target: when Cursor plugin API stabilizes.

### npm / npx (Node.js wrapper)

For teams with Node.js-first toolchains, a thin npx wrapper that manages the Python server process. Target: v0.3.

## Contributing an Integration

Open an issue with the label `integration` to propose a new distribution channel. If you're building one, create a subdirectory here (e.g. `integrations/docker/`) and open a PR — keep integration code self-contained so it can be maintained independently of the core data.
