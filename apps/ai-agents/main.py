#!/usr/bin/env python3
"""
AI Agents Service for Vocelio.ai
Advanced AI agent management and coordination
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Agents Service",
    version="1.0.0",
    description="Vocelio.ai AI Agents microservice for advanced agent management"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-agents",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ai-agents",
        "message": "Vocelio.ai AI Agents Service",
        "status": "operational",
        "endpoints": ["/health", "/api/v1/agents"]
    }

@app.get("/api/v1/agents")
async def list_agents():
    """List available AI agents"""
    return {
        "agents": [
            {"id": "voice-assistant", "name": "Voice Assistant", "status": "active"},
            {"id": "call-analyzer", "name": "Call Analyzer", "status": "active"},
            {"id": "sentiment-agent", "name": "Sentiment Agent", "status": "active"}
        ],
        "total": 3
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
