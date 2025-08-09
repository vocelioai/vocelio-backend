# apps/team-hub/src/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from shared.database.client import get_database
from shared.auth.dependencies import get_current_user, require_permissions
from schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserSummary, UserFilters, UserStatus
)
from schemas.response import APIResponse, PaginatedResponse, PaginationMeta
from services.user_service import UserService
from models.user import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_users(
    search: Optional[str] = Query(None, description="Search in name, email, role, department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_performance: Optional[float] = Query(None, ge=0, le=100, description="Minimum performance score"),
    max_performance: Optional[float] = Query(None, ge=0, le=100, description="Maximum performance score"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills"),
    certifications: Optional[List[str]] = Query(None, description="Filter by certifications"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("name", regex="^(name|email|role|department|status|performance_score|join_date)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of users with filtering and search"""
    
    filters = UserFilters(
        search=search,
        role=role,
        department=department,
        status=status,
        location=location,
        min_performance=min_performance,
        max_performance=max_performance,
        skills=skills or [],
        certifications=certifications or [],
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    user_service = UserService(db)
    users, total_count = await user_service.get_users_with_filters(filters, current_user.organization_id)
    
    # Calculate pagination metadata
    total_pages = (total_count + size - 1) // size
    has_next = page < total_pages
    has_prev = page > 1
    
    return PaginatedResponse(
        data=[UserSummary.from_orm(user) for user in users],
        meta=PaginationMeta(
            page=page,
            size=size,
            total=total_count,
            pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
    )

@router.post("/", response_model=APIResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["user:create"]))
):
    """Create a new user"""
    
    user_service = UserService(db)
    
    # Set organization from current user
    user_data.organization_id = current_user.organization_id
    
    try:
        new_user = await user_service.create_user(user_data)
        
        # Add background task for sending welcome email
        # background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
        
        return APIResponse(
            message="User created successfully",
            data=UserResponse.from_orm(new_user)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=APIResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user belongs to same organization
    if user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return APIResponse(
        message="User retrieved successfully",
        data=UserResponse.from_orm(user)
    )

@router.put("/{user_id}", response_model=APIResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["user:update"]))
):
    """Update user information"""
    
    user_service = UserService(db)
    
    # Check if user exists and belongs to same organization
    existing_user = await user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if existing_user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        updated_user = await user_service.update_user(user_id, user_data)
        
        return APIResponse(
            message="User updated successfully",
            data=UserResponse.from_orm(updated_user)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{user_id}/status", response_model=APIResponse)
async def update_user_status(
    user_id: str,
    status: UserStatus,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Update user status"""
    
    user_service = UserService(db)
    
    # Users can update their own status, or admins can update any status
    if user_id != current_user.id and not current_user.has_permission("user:update"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        updated_user = await user_service.update_user_status(user_id, status)
        
        return APIResponse(
            message="User status updated successfully",
            data={"status": updated_user.status}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{user_id}/metrics", response_model=APIResponse)
async def update_user_metrics(
    user_id: str,
    metrics: Dict[str, Any],
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["user:update"]))
):
    """Update user performance metrics"""
    
    user_service = UserService(db)
    
    try:
        updated_user = await user_service.update_performance_metrics(user_id, metrics)
        
        return APIResponse(
            message="User metrics updated successfully",
            data={
                "performance_score": updated_user.performance_score,
                "calls_today": updated_user.calls_today,
                "avg_call_duration": updated_user.avg_call_duration,
                "customer_satisfaction": updated_user.customer_satisfaction
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["user:delete"]))
):
    """Delete (deactivate) a user"""
    
    user_service = UserService(db)
    
    # Check if user exists and belongs to same organization
    existing_user = await user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if existing_user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    try:
        await user_service.delete_user(user_id)
        
        return APIResponse(
            message="User deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/roles/available", response_model=APIResponse)
async def get_available_roles(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get list of available roles in organization"""
    
    user_service = UserService(db)
    roles = await user_service.get_available_roles(current_user.organization_id)
    
    return APIResponse(
        message="Available roles retrieved successfully",
        data=roles
    )

@router.get("/departments/available", response_model=APIResponse)
async def get_available_departments(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get list of available departments in organization"""
    
    user_service = UserService(db)
    departments = await user_service.get_available_departments(current_user.organization_id)
    
    return APIResponse(
        message="Available departments retrieved successfully",
        data=departments
    )

# apps/team-hub/src/api/v1/endpoints/teams.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from shared.database.client import get_database
from shared.auth.dependencies import get_current_user, require_permissions
from schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamFilters
from schemas.response import APIResponse, PaginatedResponse, PaginationMeta
from schemas.user import UserSummary
from services.team_service import TeamService
from models.user import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_teams(
    search: Optional[str] = Query(None, description="Search in team name, description, department"),
    department: Optional[str] = Query(None, description="Filter by department"),
    min_size: Optional[int] = Query(None, ge=1, description="Minimum team size"),
    max_size: Optional[int] = Query(None, ge=1, description="Maximum team size"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("name", regex="^(name|department|member_count|performance_score|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of teams with filtering and search"""
    
    filters = TeamFilters(
        search=search,
        department=department,
        min_size=min_size,
        max_size=max_size,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    team_service = TeamService(db)
    teams, total_count = await team_service.get_teams_with_filters(filters, current_user.organization_id)
    
    # Calculate pagination metadata
    total_pages = (total_count + size - 1) // size
    has_next = page < total_pages
    has_prev = page > 1
    
    return PaginatedResponse(
        data=[TeamResponse.from_orm(team) for team in teams],
        meta=PaginationMeta(
            page=page,
            size=size,
            total=total_count,
            pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
    )

@router.post("/", response_model=APIResponse, status_code=201)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["team:create"]))
):
    """Create a new team"""
    
    team_service = TeamService(db)
    
    # Set organization from current user
    team_data.organization_id = current_user.organization_id
    
    try:
        new_team = await team_service.create_team(team_data)
        
        return APIResponse(
            message="Team created successfully",
            data=TeamResponse.from_orm(new_team)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{team_id}", response_model=APIResponse)
async def get_team(
    team_id: str,
    include_members: bool = Query(False, description="Include team member details"),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get team by ID with optional member details"""
    
    team_service = TeamService(db)
    team = await team_service.get_team_by_id(team_id, include_members=include_members)
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if team belongs to same organization
    if team.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    team_data = TeamResponse.from_orm(team)
    
    # Add member details if requested
    if include_members:
        members = await team_service.get_team_members(team_id)
        team_data.members = [UserSummary.from_orm(member) for member in members]
    
    return APIResponse(
        message="Team retrieved successfully",
        data=team_data
    )

@router.put("/{team_id}", response_model=APIResponse)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["team:update"]))
):
    """Update team information"""
    
    team_service = TeamService(db)
    
    # Check if team exists and belongs to same organization
    existing_team = await team_service.get_team_by_id(team_id)
    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if existing_team.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        updated_team = await team_service.update_team(team_id, team_data)
        
        return APIResponse(
            message="Team updated successfully",
            data=TeamResponse.from_orm(updated_team)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{team_id}/members/{user_id}", response_model=APIResponse)
async def add_team_member(
    team_id: str,
    user_id: str,
    role_in_team: Optional[str] = Query(None, description="Role within the team"),
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["team:manage_members"]))
):
    """Add a member to a team"""
    
    team_service = TeamService(db)
    
    try:
        membership = await team_service.add_member_to_team(team_id, user_id, role_in_team)
        
        return APIResponse(
            message="Member added to team successfully",
            data={"membership_id": membership.id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{team_id}/members/{user_id}", response_model=APIResponse)
async def remove_team_member(
    team_id: str,
    user_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["team:manage_members"]))
):
    """Remove a member from a team"""
    
    team_service = TeamService(db)
    
    try:
        await team_service.remove_member_from_team(team_id, user_id)
        
        return APIResponse(
            message="Member removed from team successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{team_id}/members", response_model=APIResponse)
async def get_team_members(
    team_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get all members of a team"""
    
    team_service = TeamService(db)
    
    # Check if team exists and belongs to same organization
    team = await team_service.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        members = await team_service.get_team_members(team_id)
        
        return APIResponse(
            message="Team members retrieved successfully",
            data=[UserSummary.from_orm(member) for member in members]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{team_id}/leader/{user_id}", response_model=APIResponse)
async def transfer_team_leadership(
    team_id: str,
    user_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["team:manage_leadership"]))
):
    """Transfer team leadership to another member"""
    
    team_service = TeamService(db)
    
    try:
        updated_team = await team_service.transfer_team_leadership(team_id, user_id)
        
        return APIResponse(
            message="Team leadership transferred successfully",
            data=TeamResponse.from_orm(updated_team)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{team_id}/metrics/refresh", response_model=APIResponse)
async def refresh_team_metrics(
    team_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["team:update"]))
):
    """Refresh team performance metrics"""
    
    team_service = TeamService(db)
    
    try:
        updated_team = await team_service.update_team_metrics(team_id)
        
        return APIResponse(
            message="Team metrics refreshed successfully",
            data={
                "performance_score": updated_team.performance_score,
                "total_calls_today": updated_team.total_calls_today,
                "avg_satisfaction": updated_team.avg_satisfaction,
                "member_count": updated_team.member_count
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{team_id}", response_model=APIResponse)
async def delete_team(
    team_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["team:delete"]))
):
    """Delete (deactivate) a team"""
    
    team_service = TeamService(db)
    
    # Check if team exists and belongs to same organization
    existing_team = await team_service.get_team_by_id(team_id)
    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if existing_team.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        await team_service.delete_team(team_id)
        
        return APIResponse(
            message="Team deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))