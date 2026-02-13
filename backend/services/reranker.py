"""
Cross-encoder reranker — re-scores query-chunk pairs for better precision.
"""
from sentence_transformers import CrossEncoder
from backend.config import RERANKER_MODEL

# ── Singleton ──
_reranker = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        print(f"  Loading reranker: {RERANKER_MODEL} ...")
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank(query: str, candidates: list[dict], top_n: int = 8) -> list[dict]:
    """
    Re-score candidates using a cross-encoder model.

    Args:
        query: The user's search query.
        candidates: List of chunk dicts from hybrid search.
        top_n: Number of top results to return.

    Returns:
        Re-ranked list of chunk dicts with 'rerank_score' field.
    """
    if not candidates:
        return []

    reranker = get_reranker()

    # Build (query, passage) pairs
    pairs = [(query, c["text"]) for c in candidates]

    # Score all pairs
    scores = reranker.predict(pairs)

    # Attach scores to candidates
    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)

    # Sort by rerank score descending
    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_n]
