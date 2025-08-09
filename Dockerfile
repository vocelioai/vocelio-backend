# Root Dockerfile for Vocelio Backend (API Gateway aggregate build)
# Provides required system dependencies for heavier Python libs (librosa, soundfile, etc.)

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# Install system dependencies (audio, build, networking, postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libsndfile1 \
    ffmpeg \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for better layer caching
COPY requirements.txt ./

# (Optional) If you later split heavy deps, uncomment and COPY requirements-core.txt first
# COPY requirements-core.txt ./

# Create virtual environment manually for consistency
RUN python -m venv /opt/venv \
  && . /opt/venv/bin/activate \
  && pip install --upgrade pip wheel setuptools \
  && pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Runtime user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Simple healthcheck hitting gateway health endpoint
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Start API Gateway (use --app-dir for hyphenated path safety if needed)
CMD ["bash", "-c", "uvicorn --app-dir apps/api-gateway src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
