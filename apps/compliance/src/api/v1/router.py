from fastapi import APIRouter
from .endpoints import audit, gdpr, telecom, reports

router = APIRouter()

# Include all endpoint routers
router.include_router(audit.router, prefix="/audit", tags=["audit"])
router.include_router(gdpr.router, prefix="/gdpr", tags=["gdpr"])
router.include_router(telecom.router, prefix="/telecom", tags=["telecom"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
