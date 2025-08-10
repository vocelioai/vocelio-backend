# apps/api-gateway/src/routes/health.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
import logging

from ..utils.service_discovery import ServiceDiscovery
from ..config import settings, SERVICE_CONFIG

logger = logging.getLogger(__name__)
router = APIRouter()

# Active subset only (keeps health output clean). Mirror SERVICES in main.
SERVICES = {
    "overview-service": os.getenv("OVERVIEW_SERVICE_URL", "http://overview-service:8001"),
    "ai-agents-service": os.getenv("AI_AGENTS_SERVICE_URL", "http://ai-agents-service:8002"),
    "smart-campaigns-service": os.getenv("SMART_CAMPAIGNS_SERVICE_URL", "http://smart-campaigns-service:8003"),
}

service_discovery = ServiceDiscovery(SERVICES)

@router.get("/health")
async def gateway_health():
    """Basic gateway health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "uptime": "operational"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Comprehensive health check of gateway and all services"""
    start_time = datetime.utcnow()
    
    health_status = {
        "gateway": {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": start_time.isoformat(),
            "memory_usage": "N/A",  # Could add psutil for memory monitoring
            "cpu_usage": "N/A"
        },
        "services": {},
        "summary": {
            "total_services": len(SERVICES),
            "healthy_services": 0,
            "unhealthy_services": 0,
            "unknown_services": 0
        }
    }
    
    # Check each service health
    service_check_tasks = []
    for service_name, service_url in SERVICES.items():
        task = asyncio.create_task(
            check_service_health(service_name, service_url),
            name=f"health_check_{service_name}"
        )
        service_check_tasks.append(task)
    
    # Wait for all health checks with timeout
    try:
        service_results = await asyncio.wait_for(
            asyncio.gather(*service_check_tasks, return_exceptions=True),
            timeout=10.0  # 10 second timeout for all health checks
        )
        
        # Process results
        for i, result in enumerate(service_results):
            service_name = list(SERVICES.keys())[i]
            
            if isinstance(result, Exception):
                health_status["services"][service_name] = {
                    "status": "error",
                    "error": str(result),
                    "response_time": None,
                    "last_check": start_time.isoformat()
                }
                health_status["summary"]["unknown_services"] += 1
            else:
                health_status["services"][service_name] = result
                if result["status"] == "healthy":
                    health_status["summary"]["healthy_services"] += 1
                else:
                    health_status["summary"]["unhealthy_services"] += 1
    
    except asyncio.TimeoutError:
        logger.warning("Health check timeout - some services may be slow")
        # Mark remaining services as timeout
        for service_name in SERVICES.keys():
            if service_name not in health_status["services"]:
                health_status["services"][service_name] = {
                    "status": "timeout",
                    "error": "Health check timeout",
                    "response_time": None,
                    "last_check": start_time.isoformat()
                }
                health_status["summary"]["unknown_services"] += 1
    
    # Calculate overall health
    total_check_time = (datetime.utcnow() - start_time).total_seconds()
    health_status["gateway"]["check_duration"] = round(total_check_time, 3)
    
    # Determine overall status
    healthy_ratio = health_status["summary"]["healthy_services"] / max(health_status["summary"]["total_services"], 1)
    if healthy_ratio >= 0.8:
        overall_status = "healthy"
    elif healthy_ratio >= 0.5:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    health_status["overall_status"] = overall_status
    health_status["summary"]["health_ratio"] = round(healthy_ratio * 100, 1)
    
    return health_status

async def check_service_health(service_name: str, service_url: str) -> Dict[str, Any]:
    """Check individual service health"""
    start_time = datetime.utcnow()
    
    try:
        config = SERVICE_CONFIG.get(service_name, {})
        timeout = config.get("timeout", settings.HEALTH_CHECK_TIMEOUT)
        health_path = config.get("health_check_path", "/health")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{service_url}{health_path}")
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            if response.status_code == 200:
                try:
                    service_health = response.json()
                    return {
                        "status": "healthy",
                        "service_name": SERVICE_CONFIG.get(service_name, {}).get("name", service_name),
                        "response_time": round(response_time * 1000, 2),  # milliseconds
                        "last_check": start_time.isoformat(),
                        "service_info": service_health,
                        "url": service_url
                    }
                except:
                    return {
                        "status": "healthy",
                        "service_name": SERVICE_CONFIG.get(service_name, {}).get("name", service_name),
                        "response_time": round(response_time * 1000, 2),
                        "last_check": start_time.isoformat(),
                        "service_info": {"raw_response": "non-json response"},
                        "url": service_url
                    }
            else:
                return {
                    "status": "unhealthy",
                    "service_name": SERVICE_CONFIG.get(service_name, {}).get("name", service_name),
                    "response_time": round(response_time * 1000, 2),
                    "last_check": start_time.isoformat(),
                    "error": f"HTTP {response.status_code}",
                    "url": service_url
                }
                
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "service_name": SERVICE_CONFIG.get(service_name, {}).get("name", service_name),
            "response_time": None,
            "last_check": start_time.isoformat(),
            "error": "Health check timeout",
            "url": service_url
        }
    except httpx.ConnectError:
        return {
            "status": "unreachable",
            "service_name": SERVICE_CONFIG.get(service_name, {}).get("name", service_name),
            "response_time": None,
            "last_check": start_time.isoformat(),
            "error": "Connection failed",
            "url": service_url
        }
    except Exception as e:
        return {
            "status": "error",
            "service_name": SERVICE_CONFIG.get(service_name, {}).get("name", service_name),
            "response_time": None,
            "last_check": start_time.isoformat(),
            "error": str(e),
            "url": service_url
        }

@router.get("/services")
async def list_services():
    """List all configured services with their status"""
    services_info = {}
    
    for service_name, service_url in SERVICES.items():
        config = SERVICE_CONFIG.get(service_name, {})
        services_info[service_name] = {
            "name": config.get("name", service_name.replace("-", " ").title()),
            "url": service_url,
            "timeout": config.get("timeout", settings.SERVICE_TIMEOUT),
            "retry_attempts": config.get("retry_attempts", 2),
            "health_check_path": config.get("health_check_path", "/health")
        }
    
    return {
        "total_services": len(SERVICES),
        "services": services_info,
        "gateway_version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/service/{service_name}")
async def check_specific_service(service_name: str):
    """Check health of a specific service"""
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Service not found",
                "service": service_name,
                "available_services": list(SERVICES.keys())
            }
        )
    
    service_url = SERVICES[service_name]
    health_result = await check_service_health(service_name, service_url)
    
    return health_result

@router.post("/service/{service_name}/restart")
async def restart_service_health_check(service_name: str, background_tasks: BackgroundTasks):
    """Trigger a fresh health check for a specific service"""
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )
    
    # Add background task to refresh service health
    background_tasks.add_task(
        service_discovery.force_health_check,
        service_name
    )
    
    return {
        "message": f"Health check triggered for {service_name}",
        "service": service_name,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def health_metrics():
    """Get health metrics for monitoring systems"""
    try:
        metrics = await service_discovery.get_health_metrics()
        
        return {
            "gateway_metrics": {
                "uptime_seconds": metrics.get("uptime", 0),
                "total_requests": metrics.get("total_requests", 0),
                "error_rate": metrics.get("error_rate", 0),
                "avg_response_time": metrics.get("avg_response_time", 0)
            },
            "service_metrics": metrics.get("services", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting health metrics: {e}")
        return {
            "error": "Unable to fetch metrics",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/ready")
async def readiness_check():
    """Kubernetes/Railway readiness probe"""
    # Check if critical services are available
    critical_services = ["ai-brain", "call-center", "voice-lab"]
    
    ready = True
    critical_status = {}
    
    for service in critical_services:
        if service in SERVICES:
            try:
                health = await check_service_health(service, SERVICES[service])
                critical_status[service] = health["status"]
                if health["status"] not in ["healthy"]:
                    ready = False
            except:
                critical_status[service] = "error"
                ready = False
    
    status_code = 200 if ready else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "ready": ready,
            "critical_services": critical_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@router.get("/live")
async def liveness_check():
    """Kubernetes/Railway liveness probe"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }
                