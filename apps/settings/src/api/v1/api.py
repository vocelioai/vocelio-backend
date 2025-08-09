"""
Settings Service API Router
Main API router that includes all endpoint modules
"""

from fastapi import APIRouter
from .endpoints import (
    organization,
    user,
    notifications,
    security,
    preferences
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    organization.router,
    prefix="/organization",
    tags=["Organization Settings"]
)

api_router.include_router(
    user.router,
    prefix="/user",
    tags=["User Settings"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notification Settings"]
)

api_router.include_router(
    security.router,
    prefix="/security",
    tags=["Security Settings"]
)

api_router.include_router(
    preferences.router,
    prefix="/preferences",
    tags=["User Preferences"]
)

# Settings overview endpoint
@api_router.get("/overview", tags=["Settings Overview"])
async def get_settings_overview():
    """Get complete settings overview for dashboard"""
    return {
        "message": "Settings overview endpoint",
        "available_endpoints": {
            "organization": "/api/v1/organization",
            "user": "/api/v1/user", 
            "notifications": "/api/v1/notifications",
            "security": "/api/v1/security",
            "preferences": "/api/v1/preferences"
        }
    }
