# apps/smart-campaigns/src/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from api.v1.api import api_router
from core.config import get_settings
from shared.database.client import get_database
from shared.middleware.cors import setup_cors
from shared.middleware.request_logging import RequestLoggingMiddleware
from shared.middleware.error_handling import ErrorHandlingMiddleware
from shared.middleware.metrics import MetricsMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Enhanced Smart Campaigns Service starting up...")
    
    # Initialize database connection
    try:
        db = await get_database()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Initialize any background tasks or connections here
    logger.info("🎯 Enhanced Smart Campaigns Service with AI optimization ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Enhanced Smart Campaigns Service shutting down...")
    # Cleanup tasks here
    logger.info("✅ Enhanced Smart Campaigns Service stopped")

# Create FastAPI app
app = FastAPI(
    title="Vocelio.ai Enhanced Smart Campaigns API",
    description="🎯 Advanced AI-powered campaign management with smart targeting, optimization, and 89+ campaign templates",
    version="2.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "enhanced-campaigns",
            "description": "Enhanced campaign management with AI optimization",
        },
        {
            "name": "campaigns-legacy",
            "description": "Legacy campaign management (backward compatibility)",
        },
        {
            "name": "prospects",
            "description": "Prospect management and targeting",
        },
        {
            "name": "analytics",
            "description": "Campaign analytics and performance metrics",
        },
        {
            "name": "health",
            "description": "Service health and monitoring",
        }
    ]
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {
        "status": "healthy",
        "service": "smart-campaigns-enhanced",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "features": [
            "AI Optimization",
            "A/B Testing",
            "Advanced Analytics", 
            "89+ Campaign Templates",
            "Performance Tracking"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🎯 Vocelio.ai Enhanced Smart Campaigns API",
        "version": "2.0.0",
        "features": [
            "Unified campaign management from 2 services",
            "AI-powered optimization",
            "A/B testing capabilities",
            "89+ pre-built campaign templates",
            "Advanced performance analytics"
        ],
        "docs_url": "/docs",
        "health_url": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )