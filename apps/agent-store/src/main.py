from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.v1.router import router as api_router
from core.config import get_settings
from shared.middleware.error_handling import add_error_handling

logger = structlog.get_logger()

def create_app() -> FastAPI:
    """Create FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Agent Store Service",
        description="AI Agent marketplace and management platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add error handlers
    add_error_handling(app)

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "agent-store",
            "version": "1.0.0"
        }

    return app

app = create_app()
