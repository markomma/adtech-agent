"""adtech-crosswalk MCP server."""
from mcp.server.fastmcp import FastMCP
from .loader import Loader
from .search import BM25Index

mcp = FastMCP("adtech-crosswalk")
_loader = Loader()
_engines: dict[str, BM25Index] = {}


def _get_engine(provider: str, version: str, taxonomy_type: str = "ad_product") -> BM25Index | None:
    key = f"{taxonomy_type}/{provider}/{version}"
    if key not in _engines:
        index_data = _loader.get_search_index(provider, version, taxonomy_type)
        if index_data is None:
            return None
        _engines[key] = BM25Index(index_data)
    return _engines[key]


def _list_taxonomies() -> dict:
    return _loader.list_taxonomies()


def _resolve_category(
    raw_category: str,
    taxonomy_type: str,
    providers: list[str] | None,
    version: str | None,
    min_confidence: float,
    limit: int,
) -> dict:
    if providers is None:
        providers = ["iab"]

    matches = []
    for provider in providers:
        ver = version or _loader.get_latest_version(provider, taxonomy_type)
        if ver is None:
            if taxonomy_type != "ad_product":
                return {"error": "taxonomy_unavailable", "message": f"Taxonomy type '{taxonomy_type}' has no data yet"}
            continue
        engine = _get_engine(provider, ver, taxonomy_type)
        if engine is None:
            if taxonomy_type != "ad_product":
                return {"error": "taxonomy_unavailable", "message": f"Taxonomy type '{taxonomy_type}' has no data yet"}
            continue
        for r in engine.query(raw_category, limit=limit, min_score=min_confidence):
            matches.append({"provider": provider, "version": ver, **r})

    matches.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"matches": matches}


def _get_mapping(
    provider: str,
    version: str,
    category_id: str,
    target_provider: str | None,
    min_confidence: float,
) -> dict:
    raise NotImplementedError


@mcp.tool()
def list_adtech_taxonomies() -> dict:
    """List all available taxonomy providers, versions, and mapped pairs.
    Call this first to discover what data is available before resolving categories."""
    return _list_taxonomies()


@mcp.tool()
def resolve_adtech_category(
    raw_category: str,
    taxonomy_type: str = "ad_product",
    providers: list[str] | None = None,
    version: str | None = None,
    min_confidence: float = 0.75,
    limit: int = 5,
) -> dict:
    """Resolve a raw category or concept to matching taxonomy entries.
    Default provider is IAB Tech Lab. Returns results sorted by relevance above min_confidence."""
    return _resolve_category(raw_category, taxonomy_type, providers, version, min_confidence, limit)


@mcp.tool()
def get_adtech_mapping(
    provider: str,
    version: str,
    category_id: str,
    target_provider: str | None = None,
    min_confidence: float = 0.75,
) -> dict:
    """Get cross-provider mappings for a known category ID.
    Returns mappings sorted by confidence descending, filtered by min_confidence."""
    return _get_mapping(provider, version, category_id, target_provider, min_confidence)


def main() -> None:
    mcp.run()
