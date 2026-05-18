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

STREAMING_HUB_LIVE_SHAPE_HTML = (
    """
<html><body>
<h3>Streaming Hub IDs</h3>
<table>
<tr><th>Tier</th><th>Category Name</th><th>ID</th></tr>
<tr><td>Tier 1</td><td>Alcoholic beverages</td><td>4963</td></tr>
<tr><td>Tier 2</td><td>Beer/Cider/Lager Beverages</td><td>4964</td></tr>
<tr><td>Tier 2</td><td>Wine Beverages</td><td>4965</td></tr>
"""
    + "".join(
        f"<tr><td>Tier 1</td><td>Category {i}</td><td>{6000 + i}</td></tr>"
        for i in range(1, 599)
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
def test_ingest_content_live_shape_uses_category_names_and_hierarchy(mock_fetch, tmp_path):
    mock_fetch.return_value = STREAMING_HUB_LIVE_SHAPE_HTML
    ingest_freewheel.ingest_content(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "content" / "freewheel" / "latest" / "taxonomy.json"
    data = json.loads(out.read_text())
    parent, child = data["entries"][0], data["entries"][1]
    assert parent["name"] == "Alcoholic beverages"
    assert parent["full_path"] == "Alcoholic beverages"
    assert child["name"] == "Beer/Cider/Lager Beverages"
    assert child["parent_id"] == "4963"
    assert child["full_path"] == "Alcoholic beverages > Beer/Cider/Lager Beverages"


@patch("ingest_freewheel.fetch_url")
def test_ingest_content_deduplicates_reused_source_ids(mock_fetch, tmp_path):
    html = """
    <html><body>
    <h3>Streaming Hub IDs</h3>
    <table>
    <tr><th>Tier</th><th>Category Name</th><th>ID</th></tr>
    <tr><td>Tier 1</td><td>Entertainment</td><td>100</td></tr>
    <tr><td>Tier 2</td><td>Concert</td><td>5312</td></tr>
    <tr><td>Tier 1</td><td>Music</td><td>200</td></tr>
    <tr><td>Tier 2</td><td>Concert</td><td>5312</td></tr>
    """
    html += "".join(
        f"<tr><td>Tier 1</td><td>Category {i}</td><td>{6000 + i}</td></tr>"
        for i in range(1, 598)
    )
    html += "</table></body></html>"
    mock_fetch.return_value = html
    ingest_freewheel.ingest_content(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "content" / "freewheel" / "latest" / "taxonomy.json"
    data = json.loads(out.read_text())
    ids = [entry["id"] for entry in data["entries"]]
    assert "5312" in ids
    assert "5312_2" in ids


@patch("ingest_freewheel.fetch_url")
def test_ingest_content_raises_when_names_are_numeric_ids(mock_fetch, tmp_path):
    bad_html = (
        """
    <html><body>
    <h3>Streaming Hub IDs</h3>
    <table>
    <tr><th>ID</th><th>Name</th></tr>
    """
        + "".join(f"<tr><td>{i}</td><td>{i}</td></tr>" for i in range(1, 602))
        + """
    </table></body></html>
    """
    )
    mock_fetch.return_value = bad_html
    with pytest.raises(ValueError, match="numeric names"):
        ingest_freewheel.ingest_content(repo_root=tmp_path)


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


@patch("ingest_freewheel.ingest_ad_product")
@patch("sys.argv", ["ingest_freewheel.py", "--type", "ad_product"])
def test_main_changed_exits_zero_by_default(mock_ingest):
    mock_ingest.return_value = True
    assert ingest_freewheel.main() is None


@patch("ingest_freewheel.ingest_ad_product")
@patch("sys.argv", ["ingest_freewheel.py", "--type", "ad_product", "--fail-on-change"])
def test_main_can_fail_on_change(mock_ingest):
    mock_ingest.return_value = True
    with pytest.raises(SystemExit) as exc:
        ingest_freewheel.main()
    assert exc.value.code == 1
