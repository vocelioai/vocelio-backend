FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-pip \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project structure to maintain imports
COPY ../../apps /app/apps
COPY ../../shared /app/shared

# Copy specific requirements file from knowledge-base directory
COPY apps/knowledge-base/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8011 (as per docker-compose)
EXPOSE 8011

# Run the knowledge-base service
CMD ["uvicorn", "apps.knowledge-base.src.main:app", "--host", "0.0.0.0", "--port", "8011"]
