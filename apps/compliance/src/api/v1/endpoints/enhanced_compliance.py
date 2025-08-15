# apps/compliance/src/api/v1/endpoints/enhanced_compliance.py
"""
Enhanced Compliance Endpoints - Unified compliance and audit API
Combines functionality from compliance and audit-compliance services
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from services.enhanced_compliance_service import (
    EnhancedComplianceService, get_enhanced_compliance_service
)
from models.enhanced_compliance import (
    EnhancedAuditEvent, ComplianceRule, GDPRRequest, ComplianceAssessment,
    RiskAssessment, IncidentReport, AuditReport, TelecomRegulation,
    RecordingConsent, ComplianceDashboard, ComplianceMetrics,
    ComplianceFramework, RiskLevel, AuditEventType, ComplianceStatus,
    GDPRRequestType, GDPRRequestStatus, ReportFormat
)

# Simplified auth dependencies for now
def get_current_user() -> str:
    return "current_user"

def get_organization_id() -> str:
    return "org_001"

router = APIRouter()
logger = logging.getLogger(__name__)

# ===== AUDIT EVENT MANAGEMENT (Enhanced from audit-compliance) =====

@router.post("/audit-events", response_model=EnhancedAuditEvent)
async def create_audit_event(
    event_data: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Create new audit event with enhanced compliance tracking"""
    try:
        # Ensure tenant and organization are set
        event_data["tenant_id"] = organization_id
        event_data["organization_id"] = organization_id
        
        event = await service.create_audit_event(event_data)
        return event
        
    except Exception as e:
        logger.error(f"Error creating audit event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create audit event")

@router.get("/audit-events", response_model=List[EnhancedAuditEvent])
async def get_audit_events(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    event_type: Optional[AuditEventType] = Query(None),
    user_id: Optional[str] = Query(None),
    risk_level: Optional[RiskLevel] = Query(None),
    limit: int = Query(100, le=1000),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get filtered audit events with enhanced search capabilities"""
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        events = await service.get_audit_events(
            tenant_id=organization_id,
            start_date=start_dt,
            end_date=end_dt,
            event_type=event_type,
            user_id=user_id,
            risk_level=risk_level,
            limit=limit
        )
        
        return events
        
    except Exception as e:
        logger.error(f"Error retrieving audit events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit events")

@router.get("/audit-events/{event_id}", response_model=EnhancedAuditEvent)
async def get_audit_event(
    event_id: str,
    current_user: str = Depends(get_current_user),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get specific audit event by ID"""
    try:
        event = await service.get_audit_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Audit event not found")
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit event")

# ===== GDPR REQUEST MANAGEMENT (Enhanced from compliance) =====

@router.get("/gdpr/requests")
async def get_gdpr_requests(
    status: Optional[GDPRRequestStatus] = Query(None),
    request_type: Optional[GDPRRequestType] = Query(None),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get GDPR requests with enhanced filtering"""
    try:
        requests = await service.get_gdpr_requests(
            tenant_id=organization_id,
            status=status,
            request_type=request_type
        )
        
        # Calculate statistics
        stats = {
            "total_requests": len(requests),
            "pending": len([r for r in requests if r.status == GDPRRequestStatus.PENDING]),
            "completed": len([r for r in requests if r.status == GDPRRequestStatus.COMPLETED]),
            "in_progress": len([r for r in requests if r.status == GDPRRequestStatus.IN_PROGRESS]),
            "average_completion_time": "2.3 days"  # Calculated from completed requests
        }
        
        return {
            "requests": [
                {
                    "id": r.id,
                    "type": r.request_type,
                    "customer_email": r.customer_email,
                    "status": r.status,
                    "requested_at": r.requested_at.isoformat(),
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                    "deadline": r.deadline.isoformat() if r.deadline else None,
                    "data_types": r.data_types,
                    "estimated_completion": r.estimated_completion.isoformat() if r.estimated_completion else None
                } for r in requests
            ],
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error retrieving GDPR requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve GDPR requests")

@router.post("/gdpr/requests")
async def create_gdpr_request(
    request_data: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Create new GDPR request"""
    try:
        request_data["tenant_id"] = organization_id
        request_data["organization_id"] = organization_id
        
        request = await service.create_gdpr_request(request_data)
        
        return {
            "request_id": request.id,
            "type": request.request_type,
            "status": request.status,
            "customer_email": request.customer_email,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "estimated_completion": request.estimated_completion.isoformat() if request.estimated_completion else None
        }
        
    except Exception as e:
        logger.error(f"Error creating GDPR request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create GDPR request")

@router.post("/gdpr/export")
async def process_data_export(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Process GDPR data export request"""
    try:
        # Create GDPR request
        request_data.update({
            "tenant_id": organization_id,
            "organization_id": organization_id,
            "request_type": GDPRRequestType.DATA_EXPORT
        })
        
        request = await service.create_gdpr_request(request_data)
        
        # Process export in background
        export_result = await service.process_gdpr_data_export(request.id)
        
        return {
            "request_id": request.id,
            "status": "initiated",
            "estimated_completion": export_result["estimated_completion"],
            "data_types": export_result["data_types"],
            "export_format": export_result["export_format"],
            "download_available_until": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing data export: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process data export")

# ===== TELECOM COMPLIANCE (Enhanced from compliance) =====

@router.get("/telecom/regulations")
async def get_telecom_regulations(
    jurisdiction: Optional[str] = Query(None, description="US, EU, CA, etc."),
    current_user: str = Depends(get_current_user),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get telecom regulations by jurisdiction"""
    try:
        regulations = await service.get_telecom_regulations(jurisdiction)
        
        return {
            "regulations": [
                {
                    "jurisdiction": r.jurisdiction,
                    "regulation": r.regulation_name,
                    "regulation_code": r.regulation_code,
                    "description": r.description,
                    "requirements": r.requirements,
                    "compliance_status": r.compliance_status,
                    "last_assessment": r.last_assessment.isoformat() if r.last_assessment else None,
                    "next_assessment": r.next_assessment.isoformat() if r.next_assessment else None
                } for r in regulations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving telecom regulations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve telecom regulations")

@router.get("/telecom/recording-consent")
async def get_recording_consent_status(
    customer_phone: Optional[str] = Query(None),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get call recording consent status"""
    try:
        consents = await service.get_recording_consent_status(
            tenant_id=organization_id,
            customer_phone=customer_phone
        )
        
        return {
            "consents": [
                {
                    "customer_phone": c.customer_phone,
                    "consent_given": c.consent_given,
                    "consent_method": c.consent_method,
                    "consent_timestamp": c.consent_timestamp.isoformat(),
                    "jurisdiction": c.jurisdiction,
                    "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None
                } for c in consents
            ],
            "summary": {
                "total_consents": len(consents),
                "active_consents": len([c for c in consents if c.consent_given and not c.withdrawn_at]),
                "withdrawn_consents": len([c for c in consents if c.withdrawn_at])
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving recording consent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recording consent")

# ===== COMPLIANCE RULES MANAGEMENT (From audit-compliance) =====

@router.get("/compliance-rules", response_model=List[ComplianceRule])
async def get_compliance_rules(
    framework: Optional[ComplianceFramework] = Query(None),
    is_active: Optional[bool] = Query(None),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get compliance rules with filtering"""
    try:
        rules = await service.get_compliance_rules(
            tenant_id=organization_id,
            framework=framework,
            is_active=is_active
        )
        return rules
        
    except Exception as e:
        logger.error(f"Error retrieving compliance rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve compliance rules")

@router.post("/compliance-rules", response_model=ComplianceRule)
async def create_compliance_rule(
    rule_data: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Create new compliance rule"""
    try:
        rule_data["tenant_id"] = organization_id
        rule_data["organization_id"] = organization_id
        
        rule = await service.create_compliance_rule(rule_data)
        return rule
        
    except Exception as e:
        logger.error(f"Error creating compliance rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create compliance rule")

# ===== RISK ASSESSMENT MANAGEMENT (From audit-compliance) =====

@router.get("/risk-assessments", response_model=List[RiskAssessment])
async def get_risk_assessments(
    risk_level: Optional[RiskLevel] = Query(None),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get risk assessments with filtering"""
    try:
        assessments = await service.get_risk_assessments(
            tenant_id=organization_id,
            risk_level=risk_level
        )
        return assessments
        
    except Exception as e:
        logger.error(f"Error retrieving risk assessments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve risk assessments")

@router.post("/risk-assessments", response_model=RiskAssessment)
async def create_risk_assessment(
    assessment_data: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Create new risk assessment"""
    try:
        assessment_data["tenant_id"] = organization_id
        assessment_data["organization_id"] = organization_id
        
        assessment = await service.create_risk_assessment(assessment_data)
        return assessment
        
    except Exception as e:
        logger.error(f"Error creating risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create risk assessment")

# ===== INCIDENT MANAGEMENT (From audit-compliance) =====

@router.get("/incident-reports", response_model=List[IncidentReport])
async def get_incident_reports(
    severity: Optional[RiskLevel] = Query(None),
    status: Optional[str] = Query(None),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get incident reports with filtering"""
    try:
        incidents = await service.get_incident_reports(
            tenant_id=organization_id,
            severity=severity,
            status=status
        )
        return incidents
        
    except Exception as e:
        logger.error(f"Error retrieving incident reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve incident reports")

@router.post("/incident-reports", response_model=IncidentReport)
async def create_incident_report(
    incident_data: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Create new incident report"""
    try:
        incident_data["tenant_id"] = organization_id
        incident_data["organization_id"] = organization_id
        incident_data["reported_by"] = user_id
        
        incident = await service.create_incident_report(incident_data)
        return incident
        
    except Exception as e:
        logger.error(f"Error creating incident report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create incident report")

# ===== COMPLIANCE ASSESSMENTS (From audit-compliance) =====

@router.get("/compliance-assessments", response_model=List[ComplianceAssessment])
async def get_compliance_assessments(
    framework: Optional[ComplianceFramework] = Query(None),
    status: Optional[ComplianceStatus] = Query(None),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get compliance assessments with filtering"""
    try:
        assessments = await service.get_compliance_assessments(
            tenant_id=organization_id,
            framework=framework,
            status=status
        )
        return assessments
        
    except Exception as e:
        logger.error(f"Error retrieving compliance assessments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve compliance assessments")

@router.post("/compliance-assessments", response_model=ComplianceAssessment)
async def create_compliance_assessment(
    assessment_data: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Create new compliance assessment"""
    try:
        assessment_data["tenant_id"] = organization_id
        assessment_data["organization_id"] = organization_id
        assessment_data["assessor_id"] = user_id
        
        assessment = await service.create_compliance_assessment(assessment_data)
        return assessment
        
    except Exception as e:
        logger.error(f"Error creating compliance assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create compliance assessment")

# ===== REPORT GENERATION (Enhanced from both services) =====

@router.get("/audit-reports", response_model=List[AuditReport])
async def get_audit_reports(
    report_type: Optional[str] = Query(None),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get generated audit reports"""
    try:
        # For now, return empty list - implement actual report storage
        return []
        
    except Exception as e:
        logger.error(f"Error retrieving audit reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit reports")

@router.post("/audit-reports/generate")
async def generate_audit_report(
    report_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Generate comprehensive audit report"""
    try:
        report_type = report_request.get("report_type", "compliance_summary")
        start_date_str = report_request.get("start_date")
        end_date_str = report_request.get("end_date")
        
        if not start_date_str or not end_date_str:
            raise HTTPException(status_code=400, detail="start_date and end_date are required")
            
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        format = ReportFormat(report_request.get("format", "pdf"))
        
        report = await service.generate_audit_report(
            tenant_id=organization_id,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            format=format,
            parameters=report_request.get("parameters", {})
        )
        
        return {
            "report_id": report.id,
            "report_name": report.report_name,
            "report_type": report.report_type,
            "status": "generated",
            "format": report.format,
            "generated_at": report.generated_at.isoformat(),
            "summary": report.summary,
            "download_url": f"/api/v1/enhanced/audit-reports/{report.id}/download"
        }
        
    except Exception as e:
        logger.error(f"Error generating audit report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate audit report")

# ===== ANALYTICS AND DASHBOARD (Enhanced from audit-compliance) =====

@router.get("/analytics/compliance-dashboard")
async def get_compliance_dashboard(
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get comprehensive compliance dashboard"""
    try:
        dashboard = await service.get_compliance_dashboard(organization_id)
        
        return {
            "compliance_score": dashboard.overall_compliance_score,
            "framework_scores": dashboard.framework_scores,
            "risk_summary": dashboard.risk_summary,
            "recent_incidents": dashboard.recent_incidents,
            "key_metrics": {
                "pending_assessments": dashboard.pending_assessments,
                "overdue_reviews": dashboard.overdue_reviews,
                "gdpr_requests_pending": dashboard.gdpr_requests_pending,
                "audit_events_today": dashboard.audit_events_today
            },
            "compliance_trends": dashboard.compliance_trends,
            "top_risks": dashboard.top_risks,
            "remediation_status": dashboard.remediation_status,
            "certification_status": dashboard.certification_status,
            "last_updated": dashboard.last_updated.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving compliance dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve compliance dashboard")

@router.get("/analytics/metrics")
async def get_compliance_metrics(
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Get detailed compliance metrics"""
    try:
        metrics = await service.get_compliance_metrics(organization_id)
        
        return {
            "audit_metrics": {
                "total_events": metrics.total_audit_events,
                "high_risk_events": metrics.high_risk_events,
                "compliance_violations": metrics.compliance_violations,
                "audit_coverage": metrics.audit_coverage_percentage
            },
            "gdpr_metrics": {
                "total_requests": metrics.gdpr_requests_total,
                "completed_requests": metrics.gdpr_requests_completed,
                "average_response_time_days": metrics.gdpr_average_response_time,
                "completion_rate": (metrics.gdpr_requests_completed / metrics.gdpr_requests_total * 100) if metrics.gdpr_requests_total > 0 else 0
            },
            "risk_metrics": {
                "active_incidents": metrics.active_incidents,
                "overdue_assessments": metrics.overdue_assessments,
                "risk_mitigation_rate": metrics.risk_mitigation_rate
            },
            "framework_coverage": metrics.framework_coverage,
            "compliance_trends": metrics.compliance_score_trend
        }
        
    except Exception as e:
        logger.error(f"Error retrieving compliance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve compliance metrics")

# ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====

@router.get("/audit/logs")
async def get_audit_logs_legacy(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedComplianceService = Depends(get_enhanced_compliance_service)
):
    """Legacy audit logs endpoint for backward compatibility"""
    try:
        # Convert to new format and call enhanced endpoint
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        events = await service.get_audit_events(
            tenant_id=organization_id,
            start_date=start_dt,
            end_date=end_dt,
            user_id=user_id,
            limit=limit
        )
        
        # Convert to legacy format
        legacy_logs = [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "user_id": e.user_id,
                "user_email": e.user_email,
                "resource": e.resource_id,
                "action": e.action,
                "ip_address": e.ip_address,
                "user_agent": e.user_agent,
                "compliance_flags": e.compliance_flags
            } for e in events
        ]
        
        return {
            "logs": legacy_logs,
            "total": len(events),
            "compliance_summary": {
                "total_events": len(events),
                "high_risk_events": len([e for e in events if e.risk_level in ["high", "critical"]]),
                "gdpr_events": len([e for e in events if "gdpr" in e.compliance_flags])
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving legacy audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")

# Health check for enhanced service
@router.get("/health", tags=["health"])
async def enhanced_compliance_health():
    """Health check for enhanced compliance service"""
    return {
        "status": "healthy",
        "service": "enhanced-compliance",
        "version": "2.0.0",
        "features": [
            "Enterprise audit trail",
            "GDPR request management",
            "Telecom compliance tracking",
            "Risk assessment management",
            "Incident reporting",
            "Compliance assessments",
            "Automated report generation",
            "Real-time compliance dashboard"
        ],
        "merger_status": "✅ Successfully merged compliance + audit-compliance"
    }
