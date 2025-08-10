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
            "overview-service": "pending",
            "ai-agents-service": "pending",
            "smart-campaigns-service": "pending"
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
            "basic_routing"
        ]
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
