# apps/api-gateway/src/routes/health.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
import asyncio
import time
import resource
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
import logging

from ..utils.service_discovery import ServiceDiscovery
from ..config import settings, SERVICE_CONFIG

logger = logging.getLogger(__name__)
router = APIRouter()

# Gateway start time for uptime calculation
start_time = time.time()

# Active subset only (keeps health output clean). Mirror SERVICES in main.
SERVICES = {
    "overview-service": os.getenv("OVERVIEW_SERVICE_URL", "http://overview-service:8001"),
    "ai-agents-service": os.getenv("AI_AGENTS_SERVICE_URL", "http://ai-agents-service:8002"),
    "smart-campaigns-service": os.getenv("SMART_CAMPAIGNS_SERVICE_URL", "http://smart-campaigns-service:8003"),
}

service_discovery = ServiceDiscovery(SERVICES)


@router.get("/health", 
          summary="Gateway Health Check",
          description="Comprehensive health check for the API Gateway and all connected services")
async def gateway_health():
    """
    Main health check endpoint that provides:
    - Gateway status
    - Service discovery health
    - Quick service connectivity check
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "gateway": {
                "status": "operational",
                "uptime": time.time() - start_time,
                "memory_available": True
            },
            "service_discovery": {
                "status": "operational",
                "services_count": len(SERVICES),
                "last_update": "active"
            }
        }
        
        # Quick connectivity check to a few key services
        quick_services = ["overview", "ai-agents", "billing-pro"]
        service_status = {}
        
        for service_name in quick_services:
            try:
                if service_name in SERVICES:
                    service_url = SERVICES[service_name]
                    service_status[service_name] = {
                        "status": "available",
                        "url": service_url,
                        "health_endpoint": f"{service_url}/health"
                    }
                else:
                    service_status[service_name] = {
                        "status": "not_found",
                        "url": None
                    }
            except Exception as e:
                service_status[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        health_status["quick_service_check"] = service_status
        
        logger.info("🏥 Gateway health check completed - All systems operational")
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/api/v1/health", 
          summary="API v1 Health Check",
          description="Health check endpoint for API v1 compatibility")
async def api_v1_health():
    """
    API v1 health endpoint - provides same health info but with v1 API structure
    """
    return await gateway_health()


@router.get("/api/v1/twilio/health", 
          summary="Twilio Service Health Check",
          description="Specific health check for Twilio service connectivity")
async def twilio_health():
    """
    Twilio service specific health check
    """
    try:
        # Look for Twilio service in our services map
        twilio_service_names = ["twilio-service", "phone-numbers", "call-center"]
        twilio_service = None
        twilio_service_name = None
        
        for service_name in twilio_service_names:
            if service_name in SERVICES:
                twilio_service = SERVICES[service_name]
                twilio_service_name = service_name
                break
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "twilio",
            "version": "1.0.0"
        }
        
        if twilio_service:
            health_status["twilio_service"] = {
                "service_name": twilio_service_name,
                "status": "available",
                "url": twilio_service,
                "health_endpoint": f"{twilio_service}/health"
            }
            
            # Try to ping the actual Twilio service health endpoint
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{twilio_service}/health")
                    if response.status_code == 200:
                        health_status["twilio_service"]["connectivity"] = "healthy"
                        try:
                            health_status["twilio_service"]["response_data"] = response.json()
                        except:
                            health_status["twilio_service"]["response_text"] = response.text
                    else:
                        health_status["twilio_service"]["connectivity"] = "degraded"
                        health_status["twilio_service"]["status_code"] = response.status_code
            except Exception as conn_error:
                health_status["twilio_service"]["connectivity"] = "error"
                health_status["twilio_service"]["connection_error"] = str(conn_error)
        else:
            health_status["status"] = "degraded"
            health_status["twilio_service"] = {
                "status": "not_found",
                "error": "No Twilio-related service found in service registry",
                "searched_services": twilio_service_names
            }
        
        logger.info("📞 Twilio health check completed")
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Twilio health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "service": "twilio",
            "error": str(e)
        }
    
    
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
                