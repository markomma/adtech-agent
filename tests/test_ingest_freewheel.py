import json
from unittest.mock import patch

import pytest

import ingest_freewheel


PREBID_FIXTURE = json.dumps(
    {
        "mapping": {
            "IAB1": {"id": 392, "name": "Entertainment"},
            "IAB1-1": {"id": 392, "name": "Entertainment"},
            "IAB2": {"id": 282, "name": "Automotive"},
            "IAB7": {"id": 354, "name": "Health"},
        }
    }
)

STREAMING_HUB_HTML = (
    """
<html><body>
<h3>Streaming Hub IDs</h3>
<table>
<tr><th>ID</th><th>Name</th><th>Tier 1</th><th>Tier 2</th></tr>
"""
    + "".join(
        f"<tr><td>{i}</td><td>Sport {i}</td><td>Sports</td><td>Sport {i}</td></tr>"
        for i in range(1, 602)
    )
    + """
</table>
</body></html>
"""
)


@patch("ingest_freewheel.fetch_url")
def test_ingest_ad_product_extracts_unique_fw_entries(mock_fetch, tmp_path):
    mock_fetch.return_value = PREBID_FIXTURE
    ingest_freewheel.ingest_ad_product(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "ad_product" / "freewheel" / "latest" / "taxonomy.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data["entries"]) == 3


@patch("ingest_freewheel.fetch_url")
def test_ingest_ad_product_entry_schema(mock_fetch, tmp_path):
    mock_fetch.return_value = PREBID_FIXTURE
    ingest_freewheel.ingest_ad_product(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "ad_product" / "freewheel" / "latest" / "taxonomy.json"
    data = json.loads(out.read_text())
    entry = data["entries"][0]
    assert "id" in entry
    assert "name" in entry
    assert "parent_id" in entry
    assert "full_path" in entry


@patch("ingest_freewheel.fetch_url")
def test_ingest_ad_product_metadata(mock_fetch, tmp_path):
    mock_fetch.return_value = PREBID_FIXTURE
    ingest_freewheel.ingest_ad_product(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "ad_product" / "freewheel" / "latest" / "taxonomy.json"
    data = json.loads(out.read_text())
    assert data["metadata"]["provider"] == "freewheel"
    assert data["metadata"]["taxonomy_type"] == "ad_product"
    assert data["metadata"]["version"] == "latest"
    assert "prebid" in data["metadata"]["source_url"]


@patch("ingest_freewheel.fetch_url")
def test_ingest_content_writes_taxonomy(mock_fetch, tmp_path):
    mock_fetch.return_value = STREAMING_HUB_HTML
    ingest_freewheel.ingest_content(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "content" / "freewheel" / "latest" / "taxonomy.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data["entries"]) == 601


@patch("ingest_freewheel.fetch_url")
def test_ingest_content_raises_below_floor(mock_fetch, tmp_path):
    sparse_html = """
    <html><body>
    <h3>Streaming Hub IDs</h3>
    <table>
    <tr><th>ID</th><th>Name</th><th>Tier 1</th></tr>
    <tr><td>1</td><td>Sports</td><td>Sports</td></tr>
    </table></body></html>
    """
    mock_fetch.return_value = sparse_html
    with pytest.raises(ValueError, match="Expected"):
        ingest_freewheel.ingest_content(repo_root=tmp_path)


@patch("ingest_freewheel.fetch_url")
def test_ingest_detects_no_change(mock_fetch, tmp_path):
    mock_fetch.return_value = PREBID_FIXTURE
    ingest_freewheel.ingest_ad_product(repo_root=tmp_path)
    changed = ingest_freewheel.ingest_ad_product(repo_root=tmp_path)
    assert changed is False
