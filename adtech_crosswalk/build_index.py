"""Build BM25 search indices for all taxonomy.json files."""
import json
import math
import re
from pathlib import Path

STOPWORDS = {"the", "a", "an", "and", "or", "of", "in", "for", "to", "is", "are"}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if t not in STOPWORDS and len(t) > 1]


def build_index(taxonomy: dict) -> dict:
    documents: dict[str, dict] = {}
    for entry in taxonomy["entries"]:
        text = f"{entry['name']} {entry.get('full_path', entry['name'])}"
        # deduplicate while preserving order so avgdl/dl reflect unique terms
        tokens = list(dict.fromkeys(tokenize(text)))
        documents[entry["id"]] = {
            "name": entry["name"],
            "full_path": entry.get("full_path", entry["name"]),
            "tokens": tokens,
            "dl": len(tokens),
        }

    corpus_size = len(documents)
    avgdl = sum(d["dl"] for d in documents.values()) / corpus_size if corpus_size else 1.0

    inverted: dict[str, list[str]] = {}
    for doc_id, doc in documents.items():
        for term in set(doc["tokens"]):
            inverted.setdefault(term, []).append(doc_id)

    idf: dict[str, float] = {
        term: math.log((corpus_size - len(ids) + 0.5) / (len(ids) + 0.5) + 1)
        for term, ids in inverted.items()
    }

    return {
        "corpus_size": corpus_size,
        "avgdl": avgdl,
        "idf": idf,
        "inverted": inverted,
        "documents": documents,
    }


def main() -> None:
    repo_root = Path(__file__).parent.parent
    for taxonomy_path in sorted(repo_root.glob("taxonomies/**/taxonomy.json")):
        print(f"Building index: {taxonomy_path.relative_to(repo_root)}")
        with open(taxonomy_path) as f:
            taxonomy = json.load(f)
        index = build_index(taxonomy)
        index_path = taxonomy_path.parent / "taxonomy.search-index.json"
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)
        print(f"  → {index['corpus_size']} entries indexed")


if __name__ == "__main__":
    main()
