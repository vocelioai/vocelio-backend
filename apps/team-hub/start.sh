#!/bin/bash

# 👥 Vocelio.ai Team Hub Service Startup Script

echo "🚀 Starting Vocelio.ai Team Hub Service..."
echo "=================================="

# Set PYTHONPATH for proper module imports
export PYTHONPATH=.

# Get port from environment variable or default to 8009
PORT=${PORT:-8009}

echo "📡 PORT: $PORT"
echo "🐍 PYTHONPATH: $PYTHONPATH"
echo "🔧 Python version: $(python --version)"

# Health check function
health_check() {
    echo "🏥 Running health check..."
    python -c "
import sys
try:
    from main_test import app
    print('✅ Team Hub Service health check passed')
    sys.exit(0)
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
"
}

# Run health check
health_check

# Start the Team Hub Service
echo "👥 Starting FastAPI Team Hub Service on port $PORT..."
exec uvicorn main_test:app --host 0.0.0.0 --port "$PORT"
