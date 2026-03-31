# Lecture RAG — Project Guide

## Overview

**Talkrates** is an AI-powered teaching assistant for philosophy courses (PHIL 1000 & PHIL 3600). It uses Retrieval-Augmented Generation (RAG) to answer student questions about course materials using lecture slides and Q&A content stored in a PostgreSQL vector database.

Two interaction modes:
- **Instruction Mode** — concise, direct explanations (`gpt-5.4-nano`)
- **Dialogue Mode** — deeper Socratic investigation (`gpt-5.4`)

## Architecture

```
lecture_rag/
├── lecture_rag_backend/     Flask API (port 3000)
└── lecture_rag_frontend/    React + TypeScript (Vite)
```

The backend runs a RAG pipeline: embed query → pgvector similarity search → build prompt with retrieved context + conversation history → call OpenAI.

## Development

### Backend

```bash
cd lecture_rag_backend
poetry install
python app.py          # Runs on port 3000
```

Requires:
- PostgreSQL running on `localhost:5432` with database `lecture_rag` and the pgvector extension
- `OPENAI_API_KEY` in `lecture_rag_backend/.env`
- Tables initialized from `src/models/conversations.sql` and `src/models/data_chunks.sql`

### Frontend

```bash
cd lecture_rag_frontend
npm install
npm run dev            # Dev server with HMR
npm run build          # tsc -b && vite build
npm run lint           # ESLint check
```

The frontend hardcodes the backend URL as `http://localhost:3000`.

## Key Files

| File | Purpose |
|------|---------|
| `lecture_rag_backend/app.py` | Flask app entry point |
| `lecture_rag_backend/src/routes/chat.py` | API route handlers |
| `lecture_rag_backend/src/services/context_retrieval.py` | pgvector semantic search |
| `lecture_rag_backend/src/services/history_manager.py` | Conversation persistence |
| `lecture_rag_backend/src/services/prompting.py` | Prompt construction |
| `lecture_rag_backend/src/config.py` | Model names and prompt paths |
| `lecture_rag_backend/src/data/basic_prompt.md` | Instruction mode system prompt |
| `lecture_rag_backend/src/data/dialogue_prompt.md` | Dialogue mode system prompt |
| `lecture_rag_frontend/src/App.tsx` | Root component, conversation state |
| `lecture_rag_frontend/src/components/QueryForm.tsx` | Query input and mode toggle |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST /` | Submit query | Body: `{content, conversation_id, dialogue_mode}` |
| `GET /api/conversations` | Fetch conversations | Query param: `ids` (array of UUIDs) |
| `DELETE /api/delete/<id>` | Delete conversation | Returns 204 |

## Data Pipeline

Lecture content is extracted, cleaned, chunked, and embedded as JSONL files (`chunks.jsonl`, `qa_chunks.jsonl`). Scripts live in `lecture_rag_backend/src/data/slides/`:

```bash
python extract_slides.py   # Pull from Google Slides API
python clean_slides.py
python chunk_slides.py
python create_embeddings.py
```

Embeddings use `text-embedding-3-small`. Similarity cutoff for retrieval is `> 0.50` (cosine similarity via pgvector).

## Configuration

Models and prompt paths are set in `lecture_rag_backend/src/config.py`:

```python
BASIC_MODEL = "gpt-5.4-nano"
DIALOGUE_MODEL = "gpt-5.4"
```
