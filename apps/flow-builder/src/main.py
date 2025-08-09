# apps/flow-builder/src/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from api.v1.api import api_router
from core.config import settings
from shared.database.client import get_supabase_client
from shared.middleware.cors import setup_cors
from shared.middleware.request_logging import LoggingMiddleware
from shared.middleware.error_handling import ErrorHandlerMiddleware
from shared.auth.dependencies import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🔧 Flow Builder Service starting up...")
    
    # Initialize database connection
    supabase = get_supabase_client()
    app.state.supabase = supabase
    
    # Verify database connection
    try:
        # Test connection with a simple query
        result = supabase.table('flows').select('id').limit(1).execute()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    print("🚀 Flow Builder Service ready!")
    
    yield
    
    # Shutdown
    print("🔧 Flow Builder Service shutting down...")

# Create FastAPI application
app = FastAPI(
    title="Vocelio Flow Builder Service",
    description="Visual Flow Builder for AI Call Center Automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Add custom middleware
app.add_middleware(LoggingMiddleware, service_name="flow-builder")
app.add_middleware(ErrorHandlerMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Flow Builder Service",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        supabase = app.state.supabase
        result = supabase.table('flows').select('id').limit(1).execute()
        
        return {
            "status": "healthy",
            "service": "flow-builder",
            "database": "connected",
            "timestamp": "2025-08-04T12:00:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "flow-builder",
                "database": "disconnected",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )