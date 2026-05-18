import json
from unittest.mock import patch

import pytest

import ingest_iab


def _make_long_tsv(n: int) -> str:
    header = "\t".join(["Unique ID", "Parent ID", "Name", "Tier 1"]) + "\n"
    rows = "".join(f"{i}\t\tCat {i}\tCat {i}\n" for i in range(1, n + 1))
    return header + rows


@patch("ingest_iab.fetch_url")
def test_ingest_content_writes_taxonomy(mock_fetch, tmp_path):
    mock_fetch.return_value = _make_long_tsv(350)
    changed = ingest_iab.ingest("content", "v1.0", repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "content" / "iab" / "v1.0" / "taxonomy.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["metadata"]["provider"] == "iab"
    assert data["metadata"]["taxonomy_type"] == "content"
    assert data["metadata"]["version"] == "v1.0"
    assert len(data["entries"]) == 350
    assert changed is True


@patch("ingest_iab.fetch_url")
def test_ingest_audience_writes_taxonomy(mock_fetch, tmp_path):
    mock_fetch.return_value = _make_long_tsv(120)
    ingest_iab.ingest("audience", "v1.0", repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "audience" / "iab" / "v1.0" / "taxonomy.json"
    assert out.exists()


@patch("ingest_iab.fetch_url")
def test_ingest_detects_no_change(mock_fetch, tmp_path):
    mock_fetch.return_value = _make_long_tsv(350)
    ingest_iab.ingest("content", "v1.0", repo_root=tmp_path)
    changed = ingest_iab.ingest("content", "v1.0", repo_root=tmp_path)
    assert changed is False


@patch("ingest_iab.fetch_url")
def test_ingest_raises_below_floor(mock_fetch, tmp_path):
    mock_fetch.return_value = _make_long_tsv(5)
    with pytest.raises(ValueError, match="Expected"):
        ingest_iab.ingest("content", "v1.0", repo_root=tmp_path)


@patch("ingest_iab.fetch_url")
def test_ingest_registers_in_index(mock_fetch, tmp_path):
    mock_fetch.return_value = _make_long_tsv(350)
    index = {"generated_at": "2026-01-01T00:00:00Z", "taxonomies": [], "mappings": []}
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(index))
    ingest_iab.ingest("content", "v1.0", repo_root=tmp_path)
    updated = json.loads(index_path.read_text())
    providers = [taxonomy["provider"] for taxonomy in updated["taxonomies"]]
    assert "iab" in providers


def test_sources_dict_has_all_types():
    assert "ad_product" in ingest_iab.SOURCES
    assert "content" in ingest_iab.SOURCES
    assert "audience" in ingest_iab.SOURCES
    assert "v1.0" in ingest_iab.SOURCES["content"]
    assert "v3.0" in ingest_iab.SOURCES["content"]
    assert "v1.1" in ingest_iab.SOURCES["audience"]
