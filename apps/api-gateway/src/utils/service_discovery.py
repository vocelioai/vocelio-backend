# apps/api-gateway/src/utils/service_discovery.py
import asyncio
import time
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import json
import os

from ..config import settings, SERVICE_CONFIG

logger = logging.getLogger(__name__)

class ServiceHealth:
    """Track health status of individual services"""
    
    def __init__(self, service_name: str, service_url: str):
        self.service_name = service_name
        self.service_url = service_url
        self.is_healthy = True
        self.last_check = datetime.utcnow()
        self.consecutive_failures = 0
        self.response_times = []  # Last 10 response times
        self.error_count = 0
        self.total_requests = 0
        self.last_error = None
        self.uptime_start = datetime.utcnow()
    
    def record_success(self, response_time: float):
        """Record successful health check"""
        self.is_healthy = True
        self.consecutive_failures = 0
        self.last_check = datetime.utcnow()
        self.total_requests += 1
        
        # Keep last 10 response times for average calculation
        self.response_times.append(response_time)
        if len(self.response_times) > 10:
            self.response_times.pop(0)
        
        logger.debug(f"✅ {self.service_name} health check successful: {response_time:.3f}s")
    
    def record_failure(self, error: str):
        """Record failed health check"""
        self.consecutive_failures += 1
        self.error_count += 1
        self.total_requests += 1
        self.last_error = error
        self.last_check = datetime.utcnow()
        
        # Mark as unhealthy after threshold failures
        if self.consecutive_failures >= settings.UNHEALTHY_THRESHOLD:
            self.is_healthy = False
            logger.warning(f"❌ {self.service_name} marked as unhealthy after {self.consecutive_failures} failures")
        
        logger.debug(f"⚠️ {self.service_name} health check failed: {error}")
    
    def get_average_response_time(self) -> float:
        """Get average response time from recent checks"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_error_rate(self) -> float:
        """Get error rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.error_count / self.total_requests) * 100
    
    def get_uptime_seconds(self) -> float:
        """Get uptime in seconds"""
        return (datetime.utcnow() - self.uptime_start).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "service_name": self.service_name,
            "service_url": self.service_url,
            "is_healthy": self.is_healthy,
            "last_check": self.last_check.isoformat(),
            "consecutive_failures": self.consecutive_failures,
            "avg_response_time": round(self.get_average_response_time(), 3),
            "error_rate": round(self.get_error_rate(), 2),
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "uptime_seconds": round(self.get_uptime_seconds(), 1),
            "last_error": self.last_error
        }

class ServiceDiscovery:
    """Advanced service discovery with health monitoring and circuit breaker"""
    
    def __init__(self, services: Dict[str, str]):
        self.services = services
        self.service_health: Dict[str, ServiceHealth] = {}
        self.circuit_breakers: Dict[str, Dict] = {}
        self.health_check_task: Optional[asyncio.Task] = None
        self.start_time = datetime.utcnow()
        
        # Initialize service health tracking
        for service_name, service_url in services.items():
            self.service_health[service_name] = ServiceHealth(service_name, service_url)
            self.circuit_breakers[service_name] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure": None,
                "next_attempt": None
            }
    
    async def initialize(self):
        """Initialize service discovery"""
        logger.info("🔍 Initializing Service Discovery...")
        
        # Perform initial health check of all services
        await self.health_check_all_services()
        
        logger.info(f"🎯 Service Discovery initialized with {len(self.services)} services")
    
    async def health_check_all_services(self) -> int:
        """Check health of all services and return number of healthy services"""
        health_check_tasks = []
        
        for service_name in self.services.keys():
            task = asyncio.create_task(
                self.check_service_health(service_name),
                name=f"health_check_{service_name}"
            )
            health_check_tasks.append(task)
        
        try:
            # Wait for all health checks with timeout
            await asyncio.wait_for(
                asyncio.gather(*health_check_tasks, return_exceptions=True),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            logger.warning("⏰ Some health checks timed out")
        
        # Count healthy services
        healthy_count = sum(1 for health in self.service_health.values() if health.is_healthy)
        total_count = len(self.service_health)
        
        logger.info(f"📊 Health Check Complete: {healthy_count}/{total_count} services healthy")
        return healthy_count
    
    async def check_service_health(self, service_name: str) -> bool:
        """Check health of specific service"""
        if service_name not in self.services:
            logger.error(f"❌ Unknown service: {service_name}")
            return False

        service_url = self.services[service_name]
        service_health = self.service_health[service_name]
        config = SERVICE_CONFIG.get(service_name, {})

        # Respect circuit breaker state
        if not self._is_circuit_breaker_closed(service_name):
            logger.debug(f"🔌 Circuit breaker open for {service_name}")
            return False

        try:
            start_time = time.time()
            health_path = config.get("health_check_path", "/health")
            timeout = config.get("timeout", settings.HEALTH_CHECK_TIMEOUT)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{service_url}{health_path}")
            response_time = time.time() - start_time

            if response.status_code == 200:
                service_health.record_success(response_time)
                self._reset_circuit_breaker(service_name)
                return True
            else:
                service_health.record_failure(f"HTTP {response.status_code}")
                self._record_circuit_breaker_failure(service_name)
                return False

        except httpx.TimeoutException:
            service_health.record_failure("timeout")
            self._record_circuit_breaker_failure(service_name)
            return False
        except httpx.ConnectError:
            service_health.record_failure("connection_error")
            self._record_circuit_breaker_failure(service_name)
            return False
        except Exception as e:
            service_health.record_failure(str(e))
            self._record_circuit_breaker_failure(service_name)
            return False
    
    def _is_circuit_breaker_closed(self, service_name: str) -> bool:
        """Check if circuit breaker allows requests"""
        if not settings.CIRCUIT_BREAKER_ENABLED:
            return True
        cb = self.circuit_breakers[service_name]
        current_time = datetime.utcnow()
        if cb["state"] == "closed":
            return True
        if cb["state"] == "open":
            if cb["next_attempt"] and current_time >= cb["next_attempt"]:
                cb["state"] = "half_open"
                logger.info(f"🔄 Circuit breaker half-open for {service_name}")
                return True
            return False
        if cb["state"] == "half_open":
            return True
        return False
    
    def _record_circuit_breaker_failure(self, service_name: str):
        """Record failure for circuit breaker"""
        if not settings.CIRCUIT_BREAKER_ENABLED:
            return
        cb = self.circuit_breakers[service_name]
        cb["failure_count"] += 1
        cb["last_failure"] = datetime.utcnow()
        if cb["failure_count"] >= settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD and cb["state"] != "open":
            cb["state"] = "open"
            cb["next_attempt"] = datetime.utcnow() + timedelta(seconds=settings.CIRCUIT_BREAKER_TIMEOUT)
            logger.warning(f"🔴 Circuit breaker opened for {service_name}")
    
    def _reset_circuit_breaker(self, service_name: str):
        """Reset circuit breaker on successful request"""
        if not settings.CIRCUIT_BREAKER_ENABLED:
            return
        cb = self.circuit_breakers[service_name]
        if cb["state"] != "closed":
            cb["state"] = "closed"
            cb["failure_count"] = 0
            cb["next_attempt"] = None
            logger.info(f"🟢 Circuit breaker closed for {service_name}")
    
    async def get_healthy_services(self) -> List[str]:
        """Get list of currently healthy services"""
        healthy_services = []
        for service_name, health in self.service_health.items():
            if health.is_healthy and self._is_circuit_breaker_closed(service_name):
                healthy_services.append(service_name)
        return healthy_services
    
    async def get_active_services_count(self) -> int:
        """Get count of active/healthy services"""
        healthy_services = await self.get_healthy_services()
        return len(healthy_services)
    
    async def is_service_healthy(self, service_name: str) -> bool:
        """Check if specific service is healthy"""
        if service_name not in self.service_health:
            return False
        
        health = self.service_health[service_name]
        return health.is_healthy and self._is_circuit_breaker_closed(service_name)
    
    async def update_service_health(self, service_name: str, status_code: int, response_time: float):
        """Update service health based on actual request results"""
        if service_name not in self.service_health:
            return
        
        service_health = self.service_health[service_name]
        
        if 200 <= status_code < 400:
            service_health.record_success(response_time)
            self._reset_circuit_breaker(service_name)
        else:
            service_health.record_failure(f"HTTP {status_code}")
            self._record_circuit_breaker_failure(service_name)
    
    async def mark_service_unhealthy(self, service_name: str, reason: str):
        """Manually mark service as unhealthy"""
        if service_name in self.service_health:
            self.service_health[service_name].record_failure(reason)
            self._record_circuit_breaker_failure(service_name)
            logger.warning(f"⚠️ Manually marked {service_name} as unhealthy: {reason}")
    
    async def force_health_check(self, service_name: str) -> bool:
        """Force immediate health check of specific service"""
        logger.info(f"🔄 Forcing health check for {service_name}")
        return await self.check_service_health(service_name)
    
    async def get_health_metrics(self) -> Dict[str, Any]:
        """Get comprehensive health metrics"""
        healthy_services = await self.get_healthy_services()
        total_services = len(self.services)
        
        # Calculate overall metrics
        total_requests = sum(health.total_requests for health in self.service_health.values())
        total_errors = sum(health.error_count for health in self.service_health.values())
        avg_response_times = [health.get_average_response_time() for health in self.service_health.values() if health.response_times]
        
        overall_error_rate = (total_errors / max(total_requests, 1)) * 100
        overall_avg_response_time = sum(avg_response_times) / max(len(avg_response_times), 1)
        
        # Service-specific metrics
        service_metrics = {}
        for service_name, health in self.service_health.items():
            service_metrics[service_name] = health.to_dict()
            service_metrics[service_name]["circuit_breaker"] = self.circuit_breakers[service_name].copy()
        
        return {
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "total_requests": total_requests,
            "error_rate": round(overall_error_rate, 2),
            "avg_response_time": round(overall_avg_response_time, 3),
            "healthy_services_count": len(healthy_services),
            "total_services_count": total_services,
            "health_ratio": round(len(healthy_services) / max(total_services, 1), 2),
            "services": service_metrics
        }
    
    async def periodic_health_check(self):
        """Background task for periodic health checks"""
        logger.info(f"🔄 Starting periodic health checks (interval: {settings.HEALTH_CHECK_INTERVAL}s)")
        
        while True:
            try:
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
                
                logger.debug("🔍 Performing periodic health check...")
                healthy_count = await self.health_check_all_services()
                
                # Log summary
                total_services = len(self.services)
                health_ratio = healthy_count / total_services
                
                if health_ratio >= 0.8:
                    log_level = logging.INFO
                    status_emoji = "✅"
                elif health_ratio >= 0.5:
                    log_level = logging.WARNING
                    status_emoji = "⚠️"
                else:
                    log_level = logging.ERROR
                    status_emoji = "❌"
                
                logger.log(
                    log_level,
                    f"{status_emoji} Health Check: {healthy_count}/{total_services} services healthy ({health_ratio:.1%})"
                )
                
            except Exception as e:
                logger.error(f"❌ Error in periodic health check: {e}")
                await asyncio.sleep(5)  # Short delay before retrying
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🧹 Service Discovery cleaned up")
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about specific service"""
        if service_name not in self.service_health:
            return None
        health = self.service_health[service_name]
        circuit_breaker = self.circuit_breakers[service_name]
        config = SERVICE_CONFIG.get(service_name, {})
        return {
            "service_name": service_name,
            "display_name": config.get("name", service_name.replace("-", " ").title()),
            "url": self.services[service_name],
            "health": health.to_dict(),
            "circuit_breaker": circuit_breaker.copy(),
            "config": config,
        }
    
    def get_all_services_info(self) -> Dict[str, Any]:
        """Get info about all services"""
        services_info = {}
        for service_name in self.services.keys():
            services_info[service_name] = self.get_service_info(service_name)
        
        return services_info

# Export for use in main application
__all__ = ["ServiceDiscovery", "ServiceHealth"]