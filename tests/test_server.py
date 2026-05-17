from adtech_crosswalk.server import _list_taxonomies, _resolve_category, _get_mapping

def test_list_taxonomies_structure():
    result = _list_taxonomies()
    assert "taxonomies" in result
    assert isinstance(result["taxonomies"], list)

def test_list_taxonomies_has_expected_providers():
    result = _list_taxonomies()
    providers = [t["provider"] for t in result["taxonomies"]]
    assert "iab" in providers
    assert "google" in providers

def test_list_taxonomies_entry_fields():
    result = _list_taxonomies()
    t = result["taxonomies"][0]
    assert "provider" in t
    assert "version" in t
    assert "taxonomy_type" in t
    assert "entry_count" in t
    assert "mapped_to" in t
