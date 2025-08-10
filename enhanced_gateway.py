#!/usr/bin/env python3
"""
Enhanced API Gateway with Service Routing
Routes requests to deployed Railway services
"""

import os
import logging
import asyncio
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn
import httpx
from service_config import DEPLOYED_SERVICES, SERVICE_HEALTH_PATHS, ROUTE_MAPPINGS

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

# Service health cache
service_health_cache = {}
last_health_check = None

async def check_service_health(service_name: str, service_url: str) -> dict:
    """Check health of a deployed service"""
    health_path = SERVICE_HEALTH_PATHS.get(service_name, "/health")
    full_url = f"{service_url}{health_path}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(full_url)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "last_check": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "unhealthy", 
                    "error": f"HTTP {response.status_code}",
                    "last_check": datetime.utcnow().isoformat()
                }
    except Exception as e:
        return {
            "status": "unreachable",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

async def check_all_services():
    """Check health of all deployed services"""
    global service_health_cache, last_health_check
    
    health_results = {}
    
    for service_name, service_url in DEPLOYED_SERVICES.items():
        health_results[service_name] = await check_service_health(service_name, service_url)
    
    service_health_cache = health_results
    last_health_check = datetime.utcnow().isoformat()
    
    return health_results

@app.get("/")
async def root():
    """Gateway root endpoint with service information"""
    # Get fresh service health if cache is old or empty
    if not service_health_cache or not last_health_check:
        await check_all_services()
    
    healthy_services = sum(1 for health in service_health_cache.values() if health.get("status") == "healthy")
    total_services = len(DEPLOYED_SERVICES) + 1  # +1 for gateway itself
    
    return {
        "message": "🔥 Vocelio.ai - World's Best AI Call Center Platform",
        "version": "2.0.0",
        "architecture": "microservices",
        "status": "healthy",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "unknown"),
        "port": os.environ.get("PORT", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "total": total_services,
            "healthy": healthy_services,
            "deployed": len(DEPLOYED_SERVICES),
            "gateway": "online"
        },
        "deployed_services": list(DEPLOYED_SERVICES.keys()),
        "endpoints": {
            "health": "/health",
            "system_status": "/api/v1/system/status",
            "service_health": "/api/v1/services/health", 
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

@app.get("/api/v1/system/status")
async def system_status():
    """System status with deployed services"""
    if not service_health_cache:
        await check_all_services()
    
    services_status = {
        "api-gateway": {
            "status": "online",
            "version": "2.0.0",
            "health": "healthy",
            "url": "/"
        }
    }
    
    # Add deployed services status
    for service_name, service_url in DEPLOYED_SERVICES.items():
        health = service_health_cache.get(service_name, {"status": "unknown"})
        services_status[service_name] = {
            "status": health.get("status", "unknown"),
            "version": "unknown",
            "health": health.get("status", "unknown"),
            "url": service_url,
            "last_check": health.get("last_check", "never")
        }
    
    return {
        "system": {
            "name": "Vocelio AI Call Center",
            "version": "2.0.0",
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "production"),
            "uptime": "operational",
            "health": "healthy"
        },
        "services": services_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/services/health")
async def services_health():
    """Detailed health check of all services"""
    health_results = await check_all_services()
    
    return {
        "gateway": {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        },
        "deployed_services": health_results,
        "summary": {
            "total": len(DEPLOYED_SERVICES),
            "healthy": sum(1 for health in health_results.values() if health.get("status") == "healthy"),
            "unhealthy": sum(1 for health in health_results.values() if health.get("status") == "unhealthy"),
            "unreachable": sum(1 for health in health_results.values() if health.get("status") == "unreachable")
        },
        "last_check": last_health_check
    }

# Proxy requests to deployed services
@app.api_route("/api/v1/{service_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_service(service_path: str, request: Request):
    """Proxy requests to appropriate deployed services"""
    
    # Determine which service to route to
    target_service = None
    for route_prefix, service_name in ROUTE_MAPPINGS.items():
        if f"/api/v1/{service_path}".startswith(route_prefix):
            target_service = service_name
            break
    
    if not target_service or target_service not in DEPLOYED_SERVICES:
        raise HTTPException(status_code=404, detail=f"Service not found for path: /api/v1/{service_path}")
    
    # Get target service URL
    target_url = DEPLOYED_SERVICES[target_service]
    full_url = f"{target_url}/api/v1/{service_path}"
    
    # Forward the request
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward the request with all headers and body
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=dict(request.headers),
                content=await request.body(),
                params=request.query_params
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                headers=dict(response.headers)
            )
            
    except Exception as e:
        logger.error(f"Error proxying to {target_service}: {e}")
        raise HTTPException(status_code=502, detail=f"Service {target_service} unavailable")

# Background task to periodically check service health
@app.on_event("startup")
async def startup_event():
    """Initialize service health checks on startup"""
    logger.info("🚀 Starting API Gateway with deployed services integration")
    await check_all_services()
    logger.info(f"Connected to {len(DEPLOYED_SERVICES)} deployed services")

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
    logger.info(f"🚀 Starting Vocelio API Gateway with Service Routing on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
