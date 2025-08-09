"""
Vocelio.ai Overview Service - Simple Test Version
Minimal FastAPI application for testing deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import uvicorn
import os

# Simple FastAPI app for testing
app = FastAPI(
    title="🌍 Vocelio.ai Overview Service",
    description="Enterprise-grade real-time metrics and dashboard data service",
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
    port: int

class MetricsResponse(BaseModel):
    revenue: Dict[str, Any]
    calls: Dict[str, Any]
    clients: Dict[str, Any]
    uptime: str

# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    return {
        "service": "🌍 Vocelio.ai Overview Service",
        "status": "running",
        "port": "8001",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="overview-service",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        port=8001
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    return MetricsResponse(
        revenue={
            "total": 125432.50,
            "monthly": 45231.20,
            "growth": 15.4,
            "currency": "USD"
        },
        calls={
            "total": 8542,
            "active": 127,
            "success_rate": 96.8,
            "avg_duration": 4.2
        },
        clients={
            "total": 245,
            "active": 89,
            "new_this_month": 23
        },
        uptime="99.9%"
    )

@app.get("/status")
async def service_status():
    return {
        "service": "overview-service",
        "port": 8001,
        "status": "operational",
        "environment": "test",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
