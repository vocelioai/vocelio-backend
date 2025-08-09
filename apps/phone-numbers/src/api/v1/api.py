# apps/phone-numbers/src/api/v1/api.py
from fastapi import APIRouter

from api.v1.endpoints import numbers, purchase, verification, webhooks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    numbers.router,
    prefix="/numbers",
    tags=["Phone Numbers"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    purchase.router,
    prefix="/purchase",
    tags=["Number Purchase"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    verification.router,
    prefix="/verification",
    tags=["Number Verification"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Webhooks"],
    responses={404: {"description": "Not found"}}
)


# Additional utility endpoints
@api_router.get("/health", tags=["Health"])
async def service_health():
    """Phone Numbers Service Health Check"""
    return {
        "service": "phone-numbers",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2025-08-04T00:00:00Z"
    }


@api_router.get("/info", tags=["Service Info"])
async def service_info():
    """Get service information and capabilities"""
    from core.config import settings
    
    return {
        "service": "phone-numbers",
        "version": "1.0.0",
        "description": "🌍 Global phone number management with Twilio integration",
        "capabilities": [
            "🔍 Number search across 85+ countries",
            "💳 Instant purchase with Stripe",
            "📊 Real-time usage analytics", 
            "🔗 Twilio webhook integration",
            "✅ Number verification",
            "📱 SMS/Voice/MMS support",
            "🌐 Local, toll-free, and mobile numbers"
        ],
        "supported_countries": len(settings.SUPPORTED_COUNTRIES),
        "supported_features": ["voice", "sms", "mms", "verification", "analytics"],
        "integrations": ["Twilio", "Stripe", "Vocelio AI Platform"],
        "endpoints": {
            "numbers": "/api/v1/numbers",
            "purchase": "/api/v1/purchase", 
            "verification": "/api/v1/verification",
            "webhooks": "/api/v1/webhooks"
        }
    }