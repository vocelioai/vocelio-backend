# apps/call-center/src/schemas/call.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class CallStatus(str, Enum):
    QUEUED = "queued"
    RINGING = "ringing"
    ACTIVE = "active" 
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    TRANSFERRED = "transferred"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CallStage(str, Enum):
    OPENING = "opening"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"
    APPOINTMENT_BOOKING = "appointment_booking"
    PRICING_DISCUSSION = "pricing_discussion"
    INFORMATION_GATHERING = "information_gathering"

class CallPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Base schemas
class CustomerInfo(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = None
    age: Optional[int] = None
    interest: Optional[str] = None

class CampaignInfo(BaseModel):
    name: str
    type: str
    priority: str = "medium"

class AgentInfo(BaseModel):
    name: str
    type: str = "AI Agent"
    performance: float = 90.0
    voice_id: str = "professional_female"

class AIInsights(BaseModel):
    conversion_probability: float = Field(..., ge=0, le=100)
    next_best_action: str
    objections: List[str] = []
    sentiment: float = Field(..., ge=-1, le=1)

class TranscriptMessage(BaseModel):
    speaker: str = Field(..., regex="^(agent|customer|system)$")
    text: str
    timestamp: Optional[str] = None

# Request schemas
class CallCreate(BaseModel):
    customer_phone: str = Field(..., min_length=10, max_length=20)
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_location: Optional[str] = None
    customer_type: Optional[str] = None
    campaign_id: Optional[str] = None
    agent_id: Optional[str] = None
    priority: CallPriority = CallPriority.MEDIUM
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('customer_phone')
    def validate_phone(cls, v):
        # Basic phone validation
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return v

class CallUpdate(BaseModel):
    status: Optional[CallStatus] = None
    stage: Optional[CallStage] = None
    sentiment: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CallStatusUpdate(BaseModel):
    status: CallStatus
    stage: Optional[CallStage] = None
    sentiment: Optional[str] = None
    timestamp: Optional[datetime] = None

class CallTransferRequest(BaseModel):
    target_type: str = Field(..., regex="^(agent|human|queue)$")
    target_agent_id: Optional[str] = None
    reason: Optional[str] = None

class CallFilters(BaseModel):
    status: Optional[str] = None
    agent_name: Optional[str] = None
    industry: Optional[str] = None
    priority: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

# Response schemas
class CallResponse(BaseModel):
    id: str
    status: str
    customer_phone: str
    customer_info: CustomerInfo
    campaign: CampaignInfo
    agent: AgentInfo
    duration: str
    sentiment: str
    stage: str
    transcript: List[TranscriptMessage] = []
    ai_insights: AIInsights
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CallListResponse(BaseModel):
    calls: List[CallResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class LiveMetrics(BaseModel):
    active_calls: int = 0
    success_rate: float = 0.0
    total_agents: int = 0
    conversions_today: int = 0
    appointments_today: int = 0
    queued_calls: int = 0
    avg_wait_time: float = 0.0
    system_load: int = 0
    peak_time: str = "2:00-4:00 PM"
    global_coverage: Dict[str, int] = {}
    timestamp: Optional[datetime] = None

class SystemHealth(BaseModel):
    api_status: str = "operational"
    voice_services: str = "99.99%"
    ai_models: str = "optimal"
    call_routing: str = "normal"
    database_status: str = "healthy"
    active_services: int = 17
    total_capacity: str = "75%"
    last_updated: datetime

class ConversionFunnel(BaseModel):
    calls_initiated: int
    calls_answered: int
    calls_qualified: int
    calls_converted: int
    answer_rate: float
    qualification_rate: float
    conversion_rate: float

class CallOutcomes(BaseModel):
    appointments: float = 23.4
    follow_ups: float = 18.7
    callbacks: float = 12.3
    transfers: float = 8.9
    no_interest: float = 25.2
    other: float = 11.5

# Agent schemas
class AgentPerformance(BaseModel):
    name: str
    specialty: str
    performance: float
    calls_today: int
    status: str = "active"

# Recording schemas  
class CallRecordingResponse(BaseModel):
    id: str
    call_id: str
    recording_url: str
    recording_status: str
    duration: Optional[int] = None
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    transcription_status: Optional[str] = None
    transcription_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# Webhook schemas
class TwilioCallStatus(BaseModel):
    CallSid: str
    AccountSid: str
    From: str
    To: str
    CallStatus: str
    Direction: str
    ForwardedFrom: Optional[str] = None
    CallerName: Optional[str] = None
    Duration: Optional[str] = None
    RecordingUrl: Optional[str] = None
    RecordingSid: Optional[str] = None
    Timestamp: Optional[str] = None

class TwilioRecordingStatus(BaseModel):
    RecordingSid: str
    CallSid: str
    AccountSid: str
    RecordingUrl: str
    RecordingStatus: str
    RecordingDuration: Optional[str] = None
    RecordingChannels: Optional[str] = None
    RecordingSource: Optional[str] = None

# Analytics schemas
class CallAnalytics(BaseModel):
    total_calls: int
    active_calls: int
    completed_calls: int
    success_rate: float
    average_duration: float
    total_revenue: float
    top_outcomes: Dict[str, int]
    hourly_volume: List[Dict[str, Any]]
    agent_performance: List[AgentPerformance]

class RealtimeUpdate(BaseModel):
    type: str  # metrics_update, call_update, system_update, agent_update
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None

class CallEventUpdate(BaseModel):
    call_id: str
    event_type: str  # started, ended, transferred, updated
    status: CallStatus
    stage: Optional[CallStage] = None
    data: Dict[str, Any] = {}
    timestamp: datetime

# Export schemas
class ExportRequest(BaseModel):
    format_type: str = Field(..., regex="^(json|csv|excel)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    filters: Optional[CallFilters] = None
    include_transcript: bool = False
    include_recordings: bool = False

class ExportResponse(BaseModel):
    export_id: str
    status: str = "processing"
    format_type: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

# Error schemas
class CallError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    call_id: Optional[str] = None

# Batch operation schemas
class BatchCallOperation(BaseModel):
    operation: str = Field(..., regex="^(end|transfer|update_status)$")
    call_ids: List[str] = Field(..., min_items=1, max_items=100)
    parameters: Optional[Dict[str, Any]] = None

class BatchOperationResult(BaseModel):
    operation: str
    total_calls: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[CallError] = []

# Search schemas
class CallSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    filters: Optional[CallFilters] = None
    search_fields: List[str] = ["customer_name", "customer_phone", "transcript"]
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

class CallSearchResult(BaseModel):
    calls: List[CallResponse]
    total_matches: int
    search_time_ms: int
    query: str
    suggested_queries: List[str] = []

# Statistics schemas
class CallStatistics(BaseModel):
    date_range: Dict[str, datetime]
    total_calls: int
    total_duration_seconds: int
    average_duration_seconds: float
    success_rate: float
    conversion_rate: float
    revenue_generated: float
    by_status: Dict[str, int]
    by_outcome: Dict[str, int]
    by_agent: List[Dict[str, Any]]
    by_campaign: List[Dict[str, Any]]
    by_hour: List[Dict[str, Any]]
    by_day: List[Dict[str, Any]]

# Quality monitoring schemas
class CallQualityMetrics(BaseModel):
    call_id: str
    audio_quality_score: float = Field(..., ge=0, le=100)
    transcript_accuracy: float = Field(..., ge=0, le=100)
    agent_performance_score: float = Field(..., ge=0, le=100)
    customer_satisfaction_score: Optional[float] = Field(None, ge=0, le=100)
    compliance_score: float = Field(..., ge=0, le=100)
    overall_quality_score: float = Field(..., ge=0, le=100)
    quality_issues: List[str] = []
    recommendations: List[str] = []

# Compliance schemas
class ComplianceCheck(BaseModel):
    call_id: str
    dnc_status: str = "checked"  # checked, not_checked, exempt
    consent_status: str = "obtained"  # obtained, not_obtained, not_required
    recording_consent: bool = False
    timezone_compliance: bool = True
    script_compliance: bool = True
    data_retention_policy: str = "standard"
    compliance_score: float = Field(..., ge=0, le=100)
    violations: List[str] = []
    notes: Optional[str] = None

# Integration schemas
class CRMIntegration(BaseModel):
    call_id: str
    crm_system: str  # salesforce, hubspot, pipedrive, etc.
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    sync_status: str = "pending"  # pending, synced, failed
    last_sync_at: Optional[datetime] = None
    sync_errors: List[str] = []

# Notification schemas
class CallNotification(BaseModel):
    type: str  # high_value_prospect, conversion_opportunity, escalation_needed
    call_id: str
    priority: str = "medium"  # low, medium, high, urgent
    title: str
    message: str
    action_required: bool = False
    suggested_actions: List[str] = []
    expires_at: Optional[datetime] = None
    created_at: datetime

# Performance monitoring schemas
class ServiceMetrics(BaseModel):
    service_name: str = "call-center"
    version: str = "1.0.0"
    uptime_seconds: int
    active_connections: int
    requests_per_second: float
    average_response_time_ms: float
    error_rate: float
    memory_usage_mb: int
    cpu_usage_percent: float
    database_connections: int
    cache_hit_rate: float
    last_updated: datetime

# Configuration schemas
class CallCenterConfig(BaseModel):
    max_concurrent_calls: int = 10000
    default_recording_enabled: bool = True
    auto_transcription_enabled: bool = True
    ai_insights_enabled: bool = True
    real_time_monitoring: bool = True
    compliance_checks_enabled: bool = True
    quality_monitoring_sample_rate: float = Field(0.1, ge=0, le=1)
    retention_days: int = 365
    timezone: str = "UTC"
    emergency_stop_enabled: bool = True