#!/usr/bin/env python3
"""
flow-builder Service for Vocelio.ai
Advanced Workflow Automation & Visual Flow Designer Platform
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Import enhanced API endpoints
from src.api.v1.endpoints import advanced_automation, visual_flow_designer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Flow Builder Service - Advanced Workflow Automation",
    version="2.0.0",
    description="Vocelio.ai Flow Builder microservice with advanced automation capabilities, visual flow designer, AI-powered decisions, and enterprise workflow management"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include enhanced API routers
app.include_router(advanced_automation.router, prefix="/api/v1")
app.include_router(visual_flow_designer.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "service": "flow-builder",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "flow-builder",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting flow-builder Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
