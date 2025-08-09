"""
Metrics Endpoints
Real-time metrics, KPIs, and analytics data
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from services.metrics_service import MetricsService, get_metrics_service
from schemas.metrics import (
    LiveMetrics,
    MetricCard,
    TimeSeriesData,
    MetricsFilter,
    KPIReport
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

class MetricType(str, Enum):
    CALLS = "calls"
    REVENUE = "revenue"
    SUCCESS_RATE = "success_rate"
    AI_PERFORMANCE = "ai_performance"
    SYSTEM_HEALTH = "system_health"

class TimeRange(str, Enum):
    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"

@router.get("/live", response_model=LiveMetrics)
async def get_live_metrics(
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get real-time live metrics - updates every 2 seconds"""
    try:
        metrics = await metrics_service.get_live_metrics(current_user.organization_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live metrics: {str(e)}")

@router.get("/cards", response_model=List[MetricCard])
async def get_metric_cards(
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get metric cards for dashboard display"""
    try:
        cards = await metrics_service.get_metric_cards(current_user.organization_id)
        return cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metric cards: {str(e)}")

@router.get("/timeseries/{metric_type}", response_model=TimeSeriesData)
async def get_timeseries_data(
    metric_type: MetricType,
    time_range: TimeRange = TimeRange.DAY,
    granularity: str = Query("hour", description="Data granularity: minute, hour, day"),
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get time series data for charts and graphs"""
    try:
        data = await metrics_service.get_timeseries_data(
            organization_id=current_user.organization_id,
            metric_type=metric_type.value,
            time_range=time_range.value,
            granularity=granularity
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeseries data: {str(e)}")

@router.get("/kpis", response_model=KPIReport)
async def get_kpi_report(
    time_range: TimeRange = TimeRange.DAY,
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get comprehensive KPI report"""
    try:
        kpis = await metrics_service.get_kpi_report(
            organization_id=current_user.organization_id,
            time_range=time_range.value
        )
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get KPI report: {str(e)}")

@router.get("/global-stats")
async def get_global_platform_stats(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get global platform statistics - enterprise view"""
    try:
        stats = await metrics_service.get_global_platform_stats()
        return {
            "platform_stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "description": "🌍 Global Vocelio.ai Platform Statistics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get global stats: {str(e)}")

@router.get("/performance-breakdown")
async def get_performance_breakdown(
    breakdown_type: str = Query("agent", description="Breakdown type: agent, campaign, industry"),
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get performance breakdown by different dimensions"""
    try:
        breakdown = await metrics_service.get_performance_breakdown(
            organization_id=current_user.organization_id,
            breakdown_type=breakdown_type,
            limit=limit
        )
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance breakdown: {str(e)}")

@router.get("/ai-optimization-score")
async def get_ai_optimization_score(
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get AI optimization score and recommendations"""
    try:
        score_data = await metrics_service.get_ai_optimization_score(current_user.organization_id)
        return score_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI optimization score: {str(e)}")

@router.get("/revenue-analytics")
async def get_revenue_analytics(
    time_range: TimeRange = TimeRange.MONTH,
    include_projections: bool = True,
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get detailed revenue analytics and projections"""
    try:
        analytics = await metrics_service.get_revenue_analytics(
            organization_id=current_user.organization_id,
            time_range=time_range.value,
            include_projections=include_projections
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get revenue analytics: {str(e)}")

@router.get("/call-analytics")
async def get_call_analytics(
    time_range: TimeRange = TimeRange.DAY,
    include_geographic: bool = False,
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get comprehensive call analytics"""
    try:
        analytics = await metrics_service.get_call_analytics(
            organization_id=current_user.organization_id,
            time_range=time_range.value,
            include_geographic=include_geographic
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get call analytics: {str(e)}")

@router.get("/success-rate-trends")
async def get_success_rate_trends(
    time_range: TimeRange = TimeRange.WEEK,
    segment_by: str = Query("overall", description="Segment by: overall, agent, industry, time_of_day"),
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get success rate trends and analysis"""
    try:
        trends = await metrics_service.get_success_rate_trends(
            organization_id=current_user.organization_id,
            time_range=time_range.value,
            segment_by=segment_by
        )
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get success rate trends: {str(e)}")

@router.post("/custom-metric")
async def calculate_custom_metric(
    metric_definition: Dict[str, Any],
    time_range: TimeRange = TimeRange.DAY,
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Calculate custom metric based on user definition"""
    try:
        result = await metrics_service.calculate_custom_metric(
            organization_id=current_user.organization_id,
            metric_definition=metric_definition,
            time_range=time_range.value
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate custom metric: {str(e)}")

@router.get("/comparative-analysis")
async def get_comparative_analysis(
    compare_with: str = Query("previous_period", description="Compare with: previous_period, industry_average, top_performers"),
    time_range: TimeRange = TimeRange.MONTH,
    current_user: User = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get comparative analysis against benchmarks"""
    try:
        analysis = await metrics_service.get_comparative_analysis(
            organization_id=current_user.organization_id,
            compare_with=compare_with,
            time_range=time_range.value
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comparative analysis: {str(e)}")
