# apps/team-hub/src/main.py

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List, Optional

from api.v1.api import api_router
from core.config import settings
from shared.database.client import get_database
from shared.middleware.cors import setup_cors
from shared.middleware.request_logging import RequestLoggingMiddleware
from shared.middleware.error_handling import ErrorHandlingMiddleware
from shared.auth.middleware import AuthMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Team Hub Service starting up...")
    
    # Initialize database connection
    try:
        db = await get_database()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Initialize background tasks
    logger.info("✅ Background tasks initialized")
    
    yield
    
    # Cleanup
    logger.info("🔄 Team Hub Service shutting down...")
    logger.info("✅ Team Hub Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Vocelio.ai Team Hub Service",
    description="👥 Enterprise Team Management & Performance Center",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Add custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Setup CORS
setup_cors(app)

# Include API routes
app.add_api_route("/", lambda: {"service": "team-hub", "status": "healthy", "version": "1.0.0"})
app.add_api_route("/health", lambda: {
    "service": "team-hub",
    "status": "healthy",
    "version": "1.0.0",
    "description": "👥 Enterprise Team Management & Performance Center"
})

app.include_router(api_router, prefix="/api/v1")

@app.get("/metrics")
async def get_service_metrics():
    """Get service metrics for monitoring"""
    return {
        "service": "team-hub",
        "status": "healthy",
        "active_connections": 0,  # Would be implemented with actual metrics
        "total_requests": 0,
        "avg_response_time": 0.0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
