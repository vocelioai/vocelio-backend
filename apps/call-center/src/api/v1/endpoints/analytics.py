# apps/call-center/src/api/v1/endpoints/analytics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from services.analytics_service import AnalyticsService
from schemas.analytics import (
    GlobalStats, PerformanceBreakdown, VolumeMetrics, 
    CapacityMetrics, RealTimeKPIs, AgentPerformance
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/global-stats", response_model=GlobalStats)
async def get_global_statistics(
    period: str = Query("today", regex="^(today|week|month|quarter|year)$"),
    timezone: str = Query("UTC"),
    current_user: User = Depends(get_current_user)
):
    """Get global call center statistics"""
    analytics_service = AnalyticsService()
    
    try:
        stats = await analytics_service.get_global_stats(period, timezone)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting global stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get global statistics")

@router.get("/performance-breakdown", response_model=PerformanceBreakdown)
async def get_performance_breakdown(
    period: str = Query("today", regex="^(today|week|month)$"),
    breakdown_by: str = Query("hour", regex="^(hour|day|week|agent|department)$"),
    current_user: User = Depends(get_current_user)
):
    """Get detailed performance breakdown"""
    analytics_service = AnalyticsService()
    
    try:
        breakdown = await analytics_service.get_performance_breakdown(period, breakdown_by)
        return breakdown
        
    except Exception as e:
        logger.error(f"Error getting performance breakdown: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance breakdown")

@router.get("/volume-metrics", response_model=VolumeMetrics)
async def get_volume_metrics(
    period: str = Query("today", regex="^(today|week|month)$"),
    call_type: Optional[str] = Query(None, regex="^(inbound|outbound|all)$"),
    current_user: User = Depends(get_current_user)
):
    """Get call volume analytics"""
    analytics_service = AnalyticsService()
    
    try:
        metrics = await analytics_service.get_volume_metrics(period, call_type)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting volume metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get volume metrics")

@router.get("/capacity-metrics", response_model=CapacityMetrics)
async def get_capacity_metrics(
    include_forecast: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """Get system capacity metrics and utilization"""
    analytics_service = AnalyticsService()
    
    try:
        metrics = await analytics_service.get_capacity_metrics(include_forecast)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting capacity metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get capacity metrics")

@router.get("/real-time-kpis", response_model=RealTimeKPIs)
async def get_real_time_kpis(
    refresh_interval: int = Query(30, ge=5, le=300),
    current_user: User = Depends(get_current_user)
):
    """Get real-time Key Performance Indicators"""
    analytics_service = AnalyticsService()
    
    try:
        kpis = await analytics_service.get_real_time_kpis()
        return kpis
        
    except Exception as e:
        logger.error(f"Error getting real-time KPIs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get real-time KPIs")

@router.get("/agent-performance", response_model=List[AgentPerformance])
async def get_agent_performance(
    period: str = Query("today", regex="^(today|week|month)$"),
    agent_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get agent performance metrics"""
    analytics_service = AnalyticsService()
    
    try:
        filters = {}
        if agent_id:
            filters["agent_id"] = agent_id
        if department and department != "all":
            filters["department"] = department
        
        performance = await analytics_service.get_agent_performance(
            period, filters, limit
        )
        return performance
        
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent performance")

@router.get("/conversion-funnel")
async def get_conversion_funnel(
    period: str = Query("today", regex="^(today|week|month)$"),
    campaign_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get conversion funnel analytics"""
    analytics_service = AnalyticsService()
    
    try:
        funnel = await analytics_service.get_conversion_funnel(period, campaign_id)
        return funnel
        
    except Exception as e:
        logger.error(f"Error getting conversion funnel: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversion funnel")

@router.get("/trend-analysis")
async def get_trend_analysis(
    metric: str = Query(..., regex="^(calls|conversions|revenue|duration|satisfaction)$"),
    period: str = Query("week", regex="^(week|month|quarter|year)$"),
    comparison_period: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get trend analysis for specific metrics"""
    analytics_service = AnalyticsService()
    
    try:
        trends = await analytics_service.get_trend_analysis(
            metric, period, comparison_period
        )
        return trends
        
    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trend analysis")

@router.get("/geographic-distribution")
async def get_geographic_distribution(
    period: str = Query("today", regex="^(today|week|month)$"),
    metric: str = Query("calls", regex="^(calls|conversions|revenue)$"),
    current_user: User = Depends(get_current_user)
):
    """Get geographic distribution of calls/conversions"""
    analytics_service = AnalyticsService()
    
    try:
        distribution = await analytics_service.get_geographic_distribution(period, metric)
        return distribution
        
    except Exception as e:
        logger.error(f"Error getting geographic distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to get geographic distribution")

@router.get("/peak-hours")
async def get_peak_hours_analysis(
    period: str = Query("week", regex="^(week|month|quarter)$"),
    timezone: str = Query("UTC"),
    current_user: User = Depends(get_current_user)
):
    """Get peak hours analysis"""
    analytics_service = AnalyticsService()
    
    try:
        peak_analysis = await analytics_service.get_peak_hours_analysis(period, timezone)
        return peak_analysis
        
    except Exception as e:
        logger.error(f"Error getting peak hours analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get peak hours analysis")

@router.get("/satisfaction-metrics")
async def get_satisfaction_metrics(
    period: str = Query("today", regex="^(today|week|month)$"),
    breakdown_by: str = Query("overall", regex="^(overall|agent|department|campaign)$"),
    current_user: User = Depends(get_current_user)
):
    """Get customer satisfaction metrics"""
    analytics_service = AnalyticsService()
    
    try:
        satisfaction = await analytics_service.get_satisfaction_metrics(period, breakdown_by)
        return satisfaction
        
    except Exception as e:
        logger.error(f"Error getting satisfaction metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get satisfaction metrics")

@router.get("/revenue-analytics")
async def get_revenue_analytics(
    period: str = Query("today", regex="^(today|week|month|quarter|year)$"),
    breakdown_by: str = Query("time", regex="^(time|agent|campaign|product)$"),
    current_user: User = Depends(get_current_user)
):
    """Get revenue analytics and ROI metrics"""
    analytics_service = AnalyticsService()
    
    try:
        revenue = await analytics_service.get_revenue_analytics(period, breakdown_by)
        return revenue
        
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get revenue analytics")

@router.post("/custom-report")
async def generate_custom_report(
    report_config: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Generate custom analytics report"""
    analytics_service = AnalyticsService()
    
    try:
        # Validate report configuration
        required_fields = ["metrics", "period", "filters"]
        if not all(field in report_config for field in required_fields):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: metrics, period, filters"
            )
        
        report = await analytics_service.generate_custom_report(report_config, current_user.id)
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating custom report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate custom report")

@router.get("/export/{report_type}")
async def export_analytics_data(
    report_type: str,
    format: str = Query("json", regex="^(json|csv|excel|pdf)$"),
    period: str = Query("today", regex="^(today|week|month)$"),
    current_user: User = Depends(get_current_user)
):
    """Export analytics data in various formats"""
    analytics_service = AnalyticsService()
    
    try:
        export_data = await analytics_service.export_data(report_type, format, period)
        
        # Return appropriate response based on format
        if format == "json":
            return export_data
        else:
            # For file formats, return download URL or file content
            return {"download_url": export_data.get("download_url"), "file_id": export_data.get("file_id")}
        
    except Exception as e:
        logger.error(f"Error exporting analytics data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export analytics data")
