# apps/api-gateway/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# OS deps for wheels (psycopg, uvloop, httptools, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cache-friendly)
COPY requirements.txt /app/requirements.txt
COPY constraints.txt /app/constraints.txt
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip install --no-cache-dir -r /app/requirements.txt -c /app/constraints.txt

# App code
COPY . /app

# Ensure package imports like "from src..." work
ENV PYTHONPATH=/app:/app/src
EXPOSE 8000
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
