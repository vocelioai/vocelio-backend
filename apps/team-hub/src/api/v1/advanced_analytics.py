# apps/team-hub/src/api/v1/advanced_analytics.py
"""
Advanced Team Analytics Endpoints - Missing functionality from frontend analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from schemas.team_enhanced import *
from services.advanced_analytics_service import AdvancedAnalyticsService, TrainingService, PerformanceService

logger = logging.getLogger(__name__)
router = APIRouter()

# Advanced Team Analytics Endpoints
@router.get("/analytics/team-performance", response_model=Dict[str, Any])
async def get_team_performance_analytics(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    team_id: Optional[str] = Query(None, description="Specific team ID"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get comprehensive team performance analytics"""
    return await analytics_service.get_team_performance(period=period, team_id=team_id)

@router.get("/analytics/individual-performance", response_model=List[Dict[str, Any]])
async def get_individual_performance_analytics(
    user_id: Optional[str] = Query(None, description="Specific user ID"),
    period: str = Query("30d", description="Time period"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get individual team member performance analytics"""
    return await analytics_service.get_individual_performance(user_id=user_id, period=period)

@router.get("/analytics/productivity-trends", response_model=Dict[str, Any])
async def get_productivity_trends(
    granularity: str = Query("daily", description="Data granularity: hourly, daily, weekly"),
    period: str = Query("30d", description="Time period"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get productivity trends and patterns"""
    return await analytics_service.get_productivity_trends(granularity=granularity, period=period)

@router.get("/analytics/collaboration-metrics", response_model=Dict[str, Any])
async def get_collaboration_metrics(
    team_id: Optional[str] = Query(None, description="Specific team ID"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get team collaboration and communication metrics"""
    return await analytics_service.get_collaboration_metrics(team_id=team_id)

@router.get("/analytics/skill-gap-analysis", response_model=Dict[str, Any])
async def get_skill_gap_analysis(
    department: Optional[str] = Query(None, description="Department filter"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Analyze skill gaps across the team"""
    return await analytics_service.get_skill_gap_analysis(department=department)

@router.get("/analytics/workload-distribution", response_model=Dict[str, Any])
async def get_workload_distribution(
    period: str = Query("7d", description="Time period"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Analyze workload distribution across team members"""
    return await analytics_service.get_workload_distribution(period=period)

# Training Management Endpoints
@router.get("/training/programs", response_model=List[Dict[str, Any]])
async def get_training_programs(
    status: Optional[str] = Query(None, description="Program status filter"),
    training_service: TrainingService = Depends()
):
    """Get available training programs"""
    return await training_service.get_training_programs(status=status)

@router.post("/training/assign", response_model=Dict[str, Any])
async def assign_training(
    assignment: TrainingAssignment,
    training_service: TrainingService = Depends()
):
    """Assign training to team members"""
    return await training_service.assign_training(assignment)

@router.get("/training/progress/{user_id}", response_model=Dict[str, Any])
async def get_training_progress(
    user_id: str,
    training_service: TrainingService = Depends()
):
    """Get training progress for a user"""
    return await training_service.get_user_progress(user_id)

@router.get("/training/completion-rates", response_model=Dict[str, Any])
async def get_training_completion_rates(
    period: str = Query("30d", description="Time period"),
    department: Optional[str] = Query(None, description="Department filter"),
    training_service: TrainingService = Depends()
):
    """Get training completion rates and analytics"""
    return await training_service.get_completion_rates(period=period, department=department)

# Performance Management Endpoints
@router.get("/performance/reviews", response_model=List[Dict[str, Any]])
async def get_performance_reviews(
    user_id: Optional[str] = Query(None, description="Specific user"),
    status: Optional[str] = Query(None, description="Review status"),
    performance_service: PerformanceService = Depends()
):
    """Get performance reviews"""
    return await performance_service.get_reviews(user_id=user_id, status=status)

@router.post("/performance/goals", response_model=Dict[str, Any])
async def create_performance_goal(
    goal: PerformanceGoal,
    performance_service: PerformanceService = Depends()
):
    """Create performance goal for team member"""
    return await performance_service.create_goal(goal)

@router.get("/performance/goals/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_goals(
    user_id: str,
    status: Optional[str] = Query(None, description="Goal status"),
    performance_service: PerformanceService = Depends()
):
    """Get performance goals for a user"""
    return await performance_service.get_user_goals(user_id, status=status)

@router.put("/performance/goals/{goal_id}/progress", response_model=Dict[str, Any])
async def update_goal_progress(
    goal_id: str,
    progress: GoalProgress,
    performance_service: PerformanceService = Depends()
):
    """Update goal progress"""
    return await performance_service.update_goal_progress(goal_id, progress)

@router.get("/performance/kpis", response_model=Dict[str, Any])
async def get_team_kpis(
    period: str = Query("30d", description="Time period"),
    team_id: Optional[str] = Query(None, description="Specific team"),
    performance_service: PerformanceService = Depends()
):
    """Get team KPIs and performance indicators"""
    return await performance_service.get_team_kpis(period=period, team_id=team_id)

# Team Management Enhancement Endpoints
@router.get("/teams/hierarchy", response_model=Dict[str, Any])
async def get_team_hierarchy(
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get organizational team hierarchy"""
    return await analytics_service.get_team_hierarchy()

@router.get("/teams/capacity-planning", response_model=Dict[str, Any])
async def get_capacity_planning(
    period: str = Query("30d", description="Planning period"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get team capacity planning analysis"""
    return await analytics_service.get_capacity_planning(period=period)

@router.get("/teams/resource-allocation", response_model=Dict[str, Any])
async def get_resource_allocation(
    team_id: Optional[str] = Query(None, description="Specific team"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get resource allocation analysis"""
    return await analytics_service.get_resource_allocation(team_id=team_id)

@router.get("/teams/burnout-indicators", response_model=Dict[str, Any])
async def get_burnout_indicators(
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get team burnout risk indicators"""
    return await analytics_service.get_burnout_indicators()

@router.get("/teams/engagement-scores", response_model=Dict[str, Any])
async def get_engagement_scores(
    period: str = Query("30d", description="Time period"),
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get team engagement scores and trends"""
    return await analytics_service.get_engagement_scores(period=period)

# Real-time Team Monitoring
@router.get("/realtime/team-status", response_model=Dict[str, Any])
async def get_realtime_team_status(
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get real-time team status and availability"""
    return await analytics_service.get_realtime_status()

@router.get("/realtime/active-sessions", response_model=List[Dict[str, Any]])
async def get_active_sessions(
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get currently active work sessions"""
    return await analytics_service.get_active_sessions()

@router.get("/realtime/workload-alerts", response_model=List[Dict[str, Any]])
async def get_workload_alerts(
    analytics_service: AdvancedAnalyticsService = Depends()
):
    """Get real-time workload alerts and notifications"""
    return await analytics_service.get_workload_alerts()
