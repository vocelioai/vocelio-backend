# apps/api-gateway/src/utils/load_balancer.py
import asyncio
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
import math

from ..config import settings

logger = logging.getLogger(__name__)

class LoadBalancingStrategy:
    """Base class for load balancing strategies"""
    
    def __init__(self, services: Dict[str, str]):
        self.services = services
        self.metrics = defaultdict(lambda: {
            "requests": 0,
            "response_times": deque(maxlen=100),  # Last 100 response times
            "errors": 0,
            "last_request": None,
            "connections": 0,
            "weight": 1.0
        })
    
    async def select_service_url(self, service_name: str, healthy_instances: List[str]) -> Optional[str]:
        """Select the best service URL based on strategy"""
        raise NotImplementedError
    
    def record_request(self, service_name: str, response_time: float, success: bool):
        """Record request metrics for load balancing decisions"""
        metrics = self.metrics[service_name]
        metrics["requests"] += 1
        metrics["response_times"].append(response_time)
        metrics["last_request"] = datetime.utcnow()
        
        if not success:
            metrics["errors"] += 1
        
        # Update connection count (simulated)
        metrics["connections"] = max(0, metrics["connections"] + (1 if success else -1))
    
    def get_average_response_time(self, service_name: str) -> float:
        """Get average response time for service"""
        response_times = self.metrics[service_name]["response_times"]
        if not response_times:
            return 0.0
        return sum(response_times) / len(response_times)
    
    def get_error_rate(self, service_name: str) -> float:
        """Get error rate for service"""
        metrics = self.metrics[service_name]
        if metrics["requests"] == 0:
            return 0.0
        return (metrics["errors"] / metrics["requests"]) * 100

class RoundRobinStrategy(LoadBalancingStrategy):
    """Round-robin load balancing strategy"""
    
    def __init__(self, services: Dict[str, str]):
        super().__init__(services)
        self.counters = defaultdict(int)
    
    async def select_service_url(self, service_name: str, healthy_instances: List[str]) -> Optional[str]:
        if not healthy_instances:
            return None
        
        # For single service, return the URL
        if len(healthy_instances) == 1:
            return self.services[service_name]
        
        # For multiple instances (future clustering support)
        counter = self.counters[service_name]
        selected_instance = healthy_instances[counter % len(healthy_instances)]
        self.counters[service_name] = (counter + 1) % len(healthy_instances)
        
        return self.services[service_name]  # For now, return main URL

class LeastConnectionsStrategy(LoadBalancingStrategy):
    """Least connections load balancing strategy"""
    
    async def select_service_url(self, service_name: str, healthy_instances: List[str]) -> Optional[str]:
        if not healthy_instances:
            return None
        
        # For single service, return the URL
        if len(healthy_instances) == 1:
            return self.services[service_name]
        
        # Find service with least connections
        min_connections = float('inf')
        best_instance = None
        
        for instance in healthy_instances:
            connections = self.metrics[instance]["connections"]
            if connections < min_connections:
                min_connections = connections
                best_instance = instance
        
        return self.services[service_name]  # For now, return main URL

class WeightedResponseTimeStrategy(LoadBalancingStrategy):
    """Weighted response time load balancing strategy"""
    
    async def select_service_url(self, service_name: str, healthy_instances: List[str]) -> Optional[str]:
        if not healthy_instances:
            return None
        
        # For single service, return the URL
        if len(healthy_instances) == 1:
            return self.services[service_name]
        
        # Calculate weights based on response times (inverse relationship)
        weights = []
        for instance in healthy_instances:
            avg_response_time = self.get_average_response_time(instance)
            error_rate = self.get_error_rate(instance)
            
            # Lower response time and error rate = higher weight
            if avg_response_time == 0:
                weight = 1.0
            else:
                weight = 1.0 / (avg_response_time * (1 + error_rate / 100))
            
            weights.append(weight)
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return self.services[service_name]
        
        # For now, just return main URL (future enhancement for multiple instances)
        return self.services[service_name]

class LoadBalancer:
    """Advanced load balancer with multiple strategies and health awareness"""
    
    def __init__(self, services: Dict[str, str]):
        self.services = services
        self.service_discovery = None  # Will be set externally
        
        # Initialize strategy based on configuration
        strategy_name = settings.LOAD_BALANCER_STRATEGY.lower()
        if strategy_name == "round_robin":
            self.strategy = RoundRobinStrategy(services)
        elif strategy_name == "least_connections":
            self.strategy = LeastConnectionsStrategy(services)
        elif strategy_name == "weighted":
            self.strategy = WeightedResponseTimeStrategy(services)
        else:
            logger.warning(f"Unknown load balancing strategy: {strategy_name}, using round_robin")
            self.strategy = RoundRobinStrategy(services)
        
        # Circuit breaker states
        self.circuit_breakers = {}
        for service_name in services.keys():
            self.circuit_breakers[service_name] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure": None,
                "success_count": 0
            }
        
        # Performance metrics
        self.global_metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "start_time": datetime.utcnow(),
            "request_distribution": defaultdict(int)
        }
        
        logger.info(f"🎯 Load Balancer initialized with {strategy_name} strategy")
    
    async def get_service_url(self, service_name: str) -> str:
        """Get optimal service URL using load balancing strategy"""
        if service_name not in self.services:
            raise ValueError(f"Unknown service: {service_name}")
        
        # Check circuit breaker
        if not self._is_circuit_breaker_closed(service_name):
            logger.warning(f"🔴 Circuit breaker open for {service_name}")
            # For now, still return URL but log the issue
            # In production, you might want to throw an exception or use fallback
        
        # Get healthy instances (for now, just the main service)
        healthy_instances = [service_name]
        
        # If we had service discovery integration
        if hasattr(self, 'service_discovery') and self.service_discovery:
            is_healthy = await self.service_discovery.is_service_healthy(service_name)
            if not is_healthy:
                healthy_instances = []
        
        # Use strategy to select URL
        selected_url = await self.strategy.select_service_url(service_name, healthy_instances)
        
        if selected_url is None:
            logger.error(f"❌ No healthy instances available for {service_name}")
            # Return original URL as fallback
            selected_url = self.services[service_name]
        
        # Record request distribution
        self.global_metrics["request_distribution"][service_name] += 1
        self.global_metrics["total_requests"] += 1
        
        return selected_url
    
    def record_request_result(self, service_name: str, response_time: float, 
                            status_code: int, success: bool):
        """Record request result for load balancing optimization"""
        
        # Update strategy metrics
        self.strategy.record_request(service_name, response_time, success)
        
        # Update circuit breaker
        if success and 200 <= status_code < 400:
            self._record_success(service_name)
        else:
            self._record_failure(service_name)
            self.global_metrics["total_errors"] += 1
        
        logger.debug(f"📊 Recorded {service_name}: {response_time:.3f}s, status={status_code}, success={success}")
    
    def _is_circuit_breaker_closed(self, service_name: str) -> bool:
        """Check if circuit breaker allows requests"""
        if not settings.CIRCUIT_BREAKER_ENABLED:
            return True
        
        cb = self.circuit_breakers.get(service_name, {})
        state = cb.get("state", "closed")
        
        if state == "closed":
            return True
        elif state == "open":
            # Check if we should try half-open
            last_failure = cb.get("last_failure")
            if last_failure:
                time_since_failure = (datetime.utcnow() - last_failure).total_seconds()
                if time_since_failure >= settings.CIRCUIT_BREAKER_TIMEOUT:
                    cb["state"] = "half_open"
                    cb["success_count"] = 0
                    logger.info(f"🟡 Circuit breaker half-open for {service_name}")
                    return True
            return False
        elif state == "half_open":
            return True
        
        return False
    
    def _record_success(self, service_name: str):
        """Record successful request for circuit breaker"""
        if not settings.CIRCUIT_BREAKER_ENABLED:
            return
        
        cb = self.circuit_breakers.get(service_name, {})
        
        if cb.get("state") == "half_open":
            cb["success_count"] = cb.get("success_count", 0) + 1
            if cb["success_count"] >= 3:  # 3 successful requests to close
                cb["state"] = "closed"
                cb["failure_count"] = 0
                cb["success_count"] = 0
                logger.info(f"🟢 Circuit breaker closed for {service_name}")
        elif cb.get("state") == "closed":
            cb["failure_count"] = 0  # Reset failure count on success
    
    def _record_failure(self, service_name: str):
        """Record failed request for circuit breaker"""
        if not settings.CIRCUIT_BREAKER_ENABLED:
            return
        
        cb = self.circuit_breakers.get(service_name, {})
        cb["failure_count"] = cb.get("failure_count", 0) + 1
        cb["last_failure"] = datetime.utcnow()
        
        current_state = cb.get("state", "closed")
        
        if current_state == "closed" and cb["failure_count"] >= settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD:
            cb["state"] = "open"
            logger.warning(f"🔴 Circuit breaker opened for {service_name} after {cb['failure_count']} failures")
        elif current_state == "half_open":
            cb["state"] = "open"
            cb["success_count"] = 0
            logger.warning(f"🔴 Circuit breaker re-opened for {service_name}")
    
    async def get_load_balancing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive load balancing metrics"""
        uptime = (datetime.utcnow() - self.global_metrics["start_time"]).total_seconds()
        total_requests = self.global_metrics["total_requests"]
        total_errors = self.global_metrics["total_errors"]
        
        # Calculate error rate
        error_rate = (total_errors / max(total_requests, 1)) * 100
        
        # Get service-specific metrics
        service_metrics = {}
        for service_name in self.services.keys():
            strategy_metrics = self.strategy.metrics[service_name]
            circuit_breaker = self.circuit_breakers.get(service_name, {})
            
            service_metrics[service_name] = {
                "requests": strategy_metrics["requests"],
                "avg_response_time": self.strategy.get_average_response_time(service_name),
                "error_rate": self.strategy.get_error_rate(service_name),
                "connections": strategy_metrics["connections"],
                "circuit_breaker_state": circuit_breaker.get("state", "closed"),
                "failure_count": circuit_breaker.get("failure_count", 0),
                "last_request": strategy_metrics["last_request"].isoformat() if strategy_metrics["last_request"] else None
            }
        
        return {
            "strategy": settings.LOAD_BALANCER_STRATEGY,
            "uptime_seconds": round(uptime, 1),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 2),
            "requests_per_second": round(total_requests / max(uptime, 1), 2),
            "request_distribution": dict(self.global_metrics["request_distribution"]),
            "services": service_metrics,
            "circuit_breakers_enabled": settings.CIRCUIT_BREAKER_ENABLED,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def update_metrics(self):
        """Background task to update load balancing metrics"""
        logger.info("📊 Starting load balancing metrics updater")
        
        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Clean old metrics
                await self._cleanup_old_metrics()
                
                # Log load balancing summary
                metrics = await self.get_load_balancing_metrics()
                total_requests = metrics["total_requests"]
                error_rate = metrics["error_rate"]
                rps = metrics["requests_per_second"]
                
                logger.info(f"📊 Load Balancer: {total_requests} total requests, {error_rate:.1f}% error rate, {rps:.1f} RPS")
                
            except Exception as e:
                logger.error(f"❌ Error updating load balancing metrics: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory growth"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=1)  # Keep last hour of data
        
        for service_name, metrics in self.strategy.metrics.items():
            # Clean old response times (already limited by deque maxlen)
            pass
        
        # Reset circuit breaker failure counts if they're old
        for service_name, cb in self.circuit_breakers.items():
            last_failure = cb.get("last_failure")
            if last_failure and (current_time - last_failure).total_seconds() > 3600:  # 1 hour
                if cb.get("failure_count", 0) > 0:
                    cb["failure_count"] = max(0, cb["failure_count"] - 1)
    
    def get_service_weight(self, service_name: str) -> float:
        """Get current weight for service (for weighted strategies)"""
        if hasattr(self.strategy, 'metrics'):
            return self.strategy.metrics[service_name].get("weight", 1.0)
        return 1.0
    
    def set_service_weight(self, service_name: str, weight: float):
        """Set weight for service (for weighted strategies)"""
        if hasattr(self.strategy, 'metrics') and service_name in self.strategy.metrics:
            self.strategy.metrics[service_name]["weight"] = max(0.1, min(10.0, weight))
            logger.info(f"⚖️ Set weight for {service_name}: {weight}")
    
    async def get_optimal_service_for_request(self, service_name: str, request_info: Dict[str, Any]) -> str:
        """Get optimal service URL considering request characteristics"""
        # Basic implementation - can be enhanced based on request type, size, etc.
        return await self.get_service_url(service_name)
    
    def force_circuit_breaker_open(self, service_name: str):
        """Manually open circuit breaker for service"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name]["state"] = "open"
            self.circuit_breakers[service_name]["last_failure"] = datetime.utcnow()
            logger.warning(f"🔴 Manually opened circuit breaker for {service_name}")
    
    def force_circuit_breaker_close(self, service_name: str):
        """Manually close circuit breaker for service"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name]["state"] = "closed"
            self.circuit_breakers[service_name]["failure_count"] = 0
            self.circuit_breakers[service_name]["success_count"] = 0
            logger.info(f"🟢 Manually closed circuit breaker for {service_name}")
    
    def get_health_score(self, service_name: str) -> float:
        """Calculate health score for service (0.0 to 1.0)"""
        if service_name not in self.strategy.metrics:
            return 0.5  # Unknown service
        
        metrics = self.strategy.metrics[service_name]
        
        # Factors affecting health score
        factors = {}
        
        # Response time factor (lower is better)
        avg_response_time = self.strategy.get_average_response_time(service_name)
        if avg_response_time == 0:
            factors["response_time"] = 1.0
        else:
            # Normalize response time (assume 1s is baseline, 5s is poor)
            factors["response_time"] = max(0.0, min(1.0, 1.0 - (avg_response_time - 1.0) / 4.0))
        
        # Error rate factor (lower is better)
        error_rate = self.strategy.get_error_rate(service_name)
        factors["error_rate"] = max(0.0, min(1.0, 1.0 - error_rate / 100.0))
        
        # Circuit breaker factor
        cb_state = self.circuit_breakers.get(service_name, {}).get("state", "closed")
        if cb_state == "closed":
            factors["circuit_breaker"] = 1.0
        elif cb_state == "half_open":
            factors["circuit_breaker"] = 0.5
        else:  # open
            factors["circuit_breaker"] = 0.0
        
        # Request volume factor (more requests = more confidence in metrics)
        request_count = metrics["requests"]
        if request_count < 10:
            factors["confidence"] = 0.5  # Low confidence with few requests
        elif request_count < 100:
            factors["confidence"] = 0.8  # Medium confidence
        else:
            factors["confidence"] = 1.0  # High confidence
        
        # Calculate weighted average
        weights = {
            "response_time": 0.3,
            "error_rate": 0.4,
            "circuit_breaker": 0.2,
            "confidence": 0.1
        }
        
        health_score = sum(factors[factor] * weight for factor, weight in weights.items())
        return round(health_score, 3)
    
    async def get_service_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for service optimization"""
        recommendations = []
        service_analysis = {}
        
        for service_name in self.services.keys():
            health_score = self.get_health_score(service_name)
            avg_response_time = self.strategy.get_average_response_time(service_name)
            error_rate = self.strategy.get_error_rate(service_name)
            request_count = self.strategy.metrics[service_name]["requests"]
            
            service_analysis[service_name] = {
                "health_score": health_score,
                "avg_response_time": avg_response_time,
                "error_rate": error_rate,
                "request_count": request_count
            }
            
            # Generate recommendations
            if health_score < 0.3:
                recommendations.append({
                    "service": service_name,
                    "priority": "high",
                    "issue": "Poor overall health",
                    "recommendation": "Investigate service issues immediately"
                })
            elif error_rate > 10:
                recommendations.append({
                    "service": service_name,
                    "priority": "medium",
                    "issue": f"High error rate: {error_rate:.1f}%",
                    "recommendation": "Review service logs and error handling"
                })
            elif avg_response_time > 5.0:
                recommendations.append({
                    "service": service_name,
                    "priority": "medium",
                    "issue": f"Slow response time: {avg_response_time:.2f}s",
                    "recommendation": "Optimize service performance or consider scaling"
                })
            elif request_count > 0 and health_score > 0.8:
                recommendations.append({
                    "service": service_name,
                    "priority": "low",
                    "issue": "Excellent performance",
                    "recommendation": "Service is performing well - consider as template for others"
                })
        
        return {
            "recommendations": recommendations,
            "service_analysis": service_analysis,
            "overall_health": round(sum(s["health_score"] for s in service_analysis.values()) / len(service_analysis), 3),
            "timestamp": datetime.utcnow().isoformat()
        }

# Utility functions for load balancing
def calculate_weighted_random_selection(weights: List[float]) -> int:
    """Select index based on weighted random selection"""
    if not weights or sum(weights) == 0:
        return 0
    
    total_weight = sum(weights)
    random_value = random.uniform(0, total_weight)
    
    cumulative_weight = 0
    for i, weight in enumerate(weights):
        cumulative_weight += weight
        if random_value <= cumulative_weight:
            return i
    
    return len(weights) - 1  # Fallback to last index

def normalize_response_time_to_weight(response_time: float, min_time: float = 0.1, max_time: float = 10.0) -> float:
    """Convert response time to weight (inverse relationship)"""
    if response_time <= 0:
        return 1.0
    
    # Clamp response time to reasonable bounds
    clamped_time = max(min_time, min(response_time, max_time))
    
    # Inverse relationship: faster response = higher weight
    weight = max_time / clamped_time
    
    # Normalize to 0.1 - 1.0 range
    return max(0.1, min(1.0, weight / 10.0))

# Export for use in main application
__all__ = [
    "LoadBalancer",
    "LoadBalancingStrategy", 
    "RoundRobinStrategy",
    "LeastConnectionsStrategy", 
    "WeightedResponseTimeStrategy",
    "calculate_weighted_random_selection",
    "normalize_response_time_to_weight"
]