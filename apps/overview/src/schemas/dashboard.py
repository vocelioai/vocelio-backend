"""
Dashboard Schemas
Pydantic models for dashboard data structures
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InsightCategory(str, Enum):
    PERFORMANCE = "performance"
    SCHEDULING = "scheduling"
    TARGETING = "targeting"
    OPTIMIZATION = "optimization"
    REVENUE = "revenue"
    SYSTEM = "system"

class ActionType(str, Enum):
    VOICE_OPTIMIZATION = "voice_optimization"
    SCHEDULE_OPTIMIZATION = "schedule_optimization"
    PROSPECT_PRIORITIZATION = "prospect_prioritization"
    CAMPAIGN_ADJUSTMENT = "campaign_adjustment"
    SYSTEM_OPTIMIZATION = "system_optimization"

class AIInsight(BaseModel):
    """AI-generated insight model"""
    id: str
    title: str
    description: str
    impact_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    priority: PriorityLevel
    category: InsightCategory
    estimated_revenue_impact: Optional[float] = None
    implementation_effort: str = Field(..., description="low, medium, high")
    action_type: ActionType
    created_at: datetime
    expires_at: Optional[datetime] = None
    implemented: bool = False

class SystemHealth(BaseModel):
    """System health status model"""
    overall_status: str = Field(..., description="healthy, degraded, critical")
    uptime_percentage: float = Field(..., ge=0.0, le=100.0)
    active_services: int
    total_services: int
    avg_response_time: int = Field(..., description="Average response time in ms")
    error_rate: float = Field(..., ge=0.0, le=100.0)
    last_incident: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    service_statuses: Dict[str, str] = Field(default_factory=dict)

class LiveStats(BaseModel):
    """Live statistics model"""
    active_calls: int
    calls_per_minute: int
    success_rate: float
    revenue_today: float
    ai_optimization_score: float
    average_call_duration: int = Field(..., description="Duration in seconds")
    conversion_rate: float
    agent_utilization: float
    last_updated: datetime

class GlobalMetrics(BaseModel):
    """Global platform metrics model"""
    total_clients: int
    active_calls: int
    daily_revenue: float
    monthly_call_volume: int
    success_rate: float
    ai_optimization_score: float
    system_uptime: float
    global_coverage_countries: int
    total_ai_agents: int
    last_updated: datetime

class DashboardOverview(BaseModel):
    """Complete dashboard overview model"""
    organization_id: str
    live_metrics: Dict[str, Any]
    ai_insights: List[AIInsight]
    system_health: SystemHealth
    last_updated: datetime

class DashboardFilter(BaseModel):
    """Dashboard filter model"""
    time_range: str = "24h"
    metric_types: List[str] = Field(default_factory=list)
    priority_filter: Optional[PriorityLevel] = None
    category_filter: Optional[InsightCategory] = None
    include_predictions: bool = True

class NotificationModel(BaseModel):
    """Dashboard notification model"""
    id: str
    type: str = Field(..., description="success, warning, error, info")
    title: str
    message: str
    priority: PriorityLevel
    timestamp: datetime
    unread: bool = True
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None

class QuickAction(BaseModel):
    """Quick action model"""
    id: str
    title: str
    description: str
    estimated_impact: str
    effort: str = Field(..., description="Effort required: e.g., '1 click', '2 minutes'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    category: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

class PerformanceSummary(BaseModel):
    """Performance summary model"""
    timeframe: str
    total_calls: int
    successful_calls: int
    revenue_generated: float
    avg_call_duration: int
    top_performing_agents: List[Dict[str, Any]]
    performance_trends: Dict[str, str]
    key_metrics: Dict[str, Any] = Field(default_factory=dict)

class AgentPerformance(BaseModel):
    """Agent performance model"""
    agent_id: str
    name: str
    total_calls: int
    successful_calls: int
    success_rate: float
    revenue_generated: float
    avg_call_duration: int
    utilization_rate: float
    customer_rating: Optional[float] = None
    last_active: datetime

class CampaignMetrics(BaseModel):
    """Campaign metrics model"""
    campaign_id: str
    name: str
    status: str
    total_calls: int
    success_rate: float
    conversion_rate: float
    revenue_generated: float
    cost_per_acquisition: float
    roi: float
    start_date: datetime
    end_date: Optional[datetime] = None

class RevenueBreakdown(BaseModel):
    """Revenue breakdown model"""
    total_revenue: float
    revenue_by_source: Dict[str, float]
    revenue_by_agent: Dict[str, float]
    revenue_by_campaign: Dict[str, float]
    revenue_trends: List[Dict[str, Any]]
    projections: Dict[str, float]
    growth_rate: float

class AlertModel(BaseModel):
    """Alert model"""
    id: str
    type: str = Field(..., description="performance, system, revenue, compliance")
    severity: PriorityLevel
    title: str
    description: str
    metric_name: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    acknowledged: bool = False
    resolved: bool = False
    actions_taken: List[str] = Field(default_factory=list)

class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    id: str
    type: str = Field(..., description="metric_card, chart, table, alert_list")
    title: str
    position: Dict[str, int] = Field(..., description="x, y, width, height")
    config: Dict[str, Any] = Field(default_factory=dict)
    data_source: str
    refresh_interval: int = Field(default=30, description="Refresh interval in seconds")
    visible: bool = True

class DashboardLayout(BaseModel):
    """Dashboard layout configuration"""
    id: str
    name: str
    organization_id: str
    user_id: Optional[str] = None
    widgets: List[DashboardWidget]
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

class SystemMetrics(BaseModel):
    """System performance metrics"""
    cpu_usage: float = Field(..., ge=0.0, le=100.0)
    memory_usage: float = Field(..., ge=0.0, le=100.0)
    disk_usage: float = Field(..., ge=0.0, le=100.0)
    network_io: Dict[str, float]
    active_connections: int
    request_rate: float
    error_rate: float
    avg_response_time: float
    uptime_seconds: int
    last_updated: datetime

class PredictiveInsight(BaseModel):
    """Predictive analytics insight"""
    id: str
    type: str = Field(..., description="forecast, anomaly, trend, recommendation")
    title: str
    description: str
    prediction: str
    confidence_interval: Dict[str, float]
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    data_points_used: int
    forecast_horizon: str = Field(..., description="Time horizon for prediction")
    generated_at: datetime
    valid_until: datetime

class ComplianceStatus(BaseModel):
    """Compliance status model"""
    overall_score: float = Field(..., ge=0.0, le=100.0)
    gdpr_compliance: float
    tcpa_compliance: float
    dnc_compliance: float
    recording_consent: float
    data_retention: float
    last_audit: datetime
    next_audit: datetime
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class IntegrationStatus(BaseModel):
    """Integration status model"""
    total_integrations: int
    active_integrations: int
    failed_integrations: int
    integration_health: Dict[str, str]
    recent_sync_issues: List[Dict[str, Any]] = Field(default_factory=list)
    sync_statistics: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime

class BusinessIntelligence(BaseModel):
    """Business intelligence summary"""
    revenue_insights: Dict[str, Any]
    performance_insights: Dict[str, Any]
    market_insights: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    growth_opportunities: List[str]
    risk_factors: List[str]
    recommendations: List[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime

class DashboardConfig(BaseModel):
    """Dashboard configuration model"""
    organization_id: str
    user_id: Optional[str] = None
    theme: str = "dark"
    refresh_interval: int = Field(default=30, ge=5, le=300)
    auto_refresh: bool = True
    show_notifications: bool = True
    show_ai_insights: bool = True
    metric_preferences: List[str] = Field(default_factory=list)
    layout_id: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"

class ExportRequest(BaseModel):
    """Data export request model"""
    export_type: str = Field(..., description="pdf, csv, excel, json")
    data_types: List[str] = Field(..., description="metrics, insights, reports")
    time_range: str = "30d"
    filters: Dict[str, Any] = Field(default_factory=dict)
    include_charts: bool = True
    include_raw_data: bool = False
    email_delivery: bool = False
    recipient_emails: List[str] = Field(default_factory=list)

class APIUsageMetrics(BaseModel):
    """API usage metrics for the overview service"""
    total_requests: int
    requests_per_minute: float
    average_response_time: float
    error_count: int
    error_rate: float
    active_sessions: int
    cache_hit_rate: float
    bandwidth_usage: float
    rate_limit_hits: int
    last_updated: datetime