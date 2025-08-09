"""
🎯 Vocelio.ai Smart Campaigns Service - Simple Test Version
AI-powered campaign automation and optimization service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import uvicorn
import os

# Simple FastAPI app for testing
app = FastAPI(
    title="🎯 Vocelio.ai Smart Campaigns Service",
    description="AI-powered campaign automation and optimization service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str

class CampaignStats(BaseModel):
    total_campaigns: int
    active_campaigns: int
    success_rate: float
    ai_optimization_score: float

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="smart-campaigns-service",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/", response_model=Dict[str, str])
async def root():
    return {
        "service": "🎯 Vocelio.ai Smart Campaigns Service",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/campaigns/stats", response_model=CampaignStats)
async def get_campaign_stats():
    return CampaignStats(
        total_campaigns=156,
        active_campaigns=42,
        success_rate=87.3,
        ai_optimization_score=92.1
    )

@app.get("/campaigns")
async def list_campaigns():
    return {
        "campaigns": [
            {
                "id": "camp_001",
                "name": "Q4 Sales Push",
                "status": "active",
                "ai_score": 94.2,
                "calls_made": 1247,
                "conversion_rate": 12.4
            },
            {
                "id": "camp_002", 
                "name": "Lead Nurturing",
                "status": "active",
                "ai_score": 89.1,
                "calls_made": 834,
                "conversion_rate": 18.7
            }
        ]
    }

@app.get("/status")
async def service_status():
    return {
        "service": "smart-campaigns-service",
        "port": 8003,
        "status": "operational",
        "ai_engine": "active",
        "optimization": "enabled"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
