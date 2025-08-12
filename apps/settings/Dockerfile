# apps/settings/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for settings management
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Set Python path for proper imports
ENV PYTHONPATH=/app:/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

EXPOSE 8000

# Start the settings service
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
