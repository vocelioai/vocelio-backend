#!/bin/bash

# 🎯 Vocelio.ai Smart Campaigns Service Startup Script
# Handles PYTHONPATH and PORT environment variables for Railway deployment

echo "🚀 Starting Vocelio.ai Smart Campaigns Service..."
echo "====================================================="

# Set PYTHONPATH to current directory for module imports
export PYTHONPATH="."

# Get PORT from environment or default to 8003
PORT=${PORT:-8003}

echo "📍 Service: Smart Campaigns Service"
echo "🌐 Port: $PORT"
echo "📦 PYTHONPATH: $PYTHONPATH"
echo "🔧 Environment: ${ENVIRONMENT:-production}"
echo "🤖 AI Engine: Enabled"
echo "====================================================="

# Start the service
exec uvicorn src.main_test:app --host 0.0.0.0 --port "$PORT"
