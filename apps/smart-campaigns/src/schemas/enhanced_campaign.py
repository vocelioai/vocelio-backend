# apps/smart-campaigns/src/schemas/enhanced_campaign.py
"""
Enhanced Campaign Schemas - Merged from smart-campaigns + smart-campaigns-service
Supports both structured campaign management and AI optimization features
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Enhanced Enums
class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    OPTIMIZING = "optimizing"
    TESTING = "testing"
    FAILED = "failed"

class CampaignType(str, Enum):
    OUTBOUND_CALLS = "outbound_calls"
    LEAD_NURTURING = "lead_nurturing"
    APPOINTMENT_SETTING = "appointment_setting"
    CUSTOMER_RETENTION = "customer_retention"
    SURVEY_COLLECTION = "survey_collection"
    SALES_FOLLOW_UP = "sales_follow_up"
    EVENT_PROMOTION = "event_promotion"
    PRODUCT_LAUNCH = "product_launch"

class IndustryType(str, Enum):
    SOLAR = "solar"
    INSURANCE = "insurance"
    REAL_ESTATE = "real_estate"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    AUTOMOTIVE = "automotive"
    EDUCATION = "education"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    OTHER = "other"

class OptimizationGoal(str, Enum):
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_CONVERSIONS = "maximize_conversions"
    MINIMIZE_COST = "minimize_cost"
    IMPROVE_QUALITY = "improve_quality"
    INCREASE_REACH = "increase_reach"

class CampaignPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Base Campaign Schema
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    industry: IndustryType = Field(..., description="Target industry")
    campaign_type: CampaignType = Field(..., description="Type of campaign")
    priority: CampaignPriority = Field(default=CampaignPriority.MEDIUM)
    
    # Agent configuration
    agent_id: str = Field(..., description="Primary AI agent ID")
    agent_name: Optional[str] = Field(None, description="Agent display name")
    voice_id: Optional[str] = Field(None, description="Voice ID for calls")
    ai_agent_ids: List[str] = Field(default_factory=list, description="Additional AI agents")
    
    # Targeting and settings
    location: Optional[str] = Field(None, description="Target location")
    target_demographics: Dict[str, Any] = Field(default_factory=dict)
    target_audience_size: int = Field(default=0, ge=0)
    
    # Scheduling
    start_time: Optional[str] = Field(None, description="Daily start time (e.g., '9:00 AM')")
    end_time: Optional[str] = Field(None, description="Daily end time (e.g., '6:00 PM')")
    timezone: str = Field(default="UTC")
    schedule_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Campaign limits
    daily_call_limit: int = Field(default=1000, ge=1, le=10000)
    max_prospects: int = Field(default=10000, ge=1)
    
    # Script and template
    script_template: Optional[str] = Field(None, description="Call script template")
    template_id: Optional[str] = Field(None, description="Campaign template ID")
    
    # AI Optimization (from smart-campaigns-service)
    optimization_goal: OptimizationGoal = Field(default=OptimizationGoal.MAXIMIZE_REVENUE)
    is_ai_optimized: bool = Field(default=False, description="Enable AI optimization")
    
    # Additional settings
    settings: Dict[str, Any] = Field(default_factory=dict)

# Campaign Creation Schema
class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign"""
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Campaign name cannot be empty')
        return v.strip()
    
    @validator('daily_call_limit')
    def validate_call_limit(cls, v):
        if v <= 0:
            raise ValueError('Daily call limit must be positive')
        return v

# Campaign Update Schema
class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    priority: Optional[CampaignPriority] = None
    
    # Agent configuration
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    voice_id: Optional[str] = None
    ai_agent_ids: Optional[List[str]] = None
    
    # Targeting updates
    location: Optional[str] = None
    target_demographics: Optional[Dict[str, Any]] = None
    target_audience_size: Optional[int] = Field(None, ge=0)
    
    # Scheduling updates
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    timezone: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None
    
    # Limits updates
    daily_call_limit: Optional[int] = Field(None, ge=1, le=10000)
    max_prospects: Optional[int] = Field(None, ge=1)
    
    # Script updates
    script_template: Optional[str] = None
    
    # AI optimization updates
    optimization_goal: Optional[OptimizationGoal] = None
    is_ai_optimized: Optional[bool] = None
    
    # Settings updates
    settings: Optional[Dict[str, Any]] = None

# Campaign Response Schema
class CampaignResponse(CampaignBase):
    """Schema for campaign responses"""
    id: str
    status: CampaignStatus
    user_id: str
    organization_id: str
    
    # Performance metrics (from smart-campaigns-service)
    total_calls: int = Field(default=0, ge=0)
    successful_calls: int = Field(default=0, ge=0)
    conversion_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    revenue_generated: float = Field(default=0.0, ge=0.0)
    cost_per_acquisition: float = Field(default=0.0, ge=0.0)
    roi_percentage: float = Field(default=0.0)
    
    # A/B Testing
    is_ab_test: bool = Field(default=False)
    ab_test_config: Dict[str, Any] = Field(default_factory=dict)
    parent_campaign_id: Optional[str] = None
    
    # Analytics
    analytics_data: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    optimization_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Campaign List Response
class CampaignListResponse(BaseModel):
    """Schema for paginated campaign lists"""
    campaigns: List[CampaignResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Campaign Filter Schema
class CampaignFilter(BaseModel):
    """Schema for filtering campaigns"""
    status: Optional[List[CampaignStatus]] = None
    priority: Optional[List[CampaignPriority]] = None
    industry: Optional[List[IndustryType]] = None
    campaign_type: Optional[List[CampaignType]] = None
    agent_id: Optional[str] = None
    is_ai_optimized: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

# AI Optimization Schemas
class OptimizationRequest(BaseModel):
    """Request schema for AI optimization"""
    campaign_id: str
    optimization_goal: OptimizationGoal
    optimization_type: str = Field(..., description="Type of optimization: script, timing, targeting")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class OptimizationResponse(BaseModel):
    """Response schema for optimization results"""
    id: str
    campaign_id: str
    optimization_type: str
    status: str
    improvements: Dict[str, float]
    recommendations: List[str]
    confidence_score: float
    started_at: datetime
    completed_at: Optional[datetime] = None

# A/B Testing Schemas
class ABTestRequest(BaseModel):
    """Request schema for creating A/B tests"""
    campaign_id: str
    test_name: str
    test_type: str = Field(..., description="Type of test: script, voice, timing")
    variant_a_config: Dict[str, Any]
    variant_b_config: Dict[str, Any]
    traffic_split: float = Field(default=50.0, ge=10.0, le=90.0)
    minimum_sample_size: int = Field(default=100, ge=50)
    confidence_level: float = Field(default=95.0, ge=90.0, le=99.9)

class ABTestResponse(BaseModel):
    """Response schema for A/B test results"""
    id: str
    campaign_id: str
    test_name: str
    test_type: str
    status: str
    winner: Optional[str] = None
    variant_a_metrics: Dict[str, Any]
    variant_b_metrics: Dict[str, Any]
    statistical_significance: float
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

# Campaign Analytics Schema
class CampaignAnalytics(BaseModel):
    """Comprehensive campaign analytics"""
    total_campaigns: int
    active_campaigns: int
    total_calls: int
    total_revenue: float
    average_conversion_rate: float
    average_roi: float
    
    # Industry breakdown
    industry_performance: Dict[str, Dict[str, Any]]
    
    # Campaign type performance
    type_performance: Dict[str, Dict[str, Any]]
    
    # Top performers
    top_campaigns: List[Dict[str, Any]]
    
    # AI optimization stats
    ai_optimized_campaigns: int
    optimization_improvements: Dict[str, float]
    
    # Time-based metrics
    performance_timeline: List[Dict[str, Any]]

# Campaign Performance Schema
class CampaignPerformance(BaseModel):
    """Detailed performance metrics for a single campaign"""
    campaign_id: str
    campaign_name: str
    
    # Core metrics
    total_calls: int
    successful_calls: int
    failed_calls: int
    conversion_rate: float
    
    # Financial metrics
    revenue_generated: float
    cost_per_call: float
    cost_per_acquisition: float
    roi_percentage: float
    
    # Quality metrics
    average_call_duration: float
    customer_satisfaction_score: float
    
    # Optimization metrics
    optimization_count: int
    improvement_percentage: float
    
    # Time-based performance
    daily_performance: List[Dict[str, Any]]
    hourly_performance: List[Dict[str, Any]]
    
    # Comparative metrics
    vs_industry_average: Dict[str, float]
    vs_previous_period: Dict[str, float]

# Campaign Template Schemas
class CampaignTemplateResponse(BaseModel):
    """Schema for campaign templates"""
    id: str
    name: str
    description: Optional[str]
    industry: IndustryType
    campaign_type: CampaignType
    template_config: Dict[str, Any]
    script_template: Optional[str]
    recommended_settings: Dict[str, Any]
    avg_conversion_rate: float
    avg_roi: float
    usage_count: int
    is_featured: bool
    created_at: datetime

# Bulk Operations
class CampaignBulkAction(BaseModel):
    """Schema for bulk campaign operations"""
    campaign_ids: List[str] = Field(..., description="Campaign IDs to process")
    action: str = Field(..., description="Action to perform: start, pause, stop, delete")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('campaign_ids')
    def validate_campaign_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one campaign ID is required')
        if len(v) > 100:
            raise ValueError('Maximum 100 campaign IDs allowed')
        return v

class CampaignBulkResult(BaseModel):
    """Schema for bulk operation results"""
    total_processed: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
