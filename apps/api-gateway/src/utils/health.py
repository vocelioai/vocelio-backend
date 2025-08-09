"""
Health Monitoring System for Vocelio API Gateway
Comprehensive health checks for gateway and all connected services
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import httpx
import json

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status information"""
    status: str  # healthy, degraded, unhealthy
    message: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """Comprehensive health monitoring for the API Gateway"""
    
    def __init__(self):
        self.start_time = time.time()
        self.monitoring_enabled = True
        self.health_history: List[HealthStatus] = []
        self.max_history = 100
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Health thresholds
        self.memory_threshold = 80  # percent
        self.cpu_threshold = 80     # percent
        self.response_time_threshold = 5.0  # seconds
        
    def start_monitoring(self):
        """Start background health monitoring"""
        if self.monitoring_task is None or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("🏥 Health monitoring started")
    
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self.monitoring_enabled = False
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            logger.info("🛑 Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_enabled:
            try:
                await self._periodic_health_check()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_health_check(self):
        """Perform periodic health checks"""
        try:
            health = await self.check_gateway_health()
            self._record_health_status(health)
            
            if health["status"] != "healthy":
                logger.warning(f"Gateway health: {health['status']} - {health['message']}")
                
        except Exception as e:
            logger.error(f"Periodic health check failed: {e}")
    
    def _record_health_status(self, health: Dict[str, Any]):
        """Record health status in history"""
        status = HealthStatus(
            status=health["status"],
            message=health.get("message", ""),
            details=health
        )
        
        self.health_history.append(status)
        
        # Trim history if too long
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history:]
    
    async def check_gateway_health(self) -> Dict[str, Any]:
        """Comprehensive gateway health check"""
        health_data = {
            "status": "healthy",
            "message": "All systems operational",
            "timestamp": time.time(),
            "uptime": self.get_uptime(),
            "checks": {}
        }
        
        issues = []
        
        # Memory check
        memory_check = self._check_memory()
        health_data["checks"]["memory"] = memory_check
        if memory_check["status"] != "healthy":
            issues.append(memory_check["message"])
        
        # CPU check
        cpu_check = self._check_cpu()
        health_data["checks"]["cpu"] = cpu_check
        if cpu_check["status"] != "healthy":
            issues.append(cpu_check["message"])
        
        # Disk check
        disk_check = self._check_disk()
        health_data["checks"]["disk"] = disk_check
        if disk_check["status"] != "healthy":
            issues.append(disk_check["message"])
        
        # Network check
        network_check = await self._check_network()
        health_data["checks"]["network"] = network_check
        if network_check["status"] != "healthy":
            issues.append(network_check["message"])
        
        # Overall status
        if issues:
            if len(issues) >= 2:
                health_data["status"] = "unhealthy"
                health_data["message"] = f"Multiple issues: {'; '.join(issues)}"
            else:
                health_data["status"] = "degraded"
                health_data["message"] = issues[0]
        
        return health_data
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            status = "healthy"
            message = f"Memory usage: {usage_percent:.1f}%"
            
            if usage_percent > self.memory_threshold:
                status = "unhealthy" if usage_percent > 90 else "degraded"
                message = f"High memory usage: {usage_percent:.1f}%"
            
            return {
                "status": status,
                "message": message,
                "usage_percent": usage_percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Memory check failed: {e}",
                "error": str(e)
            }
    
    def _check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage"""
        try:
            # Get CPU usage over 1 second interval
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            status = "healthy"
            message = f"CPU usage: {cpu_percent:.1f}%"
            
            if cpu_percent > self.cpu_threshold:
                status = "unhealthy" if cpu_percent > 95 else "degraded"
                message = f"High CPU usage: {cpu_percent:.1f}%"
            
            return {
                "status": status,
                "message": message,
                "usage_percent": cpu_percent,
                "cpu_count": cpu_count,
                "load_average": load_avg
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"CPU check failed: {e}",
                "error": str(e)
            }
    
    def _check_disk(self) -> Dict[str, Any]:
        """Check disk usage"""
        try:
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            
            status = "healthy"
            message = f"Disk usage: {usage_percent:.1f}%"
            
            if usage_percent > 85:
                status = "unhealthy" if usage_percent > 95 else "degraded"
                message = f"High disk usage: {usage_percent:.1f}%"
            
            return {
                "status": status,
                "message": message,
                "usage_percent": round(usage_percent, 1),
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Disk check failed: {e}",
                "error": str(e)
            }
    
    async def _check_network(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            # Test external connectivity
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://httpbin.org/status/200")
                response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            status = "healthy"
            message = f"Network connectivity: {response_time:.0f}ms"
            
            if response.status_code != 200:
                status = "degraded"
                message = f"Network issues detected (status: {response.status_code})"
            elif response_time > 2000:  # 2 seconds
                status = "degraded"
                message = f"Slow network response: {response_time:.0f}ms"
            
            return {
                "status": status,
                "message": message,
                "response_time_ms": round(response_time, 2),
                "external_connectivity": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Network connectivity failed: {e}",
                "external_connectivity": False,
                "error": str(e)
            }
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get gateway uptime information"""
        uptime_seconds = time.time() - self.start_time
        uptime_timedelta = timedelta(seconds=uptime_seconds)
        
        return {
            "seconds": round(uptime_seconds, 1),
            "human_readable": str(uptime_timedelta),
            "started_at": datetime.fromtimestamp(self.start_time).isoformat()
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get detailed memory usage"""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "system": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent
                },
                "process": {
                    "rss_mb": round(process_memory.rss / (1024**2), 2),
                    "vms_mb": round(process_memory.vms / (1024**2), 2)
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_health_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get health history for specified hours"""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_history = [
            {
                "status": h.status,
                "message": h.message,
                "timestamp": h.timestamp,
                "datetime": datetime.fromtimestamp(h.timestamp).isoformat()
            }
            for h in self.health_history
            if h.timestamp > cutoff_time
        ]
        
        return recent_history
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics"""
        if not self.health_history:
            return {"message": "No health data available"}
        
        # Last 24 hours
        last_24h = self.get_health_history(24)
        
        if not last_24h:
            return {"message": "No recent health data"}
        
        # Calculate statistics
        total_checks = len(last_24h)
        healthy_checks = len([h for h in last_24h if h["status"] == "healthy"])
        degraded_checks = len([h for h in last_24h if h["status"] == "degraded"])
        unhealthy_checks = len([h for h in last_24h if h["status"] == "unhealthy"])
        
        return {
            "period": "last_24_hours",
            "total_checks": total_checks,
            "healthy_percentage": round((healthy_checks / total_checks) * 100, 1),
            "degraded_percentage": round((degraded_checks / total_checks) * 100, 1),
            "unhealthy_percentage": round((unhealthy_checks / total_checks) * 100, 1),
            "current_status": last_24h[-1]["status"] if last_24h else "unknown",
            "last_check": last_24h[-1] if last_24h else None
        }
    
    async def check_external_dependencies(self) -> Dict[str, Any]:
        """Check external service dependencies"""
        dependencies = {
            "supabase": "https://supabase.com/health",
            "openai": "https://status.openai.com/api/v2/status.json",
            "twilio": "https://status.twilio.com/api/v2/status.json",
            "elevenlabs": "https://api.elevenlabs.io/v1/user"
        }
        
        results = {}
        
        for service, url in dependencies.items():
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    start_time = time.time()
                    response = await client.get(url)
                    response_time = (time.time() - start_time) * 1000
                    
                    results[service] = {
                        "status": "healthy" if response.status_code < 400 else "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                results[service] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time_ms": None
                }
        
        # Overall dependency health
        healthy_deps = len([r for r in results.values() if r["status"] == "healthy"])
        total_deps = len(results)
        
        overall_status = "healthy"
        if healthy_deps < total_deps:
            overall_status = "degraded" if healthy_deps >= total_deps * 0.7 else "unhealthy"
        
        return {
            "overall_status": overall_status,
            "healthy_count": healthy_deps,
            "total_count": total_deps,
            "dependencies": results
        }
