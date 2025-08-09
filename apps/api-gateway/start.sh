#!/bin/bash

# Vocelio API Gateway Startup Script
# Creates necessary directories and starts the application

echo "🚀 Starting Vocelio.ai API Gateway..."

# Create logs directory if it doesn't exist
mkdir -p logs

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
