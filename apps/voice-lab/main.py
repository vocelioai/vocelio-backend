#!/usr/bin/env python3
"""
voice-lab Service for Vocelio.ai
Advanced Audio Processing & Voice Analytics Platform
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Import enhanced API endpoints
from src.api.v1.endpoints import advanced_audio, voice_analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Voice Lab Service - Advanced Audio Processing",
    version="2.0.0",
    description="Vocelio.ai Voice Lab microservice with advanced audio processing, voice analytics, and AI-powered voice enhancement capabilities"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include enhanced API routers
app.include_router(advanced_audio.router, prefix="/api/v1")
app.include_router(voice_analytics.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "service": "voice-lab",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "voice-lab",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting voice-lab Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
