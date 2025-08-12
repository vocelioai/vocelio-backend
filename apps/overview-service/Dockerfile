# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8001

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Add lightweight wait script (cannot reach root-level scripts from this build context)
RUN set -eux; \
  cat > /app/wait_for_services.py <<'EOF'
import os, time, sys, asyncio, socket

POSTGRES = (os.getenv('POSTGRES_HOST', 'postgres'), int(os.getenv('POSTGRES_PORT', '5432')))
REDIS = (os.getenv('REDIS_HOST', 'redis'), int(os.getenv('REDIS_PORT', '6379')))
TIMEOUT = float(os.getenv('STARTUP_WAIT_TIMEOUT', '40'))
DELAY = 1.5

async def check_postgres():
  try:
    import asyncpg
    conn = await asyncpg.connect(
      host=POSTGRES[0],
      port=POSTGRES[1],
      user=os.getenv('POSTGRES_USER','postgres'),
      password=os.getenv('POSTGRES_PASSWORD','password'),
      database=os.getenv('POSTGRES_DB','vocelio'),
      timeout=3
    )
    await conn.close()
    return True
  except Exception:
    return False

def check_socket(target):
  host, port = target
  try:
    with socket.create_connection((host, port), timeout=1.5):
      return True
  except OSError:
    return False

async def main():
  start = time.time()
  print('[wait] Waiting for Postgres & Redis readiness...')
  while True:
    pg_ready = await check_postgres()
    redis_ready = check_socket(REDIS)
    if pg_ready and redis_ready:
      print(f'[wait] All dependencies ready in {time.time()-start:.1f}s.')
      return
    if time.time() - start > TIMEOUT:
      print('[wait] Timeout waiting for services', file=sys.stderr)
      sys.exit(1)
    time.sleep(DELAY)

if __name__ == '__main__':
  asyncio.run(main())
EOF

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

# Start command
CMD ["python", "main.py"]
