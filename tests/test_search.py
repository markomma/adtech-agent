import pytest
from adtech_crosswalk.search import BM25Index

def test_exact_match(small_index):
    engine = BM25Index(small_index)
    results = engine.query("beer", limit=5, min_score=0.0)
    assert len(results) > 0
    assert results[0]["category_id"] == "1"

def test_results_sorted_by_score(small_index):
    engine = BM25Index(small_index)
    results = engine.query("alcohol", limit=5, min_score=0.0)
    scores = [r["relevance_score"] for r in results]
    assert scores == sorted(scores, reverse=True)

def test_min_score_filters(small_index):
    engine = BM25Index(small_index)
    results = engine.query("beer", limit=5, min_score=0.9)
    assert all(r["relevance_score"] >= 0.9 for r in results)

def test_no_match_returns_empty(small_index):
    engine = BM25Index(small_index)
    results = engine.query("completely unrelated xyzzy", limit=5, min_score=0.0)
    assert results == []

def test_limit_respected(small_index):
    engine = BM25Index(small_index)
    results = engine.query("alcohol", limit=2, min_score=0.0)
    assert len(results) <= 2

def test_result_has_required_fields(small_index):
    engine = BM25Index(small_index)
    results = engine.query("beer", limit=1, min_score=0.0)
    assert len(results) == 1
    r = results[0]
    assert "category_id" in r
    assert "category_name" in r
    assert "full_path" in r
    assert "relevance_score" in r

def test_empty_query_returns_empty(small_index):
    engine = BM25Index(small_index)
    assert engine.query("", limit=5, min_score=0.0) == []

def test_stopword_only_query_returns_empty(small_index):
    engine = BM25Index(small_index)
    assert engine.query("the and or", limit=5, min_score=0.0) == []

def test_real_iab_beer_query():
    from adtech_crosswalk.loader import Loader
    loader = Loader()
    index = loader.get_search_index("iab", "v2.0")
    engine = BM25Index(index)
    results = engine.query("beer", limit=5, min_score=0.0)
    assert any(r["category_id"] == "1004" for r in results)

def test_real_iab_beer_is_top_result():
    from adtech_crosswalk.loader import Loader
    loader = Loader()
    index = loader.get_search_index("iab", "v2.0")
    engine = BM25Index(index)
    results = engine.query("beer", limit=5, min_score=0.0)
    assert results[0]["category_id"] == "1004"
