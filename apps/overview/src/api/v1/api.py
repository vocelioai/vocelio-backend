"""
Overview Service API Router
Central router for all dashboard endpoints
"""

from fastapi import APIRouter
from api.v1.endpoints.dashboard import router as dashboard_router
from api.v1.endpoints.metrics import router as metrics_router
from api.v1.endpoints.reports import router as reports_router
from api.v1.endpoints.dashboard_integration import router as integration_router

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    dashboard_router, 
    prefix="/dashboard", 
    tags=["Dashboard"]
)

api_router.include_router(
    metrics_router, 
    prefix="/metrics", 
    tags=["Metrics"]
)

api_router.include_router(
    reports_router, 
    prefix="/reports", 
    tags=["Reports"]
)

# Dashboard Integration - Main endpoints for frontend
api_router.include_router(
    integration_router,
    prefix="/integration",
    tags=["Dashboard Integration"]
)

@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "🌍 Vocelio.ai Overview API v1",
        "description": "Global Command Center Dashboard API",
        "endpoints": {
            "dashboard": "/dashboard - Dashboard data and insights",
            "metrics": "/metrics - Real-time metrics and KPIs", 
            "reports": "/reports - Analytics and reporting"
        },
        "status": "🔥 LIVE",
        "version": "1.0.0"
    }
