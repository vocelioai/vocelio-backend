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
    logger.info("🚀 Smart Campaigns Service starting up...")
    
    # Initialize database connection
    try:
        db = await get_database()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Initialize any background tasks or connections here
    logger.info("🎯 Smart Campaigns Service ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Smart Campaigns Service shutting down...")
    # Cleanup tasks here
    logger.info("✅ Smart Campaigns Service stopped")

# Create FastAPI app
app = FastAPI(
    title="Vocelio.ai Smart Campaigns API",
    description="🎯 Advanced AI-powered campaign management with smart targeting and optimization",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "campaigns",
            "description": "Campaign management operations",
        },
        {
            "name": "prospects",
            "description": "Prospect management and targeting",
        },
        {
            "name": "scheduling",
            "description": "Campaign scheduling and automation",
        },
        {
            "name": "automation",
            "description": "AI-powered campaign automation",
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
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(MetricsMiddleware, service_name="smart-campaigns")

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {
        "status": "healthy",
        "service": "smart-campaigns",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🎯 Vocelio.ai Smart Campaigns API",
        "version": "1.0.0",
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