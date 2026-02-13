"""
BM25 keyword search using Whoosh.
"""
from pathlib import Path
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser
from whoosh import scoring

from backend.config import BM25_INDEX_DIR


# ── Whoosh Schema ──
SCHEMA = Schema(
    chunk_id=ID(stored=True, unique=True),
    doc_id=ID(stored=True),
    doc_title=TEXT(stored=True),
    department=ID(stored=True),
    classification=ID(stored=True),
    text=TEXT(stored=True),
)


def ensure_index_dir():
    """Create the index directory if it doesn't exist."""
    BM25_INDEX_DIR.mkdir(parents=True, exist_ok=True)


def create_bm25_index():
    """Create a fresh Whoosh index (overwrites existing)."""
    ensure_index_dir()
    ix = create_in(str(BM25_INDEX_DIR), SCHEMA)
    print(f"  Created BM25 index at: {BM25_INDEX_DIR}")
    return ix


def get_bm25_index():
    """Open existing index or create a new one."""
    ensure_index_dir()
    if exists_in(str(BM25_INDEX_DIR)):
        return open_dir(str(BM25_INDEX_DIR))
    return create_bm25_index()


def index_chunks(
    chunks: list[str],
    doc_id: str,
    doc_title: str,
    department: str,
    classification: str,
) -> int:
    """
    Index text chunks into BM25.

    Returns:
        Number of chunks indexed.
    """
    ix = get_bm25_index()
    writer = ix.writer()

    for i, chunk_text in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"
        writer.update_document(
            chunk_id=chunk_id,
            doc_id=doc_id,
            doc_title=doc_title,
            department=department,
            classification=classification,
            text=chunk_text,
        )

    writer.commit()
    return len(chunks)


def keyword_search(
    query: str,
    allowed_roles: list[str] | None = None,
    department_filter: str | None = None,
    top_k: int = 20,
) -> list[dict]:
    """
    Search BM25 index for keyword matches.

    Permission filtering is done post-retrieval since Whoosh doesn't support
    complex role-based filters natively.

    Returns:
        List of dicts with text, doc_id, doc_title, department, score.
    """
    ix = get_bm25_index()
    parser = MultifieldParser(["text", "doc_title"], schema=ix.schema)
    parsed_query = parser.parse(query)

    results = []
    with ix.searcher(weighting=scoring.BM25F()) as searcher:
        hits = searcher.search(parsed_query, limit=top_k * 2)  # over-fetch for filtering

        for hit in hits:
            # Department filter
            if department_filter and hit["department"] != department_filter:
                continue

            results.append({
                "text": hit["text"],
                "doc_id": hit["doc_id"],
                "doc_title": str(hit["doc_title"]),
                "department": hit["department"],
                "classification": hit.get("classification", "public"),
                "score": hit.score,
                "source": "bm25",
            })

            if len(results) >= top_k:
                break

    return results
