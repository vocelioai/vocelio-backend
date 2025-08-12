FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-pip \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY ../../apps /app/apps
COPY ../../shared /app/shared
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Python path
ENV PYTHONPATH="/app"

# Expose port
EXPOSE 8018

# Run the application
CMD ["uvicorn", "apps.notifications.src.main:app", "--host", "0.0.0.0", "--port", "8018"]
