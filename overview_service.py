#!/usr/bin/env python3
"""
Overview Service - Simplified for Railway deployment
Dashboard and system overview functionality
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="📊 Vocelio Overview Service",
    version="1.0.0",
    description="Dashboard and System Overview - Vocelio AI Call Center",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Overview service root endpoint"""
    return {
        "service": "overview-service",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Dashboard and System Overview",
        "timestamp": datetime.utcnow().isoformat(),
        "port": os.environ.get("PORT", "unknown"),
        "features": [
            "system_dashboard",
            "service_status",
            "basic_analytics",
            "health_monitoring"
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "overview-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dashboard")
async def dashboard():
    """Main dashboard data"""
    return {
        "dashboard": {
            "title": "Vocelio AI Call Center",
            "status": "operational",
            "services": {
                "total": 4,
                "online": 2,
                "pending": 2,
                "offline": 0
            },
            "stats": {
                "total_calls": 0,
                "active_campaigns": 0,
                "ai_agents": 0,
                "success_rate": "0%"
            },
            "recent_activity": [],
            "alerts": []
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/system/status")
async def system_status():
    """System status overview"""
    return {
        "system": {
            "name": "Vocelio AI Call Center",
            "version": "2.0.0",
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "production"),
            "uptime": "operational",
            "health": "healthy"
        },
        "services": {
            "api-gateway": {
                "status": "online",
                "version": "2.0.0",
                "health": "healthy"
            },
            "overview-service": {
                "status": "online", 
                "version": "1.0.0",
                "health": "healthy"
            },
            "ai-agents-service": {
                "status": "pending",
                "version": "unknown",
                "health": "not deployed"
            },
            "smart-campaigns-service": {
                "status": "pending",
                "version": "unknown", 
                "health": "not deployed"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/metrics")
async def basic_metrics():
    """Basic system metrics"""
    return {
        "metrics": {
            "requests_total": 0,
            "requests_per_minute": 0,
            "response_time_avg": 0,
            "error_rate": 0,
            "active_connections": 0
        },
        "performance": {
            "cpu_usage": "unknown",
            "memory_usage": "unknown",
            "disk_usage": "unknown"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    logger.info(f"📊 Starting Overview Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
