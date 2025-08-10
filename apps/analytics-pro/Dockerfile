# 📊 Vocelio.ai Analytics Pro Service Dockerfile
# Based on proven FastAPI 0.112.2 compatible configuration

FROM python:3.11-slim

# System dependencies
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

# Copy requirements and install dependencies (use test requirements for now)
COPY requirements-test.txt ./requirements.txt
RUN python -m venv /opt/venv \
  && . /opt/venv/bin/activate \
  && pip install --upgrade pip wheel setuptools \
  && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Activate virtual environment and set environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="."

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8010}/health || exit 1

# Use start.sh script
CMD ["./start.sh"]
