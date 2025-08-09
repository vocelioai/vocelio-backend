#!/usr/bin/env python3
"""
🌉 Vocelio.ai API Gateway - Test Version
Simplified version for testing without database dependencies
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
SERVICE_URLS = {
    "overview": "http://localhost:8001",
    "ai-agents": "http://localhost:8002", 
    "smart-campaigns": "http://localhost:8003"
}

# Initialize FastAPI app
app = FastAPI(
    title="Vocelio.ai API Gateway",
    description="Central API gateway for all Vocelio services",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Service health check
@app.get("/api/v1/services/health")
async def check_all_services():
    """Check health of all services"""
    service_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, base_url in SERVICE_URLS.items():
            try:
                response = await client.get(f"{base_url}/health", timeout=5.0)
                service_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                service_status[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
    
    return {
        "gateway_status": "healthy",
        "services": service_status,
        "timestamp": datetime.now().isoformat()
    }

# Overview service routes
@app.get("/api/v1/overview/{path:path}")
async def overview_proxy(path: str, request: Request):
    """Proxy requests to Overview service"""
    return await proxy_request("overview", path, request)

# AI Agents service routes  
@app.get("/api/v1/agents/{path:path}")
@app.post("/api/v1/agents/{path:path}")
@app.put("/api/v1/agents/{path:path}")
async def agents_proxy(path: str, request: Request):
    """Proxy requests to AI Agents service"""
    return await proxy_request("ai-agents", f"api/v1/agents/{path}", request)

# Smart Campaigns service routes
@app.get("/api/v1/campaigns/{path:path}")
@app.post("/api/v1/campaigns/{path:path}")
@app.put("/api/v1/campaigns/{path:path}")
async def campaigns_proxy(path: str, request: Request):
    """Proxy requests to Smart Campaigns service"""
    return await proxy_request("smart-campaigns", f"api/v1/campaigns/{path}", request)

async def proxy_request(service_name: str, path: str, request: Request):
    """Generic proxy function"""
    if service_name not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    base_url = SERVICE_URLS[service_name]
    target_url = f"{base_url}/{path}"
    
    # Get query parameters
    query_params = dict(request.query_params)
    
    try:
        async with httpx.AsyncClient() as client:
            if request.method == "GET":
                response = await client.get(target_url, params=query_params, timeout=30.0)
            elif request.method == "POST":
                body = await request.body()
                response = await client.post(
                    target_url, 
                    content=body,
                    headers={"Content-Type": request.headers.get("content-type", "application/json")},
                    params=query_params,
                    timeout=30.0
                )
            elif request.method == "PUT":
                body = await request.body()
                response = await client.put(
                    target_url,
                    content=body, 
                    headers={"Content-Type": request.headers.get("content-type", "application/json")},
                    params=query_params,
                    timeout=30.0
                )
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Service {service_name} timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
    except Exception as e:
        logger.error(f"Proxy error for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal proxy error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main_test:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
