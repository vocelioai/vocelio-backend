# apps/overview/src/schemas/enhanced_overview.py
"""
Enhanced Overview Schemas - Merged from overview + overview-service
Supports both structured dashboard management and real-time features
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Enhanced Enums
class MetricType(str, Enum):
    LIVE = "live"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class InsightType(str, Enum):
    OPTIMIZATION = "optimization"
    ALERT = "alert"
    RECOMMENDATION = "recommendation"
    PERFORMANCE = "performance"
    REVENUE = "revenue"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SystemStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"

# Live Metrics (from overview-service)
class LiveMetrics(BaseModel):
    """Real-time metrics for the dashboard"""
    total_clients: int = Field(..., description="Total active clients")
    active_calls: int = Field(..., description="Current active calls")
    calls_today: int = Field(..., description="Calls made today")
    revenue_today: float = Field(..., description="Revenue generated today")
    success_rate: float = Field(..., description="Overall success rate percentage")
    ai_optimization_score: float = Field(..., description="AI optimization score")
    system_uptime: float = Field(..., description="System uptime percentage")
    monthly_call_volume: int = Field(..., description="Monthly call volume")
    agents_active: int = Field(..., description="Number of active AI agents")
    campaigns_running: int = Field(..., description="Number of running campaigns")
    last_updated: datetime = Field(default_factory=datetime.now)

# System Health (from overview-service)
class SystemHealth(BaseModel):
    """System health status"""
    status: SystemStatus = Field(..., description="Overall system status")
    uptime: float = Field(..., description="System uptime percentage")
    services_online: int = Field(..., description="Number of services online")
    total_services: int = Field(..., description="Total number of services")
    response_time_avg: float = Field(default=0.0, description="Average response time (ms)")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    active_alerts: int = Field(default=0, description="Number of active alerts")
    last_check: datetime = Field(default_factory=datetime.now)

# Revenue Metrics (from overview-service)
class RevenueMetrics(BaseModel):
    """Revenue tracking metrics"""
    daily_revenue: float = Field(..., description="Revenue for today")
    monthly_revenue: float = Field(..., description="Revenue for current month")
    yearly_revenue: float = Field(..., description="Revenue for current year")
    revenue_growth: float = Field(..., description="Revenue growth percentage")
    top_revenue_sources: List[Dict[str, Any]] = Field(default_factory=list)
    projected_monthly: float = Field(..., description="Projected monthly revenue")

# AI Insights (enhanced from both services)
class AIInsight(BaseModel):
    """AI-generated insights for optimization"""
    id: str = Field(..., description="Unique insight ID")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    insight_type: InsightType = Field(..., description="Type of insight")
    category: str = Field(..., description="Insight category")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confidence score")
    impact_estimate: str = Field(..., description="Estimated impact")
    potential_value: float = Field(default=0.0, description="Potential monetary value")
    priority: str = Field(..., description="Priority level")
    action_type: str = Field(..., description="Type of action required")
    recommended_action: Dict[str, Any] = Field(default_factory=dict)
    implementation_steps: List[str] = Field(default_factory=list)
    is_implemented: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.now)

# Global Stats (from overview-service)
class GlobalStats(BaseModel):
    """Global platform statistics"""
    total_ai_agents: int = Field(default=247, description="Total AI agents")
    industries_covered: int = Field(default=89, description="Industries covered")
    global_success_rate: float = Field(default=94.7, description="Global success rate")
    monthly_call_volume: int = Field(default=89500000, description="Monthly call volume")
    total_revenue: float = Field(default=47000000, description="Total platform revenue")
    system_uptime: float = Field(default=99.99, description="System uptime")

# Dashboard Overview (enhanced from overview)
class DashboardOverview(BaseModel):
    """Complete dashboard overview with live metrics"""
    organization_id: str = Field(..., description="Organization ID")
    live_metrics: LiveMetrics = Field(..., description="Real-time metrics")
    ai_insights: List[AIInsight] = Field(default_factory=list, description="AI insights")
    system_health: SystemHealth = Field(..., description="System health status")
    revenue_metrics: Optional[RevenueMetrics] = None
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)

# Live Stats (from overview)
class LiveStats(BaseModel):
    """Live statistics for real-time updates"""
    active_calls: int = Field(..., description="Current active calls")
    calls_per_minute: float = Field(..., description="Calls per minute rate")
    success_rate_live: float = Field(..., description="Live success rate")
    revenue_per_hour: float = Field(..., description="Revenue per hour")
    top_performing_agents: List[Dict[str, Any]] = Field(default_factory=list)
    system_load: float = Field(..., description="Current system load")
    timestamp: datetime = Field(default_factory=datetime.now)

# Widget Configuration
class WidgetConfig(BaseModel):
    """Dashboard widget configuration"""
    widget_type: str = Field(..., description="Type of widget")
    title: str = Field(..., description="Widget title")
    configuration: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, Any] = Field(default_factory=dict)
    refresh_interval: int = Field(default=30, description="Refresh interval in seconds")
    is_visible: bool = Field(default=True)

class WidgetResponse(WidgetConfig):
    """Widget response with ID and metadata"""
    id: str = Field(..., description="Widget ID")
    user_id: str = Field(..., description="User ID")
    organization_id: str = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Metrics Snapshot
class MetricsSnapshot(BaseModel):
    """Historical metrics snapshot"""
    organization_id: str = Field(..., description="Organization ID")
    snapshot_type: MetricType = Field(..., description="Snapshot type")
    total_calls: int = Field(default=0)
    successful_calls: int = Field(default=0)
    active_campaigns: int = Field(default=0)
    revenue_generated: float = Field(default=0.0)
    success_rate: float = Field(default=0.0)
    ai_optimization_score: float = Field(default=0.0)
    metrics_data: Dict[str, Any] = Field(default_factory=dict)
    snapshot_time: datetime = Field(default_factory=datetime.now)

class MetricsSnapshotResponse(MetricsSnapshot):
    """Metrics snapshot response with ID"""
    id: str = Field(..., description="Snapshot ID")
    created_at: datetime = Field(..., description="Creation timestamp")

# Dashboard Alert
class DashboardAlert(BaseModel):
    """Dashboard alert/notification"""
    alert_type: str = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    related_data: Dict[str, Any] = Field(default_factory=dict)
    action_required: bool = Field(default=False)
    action_url: Optional[str] = None

class DashboardAlertResponse(DashboardAlert):
    """Dashboard alert response with metadata"""
    id: str = Field(..., description="Alert ID")
    organization_id: str = Field(..., description="Organization ID")
    user_id: Optional[str] = None
    is_read: bool = Field(default=False)
    is_dismissed: bool = Field(default=False)
    created_at: datetime = Field(..., description="Creation timestamp")
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None

# WebSocket Messages
class WebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now)

class LiveUpdateMessage(WebSocketMessage):
    """Live update message for WebSocket"""
    type: str = Field(default="live_update")
    metrics: LiveMetrics = Field(..., description="Live metrics data")

class AlertMessage(WebSocketMessage):
    """Alert message for WebSocket"""
    type: str = Field(default="alert")
    alert: DashboardAlert = Field(..., description="Alert data")

class InsightMessage(WebSocketMessage):
    """AI insight message for WebSocket"""
    type: str = Field(default="ai_insight")
    insight: AIInsight = Field(..., description="AI insight data")

# Request/Response Schemas
class DashboardFilter(BaseModel):
    """Filter options for dashboard data"""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    metric_types: Optional[List[MetricType]] = None
    insight_types: Optional[List[InsightType]] = None
    severity_levels: Optional[List[AlertSeverity]] = None

class AnalyticsRequest(BaseModel):
    """Request for analytics data"""
    organization_id: str = Field(..., description="Organization ID")
    time_range: str = Field(..., description="Time range for analytics")
    metrics: List[str] = Field(..., description="Metrics to include")
    granularity: MetricType = Field(default=MetricType.HOURLY)

class AnalyticsResponse(BaseModel):
    """Analytics response with time series data"""
    organization_id: str = Field(..., description="Organization ID")
    time_range: str = Field(..., description="Time range")
    data_points: List[Dict[str, Any]] = Field(..., description="Time series data")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    generated_at: datetime = Field(default_factory=datetime.now)

# Bulk Operations
class BulkMetricsRequest(BaseModel):
    """Request for bulk metrics updates"""
    organization_id: str = Field(..., description="Organization ID")
    snapshots: List[MetricsSnapshot] = Field(..., description="Metrics snapshots")

class BulkInsightsRequest(BaseModel):
    """Request for bulk AI insights"""
    organization_id: str = Field(..., description="Organization ID")
    insights: List[AIInsight] = Field(..., description="AI insights")

# Cache Management
class CacheStatus(BaseModel):
    """Cache status information"""
    cache_key: str = Field(..., description="Cache key")
    hit_rate: float = Field(..., description="Cache hit rate")
    size: int = Field(..., description="Cache size")
    expires_at: datetime = Field(..., description="Expiration time")
    last_updated: datetime = Field(..., description="Last update time")

# Performance Metrics
class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_io: Dict[str, float] = Field(..., description="Network I/O metrics")
    database_connections: int = Field(..., description="Active database connections")
    redis_connections: int = Field(..., description="Active Redis connections")
    websocket_connections: int = Field(..., description="Active WebSocket connections")
    timestamp: datetime = Field(default_factory=datetime.now)
