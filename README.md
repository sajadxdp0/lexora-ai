# Lexora

Document Q&A with cited sources.

Python · FastAPI · PostgreSQL · Redis · Celery · FAISS

Upload → chunk → embed → retrieve → stream an answer. Per-user vectors, cached retrieval, JWT auth.

```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d postgres redis
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Tests: `python -m pytest`
