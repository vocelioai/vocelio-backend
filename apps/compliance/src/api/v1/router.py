from fastapi import APIRouter
from .endpoints import audit, gdpr, telecom, reports, enhanced_compliance

router = APIRouter()

# Enhanced compliance endpoints (NEW - merged functionality)
router.include_router(
    enhanced_compliance.router, 
    prefix="/enhanced", 
    tags=["Enhanced Compliance", "Audit", "GDPR", "Risk Management"]
)

# Legacy endpoints (maintained for backward compatibility)
router.include_router(audit.router, prefix="/audit", tags=["Audit (Legacy)"])
router.include_router(gdpr.router, prefix="/gdpr", tags=["GDPR (Legacy)"])
router.include_router(telecom.router, prefix="/telecom", tags=["Telecom (Legacy)"])
router.include_router(reports.router, prefix="/reports", tags=["Reports (Legacy)"])
