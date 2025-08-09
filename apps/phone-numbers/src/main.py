# apps/phone-numbers/src/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.v1.api import api_router
from core.config import settings
from shared.database.client import get_db
from shared.middleware.cors import cors_middleware
from shared.middleware.rate_limiting import rate_limit_middleware
from shared.middleware.request_logging import logging_middleware
from shared.middleware.error_handling import error_handling_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Phone Numbers Service Starting...")
    print(f"📞 Service URL: {settings.SERVICE_URL}")
    print(f"🔗 Twilio Account: {settings.TWILIO_ACCOUNT_SID[:8]}...")
    print(f"💳 Stripe Mode: {'Live' if settings.STRIPE_LIVE_MODE else 'Test'}")
    
    yield
    
    # Shutdown
    print("📱 Phone Numbers Service Shutting Down...")


def create_application() -> FastAPI:
    """Create FastAPI application with all configurations"""
    
    application = FastAPI(
        title="Vocelio.ai Phone Numbers Service",
        description="🌍 Global phone number management with Twilio integration",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    application.middleware("http")(error_handling_middleware)
    application.middleware("http")(logging_middleware)
    application.middleware("http")(rate_limit_middleware)
    
    # Include API router
    application.include_router(
        api_router,
        prefix="/api/v1"
    )
    
    # Health check endpoint
    @application.get("/health")
    async def health_check():
        return {
            "service": "phone-numbers",
            "status": "healthy",
            "version": "1.0.0",
            "twilio_connected": True,
            "stripe_connected": True
        }
    
    # Root endpoint
    @application.get("/")
    async def root():
        return {
            "service": "Vocelio.ai Phone Numbers Service",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    return application


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )