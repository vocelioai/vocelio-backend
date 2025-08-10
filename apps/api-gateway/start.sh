#!/bin/sh
# Startup script for api-gateway service

# Set default port
PORT=${PORT:-8000}

# Create temporary directory for uploads
mkdir -p tmp/uploads logs

# Set permissions
chmod 755 logs tmp 2>/dev/null || true

# Print configuration info
echo "📊 Configuration:"
echo "   Environment: ${ENVIRONMENT:-development}"
echo "   Port: $PORT"
echo "   Python Path: $PYTHONPATH"

echo "🚀 Starting Vocelio.ai API Gateway on port $PORT..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$PORT"
echo "   Log Level: ${LOG_LEVEL:-INFO}"
echo "   Redis URL: ${REDIS_URL:+configured}"
echo "   Database URL: ${DATABASE_URL:+configured}"

# Start the application
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🌟 Starting in PRODUCTION mode..."
    exec uvicorn apps.api-gateway.src.main:app \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --workers 4 \
        --loop asyncio \
        --no-access-log \
        --log-level info
else
    echo "🔧 Starting in DEVELOPMENT mode..."
    exec uvicorn apps.api-gateway.src.main:app \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --reload \
        --loop asyncio \
        --log-level debug
fi
