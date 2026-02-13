"""
Ingestion script — parse, chunk, embed, and index all documents.
Run: python scripts/ingest.py
"""
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import DOCUMENTS_DIR
from backend.database import SessionLocal
from backend.models import Document
from backend.services.parser import parse_document
from backend.services.chunker import chunk_document_segments
from backend.services.embedder import ensure_collection, embed_and_upsert
from backend.services.bm25_index import create_bm25_index, index_chunks


def load_manifest() -> list[dict]:
    """Load the document manifest."""
    manifest_path = DOCUMENTS_DIR / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest.json not found at {manifest_path}")
        sys.exit(1)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def ingest_all():
    """Run the full ingestion pipeline."""
    print("=== EKIP Document Ingestion ===\n")

    manifest = load_manifest()
    print(f"Found {len(manifest)} documents in manifest.\n")

    # Ensure Qdrant collection exists
    ensure_collection()

    # Create fresh BM25 index
    create_bm25_index()

    # Database session for document metadata
    db = SessionLocal()

    total_chunks = 0
    success_count = 0

    for entry in manifest:
        file_path = DOCUMENTS_DIR / entry["path"]
        title = entry["title"]
        department = entry["department"]
        classification = entry["classification"]

        print(f"  [{department}] {title}")

        if not file_path.exists():
            print(f"    ⚠ File not found: {file_path}, skipping.")
            continue

        # 1. Parse
        try:
            segments = parse_document(file_path)
        except Exception as e:
            print(f"    ⚠ Parse error: {e}, skipping.")
            continue

        if not segments:
            print(f"    ⚠ No text extracted, skipping.")
            continue

        # 2. Chunk
        chunks = chunk_document_segments(segments)
        print(f"    → {len(segments)} segments → {len(chunks)} chunks")

        # 3. Save document metadata to PostgreSQL
        import uuid
        doc_id = str(uuid.uuid4())

        existing = db.query(Document).filter(Document.title == title).first()
        if existing:
            doc_id = existing.id
            print(f"    → Document already in DB (id={doc_id[:8]}...), re-indexing.")
        else:
            doc = Document(
                id=doc_id,
                title=title,
                department=department,
                classification=classification,
                file_path=str(entry["path"]),
            )
            db.add(doc)
            db.commit()
            print(f"    → Saved to PostgreSQL (id={doc_id[:8]}...)")

        # 4. Embed and upsert to Qdrant
        n_vectors = embed_and_upsert(
            chunks=chunks,
            doc_id=doc_id,
            doc_title=title,
            department=department,
            classification=classification,
        )
        print(f"    → {n_vectors} vectors upserted to Qdrant")

        # 5. Index in BM25
        n_bm25 = index_chunks(
            chunks=chunks,
            doc_id=doc_id,
            doc_title=title,
            department=department,
            classification=classification,
        )
        print(f"    → {n_bm25} chunks indexed in Whoosh BM25")

        total_chunks += len(chunks)
        success_count += 1
        print()

    db.close()

    print(f"=== Done! Ingested {success_count}/{len(manifest)} documents, {total_chunks} chunks total. ===")


if __name__ == "__main__":
    ingest_all()
