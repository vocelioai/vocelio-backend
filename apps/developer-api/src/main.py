# apps/developer-api/src/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

# Import API routes
from api.v1.api import api_router
from core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🔧 Vocelio.ai Developer API",
    version="1.0.0",
    description="Developer API, SDK, and integration tools for Vocelio.ai platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "developer-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "features": {
            "api_keys": True,
            "webhooks": True,
            "sdk_generation": True,
            "rate_limiting": True,
            "documentation": True,
            "testing_tools": True
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🔧 Vocelio.ai Developer API Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "API Key Management",
            "Webhook Configuration", 
            "SDK Generation",
            "Rate Limiting",
            "API Documentation",
            "Testing Tools",
            "Integration Guides"
        ],
        "getting_started": {
            "step_1": "Create API key at /api/v1/keys",
            "step_2": "Configure webhooks at /api/v1/webhooks",
            "step_3": "Download SDK at /api/v1/sdk",
            "step_4": "Test integration at /api/v1/test"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8005)),
        reload=settings.ENVIRONMENT == "development"
    )
