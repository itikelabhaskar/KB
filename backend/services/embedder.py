"""
Embedding service — encodes text chunks and upserts into Qdrant.
"""
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue,
)
import uuid

from backend.config import (
    QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION,
    EMBEDDING_MODEL, EMBEDDING_DIM,
)

# ── Singletons (loaded once, reused) ──
_model = None
_client = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"  Loading embedding model: {EMBEDDING_MODEL} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def ensure_collection():
    """Create the Qdrant collection if it doesn't exist."""
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        print(f"  Created Qdrant collection: {QDRANT_COLLECTION}")
    else:
        print(f"  Qdrant collection already exists: {QDRANT_COLLECTION}")


def embed_and_upsert(
    chunks: list[str],
    doc_id: str,
    doc_title: str,
    department: str,
    classification: str,
) -> int:
    """
    Embed text chunks and upsert them into Qdrant.

    Returns:
        Number of points upserted.
    """
    if not chunks:
        return 0

    model = get_embedding_model()
    client = get_qdrant_client()

    # Embed all chunks in one batch
    vectors = model.encode(chunks, show_progress_bar=False).tolist()

    # Build access_roles list based on classification + department
    if classification == "public":
        access_roles = ["Employee", "HR", "Engineer", "Sales", "Admin"]
    else:
        # restricted: only the department's role + admin
        access_roles = [department_to_role(department), "Admin"]

    # Create points
    points = []
    for i, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
        point_id = str(uuid.uuid4())
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": chunk_text,
                    "doc_id": doc_id,
                    "doc_title": doc_title,
                    "department": department,
                    "classification": classification,
                    "access_roles": access_roles,
                    "chunk_index": i,
                },
            )
        )

    # Upsert in batches of 64
    batch_size = 64
    for start in range(0, len(points), batch_size):
        batch = points[start : start + batch_size]
        client.upsert(collection_name=QDRANT_COLLECTION, points=batch)

    return len(points)


def department_to_role(department: str) -> str:
    """Map department name to role name."""
    mapping = {
        "HR": "HR",
        "Engineering": "Engineer",
        "Sales": "Sales",
    }
    return mapping.get(department, "Employee")


def vector_search(
    query: str,
    qdrant_filter: Filter | None = None,
    top_k: int = 20,
) -> list[dict]:
    """
    Search Qdrant for chunks similar to the query.

    Returns:
        List of dicts with text, doc_id, doc_title, department, score.
    """
    model = get_embedding_model()
    client = get_qdrant_client()

    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        query_filter=qdrant_filter,
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "text": hit.payload["text"],
            "doc_id": hit.payload["doc_id"],
            "doc_title": hit.payload["doc_title"],
            "department": hit.payload["department"],
            "classification": hit.payload.get("classification", "public"),
            "chunk_index": hit.payload.get("chunk_index", 0),
            "score": hit.score,
            "source": "vector",
        }
        for hit in results.points
    ]
