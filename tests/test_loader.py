import pytest
from adtech_crosswalk.loader import Loader

@pytest.fixture(scope="module")
def loader():
    return Loader()

def test_list_taxonomies_returns_dict(loader):
    result = loader.list_taxonomies()
    assert "taxonomies" in result

def test_list_taxonomies_has_iab_and_google(loader):
    result = loader.list_taxonomies()
    providers = [t["provider"] for t in result["taxonomies"]]
    assert "iab" in providers
    assert "google" in providers

def test_list_taxonomies_has_mapped_to(loader):
    result = loader.list_taxonomies()
    iab = next(
        t
        for t in result["taxonomies"]
        if t["provider"] == "iab" and t["version"] == "v2.0" and t["taxonomy_type"] == "ad_product"
    )
    assert "google" in iab["mapped_to"]

def test_list_taxonomies_mapped_to_is_scoped_to_taxonomy_type(loader):
    result = loader.list_taxonomies()
    iab_content = next(
        t
        for t in result["taxonomies"]
        if t["provider"] == "iab" and t["version"] == "v1.0" and t["taxonomy_type"] == "content"
    )
    assert "google" not in iab_content["mapped_to"]

def test_list_taxonomies_has_entry_count(loader):
    result = loader.list_taxonomies()
    iab = next(
        t
        for t in result["taxonomies"]
        if t["provider"] == "iab" and t["version"] == "v2.0" and t["taxonomy_type"] == "ad_product"
    )
    assert iab["entry_count"] == 583

def test_get_latest_version(loader):
    assert loader.get_latest_version("iab") == "v2.0"

def test_get_latest_version_unknown_provider(loader):
    assert loader.get_latest_version("nonexistent") is None

def test_get_taxonomy_valid(loader):
    taxonomy = loader.get_taxonomy("iab", "v2.0")
    assert taxonomy is not None
    assert "entries" in taxonomy
    assert len(taxonomy["entries"]) == 583

def test_get_taxonomy_invalid(loader):
    assert loader.get_taxonomy("nonexistent", "v9.9") is None

def test_get_search_index_valid(loader):
    index = loader.get_search_index("iab", "v2.0")
    assert index is not None
    assert "idf" in index
    assert "documents" in index
    assert "inverted" in index

def test_get_search_index_invalid(loader):
    assert loader.get_search_index("nonexistent", "v9.9") is None

def test_get_mapping_entries_beer(loader):
    entries = loader.get_mapping_entries("iab", "v2.0", "1004")
    assert isinstance(entries, list)
    assert len(entries) > 0
    assert all("target_id" in e for e in entries)
    assert all("confidence" in e for e in entries)
    assert all("target_provider" in e for e in entries)

def test_get_mapping_entries_unknown_category(loader):
    entries = loader.get_mapping_entries("iab", "v2.0", "99999")
    assert entries == []

def test_get_mapping_entries_filtered_by_target_provider(loader):
    entries = loader.get_mapping_entries("iab", "v2.0", "1004", target_provider="google")
    assert all(e["target_provider"] == "google" for e in entries)
