import json
from unittest.mock import patch

import pytest

import ingest_xandr


IAB_SUPPORT_MD = """
# IAB Content Taxonomy Support

Some intro text.

| Xandr Category | Xandr ID | IAB v1.0 | IAB v2.0 |
|---|---|---|---|
| Arts & Entertainment | 25 | IAB1 | 1 |
| Automotive | 26 | IAB2 | 2 |
| Business | 27 | IAB3 | 3 |
| Entertainment | 28 | IAB1 | 1 |
| Health & Fitness | 29 | IAB7 | 7 |
| Home & Garden | 30 | IAB10 | 10 |
| News | 31 | IAB12 | 12 |
| Sports | 32 | IAB17 | 17 |
| Technology | 33 | IAB19 | 19 |
| Travel | 34 | IAB20 | 20 |
| Food & Drink | 35 | IAB8 | 8 |
| Finance | 36 | IAB13 | 13 |
| Education | 37 | IAB5 | 5 |
| Society | 38 | IAB14 | 14 |
| Pets | 39 | IAB16 | 16 |
| Religion | 40 | IAB23 | 23 |
| Science | 41 | IAB15 | 15 |
| Shopping | 42 | IAB22 | 22 |
| Style | 43 | IAB18 | 18 |
| Family | 44 | IAB6 | 6 |
| Law | 45 | IAB11 | 11 |
| Real Estate | 46 | IAB21 | 21 |
| Politics | 47 | IAB11 | 11 |
| Career | 48 | IAB4 | 4 |
| Environment | 49 | IAB9 | 9 |
| Hobbies | 50 | IAB9 | 9 |
| Video Games | 51 | IAB1 | 1 |
| Music | 52 | IAB1 | 1 |
| Movies | 53 | IAB1 | 1 |
| Books | 54 | IAB1 | 1 |
| Radio | 55 | IAB1 | 1 |
| Mature | 56 | IAB25 | 25 |
| Illegal Content | 57 | IAB26 | 26 |
| Sensitive | 58 | IAB25 | 25 |
| Unknown | 210 | | |
| Uncategorized | 211 | | |
| Testing | 212 | | |
| Other | 213 | | |
| Unbranded | 214 | | |
| Default | 215 | | |
| Placeholder | 216 | | |
| Spare | 217 | | |
| Overflow | 218 | | |
| Buffer | 219 | | |
| Extra | 220 | | |
| Additional | 221 | | |
| Supplemental | 222 | | |
| Extended | 223 | | |
| Reserved | 224 | | |
| Legacy | 225 | | |
| Deprecated | 226 | | |
| Archive | 227 | | |
| Historical | 228 | | |
| Old | 229 | | |
| New | 230 | | |
| Recent | 231 | | |
| Current | 232 | | |
| Active | 233 | | |
| Inactive | 234 | | |
"""

CONTENT_MD = """
# Content Category Service

| Category Name | ID | Parent ID |
|---|---|---|
| Arts | 1 | |
| Entertainment | 2 | 1 |
| Music | 3 | 1 |
| Sports | 4 | |
| Football | 5 | 4 |
| Basketball | 6 | 4 |
| Technology | 7 | |
| Mobile | 8 | 7 |
| Gaming | 9 | 7 |
| News | 10 | |
| World News | 11 | 10 |
| Local News | 12 | 10 |
| Finance | 13 | |
| Stocks | 14 | 13 |
| Real Estate | 15 | 13 |
| Health | 16 | |
| Fitness | 17 | 16 |
| Nutrition | 18 | 16 |
| Travel | 19 | |
| Destinations | 20 | 19 |
| Hotels | 21 | 19 |
| Food | 22 | |
| Restaurants | 23 | 22 |
| Recipes | 24 | 22 |
"""


@patch("ingest_xandr.fetch_url")
def test_ingest_ad_product_writes_taxonomy(mock_fetch, tmp_path):
    mock_fetch.return_value = IAB_SUPPORT_MD
    ingest_xandr.ingest_ad_product(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "ad_product" / "xandr" / "latest" / "taxonomy.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["metadata"]["provider"] == "xandr"
    assert data["metadata"]["taxonomy_type"] == "ad_product"
    assert len(data["entries"]) >= 50


@patch("ingest_xandr.fetch_url")
def test_ingest_ad_product_entry_fields(mock_fetch, tmp_path):
    mock_fetch.return_value = IAB_SUPPORT_MD
    ingest_xandr.ingest_ad_product(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "ad_product" / "xandr" / "latest" / "taxonomy.json"
    data = json.loads(out.read_text())
    entry = data["entries"][0]
    assert "id" in entry
    assert "name" in entry
    assert "full_path" in entry
    assert "parent_id" in entry


@patch("ingest_xandr.fetch_url")
def test_ingest_content_writes_taxonomy(mock_fetch, tmp_path):
    mock_fetch.return_value = CONTENT_MD
    ingest_xandr.ingest_content(repo_root=tmp_path)
    out = tmp_path / "taxonomies" / "content" / "xandr" / "latest" / "taxonomy.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data["entries"]) == 24


@patch("ingest_xandr.fetch_url")
def test_ingest_content_raises_below_floor(mock_fetch, tmp_path):
    tiny_md = "| Category Name | ID | Parent ID |\n|---|---|---|\n| Sports | 1 | |\n"
    mock_fetch.return_value = tiny_md
    with pytest.raises(ValueError, match="Expected"):
        ingest_xandr.ingest_content(repo_root=tmp_path)


@patch("ingest_xandr.fetch_url")
def test_ingest_ad_product_raises_below_floor(mock_fetch, tmp_path):
    tiny_md = (
        "| Xandr Category | Xandr ID | IAB v1.0 | IAB v2.0 |\n"
        "|---|---|---|---|\n"
        "| Arts | 25 | IAB1 | 1 |\n"
    )
    mock_fetch.return_value = tiny_md
    with pytest.raises(ValueError, match="Expected"):
        ingest_xandr.ingest_ad_product(repo_root=tmp_path)


@patch("ingest_xandr.fetch_url")
def test_ingest_detects_no_change(mock_fetch, tmp_path):
    mock_fetch.return_value = IAB_SUPPORT_MD
    ingest_xandr.ingest_ad_product(repo_root=tmp_path)
    changed = ingest_xandr.ingest_ad_product(repo_root=tmp_path)
    assert changed is False
