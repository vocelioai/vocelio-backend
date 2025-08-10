## API Gateway Container & Deployment Reference

This document consolidates the build and deployment configuration for the API Gateway. The real build uses `Dockerfile` plus service-specific `railway.toml`; previous `Dockerfile.txt` (now removed) mixed multiple syntaxes and pinned obsolete dependency versions, which caused parsing errors.

### 1. Production Dockerfile (authoritative)
```
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev ffmpeg \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
COPY constraints.txt /app/constraints.txt
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip install --no-cache-dir -r /app/requirements.txt -c /app/constraints.txt
COPY . /app
RUN chmod +x start.sh
ENV PYTHONPATH=/app:/app/src
EXPOSE 8000
CMD ["./start.sh"]
```

### 2. Railway Deployment Snippet
```
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "sh -c 'python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}'"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

Environment variables are injected via the Railway dashboard (secrets) rather than committed.

### 3. Requirements Strategy
Service `requirements.txt` includes:
```
-c ../../constraints.txt
fastapi
starlette
uvicorn[standard]
httpx
pydantic
pydantic-core
python-dotenv
asyncpg
python-jose[cryptography]
python-multipart
structlog
pytest
pytest-asyncio
```
All versions are centrally pinned in `constraints.txt`; avoid adding `==` pins here.

### 4. Local Development (docker-compose excerpt)
```
services:
  api-gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./src:/app/src
      - ./shared:/app/shared
```

### 5. Health Check
Expose `/health` endpoint; Dockerfile includes a curl-based HEALTHCHECK (can be re-added if needed using base image shell tools).

### 6. Rationale for Cleanup
- Removed obsolete pinned versions (e.g., `fastapi==0.104.1`).
- Eliminated mixed-format file that produced Docker parser errors (Unknown instruction lines like `[env]`).
- Ensures single source of truth & clearer CI linting.

### 7. Next Steps
If any documentation referenced `Dockerfile.txt`, update links to this file.
