#!/bin/sh
# Startup script for api-gateway service
PORT=${PORT:-8000}
echo "🚀 Starting Vocelio.ai API Gateway on port $PORT..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$PORT"

# Create temporary directory for uploads
mkdir -p tmp/uploads

# Set permissions
chmod 755 logs tmp

# Print configuration info
echo "📊 Configuration:"
echo "   Environment: ${ENVIRONMENT:-development}"
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
