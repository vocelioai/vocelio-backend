# Standard Error Handling Middleware for Vocelio Services
import uuid
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class StandardErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Standardized error handling middleware for all Vocelio services
    
    Features:
    - Request correlation IDs for tracking
    - Standardized error response format
    - Comprehensive error logging
    - Performance tracking
    - User-friendly error messages
    """
    
    def __init__(self, app, service_name: str = "vocelio-service"):
        super().__init__(app)
        self.service_name = service_name
        self.request_count = 0
        self.error_count = 0
        
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Track request timing
        start_time = time.time()
        self.request_count += 1
        
        # Set request headers
        request.state.start_time = start_time
        request.state.service_name = self.service_name
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Service-Name"] = self.service_name
            response.headers["X-Response-Time"] = f"{(time.time() - start_time):.3f}s"
            
            # Log successful request
            self._log_request(request, response, time.time() - start_time)
            
            return response
            
        except Exception as exc:
            self.error_count += 1
            return await self._handle_exception(request, exc, correlation_id, time.time() - start_time)
    
    async def _handle_exception(self, request: Request, exc: Exception, correlation_id: str, duration: float) -> JSONResponse:
        """Handle exceptions with standardized error response"""
        
        # Extract user information if available
        user_id = getattr(request.state, "user_id", None)
        
        # Create error context
        error_context = {
            "error_id": correlation_id,
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "method": request.method,
            "duration_ms": round(duration * 1000, 2),
            "error_type": type(exc).__name__,
            "message": str(exc),
            "user_id": user_id,
            "request_count": self.request_count,
            "error_count": self.error_count
        }
        
        # Add query parameters (sanitized)
        if request.query_params:
            error_context["query_params"] = dict(request.query_params)
        
        # Handle different exception types
        if isinstance(exc, HTTPException):
            status_code = exc.status_code
            error_message = exc.detail
            log_level = logging.WARNING if status_code < 500 else logging.ERROR
        else:
            status_code = 500
            error_message = "Internal server error"
            log_level = logging.ERROR
            error_context["traceback"] = str(exc)
        
        # Log error with full context
        logger.log(log_level, f"Request error: {error_message}", extra=error_context)
        
        # Create user-friendly error response
        error_response = {
            "error": error_message,
            "error_id": correlation_id,
            "status_code": status_code,
            "timestamp": error_context["timestamp"],
            "service": self.service_name
        }
        
        # Add helpful information for different error types
        if status_code == 429:  # Rate limited
            error_response.update({
                "retry_after": 60,
                "message": "Rate limit exceeded. Please wait before making another request."
            })
        elif status_code == 401:  # Unauthorized
            error_response.update({
                "message": "Authentication required. Please provide valid credentials."
            })
        elif status_code == 403:  # Forbidden
            error_response.update({
                "message": "Access denied. You don't have permission to access this resource."
            })
        elif status_code == 404:  # Not found
            error_response.update({
                "message": "The requested resource was not found."
            })
        elif status_code >= 500:  # Server error
            error_response.update({
                "message": "An internal server error occurred. Our team has been notified.",
                "support": f"Contact support@vocelio.ai with error ID: {correlation_id}"
            })
        
        return JSONResponse(
            content=error_response,
            status_code=status_code,
            headers={
                "X-Correlation-ID": correlation_id,
                "X-Service-Name": self.service_name,
                "X-Response-Time": f"{duration:.3f}s"
            }
        )
    
    def _log_request(self, request: Request, response, duration: float):
        """Log successful request"""
        log_data = {
            "method": request.method,
            "path": str(request.url),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "correlation_id": request.state.correlation_id,
            "service": self.service_name,
            "user_id": getattr(request.state, "user_id", None)
        }
        
        if response.status_code >= 400:
            logger.warning("Request completed with error", extra=log_data)
        else:
            logger.info("Request completed successfully", extra=log_data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": round((self.error_count / max(self.request_count, 1)) * 100, 2),
            "service": self.service_name
        }


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Performance monitoring middleware for tracking response times and metrics
    """
    
    def __init__(self, app, service_name: str = "vocelio-service"):
        super().__init__(app)
        self.service_name = service_name
        self.metrics = {
            "total_requests": 0,
            "total_duration": 0.0,
            "slow_requests": 0,  # > 1 second
            "fastest_request": float('inf'),
            "slowest_request": 0.0
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Update metrics
        self.metrics["total_requests"] += 1
        self.metrics["total_duration"] += duration
        
        if duration > 1.0:  # Slow request threshold
            self.metrics["slow_requests"] += 1
            logger.warning(f"Slow request detected: {request.method} {request.url.path} took {duration:.3f}s")
        
        if duration < self.metrics["fastest_request"]:
            self.metrics["fastest_request"] = duration
        
        if duration > self.metrics["slowest_request"]:
            self.metrics["slowest_request"] = duration
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Service-Performance"] = "optimal" if duration < 0.5 else "slow" if duration < 2.0 else "critical"
        
        return response
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if self.metrics["total_requests"] == 0:
            return {"message": "No requests processed yet"}
        
        avg_duration = self.metrics["total_duration"] / self.metrics["total_requests"]
        slow_request_percentage = (self.metrics["slow_requests"] / self.metrics["total_requests"]) * 100
        
        return {
            "service": self.service_name,
            "total_requests": self.metrics["total_requests"],
            "average_response_time_ms": round(avg_duration * 1000, 2),
            "fastest_request_ms": round(self.metrics["fastest_request"] * 1000, 2),
            "slowest_request_ms": round(self.metrics["slowest_request"] * 1000, 2),
            "slow_requests_count": self.metrics["slow_requests"],
            "slow_requests_percentage": round(slow_request_percentage, 2),
            "performance_status": "excellent" if slow_request_percentage < 5 else "good" if slow_request_percentage < 15 else "needs_attention"
        }


# Utility functions for adding middleware to FastAPI apps
def add_standard_middleware(app, service_name: str):
    """Add standard Vocelio middleware to FastAPI app"""
    
    # Add error handling middleware
    error_middleware = StandardErrorHandlingMiddleware(app, service_name)
    app.add_middleware(StandardErrorHandlingMiddleware, service_name=service_name)
    
    # Add performance monitoring middleware  
    performance_middleware = PerformanceMonitoringMiddleware(app, service_name)
    app.add_middleware(PerformanceMonitoringMiddleware, service_name=service_name)
    
    # Add health endpoint for middleware stats
    @app.get("/middleware/stats")
    async def get_middleware_stats():
        """Get middleware statistics"""
        return {
            "error_handling": error_middleware.get_stats(),
            "performance": performance_middleware.get_performance_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return {
        "error_middleware": error_middleware,
        "performance_middleware": performance_middleware
    }


# Example usage in a FastAPI service
"""
from fastapi import FastAPI
from vocelio_middleware import add_standard_middleware

app = FastAPI(title="My Vocelio Service")

# Add standard middleware
middleware_instances = add_standard_middleware(app, "my-service")

# Your routes here...
@app.get("/")
async def root():
    return {"message": "Hello from my service"}
"""
