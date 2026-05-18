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


def test_resolve_beer_returns_match():
    result = _resolve_category(
        raw_category="beer",
        taxonomy_type="ad_product",
        providers=["iab"],
        version="v2.0",
        min_confidence=0.5,
        limit=5,
    )
    assert "matches" in result
    assert len(result["matches"]) > 0

def test_resolve_beer_top_result_is_beer():
    result = _resolve_category(
        raw_category="beer",
        taxonomy_type="ad_product",
        providers=["iab"],
        version="v2.0",
        min_confidence=0.5,
        limit=5,
    )
    assert result["matches"][0]["category_id"] == "1004"

def test_resolve_results_have_required_fields():
    result = _resolve_category(
        raw_category="beer",
        taxonomy_type="ad_product",
        providers=["iab"],
        version="v2.0",
        min_confidence=0.0,
        limit=1,
    )
    m = result["matches"][0]
    assert "provider" in m
    assert "version" in m
    assert "category_id" in m
    assert "category_name" in m
    assert "full_path" in m
    assert "relevance_score" in m

def test_resolve_unknown_concept_returns_empty():
    result = _resolve_category(
        raw_category="xyzzy unmatched concept",
        taxonomy_type="ad_product",
        providers=["iab"],
        version="v2.0",
        min_confidence=0.75,
        limit=5,
    )
    assert result["matches"] == []

def test_resolve_defaults_to_iab_provider():
    result = _resolve_category(
        raw_category="beer",
        taxonomy_type="ad_product",
        providers=None,
        version=None,
        min_confidence=0.5,
        limit=5,
    )
    assert all(m["provider"] == "iab" for m in result["matches"])

def test_resolve_unavailable_taxonomy_type():
    result = _resolve_category(
        raw_category="beer",
        taxonomy_type="nonexistent_type",
        providers=["iab"],
        version=None,
        min_confidence=0.75,
        limit=5,
    )
    assert "error" in result
    assert result["error"] == "taxonomy_unavailable"

def test_resolve_sorted_by_relevance():
    result = _resolve_category(
        raw_category="beer",
        taxonomy_type="ad_product",
        providers=["iab"],
        version="v2.0",
        min_confidence=0.0,
        limit=10,
    )
    scores = [m["relevance_score"] for m in result["matches"]]
    assert scores == sorted(scores, reverse=True)

def test_resolve_multi_provider():
    result = _resolve_category(
        raw_category="beer",
        taxonomy_type="ad_product",
        providers=["iab", "google"],
        version=None,
        min_confidence=0.5,
        limit=3,
    )
    providers_in_results = {m["provider"] for m in result["matches"]}
    assert "iab" in providers_in_results
    assert "google" in providers_in_results


def test_get_mapping_beer_has_source():
    result = _get_mapping("iab", "v2.0", "1004", None, 0.0)
    assert "source" in result
    assert result["source"]["category_id"] == "1004"
    assert result["source"]["category_name"] == "Beer"

def test_get_mapping_beer_has_mappings():
    result = _get_mapping("iab", "v2.0", "1004", None, 0.0)
    assert "mappings" in result
    assert len(result["mappings"]) > 0

def test_get_mapping_fields():
    result = _get_mapping("iab", "v2.0", "1004", None, 0.0)
    m = result["mappings"][0]
    assert "target_provider" in m
    assert "target_version" in m
    assert "target_id" in m
    assert "target_path" in m
    assert "confidence" in m
    assert "match_type" in m
    assert "notes" in m

def test_get_mapping_sorted_by_confidence():
    result = _get_mapping("iab", "v2.0", "1058", None, 0.0)  # Clothing
    confidences = [m["confidence"] for m in result["mappings"]]
    assert confidences == sorted(confidences, reverse=True)

def test_get_mapping_min_confidence_filters():
    result = _get_mapping("iab", "v2.0", "1004", None, 0.95)
    assert all(m["confidence"] >= 0.95 for m in result["mappings"])

def test_get_mapping_unknown_category():
    result = _get_mapping("iab", "v2.0", "99999", None, 0.75)
    assert "error" in result
    assert result["error"] == "category_not_found"

def test_get_mapping_unknown_taxonomy():
    result = _get_mapping("nonexistent", "v9.9", "1", None, 0.75)
    assert "error" in result
    assert result["error"] == "taxonomy_unavailable"

def test_get_mapping_filtered_by_target_provider():
    result = _get_mapping("iab", "v2.0", "1004", "google", 0.0)
    assert all(m["target_provider"] == "google" for m in result["mappings"])

def test_get_mapping_no_mapping_for_target():
    result = _get_mapping("iab", "v2.0", "1004", "nonexistent_provider", 0.75)
    assert "error" in result
    assert result["error"] == "no_mapping_available"
