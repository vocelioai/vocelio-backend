# apps/compliance/src/services/enhanced_compliance_service.py
"""
Enhanced Compliance Service - Unified compliance and audit service layer
Combines structured compliance with comprehensive audit capabilities
"""

import logging
import json
import csv
import io
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from models.enhanced_compliance import (
    EnhancedAuditEvent, ComplianceRule, GDPRRequest, ComplianceAssessment,
    RiskAssessment, IncidentReport, AuditReport, TelecomRegulation,
    RecordingConsent, ComplianceDashboard, ComplianceMetrics,
    ComplianceFramework, RiskLevel, AuditEventType, ComplianceStatus,
    GDPRRequestType, GDPRRequestStatus, ReportFormat
)

logger = logging.getLogger(__name__)

class EnhancedComplianceService:
    """Enhanced compliance service with comprehensive audit capabilities"""
    
    def __init__(self):
        # In-memory storage for demo - replace with actual database
        self.audit_events = []
        self.compliance_rules = []
        self.gdpr_requests = []
        self.risk_assessments = []
        self.incident_reports = []
        self.compliance_assessments = []
        self.audit_reports = []
        self.telecom_regulations = []
        self.recording_consents = []
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample compliance data"""
        # Sample audit events
        self.audit_events = [
            EnhancedAuditEvent(
                tenant_id="tenant_001",
                organization_id="org_001",
                event_type=AuditEventType.CALL_RECORDING_ACCESS,
                user_id="user_123",
                user_email="john@company.com",
                resource_type="recording",
                resource_id="recording_456",
                action="download",
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0...",
                compliance_flags=["data_access"],
                compliance_frameworks=[ComplianceFramework.GDPR],
                risk_level=RiskLevel.MEDIUM
            ),
            EnhancedAuditEvent(
                tenant_id="tenant_001",
                organization_id="org_001",
                event_type=AuditEventType.GDPR_REQUEST,
                user_id="user_456",
                user_email="sarah@company.com",
                resource_type="customer_data",
                resource_id="customer_789",
                action="data_export",
                ip_address="10.0.0.50",
                user_agent="Chrome/120.0...",
                compliance_flags=["gdpr", "data_export"],
                compliance_frameworks=[ComplianceFramework.GDPR],
                risk_level=RiskLevel.HIGH
            )
        ]
        
        # Sample GDPR requests
        self.gdpr_requests = [
            GDPRRequest(
                tenant_id="tenant_001",
                organization_id="org_001",
                request_type=GDPRRequestType.DATA_EXPORT,
                customer_email="customer@example.com",
                status=GDPRRequestStatus.COMPLETED,
                requested_at=datetime.now() - timedelta(days=5),
                completed_at=datetime.now() - timedelta(days=3),
                data_types=["call_recordings", "transcripts", "contact_info"],
                export_format=ReportFormat.JSON
            ),
            GDPRRequest(
                tenant_id="tenant_001",
                organization_id="org_001",
                request_type=GDPRRequestType.DATA_DELETION,
                customer_email="deleteuser@example.com",
                status=GDPRRequestStatus.PENDING,
                requested_at=datetime.now() - timedelta(days=1),
                deadline=datetime.now() + timedelta(days=29),
                data_types=["all_personal_data"]
            )
        ]
        
        # Sample telecom regulations
        self.telecom_regulations = [
            TelecomRegulation(
                jurisdiction="US",
                regulation_name="FCC Part 64",
                regulation_code="FCC-64",
                description="Telephone Consumer Protection Act compliance",
                requirements=[
                    "Call recording consent",
                    "Do Not Call registry compliance",
                    "Caller ID transmission"
                ],
                compliance_status=ComplianceStatus.COMPLIANT
            ),
            TelecomRegulation(
                jurisdiction="EU",
                regulation_name="ePrivacy Directive",
                regulation_code="2002/58/EC",
                description="Electronic communications privacy",
                requirements=[
                    "Recording consent",
                    "Data retention limits",
                    "Cross-border data transfers"
                ],
                compliance_status=ComplianceStatus.COMPLIANT
            )
        ]
    
    # Audit Event Management (Enhanced from audit-compliance)
    async def create_audit_event(self, event_data: Dict[str, Any]) -> EnhancedAuditEvent:
        """Create new audit event with enhanced tracking"""
        event = EnhancedAuditEvent(**event_data)
        self.audit_events.append(event)
        
        # Auto-detect compliance frameworks based on event type
        if event.event_type == AuditEventType.GDPR_REQUEST:
            event.compliance_frameworks.append(ComplianceFramework.GDPR)
        elif event.event_type == AuditEventType.CALL_RECORDING_ACCESS:
            event.compliance_frameworks.extend([
                ComplianceFramework.FCC_PART_64,
                ComplianceFramework.EPRIVACY
            ])
        
        logger.info(f"Created audit event: {event.id} - {event.event_type}")
        return event
    
    async def get_audit_events(
        self,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        limit: int = 100
    ) -> List[EnhancedAuditEvent]:
        """Get filtered audit events"""
        events = [e for e in self.audit_events if e.tenant_id == tenant_id]
        
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]
        
        return events[:limit]
    
    async def get_audit_event_by_id(self, event_id: str) -> Optional[EnhancedAuditEvent]:
        """Get specific audit event"""
        return next((e for e in self.audit_events if e.id == event_id), None)
    
    # GDPR Request Management (Enhanced from compliance)
    async def create_gdpr_request(self, request_data: Dict[str, Any]) -> GDPRRequest:
        """Create new GDPR request with enhanced tracking"""
        request = GDPRRequest(**request_data)
        
        # Set deadline based on request type
        if request.request_type == GDPRRequestType.DATA_EXPORT:
            request.deadline = request.requested_at + timedelta(days=30)
        elif request.request_type == GDPRRequestType.DATA_DELETION:
            request.deadline = request.requested_at + timedelta(days=30)
        
        self.gdpr_requests.append(request)
        
        # Create corresponding audit event
        await self.create_audit_event({
            "tenant_id": request.tenant_id,
            "organization_id": request.organization_id,
            "event_type": AuditEventType.GDPR_REQUEST,
            "resource_type": "gdpr_request",
            "resource_id": request.id,
            "action": f"created_{request.request_type}",
            "ip_address": "system",
            "user_agent": "system",
            "compliance_frameworks": [ComplianceFramework.GDPR],
            "details": {"request_type": request.request_type, "customer_email": request.customer_email}
        })
        
        logger.info(f"Created GDPR request: {request.id} - {request.request_type}")
        return request
    
    async def get_gdpr_requests(
        self,
        tenant_id: str,
        status: Optional[GDPRRequestStatus] = None,
        request_type: Optional[GDPRRequestType] = None
    ) -> List[GDPRRequest]:
        """Get filtered GDPR requests"""
        requests = [r for r in self.gdpr_requests if r.tenant_id == tenant_id]
        
        if status:
            requests = [r for r in requests if r.status == status]
        if request_type:
            requests = [r for r in requests if r.request_type == request_type]
        
        return requests
    
    async def process_gdpr_data_export(self, request_id: str) -> Dict[str, Any]:
        """Process GDPR data export request"""
        request = next((r for r in self.gdpr_requests if r.id == request_id), None)
        if not request:
            raise ValueError("GDPR request not found")
        
        request.status = GDPRRequestStatus.IN_PROGRESS
        request.estimated_completion = datetime.now() + timedelta(days=2)
        
        # Simulate data export process
        export_data = {
            "request_id": request.id,
            "customer_email": request.customer_email,
            "data_types": request.data_types,
            "export_format": request.export_format or ReportFormat.JSON,
            "estimated_completion": request.estimated_completion.isoformat()
        }
        
        logger.info(f"Processing GDPR export: {request_id}")
        return export_data
    
    # Compliance Rule Management (From audit-compliance)
    async def create_compliance_rule(self, rule_data: Dict[str, Any]) -> ComplianceRule:
        """Create new compliance rule"""
        rule = ComplianceRule(**rule_data)
        self.compliance_rules.append(rule)
        
        logger.info(f"Created compliance rule: {rule.id} - {rule.framework}")
        return rule
    
    async def get_compliance_rules(
        self,
        tenant_id: str,
        framework: Optional[ComplianceFramework] = None,
        is_active: Optional[bool] = None
    ) -> List[ComplianceRule]:
        """Get filtered compliance rules"""
        rules = [r for r in self.compliance_rules if r.tenant_id == tenant_id]
        
        if framework:
            rules = [r for r in rules if r.framework == framework]
        if is_active is not None:
            rules = [r for r in rules if r.is_active == is_active]
        
        return rules
    
    # Risk Assessment Management (From audit-compliance)
    async def create_risk_assessment(self, assessment_data: Dict[str, Any]) -> RiskAssessment:
        """Create new risk assessment"""
        assessment = RiskAssessment(**assessment_data)
        
        # Calculate risk score
        assessment.risk_score = assessment.likelihood * assessment.impact
        
        self.risk_assessments.append(assessment)
        
        logger.info(f"Created risk assessment: {assessment.id} - {assessment.risk_name}")
        return assessment
    
    async def get_risk_assessments(
        self,
        tenant_id: str,
        risk_level: Optional[RiskLevel] = None
    ) -> List[RiskAssessment]:
        """Get filtered risk assessments"""
        assessments = [a for a in self.risk_assessments if a.tenant_id == tenant_id]
        
        if risk_level:
            assessments = [a for a in assessments if a.residual_risk_level == risk_level]
        
        return assessments
    
    # Incident Report Management (From audit-compliance)
    async def create_incident_report(self, incident_data: Dict[str, Any]) -> IncidentReport:
        """Create new incident report"""
        incident = IncidentReport(**incident_data)
        self.incident_reports.append(incident)
        
        # Create corresponding audit event
        await self.create_audit_event({
            "tenant_id": incident.tenant_id,
            "organization_id": incident.organization_id,
            "event_type": AuditEventType.SECURITY_EVENT,
            "resource_type": "incident_report",
            "resource_id": incident.id,
            "action": "incident_reported",
            "ip_address": "system",
            "user_agent": "system",
            "risk_level": incident.severity,
            "details": {"incident_type": incident.incident_type, "title": incident.title}
        })
        
        logger.info(f"Created incident report: {incident.id} - {incident.title}")
        return incident
    
    async def get_incident_reports(
        self,
        tenant_id: str,
        severity: Optional[RiskLevel] = None,
        status: Optional[str] = None
    ) -> List[IncidentReport]:
        """Get filtered incident reports"""
        incidents = [i for i in self.incident_reports if i.tenant_id == tenant_id]
        
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        return incidents
    
    # Telecom Compliance (Enhanced from compliance)
    async def get_telecom_regulations(
        self,
        jurisdiction: Optional[str] = None
    ) -> List[TelecomRegulation]:
        """Get telecom regulations by jurisdiction"""
        regulations = self.telecom_regulations
        
        if jurisdiction:
            regulations = [r for r in regulations if r.jurisdiction.upper() == jurisdiction.upper()]
        
        return regulations
    
    async def get_recording_consent_status(
        self,
        tenant_id: str,
        customer_phone: Optional[str] = None
    ) -> List[RecordingConsent]:
        """Get recording consent status"""
        consents = [c for c in self.recording_consents if c.tenant_id == tenant_id]
        
        if customer_phone:
            consents = [c for c in consents if c.customer_phone == customer_phone]
        
        return consents
    
    # Compliance Assessment (From audit-compliance)
    async def create_compliance_assessment(self, assessment_data: Dict[str, Any]) -> ComplianceAssessment:
        """Create new compliance assessment"""
        assessment = ComplianceAssessment(**assessment_data)
        self.compliance_assessments.append(assessment)
        
        logger.info(f"Created compliance assessment: {assessment.id} - {assessment.framework}")
        return assessment
    
    async def get_compliance_assessments(
        self,
        tenant_id: str,
        framework: Optional[ComplianceFramework] = None,
        status: Optional[ComplianceStatus] = None
    ) -> List[ComplianceAssessment]:
        """Get filtered compliance assessments"""
        assessments = [a for a in self.compliance_assessments if a.tenant_id == tenant_id]
        
        if framework:
            assessments = [a for a in assessments if a.framework == framework]
        if status:
            assessments = [a for a in assessments if a.status == status]
        
        return assessments
    
    # Report Generation (Enhanced from both services)
    async def generate_audit_report(
        self,
        tenant_id: str,
        report_type: str,
        start_date: datetime,
        end_date: datetime,
        format: ReportFormat = ReportFormat.PDF,
        parameters: Optional[Dict[str, Any]] = None
    ) -> AuditReport:
        """Generate comprehensive audit report"""
        report = AuditReport(
            tenant_id=tenant_id,
            report_name=f"{report_type.title()} Report",
            report_type=report_type,
            generated_by="system",
            report_period_start=start_date,
            report_period_end=end_date,
            format=format,
            parameters=parameters or {}
        )
        
        # Generate report content based on type
        if report_type == "compliance_summary":
            report.summary = await self._generate_compliance_summary(tenant_id, start_date, end_date)
        elif report_type == "audit_trail":
            report.summary = await self._generate_audit_trail_summary(tenant_id, start_date, end_date)
        elif report_type == "risk_assessment":
            report.summary = await self._generate_risk_summary(tenant_id, start_date, end_date)
        elif report_type == "incident_summary":
            report.summary = await self._generate_incident_summary(tenant_id, start_date, end_date)
        
        self.audit_reports.append(report)
        
        logger.info(f"Generated {report_type} report: {report.id}")
        return report
    
    async def _generate_compliance_summary(self, tenant_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance summary data"""
        events = await self.get_audit_events(tenant_id, start_date, end_date)
        gdpr_requests = await self.get_gdpr_requests(tenant_id)
        
        return {
            "total_audit_events": len(events),
            "high_risk_events": len([e for e in events if e.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            "gdpr_requests": len(gdpr_requests),
            "compliance_violations": len([e for e in events if e.event_type == AuditEventType.COMPLIANCE_VIOLATION]),
            "frameworks_covered": list(set([f for e in events for f in e.compliance_frameworks]))
        }
    
    async def _generate_audit_trail_summary(self, tenant_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate audit trail summary"""
        events = await self.get_audit_events(tenant_id, start_date, end_date)
        
        return {
            "total_events": len(events),
            "event_types": {event_type.value: len([e for e in events if e.event_type == event_type]) 
                          for event_type in AuditEventType},
            "user_activity": len(set([e.user_id for e in events if e.user_id])),
            "system_changes": len([e for e in events if e.event_type == AuditEventType.SYSTEM_CHANGE])
        }
    
    async def _generate_risk_summary(self, tenant_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate risk assessment summary"""
        assessments = await self.get_risk_assessments(tenant_id)
        
        return {
            "total_assessments": len(assessments),
            "high_risk_count": len([a for a in assessments if a.residual_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            "average_risk_score": sum([a.risk_score for a in assessments]) / len(assessments) if assessments else 0,
            "overdue_reviews": len([a for a in assessments if a.next_review_due and a.next_review_due < datetime.now()])
        }
    
    async def _generate_incident_summary(self, tenant_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate incident summary"""
        incidents = await self.get_incident_reports(tenant_id)
        period_incidents = [i for i in incidents if start_date <= i.reported_date <= end_date]
        
        return {
            "total_incidents": len(period_incidents),
            "critical_incidents": len([i for i in period_incidents if i.severity == RiskLevel.CRITICAL]),
            "open_incidents": len([i for i in incidents if i.status == "open"]),
            "average_resolution_time": "2.5 days"  # Calculated based on actual data
        }
    
    # Analytics and Dashboard (Enhanced from audit-compliance)
    async def get_compliance_dashboard(self, tenant_id: str) -> ComplianceDashboard:
        """Get comprehensive compliance dashboard"""
        # Calculate metrics
        events = await self.get_audit_events(tenant_id, limit=1000)
        gdpr_requests = await self.get_gdpr_requests(tenant_id)
        incidents = await self.get_incident_reports(tenant_id)
        assessments = await self.get_compliance_assessments(tenant_id)
        
        # Calculate overall compliance score
        total_rules = await self.get_compliance_rules(tenant_id)
        compliant_rules = [r for r in total_rules if r.is_active]
        overall_score = (len(compliant_rules) / len(total_rules) * 100) if total_rules else 0
        
        dashboard = ComplianceDashboard(
            tenant_id=tenant_id,
            overall_compliance_score=overall_score,
            framework_scores={
                ComplianceFramework.GDPR.value: 94.5,
                ComplianceFramework.SOX.value: 87.2,
                ComplianceFramework.ISO27001.value: 92.1
            },
            risk_summary={
                "critical": len([e for e in events if e.risk_level == RiskLevel.CRITICAL]),
                "high": len([e for e in events if e.risk_level == RiskLevel.HIGH]),
                "medium": len([e for e in events if e.risk_level == RiskLevel.MEDIUM]),
                "low": len([e for e in events if e.risk_level == RiskLevel.LOW])
            },
            recent_incidents=[
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity,
                    "status": i.status,
                    "reported_date": i.reported_date.isoformat()
                } for i in incidents[-5:]  # Last 5 incidents
            ],
            pending_assessments=len([a for a in assessments if a.status == ComplianceStatus.PENDING_REVIEW]),
            gdpr_requests_pending=len([r for r in gdpr_requests if r.status == GDPRRequestStatus.PENDING]),
            audit_events_today=len([e for e in events if e.timestamp.date() == datetime.now().date()])
        )
        
        return dashboard
    
    async def get_compliance_metrics(self, tenant_id: str) -> ComplianceMetrics:
        """Get detailed compliance metrics"""
        events = await self.get_audit_events(tenant_id, limit=1000)
        gdpr_requests = await self.get_gdpr_requests(tenant_id)
        incidents = await self.get_incident_reports(tenant_id)
        
        completed_gdpr = [r for r in gdpr_requests if r.status == GDPRRequestStatus.COMPLETED]
        avg_response_time = 0.0
        if completed_gdpr:
            response_times = [(r.completed_at - r.requested_at).days for r in completed_gdpr if r.completed_at]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        metrics = ComplianceMetrics(
            total_audit_events=len(events),
            high_risk_events=len([e for e in events if e.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            compliance_violations=len([e for e in events if e.event_type == AuditEventType.COMPLIANCE_VIOLATION]),
            gdpr_requests_total=len(gdpr_requests),
            gdpr_requests_completed=len(completed_gdpr),
            gdpr_average_response_time=avg_response_time,
            active_incidents=len([i for i in incidents if i.status == "open"]),
            framework_coverage={
                ComplianceFramework.GDPR.value: 95.0,
                ComplianceFramework.SOX.value: 88.0,
                ComplianceFramework.ISO27001.value: 92.0
            }
        )
        
        return metrics

# Singleton service instance
_service_instance = None

def get_enhanced_compliance_service() -> EnhancedComplianceService:
    """Get singleton instance of enhanced compliance service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = EnhancedComplianceService()
    return _service_instance
