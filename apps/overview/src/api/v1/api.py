"""
Enhanced Overview Service API Router
Central router for unified dashboard endpoints with real-time features
"""

from fastapi import APIRouter
from api.v1.endpoints.dashboard import router as dashboard_router
from api.v1.endpoints.metrics import router as metrics_router
from api.v1.endpoints.reports import router as reports_router
from api.v1.endpoints.dashboard_integration import router as integration_router
from api.v1.endpoints.enhanced_overview import router as enhanced_router

# Create main API router
api_router = APIRouter()

# Enhanced Overview - Primary unified endpoints (NEW)
api_router.include_router(
    enhanced_router,
    prefix="/enhanced",
    tags=["Enhanced Overview", "Real-time", "WebSocket"]
)

# Legacy endpoints (maintained for backward compatibility)
api_router.include_router(
    dashboard_router, 
    prefix="/dashboard", 
    tags=["Dashboard (Legacy)"]
)

api_router.include_router(
    metrics_router, 
    prefix="/metrics", 
    tags=["Metrics (Legacy)"]
)

api_router.include_router(
    reports_router, 
    prefix="/reports", 
    tags=["Reports (Legacy)"]
)

# Dashboard Integration - Main endpoints for frontend
api_router.include_router(
    integration_router,
    prefix="/integration",
    tags=["Dashboard Integration"]
)

@api_router.get("/")
async def api_root():
    """Enhanced API root endpoint"""
    return {
        "message": "🌍 Vocelio.ai Enhanced Overview API v2",
        "description": "Unified Command Center Dashboard API with Real-time Features",
        "endpoints": {
            "enhanced": "/enhanced - 🚀 NEW Unified real-time dashboard API",
            "dashboard": "/dashboard - 📊 Legacy dashboard data and insights",
            "metrics": "/metrics - 📈 Legacy real-time metrics and KPIs", 
            "reports": "/reports - 📋 Legacy analytics and reporting",
            "integration": "/integration - 🔗 Dashboard integration endpoints"
        },
        "features": [
            "🔥 Real-time WebSocket updates",
            "🧠 AI-powered insights",
            "⚡ Redis caching for performance",
            "📊 Live metrics tracking",
            "💾 System health monitoring",
            "🎯 Advanced analytics"
        ],
        "status": "🔥 ENHANCED & LIVE",
        "version": "2.0.0",
        "migration": {
            "from": "overview + overview-service",
            "to": "enhanced overview service",
            "backward_compatible": True
        }
    }
