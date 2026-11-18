# Lexora

Document question-answering with cited sources.

Upload PDFs, text files, or DOCX documents and ask questions against them. Lexora handles validation, chunking, embedding, retrieval, and streaming, so answers arrive with the source chunks that produced them rather than a plausible sentence.

## Features

- JWT authentication with refresh, logout, and token revocation
- Validated uploads with status tracking, pagination, and deletion
- Chunking and embedding into per-user FAISS indexes
- Redis-backed retrieval cache and Celery ingestion workers
- SSE chat streaming with persisted conversation history
- Health and readiness checks, Prometheus metrics, structured logs

## Stack

Python · FastAPI · PostgreSQL · Redis · Celery · FAISS · OpenAI

## Quick start

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d postgres redis
uvicorn app.main:app --reload
```

API docs are at `/docs` and health at `/health`.

## Tests

```bash
python -m pytest
```

## Documentation

[Architecture](docs/architecture.md) · [API](docs/api.md) · [Security](SECURITY.md) · [Deployment](DEPLOYMENT.md)

MIT licensed.
