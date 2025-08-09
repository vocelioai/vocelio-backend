"""
Analytics Schemas
📊 Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class TimeRangeEnum(str, Enum):
    """Time range options for analytics queries"""
    ONE_HOUR = "1h"
    TWENTY_FOUR_HOURS = "24h"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"

class MetricType(str, Enum):
    """Types of metrics available"""
    CALLS = "calls"
    REVENUE = "revenue"
    PERFORMANCE = "performance"
    SATISFACTION = "satisfaction"
    CONVERSION = "conversion"

class ChartType(str, Enum):
    """Chart visualization types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"

class TrendDirection(str, Enum):
    """Trend direction indicators"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

# Base schemas
class BaseAnalyticsSchema(BaseModel):
    """Base schema for all analytics responses"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Request schemas
class AnalyticsQueryRequest(BaseModel):
    """Base analytics query request"""
    time_range: TimeRangeEnum = Field(default=TimeRangeEnum.SEVEN_DAYS)
    organization_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class ChartDataRequest(BaseAnalyticsSchema):
    """Chart data request schema"""
    chart_type: ChartType
    time_range: TimeRangeEnum = Field(default=TimeRangeEnum.SEVEN_DAYS)
    metric_type: Optional[MetricType] = None
    granularity: Optional[str] = Field(default="day", regex="^(hour|day|week|month)$")

# Response schemas
class OverviewMetrics(BaseAnalyticsSchema):
    """Overview metrics response schema"""
    active_calls: int = Field(..., ge=0, description="Current active calls")
    total_calls: int = Field(..., ge=0, description="Total calls in period")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    avg_duration: int = Field(..., ge=0, description="Average call duration in seconds")
    revenue: float = Field(..., ge=0, description="Total revenue generated")
    agents: int = Field(..., ge=0, description="Total number of agents")
    satisfaction: float = Field(..., ge=0, le=5, description="Customer satisfaction score")
    conversion_rate: float = Field(..., ge=0, le=100, description="Conversion rate percentage")

class PerformanceMetrics(BaseAnalyticsSchema):
    """Performance metrics response schema"""
    overall_performance: float = Field(..., ge=0, le=100, description="Overall performance score")
    response_time: float = Field(..., ge=0, description="Average response time in seconds")
    quality_score: float = Field(..., ge=0, le=100, description="Call quality score")
    customer_satisfaction: float = Field(..., ge=0, le=5, description="Customer satisfaction")
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    hourly_performance: List[Dict[str, Any]] = Field(default_factory=list)

class AgentAnalytics(BaseAnalyticsSchema):
    """Individual agent analytics schema"""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Agent display name")
    total_calls: int = Field(..., ge=0, description="Total calls handled")
    successful_calls: int = Field(..., ge=0, description="Successful calls")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    avg_duration: int = Field(..., ge=0, description="Average call duration")
    revenue_generated: float = Field(..., ge=0, description="Revenue generated")
    satisfaction_score: float = Field(..., ge=0, le=5, description="Customer satisfaction")
    performance_score: float = Field(..., ge=0, le=100, description="Overall performance score")
    status: str = Field(..., description="Agent status")
    last_activity: datetime = Field(..., description="Last activity timestamp")

    @validator('success_rate')
    def validate_success_rate(cls, v, values):
        """Validate success rate against call counts"""
        if 'total_calls' in values and values['total_calls'] > 0:
            calculated_rate = (values.get('successful_calls', 0) / values['total_calls']) * 100
            # Allow some tolerance for rounding
            if abs(v - calculated_rate) > 1.0:
                raise ValueError('Success rate does not match call counts')
        return v

class CampaignAnalytics(BaseAnalyticsSchema):
    """Campaign analytics schema"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    campaign_name: str = Field(..., description="Campaign display name")
    total_calls: int = Field(..., ge=0, description="Total calls made")
    successful_calls: int = Field(..., ge=0, description="Successful calls")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    conversion_rate: float = Field(..., ge=0, le=100, description="Conversion rate")
    cost_per_lead: float = Field(..., ge=0, description="Cost per lead")
    revenue_generated: float = Field(..., ge=0, description="Revenue generated")
    roi: float = Field(..., description="Return on investment percentage")
    status: str = Field(..., description="Campaign status")
    created_at: datetime = Field(..., description="Campaign creation date")

class VoiceAnalytics(BaseAnalyticsSchema):
    """Voice performance analytics schema"""
    voice_id: str = Field(..., description="Unique voice identifier")
    voice_name: str = Field(..., description="Voice display name")
    usage_count: int = Field(..., ge=0, description="Number of times used")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    avg_duration: int = Field(..., ge=0, description="Average call duration")
    customer_satisfaction: float = Field(..., ge=0, le=5, description="Customer satisfaction")
    conversion_rate: float = Field(..., ge=0, le=100, description="Conversion rate")
    cost: float = Field(..., ge=0, description="Total cost for usage")
    performance_score: float = Field(..., ge=0, le=100, description="Overall performance score")

class AIRecommendation(BaseModel):
    """AI recommendation schema"""
    id: str = Field(..., description="Recommendation ID")
    type: str = Field(..., description="Recommendation type")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    impact: str = Field(..., description="Expected impact")
    confidence: int = Field(..., ge=0, le=100, description="Confidence percentage")
    action: str = Field(..., description="Suggested action")
    priority: str = Field(..., regex="^(low|medium|high|critical)$", description="Priority level")

class OptimizationOpportunity(BaseModel):
    """Optimization opportunity schema"""
    area: str = Field(..., description="Area for optimization")
    description: str = Field(..., description="Opportunity description")
    potential_improvement: str = Field(..., description="Expected improvement")

class PerformancePrediction(BaseModel):
    """Performance prediction schema"""
    call_volume: str = Field(..., description="Predicted call volume change")
    success_rate: str = Field(..., description="Predicted success rate change")
    revenue: str = Field(..., description="Predicted revenue change")

class Anomaly(BaseModel):
    """System anomaly schema"""
    type: str = Field(..., description="Anomaly type")
    description: str = Field(..., description="Anomaly description")
    severity: str = Field(..., regex="^(low|medium|high|critical)$", description="Severity level")
    suggested_action: str = Field(..., description="Suggested remediation action")

class Trend(BaseModel):
    """Trend data schema"""
    metric: str = Field(..., description="Metric name")
    direction: TrendDirection = Field(..., description="Trend direction")
    change: str = Field(..., description="Change amount")
    period: str = Field(..., description="Time period")

class AIInsights(BaseAnalyticsSchema):
    """AI insights response schema"""
    recommendations: List[AIRecommendation] = Field(default_factory=list)
    optimization_opportunities: List[OptimizationOpportunity] = Field(default_factory=list)
    performance_predictions: Dict[str, PerformancePrediction] = Field(default_factory=dict)
    anomalies: List[Anomaly] = Field(default_factory=list)
    trends: List[Trend] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0, le=100, description="Overall confidence score")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ActiveCall(BaseModel):
    """Active call information schema"""
    call_id: str = Field(..., description="Call identifier")
    agent_id: str = Field(..., description="Agent handling the call")
    duration: int = Field(..., ge=0, description="Call duration in seconds")
    status: str = Field(..., description="Call status")
    prospect_info: Optional[Dict[str, Any]] = None

class SystemHealth(BaseModel):
    """System health indicators schema"""
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    api_response_time: float = Field(..., ge=0, description="API response time in seconds")
    uptime: float = Field(..., ge=0, le=100, description="System uptime percentage")

class AgentStatus(BaseModel):
    """Agent status information schema"""
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="Current status")
    current_call: Optional[str] = None
    idle_time: Optional[int] = None

class QueueStatus(BaseModel):
    """Call queue status schema"""
    waiting_calls: int = Field(..., ge=0, description="Calls waiting in queue")
    avg_wait_time: float = Field(..., ge=0, description="Average wait time")
    max_wait_time: float = Field(..., ge=0, description="Maximum wait time")

class Alert(BaseModel):
    """System alert schema"""
    id: str = Field(..., description="Alert identifier")
    type: str = Field(..., description="Alert type")
    severity: str = Field(..., regex="^(info|warning|critical)$", description="Alert severity")
    message: str = Field(..., description="Alert message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RealTimeMonitor(BaseAnalyticsSchema):
    """Real-time monitoring data schema"""
    active_calls: List[ActiveCall] = Field(default_factory=list)
    system_health: SystemHealth
    agent_status: List[AgentStatus] = Field(default_factory=list)
    queue_status: QueueStatus
    alerts: List[Alert] = Field(default_factory=list)

class ChartDataPoint(BaseModel):
    """Individual chart data point schema"""
    timestamp: datetime = Field(..., description="Data point timestamp")
    value: Union[int, float] = Field(..., description="Data point value")
    label: Optional[str] = None
    category: Optional[str] = None

class ChartData(BaseModel):
    """Chart data response schema"""
    chart_type: ChartType = Field(..., description="Type of chart")
    title: str = Field(..., description="Chart title")
    data: List[Dict[str, Any]] = Field(..., description="Chart data points")
    time_range: TimeRangeEnum = Field(..., description="Data time range")
    metadata: Optional[Dict[str, Any]] = None

# Call volume chart specific schemas
class CallVolumeData(BaseModel):
    """Call volume chart data"""
    time: str = Field(..., description="Time label")
    calls: int = Field(..., ge=0, description="Total calls")
    successful: int = Field(..., ge=0, description="Successful calls")
    failed: int = Field(..., ge=0, description="Failed calls")

class CallResultsData(BaseModel):
    """Call results pie chart data"""
    name: str = Field(..., description="Result category name")
    value: int = Field(..., ge=0, description="Count of calls")
    color: str = Field(..., regex="^#[0-9A-Fa-f]{6}$", description="Chart color")

class PerformanceData(BaseModel):
    """Performance chart data"""
    date: str = Field(..., description="Date label")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate")
    avg_duration: int = Field(..., ge=0, description="Average duration")
    satisfaction: float = Field(..., ge=0, le=5, description="Satisfaction score")

# Export schemas
class ExportRequest(BaseModel):
    """Data export request schema"""
    export_type: str = Field(..., regex="^(csv|xlsx|pdf|json)$", description="Export format")
    data_type: str = Field(..., description="Type of data to export")
    time_range: TimeRangeEnum = Field(default=TimeRangeEnum.SEVEN_DAYS)
    filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = Field(default=True, description="Include metadata in export")

class ExportResponse(BaseAnalyticsSchema):
    """Data export response schema"""
    export_id: str = Field(..., description="Export job identifier")
    status: str = Field(..., regex="^(pending|processing|completed|failed)$")
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    expires_at: Optional[datetime] = None

# Report schemas
class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: str = Field(..., description="Type of report")
    title: str = Field(..., description="Report title")
    time_range: TimeRangeEnum = Field(default=TimeRangeEnum.SEVEN_DAYS)
    sections: List[str] = Field(..., description="Report sections to include")
    format: str = Field(default="pdf", regex="^(pdf|html|docx)$")
    recipients: Optional[List[str]] = None

class ReportResponse(BaseAnalyticsSchema):
    """Report generation response"""
    report_id: str = Field(..., description="Report identifier")
    status: str = Field(..., regex="^(pending|generating|completed|failed)$")
    download_url: Optional[str] = None
    preview_url: Optional[str] = None

# Dashboard schemas
class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    widget_id: str = Field(..., description="Widget identifier")
    widget_type: str = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    position: Dict[str, int] = Field(..., description="Widget position and size")
    config: Dict[str, Any] = Field(default_factory=dict, description="Widget configuration")

class Dashboard(BaseAnalyticsSchema):
    """Dashboard configuration schema"""
    dashboard_id: str = Field(..., description="Dashboard identifier")
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = None
    widgets: List[DashboardWidget] = Field(default_factory=list)
    is_public: bool = Field(default=False, description="Public dashboard flag")
    created_by: str = Field(..., description="Creator user ID")

class DashboardResponse(BaseModel):
    """Dashboard data response"""
    dashboard: Dashboard
    widget_data: Dict[str, Any] = Field(default_factory=dict, description="Data for each widget")

# Error schemas
class AnalyticsError(BaseModel):
    """Analytics error response schema"""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Pagination schemas
class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=1000, description="Items per page")
    total: int = Field(..., ge=0, description="Total items")
    pages: int = Field(..., ge=0, description="Total pages")

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    data: List[Any] = Field(..., description="Response data")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

# Health check schemas
class ServiceHealth(BaseModel):
    """Service health check response"""
    status: str = Field(..., regex="^(healthy|unhealthy|degraded)$")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    environment: str = Field(..., description="Environment name")

class DetailedHealthCheck(ServiceHealth):
    """Detailed health check with dependencies"""
    dependencies: Dict[str, str] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)

# Configuration validation
class AnalyticsConfig(BaseModel):
    """Analytics service configuration"""
    cache_ttl: int = Field(default=300, ge=60, le=3600, description="Cache TTL in seconds")
    max_query_range: int = Field(default=90, ge=1, le=365, description="Max query range in days")
    real_time_update_interval: int = Field(default=3, ge=1, le=60, description="Real-time update interval")
    max_export_rows: int = Field(default=100000, ge=1000, le=1000000, description="Max rows per export")
    
    class Config:
        validate_assignment = True