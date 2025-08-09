"""
Advanced Rate Limiting Middleware for Vocelio API Gateway
Implements sliding window rate limiting with Redis backend and memory fallback
"""

import time
import json
import asyncio
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging
import hashlib
from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Rate limit information"""
    limit: int
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None


class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies and Redis backend"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, deque] = defaultdict(deque)
        self.connection_ready = False
        
        # Rate limit configurations by endpoint type
        self.rate_limits = {
            "default": {"requests": 1000, "window": 3600},  # 1000/hour
            "auth": {"requests": 100, "window": 3600},       # 100/hour for auth endpoints
            "api_key": {"requests": 5000, "window": 3600},   # 5000/hour for API key users
            "premium": {"requests": 10000, "window": 3600},  # 10000/hour for premium users
            "webhook": {"requests": 10000, "window": 3600},  # 10000/hour for webhooks
            "health": {"requests": 1000, "window": 60},      # 1000/minute for health checks
            "upload": {"requests": 50, "window": 3600},      # 50/hour for file uploads
            "ai": {"requests": 500, "window": 3600},         # 500/hour for AI endpoints
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not settings.REDIS_URL:
            logger.warning("⚠️ No Redis URL configured, using memory-based rate limiting")
            return
        
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            await self.redis_client.ping()
            self.connection_ready = True
            logger.info("✅ Redis connected for advanced rate limiting")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed, using memory store: {e}")
            self.redis_client = None
            self.connection_ready = False
    
    def _get_rate_limit_config(self, request: Request) -> Dict[str, int]:
        """Get rate limit configuration based on request context"""
        path = request.url.path
        
        # Determine rate limit type based on path
        if path.startswith("/auth/"):
            return self.rate_limits["auth"]
        elif path.startswith("/health"):
            return self.rate_limits["health"]
        elif path.startswith("/webhooks/"):
            return self.rate_limits["webhook"]
        elif path.startswith("/upload/") or "upload" in path:
            return self.rate_limits["upload"]
        elif any(ai_path in path for ai_path in ["/ai/", "/agents/", "/smart-campaigns/"]):
            return self.rate_limits["ai"]
        
        # Check user type
        user_type = getattr(request.state, "user_type", "default")
        if user_type == "api_key":
            return self.rate_limits["api_key"]
        elif user_type == "premium":
            return self.rate_limits["premium"]
        
        return self.rate_limits["default"]
    
    def _generate_rate_limit_key(self, request: Request) -> str:
        """Generate unique rate limiting key"""
        # Try to get user/org identification
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)
        api_key = request.headers.get("x-api-key")
        
        # Create hierarchical key
        if user_id:
            base_key = f"user:{user_id}"
        elif org_id:
            base_key = f"org:{org_id}"
        elif api_key:
            # Hash API key for privacy
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            base_key = f"api:{key_hash}"
        else:
            # Fall back to IP address
            client_ip = request.client.host
            base_key = f"ip:{client_ip}"
        
        # Add endpoint specificity
        endpoint_type = self._get_endpoint_type(request)
        return f"rate_limit:{base_key}:{endpoint_type}"
    
    def _get_endpoint_type(self, request: Request) -> str:
        """Get endpoint type for granular rate limiting"""
        path = request.url.path
        
        if path.startswith("/auth/"):
            return "auth"
        elif path.startswith("/health"):
            return "health"
        elif path.startswith("/webhooks/"):
            return "webhook"
        elif any(ai_path in path for ai_path in ["/ai/", "/agents/", "/smart-campaigns/"]):
            return "ai"
        elif "upload" in path:
            return "upload"
        else:
            return "general"
    
    async def check_rate_limit(self, request: Request) -> Tuple[bool, RateLimitInfo]:
        """Check if request is within rate limits"""
        config = self._get_rate_limit_config(request)
        key = self._generate_rate_limit_key(request)
        limit = config["requests"]
        window = config["window"]
        
        current_time = time.time()
        
        if self.redis_client and self.connection_ready:
            return await self._redis_rate_limit(key, limit, window, current_time)
        else:
            return await self._memory_rate_limit(key, limit, window, current_time)
    
    async def _redis_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        current_time: float
    ) -> Tuple[bool, RateLimitInfo]:
        """Redis-based sliding window rate limiting"""
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            cutoff_time = current_time - window
            pipe.zremrangebyscore(key, 0, cutoff_time)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Get the oldest entry to calculate reset time
            pipe.zrange(key, 0, 0, withscores=True)
            
            results = await pipe.execute()
            current_count = results[1]
            oldest_entries = results[2]
            
            # Calculate reset time
            if oldest_entries:
                oldest_time = oldest_entries[0][1]
                reset_time = int(oldest_time + window)
            else:
                reset_time = int(current_time + window)
            
            # Check if limit exceeded
            if current_count >= limit:
                return False, RateLimitInfo(
                    limit=limit,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=int(reset_time - current_time)
                )
            
            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, window + 10)  # Add buffer for cleanup
            
            return True, RateLimitInfo(
                limit=limit,
                remaining=limit - current_count - 1,
                reset_time=reset_time
            )
            
        except Exception as e:
            logger.error(f"Redis rate limiting error for key {key}: {e}")
            # Graceful degradation - allow request but log error
            return True, RateLimitInfo(
                limit=limit,
                remaining=limit - 1,
                reset_time=int(current_time + window)
            )
    
    async def _memory_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        current_time: float
    ) -> Tuple[bool, RateLimitInfo]:
        """Memory-based rate limiting (fallback)"""
        # Clean expired entries
        cutoff_time = current_time - window
        requests = self.memory_store[key]
        
        # Remove old requests
        while requests and requests[0] <= cutoff_time:
            requests.popleft()
        
        current_count = len(requests)
        
        # Calculate reset time
        if requests:
            reset_time = int(requests[0] + window)
        else:
            reset_time = int(current_time + window)
        
        # Check if limit exceeded
        if current_count >= limit:
            return False, RateLimitInfo(
                limit=limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=int(reset_time - current_time)
            )
        
        # Add current request
        requests.append(current_time)
        
        return True, RateLimitInfo(
            limit=limit,
            remaining=limit - current_count - 1,
            reset_time=reset_time
        )
    
    async def record_request(self, request: Request, response_status: int):
        """Record request for analytics and adaptive rate limiting"""
        if not self.redis_client or not self.connection_ready:
            return
        
        try:
            # Record request metrics
            metrics_key = f"metrics:{self._generate_rate_limit_key(request)}"
            current_time = int(time.time())
            
            # Store request data
            request_data = {
                "timestamp": current_time,
                "status": response_status,
                "endpoint": request.url.path,
                "method": request.method
            }
            
            # Use Redis hash to store recent requests (last 24 hours)
            await self.redis_client.hset(
                metrics_key,
                current_time,
                json.dumps(request_data)
            )
            
            # Expire old metrics
            await self.redis_client.expire(metrics_key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")


# Global rate limiter instance
advanced_rate_limiter = AdvancedRateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Advanced rate limiting middleware with detailed analytics (public name expected by main)."""
    
    # Skip rate limiting for specific paths
    skip_paths = ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)
    
    # Initialize rate limiter if needed
    if not advanced_rate_limiter.connection_ready and settings.REDIS_URL:
        await advanced_rate_limiter.initialize()
    
    start_time = time.time()
    
    try:
        # Check rate limits
        allowed, rate_info = await advanced_rate_limiter.check_rate_limit(request)
        
        if not allowed:
            # Log rate limit violation
            key = advanced_rate_limiter._generate_rate_limit_key(request)
            logger.warning(
                f"🚫 Rate limit exceeded",
                extra={
                    "key": key,
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host,
                    "limit": rate_info.limit,
                    "retry_after": rate_info.retry_after
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {rate_info.limit} requests per hour",
                    "retry_after": rate_info.retry_after,
                    "reset_time": rate_info.reset_time,
                    "documentation": "https://docs.vocelio.ai/rate-limits"
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info.limit),
                    "X-RateLimit-Remaining": str(rate_info.remaining),
                    "X-RateLimit-Reset": str(rate_info.reset_time),
                    "Retry-After": str(rate_info.retry_after or 3600),
                    "X-RateLimit-Policy": "sliding-window"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        response.headers.update({
            "X-RateLimit-Limit": str(rate_info.limit),
            "X-RateLimit-Remaining": str(rate_info.remaining),
            "X-RateLimit-Reset": str(rate_info.reset_time),
            "X-RateLimit-Policy": "sliding-window"
        })
        
        # Record request for analytics
        await advanced_rate_limiter.record_request(request, response.status_code)
        
        return response
        
    except Exception as e:
        logger.error(f"Rate limiting middleware error: {e}")
        # Allow request to proceed if rate limiting fails
        response = await call_next(request)
        
        # Add basic headers even if rate limiting failed
        response.headers.update({
            "X-RateLimit-Limit": "1000",
            "X-RateLimit-Remaining": "999",
            "X-RateLimit-Reset": str(int(time.time() + 3600))
        })
        
        return response


async def cleanup_rate_limit_data():
    """Periodic cleanup of rate limit data"""
    if not advanced_rate_limiter.redis_client or not advanced_rate_limiter.connection_ready:
        return
    
    try:
        # Clean up old rate limit keys
        keys = await advanced_rate_limiter.redis_client.keys("rate_limit:*")
        current_time = time.time()
        
        for key in keys:
            # Remove entries older than 2 hours
            await advanced_rate_limiter.redis_client.zremrangebyscore(
                key, 0, current_time - 7200
            )
        
        logger.info(f"🧹 Cleaned up rate limit data for {len(keys)} keys")
        
    except Exception as e:
        logger.error(f"Error cleaning up rate limit data: {e}")


# Schedule periodic cleanup (in production, use a proper scheduler like Celery)
async def start_rate_limit_cleanup():
    """Start periodic cleanup task"""
    while True:
        await asyncio.sleep(3600)  # Run every hour
        await cleanup_rate_limit_data()
