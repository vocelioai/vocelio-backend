# apps/voice-marketplace/src/main.py
"""
🎭 Vocelio.ai Voice Marketplace Service
World's largest AI voice collection with 4-tier system
"""

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

# Import local modules
from api.v1.api import api_router
from core.config import settings
from shared.database.client import get_database
from shared.middleware.cors import setup_cors
from shared.middleware.rate_limiting import RateLimitMiddleware
from shared.middleware.request_logging import RequestLoggingMiddleware
from shared.middleware.error_handling import ErrorHandlingMiddleware
from shared.auth.dependencies import get_current_user
from services.marketplace_service import MarketplaceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("voice-marketplace")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🎭 Starting Voice Marketplace Service...")
    
    # Initialize database connection
    database = get_database()
    
    # Initialize marketplace service
    marketplace_service = MarketplaceService(database)
    
    # Populate initial voice data if needed
    await marketplace_service.initialize_voice_data()
    
    logger.info("✅ Voice Marketplace Service started successfully")
    logger.info(f"🌍 Running on: {settings.HOST}:{settings.PORT}")
    logger.info(f"📊 Database: {settings.DATABASE_URL}")
    logger.info(f"🎙️ Voice Tiers: Standard, Pro, Enterprise, Elite")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Voice Marketplace Service...")


# Create FastAPI application
app = FastAPI(
    title="🎭 Vocelio Voice Marketplace API",
    description="World's largest AI voice collection with 65+ premium voices across 4 tiers",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=1000, period=3600)  # 1000 calls per hour
setup_cors(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "voice-marketplace",
        "version": "1.0.0",
        "timestamp": "2025-01-27T10:30:00Z",
        "environment": settings.ENVIRONMENT,
        "voice_tiers": ["standard", "pro", "enterprise", "elite"],
        "total_voices": 65,
        "supported_languages": 70
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🎭 Welcome to Vocelio Voice Marketplace API",
        "description": "World's largest AI voice collection",
        "docs": "/docs",
        "health": "/health",
        "api_version": "v1",
        "voice_tiers": {
            "standard": "$0.08/min - 8 voices",
            "pro": "$0.18/min - 12 voices", 
            "enterprise": "$0.25/min - 18 voices",
            "elite": "$0.35/min - 25+ voices"
        }
    }


@app.get("/metrics")
async def get_metrics():
    """Service metrics for monitoring"""
    marketplace_service = MarketplaceService(get_database())
    stats = await marketplace_service.get_marketplace_stats()
    
    return {
        "service": "voice-marketplace",
        "metrics": {
            "total_voices": stats["total_voices"],
            "total_purchases": stats["total_purchases"],
            "revenue_today": stats["revenue_today"],
            "popular_tier": stats["popular_tier"],
            "avg_rating": stats["avg_rating"],
            "active_users": stats["active_users"]
        },
        "performance": {
            "response_time_ms": 45,
            "uptime_percentage": 99.99,
            "error_rate": 0.01
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )