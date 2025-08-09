# apps/smart-campaigns/src/schemas/campaign.py
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from core.config import CampaignStatus, CampaignPriority, CampaignType, OptimizationType

# Enums for validation
class CampaignStatusEnum(str, Enum):
    DRAFT = CampaignStatus.DRAFT
    SCHEDULED = CampaignStatus.SCHEDULED
    ACTIVE = CampaignStatus.ACTIVE
    RUNNING = CampaignStatus.RUNNING
    PAUSED = CampaignStatus.PAUSED
    COMPLETED = CampaignStatus.COMPLETED
    CANCELLED = CampaignStatus.CANCELLED
    FAILED = CampaignStatus.FAILED

class CampaignPriorityEnum(str, Enum):
    LOW = CampaignPriority.LOW
    MEDIUM = CampaignPriority.MEDIUM
    HIGH = CampaignPriority.HIGH
    URGENT = CampaignPriority.URGENT

class CampaignTypeEnum(str, Enum):
    OUTBOUND_CALL = CampaignType.OUTBOUND_CALL
    FOLLOW_UP = CampaignType.FOLLOW_UP
    APPOINTMENT_SETTING = CampaignType.APPOINTMENT_SETTING
    LEAD_QUALIFICATION = CampaignType.LEAD_QUALIFICATION
    CUSTOMER_SURVEY = CampaignType.CUSTOMER_SURVEY
    PRODUCT_PROMOTION = CampaignType.PRODUCT_PROMOTION

# Base Schemas
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: Optional[str] = Field(None, max_length=1000, description="Campaign description")
    industry: str = Field(..., min_length=1, max_length=100, description="Target industry")
    campaign_type: CampaignTypeEnum = Field(default=CampaignType.OUTBOUND_CALL, description="Type of campaign")
    priority: CampaignPriorityEnum = Field(default=CampaignPriority.MEDIUM, description="Campaign priority")
    
    # Agent Configuration
    agent_id: str = Field(..., description="ID of the AI agent to use")
    voice_id: Optional[str] = Field(None, description="Voice ID for the agent")
    
    # Location & Targeting
    location: Optional[str] = Field(None, max_length=255, description="Target location")
    target_demographics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Target demographics")
    
    # Scheduling
    start_time: str = Field(default="9:00 AM", pattern=r"^\d{1,2}:\d{2}\s?(AM|PM)$", description="Daily start time")
    end_time: str = Field(default="6:00 PM", pattern=r"^\d{1,2}:\d{2}\s?(AM|PM)$", description="Daily end time")
    timezone: str = Field(default="UTC", description="Campaign timezone")
    
    # Settings
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Campaign settings")
    tags: Optional[List[str]] = Field(default_factory=list, description="Campaign tags")
    
    # AI Configuration
    ai_optimization_enabled: bool = Field(default=True, description="Enable AI optimization")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Campaign name cannot be empty')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        return v

class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign"""
    pass

class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, min_length=1, max_length=100)
    campaign_type: Optional[CampaignTypeEnum] = None
    priority: Optional[CampaignPriorityEnum] = None
    status: Optional[CampaignStatusEnum] = None
    
    agent_id: Optional[str] = None
    voice_id: Optional[str] = None
    
    location: Optional[str] = Field(None, max_length=255)
    target_demographics: Optional[Dict[str, Any]] = None
    
    start_time: Optional[str] = Field(None, pattern=r"^\d{1,2}:\d{2}\s?(AM|PM)$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{1,2}:\d{2}\s?(AM|PM)$")
    timezone: Optional[str] = None
    
    settings: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    ai_optimization_enabled: Optional[bool] = None

class CampaignScheduleConfig(BaseModel):
    """Schema for campaign scheduling configuration"""
    schedule_type: str = Field(default="immediate", description="Schedule type: immediate, scheduled, recurring")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start datetime")
    scheduled_end: Optional[datetime] = Field(None, description="Scheduled end datetime")
    
    # Recurring configuration
    is_recurring: bool = Field(default=False, description="Is this a recurring campaign")
    recurrence_pattern: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Recurrence pattern")
    
    # Daily time windows
    daily_start_time: str = Field(default="09:00", pattern=r"^\d{2}:\d{2}$", description="Daily start time (24h format)")
    daily_end_time: str = Field(default="17:00", pattern=r"^\d{2}:\d{2}$", description="Daily end time (24h format)")
    timezone: str = Field(default="UTC", description="Timezone")
    
    # Days of week (0 = Monday, 6 = Sunday)
    allowed_days: List[int] = Field(default=[0, 1, 2, 3, 4], description="Allowed days of week")
    
    @validator('allowed_days')
    def validate_allowed_days(cls, v):
        if not v:
            raise ValueError('At least one day must be allowed')
        for day in v:
            if day < 0 or day > 6:
                raise ValueError('Days must be between 0 (Monday) and 6 (Sunday)')
        return sorted(list(set(v)))  # Remove duplicates and sort

class ABTestConfig(BaseModel):
    """Schema for A/B test configuration"""
    test_name: str = Field(..., description="Name of the A/B test")
    test_type: str = Field(..., description="Type of test: voice, script, timing, etc.")
    variants: List[Dict[str, Any]] = Field(..., min_items=2, max_items=5, description="Test variants")
    traffic_split: List[float] = Field(..., description="Traffic split percentages")
    success_metric: str = Field(..., description="Primary success metric")
    minimum_sample_size: int = Field(default=100, description="Minimum sample size per variant")
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99, description="Statistical confidence level")
    
    @validator('traffic_split')
    def validate_traffic_split(cls, v, values):
        if 'variants' in values and len(v) != len(values['variants']):
            raise ValueError('Traffic split must match number of variants')
        if abs(sum(v) - 1.0) > 0.001:
            raise ValueError('Traffic split must sum to 1.0')
        return v

class CampaignMetrics(BaseModel):
    """Schema for campaign performance metrics"""
    total_prospects: int = Field(default=0, description="Total number of prospects")
    calls_made: int = Field(default=0, description="Total calls made")
    calls_answered: int = Field(default=0, description="Calls answered")
    calls_completed: int = Field(default=0, description="Calls completed successfully")
    success_rate: float = Field(default=0.0, ge=0, le=100, description="Success rate percentage")
    conversion_rate: float = Field(default=0.0, ge=0, le=100, description="Conversion rate percentage")
    average_call_duration: float = Field(default=0.0, ge=0, description="Average call duration in seconds")
    
    # Financial metrics
    total_cost: float = Field(default=0.0, ge=0, description="Total campaign cost")
    revenue_generated: float = Field(default=0.0, ge=0, description="Revenue generated")
    cost_per_lead: float = Field(default=0.0, ge=0, description="Cost per lead")
    roi: float = Field(default=0.0, description="Return on investment")
    
    # Live metrics
    live_calls: int = Field(default=0, ge=0, description="Currently active calls")
    calls_today: int = Field(default=0, ge=0, description="Calls made today")
    conversions_today: int = Field(default=0, ge=0, description="Conversions today")

class CampaignPredictions(BaseModel):
    """Schema for AI predictions"""
    predicted_success_rate: Optional[float] = Field(None, ge=0, le=100, description="Predicted success rate")
    predicted_revenue: Optional[float] = Field(None, ge=0, description="Predicted revenue")
    prediction_confidence: Optional[float] = Field(None, ge=0, le=100, description="Prediction confidence")
    optimal_call_times: Optional[List[str]] = Field(None, description="Optimal call times")
    recommended_improvements: Optional[List[str]] = Field(None, description="AI recommendations")

class CampaignResponse(CampaignBase):
    """Schema for campaign response"""
    id: str
    status: CampaignStatusEnum
    user_id: str
    organization_id: str
    agent_name: Optional[str] = None
    
    # Metrics
    metrics: CampaignMetrics
    
    # AI & Optimization
    ai_optimization_score: Optional[float] = Field(None, ge=0, le=100)
    optimization_suggestions: List[str] = Field(default_factory=list)
    
    # A/B Testing
    is_ab_test: bool = Field(default=False)
    ab_test_config: Optional[ABTestConfig] = None
    ab_test_results: Optional[Dict[str, Any]] = None
    
    # Predictions
    predictions: Optional[CampaignPredictions] = None
    
    # Progress
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CampaignListResponse(BaseModel):
    """Schema for campaign list response"""
    campaigns: List[CampaignResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class CampaignAction(BaseModel):
    """Schema for campaign actions"""
    action: str = Field(..., description="Action to perform: start, pause, resume, stop, cancel")
    reason: Optional[str] = Field(None, description="Reason for the action")
    force: bool = Field(default=False, description="Force action even if validation fails")

class CampaignBulkAction(BaseModel):
    """Schema for bulk campaign actions"""
    campaign_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of campaign IDs")
    action: str = Field(..., description="Action to perform on all campaigns")
    reason: Optional[str] = Field(None, description="Reason for the bulk action")

class CampaignOptimization(BaseModel):
    """Schema for campaign optimization requests"""
    optimization_type: str = Field(..., description="Type of optimization")
    target_metric: str = Field(..., description="Target metric to optimize")
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optimization constraints")
    apply_immediately: bool = Field(default=False, description="Apply optimization immediately")

class CampaignAnalytics(BaseModel):
    """Schema for campaign analytics"""
    campaign_id: str
    date_range: Dict[str, datetime]
    metrics: Dict[str, Any]
    trends: Dict[str, List[float]]
    comparisons: Optional[Dict[str, Any]] = None
    insights: List[str] = Field(default_factory=list)

# Filter and Search Schemas
class CampaignFilter(BaseModel):
    """Schema for campaign filtering"""
    status: Optional[List[CampaignStatusEnum]] = None
    priority: Optional[List[CampaignPriorityEnum]] = None
    campaign_type: Optional[List[CampaignTypeEnum]] = None
    industry: Optional[List[str]] = None
    agent_id: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    success_rate_min: Optional[float] = Field(None, ge=0, le=100)
    success_rate_max: Optional[float] = Field(None, ge=0, le=100)

class CampaignSearch(BaseModel):
    """Schema for campaign search"""
    query: str = Field(..., min_length=1, max_length=255, description="Search query")
    filters: Optional[CampaignFilter] = None
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")