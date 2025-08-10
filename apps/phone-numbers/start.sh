#!/bin/bash

# 📞 Vocelio.ai Phone Numbers Service Startup Script

echo "🚀 Starting Vocelio.ai Phone Numbers Service..."
echo "=================================="

# Set PYTHONPATH for proper module imports
export PYTHONPATH=.

# Get port from environment variable or default to 8008
PORT=${PORT:-8008}

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
    print('✅ Phone Numbers Service health check passed')
    sys.exit(0)
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
"
}

# Run health check
health_check

# Start the Phone Numbers Service
echo "📞 Starting FastAPI Phone Numbers Service on port $PORT..."
exec uvicorn main_test:app --host 0.0.0.0 --port "$PORT"
