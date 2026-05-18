"""Load taxonomy, mapping, and search index data from the bundled data directory."""
import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"


class Loader:
    def __init__(self, data_dir: Path = _DATA_DIR) -> None:
        self._data_dir = data_dir
        with open(data_dir / "index.json") as f:
            self._index: dict = json.load(f)
        self._taxonomies: dict[str, dict | None] = {}
        self._mappings: dict[str, dict | None] = {}
        self._search_indices: dict[str, dict | None] = {}

    def list_taxonomies(self) -> dict:
        result = []
        for t in self._index["taxonomies"]:
            mapped_to = [
                m["target_provider"]
                for m in self._index["mappings"]
                if m["source_provider"] == t["provider"]
                and m["source_version"] == t["version"]
            ]
            result.append({
                "provider": t["provider"],
                "version": t["version"],
                "taxonomy_type": t["taxonomy_type"],
                "entry_count": t["entry_count"],
                "mapped_to": mapped_to,
            })
        return {"taxonomies": result}

    def get_latest_version(self, provider: str, taxonomy_type: str = "ad_product") -> str | None:
        versions = [
            t["version"]
            for t in self._index["taxonomies"]
            if t["provider"] == provider and t["taxonomy_type"] == taxonomy_type
        ]
        if not versions:
            return None
        return sorted(versions, key=_version_sort_key)[-1]

    def get_taxonomy(self, provider: str, version: str, taxonomy_type: str = "ad_product") -> dict | None:
        key = f"{taxonomy_type}/{provider}/{version}"
        if key not in self._taxonomies:
            path = self._data_dir / "taxonomies" / taxonomy_type / provider / version / "taxonomy.json"
            self._taxonomies[key] = json.loads(path.read_text()) if path.exists() else None
        return self._taxonomies[key]

    def get_search_index(self, provider: str, version: str, taxonomy_type: str = "ad_product") -> dict | None:
        key = f"{taxonomy_type}/{provider}/{version}"
        if key not in self._search_indices:
            path = self._data_dir / "taxonomies" / taxonomy_type / provider / version / "taxonomy.search-index.json"
            self._search_indices[key] = json.loads(path.read_text()) if path.exists() else None
        return self._search_indices[key]

    def get_mapping_entries(
        self,
        source_provider: str,
        source_version: str,
        category_id: str,
        target_provider: str | None = None,
    ) -> list[dict]:
        results = []
        for m in self._index["mappings"]:
            if m["source_provider"] != source_provider or m["source_version"] != source_version:
                continue
            if target_provider and m["target_provider"] != target_provider:
                continue
            mapping_data = self._load_mapping(m["path"])
            if mapping_data is None:
                continue
            entry = next((e for e in mapping_data["entries"] if e["source_id"] == category_id), None)
            if entry is None:
                continue
            for target in entry["targets"]:
                results.append({
                    "target_provider": m["target_provider"],
                    "target_version": m["target_version"],
                    **target,
                })
        return results

    def _load_mapping(self, path: str) -> dict | None:
        if path not in self._mappings:
            full_path = self._data_dir / path
            self._mappings[path] = json.loads(full_path.read_text()) if full_path.exists() else None
        return self._mappings[path]


def _version_sort_key(version: str) -> tuple[int, ...] | tuple[int, str]:
    if version == "latest":
        return (999999,)
    if version.startswith("v"):
        parts = version[1:].split(".")
        if all(part.isdigit() for part in parts):
            return tuple(int(part) for part in parts)
    return (-1, version)
