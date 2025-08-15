# apps/compliance/src/models/enhanced_compliance.py
"""
Enhanced Compliance Models - Unified compliance and audit models
Combines structured compliance with comprehensive audit capabilities
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# Enhanced Enums from audit-compliance
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
    FCC_PART_64 = "fcc_part_64"  # Telecom compliance
    EPRIVACY = "eprivacy"  # EU ePrivacy Directive
    CRTC = "crtc"  # Canadian telecom regulations

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
    CALL_RECORDING_ACCESS = "call_recording_access"  # From compliance service
    GDPR_REQUEST = "gdpr_request"  # From compliance service
    TELECOM_COMPLIANCE = "telecom_compliance"  # From compliance service

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

class GDPRRequestType(str, Enum):
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    DATA_RECTIFICATION = "data_rectification"
    DATA_PORTABILITY = "data_portability"
    PROCESSING_RESTRICTION = "processing_restriction"
    RIGHT_TO_OBJECT = "right_to_object"

class GDPRRequestStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"

# Enhanced Models
class EnhancedAuditEvent(BaseModel):
    """Enhanced audit event combining both service capabilities"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
    event_type: AuditEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    session_id: Optional[str] = None
    resource_type: str
    resource_id: Optional[str] = None
    action: str
    outcome: str = "success"  # success, failure, partial
    ip_address: str
    user_agent: str
    location: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    compliance_frameworks: List[ComplianceFramework] = []
    compliance_flags: List[str] = []  # From compliance service
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
    """Enhanced compliance rule management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
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
    jurisdiction: Optional[str] = None  # From telecom regulations
    requirements: List[str] = []  # From telecom compliance
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GDPRRequest(BaseModel):
    """Enhanced GDPR request management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
    request_type: GDPRRequestType
    customer_email: EmailStr
    customer_id: Optional[str] = None
    status: GDPRRequestStatus = GDPRRequestStatus.PENDING
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    data_types: List[str] = []
    data_categories: List[str] = []
    legal_basis: Optional[str] = None
    rejection_reason: Optional[str] = None
    export_format: Optional[ReportFormat] = None
    download_url: Optional[str] = None
    download_expires_at: Optional[datetime] = None
    verification_method: Optional[str] = None
    verification_completed: bool = False
    estimated_completion: Optional[datetime] = None
    progress_notes: List[str] = []
    affected_systems: List[str] = []
    data_volume_estimate: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ComplianceAssessment(BaseModel):
    """Enhanced compliance assessment"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
    framework: ComplianceFramework
    assessment_name: str
    assessment_description: Optional[str] = None
    assessor_id: str
    assessor_name: Optional[str] = None
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
    compliance_percentage: Optional[float] = None
    non_compliance_issues: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RiskAssessment(BaseModel):
    """Enhanced risk assessment management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
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
    risk_owner_email: Optional[EmailStr] = None
    review_frequency: str = "quarterly"
    last_reviewed: Optional[datetime] = None
    next_review_due: Optional[datetime] = None
    treatment_strategy: str  # accept, mitigate, transfer, avoid
    monitoring_indicators: List[str] = []
    related_incidents: List[str] = []
    regulatory_impact: List[ComplianceFramework] = []
    business_impact: Optional[str] = None
    financial_impact: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IncidentReport(BaseModel):
    """Enhanced incident reporting"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
    incident_type: str
    severity: RiskLevel
    title: str
    description: str
    discovered_date: datetime
    reported_date: datetime = Field(default_factory=datetime.utcnow)
    reported_by: str
    reported_by_email: Optional[EmailStr] = None
    affected_systems: List[str] = []
    affected_users: List[str] = []
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    lessons_learned: List[str] = []
    preventive_measures: List[str] = []
    incident_commander: Optional[str] = None
    status: str = "open"  # open, investigating, resolved, closed
    priority: str = "medium"  # low, medium, high, critical
    estimated_resolution: Optional[datetime] = None
    actual_resolution: Optional[datetime] = None
    communication_log: List[Dict[str, Any]] = []
    evidence_collected: List[str] = []
    regulatory_notifications: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AuditReport(BaseModel):
    """Enhanced audit report generation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
    report_name: str
    report_type: str  # compliance_summary, audit_trail, risk_assessment, incident_summary
    framework: Optional[ComplianceFramework] = None
    generated_by: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    report_period_start: datetime
    report_period_end: datetime
    format: ReportFormat = ReportFormat.PDF
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    parameters: Dict[str, Any] = {}
    summary: Dict[str, Any] = {}
    recipient_emails: List[EmailStr] = []
    distribution_list: List[str] = []
    confidentiality_level: str = "internal"  # public, internal, confidential, restricted
    retention_period_days: int = 2555  # 7 years default
    download_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TelecomRegulation(BaseModel):
    """Telecom-specific compliance requirements"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jurisdiction: str  # US, EU, CA, etc.
    regulation_name: str
    regulation_code: str  # FCC Part 64, ePrivacy Directive, etc.
    description: str
    requirements: List[str] = []
    compliance_status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    last_assessment: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    responsible_party: Optional[str] = None
    documentation_links: List[str] = []
    implementation_notes: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RecordingConsent(BaseModel):
    """Call recording consent management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    organization_id: Optional[str] = None
    customer_phone: str
    customer_email: Optional[EmailStr] = None
    consent_given: bool
    consent_method: str  # verbal, written, digital, implied
    consent_timestamp: datetime
    recording_purpose: str
    jurisdiction: str
    legal_basis: str
    consent_language: str = "en"
    withdrawal_method: Optional[str] = None
    withdrawn_at: Optional[datetime] = None
    retention_period: int = 2555  # days
    auto_delete_date: Optional[datetime] = None
    call_id: Optional[str] = None
    agent_id: Optional[str] = None
    campaign_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Response Models
class ComplianceDashboard(BaseModel):
    """Enhanced compliance dashboard data"""
    tenant_id: str
    organization_id: Optional[str] = None
    overall_compliance_score: float
    framework_scores: Dict[str, float] = {}
    risk_summary: Dict[str, int] = {}
    recent_incidents: List[Dict[str, Any]] = []
    pending_assessments: int = 0
    overdue_reviews: int = 0
    gdpr_requests_pending: int = 0
    audit_events_today: int = 0
    compliance_trends: Dict[str, List[float]] = {}
    top_risks: List[Dict[str, Any]] = []
    remediation_status: Dict[str, int] = {}
    certification_status: List[Dict[str, Any]] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ComplianceMetrics(BaseModel):
    """Key compliance metrics"""
    total_audit_events: int = 0
    high_risk_events: int = 0
    compliance_violations: int = 0
    gdpr_requests_total: int = 0
    gdpr_requests_completed: int = 0
    gdpr_average_response_time: float = 0.0
    active_incidents: int = 0
    overdue_assessments: int = 0
    compliance_score_trend: List[float] = []
    framework_coverage: Dict[str, float] = {}
    risk_mitigation_rate: float = 0.0
    audit_coverage_percentage: float = 0.0
