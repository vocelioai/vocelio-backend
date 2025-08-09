"""
Analytics Pro API Router
📊 Main API routing configuration for Analytics Pro service
"""

from fastapi import APIRouter
from src.api.v1.endpoints import analytics, reports, dashboards, exports

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    reports.router,
    prefix="/reports", 
    tags=["Reports"]
)

api_router.include_router(
    dashboards.router,
    prefix="/dashboards",
    tags=["Dashboards"]
)

api_router.include_router(
    exports.router,
    prefix="/exports",
    tags=["Exports"]
)
