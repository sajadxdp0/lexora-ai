# Lexora

Upload documents, ask questions, get answers with the source chunks cited.

Retrieval, auth, and ingestion are handled end to end: validated uploads, chunking and embedding, per-user FAISS isolation, cached retrieval, Celery workers, and answers streamed over SSE.

Python · FastAPI · PostgreSQL · Redis · Celery · FAISS

## Run

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d postgres redis
uvicorn app.main:app --reload
```

API docs at `/docs`, health at `/health`.

## Test

```bash
python -m pytest
```

Design notes live in [docs](docs/architecture.md).
