#!/bin/bash

# 🌍 Vocelio.ai Overview Service Startup Script
# Handles PYTHONPATH and PORT environment variables for Railway deployment

echo "🚀 Starting Vocelio.ai Overview Service..."
echo "================================================="

# Set PYTHONPATH to current directory for module imports
export PYTHONPATH="."

# Get PORT from environment or default to 8001
PORT=${PORT:-8001}

echo "📍 Service: Overview Service"
echo "🌐 Port: $PORT"
echo "📦 PYTHONPATH: $PYTHONPATH"
echo "🔧 Environment: ${ENVIRONMENT:-production}"
echo "================================================="

# Start the service
exec uvicorn src.main_test:app --host 0.0.0.0 --port "$PORT"
