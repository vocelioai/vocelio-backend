#!/usr/bin/env python3
"""
Simplified API Gateway for Railway deployment
Self-contained version without external dependencies
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="🔥 Vocelio.ai API Gateway",
    version="2.0.0",
    description="World's Best AI Call Center Platform - Microservices Gateway",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Gateway root endpoint with service information"""
    return {
        "message": "🔥 Vocelio.ai - World's Best AI Call Center Platform",
        "version": "2.0.0",
        "architecture": "microservices",
        "status": "healthy",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "unknown"),
        "port": os.environ.get("PORT", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api-gateway": "online",
            "overview-service": "embedded",
            "ai-agents-service": "pending",
            "smart-campaigns-service": "pending"
        },
        "endpoints": {
            "health": "/health",
            "dashboard": "/api/v1/dashboard", 
            "system_status": "/api/v1/system/status",
            "metrics": "/api/v1/metrics",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "operational"
    }

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check"""
    return {
        "gateway": {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        },
        "environment": {
            "port": os.environ.get("PORT", "unknown"),
            "railway_env": os.environ.get("RAILWAY_ENVIRONMENT", "unknown"),
            "python_path": os.environ.get("PYTHONPATH", "not set")
        },
        "services": {
            "overview-service": "not deployed",
            "ai-agents-service": "not deployed", 
            "smart-campaigns-service": "not deployed"
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "online",
        "features": [
            "cors_enabled",
            "health_checks",
            "basic_routing",
            "overview_service"
        ]
    }

# Overview Service Routes (embedded for simplicity)
@app.get("/api/v1/dashboard")
async def dashboard():
    """Main dashboard data"""
    return {
        "dashboard": {
            "title": "Vocelio AI Call Center",
            "status": "operational",
            "services": {
                "total": 4,
                "online": 1,
                "pending": 3,
                "offline": 0
            },
            "stats": {
                "total_calls": 0,
                "active_campaigns": 0,
                "ai_agents": 0,
                "success_rate": "0%"
            },
            "recent_activity": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "API Gateway deployed successfully",
                    "type": "deployment"
                }
            ],
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
                "health": "healthy",
                "url": "/"
            },
            "overview-service": {
                "status": "embedded",
                "version": "1.0.0",
                "health": "healthy",
                "url": "/api/v1/dashboard"
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
            "active_connections": 1
        },
        "performance": {
            "cpu_usage": "optimal",
            "memory_usage": "low",
            "disk_usage": "minimal"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Simple middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.utcnow()
    
    # Process request
    response = await call_next(request)
    
    # Log the request
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Add headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Powered-By"] = "Vocelio.ai Gateway v2.0"
    
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Vocelio API Gateway on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
