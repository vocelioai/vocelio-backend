"""
Metrics Schemas
Pydantic models for metrics and analytics data structures
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MetricDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

class MetricColor(str, Enum):
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    ORANGE = "orange"
    CYAN = "cyan"
    RED = "red"

class LiveMetrics(BaseModel):
    """Live metrics model for real-time data"""
    organization_id: str
    active_calls: int = Field(..., ge=0)
    calls_per_minute: int = Field(..., ge=0)
    revenue_today: float = Field(..., ge=0.0)
    revenue_this_hour: float = Field(..., ge=0.0)
    success_rate: float = Field(..., ge=0.0, le=100.0)
    bookings_today: int = Field(..., ge=0)
    conversion_rate: float = Field(..., ge=0.0, le=100.0)
    average_call_duration: int = Field(..., ge=0, description="Duration in seconds")
    ai_optimization_score: float = Field(..., ge=0.0, le=100.0)
    agent_utilization: float = Field(..., ge=0.0, le=100.0)
    queue_wait_time: int = Field(..., ge=0, description="Wait time in seconds")
    system_load: float = Field(..., ge=0.0, le=100.0)
    last_updated: datetime

class MetricCard(BaseModel):
    """Metric card for dashboard display"""
    id: str
    title: str
    value: str
    subtitle: Optional[str] = None
    change_percentage: Optional[float] = None
    change_direction: Optional[MetricDirection] = None
    icon: str
    color: MetricColor
    trend_data: List[float] = Field(default_factory=list)
    target_value: Optional[float] = None
    unit: Optional[str] = None
    description: Optional[str] = None

class TimeSeriesPoint(BaseModel):
    """Single point in time series data"""
    timestamp: str
    value: float
    label: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TimeSeriesData(BaseModel):
    """Time series data for charts"""
    metric_type: str
    time_range: str
    granularity: str
    data_points: List[Dict[str, Any]]
    total_points: int
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    average_value: Optional[float] = None
    trend_direction: Optional[MetricDirection] = None
    generated_at: datetime

class KPIReport(BaseModel):
    """Comprehensive KPI report"""
    organization_id: str
    time_range: str
    total_calls: int
    successful_calls: int
    total_revenue: float
    average_call_duration: int
    success_rate: float
    conversion_rate: float
    cost_per_call: float
    revenue_per_call: float
    agent_utilization: float
    customer_satisfaction: float
    first_call_resolution: float
    call_abandonment_rate: float
    generated_at: datetime

class MetricsFilter(BaseModel):
    """Filter options for metrics queries"""
    time_range: str = "24h"
    metric_types: List[str] = Field(default_factory=list)
    agent_ids: List[str] = Field(default_factory=list)
    campaign_ids: List[str] = Field(default_factory=list)
    include_predictions: bool = False
    granularity: str = "hour"
    group_by: Optional[str] = None

class CallMetrics(BaseModel):
    """Call-specific metrics"""
    total_calls: int
    inbound_calls: int
    outbound_calls: int
    answered_calls: int
    missed_calls: int
    average_wait_time: float
    average_talk_time: float
    average_hold_time: float
    call_resolution_rate: float
    callback_rate: float
    transfer_rate: float

class RevenueMetrics(BaseModel):
    """Revenue-specific metrics"""
    total_revenue: float
    recurring_revenue: float
    new_revenue: float
    revenue_per_call: float
    revenue_per_agent: float
    revenue_growth_rate: float
    projected_monthly_revenue: float
    lifetime_value: float
    churn_rate: float
    retention_rate: float

class AgentMetrics(BaseModel):
    """Agent performance metrics"""
    agent_id: str
    agent_name: str
    calls_handled: int
    calls_successful: int
    success_rate: float
    average_call_time: int
    utilization_rate: float
    customer_rating: float
    revenue_generated: float
    first_call_resolution: float
    escalation_rate: float

class CampaignMetrics(BaseModel):
    """Campaign performance metrics"""
    campaign_id: str
    campaign_name: str
    status: str
    calls_made: int
    connections: int
    appointments: int
    sales: int
    contact_rate: float
    appointment_rate: float
    close_rate: float
    revenue: float
    cost: float
    roi: float

class GeographicMetrics(BaseModel):
    """Geographic performance breakdown"""
    region: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    calls: int
    success_rate: float
    revenue: float
    agent_count: int
    local_time_performance: Dict[str, float] = Field(default_factory=dict)

class PerformanceComparison(BaseModel):
    """Performance comparison data"""
    current_period: Dict[str, float]
    previous_period: Dict[str, float]
    industry_benchmark: Optional[Dict[str, float]] = None
    top_performers: Optional[Dict[str, float]] = None
    percentage_changes: Dict[str, float]
    improvement_areas: List[str]
    strengths: List[str]

class PredictiveMetrics(BaseModel):
    """Predictive analytics metrics"""
    prediction_type: str = Field(..., description="forecast, trend, anomaly")
    forecast_values: List[float]
    confidence_intervals: List[Dict[str, float]]
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    trend_direction: MetricDirection
    seasonal_patterns: Dict[str, Any] = Field(default_factory=dict)
    prediction_horizon: str
    generated_at: datetime

class RealTimeAlert(BaseModel):
    """Real-time metric alert"""
    id: str
    metric_name: str
    current_value: float
    threshold_value: float
    alert_type: str = Field(..., description="threshold, anomaly, trend")
    severity: str = Field(..., description="low, medium, high, critical")
    message: str
    triggered_at: datetime
    acknowledged: bool = False
    auto_resolve: bool = False

class MetricGoal(BaseModel):
    """Metric goal/target definition"""
    id: str
    metric_name: str
    target_value: float
    current_value: float
    progress_percentage: float = Field(..., ge=0.0, le=100.0)
    target_date: datetime
    goal_type: str = Field(..., description="daily, weekly, monthly, quarterly")
    status: str = Field(..., description="on_track, behind, ahead, achieved")
    created_by: str

class CustomMetric(BaseModel):
    """Custom metric definition"""
    id: str
    name: str
    description: str
    formula: str
    data_sources: List[str]
    aggregation_method: str = Field(..., description="sum, avg, count, max, min")
    unit: str
    category: str
    refresh_frequency: int = Field(..., description="Refresh frequency in seconds")
    created_by: str
    created_at: datetime

class MetricTrend(BaseModel):
    """Metric trend analysis"""
    metric_name: str
    trend_direction: MetricDirection
    trend_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of trend")
    rate_of_change: float
    trend_duration: int = Field(..., description="Duration in hours")
    seasonal_factor: Optional[float] = None
    anomalies_detected: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class QualityMetrics(BaseModel):
    """Call quality metrics"""
    call_quality_score: float = Field(..., ge=0.0, le=10.0)
    audio_quality: float = Field(..., ge=0.0, le=10.0)
    script_adherence: float = Field(..., ge=0.0, le=100.0)
    compliance_score: float = Field(..., ge=0.0, le=100.0)
    customer_satisfaction: float = Field(..., ge=0.0, le=10.0)
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    emotion_analysis: Dict[str, float] = Field(default_factory=dict)

class SystemMetrics(BaseModel):
    """System performance metrics"""
    service_name: str
    cpu_usage: float = Field(..., ge=0.0, le=100.0)
    memory_usage: float = Field(..., ge=0.0, le=100.0)
    disk_usage: float = Field(..., ge=0.0, le=100.0)
    network_latency: float
    request_rate: float
    error_rate: float = Field(..., ge=0.0, le=100.0)
    uptime: float = Field(..., ge=0.0, le=100.0)
    active_connections: int
    queue_depth: int
    response_times: Dict[str, float] = Field(default_factory=dict)

class BusinessMetrics(BaseModel):
    """High-level business metrics"""
    customer_acquisition_cost: float
    customer_lifetime_value: float
    monthly_recurring_revenue: float
    annual_recurring_revenue: float
    churn_rate: float = Field(..., ge=0.0, le=100.0)
    retention_rate: float = Field(..., ge=0.0, le=100.0)
    net_promoter_score: float = Field(..., ge=-100.0, le=100.0)
    market_share: float = Field(..., ge=0.0, le=100.0)
    competitive_win_rate: float = Field(..., ge=0.0, le=100.0)

class MetricsBenchmark(BaseModel):
    """Industry benchmarks for metrics"""
    industry: str
    metric_name: str
    benchmark_value: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_90: float
    data_source: str
    sample_size: int
    last_updated: datetime