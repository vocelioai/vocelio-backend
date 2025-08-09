# Vocelio.ai AI Agents Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8002

# System deps
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Install requirements first (cache layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Wait script to ensure Postgres & Redis are ready
RUN set -eux; \
    cat > /app/wait_for_services.py <<'EOF'
import os, time, sys, asyncio, socket
POSTGRES = (os.getenv('POSTGRES_HOST','postgres'), int(os.getenv('POSTGRES_PORT','5432')))
REDIS = (os.getenv('REDIS_HOST','redis'), int(os.getenv('REDIS_PORT','6379')))
TIMEOUT=float(os.getenv('STARTUP_WAIT_TIMEOUT','40'))
async def check_postgres():
    try:
        import asyncpg
        conn = await asyncpg.connect(host=POSTGRES[0], port=POSTGRES[1], user=os.getenv('POSTGRES_USER','postgres'), password=os.getenv('POSTGRES_PASSWORD','password'), database=os.getenv('POSTGRES_DB','vocelio'), timeout=3)
        await conn.close(); return True
    except Exception: return False
def check_socket(target):
    try:
        import socket as s
        with s.create_connection(target, timeout=1.5): return True
    except Exception: return False
async def main():
    start=time.time(); print('[wait] (ai-agents) waiting for services...')
    while True:
        if await check_postgres() and check_socket(REDIS):
            print(f'[wait] dependencies ready in {time.time()-start:.1f}s'); return
        if time.time()-start>TIMEOUT: print('[wait] timeout', file=sys.stderr); sys.exit(1)
        time.sleep(1.2)
if __name__=='__main__': asyncio.run(main())
EOF

# Non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8002/health')"

CMD ["bash", "-c", "python wait_for_services.py && python main.py"]
