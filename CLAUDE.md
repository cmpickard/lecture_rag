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

The backend runs a RAG pipeline: embed query → pgvector cache lookup (mode-aware) → if miss, classify query → pgvector similarity search → build prompt with retrieved context + conversation history → call OpenAI → write to cache if cacheable.

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
- Tables initialized from `src/models/conversations.sql`, `src/models/data_chunks.sql`, and `src/models/response_cache.sql`

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
| `lecture_rag_backend/src/services/cache_lookup.py` | pgvector cache similarity search (mode-aware, threshold 0.92) |
| `lecture_rag_backend/src/services/cache_write.py` | Insert cacheable responses into `response_cache` |
| `lecture_rag_backend/src/services/classify_query.py` | Cheap LLM call to classify query as cacheable (YES/NO) |
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
CLASSIFY_MODEL = "gpt-4.1-nano"           # Cheap classifier for cache eligibility
CLASSIFY_MODEL_PROMPT = "./src/data/classify_prompt.md"
```

## Caching

Cacheable queries (standalone explanation requests like "Explain X") are stored in the `response_cache` table and reused on similar future queries, skipping the main LLM call entirely.

**Order of operations per request:**
1. Embed the query (`text-embedding-3-small`)
2. Cache lookup — pgvector cosine similarity against `response_cache`, filtered by `dialogue_mode`, threshold `0.92`
3. Cache hit → return cached response (still generates a summary if first turn)
4. Cache miss → classify query via cheap LLM (`gpt-4.1-nano` + `classify_prompt.md`)
5. Proceed with normal RAG pipeline
6. If classified cacheable → write response to `response_cache`

Cache entries are **mode-aware**: Instruction mode and Dialogue mode responses are stored and retrieved separately via the `dialogue_mode` boolean column on `response_cache`.
