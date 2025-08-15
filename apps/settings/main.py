#!/usr/bin/env python3
"""
Settings Service for Vocelio.ai
Enhanced with advanced configuration management capabilities
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Import enhanced endpoint routers
from src.api.v1.endpoints.advanced_configuration import router as advanced_config_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"Settings Service - Enhanced v2.0.0",
    version="2.0.0",
    description=f"Vocelio.ai enhanced settings microservice with enterprise-grade configuration management"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include enhanced configuration endpoints
app.include_router(advanced_config_router, prefix="/api/v1", tags=["Advanced Configuration"])

@app.get("/")
async def root():
    return {
        "service": "settings",
        "status": "operational",
        "version": "2.0.0",
        "enhanced_features": [
            "Configuration templates",
            "Multi-environment management", 
            "Compliance governance",
            "Advanced automation rules",
            "Configuration analytics"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "settings",
        "version": "2.0.0",
        "capabilities": {
            "advanced_configuration": True,
            "multi_environment": True,
            "compliance_governance": True,
            "automation_rules": True,
            "analytics": True
        },
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting settings Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
