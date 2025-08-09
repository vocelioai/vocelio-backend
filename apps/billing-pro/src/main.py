# apps/billing-pro/src/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

# Import API routes
from api.v1.api import api_router
from core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="💰 Vocelio.ai Billing Pro",
    version="1.0.0",
    description="Enterprise billing, subscriptions, and payment processing service",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "billing-pro",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "features": {
            "stripe_integration": True,
            "subscription_management": True,
            "usage_tracking": True,
            "invoicing": True,
            "payment_processing": True,
            "enterprise_billing": True
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "💰 Vocelio.ai Billing Pro Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Subscription Management",
            "Usage-based Billing", 
            "Payment Processing",
            "Invoice Generation",
            "Revenue Analytics",
            "Enterprise Billing"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8004)),
        reload=settings.ENVIRONMENT == "development"
    )
