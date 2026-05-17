"""BM25 search engine over pre-built taxonomy indices."""
import re

STOPWORDS = {"the", "a", "an", "and", "or", "of", "in", "for", "to", "is", "are"}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if t not in STOPWORDS and len(t) > 1]


class BM25Index:
    def __init__(self, index_data: dict, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.avgdl: float = index_data["avgdl"]
        self.idf: dict[str, float] = index_data["idf"]
        self.inverted: dict[str, list[str]] = index_data["inverted"]
        self.documents: dict[str, dict] = index_data["documents"]

    def _score(self, tokens: list[str]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for term in tokens:
            if term not in self.inverted:
                continue
            idf = self.idf[term]
            for doc_id in self.inverted[term]:
                doc = self.documents[doc_id]
                tf = doc["tokens"].count(term)
                dl = doc["dl"]
                tf_score = (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                )
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * tf_score
        return scores

    def query(self, raw_query: str, limit: int = 5, min_score: float = 0.75) -> list[dict]:
        tokens = tokenize(raw_query)
        if not tokens:
            return []
        scores = self._score(tokens)
        if not scores:
            return []
        max_score = max(scores.values())
        if max_score == 0:
            return []
        results = []
        for doc_id, raw in sorted(scores.items(), key=lambda x: -x[1]):
            normalized = raw / max_score
            if normalized < min_score:
                break
            if len(results) >= limit:
                break
            doc = self.documents[doc_id]
            results.append({
                "category_id": doc_id,
                "category_name": doc["name"],
                "full_path": doc["full_path"],
                "relevance_score": round(normalized, 4),
            })
        return results
