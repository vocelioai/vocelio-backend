"""
🔧 CORS Middleware for Vocelio Services
Handles Cross-Origin Resource Sharing for all microservices
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to FastAPI app"""
    
    # Get allowed origins from environment
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    
    # Combine and clean origins
    origins = list(set(cors_origins + allowed_origins))
    origins = [origin.strip() for origin in origins if origin.strip()]
    
    # Default origins if none specified
    if not origins:
        origins = [
            "https://app.vocelio.ai",
            "https://dashboard.vocelio.ai",
            "https://*.railway.app",
            "http://localhost:3000",
            "http://localhost:3001"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    print(f"✅ CORS middleware added with origins: {origins}")
