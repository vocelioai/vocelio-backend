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

# Make startup script executable  
RUN chmod +x start.sh

# Ensure package imports like "from src..." work
ENV PYTHONPATH=/app:/app/src
EXPOSE 8000
CMD ["./start.sh"]
