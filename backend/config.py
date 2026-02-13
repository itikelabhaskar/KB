"""
Application configuration — loads environment variables from .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# PostgreSQL
POSTGRES_USER = os.getenv("POSTGRES_USER", "ekip")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ekip_dev_2026")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ekip")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = "enterprise_docs"

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "ekip-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"

# Paths
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
BM25_INDEX_DIR = PROJECT_ROOT / "indexdir"

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Reranker model
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
