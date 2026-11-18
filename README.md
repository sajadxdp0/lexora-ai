# Lexora

**Document question-answering backend with cited sources and SSE streaming.**

The LLM call is the easy part of RAG. Lexora is the surrounding service: validated document uploads, background extraction and chunking, per-user FAISS vector isolation, a Redis retrieval cache, and answers streamed over Server-Sent Events with the source chunks that backed them.

## Design notes

- **Per-tenant vector isolation.** Each user's embeddings live in a separate FAISS index on disk rather than a shared index with metadata filtering, so a bug in query construction cannot leak chunks across users. Deletion rebuilds that user's index; moving to `pgvector` is the documented path once per-user corpus sizes outgrow local files.
- **Dual-mode ingestion.** Document parsing, chunking, and embedding run through the same pipeline whether executed inline in local development or dispatched to a Celery worker in production.
- **Redis for two bounded jobs.** A 1-hour user-scoped retrieval cache avoids re-embedding identical queries, and a JWT `jti` blocklist handles token revocation on logout and refresh rotation.
- **Operational surface.** `/health` and `/ready` verify database and Redis connectivity; `/metrics` exposes Prometheus counters and histograms; logs are structured JSON via `structlog`.

## Stack

Python 3.11 · FastAPI · PostgreSQL (async SQLAlchemy) · Redis · Celery · FAISS · OpenAI · Docker

## Where to look

- `app/services/retrieval_service.py` — query embedding, top-k search, deduplication, and context assembly
- `app/services/vector_service.py` — per-user FAISS index lifecycle and rebuild-on-delete
- `app/services/chat_service.py` — conversation persistence and SSE answer streaming
- `app/core/token_blacklist.py` — Redis-backed JWT revocation shared across auth routes
- `scripts/eval_retrieval.py` — deterministic retrieval recall probe that runs without an OpenAI key

## Running locally

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d postgres redis
uvicorn app.main:app --reload
```

Interactive API docs are served at `/docs`.

## Testing

```bash
python -m pytest
python scripts/eval_retrieval.py --top-k 3
```

The test suite runs against an in-memory SQLite override with stubbed embeddings, so it needs no live OpenAI key.

## Documentation

[Architecture](docs/architecture.md) · [API](docs/api.md) · [Database](docs/database.md) · [Engineering decisions](docs/engineering-decisions.md) · [Retrieval evaluation](EVAL.md) · [Security](SECURITY.md) · [Deployment](DEPLOYMENT.md)

MIT License.
