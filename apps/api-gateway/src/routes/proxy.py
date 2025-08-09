# apps/api-gateway/src/routes/proxy.py
from fastapi import APIRouter, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import httpx
import asyncio
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os

from ..utils.service_discovery import ServiceDiscovery
from ..utils.load_balancer import LoadBalancer
from ..config import settings, SERVICE_CONFIG

logger = logging.getLogger(__name__)
router = APIRouter()

# Active deployed subset only (keeps proxy health & metrics clean)
SERVICES = {
    "overview-service": os.getenv("OVERVIEW_SERVICE_URL", "http://overview-service:8001"),
    "ai-agents-service": os.getenv("AI_AGENTS_SERVICE_URL", "http://ai-agents-service:8002"),
    "smart-campaigns-service": os.getenv("SMART_CAMPAIGNS_SERVICE_URL", "http://smart-campaigns-service:8003"),
}

# Initialize service discovery and load balancer
service_discovery = ServiceDiscovery(SERVICES)
load_balancer = LoadBalancer(SERVICES)

@router.get("/proxy/services")
async def list_proxy_services():
    """List all available services for proxying"""
    services_info = {}
    
    for service_name, service_url in SERVICES.items():
        config = SERVICE_CONFIG.get(service_name, {})
        health = await service_discovery.is_service_healthy(service_name)
        
        services_info[service_name] = {
            "name": config.get("name", service_name.replace("-", " ").title()),
            "url": service_url,
            "healthy": health,
            "timeout": config.get("timeout", settings.SERVICE_TIMEOUT),
            "retry_attempts": config.get("retry_attempts", 2),
            "description": get_service_description(service_name)
        }
    
    return {
        "services": services_info,
        "total_services": len(SERVICES),
        "timestamp": datetime.utcnow().isoformat()
    }

def get_service_description(service_name: str) -> str:
    """Get human-readable description for service"""
    descriptions = {
        "overview-service": "Real-time dashboard & command center",
        "ai-agents-service": "AI agent management & orchestration",
        "smart-campaigns-service": "Intelligent campaign automation engine",
    }
    return descriptions.get(service_name, f"{service_name.replace('-', ' ').title()} service")

@router.get("/proxy/load-balancer/status")
async def get_load_balancer_status():
    """Get current load balancer status and metrics"""
    try:
        metrics = await load_balancer.get_load_balancing_metrics()
        recommendations = await load_balancer.get_service_recommendations()
        
        return {
            "load_balancer": metrics,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting load balancer status: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch load balancer status")

@router.post("/proxy/load-balancer/circuit-breaker/{service_name}/{action}")
async def control_circuit_breaker(service_name: str, action: str):
    """Manually control circuit breaker for a service"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    if action not in ["open", "close"]:
        raise HTTPException(status_code=400, detail="Action must be 'open' or 'close'")
    
    try:
        if action == "open":
            load_balancer.force_circuit_breaker_open(service_name)
            message = f"Circuit breaker opened for {service_name}"
        else:
            load_balancer.force_circuit_breaker_close(service_name)
            message = f"Circuit breaker closed for {service_name}"
        
        return {
            "message": message,
            "service": service_name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error controlling circuit breaker: {e}")
        raise HTTPException(status_code=500, detail="Unable to control circuit breaker")

@router.get("/proxy/metrics")
async def get_proxy_metrics():
    """Get comprehensive proxy metrics"""
    try:
        # Get service discovery metrics
        sd_metrics = await service_discovery.get_health_metrics()
        
        # Get load balancer metrics
        lb_metrics = await load_balancer.get_load_balancing_metrics()
        
        # Combine metrics
        return {
            "service_discovery": sd_metrics,
            "load_balancer": lb_metrics,
            "gateway_info": {
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "total_services": len(SERVICES),
                "rate_limit_enabled": settings.RATE_LIMIT_REQUESTS > 0,
                "circuit_breaker_enabled": settings.CIRCUIT_BREAKER_ENABLED
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting proxy metrics: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch proxy metrics")

async def proxy_request_with_retry(
    service_name: str,
    path: str,
    request: Request,
    max_retries: int = None
) -> Response:
    """Proxy request with intelligent retry logic"""
    
    if max_retries is None:
        config = SERVICE_CONFIG.get(service_name, {})
        max_retries = config.get("retry_attempts", 2)
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            # Get optimal service URL
            service_url = await load_balancer.get_service_url(service_name)
            target_url = f"{service_url}/api/v1/{path}"
            
            # Prepare request
            headers = dict(request.headers)
            headers.pop("host", None)
            headers["X-Forwarded-For"] = request.client.host
            headers["X-Gateway-Version"] = settings.VERSION
            headers["X-Service-Route"] = service_name
            headers["X-Attempt"] = str(attempt + 1)
            
            body = await request.body()
            
            # Log attempt
            if attempt > 0:
                logger.info(f"🔄 Retry attempt {attempt + 1}/{max_retries + 1} for {service_name}/{path}")
            
            start_time = time.time()
            
            # Make request with appropriate timeout
            config = SERVICE_CONFIG.get(service_name, {})
            timeout = config.get("timeout", settings.SERVICE_TIMEOUT)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=dict(request.query_params)
                )
                
                response_time = time.time() - start_time
                success = 200 <= response.status_code < 400
                
                # Record metrics
                load_balancer.record_request_result(
                    service_name, response_time, response.status_code, success
                )
                
                # Log successful request
                logger.info(f"✅ {service_name} responded {response.status_code} in {response_time:.3f}s (attempt {attempt + 1})")
                
                # Prepare response headers
                response_headers = dict(response.headers)
                response_headers["X-Service-Name"] = service_name
                response_headers["X-Service-Response-Time"] = str(response_time)
                response_headers["X-Attempt-Count"] = str(attempt + 1)
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response_headers.get("content-type", "application/json")
                )
                
        except httpx.TimeoutException as e:
            last_exception = e
            error_msg = f"Timeout calling {service_name} (attempt {attempt + 1})"
            logger.warning(f"⏰ {error_msg}")
            
            # Don't retry on final attempt
            if attempt == max_retries:
                break
                
            # Exponential backoff for retries
            await asyncio.sleep(min(2 ** attempt, 10))
            
        except httpx.ConnectError as e:
            last_exception = e
            error_msg = f"Connection error to {service_name} (attempt {attempt + 1})"
            logger.warning(f"🔌 {error_msg}")
            
            # Don't retry connection errors immediately
            if attempt == max_retries:
                break
                
            await asyncio.sleep(min(2 ** attempt, 10))
            
        except Exception as e:
            last_exception = e
            logger.error(f"❌ Unexpected error proxying to {service_name}: {e}")
            break  # Don't retry unexpected errors
    
    # All retries failed
    if isinstance(last_exception, httpx.TimeoutException):
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Service timeout",
                "service": service_name,
                "message": f"The {service_name} service took too long to respond after {max_retries + 1} attempts",
                "attempts": max_retries + 1
            }
        )
    elif isinstance(last_exception, httpx.ConnectError):
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service unavailable", 
                "service": service_name,
                "message": f"The {service_name} service is currently unavailable after {max_retries + 1} attempts",
                "attempts": max_retries + 1
            }
        )
    else:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Gateway error",
                "service": service_name,
                "message": f"Unable to connect to {service_name} service",
                "attempts": max_retries + 1
            }
        )

async def proxy_streaming_request(
    service_name: str,
    path: str, 
    request: Request
) -> StreamingResponse:
    """Proxy streaming requests (for real-time features)"""
    
    try:
        service_url = await load_balancer.get_service_url(service_name)
        target_url = f"{service_url}/api/v1/{path}"
        
        headers = dict(request.headers)
        headers.pop("host", None)
        headers["X-Forwarded-For"] = request.client.host
        headers["X-Gateway-Version"] = settings.VERSION
        headers["X-Stream-Proxy"] = "true"
        
        config = SERVICE_CONFIG.get(service_name, {})
        timeout = httpx.Timeout(config.get("timeout", 300))  # Longer timeout for streaming
        
        async def stream_response():
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=dict(request.query_params),
                    content=await request.body()
                ) as response:
                    
                    # Stream the response
                    async for chunk in response.aiter_bytes():
                        yield chunk
        
        return StreamingResponse(
            stream_response(),
            media_type="application/json",
            headers={
                "X-Service-Name": service_name,
                "X-Stream-Proxy": "true"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error streaming from {service_name}: {e}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Streaming error",
                "service": service_name,
                "message": "Unable to establish streaming connection"
            }
        )

# Health check for proxy router
@router.get("/proxy/health")
async def proxy_health():
    """Proxy router health check"""
    return {
        "status": "healthy",
        "component": "proxy_router",
        "services_configured": len(SERVICES),
        "timestamp": datetime.utcnow().isoformat()
    }