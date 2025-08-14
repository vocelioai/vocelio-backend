# Enhanced Service Communication Client for Vocelio Services
import asyncio
import httpx
import logging
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class CircuitBreakerState:
    """Circuit breaker state for service calls"""
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    state: str = "closed"  # closed, open, half-open
    failure_threshold: int = 5
    recovery_timeout: int = 30
    
    def should_attempt_call(self) -> bool:
        """Check if we should attempt a service call"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - (self.last_failure_time or 0) > self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True
    
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"

@dataclass 
class ServiceMetrics:
    """Service performance metrics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_response_time: float = 0.0
    fastest_call: float = float('inf')
    slowest_call: float = 0.0
    last_call_time: Optional[datetime] = None
    last_error: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
    
    @property
    def average_response_time(self) -> float:
        if self.successful_calls == 0:
            return 0.0
        return self.total_response_time / self.successful_calls
    
    def record_call(self, success: bool, response_time: float, error: Optional[str] = None):
        """Record call metrics"""
        self.total_calls += 1
        self.last_call_time = datetime.utcnow()
        
        if success:
            self.successful_calls += 1
            self.total_response_time += response_time
            self.fastest_call = min(self.fastest_call, response_time)
            self.slowest_call = max(self.slowest_call, response_time)
        else:
            self.failed_calls += 1
            self.last_error = error

class ServiceClient:
    """
    Enhanced service communication client with circuit breaker, retry logic,
    and comprehensive monitoring for Vocelio microservices
    """
    
    def __init__(self, service_name: str, base_url: str, timeout: int = 30):
        self.service_name = service_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Circuit breaker and metrics
        self.circuit_breaker = CircuitBreakerState()
        self.metrics = ServiceMetrics()
        
        # HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        
        logger.info(f"🔧 ServiceClient initialized for {service_name} at {base_url}")
    
    async def make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with circuit breaker, retries, and monitoring
        """
        url = f"{self.base_url}{endpoint}"
        
        # Check circuit breaker
        if not self.circuit_breaker.should_attempt_call():
            error_msg = f"Circuit breaker open for {self.service_name}"
            logger.warning(error_msg)
            self.metrics.record_call(False, 0.0, error_msg)
            raise ServiceUnavailableException(error_msg)
        
        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "X-Service-Client": f"vocelio-{self.service_name}",
            "X-Request-ID": f"req_{int(time.time() * 1000)}",
            **(headers or {})
        }
        
        # Retry logic
        last_error = None
        for attempt in range(retries + 1):
            try:
                start_time = time.time()
                
                # Make request
                logger.debug(f"🌐 {method} {url} (attempt {attempt + 1}/{retries + 1})")
                
                if method.upper() == "GET":
                    response = await self.client.get(url, headers=request_headers, **kwargs)
                elif method.upper() == "POST":
                    response = await self.client.post(url, json=data, headers=request_headers, **kwargs)
                elif method.upper() == "PUT":
                    response = await self.client.put(url, json=data, headers=request_headers, **kwargs)
                elif method.upper() == "DELETE":
                    response = await self.client.delete(url, headers=request_headers, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response_time = time.time() - start_time
                
                # Handle response
                if response.status_code < 400:
                    # Success
                    self.circuit_breaker.record_success()
                    self.metrics.record_call(True, response_time)
                    
                    logger.debug(f"✅ {self.service_name} request successful ({response_time:.3f}s)")
                    
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"status": "success", "data": response.text}
                
                else:
                    # HTTP error
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.metrics.record_call(False, response_time, error_msg)
                    
                    if response.status_code >= 500:
                        # Server error - retry
                        last_error = ServiceException(error_msg, response.status_code)
                        if attempt < retries:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    
                    # Client error or final retry - don't retry
                    self.circuit_breaker.record_failure()
                    raise ServiceException(error_msg, response.status_code)
            
            except httpx.TimeoutException:
                error_msg = f"Request timeout to {self.service_name}"
                self.metrics.record_call(False, 0.0, error_msg)
                last_error = ServiceTimeoutException(error_msg)
                
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                    
            except httpx.RequestError as e:
                error_msg = f"Request error to {self.service_name}: {str(e)}"
                self.metrics.record_call(False, 0.0, error_msg)
                last_error = ServiceException(error_msg)
                
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
        
        # All retries failed
        self.circuit_breaker.record_failure()
        logger.error(f"❌ All retry attempts failed for {self.service_name}")
        raise last_error or ServiceException(f"Request failed after {retries + 1} attempts")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            result = await self.make_request("/health", retries=1)
            return {
                "service": self.service_name,
                "status": ServiceStatus.HEALTHY,
                "url": self.base_url,
                "response": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service": self.service_name,
                "status": ServiceStatus.UNHEALTHY,
                "url": self.base_url,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service call metrics"""
        return {
            "service": self.service_name,
            "url": self.base_url,
            "circuit_breaker": {
                "state": self.circuit_breaker.state,
                "failure_count": self.circuit_breaker.failure_count,
                "last_failure": self.circuit_breaker.last_failure_time
            },
            "metrics": {
                "total_calls": self.metrics.total_calls,
                "successful_calls": self.metrics.successful_calls,
                "failed_calls": self.metrics.failed_calls,
                "success_rate_percent": round(self.metrics.success_rate, 2),
                "average_response_time_ms": round(self.metrics.average_response_time * 1000, 2),
                "fastest_call_ms": round(self.metrics.fastest_call * 1000, 2) if self.metrics.fastest_call != float('inf') else 0,
                "slowest_call_ms": round(self.metrics.slowest_call * 1000, 2),
                "last_call": self.metrics.last_call_time.isoformat() if self.metrics.last_call_time else None,
                "last_error": self.metrics.last_error
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class ServiceRegistry:
    """
    Central registry for managing multiple service clients
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceClient] = {}
        logger.info("🏢 ServiceRegistry initialized")
    
    def register_service(self, name: str, url: str, timeout: int = 30) -> ServiceClient:
        """Register a new service"""
        client = ServiceClient(name, url, timeout)
        self.services[name] = client
        logger.info(f"📝 Registered service: {name} at {url}")
        return client
    
    def get_service(self, name: str) -> Optional[ServiceClient]:
        """Get service client by name"""
        return self.services.get(name)
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Check health of all registered services"""
        logger.info(f"🏥 Checking health of {len(self.services)} services")
        
        health_checks = []
        for service in self.services.values():
            health_checks.append(service.health_check())
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Process results
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_services": len(self.services),
            "services": {},
            "summary": {
                "healthy": 0,
                "unhealthy": 0,
                "unknown": 0
            }
        }
        
        for i, result in enumerate(results):
            service_name = list(self.services.keys())[i]
            
            if isinstance(result, Exception):
                health_data["services"][service_name] = {
                    "status": ServiceStatus.UNKNOWN,
                    "error": str(result)
                }
                health_data["summary"]["unknown"] += 1
            else:
                health_data["services"][service_name] = result
                status = result.get("status", ServiceStatus.UNKNOWN)
                if status == ServiceStatus.HEALTHY:
                    health_data["summary"]["healthy"] += 1
                else:
                    health_data["summary"]["unhealthy"] += 1
        
        # Calculate overall health percentage
        total = health_data["total_services"]
        healthy = health_data["summary"]["healthy"]
        health_data["overall_health_percent"] = round((healthy / total) * 100, 1) if total > 0 else 0
        
        logger.info(f"📊 Health check complete: {healthy}/{total} services healthy ({health_data['overall_health_percent']}%)")
        
        return health_data
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all services"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {name: client.get_metrics() for name, client in self.services.items()}
        }
    
    async def close_all(self):
        """Close all service clients"""
        for client in self.services.values():
            await client.close()
        logger.info("🔒 All service clients closed")


# Exception classes
class ServiceException(Exception):
    """Base exception for service communication errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ServiceUnavailableException(ServiceException):
    """Service is unavailable (circuit breaker open)"""
    def __init__(self, message: str):
        super().__init__(message, 503)

class ServiceTimeoutException(ServiceException):
    """Service request timed out"""
    def __init__(self, message: str):
        super().__init__(message, 504)


# Example usage
"""
# Initialize service registry
registry = ServiceRegistry()

# Register services
registry.register_service("ai-agents", "https://ai-agents-production.up.railway.app")
registry.register_service("call-center", "https://call-center-production.up.railway.app")

# Use service
ai_service = registry.get_service("ai-agents")
try:
    agents = await ai_service.make_request("/agents")
    print(f"Retrieved {len(agents)} agents")
except ServiceException as e:
    print(f"Service error: {e.message}")

# Check health of all services
health_status = await registry.health_check_all()
print(f"Overall health: {health_status['overall_health_percent']}%")
"""
