from fastapi import APIRouter
from .endpoints import branding, templates, domains, assets

router = APIRouter()

# Include all endpoint routers
router.include_router(branding.router, prefix="/branding", tags=["branding"])
router.include_router(templates.router, prefix="/templates", tags=["templates"]) 
router.include_router(domains.router, prefix="/domains", tags=["domains"])
router.include_router(assets.router, prefix="/assets", tags=["assets"])
