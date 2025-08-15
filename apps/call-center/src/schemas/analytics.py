"""
Analytics Schema Definitions for Call Center
Comprehensive data models for analytics, reporting, and KPIs
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class TimeFrame(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


class MetricType(str, Enum):
    COUNT = "count"
    PERCENTAGE = "percentage"
    AVERAGE = "average"
    TOTAL = "total"
    RATE = "rate"
    DURATION = "duration"


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


class GlobalStats(BaseModel):
    total_calls: int = Field(..., description="Total calls processed")
    answered_calls: int = Field(..., description="Total answered calls")
    missed_calls: int = Field(..., description="Total missed calls")
    average_call_duration: float = Field(..., description="Average call duration in seconds")
    total_call_time: float = Field(..., description="Total call time in seconds")
    answer_rate: float = Field(..., description="Answer rate percentage")
    satisfaction_score: float = Field(..., description="Average satisfaction score")
    revenue_generated: float = Field(..., description="Total revenue generated")
    cost_per_call: float = Field(..., description="Average cost per call")
    conversion_rate: float = Field(..., description="Overall conversion rate")
    last_updated: datetime = Field(..., description="Last update timestamp")


class PerformanceBreakdown(BaseModel):
    inbound_calls: int = Field(..., description="Inbound calls count")
    outbound_calls: int = Field(..., description="Outbound calls count")
    successful_connects: int = Field(..., description="Successful connections")
    failed_attempts: int = Field(..., description="Failed connection attempts")
    average_wait_time: float = Field(..., description="Average wait time in seconds")
    average_handle_time: float = Field(..., description="Average handle time in seconds")
    first_call_resolution: float = Field(..., description="First call resolution rate")
    transfer_rate: float = Field(..., description="Call transfer rate")
    abandon_rate: float = Field(..., description="Call abandon rate")
    quality_score: float = Field(..., description="Overall quality score")


class VolumeMetrics(BaseModel):
    calls_by_hour: Dict[str, int] = Field(..., description="Calls count by hour")
    calls_by_day: Dict[str, int] = Field(..., description="Calls count by day")
    peak_hour: str = Field(..., description="Peak hour of the day")
    peak_day: str = Field(..., description="Peak day of the week")
    volume_trend: str = Field(..., description="Volume trend (increasing/decreasing/stable)")
    predicted_volume: Dict[str, int] = Field(..., description="Predicted future volume")
    seasonal_patterns: Dict[str, Any] = Field(default_factory=dict, description="Seasonal patterns")


class CapacityMetrics(BaseModel):
    max_concurrent_calls: int = Field(..., description="Maximum concurrent calls supported")
    current_active_calls: int = Field(..., description="Current active calls")
    peak_concurrent_calls: int = Field(..., description="Peak concurrent calls today")
    utilization_rate: float = Field(..., description="Current utilization rate")
    agent_capacity: int = Field(..., description="Total agent capacity")
    available_agents: int = Field(..., description="Currently available agents")
    queue_length: int = Field(..., description="Current queue length")
    estimated_wait_time: float = Field(..., description="Estimated wait time in seconds")


class RealTimeKPIs(BaseModel):
    calls_in_progress: int = Field(..., description="Calls currently in progress")
    calls_waiting: int = Field(..., description="Calls waiting in queue")
    average_wait_time: float = Field(..., description="Current average wait time")
    service_level: float = Field(..., description="Current service level percentage")
    abandon_rate_today: float = Field(..., description="Today's abandon rate")
    answer_rate_today: float = Field(..., description="Today's answer rate")
    agent_utilization: float = Field(..., description="Current agent utilization")
    system_health: str = Field(..., description="Overall system health status")
    last_refresh: datetime = Field(..., description="Last data refresh time")


class AgentPerformance(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent name")
    calls_handled: int = Field(..., description="Total calls handled")
    average_handle_time: float = Field(..., description="Average handle time")
    customer_satisfaction: float = Field(..., description="Customer satisfaction score")
    first_call_resolution: float = Field(..., description="First call resolution rate")
    adherence_score: float = Field(..., description="Schedule adherence score")
    quality_score: float = Field(..., description="Quality assessment score")
    sales_conversions: int = Field(..., description="Sales conversions achieved")
    revenue_generated: float = Field(..., description="Revenue generated by agent")
    last_activity: datetime = Field(..., description="Last activity timestamp")


class ConversionFunnel(BaseModel):
    total_contacts: int = Field(..., description="Total contacts attempted")
    connections_made: int = Field(..., description="Successful connections")
    qualified_leads: int = Field(..., description="Qualified leads identified")
    presentations_given: int = Field(..., description="Presentations completed")
    proposals_sent: int = Field(..., description="Proposals sent")
    closes_achieved: int = Field(..., description="Sales closed")
    conversion_rates: Dict[str, float] = Field(..., description="Conversion rates at each stage")
    revenue_by_stage: Dict[str, float] = Field(..., description="Revenue by funnel stage")


class TrendAnalysis(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    time_series: List[Dict[str, Union[str, float]]] = Field(..., description="Time series data")
    trend_direction: str = Field(..., description="Trend direction (up/down/stable)")
    percentage_change: float = Field(..., description="Percentage change from previous period")
    forecast: List[Dict[str, Union[str, float]]] = Field(..., description="Forecasted values")
    confidence_interval: float = Field(..., description="Forecast confidence interval")
    seasonal_factors: Dict[str, float] = Field(default_factory=dict, description="Seasonal adjustment factors")


class GeographicDistribution(BaseModel):
    country_stats: Dict[str, Dict[str, Any]] = Field(..., description="Statistics by country")
    state_stats: Dict[str, Dict[str, Any]] = Field(..., description="Statistics by state/province")
    city_stats: Dict[str, Dict[str, Any]] = Field(..., description="Statistics by city")
    timezone_distribution: Dict[str, int] = Field(..., description="Call distribution by timezone")
    regional_performance: Dict[str, float] = Field(..., description="Performance metrics by region")


class PeakHoursAnalysis(BaseModel):
    hourly_distribution: Dict[str, int] = Field(..., description="Call distribution by hour")
    peak_hours: List[str] = Field(..., description="Identified peak hours")
    off_peak_hours: List[str] = Field(..., description="Identified off-peak hours")
    staff_recommendations: Dict[str, int] = Field(..., description="Recommended staffing by hour")
    efficiency_scores: Dict[str, float] = Field(..., description="Efficiency scores by hour")
    cost_analysis: Dict[str, float] = Field(..., description="Cost analysis by time period")


class SatisfactionMetrics(BaseModel):
    overall_satisfaction: float = Field(..., description="Overall satisfaction score")
    satisfaction_by_channel: Dict[str, float] = Field(..., description="Satisfaction by communication channel")
    satisfaction_trend: List[Dict[str, Union[str, float]]] = Field(..., description="Satisfaction trend over time")
    nps_score: float = Field(..., description="Net Promoter Score")
    detractor_percentage: float = Field(..., description="Percentage of detractors")
    promoter_percentage: float = Field(..., description="Percentage of promoters")
    feedback_categories: Dict[str, int] = Field(..., description="Categorized feedback counts")
    improvement_areas: List[str] = Field(..., description="Identified improvement areas")


class RevenueAnalytics(BaseModel):
    total_revenue: float = Field(..., description="Total revenue generated")
    revenue_by_channel: Dict[str, float] = Field(..., description="Revenue by communication channel")
    revenue_by_agent: Dict[str, float] = Field(..., description="Revenue by agent")
    average_deal_size: float = Field(..., description="Average deal size")
    revenue_per_call: float = Field(..., description="Average revenue per call")
    cost_per_acquisition: float = Field(..., description="Cost per customer acquisition")
    roi_by_campaign: Dict[str, float] = Field(..., description="ROI by marketing campaign")
    revenue_forecast: Dict[str, float] = Field(..., description="Revenue forecast")


class CustomReportRequest(BaseModel):
    report_name: str = Field(..., description="Name for the custom report")
    metrics: List[str] = Field(..., description="Metrics to include in report")
    dimensions: List[str] = Field(..., description="Dimensions to group by")
    date_range: Dict[str, str] = Field(..., description="Date range for the report")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    format: ExportFormat = Field(..., description="Desired export format")
    schedule: Optional[str] = Field(None, description="Schedule for recurring reports")


class CustomReportResponse(BaseModel):
    report_id: str = Field(..., description="Generated report identifier")
    report_name: str = Field(..., description="Report name")
    status: str = Field(..., description="Report generation status")
    data: List[Dict[str, Any]] = Field(..., description="Report data")
    metadata: Dict[str, Any] = Field(..., description="Report metadata")
    created_at: datetime = Field(..., description="Report creation timestamp")
    expires_at: datetime = Field(..., description="Report expiration timestamp")


class ExportRequest(BaseModel):
    data_type: str = Field(..., description="Type of data to export")
    format: ExportFormat = Field(..., description="Export format")
    date_range: Dict[str, str] = Field(..., description="Date range for export")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Export filters")
    include_metadata: bool = Field(True, description="Include metadata in export")


class ExportResponse(BaseModel):
    export_id: str = Field(..., description="Export job identifier")
    download_url: str = Field(..., description="Download URL for the export")
    status: str = Field(..., description="Export status")
    file_size: int = Field(..., description="File size in bytes")
    record_count: int = Field(..., description="Number of records exported")
    created_at: datetime = Field(..., description="Export creation timestamp")
    expires_at: datetime = Field(..., description="Download link expiration")


class AnalyticsFilter(BaseModel):
    start_date: Optional[date] = Field(None, description="Start date for analytics")
    end_date: Optional[date] = Field(None, description="End date for analytics")
    agent_ids: Optional[List[str]] = Field(None, description="Filter by specific agents")
    departments: Optional[List[str]] = Field(None, description="Filter by departments")
    call_types: Optional[List[str]] = Field(None, description="Filter by call types")
    customer_segments: Optional[List[str]] = Field(None, description="Filter by customer segments")
    time_frame: TimeFrame = Field(TimeFrame.DAY, description="Time frame for aggregation")
    include_weekends: bool = Field(True, description="Include weekends in analysis")
    timezone: str = Field("UTC", description="Timezone for date calculations")
