"""
Dashboard Endpoints
Main dashboard data, insights, and AI recommendations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta

from services.dashboard_service import DashboardService, get_dashboard_service
from schemas.dashboard import (
    DashboardOverview, 
    AIInsight, 
    GlobalMetrics,
    SystemHealth,
    DashboardFilter
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get complete dashboard overview with live metrics"""
    try:
        overview = await dashboard_service.get_dashboard_overview(current_user.organization_id)
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard overview: {str(e)}")

@router.get("/global-metrics", response_model=GlobalMetrics)
async def get_global_metrics(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get global platform metrics - enterprise view"""
    try:
        metrics = await dashboard_service.get_global_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get global metrics: {str(e)}")

@router.get("/ai-insights", response_model=List[AIInsight])
async def get_ai_insights(
    limit: int = 10,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get AI-generated insights and recommendations"""
    try:
        insights = await dashboard_service.get_ai_insights(
            organization_id=current_user.organization_id,
            limit=limit,
            priority_filter=priority
        )
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI insights: {str(e)}")

@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get global system health and uptime"""
    try:
        health = await dashboard_service.get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

@router.get("/live-stats")
async def get_live_stats(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get live statistics - updates every 2 seconds"""
    try:
        stats = await dashboard_service.get_live_stats(current_user.organization_id)
        return {
            "live_metrics": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "next_update": (datetime.utcnow() + timedelta(seconds=2)).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live stats: {str(e)}")

@router.post("/trigger-ai-analysis")
async def trigger_ai_analysis(
    background_tasks: BackgroundTasks,
    analysis_type: Optional[str] = "performance",
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Trigger AI analysis for performance optimization"""
    try:
        # Add background task for AI analysis
        background_tasks.add_task(
            dashboard_service.run_ai_analysis,
            current_user.organization_id,
            analysis_type
        )
        
        return {
            "message": "🧠 AI Analysis triggered successfully",
            "analysis_type": analysis_type,
            "estimated_completion": "2-5 minutes",
            "organization_id": current_user.organization_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger AI analysis: {str(e)}")

@router.get("/performance-summary")
async def get_performance_summary(
    timeframe: str = "24h",
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get performance summary for specified timeframe"""
    try:
        summary = await dashboard_service.get_performance_summary(
            organization_id=current_user.organization_id,
            timeframe=timeframe
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")

@router.get("/notifications")
async def get_dashboard_notifications(
    unread_only: bool = True,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get dashboard notifications and alerts"""
    try:
        notifications = await dashboard_service.get_notifications(
            organization_id=current_user.organization_id,
            unread_only=unread_only,
            limit=limit
        )
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Mark notification as read"""
    try:
        await dashboard_service.mark_notification_read(notification_id, current_user.id)
        return {"message": "Notification marked as read", "notification_id": notification_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

@router.get("/quick-actions")
async def get_quick_actions(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get AI-recommended quick actions"""
    try:
        actions = await dashboard_service.get_quick_actions(current_user.organization_id)
        return actions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quick actions: {str(e)}")

@router.post("/execute-action")
async def execute_quick_action(
    action_id: str,
    parameters: Dict[str, Any] = {},
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Execute a quick action"""
    try:
        # Add background task for action execution
        background_tasks.add_task(
            dashboard_service.execute_action,
            action_id,
            parameters,
            current_user.id
        )
        
        return {
            "message": "⚡ Action execution started",
            "action_id": action_id,
            "status": "processing",
            "estimated_completion": "30 seconds - 2 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute action: {str(e)}")
