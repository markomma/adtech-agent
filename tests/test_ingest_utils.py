import json
import re
from pathlib import Path

import pytest

import utils


TSV_FIXTURE = (
    "\t".join(["Unique ID", "Parent ID", "Name", "Tier 1", "Tier 2"])
    + "\n"
    + "\t".join(["1", "", "Arts", "Arts", ""])
    + "\n"
    + "\t".join(["2", "1", "Books", "Arts", "Books"])
    + "\n"
)


def test_parse_tsv_returns_entries():
    entries = utils.parse_tsv(TSV_FIXTURE)
    assert len(entries) == 2


def test_parse_tsv_entry_fields():
    entries = utils.parse_tsv(TSV_FIXTURE)
    e = entries[0]
    assert e["id"] == "1"
    assert e["parent_id"] is None
    assert e["name"] == "Arts"
    assert e["full_path"] == "Arts"


def test_parse_tsv_child_has_parent():
    entries = utils.parse_tsv(TSV_FIXTURE)
    child = entries[1]
    assert child["parent_id"] == "1"
    assert child["full_path"] == "Arts > Books"


def test_parse_tsv_skips_blank_rows():
    tsv = (
        "\t".join(["Unique ID", "Parent ID", "Name", "Tier 1"])
        + "\n"
        + "\t".join(["", "", "", ""])
        + "\n"
        + "\t".join(["1", "", "Art", "Art"])
        + "\n"
    )
    entries = utils.parse_tsv(tsv)
    assert len(entries) == 1


def test_parse_tsv_deduplicates_ids():
    tsv = (
        "\t".join(["Unique ID", "Parent ID", "Name", "Tier 1"])
        + "\n"
        + "\t".join(["51", "", "First", "First"])
        + "\n"
        + "\t".join(["51", "", "Duplicate", "Duplicate"])
        + "\n"
    )
    entries = utils.parse_tsv(tsv)
    ids = [e["id"] for e in entries]
    assert len(set(ids)) == 2
    assert "51" in ids
    assert "51_2" in ids


MD_TABLE = """
## Categories

| Name | ID | IAB Code |
|---|---|---|
| Arts | 25 | IAB1 |
| Automotive | 26 | IAB2 |
"""


def test_parse_markdown_table_returns_rows():
    rows = utils.parse_markdown_table(MD_TABLE)
    assert len(rows) == 2


def test_parse_markdown_table_row_fields():
    rows = utils.parse_markdown_table(MD_TABLE)
    assert rows[0]["Name"] == "Arts"
    assert rows[0]["ID"] == "25"
    assert rows[0]["IAB Code"] == "IAB1"


def test_parse_markdown_table_skips_separator():
    rows = utils.parse_markdown_table(MD_TABLE)
    assert not any(re.match(r"^[-:]+$", r.get("Name", "")) for r in rows)


HTML_FIXTURE = """
<html><body>
<h3>Streaming Hub IDs</h3>
<table>
  <tr><th>ID</th><th>Name</th><th>Tier 1</th></tr>
  <tr><td>100</td><td>Sports</td><td>Sports</td></tr>
  <tr><td>101</td><td>Football</td><td>Sports</td></tr>
</table>
<h3>Platform IDs</h3>
<table>
  <tr><th>ID</th><th>Platform</th></tr>
  <tr><td>1</td><td>Desktop</td></tr>
</table>
</body></html>
"""


def test_parse_html_table_finds_by_caption():
    rows = utils.parse_html_table(HTML_FIXTURE, "Streaming Hub")
    assert len(rows) == 2


def test_parse_html_table_correct_rows():
    rows = utils.parse_html_table(HTML_FIXTURE, "Streaming Hub")
    assert rows[0]["ID"] == "100"
    assert rows[0]["Name"] == "Sports"


def test_parse_html_table_selects_correct_table():
    rows = utils.parse_html_table(HTML_FIXTURE, "Platform")
    assert len(rows) == 1
    assert rows[0]["Platform"] == "Desktop"


def test_parse_html_table_raises_when_not_found():
    with pytest.raises(ValueError, match="No table found"):
        utils.parse_html_table(HTML_FIXTURE, "Nonexistent Section")


def test_detect_changes_true_when_file_missing(tmp_path):
    assert utils.detect_changes({"entries": []}, tmp_path / "missing.json") is True


def test_detect_changes_false_when_identical(tmp_path):
    data = {"metadata": {"fetched_at": "2026-01-01T00:00:00Z"}, "entries": [{"id": "1"}]}
    path = tmp_path / "tax.json"
    path.write_text(json.dumps(data))
    assert utils.detect_changes(data, path) is False


def test_detect_changes_ignores_fetched_at(tmp_path):
    old = {"metadata": {"fetched_at": "2025-01-01T00:00:00Z"}, "entries": [{"id": "1"}]}
    new = {"metadata": {"fetched_at": "2026-01-01T00:00:00Z"}, "entries": [{"id": "1"}]}
    path = tmp_path / "tax.json"
    path.write_text(json.dumps(old))
    assert utils.detect_changes(new, path) is False


def test_detect_changes_ignores_generated_at(tmp_path):
    old = {"metadata": {"generated_at": "2025-01-01T00:00:00Z"}, "entries": []}
    new = {"metadata": {"generated_at": "2026-06-01T00:00:00Z"}, "entries": []}
    path = tmp_path / "map.json"
    path.write_text(json.dumps(old))
    assert utils.detect_changes(new, path) is False


def test_detect_changes_true_when_entries_differ(tmp_path):
    old = {"metadata": {}, "entries": [{"id": "1"}]}
    new = {"metadata": {}, "entries": [{"id": "1"}, {"id": "2"}]}
    path = tmp_path / "tax.json"
    path.write_text(json.dumps(old))
    assert utils.detect_changes(new, path) is True


def test_write_taxonomy_creates_file(tmp_path):
    metadata = {"provider": "test", "taxonomy_type": "ad_product", "version": "v1.0"}
    entries = [{"id": "1", "name": "A", "full_path": "A", "parent_id": None}]
    out = tmp_path / "out" / "taxonomy.json"
    utils.write_taxonomy(metadata, entries, out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["metadata"]["provider"] == "test"
    assert len(data["entries"]) == 1


def test_register_taxonomy_adds_new(tmp_path):
    index = {"generated_at": "2026-01-01T00:00:00Z", "taxonomies": [], "mappings": []}
    path = tmp_path / "index.json"
    path.write_text(json.dumps(index))
    entry = {
        "provider": "test",
        "taxonomy_type": "content",
        "version": "v1.0",
        "path": "taxonomies/content/test/v1.0/taxonomy.json",
        "entry_count": 10,
    }
    utils.register_taxonomy(path, entry)
    updated = json.loads(path.read_text())
    assert len(updated["taxonomies"]) == 1
    assert updated["taxonomies"][0]["entry_count"] == 10


def test_register_taxonomy_upserts_existing(tmp_path):
    existing_entry = {
        "provider": "test",
        "taxonomy_type": "content",
        "version": "v1.0",
        "path": "old/path.json",
        "entry_count": 5,
    }
    index = {"generated_at": "2026-01-01T00:00:00Z", "taxonomies": [existing_entry], "mappings": []}
    path = tmp_path / "index.json"
    path.write_text(json.dumps(index))
    new_entry = {**existing_entry, "entry_count": 15, "path": "new/path.json"}
    utils.register_taxonomy(path, new_entry)
    updated = json.loads(path.read_text())
    assert len(updated["taxonomies"]) == 1
    assert updated["taxonomies"][0]["entry_count"] == 15


def test_register_mapping_adds_new(tmp_path):
    index = {"generated_at": "2026-01-01T00:00:00Z", "taxonomies": [], "mappings": []}
    path = tmp_path / "index.json"
    path.write_text(json.dumps(index))
    entry = {
        "source_provider": "iab",
        "source_version": "v1.0",
        "target_provider": "xandr",
        "target_version": "latest",
        "taxonomy_type": "ad_product",
        "canonical": True,
        "path": "mappings/ad_product/iab_v1.0__xandr_latest/mapping.json",
        "total_source_entries": 87,
        "mapped_entries": 87,
    }
    utils.register_mapping(path, entry)
    updated = json.loads(path.read_text())
    assert len(updated["mappings"]) == 1


def test_register_mapping_upserts_existing(tmp_path):
    entry = {
        "source_provider": "iab",
        "source_version": "v1.0",
        "target_provider": "xandr",
        "target_version": "latest",
        "taxonomy_type": "ad_product",
        "canonical": True,
        "path": "old.json",
        "total_source_entries": 80,
        "mapped_entries": 80,
    }
    index = {"generated_at": "2026-01-01T00:00:00Z", "taxonomies": [], "mappings": [entry]}
    path = tmp_path / "index.json"
    path.write_text(json.dumps(index))
    updated_entry = {**entry, "mapped_entries": 87}
    utils.register_mapping(path, updated_entry)
    result = json.loads(path.read_text())
    assert len(result["mappings"]) == 1
    assert result["mappings"][0]["mapped_entries"] == 87
