# apps/smart-campaigns/src/api/v1/api.py
from fastapi import APIRouter

from api.v1.endpoints import campaigns, prospects, enhanced_campaigns

api_router = APIRouter()

# Include enhanced campaigns router (primary)
api_router.include_router(
    enhanced_campaigns.router,
    prefix="/enhanced-campaigns",
    tags=["enhanced-campaigns"]
)

# Include legacy campaign router for backward compatibility
api_router.include_router(
    campaigns.router,
    prefix="/campaigns",
    tags=["campaigns-legacy"]
)

api_router.include_router(
    prospects.router,
    prefix="/prospects", 
    tags=["prospects"]
)

# Health check endpoint for this service
@api_router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for Enhanced Smart Campaigns service"""
    return {
        "status": "healthy",
        "service": "smart-campaigns-enhanced",
        "version": "2.0.0",
        "features": [
            "AI Optimization",
            "A/B Testing", 
            "Advanced Analytics",
            "89+ Campaign Templates",
            "Comprehensive Performance Tracking"
        ]
    }
