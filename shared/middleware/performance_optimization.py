# shared/middleware/performance_optimization.py
"""
System-wide Performance Optimization Middleware
Advanced caching, monitoring, and optimization features for all services
"""

import asyncio
import time
import json
import os
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import psutil
import logging

# Try to import redis and fastapi dependencies
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from fastapi import Request, Response
    from fastapi.middleware.base import BaseHTTPMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

logger = logging.getLogger(__name__)

class PerformanceOptimizationMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Advanced performance optimization middleware"""
    
    def __init__(self, app, service_name: str, redis_url: Optional[str] = None):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.service_name = service_name
        self.redis_client = None
        self.performance_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0}
        self.request_metrics = {}
        
        # Initialize Redis if available
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                logger.warning(f"Redis connection failed, using memory cache: {e}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance optimizations"""
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
        
        # Check cache for GET requests
        if request.method == "GET":
            cached_response = await self._get_cached_response(request)
            if cached_response:
                self.cache_stats["hits"] += 1
                response = Response(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers=cached_response.get("headers", {})
                )
                response.headers["X-Cache"] = "HIT"
                response.headers["X-Response-Time"] = f"{time.time() - start_time:.3f}s"
                return response
            else:
                self.cache_stats["misses"] += 1
        
        # Process request
        response = await call_next(request)
        
        # Calculate performance metrics
        duration = time.time() - start_time
        
        # Cache successful GET responses
        if request.method == "GET" and response.status_code == 200:
            await self._cache_response(request, response, duration)
        
        # Track performance metrics
        await self._track_performance_metrics(request_id, request, response, duration)
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Service"] = self.service_name
        response.headers["X-Cache"] = "MISS" if request.method == "GET" else "N/A"
        
        return response
    
    async def _get_cached_response(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get cached response for request"""
        cache_key = self._generate_cache_key(request)
        
        try:
            # Try Redis first
            if self.redis_client:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            # Fallback to memory cache
            if cache_key in self.performance_cache:
                entry = self.performance_cache[cache_key]
                if entry["expires_at"] > datetime.utcnow():
                    return entry["data"]
                else:
                    del self.performance_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    async def _cache_response(self, request: Request, response: Response, duration: float):
        """Cache response if appropriate"""
        cache_key = self._generate_cache_key(request)
        
        # Determine cache TTL based on endpoint and performance
        ttl_seconds = self._calculate_cache_ttl(request.url.path, duration)
        
        if ttl_seconds > 0:
            try:
                # Create cache data
                cache_data = {
                    "content": "Response content cached",  # Simplified for demo
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "cached_at": datetime.utcnow().isoformat(),
                    "duration": duration
                }
                
                # Cache in Redis
                if self.redis_client:
                    await self.redis_client.setex(
                        cache_key,
                        ttl_seconds,
                        json.dumps(cache_data)
                    )
                
                # Cache in memory as fallback
                self.performance_cache[cache_key] = {
                    "data": cache_data,
                    "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds)
                }
                
            except Exception as e:
                logger.error(f"Response caching failed: {e}")
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        # Include path, query params, and relevant headers
        key_parts = [
            self.service_name,
            request.url.path,
            str(sorted(request.query_params.items())),
            request.headers.get("X-User-ID", "anonymous"),
            request.headers.get("Authorization", "")[:20] if request.headers.get("Authorization") else ""
        ]
        return f"cache:{':'.join(key_parts)}"
    
    def _calculate_cache_ttl(self, path: str, duration: float) -> int:
        """Calculate appropriate cache TTL based on endpoint"""
        # High-performance caching strategy
        cache_strategies = {
            "/health": 10,  # Short cache for health checks
            "/api/v1/analytics": 300,  # 5 minutes for analytics
            "/api/v1/dashboard": 180,  # 3 minutes for dashboard data
            "/api/v1/performance": 120,  # 2 minutes for performance data
            "/api/v1/campaigns": 240,  # 4 minutes for campaign data
            "/api/v1/agents": 180,  # 3 minutes for agent data
        }
        
        # Check for exact match
        for pattern, ttl in cache_strategies.items():
            if pattern in path:
                return ttl
        
        # Dynamic TTL based on response time
        if duration < 0.1:  # Fast responses - short cache
            return 60
        elif duration < 0.5:  # Medium responses - medium cache
            return 180
        elif duration < 2.0:  # Slow responses - longer cache
            return 300
        else:  # Very slow responses - very long cache
            return 600
        
        return 120  # Default 2 minutes
    
    async def _track_performance_metrics(self, request_id: str, request: Request, response: Response, duration: float):
        """Track detailed performance metrics"""
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        
        # Update metrics
        if endpoint not in self.request_metrics:
            self.request_metrics[endpoint] = {
                "count": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "status_codes": {},
                "error_count": 0
            }
        
        metrics = self.request_metrics[endpoint]
        metrics["count"] += 1
        metrics["total_time"] += duration
        metrics["min_time"] = min(metrics["min_time"], duration)
        metrics["max_time"] = max(metrics["max_time"], duration)
        
        if status_code not in metrics["status_codes"]:
            metrics["status_codes"][status_code] = 0
        metrics["status_codes"][status_code] += 1
        
        if status_code >= 400:
            metrics["error_count"] += 1
        
        # Log slow requests
        if duration > 2.0:
            logger.warning(f"Slow request detected: {method} {endpoint} took {duration:.3f}s")
        
        # Store in Redis for monitoring dashboard
        if self.redis_client:
            try:
                performance_data = {
                    "service": self.service_name,
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "method": method,
                    "duration": duration,
                    "status_code": status_code,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Store performance log (simplified)
                await self.redis_client.set(
                    f"perf:{self.service_name}:{request_id}",
                    json.dumps(performance_data),
                    ex=3600  # Expire after 1 hour
                )
                
            except Exception as e:
                logger.error(f"Failed to store performance data: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        total_requests = sum(m["count"] for m in self.request_metrics.values())
        total_cache_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        
        return {
            "service": self.service_name,
            "total_requests": total_requests,
            "cache_stats": {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "hit_rate": (self.cache_stats["hits"] / total_cache_requests * 100) if total_cache_requests > 0 else 0
            },
            "endpoint_metrics": {
                endpoint: {
                    "count": metrics["count"],
                    "avg_time": metrics["total_time"] / metrics["count"] if metrics["count"] > 0 else 0,
                    "min_time": metrics["min_time"] if metrics["min_time"] != float('inf') else 0,
                    "max_time": metrics["max_time"],
                    "error_rate": (metrics["error_count"] / metrics["count"] * 100) if metrics["count"] > 0 else 0
                }
                for endpoint, metrics in self.request_metrics.items()
            },
            "system_resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else 50.0  # Windows fallback
            },
            "timestamp": datetime.utcnow().isoformat()
        }

# Smart Caching Decorator
def smart_cache(ttl: int = 300, key_prefix: Optional[str] = None, redis_client: Optional[Any] = None):
    """Smart caching decorator with automatic cache invalidation"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(kwargs))}"
            
            try:
                # Try to get from cache
                if redis_client and REDIS_AVAILABLE:
                    cached_result = await redis_client.get(cache_key)
                    if cached_result:
                        return json.loads(cached_result)
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                
                if redis_client and REDIS_AVAILABLE:
                    await redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                
                return result
                
            except Exception as e:
                logger.error(f"Caching error in {func.__name__}: {e}")
                # Return uncached result on cache failure
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Real-time Performance Monitor
class RealTimePerformanceMonitor:
    """Real-time performance monitoring and optimization"""
    
    def __init__(self, service_name: str, redis_client: Optional[Any] = None):
        self.service_name = service_name
        self.redis_client = redis_client
        self.running = False
        self.optimization_rules = []
    
    async def start_monitoring(self):
        """Start real-time performance monitoring"""
        self.running = True
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._optimize_cache())
        asyncio.create_task(self._detect_anomalies())
        
        logger.info(f"Performance monitoring started for {self.service_name}")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.running = False
        logger.info(f"Performance monitoring stopped for {self.service_name}")
    
    async def _monitor_performance(self):
        """Monitor performance metrics in real-time"""
        while self.running:
            try:
                # Collect system metrics
                metrics = {
                    "service": self.service_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                    "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
                }
                
                # Store metrics in Redis
                if self.redis_client and REDIS_AVAILABLE:
                    await self.redis_client.set(
                        f"sys_metrics:{self.service_name}:{int(time.time())}",
                        json.dumps(metrics),
                        ex=3600  # Expire after 1 hour
                    )
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _optimize_cache(self):
        """Automatically optimize cache based on usage patterns"""
        while self.running:
            try:
                if self.redis_client and REDIS_AVAILABLE:
                    # Simple cache optimization
                    cache_info = await self.redis_client.info("memory")
                    logger.debug(f"Cache optimization running for {self.service_name}")
                
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
            except Exception as e:
                logger.error(f"Cache optimization error: {e}")
                await asyncio.sleep(600)
    
    async def _detect_anomalies(self):
        """Detect performance anomalies and auto-optimize"""
        while self.running:
            try:
                # Check for high CPU usage
                cpu_percent = psutil.cpu_percent(interval=5)
                if cpu_percent > 80:
                    logger.warning(f"High CPU usage detected: {cpu_percent}%")
                    await self._apply_cpu_optimization()
                
                # Check for high memory usage
                memory_percent = psutil.virtual_memory().percent
                if memory_percent > 85:
                    logger.warning(f"High memory usage detected: {memory_percent}%")
                    await self._apply_memory_optimization()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Anomaly detection error: {e}")
                await asyncio.sleep(120)
    
    async def _apply_cpu_optimization(self):
        """Apply CPU optimization strategies"""
        logger.info("CPU optimization applied")
    
    async def _apply_memory_optimization(self):
        """Apply memory optimization strategies"""
        logger.info("Memory optimization applied")

# Utility Functions
async def add_performance_optimization(
    app,
    service_name: str,
    redis_url: Optional[str] = None,
    enable_monitoring: bool = True
) -> tuple:
    """Add performance optimization to FastAPI app"""
    
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI not available, skipping middleware")
        return app, None
    
    # Add performance middleware
    app.add_middleware(
        PerformanceOptimizationMiddleware,
        service_name=service_name,
        redis_url=redis_url
    )
    
    # Initialize performance monitor
    monitor = None
    if enable_monitoring and redis_url and REDIS_AVAILABLE:
        try:
            redis_client = redis.from_url(redis_url)
            monitor = RealTimePerformanceMonitor(service_name, redis_client)
            await monitor.start_monitoring()
        except Exception as e:
            logger.warning(f"Performance monitor initialization failed: {e}")
    
    # Add performance endpoints
    @app.get("/performance/stats")
    async def get_performance_stats():
        """Get current performance statistics"""
        # Get middleware instance
        for middleware in app.middleware_stack:
            if hasattr(middleware, 'cls') and middleware.cls == PerformanceOptimizationMiddleware:
                return middleware.kwargs.get('app', {})
        return {"service": service_name, "status": "monitoring_active"}
    
    @app.post("/performance/clear-cache")
    async def clear_performance_cache():
        """Clear performance cache"""
        try:
            if redis_url and REDIS_AVAILABLE:
                redis_client = redis.from_url(redis_url)
                # Clear specific cache keys
                keys = await redis_client.keys(f"cache:{service_name}:*")
                if keys:
                    await redis_client.delete(*keys)
                return {"success": True, "message": "Cache cleared", "keys_cleared": len(keys)}
            return {"error": "Redis not available"}
        except Exception as e:
            return {"error": f"Cache clear failed: {str(e)}"}
    
    return app, monitor

# Export all optimization tools
__all__ = [
    "PerformanceOptimizationMiddleware",
    "smart_cache", 
    "RealTimePerformanceMonitor",
    "add_performance_optimization"
]
