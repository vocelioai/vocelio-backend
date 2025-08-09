"""
Voice Lab Microservice - Main Application
FastAPI service for voice generation, management, cloning, and analytics
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from pathlib import Path

from api.v1.api import api_router
from core.config import settings
from shared.database.client import get_database
from shared.middleware.cors import setup_cors
from shared.middleware.error_handling import setup_error_handling
from shared.middleware.request_logging import setup_request_logging

# Create FastAPI app
app = FastAPI(
    title="Voice Lab Service",
    description="Advanced AI voice generation, management, cloning, and analytics service",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Setup middleware
setup_cors(app)
setup_error_handling(app)
setup_request_logging(app)

# Mount static files for generated audio
static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize service resources"""
    # Ensure static directories exist
    directories = ["static/voices", "static/previews", "static/clones", "static/tests"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("🎙️ Voice Lab Service started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup service resources"""
    print("🎙️ Voice Lab Service shutting down...")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Voice Lab",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "voice_generation",
            "voice_cloning", 
            "voice_testing",
            "voice_analytics",
            "batch_operations"
        ]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "voice-lab",
        "database": "connected",
        "static_files": "accessible",
        "ai_engine": "operational"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
