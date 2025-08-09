# apps/team-hub/src/api/v1/endpoints/dashboard.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from shared.database.client import get_database
from shared.auth.dependencies import get_current_user
from schemas.response import APIResponse, TeamMetrics, DepartmentSummary, TeamStatusSummary
from services.user_service import UserService
from services.team_service import TeamService
from models.user import User

router = APIRouter()

@router.get("/metrics", response_model=APIResponse)
async def get_team_metrics(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive team metrics for dashboard"""
    
    user_service = UserService(db)
    
    try:
        metrics = await user_service.get_team_metrics(current_user.organization_id)
        
        return APIResponse(
            message="Team metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/departments", response_model=APIResponse)
async def get_department_summary(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get department summary with counts and performance"""
    
    user_service = UserService(db)
    
    try:
        departments = await user_service.get_department_summary(current_user.organization_id)
        
        return APIResponse(
            message="Department summary retrieved successfully",
            data=departments
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status-summary", response_model=APIResponse)
async def get_team_status_summary(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get team status breakdown"""
    
    user_service = UserService(db)
    
    try:
        metrics = await user_service.get_team_metrics(current_user.organization_id)
        status_summary = metrics.get("status_breakdown", {})
        
        return APIResponse(
            message="Team status summary retrieved successfully",
            data=status_summary
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/performance-trends", response_model=APIResponse)
async def get_performance_trends(
    days: int = 30,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get performance trends over time (mock data for now)"""
    
    # In a real implementation, this would query historical performance data
    # For now, we'll return mock trend data
    mock_trends = {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "datasets": [
            {
                "label": "Team Performance",
                "data": [92.1, 93.8, 94.2, 94.7],
                "borderColor": "rgb(59, 130, 246)",
                "backgroundColor": "rgba(59, 130, 246, 0.1)"
            },
            {
                "label": "Customer Satisfaction",
                "data": [95.2, 96.1, 96.8, 97.1],
                "borderColor": "rgb(16, 185, 129)",
                "backgroundColor": "rgba(16, 185, 129, 0.1)"
            }
        ]
    }
    
    return APIResponse(
        message="Performance trends retrieved successfully",
        data=mock_trends
    )

@router.get("/top-performers", response_model=APIResponse)
async def get_top_performers(
    limit: int = 10,
    metric: str = "performance_score",
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get top performing team members"""
    
    user_service = UserService(db)
    
    try:
        from schemas.user import UserFilters
        
        # Get users sorted by the specified metric
        filters = UserFilters(
            page=1,
            size=limit,
            sort_by=metric,
            sort_order="desc"
        )
        
        users, _ = await user_service.get_users_with_filters(filters, current_user.organization_id)
        
        top_performers = []
        for i, user in enumerate(users):
            top_performers.append({
                "rank": i + 1,
                "id": user.id,
                "name": user.name,
                "avatar": user.avatar,
                "role": user.role,
                "department": user.department,
                "performance_score": user.performance_score,
                "calls_today": user.calls_today,
                "customer_satisfaction": user.customer_satisfaction
            })
        
        return APIResponse(
            message="Top performers retrieved successfully",
            data=top_performers
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/recent-activities", response_model=APIResponse)
async def get_recent_activities(
    limit: int = 20,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get recent team activities (mock data for now)"""
    
    # In a real implementation, this would query an activity log
    # For now, we'll return mock activity data
    mock_activities = [
        {
            "id": "act_001",
            "type": "user_status_change",
            "description": "Sarah Chen changed status to On Call",
            "user": {"name": "Sarah Chen", "avatar": "👩‍💼"},
            "timestamp": "2024-11-28T10:30:00Z",
            "icon": "phone"
        },
        {
            "id": "act_002",
            "type": "performance_milestone",
            "description": "Marcus Rodriguez achieved 95% satisfaction rate",
            "user": {"name": "Marcus Rodriguez", "avatar": "👨‍💻"},
            "timestamp": "2024-11-28T10:15:00Z",
            "icon": "trophy"
        },
        {
            "id": "act_003",
            "type": "team_join",
            "description": "Elena Vasquez joined Sales Team Alpha",
            "user": {"name": "Elena Vasquez", "avatar": "👩‍⚖️"},
            "timestamp": "2024-11-28T09:45:00Z",
            "icon": "user-plus"
        },
        {
            "id": "act_004",
            "type": "certification_earned",
            "description": "David Kim earned TCPA Advanced certification",
            "user": {"name": "David Kim", "avatar": "👨‍🔧"},
            "timestamp": "2024-11-28T09:30:00Z",
            "icon": "award"
        }
    ]
    
    return APIResponse(
        message="Recent activities retrieved successfully",
        data=mock_activities[:limit]
    )

@router.get("/department/{department_name}", response_model=APIResponse)
async def get_department_details(
    department_name: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific department"""
    
    user_service = UserService(db)
    team_service = TeamService(db)
    
    try:
        # Get users in department
        from schemas.user import UserFilters
        filters = UserFilters(department=department_name, page=1, size=100)
        users, total_users = await user_service.get_users_with_filters(filters, current_user.organization_id)
        
        # Get teams in department
        teams = await team_service.get_teams_by_department(current_user.organization_id, department_name)
        
        # Calculate department metrics
        if users:
            avg_performance = sum(user.performance_score for user in users) / len(users)
            total_calls = sum(user.calls_today for user in users)
            avg_satisfaction = sum(user.customer_satisfaction for user in users) / len(users)
            
            status_counts = {}
            for user in users:
                status_counts[user.status.value] = status_counts.get(user.status.value, 0) + 1
        else:
            avg_performance = 0
            total_calls = 0
            avg_satisfaction = 0
            status_counts = {}
        
        department_details = {
            "name": department_name,
            "total_members": total_users,
            "total_teams": len(teams),
            "avg_performance": round(avg_performance, 1),
            "total_calls_today": total_calls,
            "avg_satisfaction": round(avg_satisfaction, 1),
            "status_breakdown": status_counts,
            "teams": [{"id": team.id, "name": team.name, "member_count": team.member_count} for team in teams],
            "top_performers": [
                {
                    "id": user.id,
                    "name": user.name,
                    "avatar": user.avatar,
                    "performance_score": user.performance_score
                }
                for user in sorted(users, key=lambda x: x.performance_score, reverse=True)[:5]
            ]
        }
        
        return APIResponse(
            message="Department details retrieved successfully",
            data=department_details
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/call-volume", response_model=APIResponse)
async def get_call_volume_analytics(
    period: str = "today",  # today, week, month
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get call volume analytics"""
    
    # Mock data - in real implementation, this would come from call center service
    if period == "today":
        mock_data = {
            "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
            "data": [450, 320, 1250, 1890, 2100, 1650],
            "total": 18947,
            "average_per_hour": 789,
            "peak_hour": "16:00-17:00",
            "peak_volume": 2100
        }
    elif period == "week":
        mock_data = {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "data": [15200, 18947, 17800, 19200, 16500, 8900, 6200],
            "total": 102747,
            "average_per_day": 14678,
            "peak_day": "Thursday",
            "peak_volume": 19200
        }
    else:  # month
        mock_data = {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "data": [98500, 102747, 105200, 89300],
            "total": 395747,
            "average_per_week": 98937,
            "peak_week": "Week 3",
            "peak_volume": 105200
        }
    
    return APIResponse(
        message="Call volume analytics retrieved successfully",
        data=mock_data
    )

@router.get("/analytics/performance-distribution", response_model=APIResponse)
async def get_performance_distribution(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get performance score distribution across team"""
    
    user_service = UserService(db)
    
    try:
        from schemas.user import UserFilters
        filters = UserFilters(page=1, size=1000)  # Get all users
        users, _ = await user_service.get_users_with_filters(filters, current_user.organization_id)
        
        # Create performance buckets
        buckets = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "0-59": 0
        }
        
        for user in users:
            score = user.performance_score
            if score >= 90:
                buckets["90-100"] += 1
            elif score >= 80:
                buckets["80-89"] += 1
            elif score >= 70:
                buckets["70-79"] += 1
            elif score >= 60:
                buckets["60-69"] += 1
            else:
                buckets["0-59"] += 1
        
        distribution_data = {
            "labels": list(buckets.keys()),
            "data": list(buckets.values()),
            "total_users": len(users),
            "avg_score": round(sum(user.performance_score for user in users) / len(users), 1) if users else 0,
            "high_performers": buckets["90-100"],  # 90%+ performers
            "improvement_needed": buckets["0-59"] + buckets["60-69"]  # <70% performers
        }
        
        return APIResponse(
            message="Performance distribution retrieved successfully",
            data=distribution_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports/export", response_model=APIResponse)
async def export_team_report(
    format: str = "json",  # json, csv, xlsx
    include_metrics: bool = True,
    include_members: bool = True,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Export comprehensive team report"""
    
    user_service = UserService(db)
    
    try:
        # Get team metrics
        metrics = await user_service.get_team_metrics(current_user.organization_id) if include_metrics else {}
        
        # Get team members
        members = []
        if include_members:
            from schemas.user import UserFilters
            filters = UserFilters(page=1, size=1000)
            users, _ = await user_service.get_users_with_filters(filters, current_user.organization_id)
            members = [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "department": user.department,
                    "status": user.status.value,
                    "performance_score": user.performance_score,
                    "calls_today": user.calls_today,
                    "customer_satisfaction": user.customer_satisfaction,
                    "location": user.location,
                    "join_date": user.join_date.isoformat() if user.join_date else None
                }
                for user in users
            ]
        
        # Get departments
        departments = await user_service.get_department_summary(current_user.organization_id)
        
        report_data = {
            "organization_id": current_user.organization_id,
            "generated_at": "2024-11-28T12:00:00Z",
            "generated_by": current_user.name,
            "report_type": "comprehensive_team_report",
            "metrics": metrics,
            "departments": departments,
            "members": members,
            "summary": {
                "total_members": len(members),
                "departments_count": len(departments),
                "export_format": format
            }
        }
        
        # In a real implementation, you would:
        # 1. Generate the file in the requested format
        # 2. Store it temporarily or in cloud storage
        # 3. Return a download URL
        
        return APIResponse(
            message=f"Team report exported successfully in {format.upper()} format",
            data={
                "download_url": f"/api/v1/reports/download/{current_user.organization_id}_{format}",
                "expires_at": "2024-11-28T18:00:00Z",
                "file_size": "2.5MB",
                "record_count": len(members)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))