# apps/data-warehouse/src/main.py
"""
🏛️ Vocelio.ai Data Warehouse Service
Enterprise data lake, ETL pipelines, and advanced analytics platform
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncio
import uuid

from api.v1.api import api_router
from core.config import get_settings
from services.etl_service import ETLService
from services.analytics_service import AnalyticsService
from services.data_lake_service import DataLakeService
from services.reporting_service import ReportingService
from shared.middleware.cors import setup_cors
from shared.middleware.rate_limiting import RateLimitMiddleware
from shared.middleware.request_logging import RequestLoggingMiddleware
from shared.middleware.error_handling import ErrorHandlingMiddleware
from shared.database.client import init_db

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
etl_service = None
analytics_service = None
data_lake_service = None
reporting_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global etl_service, analytics_service, data_lake_service, reporting_service
    
    try:
        # Initialize database
        await init_db()
        
        # Initialize services
        etl_service = ETLService()
        analytics_service = AnalyticsService()
        data_lake_service = DataLakeService()
        reporting_service = ReportingService()
        
        # Start background ETL processes
        asyncio.create_task(etl_service.start_continuous_processing())
        
        logger.info("Data Warehouse Service initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize Data Warehouse Service: {e}")
        raise
    finally:
        # Cleanup
        if etl_service:
            await etl_service.stop_processing()
        logger.info("Data Warehouse Service shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="🏛️ Vocelio.ai Data Warehouse Service",
    description="Enterprise data lake, ETL pipelines, and advanced analytics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "data-warehouse",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "data_sources": await data_lake_service.get_connected_sources() if data_lake_service else [],
        "active_pipelines": await etl_service.get_active_pipelines() if etl_service else 0
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "🏛️ Vocelio.ai Data Warehouse Service",
        "version": "1.0.0",
        "description": "Enterprise data lake, ETL pipelines, and advanced analytics platform",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Data Lake Management",
            "ETL Pipeline Processing",
            "Advanced Analytics",
            "Custom Reporting",
            "Real-time Data Streaming",
            "Data Quality Monitoring"
        ]
    }

# Dependency injection
async def get_etl_service() -> ETLService:
    """Get ETL service instance"""
    return etl_service

async def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance"""
    return analytics_service

async def get_data_lake_service() -> DataLakeService:
    """Get data lake service instance"""
    return data_lake_service

async def get_reporting_service() -> ReportingService:
    """Get reporting service instance"""
    return reporting_service

# Include API routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(settings.PORT or 8000),
        reload=settings.ENVIRONMENT == "development"
    )
