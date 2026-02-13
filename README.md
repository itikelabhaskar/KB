# Knowledge Base (formerly EKIP)

**Internal Knowledge Assistant** — A RAG-based search platform that lets employees search across company documents (HR, Engineering, Sales) and get AI-generated answers with citations, respecting their role-based access permissions.

## Features

- **Role-Based Access Control (RBAC):** Users see only what they are allowed to see.
  - *HR* sees HR docs + General.
  - *Engineers* see Engineering docs + General.
  - *Admin* sees everything.
- **Hybrid Search:** Combines Vector Search (semantic) + Keyword Search (BM25) for best results.
- **AI Answers:** Generates answers using Google Gemini 2.5 Flash, citing specific source documents.
- **Instant Search UI:** Clean, professional interface with streaming-like experience.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Docker Desktop** (for Database & Vector Store)
- **Google Gemini API Key** (Free from [aistudio.google.com](https://aistudio.google.com/apikey))

### 1. Setup Backend

```bash
# 1. Clone & Enter
git clone https://github.com/itikelabhaskar/KB.git 
cd project

# 2. Create Virtual Environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example env file:
```bash
# Windows
copy .env.example .env
# Mac/Linux
cp .env.example .env
```
👉 **Edit `.env`** and paste your `GEMINI_API_KEY`.

### 3. Start Infrastructure (Docker)

Start PostgreSQL and Qdrant vector database:
```bash
docker compose up -d
```

### 4. Initialize Data

Create tables and seed demo users:
```bash
python scripts/init_db.py
```
*(This sets up users: Amrutha, Harshini, Tanvi, Bhaskar, Arijith)*

Index the sample documents:
```bash
python scripts/ingest.py
```
*(Processes PDF/Markdown files in `documents/` folder)*

### 5. Run Backend Server

**Run from the `project/` root directory:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API will be at: http://localhost:8000/docs

### 6. Run Frontend

Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your browser.

---

## 🧪 Testing & Evaluation

We have a built-in evaluation script to verify retrieval quality and permissions:

```bash
python scripts/evaluate.py
```
This runs 13 test cases:
- ✅ **Permissions:** Verifies Amrutha (HR) can see HR docs, but Harshini (Eng) cannot.
- ✅ **Retrieval Quality:** Checks if the correct document comes up for specific queries.
- ✅ **Latency:** Ensures search is fast (<1s).

---

## ⚠️ Troubleshooting

**Gemini API Error (429 Resource Exhausted):**
If you see "LLM unavailable", it means the free tier quota for the Gemini API is temporarily exhausted.
- The app will **fallback** to showing search results only.
- Wait ~1 minute and try again.
- **Fix:** If it persists, ensure your API key uses `gemini-2.5-flash` (checked in `backend/services/generator.py`) as older models may have zero quota.

**Port Conflicts:**
If ports 8000 (Backend) or 5432 (Postgres) are busy, kill the processes using them or update `.env` and `docker-compose.yml`.

---

## Project Structure

```
project/
├── backend/           # FastAPI App
│   ├── main.py        # Entry Point
│   ├── config.py      # Settings
│   ├── services/      # RAG Pipeline (Search, Generator)
│   ├── routers/       # API Endpoints
│   └── models/        # DB Schemas
├── frontend/          # React + Vite App
├── documents/         # Knowledge Base Content (PDF/MD)
├── scripts/           # Ingestion & Eval Scripts
├── docker-compose.yml # Infra Setup
└── requirements.txt   # Python Deps
```
