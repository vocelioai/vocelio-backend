"""
Comprehensive Service Router for Vocelio API Gateway
Handles intelligent routing to microservices with load balancing and health checks
"""

import asyncio
import random
import time
import httpx
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from fastapi import Request, HTTPException, status
from fastapi.responses import Response, JSONResponse
import json
from urllib.parse import urljoin
from ..config import settings

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class ServiceInstance:
    """Service instance information"""
    url: str
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_check: float = field(default_factory=time.time)
    response_time: float = 0.0
    error_count: int = 0
    success_count: int = 0
    weight: int = 1  # Load balancing weight
    
    @property
    def health_score(self) -> float:
        """Calculate health score based on metrics"""
        if self.status == ServiceStatus.MAINTENANCE:
            return 0.0
        if self.status == ServiceStatus.UNHEALTHY:
            return 0.1
        
        # Calculate score based on success rate and response time
        total_requests = self.success_count + self.error_count
        if total_requests == 0:
            return 0.8  # Default for new instances
        
        success_rate = self.success_count / total_requests
        # Penalize high response times (above 1000ms)
        time_penalty = max(0, (self.response_time - 1000) / 1000) * 0.2
        
        score = success_rate - time_penalty
        return max(0.0, min(1.0, score))


class ServiceRouter:
    """Intelligent service router with health checking and load balancing"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.service_patterns: Dict[str, str] = {}
        self.health_check_interval = 30  # seconds
        self.timeout = 30.0  # request timeout
        self.max_retries = 2
        self.circuit_breaker_threshold = 5  # failures before circuit break
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Initialize service registry
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize service registry with configured services"""
        service_configs = {
            "overview": {
                "urls": [settings.OVERVIEW_SERVICE_URL],
                "patterns": ["/api/v1/overview", "/overview"]
            },
            "ai-agents": {
                "urls": [settings.AI_AGENTS_SERVICE_URL],
                "patterns": ["/api/v1/ai-agents", "/ai-agents", "/agents"]
            },
            "smart-campaigns": {
                "urls": [settings.SMART_CAMPAIGNS_SERVICE_URL],
                "patterns": ["/api/v1/smart-campaigns", "/smart-campaigns", "/campaigns"]
            },
            "call-center": {
                "urls": [settings.CALL_CENTER_SERVICE_URL],
                "patterns": ["/api/v1/call-center", "/call-center", "/calls"]
            },
            "voice-lab": {
                "urls": [settings.VOICE_LAB_SERVICE_URL],
                "patterns": ["/api/v1/voice-lab", "/voice-lab", "/voices"]
            },
            "analytics": {
                "urls": [settings.ANALYTICS_SERVICE_URL],
                "patterns": ["/api/v1/analytics", "/analytics", "/stats"]
            },
            "billing": {
                "urls": [settings.BILLING_SERVICE_URL],
                "patterns": ["/api/v1/billing", "/billing", "/payments"]
            },
            "integrations": {
                "urls": [settings.INTEGRATIONS_SERVICE_URL],
                "patterns": ["/api/v1/integrations", "/integrations"]
            },
            "marketplace": {
                "urls": [settings.MARKETPLACE_SERVICE_URL],
                "patterns": ["/api/v1/marketplace", "/marketplace"]
            },
            "lead-qualification": {
                "urls": [settings.LEAD_QUALIFICATION_SERVICE_URL],
                "patterns": ["/api/v1/lead-qualification", "/lead-qualification", "/leads"]
            },
            "appointment-booking": {
                "urls": [settings.APPOINTMENT_BOOKING_SERVICE_URL],
                "patterns": ["/api/v1/appointment-booking", "/appointment-booking", "/appointments"]
            },
            "inbound-calls": {
                "urls": [settings.INBOUND_CALLS_SERVICE_URL],
                "patterns": ["/api/v1/inbound-calls", "/inbound-calls", "/inbound"]
            },
            "outbound-calls": {
                "urls": [settings.OUTBOUND_CALLS_SERVICE_URL],
                "patterns": ["/api/v1/outbound-calls", "/outbound-calls", "/outbound"]
            },
            "knowledge-base": {
                "urls": [settings.KNOWLEDGE_BASE_SERVICE_URL],
                "patterns": ["/api/v1/knowledge-base", "/knowledge-base", "/kb"]
            },
            "team-management": {
                "urls": [settings.TEAM_MANAGEMENT_SERVICE_URL],
                "patterns": ["/api/v1/team-management", "/team-management", "/team"]
            },
            "workflows": {
                "urls": [settings.WORKFLOWS_SERVICE_URL],
                "patterns": ["/api/v1/workflows", "/workflows"]
            },
            "developer-api": {
                "urls": [settings.DEVELOPER_API_SERVICE_URL],
                "patterns": ["/api/v1/developer-api", "/developer-api", "/api"]
            },
            "webhooks": {
                "urls": [settings.WEBHOOKS_SERVICE_URL],
                "patterns": ["/api/v1/webhooks", "/webhooks"]
            }
        }
        
        for service_name, config in service_configs.items():
            # Create service instances
            instances = []
            for url in config["urls"]:
                if url:  # Only add if URL is configured
                    instances.append(ServiceInstance(url=url))
            
            if instances:
                self.services[service_name] = instances
                
                # Register URL patterns
                for pattern in config["patterns"]:
                    self.service_patterns[pattern] = service_name
        
        logger.info(f"✅ Initialized {len(self.services)} services with {sum(len(instances) for instances in self.services.values())} instances")
    
    def find_service(self, path: str) -> Optional[str]:
        """Find service name based on request path"""
        # Direct pattern matching
        for pattern, service_name in self.service_patterns.items():
            if path.startswith(pattern):
                return service_name
        
        # Fallback pattern matching
        path_parts = path.strip("/").split("/")
        if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1] == "v1":
            service_path = path_parts[2]
            if service_path in self.services:
                return service_path
        
        return None
    
    async def get_healthy_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get a healthy service instance using weighted load balancing"""
        if service_name not in self.services:
            return None
        
        instances = self.services[service_name]
        healthy_instances = [
            inst for inst in instances 
            if inst.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
        ]
        
        if not healthy_instances:
            # No healthy instances, try maintenance ones as last resort
            maintenance_instances = [
                inst for inst in instances 
                if inst.status == ServiceStatus.MAINTENANCE
            ]
            if maintenance_instances:
                logger.warning(f"Using maintenance instance for {service_name}")
                return maintenance_instances[0]
            return None
        
        # Weighted selection based on health score
        weights = [inst.health_score * inst.weight for inst in healthy_instances]
        total_weight = sum(weights)
        
        if total_weight == 0:
            # All instances have zero weight, pick randomly
            return random.choice(healthy_instances)
        
        # Weighted random selection
        r = random.uniform(0, total_weight)
        current = 0
        for inst, weight in zip(healthy_instances, weights):
            current += weight
            if current >= r:
                return inst
        
        # Fallback
        return healthy_instances[0]
    
    async def route_request(self, request: Request) -> Response:
        """Route request to appropriate service"""
        path = request.url.path
        service_name = self.find_service(path)
        
        if not service_name:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Service not found",
                    "message": f"No service configured for path: {path}",
                    "available_services": list(self.services.keys())
                }
            )
        
        instance = await self.get_healthy_instance(service_name)
        if not instance:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service unavailable",
                    "message": f"No healthy instances available for {service_name}",
                    "service": service_name
                }
            )
        
        # Attempt request with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                response = await self._forward_request(request, instance)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Update instance metrics
                instance.response_time = response_time
                instance.success_count += 1
                instance.error_count = max(0, instance.error_count - 1)  # Decay error count
                
                if instance.status == ServiceStatus.DEGRADED and instance.error_count == 0:
                    instance.status = ServiceStatus.HEALTHY
                    logger.info(f"✅ Service {service_name} instance {instance.url} recovered")
                
                return response
                
            except Exception as e:
                last_exception = e
                instance.error_count += 1
                
                # Circuit breaker logic
                if instance.error_count >= self.circuit_breaker_threshold:
                    instance.status = ServiceStatus.UNHEALTHY
                    logger.error(f"🔴 Service {service_name} instance {instance.url} marked unhealthy after {instance.error_count} errors")
                elif instance.error_count >= self.circuit_breaker_threshold // 2:
                    instance.status = ServiceStatus.DEGRADED
                    logger.warning(f"🟡 Service {service_name} instance {instance.url} degraded")
                
                if attempt < self.max_retries:
                    # Try another instance
                    instance = await self.get_healthy_instance(service_name)
                    if not instance:
                        break
                    logger.info(f"🔄 Retrying request on different instance (attempt {attempt + 1})")
                    await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
        
        # All retries failed
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service unavailable",
                "message": f"All attempts to reach {service_name} failed",
                "last_error": str(last_exception),
                "retries": self.max_retries
            }
        )
    
    async def _forward_request(self, request: Request, instance: ServiceInstance) -> Response:
        """Forward request to service instance"""
        # Build target URL
        target_url = urljoin(instance.url, request.url.path)
        if request.url.query:
            target_url += f"?{request.url.query}"
        
        # Prepare headers (exclude hop-by-hop headers)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # Add tracing headers
        headers["X-Forwarded-For"] = request.client.host
        headers["X-Forwarded-Proto"] = request.url.scheme
        headers["X-Gateway-Request-ID"] = getattr(request.state, "request_id", "unknown")
        
        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=True
            )
        
        # Create response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    
    async def health_check_service(self, service_name: str, instance: ServiceInstance):
        """Perform health check on service instance"""
        try:
            health_url = urljoin(instance.url, "/health")
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = time.time()
                response = await client.get(health_url)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    if instance.status == ServiceStatus.UNHEALTHY:
                        logger.info(f"✅ Service {service_name} instance {instance.url} is back online")
                    instance.status = ServiceStatus.HEALTHY
                    instance.response_time = response_time
                    instance.error_count = 0
                else:
                    instance.status = ServiceStatus.DEGRADED
                    
        except Exception as e:
            if instance.status == ServiceStatus.HEALTHY:
                logger.warning(f"⚠️ Health check failed for {service_name} at {instance.url}: {e}")
            instance.status = ServiceStatus.UNHEALTHY
            instance.error_count += 1
        
        instance.last_check = time.time()
    
    async def run_health_checks(self):
        """Run periodic health checks on all service instances"""
        while True:
            try:
                tasks = []
                for service_name, instances in self.services.items():
                    for instance in instances:
                        if time.time() - instance.last_check > self.health_check_interval:
                            task = self.health_check_service(service_name, instance)
                            tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    logger.debug(f"🔍 Completed health checks for {len(tasks)} service instances")
                
            except Exception as e:
                logger.error(f"Error in health check cycle: {e}")
            
            await asyncio.sleep(10)  # Check every 10 seconds for instances that need checking
    
    def start_health_checks(self):
        """Start health check background task"""
        if self.health_check_task is None or self.health_check_task.done():
            self.health_check_task = asyncio.create_task(self.run_health_checks())
            logger.info("🏥 Started health check monitoring")
    
    def stop_health_checks(self):
        """Stop health check background task"""
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            logger.info("🛑 Stopped health check monitoring")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        status = {}
        total_instances = 0
        healthy_instances = 0
        
        for service_name, instances in self.services.items():
            service_status = {
                "instances": [],
                "healthy_count": 0,
                "total_count": len(instances)
            }
            
            for instance in instances:
                instance_info = {
                    "url": instance.url,
                    "status": instance.status.value,
                    "health_score": round(instance.health_score, 3),
                    "response_time": round(instance.response_time, 2),
                    "error_count": instance.error_count,
                    "success_count": instance.success_count,
                    "last_check": instance.last_check
                }
                
                service_status["instances"].append(instance_info)
                total_instances += 1
                
                if instance.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                    service_status["healthy_count"] += 1
                    healthy_instances += 1
            
            service_status["health_percentage"] = (
                service_status["healthy_count"] / service_status["total_count"] * 100
                if service_status["total_count"] > 0 else 0
            )
            
            status[service_name] = service_status
        
        return {
            "services": status,
            "summary": {
                "total_services": len(self.services),
                "total_instances": total_instances,
                "healthy_instances": healthy_instances,
                "overall_health": round(healthy_instances / total_instances * 100, 1) if total_instances > 0 else 0
            }
        }


# Global service router instance
service_router = ServiceRouter()
