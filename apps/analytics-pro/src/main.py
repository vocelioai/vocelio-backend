"""
Analytics Pro Microservice - Main FastAPI Application
📊 Advanced Analytics & Intelligence Dashboard Backend

This service provides real-time analytics, performance metrics,
and business intelligence for the Vocelio.ai platform.
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from datetime import datetime
import logging

# Internal imports
from src.api.v1.api import api_router
from src.core.config import settings
from src.core.logging_config import setup_logging
from src.services.analytics_service import AnalyticsService
from src.services.real_time_service import RealTimeService
from shared.middleware.cors import cors_middleware
from shared.middleware.rate_limiting import rate_limit_middleware
from shared.middleware.request_logging import request_logging_middleware
from shared.middleware.error_handling import error_handling_middleware
from shared.middleware.metrics import metrics_middleware
from shared.database.client import get_database
from shared.auth.dependencies import get_current_user

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
analytics_service = None
real_time_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Analytics Pro Service...")
    
    global analytics_service, real_time_service
    
    # Initialize database connection
    database = get_database()
    
    # Initialize services
    analytics_service = AnalyticsService(database)
    real_time_service = RealTimeService(database)
    
    # Start background tasks
    asyncio.create_task(real_time_service.start_real_time_updates())
    
    logger.info("✅ Analytics Pro Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Analytics Pro Service...")
    
    if real_time_service:
        await real_time_service.stop_real_time_updates()
    
    logger.info("✅ Analytics Pro Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Analytics Pro Service",
    description="🎯 Advanced Analytics & Business Intelligence Microservice for Vocelio.ai",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add middleware (order matters!)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.ENVIRONMENT == "development" else settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(metrics_middleware)
app.middleware("http")(error_handling_middleware)
app.middleware("http")(request_logging_middleware)
app.middleware("http")(rate_limit_middleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "analytics-pro",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service dependencies"""
    try:
        # Check database connection
        database = get_database()
        db_status = await database.execute_query("SELECT 1")
        
        # Check real-time service
        real_time_status = real_time_service.is_running if real_time_service else False
        
        return {
            "status": "healthy",
            "service": "analytics-pro",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT,
            "dependencies": {
                "database": "healthy" if db_status else "unhealthy",
                "real_time_service": "running" if real_time_status else "stopped"
            },
            "metrics": {
                "active_connections": getattr(real_time_service, 'active_connections', 0),
                "requests_processed": getattr(analytics_service, 'requests_processed', 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Metrics endpoint for monitoring
@app.get("/metrics")
async def get_service_metrics():
    """Prometheus-style metrics endpoint"""
    try:
        metrics = {}
        
        if analytics_service:
            metrics.update(await analytics_service.get_service_metrics())
        
        if real_time_service:
            metrics.update(await real_time_service.get_service_metrics())
        
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

# WebSocket endpoint for real-time updates
@app.websocket("/ws/analytics")
async def websocket_analytics_endpoint(websocket):
    """WebSocket endpoint for real-time analytics updates"""
    if real_time_service:
        await real_time_service.handle_websocket(websocket)
    else:
        await websocket.close(code=1003, reason="Real-time service not available")

# Service information endpoint
@app.get("/info")
async def service_info():
    """Get service information and capabilities"""
    return {
        "service": "analytics-pro",
        "description": "Advanced Analytics & Business Intelligence Service",
        "version": "1.0.0",
        "capabilities": [
            "real-time-analytics",
            "performance-metrics",
            "agent-analytics",
            "campaign-analytics",
            "voice-analytics",
            "ai-insights",
            "custom-reports",
            "data-export",
            "real-time-monitoring"
        ],
        "endpoints": {
            "analytics": "/api/v1/analytics",
            "reports": "/api/v1/reports",
            "dashboards": "/api/v1/dashboards",
            "exports": "/api/v1/exports",
            "real_time": "/ws/analytics"
        },
        "supported_formats": ["json", "csv", "xlsx", "pdf"],
        "real_time": True,
        "rate_limits": {
            "analytics": "1000/hour",
            "reports": "100/hour",
            "exports": "50/hour"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service welcome message"""
    return {
        "message": "🎯 Welcome to Analytics Pro Service",
        "description": "Advanced Analytics & Business Intelligence for Vocelio.ai",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "Contact admin for API documentation",
        "health": "/health",
        "info": "/info"
    }

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested analytics endpoint was not found",
        "available_endpoints": [
            "/api/v1/analytics",
            "/api/v1/reports", 
            "/api/v1/dashboards",
            "/health",
            "/info"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An error occurred processing your analytics request",
        "support": "Contact support@vocelio.ai for assistance"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True
    )
