"""
Audit Compliance Service - Vocelio AI Enterprise Platform
Enterprise Audit, Compliance, Risk Management, and Regulatory Reporting
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import csv
import io
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

# Compliance & Audit Models
class ComplianceFramework(str, Enum):
    SOX = "sox"  # Sarbanes-Oxley
    GDPR = "gdpr"  # General Data Protection Regulation
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    ISO27001 = "iso27001"  # Information Security Management
    NIST = "nist"  # National Institute of Standards and Technology
    FISMA = "fisma"  # Federal Information Security Management Act
    CCPA = "ccpa"  # California Consumer Privacy Act
    FERPA = "ferpa"  # Family Educational Rights and Privacy Act
    GLBA = "glba"  # Gramm-Leach-Bliley Act
    COSO = "coso"  # Committee of Sponsoring Organizations
    COBIT = "cobit"  # Control Objectives for Information and Related Technologies

class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class AuditEventType(str, Enum):
    USER_ACCESS = "user_access"
    DATA_ACCESS = "data_access"
    SYSTEM_CHANGE = "system_change"
    CONFIGURATION_CHANGE = "configuration_change"
    POLICY_CHANGE = "policy_change"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_VIOLATION = "compliance_violation"
    DATA_EXPORT = "data_export"
    PRIVILEGED_ACCESS = "privileged_access"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    FILE_ACCESS = "file_access"
    DATABASE_ACCESS = "database_access"
    API_ACCESS = "api_access"
    ADMIN_ACTION = "admin_action"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REMEDIATION_REQUIRED = "remediation_required"
    EXEMPTED = "exempted"
    NOT_APPLICABLE = "not_applicable"

class ControlType(str, Enum):
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATING = "compensating"
    DIRECTIVE = "directive"

class ReportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"
    HTML = "html"

class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    event_type: AuditEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    resource_type: str
    resource_id: Optional[str] = None
    action: str
    outcome: str  # success, failure, partial
    ip_address: str
    user_agent: str
    location: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    compliance_frameworks: List[ComplianceFramework] = []
    sensitive_data_involved: bool = False
    data_classification: Optional[str] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    details: Dict[str, Any] = {}
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    retention_period_days: int = 2555  # 7 years default
    is_archived: bool = False
    archived_at: Optional[datetime] = None

class ComplianceRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    framework: ComplianceFramework
    control_id: str
    control_name: str
    control_description: str
    control_type: ControlType
    risk_level: RiskLevel
    is_active: bool = True
    automation_enabled: bool = False
    monitoring_frequency: str = "daily"  # real-time, hourly, daily, weekly, monthly
    evaluation_criteria: Dict[str, Any] = {}
    remediation_steps: List[str] = []
    responsible_party: Optional[str] = None
    evidence_requirements: List[str] = []
    testing_procedures: List[str] = []
    last_tested: Optional[datetime] = None
    next_test_due: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ComplianceAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    framework: ComplianceFramework
    assessment_name: str
    assessment_description: Optional[str] = None
    assessor_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    scope: List[str] = []  # systems, processes, controls in scope
    findings: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []
    overall_score: Optional[float] = None
    risk_rating: RiskLevel = RiskLevel.MEDIUM
    certification_body: Optional[str] = None
    certificate_number: Optional[str] = None
    certificate_valid_until: Optional[datetime] = None
    remediation_plan: List[Dict[str, Any]] = []
    evidence_collected: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RiskAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    risk_name: str
    risk_description: str
    risk_category: str
    inherent_risk_level: RiskLevel
    residual_risk_level: RiskLevel
    likelihood: int = Field(ge=1, le=5)  # 1-5 scale
    impact: int = Field(ge=1, le=5)  # 1-5 scale
    risk_score: float = Field(ge=0.0, le=25.0)
    mitigation_controls: List[str] = []
    risk_owner: str
    review_frequency: str = "quarterly"
    last_reviewed: Optional[datetime] = None
    next_review_due: Optional[datetime] = None
    treatment_strategy: str  # accept, mitigate, transfer, avoid
    monitoring_indicators: List[str] = []
    related_incidents: List[str] = []
    regulatory_impact: List[ComplianceFramework] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IncidentReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    incident_type: str
    severity: RiskLevel
    title: str
    description: str
    discovered_date: datetime
    reported_date: datetime = Field(default_factory=datetime.utcnow)
    reported_by: str
    affected_systems: List[str] = []
    affected_users: List[str] = []
    data_involved: bool = False
    personal_data_involved: bool = False
    estimated_records_affected: Optional[int] = None
    root_cause: Optional[str] = None
    impact_assessment: str
    containment_actions: List[str] = []
    remediation_actions: List[str] = []
    lessons_learned: Optional[str] = None
    regulatory_notifications_required: List[ComplianceFramework] = []
    regulatory_notifications_sent: List[Dict[str, Any]] = []
    status: str = "open"  # open, investigating, contained, resolved, closed
    resolution_date: Optional[datetime] = None
    assignee: Optional[str] = None
    related_audit_events: List[str] = []

class AuditReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    report_name: str
    report_type: str
    framework: Optional[ComplianceFramework] = None
    reporting_period_start: datetime
    reporting_period_end: datetime
    generated_by: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    report_format: ReportFormat
    executive_summary: Optional[str] = None
    key_findings: List[str] = []
    recommendations: List[str] = []
    compliance_score: Optional[float] = None
    risk_summary: Dict[str, Any] = {}
    control_effectiveness: Dict[str, Any] = {}
    trend_analysis: Dict[str, Any] = {}
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    recipients: List[str] = []
    distribution_date: Optional[datetime] = None

class DataRetentionPolicy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    policy_name: str
    data_type: str
    retention_period_days: int
    applicable_frameworks: List[ComplianceFramework] = []
    legal_hold_override: bool = False
    archive_after_days: Optional[int] = None
    purge_method: str = "secure_delete"
    approval_required: bool = False
    approver_roles: List[str] = []
    exceptions: List[Dict[str, Any]] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: Optional[datetime] = None

# In-memory storage (replace with proper database in production)
audit_events_db: List[AuditEvent] = []
compliance_rules_db: Dict[str, ComplianceRule] = {}
assessments_db: Dict[str, ComplianceAssessment] = {}
risk_assessments_db: Dict[str, RiskAssessment] = {}
incident_reports_db: Dict[str, IncidentReport] = {}
audit_reports_db: Dict[str, AuditReport] = {}
retention_policies_db: Dict[str, DataRetentionPolicy] = {}

# Utility functions
def calculate_risk_score(likelihood: int, impact: int) -> float:
    """Calculate risk score based on likelihood and impact"""
    return likelihood * impact

def determine_risk_level(risk_score: float) -> RiskLevel:
    """Determine risk level based on score"""
    if risk_score >= 20:
        return RiskLevel.CRITICAL
    elif risk_score >= 15:
        return RiskLevel.HIGH
    elif risk_score >= 10:
        return RiskLevel.MEDIUM
    elif risk_score >= 5:
        return RiskLevel.LOW
    else:
        return RiskLevel.NEGLIGIBLE

def evaluate_compliance_rule(rule: ComplianceRule, audit_events: List[AuditEvent]) -> ComplianceStatus:
    """Evaluate compliance rule against audit events"""
    # Simplified evaluation logic - in production this would be more sophisticated
    relevant_events = [
        event for event in audit_events
        if rule.framework in event.compliance_frameworks
    ]
    
    if not relevant_events:
        return ComplianceStatus.NOT_APPLICABLE
    
    # Check for any compliance violations
    violations = [
        event for event in relevant_events
        if event.event_type == AuditEventType.COMPLIANCE_VIOLATION
    ]
    
    if violations:
        return ComplianceStatus.NON_COMPLIANT
    
    return ComplianceStatus.COMPLIANT

def generate_audit_report_content(
    tenant_id: str,
    framework: Optional[ComplianceFramework],
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Generate audit report content"""
    # Filter events by time period and tenant
    period_events = [
        event for event in audit_events_db
        if (event.tenant_id == tenant_id and
            start_date <= event.timestamp <= end_date and
            (not framework or framework in event.compliance_frameworks))
    ]
    
    # Generate statistics
    total_events = len(period_events)
    risk_distribution = {}
    for risk_level in RiskLevel:
        risk_distribution[risk_level.value] = len([
            e for e in period_events if e.risk_level == risk_level
        ])
    
    event_type_distribution = {}
    for event_type in AuditEventType:
        event_type_distribution[event_type.value] = len([
            e for e in period_events if e.event_type == event_type
        ])
    
    return {
        "total_events": total_events,
        "risk_distribution": risk_distribution,
        "event_type_distribution": event_type_distribution,
        "high_risk_events": [
            e.dict() for e in period_events 
            if e.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
        ][:10],  # Top 10 high-risk events
        "compliance_violations": [
            e.dict() for e in period_events
            if e.event_type == AuditEventType.COMPLIANCE_VIOLATION
        ],
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat()
    }

# Mock authentication (replace with actual SSO integration)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"id": "user-123", "tenant_id": "tenant-123", "roles": ["admin"]}

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Audit Compliance Service starting up...")
    
    # Create default compliance rules
    default_rules = [
        ComplianceRule(
            id="gdpr-data-access",
            tenant_id="tenant-123",
            framework=ComplianceFramework.GDPR,
            control_id="GDPR-32",
            control_name="Data Access Logging",
            control_description="All access to personal data must be logged",
            control_type=ControlType.DETECTIVE,
            risk_level=RiskLevel.HIGH
        ),
        ComplianceRule(
            id="sox-financial-controls",
            tenant_id="tenant-123",
            framework=ComplianceFramework.SOX,
            control_id="SOX-404",
            control_name="Financial System Access Controls",
            control_description="Controls over financial system access",
            control_type=ControlType.PREVENTIVE,
            risk_level=RiskLevel.CRITICAL
        )
    ]
    
    for rule in default_rules:
        compliance_rules_db[rule.id] = rule
    
    yield
    
    # Shutdown
    logger.info("Audit Compliance Service shutting down...")

# FastAPI app
app = FastAPI(
    title="Vocelio Audit Compliance Service",
    description="Enterprise Audit, Compliance, Risk Management, and Regulatory Reporting",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "audit-compliance",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Audit Event endpoints
@app.post("/audit-events", response_model=AuditEvent)
async def create_audit_event(
    event: AuditEvent,
    current_user: dict = Depends(get_current_user)
):
    """Create a new audit event"""
    event.tenant_id = current_user["tenant_id"]
    audit_events_db.append(event)
    
    # Check for compliance violations
    for rule in compliance_rules_db.values():
        if (rule.tenant_id == event.tenant_id and 
            rule.framework in event.compliance_frameworks):
            # Evaluate rule against event (simplified)
            if event.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                logger.warning(f"High-risk event detected: {event.id}")
    
    return event

@app.get("/audit-events", response_model=List[AuditEvent])
async def get_audit_events(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[AuditEventType] = None,
    risk_level: Optional[RiskLevel] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get audit events with filtering"""
    tenant_events = [e for e in audit_events_db if e.tenant_id == current_user["tenant_id"]]
    
    # Apply filters
    if event_type:
        tenant_events = [e for e in tenant_events if e.event_type == event_type]
    if risk_level:
        tenant_events = [e for e in tenant_events if e.risk_level == risk_level]
    if start_date:
        tenant_events = [e for e in tenant_events if e.timestamp >= start_date]
    if end_date:
        tenant_events = [e for e in tenant_events if e.timestamp <= end_date]
    if user_id:
        tenant_events = [e for e in tenant_events if e.user_id == user_id]
    
    # Sort by timestamp (newest first)
    tenant_events.sort(key=lambda x: x.timestamp, reverse=True)
    
    return tenant_events[skip:skip + limit]

@app.get("/audit-events/{event_id}", response_model=AuditEvent)
async def get_audit_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific audit event"""
    event = next((e for e in audit_events_db 
                 if e.id == event_id and e.tenant_id == current_user["tenant_id"]), None)
    if not event:
        raise HTTPException(status_code=404, detail="Audit event not found")
    return event

# Compliance Rules endpoints
@app.get("/compliance-rules", response_model=List[ComplianceRule])
async def get_compliance_rules(
    framework: Optional[ComplianceFramework] = None,
    is_active: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get compliance rules"""
    tenant_rules = [r for r in compliance_rules_db.values() 
                   if r.tenant_id == current_user["tenant_id"]]
    
    if framework:
        tenant_rules = [r for r in tenant_rules if r.framework == framework]
    if is_active is not None:
        tenant_rules = [r for r in tenant_rules if r.is_active == is_active]
    
    return tenant_rules

@app.post("/compliance-rules", response_model=ComplianceRule)
async def create_compliance_rule(
    rule: ComplianceRule,
    current_user: dict = Depends(get_current_user)
):
    """Create new compliance rule"""
    rule.tenant_id = current_user["tenant_id"]
    compliance_rules_db[rule.id] = rule
    return rule

@app.put("/compliance-rules/{rule_id}", response_model=ComplianceRule)
async def update_compliance_rule(
    rule_id: str,
    rule_update: ComplianceRule,
    current_user: dict = Depends(get_current_user)
):
    """Update compliance rule"""
    existing_rule = compliance_rules_db.get(rule_id)
    if not existing_rule or existing_rule.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="Compliance rule not found")
    
    rule_update.tenant_id = current_user["tenant_id"]
    rule_update.updated_at = datetime.utcnow()
    compliance_rules_db[rule_id] = rule_update
    return rule_update

# Risk Assessment endpoints
@app.get("/risk-assessments", response_model=List[RiskAssessment])
async def get_risk_assessments(
    current_user: dict = Depends(get_current_user)
):
    """Get risk assessments for tenant"""
    return [r for r in risk_assessments_db.values() 
           if r.tenant_id == current_user["tenant_id"]]

@app.post("/risk-assessments", response_model=RiskAssessment)
async def create_risk_assessment(
    risk: RiskAssessment,
    current_user: dict = Depends(get_current_user)
):
    """Create new risk assessment"""
    risk.tenant_id = current_user["tenant_id"]
    risk.risk_score = calculate_risk_score(risk.likelihood, risk.impact)
    risk.residual_risk_level = determine_risk_level(risk.risk_score)
    risk_assessments_db[risk.id] = risk
    return risk

@app.put("/risk-assessments/{risk_id}", response_model=RiskAssessment)
async def update_risk_assessment(
    risk_id: str,
    risk_update: RiskAssessment,
    current_user: dict = Depends(get_current_user)
):
    """Update risk assessment"""
    existing_risk = risk_assessments_db.get(risk_id)
    if not existing_risk or existing_risk.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    
    risk_update.tenant_id = current_user["tenant_id"]
    risk_update.risk_score = calculate_risk_score(risk_update.likelihood, risk_update.impact)
    risk_update.residual_risk_level = determine_risk_level(risk_update.risk_score)
    risk_update.updated_at = datetime.utcnow()
    risk_assessments_db[risk_id] = risk_update
    return risk_update

# Incident Report endpoints
@app.get("/incident-reports", response_model=List[IncidentReport])
async def get_incident_reports(
    status: Optional[str] = None,
    severity: Optional[RiskLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get incident reports"""
    tenant_incidents = [i for i in incident_reports_db.values() 
                       if i.tenant_id == current_user["tenant_id"]]
    
    if status:
        tenant_incidents = [i for i in tenant_incidents if i.status == status]
    if severity:
        tenant_incidents = [i for i in tenant_incidents if i.severity == severity]
    
    return tenant_incidents

@app.post("/incident-reports", response_model=IncidentReport)
async def create_incident_report(
    incident: IncidentReport,
    current_user: dict = Depends(get_current_user)
):
    """Create new incident report"""
    incident.tenant_id = current_user["tenant_id"]
    incident.reported_by = current_user["id"]
    incident_reports_db[incident.id] = incident
    return incident

# Compliance Assessment endpoints
@app.get("/compliance-assessments", response_model=List[ComplianceAssessment])
async def get_compliance_assessments(
    framework: Optional[ComplianceFramework] = None,
    status: Optional[ComplianceStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get compliance assessments"""
    tenant_assessments = [a for a in assessments_db.values() 
                         if a.tenant_id == current_user["tenant_id"]]
    
    if framework:
        tenant_assessments = [a for a in tenant_assessments if a.framework == framework]
    if status:
        tenant_assessments = [a for a in tenant_assessments if a.status == status]
    
    return tenant_assessments

@app.post("/compliance-assessments", response_model=ComplianceAssessment)
async def create_compliance_assessment(
    assessment: ComplianceAssessment,
    current_user: dict = Depends(get_current_user)
):
    """Create new compliance assessment"""
    assessment.tenant_id = current_user["tenant_id"]
    assessment.assessor_id = current_user["id"]
    assessments_db[assessment.id] = assessment
    return assessment

# Audit Reports endpoints
@app.get("/audit-reports", response_model=List[AuditReport])
async def get_audit_reports(
    current_user: dict = Depends(get_current_user)
):
    """Get audit reports for tenant"""
    return [r for r in audit_reports_db.values() 
           if r.tenant_id == current_user["tenant_id"]]

@app.post("/audit-reports/generate")
async def generate_audit_report(
    report_name: str,
    report_type: str,
    start_date: datetime,
    end_date: datetime,
    framework: Optional[ComplianceFramework] = None,
    report_format: ReportFormat = ReportFormat.PDF,
    current_user: dict = Depends(get_current_user)
):
    """Generate new audit report"""
    report_content = generate_audit_report_content(
        current_user["tenant_id"], framework, start_date, end_date
    )
    
    report = AuditReport(
        tenant_id=current_user["tenant_id"],
        report_name=report_name,
        report_type=report_type,
        framework=framework,
        reporting_period_start=start_date,
        reporting_period_end=end_date,
        generated_by=current_user["id"],
        report_format=report_format,
        key_findings=report_content.get("compliance_violations", []),
        compliance_score=85.5,  # Mock score
        risk_summary=report_content["risk_distribution"],
        trend_analysis=report_content["event_type_distribution"]
    )
    
    audit_reports_db[report.id] = report
    return {"report_id": report.id, "status": "generated", "content": report_content}

# Analytics endpoints
@app.get("/analytics/compliance-dashboard")
async def get_compliance_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get compliance dashboard analytics"""
    tenant_id = current_user["tenant_id"]
    
    # Get recent events (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_events = [e for e in audit_events_db 
                    if e.tenant_id == tenant_id and e.timestamp >= thirty_days_ago]
    
    # Calculate metrics
    total_events = len(recent_events)
    high_risk_events = len([e for e in recent_events 
                           if e.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]])
    compliance_violations = len([e for e in recent_events 
                               if e.event_type == AuditEventType.COMPLIANCE_VIOLATION])
    
    # Compliance score (mock calculation)
    compliance_score = max(0, 100 - (compliance_violations * 10))
    
    # Risk trend (mock data)
    risk_trend = [
        {"date": (datetime.utcnow() - timedelta(days=i)).date().isoformat(), 
         "risk_score": max(1, 25 - i)} 
        for i in range(30, 0, -1)
    ]
    
    return {
        "total_events_30_days": total_events,
        "high_risk_events_30_days": high_risk_events,
        "compliance_violations_30_days": compliance_violations,
        "compliance_score": compliance_score,
        "risk_trend": risk_trend,
        "top_risk_areas": [
            {"area": "Data Access", "risk_score": 8.5},
            {"area": "System Changes", "risk_score": 6.2},
            {"area": "Privileged Access", "risk_score": 5.8}
        ],
        "compliance_by_framework": {
            framework.value: len([r for r in compliance_rules_db.values() 
                                if r.framework == framework and r.tenant_id == tenant_id])
            for framework in ComplianceFramework
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
