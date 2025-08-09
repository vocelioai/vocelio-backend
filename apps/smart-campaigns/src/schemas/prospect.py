# apps/smart-campaigns/src/schemas/prospect.py
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from core.config import ProspectStatus

class ProspectStatusEnum(str, Enum):
    NEW = ProspectStatus.NEW
    CONTACTED = ProspectStatus.CONTACTED
    ANSWERED = ProspectStatus.ANSWERED
    NO_ANSWER = ProspectStatus.NO_ANSWER
    BUSY = ProspectStatus.BUSY
    VOICEMAIL = ProspectStatus.VOICEMAIL
    DISCONNECTED = ProspectStatus.DISCONNECTED
    CALLBACK_REQUESTED = ProspectStatus.CALLBACK_REQUESTED
    DO_NOT_CALL = ProspectStatus.DO_NOT_CALL
    CONVERTED = ProspectStatus.CONVERTED
    FAILED = ProspectStatus.FAILED

class ProspectPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Base Schemas
class ProspectBase(BaseModel):
    """Base prospect schema"""
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone_number: str = Field(..., min_length=10, max_length=20, description="Phone number (required)")
    
    # Professional information
    company: Optional[str] = Field(None, max_length=255, description="Company name")
    job_title: Optional[str] = Field(None, max_length=255, description="Job title")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    
    # Address information
    address_line1: Optional[str] = Field(None, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    zip_code: Optional[str] = Field(None, max_length=20, description="ZIP code")
    country: str = Field(default="US", max_length=50, description="Country")
    
    # Classification
    priority: ProspectPriorityEnum = Field(default="medium", description="Prospect priority")
    lead_score: Optional[float] = Field(None, ge=0, le=100, description="Lead score (0-100)")
    
    # Custom data
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom fields")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    notes: Optional[str] = Field(None, max_length=2000, description="Notes")
    
    # Scheduling preferences
    best_time_to_call: Optional[str] = Field(None, description="Best time to call")
    timezone: Optional[str] = Field(None, description="Prospect timezone")
    
    # Source information
    source: Optional[str] = Field(None, max_length=100, description="Lead source")
    source_campaign: Optional[str] = Field(None, max_length=255, description="Source campaign")
    utm_source: Optional[str] = Field(None, max_length=100, description="UTM source")
    utm_medium: Optional[str] = Field(None, max_length=100, description="UTM medium")
    utm_campaign: Optional[str] = Field(None, max_length=100, description="UTM campaign")
    
    # Compliance
    consent_given: bool = Field(default=False, description="Marketing consent given")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        import re
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed per prospect')
        return v
    
    @validator('lead_score')
    def validate_lead_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Lead score must be between 0 and 100')
        return v

class ProspectCreate(ProspectBase):
    """Schema for creating a new prospect"""
    campaign_id: str = Field(..., description="Campaign ID")

class ProspectUpdate(BaseModel):
    """Schema for updating an existing prospect"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=50)
    
    status: Optional[ProspectStatusEnum] = None
    priority: Optional[ProspectPriorityEnum] = None
    lead_score: Optional[float] = Field(None, ge=0, le=100)
    
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=2000)
    
    best_time_to_call: Optional[str] = None
    timezone: Optional[str] = None
    
    consent_given: Optional[bool] = None

class ProspectBulkCreate(BaseModel):
    """Schema for bulk prospect creation"""
    campaign_id: str = Field(..., description="Campaign ID")
    prospects: List[ProspectBase] = Field(..., min_items=1, max_items=1000, description="List of prospects")
    skip_duplicates: bool = Field(default=True, description="Skip duplicate phone numbers")
    validate_phones: bool = Field(default=True, description="Validate phone numbers")

class ProspectCallUpdate(BaseModel):
    """Schema for updating prospect after a call"""
    call_id: str = Field(..., description="Call ID")
    status: ProspectStatusEnum = Field(..., description="Call outcome status")
    duration: Optional[float] = Field(None, ge=0, description="Call duration in seconds")
    outcome: Optional[str] = Field(None, max_length=100, description="Call outcome")
    notes: Optional[str] = Field(None, max_length=1000, description="Call notes")
    next_call_scheduled: Optional[datetime] = Field(None, description="Next scheduled call")
    converted: bool = Field(default=False, description="Was prospect converted")
    conversion_value: Optional[float] = Field(None, ge=0, description="Conversion value")

class ProspectSchedule(BaseModel):
    """Schema for scheduling prospect calls"""
    prospect_ids: List[str] = Field(..., min_items=1, max_items=100, description="Prospect IDs")
    scheduled_time: datetime = Field(..., description="Scheduled call time")
    priority: ProspectPriorityEnum = Field(default="medium", description="Call priority")
    notes: Optional[str] = Field(None, max_length=500, description="Scheduling notes")

class ProspectMetrics(BaseModel):
    """Schema for prospect performance metrics"""
    total_calls: int = Field(default=0, description="Total calls made")
    successful_calls: int = Field(default=0, description="Successful calls")
    failed_calls: int = Field(default=0, description="Failed calls")
    no_answer_count: int = Field(default=0, description="No answer count")
    busy_count: int = Field(default=0, description="Busy count")
    voicemail_count: int = Field(default=0, description="Voicemail count")
    
    success_rate: float = Field(default=0.0, ge=0, le=100, description="Success rate percentage")
    answer_rate: float = Field(default=0.0, ge=0, le=100, description="Answer rate percentage")
    
    # Engagement metrics
    email_opens: int = Field(default=0, description="Email opens")
    email_clicks: int = Field(default=0, description="Email clicks")
    website_visits: int = Field(default=0, description="Website visits")

class ProspectAIPrediction(BaseModel):
    """Schema for AI predictions about prospects"""
    prediction_score: Optional[float] = Field(None, ge=0, le=100, description="AI prediction score")
    predicted_outcome: Optional[str] = Field(None, description="Predicted call outcome")
    optimal_call_time: Optional[str] = Field(None, description="Optimal time to call")
    likelihood_to_convert: Optional[float] = Field(None, ge=0, le=100, description="Conversion likelihood")
    recommended_approach: Optional[str] = Field(None, description="Recommended approach")
    confidence: Optional[float] = Field(None, ge=0, le=100, description="Prediction confidence")

class ProspectResponse(ProspectBase):
    """Schema for prospect response"""
    id: str
    campaign_id: str
    full_name: Optional[str] = None
    status: ProspectStatusEnum
    
    # Call history
    metrics: ProspectMetrics
    
    # Last call information
    last_call_id: Optional[str] = None
    last_call_date: Optional[datetime] = None
    last_call_status: Optional[str] = None
    last_call_duration: Optional[float] = None
    last_call_outcome: Optional[str] = None
    
    # Conversion tracking
    is_converted: bool = Field(default=False)
    conversion_date: Optional[datetime] = None
    conversion_value: Optional[float] = None
    conversion_type: Optional[str] = None
    
    # Scheduling
    next_call_scheduled: Optional[datetime] = None
    do_not_call_before: Optional[datetime] = None
    
    # AI predictions
    ai_predictions: Optional[ProspectAIPrediction] = None
    
    # Compliance
    opt_out_requested: bool = Field(default=False)
    opt_out_date: Optional[datetime] = None
    dnc_listed: bool = Field(default=False)
    consent_date: Optional[datetime] = None
    
    # Engagement
    last_engagement_date: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    first_contacted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProspectListResponse(BaseModel):
    """Schema for prospect list response"""
    prospects: List[ProspectResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class ProspectImport(BaseModel):
    """Schema for prospect import configuration"""
    file_type: str = Field(..., description="File type: csv, xlsx, json")
    mapping: Dict[str, str] = Field(..., description="Field mapping")
    skip_header: bool = Field(default=True, description="Skip header row")
    validate_data: bool = Field(default=True, description="Validate data before import")
    skip_duplicates: bool = Field(default=True, description="Skip duplicate phone numbers")
    default_values: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Default values")

class ProspectExport(BaseModel):
    """Schema for prospect export configuration"""
    format: str = Field(default="csv", description="Export format: csv, xlsx, json")
    fields: Optional[List[str]] = Field(None, description="Fields to export")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    include_history: bool = Field(default=False, description="Include call history")

class ProspectAction(BaseModel):
    """Schema for prospect actions"""
    action: str = Field(..., description="Action: call, schedule, convert, opt_out, add_note")
    prospect_ids: List[str] = Field(..., min_items=1, max_items=100, description="Prospect IDs")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action parameters")
    reason: Optional[str] = Field(None, description="Reason for action")

class ProspectFilter(BaseModel):
    """Schema for prospect filtering"""
    status: Optional[List[ProspectStatusEnum]] = None
    priority: Optional[List[ProspectPriorityEnum]] = None
    industry: Optional[List[str]] = None
    company: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    lead_score_min: Optional[float] = Field(None, ge=0, le=100)
    lead_score_max: Optional[float] = Field(None, ge=0, le=100)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_contacted_after: Optional[datetime] = None
    last_contacted_before: Optional[datetime] = None
    converted: Optional[bool] = None
    has_consent: Optional[bool] = None
    dnc_listed: Optional[bool] = None

class ProspectSearch(BaseModel):
    """Schema for prospect search"""
    query: str = Field(..., min_length=1, max_length=255, description="Search query")
    filters: Optional[ProspectFilter] = None
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

class ProspectAnalytics(BaseModel):
    """Schema for prospect analytics"""
    campaign_id: str
    total_prospects: int
    status_breakdown: Dict[str, int]
    conversion_metrics: Dict[str, float]
    engagement_metrics: Dict[str, float]
    performance_trends: Dict[str, List[float]]
    top_performing_segments: List[Dict[str, Any]]
    insights: List[str]

class ProspectSegment(BaseModel):
    """Schema for prospect segmentation"""
    name: str = Field(..., max_length=100, description="Segment name")
    description: Optional[str] = Field(None, max_length=500, description="Segment description")
    criteria: Dict[str, Any] = Field(..., description="Segmentation criteria")
    size: Optional[int] = Field(None, description="Segment size")
    tags: Optional[List[str]] = Field(default_factory=list, description="Segment tags")