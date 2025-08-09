# Vocelio.ai API Gateway Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Lightweight wait script to ensure core upstream services are reachable
RUN set -eux; \
  cat > /app/wait_for_core.py <<'EOF'
import os, time, socket, sys
targets = [
    (os.getenv('OVERVIEW_SERVICE_URL','http://overview-service:8001').replace('http://','').split(':')[0], 8001),
    ('ai-agents-service', 8002),
    ('smart-campaigns-service', 8003),
]
TIMEOUT=float(os.getenv('STARTUP_WAIT_TIMEOUT','40'))
start=time.time()
print('[wait] (gateway) waiting for core services...')
for host, port in targets:
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f'[wait] {host}:{port} ready'); break
        except OSError:
            if time.time()-start>TIMEOUT:
                print(f'[wait] timeout waiting for {host}:{port}', file=sys.stderr); sys.exit(1)
            time.sleep(1)
print('[wait] core services reachable')
EOF

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Run via uvicorn using the package path (src.main:app)
CMD ["bash", "-c", "python wait_for_core.py && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
