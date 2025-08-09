#!/bin/sh
# Startup script to handle PORT env var properly
PORT=${PORT:-8000}
exec uvicorn --app-dir apps/api-gateway src.main:app --host 0.0.0.0 --port "$PORT"
