from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.v1.router import router as api_router
from core.config import get_settings

logger = structlog.get_logger()

def create_app() -> FastAPI:
    """Create Enhanced Compliance FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Enhanced Compliance & Audit Service",
        description="Unified regulatory compliance, audit management, and risk assessment platform",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {
                "name": "Enhanced Compliance",
                "description": "🚀 Unified compliance and audit management"
            },
            {
                "name": "Audit",
                "description": "📋 Enterprise audit trail and event tracking"
            },
            {
                "name": "GDPR",
                "description": "🛡️ GDPR request management and data protection"
            },
            {
                "name": "Risk Management",
                "description": "⚠️ Risk assessments and incident reporting"
            },
            {
                "name": "Audit (Legacy)",
                "description": "📊 Legacy audit endpoints (backward compatible)"
            },
            {
                "name": "GDPR (Legacy)",
                "description": "🔒 Legacy GDPR endpoints (backward compatible)"
            },
            {
                "name": "Telecom (Legacy)",
                "description": "📞 Legacy telecom compliance endpoints"
            },
            {
                "name": "Reports (Legacy)",
                "description": "📈 Legacy reporting endpoints"
            }
        ]
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        """Enhanced service root endpoint"""
        return {
            "service": "enhanced-compliance",
            "status": "🔥 ENHANCED & OPERATIONAL",
            "version": "2.0.0",
            "migration": {
                "from": ["compliance", "audit-compliance"],
                "to": "enhanced-compliance",
                "completed": True
            },
            "features": [
                "🔐 Enterprise audit trail tracking",
                "🛡️ GDPR request management",
                "📞 Telecom compliance monitoring",
                "⚠️ Risk assessment and incident reporting",
                "📊 Compliance assessments and scoring",
                "📈 Automated report generation",
                "📋 Real-time compliance dashboard",
                "🎯 Multi-framework support (GDPR, SOX, ISO27001, etc.)"
            ],
            "endpoints": {
                "primary": "/api/v1/enhanced - 🚀 NEW Unified compliance API",
                "legacy": {
                    "audit": "/api/v1/audit - 📊 Legacy audit endpoints",
                    "gdpr": "/api/v1/gdpr - 🔒 Legacy GDPR endpoints",
                    "telecom": "/api/v1/telecom - 📞 Legacy telecom endpoints",
                    "reports": "/api/v1/reports - 📈 Legacy reports endpoints"
                }
            },
            "frameworks_supported": [
                "GDPR", "SOX", "HIPAA", "PCI-DSS", "ISO27001", 
                "NIST", "FISMA", "CCPA", "FCC Part 64", "ePrivacy"
            ],
            "compatibility": "✅ Backward compatible with legacy endpoints",
            "description": "Enterprise compliance platform with comprehensive audit capabilities"
        }

    @app.get("/health")
    async def health():
        """Enhanced health check endpoint."""
        return {
            "status": "🔥 ENHANCED & HEALTHY",
            "service": "enhanced-compliance",
            "version": "2.0.0",
            "features": {
                "audit_tracking": True,
                "gdpr_management": True,
                "risk_assessment": True,
                "incident_reporting": True,
                "compliance_scoring": True,
                "report_generation": True,
                "telecom_compliance": True,
                "multi_framework_support": True
            },
            "merger_status": "✅ Successfully merged compliance + audit-compliance",
            "frameworks": [
                "GDPR", "SOX", "HIPAA", "PCI-DSS", "ISO27001",
                "NIST", "FISMA", "CCPA", "FCC Part 64", "ePrivacy"
            ]
        }

    return app

app = create_app()
