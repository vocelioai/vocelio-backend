#!/usr/bin/env python3
"""
integrations Service for Vocelio.ai
Enterprise Integration Platform & API Marketplace
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Import enhanced API endpoints
from src.api.v1.endpoints import enterprise_integrations, api_marketplace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Integrations Service - Enterprise Integration Platform",
    version="2.0.0",
    description="Vocelio.ai Integrations microservice with enterprise-grade third-party integrations, API marketplace, custom connectors, and advanced data synchronization"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include enhanced API routers
app.include_router(enterprise_integrations.router, prefix="/api/v1")
app.include_router(api_marketplace.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "service": "integrations",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "integrations",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting integrations Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
