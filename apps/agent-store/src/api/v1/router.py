from fastapi import APIRouter
from .endpoints import agents, marketplace, reviews, analytics

router = APIRouter()

# Include all endpoint routers
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
