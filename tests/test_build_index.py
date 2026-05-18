from adtech_crosswalk.build_index import tokenize, build_index

def test_tokenize_simple():
    assert tokenize("Beer") == ["beer"]

def test_tokenize_path_separator():
    assert tokenize("Alcohol > Beer") == ["alcohol", "beer"]

def test_tokenize_ampersand():
    assert tokenize("Food, Beverages & Tobacco") == ["food", "beverages", "tobacco"]

def test_tokenize_removes_stopwords():
    tokens = tokenize("the a an and or of")
    assert tokens == []

def test_tokenize_short_words():
    # single-char tokens are dropped
    assert "a" not in tokenize("a beer")

def test_build_index_structure(small_taxonomy):
    index = build_index(small_taxonomy)
    assert index["corpus_size"] == 3
    assert "beer" in index["idf"]
    assert "alcohol" in index["idf"]
    assert "1" in index["documents"]

def test_build_index_tokens(small_taxonomy):
    index = build_index(small_taxonomy)
    assert index["documents"]["1"]["tokens"] == ["beer", "alcohol"]
    assert index["documents"]["1"]["dl"] == 2

def test_build_index_idf_ordering(small_taxonomy):
    # "alcohol" appears in all 3 docs → lower IDF than "beer" (1 doc)
    index = build_index(small_taxonomy)
    assert index["idf"]["alcohol"] < index["idf"]["beer"]

def test_build_index_inverted(small_taxonomy):
    index = build_index(small_taxonomy)
    assert "1" in index["inverted"]["beer"]
    assert set(index["inverted"]["alcohol"]) == {"1", "2", "3"}

def test_build_index_inverted_order_is_deterministic(small_taxonomy):
    index = build_index(small_taxonomy)
    assert list(index["inverted"]) == ["beer", "alcohol", "wine", "spirits"]

def test_build_index_avgdl(small_taxonomy):
    index = build_index(small_taxonomy)
    assert index["avgdl"] == 2.0
