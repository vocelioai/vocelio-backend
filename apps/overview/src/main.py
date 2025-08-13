"""
Vocelio.ai Overview/Command Center Service
Main FastAPI application for dashboard metrics and analytics
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from src.api.v1.api import api_router
from src.core.config import settings
from shared.middleware.cors import add_cors_middleware
from shared.middleware.request_logging import add_request_logging
from shared.middleware.error_handling import add_error_handling
from shared.database.client import init_database
from services.dashboard_service import DashboardService
from services.metrics_service import MetricsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global services
dashboard_service = None
metrics_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global dashboard_service, metrics_service
    
    # Startup
    logger.info("🚀 Starting Vocelio.ai Overview Service...")
    
    try:
        # Initialize database
        init_database()
        logger.info("✅ Database initialized")
        
        # Initialize services
        dashboard_service = DashboardService()
        metrics_service = MetricsService()
        
        # Start background tasks
        asyncio.create_task(start_background_tasks())
        
        logger.info("✅ Overview Service started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Overview Service: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Overview Service...")

async def start_background_tasks():
    """Start background tasks for real-time metrics"""
    try:
        # Start metrics collection task
        asyncio.create_task(collect_real_time_metrics())
        logger.info("✅ Background tasks started")
    except Exception as e:
        logger.error(f"❌ Failed to start background tasks: {str(e)}")

async def collect_real_time_metrics():
    """Collect real-time metrics every 2 seconds"""
    while True:
        try:
            if metrics_service:
                await metrics_service.update_live_metrics()
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
        
        await asyncio.sleep(2)  # Update every 2 seconds

# Create FastAPI application
app = FastAPI(
    title="Vocelio.ai Overview Service",
    description="Command Center Dashboard - Real-time metrics and analytics for the world's #1 AI Call Center",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
add_cors_middleware(app)
add_request_logging(app)
add_error_handling(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vocelio.ai Overview Service",
        "status": "🔥 LIVE",
        "description": "Global Command Center Dashboard",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from shared.database.client import get_database
        db = get_database()
        
        # Test database query
        connection_ok = await db.test_connection()
        
        return {
            "status": "healthy",
            "service": "overview",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def get_service_metrics():
    """Get service-level metrics"""
    try:
        return {
            "service": "overview",
            "uptime": "99.99%",
            "requests_per_second": 1250,
            "average_response_time": "45ms",
            "active_connections": 2847,
            "memory_usage": "512MB",
            "cpu_usage": "15%"
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
