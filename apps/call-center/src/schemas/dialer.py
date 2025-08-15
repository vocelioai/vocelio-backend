# apps/call-center/src/schemas/dialer.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DialerMode(str, Enum):
    PREDICTIVE = "predictive"
    PROGRESSIVE = "progressive"
    PREVIEW = "preview"
    MANUAL = "manual"

class DialerState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"

class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    SCHEDULED = "scheduled"

# Base schemas
class DialerConfig(BaseModel):
    mode: DialerMode
    campaign_id: str
    max_concurrent_calls: int = Field(10, ge=1, le=100)
    dial_ratio: float = Field(1.5, ge=1.0, le=5.0)
    answer_delay: int = Field(2, ge=0, le=10)
    retry_attempts: int = Field(3, ge=1, le=5)
    retry_interval: int = Field(300, ge=60, le=3600)  # seconds
    caller_id: Optional[str] = None
    recording_enabled: bool = True
    transcription_enabled: bool = True
    filters: Optional[Dict[str, Any]] = None

class DialerStatus(BaseModel):
    session_id: str
    state: DialerState
    mode: DialerMode
    campaign_id: str
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    total_calls: int = 0
    active_calls: int = 0
    completed_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    current_dial_ratio: float = 1.0
    estimated_completion: Optional[datetime] = None

class DialerMetrics(BaseModel):
    session_id: Optional[str] = None
    period: str
    total_calls_attempted: int = 0
    total_calls_connected: int = 0
    total_calls_answered: int = 0
    total_calls_voicemail: int = 0
    total_calls_busy: int = 0
    total_calls_no_answer: int = 0
    total_calls_failed: int = 0
    connection_rate: float = 0.0
    answer_rate: float = 0.0
    conversion_rate: float = 0.0
    average_call_duration: float = 0.0
    average_wait_time: float = 0.0
    leads_contacted: int = 0
    appointments_set: int = 0
    sales_made: int = 0
    revenue_generated: float = 0.0

class DialerModeUpdate(BaseModel):
    mode: DialerMode
    session_id: Optional[str] = None
    dial_ratio: Optional[float] = Field(None, ge=1.0, le=5.0)
    max_concurrent_calls: Optional[int] = Field(None, ge=1, le=100)

class CampaignConfig(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: CampaignStatus = CampaignStatus.ACTIVE
    lead_list_id: str
    script_id: Optional[str] = None
    caller_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    daily_call_limit: Optional[int] = Field(None, ge=1, le=10000)
    hours_of_operation: Optional[Dict[str, Any]] = None
    time_zone: str = "UTC"
    priority: int = Field(5, ge=1, le=10)
    auto_start: bool = False
    recording_enabled: bool = True
    transcription_enabled: bool = True
    compliance_settings: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    @validator('hours_of_operation')
    def validate_hours(cls, v):
        if v is None:
            return v
        
        required_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in required_days:
            if day not in v:
                v[day] = {"enabled": False}
            elif 'enabled' not in v[day]:
                v[day]['enabled'] = False
        
        return v

class LeadRecord(BaseModel):
    id: str
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    status: str = "new"
    priority: int = 5
    attempts: int = 0
    last_contacted: Optional[datetime] = None
    next_contact: Optional[datetime] = None
    timezone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DialerEvent(BaseModel):
    event_type: str
    session_id: str
    call_id: Optional[str] = None
    lead_id: Optional[str] = None
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None

# Response models
class DialerSessionResponse(BaseModel):
    session_id: str
    status: DialerStatus
    config: DialerConfig
    metrics: DialerMetrics

class CampaignListResponse(BaseModel):
    campaigns: List[CampaignConfig]
    total: int
    page: int
    limit: int
