"""
Comprehensive Metrics Collection System for Vocelio API Gateway
Tracks requests, performance, errors, and service health metrics
"""

import time
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, DefaultDict
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import redis.asyncio as redis
from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class RequestMetric:
    """Individual request metric data"""
    timestamp: float
    service: str
    method: str
    path: str
    status_code: int
    duration: float
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    error_message: Optional[str] = None


class MetricsCollector:
    """Advanced metrics collection and analytics system"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connection_ready = False
        
        # In-memory metrics (fallback when Redis is unavailable)
        self.request_metrics: deque = deque(maxlen=10000)
        self.service_metrics: DefaultDict[str, List] = defaultdict(list)
        self.error_metrics: deque = deque(maxlen=1000)
        self.performance_metrics: deque = deque(maxlen=5000)
        
        # Counters
        self.total_requests = 0
        self.total_errors = 0
        self.service_counters: DefaultDict[str, int] = defaultdict(int)
        self.status_counters: DefaultDict[int, int] = defaultdict(int)
        
        # Performance tracking
        self.response_times: DefaultDict[str, List[float]] = defaultdict(list)
        self.start_time = time.time()
        
        # Metrics retention settings
        self.retention_hours = 24
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    async def initialize(self):
        """Initialize Redis connection for metrics storage"""
        if not settings.REDIS_URL:
            logger.warning("⚠️ No Redis URL configured, using memory-based metrics")
            return
        
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            self.connection_ready = True
            logger.info("✅ Redis connected for metrics collection")
            
            # Start background cleanup task
            asyncio.create_task(self._periodic_cleanup())
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed, using memory store: {e}")
            self.redis_client = None
            self.connection_ready = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("📊 Metrics collector closed")
    
    def get_timestamp(self) -> float:
        """Get current timestamp"""
        return time.time()
    
    async def record_request(
        self,
        service: Optional[str],
        method: str,
        status_code: int,
        duration: float,
        path: str = "",
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Record a request metric"""
        timestamp = self.get_timestamp()
        
        # Create metric record
        metric = RequestMetric(
            timestamp=timestamp,
            service=service or "unknown",
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            user_id=user_id,
            organization_id=organization_id,
            error_message=error_message
        )
        
        # Update counters
        self.total_requests += 1
        self.service_counters[metric.service] += 1
        self.status_counters[status_code] += 1
        
        if status_code >= 400:
            self.total_errors += 1
        
        # Store in memory
        self.request_metrics.append(metric)
        self.service_metrics[metric.service].append(metric)
        self.response_times[metric.service].append(duration)
        
        # Store in Redis if available
        if self.redis_client and self.connection_ready:
            await self._store_metric_in_redis(metric)
        
        # Record error separately
        if status_code >= 400:
            await self._record_error(metric)
    
    async def _store_metric_in_redis(self, metric: RequestMetric):
        """Store metric in Redis for persistence and analytics"""
        try:
            # Create metric data
            metric_data = {
                "timestamp": metric.timestamp,
                "service": metric.service,
                "method": metric.method,
                "path": metric.path,
                "status_code": metric.status_code,
                "duration": metric.duration,
                "user_id": metric.user_id,
                "organization_id": metric.organization_id,
                "error_message": metric.error_message
            }
            
            # Store in time-series format
            key = f"metrics:requests:{int(metric.timestamp)}"
            await self.redis_client.setex(
                key, 
                self.retention_hours * 3600,  # TTL
                json.dumps(metric_data)
            )
            
            # Update aggregated counters
            pipe = self.redis_client.pipeline()
            
            # Daily counters
            date_key = datetime.fromtimestamp(metric.timestamp).strftime("%Y-%m-%d")
            pipe.hincrby(f"metrics:daily:{date_key}", "total_requests", 1)
            pipe.hincrby(f"metrics:daily:{date_key}", f"service:{metric.service}", 1)
            pipe.hincrby(f"metrics:daily:{date_key}", f"status:{metric.status_code}", 1)
            
            # Hourly performance metrics
            hour_key = datetime.fromtimestamp(metric.timestamp).strftime("%Y-%m-%d:%H")
            pipe.lpush(f"metrics:performance:{hour_key}", metric.duration)
            pipe.expire(f"metrics:performance:{hour_key}", self.retention_hours * 3600)
            
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"Error storing metric in Redis: {e}")
    
    async def _record_error(self, metric: RequestMetric):
        """Record error metrics separately"""
        error_data = {
            "timestamp": metric.timestamp,
            "service": metric.service,
            "method": metric.method,
            "path": metric.path,
            "status_code": metric.status_code,
            "duration": metric.duration,
            "error_message": metric.error_message,
            "user_id": metric.user_id
        }
        
        self.error_metrics.append(error_data)
        
        # Store in Redis
        if self.redis_client and self.connection_ready:
            try:
                key = f"metrics:errors:{int(metric.timestamp)}"
                await self.redis_client.setex(
                    key,
                    self.retention_hours * 3600,
                    json.dumps(error_data)
                )
            except Exception as e:
                logger.error(f"Error storing error metric: {e}")
    
    def get_request_count(self) -> int:
        """Get total request count"""
        return self.total_requests
    
    def get_error_count(self) -> int:
        """Get total error count"""
        return self.total_errors
    
    def get_error_rate(self) -> float:
        """Get error rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.total_errors / self.total_requests) * 100
    
    def get_service_metrics(self, service: str) -> Dict[str, Any]:
        """Get metrics for a specific service"""
        service_requests = self.service_metrics.get(service, [])
        service_response_times = self.response_times.get(service, [])
        
        if not service_requests:
            return {"message": f"No metrics available for service: {service}"}
        
        # Calculate statistics
        total_requests = len(service_requests)
        error_requests = len([r for r in service_requests if r.status_code >= 400])
        
        response_times = [r.duration for r in service_requests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "service": service,
            "total_requests": total_requests,
            "error_count": error_requests,
            "error_rate": (error_requests / total_requests) * 100 if total_requests > 0 else 0,
            "avg_response_time": round(avg_response_time, 3),
            "min_response_time": round(min(response_times), 3) if response_times else 0,
            "max_response_time": round(max(response_times), 3) if response_times else 0,
            "requests_per_minute": self._calculate_requests_per_minute(service_requests)
        }
    
    def _calculate_requests_per_minute(self, requests: List[RequestMetric]) -> float:
        """Calculate requests per minute for a service"""
        if not requests:
            return 0.0
        
        current_time = time.time()
        one_minute_ago = current_time - 60
        
        recent_requests = [r for r in requests if r.timestamp > one_minute_ago]
        return len(recent_requests)
    
    def get_status_code_distribution(self) -> Dict[str, Any]:
        """Get status code distribution"""
        total = sum(self.status_counters.values())
        
        if total == 0:
            return {"message": "No requests recorded"}
        
        distribution = {}
        for status_code, count in self.status_counters.items():
            percentage = (count / total) * 100
            distribution[str(status_code)] = {
                "count": count,
                "percentage": round(percentage, 1)
            }
        
        return {
            "total_requests": total,
            "distribution": distribution
        }
    
    def get_top_services(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top services by request count"""
        sorted_services = sorted(
            self.service_counters.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "service": service,
                "request_count": count,
                "percentage": round((count / self.total_requests) * 100, 1) if self.total_requests > 0 else 0
            }
            for service, count in sorted_services[:limit]
        ]
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent error metrics"""
        recent_errors = list(self.error_metrics)[-limit:]
        
        return [
            {
                "timestamp": error["timestamp"],
                "datetime": datetime.fromtimestamp(error["timestamp"]).isoformat(),
                "service": error["service"],
                "method": error["method"],
                "path": error["path"],
                "status_code": error["status_code"],
                "duration": error["duration"],
                "error_message": error["error_message"],
                "user_id": error.get("user_id")
            }
            for error in reversed(recent_errors)
        ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics"""
        if not self.request_metrics:
            return {"message": "No performance data available"}
        
        all_durations = [r.duration for r in self.request_metrics]
        
        return {
            "total_requests": len(all_durations),
            "avg_response_time": round(sum(all_durations) / len(all_durations), 3),
            "min_response_time": round(min(all_durations), 3),
            "max_response_time": round(max(all_durations), 3),
            "median_response_time": round(sorted(all_durations)[len(all_durations)//2], 3),
            "p95_response_time": round(sorted(all_durations)[int(len(all_durations) * 0.95)], 3),
            "p99_response_time": round(sorted(all_durations)[int(len(all_durations) * 0.99)], 3)
        }
    
    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics report"""
        uptime = time.time() - self.start_time
        
        # Get metrics from Redis if available
        redis_metrics = {}
        if self.redis_client and self.connection_ready:
            redis_metrics = await self._get_redis_metrics()
        
        return {
            "timestamp": self.get_timestamp(),
            "uptime": {
                "seconds": round(uptime, 1),
                "human_readable": str(timedelta(seconds=uptime))
            },
            "requests": {
                "total": self.total_requests,
                "errors": self.total_errors,
                "error_rate": round(self.get_error_rate(), 2),
                "requests_per_second": round(self.total_requests / uptime, 2) if uptime > 0 else 0
            },
            "services": {
                "total_services": len(self.service_counters),
                "top_services": self.get_top_services(5),
                "service_distribution": dict(self.service_counters)
            },
            "performance": self.get_performance_metrics(),
            "status_codes": self.get_status_code_distribution(),
            "recent_errors": self.get_recent_errors(10),
            "redis_metrics": redis_metrics
        }
    
    async def _get_redis_metrics(self) -> Dict[str, Any]:
        """Get metrics from Redis storage"""
        try:
            # Get today's metrics
            today = datetime.now().strftime("%Y-%m-%d")
            daily_metrics = await self.redis_client.hgetall(f"metrics:daily:{today}")
            
            # Get current hour performance
            current_hour = datetime.now().strftime("%Y-%m-%d:%H")
            performance_data = await self.redis_client.lrange(f"metrics:performance:{current_hour}", 0, -1)
            
            return {
                "daily_totals": daily_metrics,
                "current_hour_performance": [float(x) for x in performance_data] if performance_data else []
            }
            
        except Exception as e:
            logger.error(f"Error getting Redis metrics: {e}")
            return {"error": str(e)}
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of old metrics"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = time.time()
                cutoff_time = current_time - (self.retention_hours * 3600)
                
                # Clean memory metrics
                self.request_metrics = deque(
                    [m for m in self.request_metrics if m.timestamp > cutoff_time],
                    maxlen=10000
                )
                
                # Clean service metrics
                for service in self.service_metrics:
                    self.service_metrics[service] = [
                        m for m in self.service_metrics[service] 
                        if m.timestamp > cutoff_time
                    ]
                
                # Clean response times
                for service in self.response_times:
                    # Keep only recent response times (last 1000 per service)
                    if len(self.response_times[service]) > 1000:
                        self.response_times[service] = self.response_times[service][-1000:]
                
                logger.debug("🧹 Metrics cleanup completed")
                
            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get metrics related to system health"""
        current_time = time.time()
        one_minute_ago = current_time - 60
        
        # Recent request rate
        recent_requests = [r for r in self.request_metrics if r.timestamp > one_minute_ago]
        requests_per_minute = len(recent_requests)
        
        # Recent error rate
        recent_errors = [r for r in recent_requests if r.status_code >= 400]
        recent_error_rate = (len(recent_errors) / len(recent_requests) * 100) if recent_requests else 0
        
        return {
            "requests_per_minute": requests_per_minute,
            "recent_error_rate": round(recent_error_rate, 2),
            "total_services_active": len([s for s, reqs in self.service_counters.items() if reqs > 0]),
            "memory_usage": {
                "request_metrics_count": len(self.request_metrics),
                "error_metrics_count": len(self.error_metrics),
                "service_metrics_count": sum(len(metrics) for metrics in self.service_metrics.values())
            }
        }
