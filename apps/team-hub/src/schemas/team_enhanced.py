# apps/team-hub/src/schemas/team_enhanced.py
"""
Enhanced Team Hub Schemas - Additional functionality
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TrainingStatus(str, Enum):
    """Training status options"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class GoalStatus(str, Enum):
    """Performance goal status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Training Schemas
class TrainingAssignment(BaseModel):
    """Training assignment schema"""
    user_ids: List[str] = Field(..., description="List of user IDs to assign training")
    program_id: str = Field(..., description="Training program ID")
    due_date: Optional[datetime] = Field(None, description="Assignment due date")
    priority: Priority = Field(Priority.MEDIUM, description="Assignment priority")
    notes: Optional[str] = Field(None, description="Additional notes")

class TrainingProgram(BaseModel):
    """Training program schema"""
    id: str = Field(..., description="Program ID")
    name: str = Field(..., description="Program name")
    description: str = Field(..., description="Program description")
    duration_hours: int = Field(..., description="Duration in hours")
    difficulty_level: str = Field(..., description="Difficulty level")
    skills_covered: List[str] = Field(..., description="Skills covered")
    status: str = Field(..., description="Program status")
    completion_rate: float = Field(..., description="Overall completion rate")

# Performance Schemas
class PerformanceGoal(BaseModel):
    """Performance goal schema"""
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Goal title")
    description: str = Field(..., description="Goal description")
    target_value: float = Field(..., description="Target value")
    current_value: float = Field(0.0, description="Current progress value")
    unit: str = Field(..., description="Measurement unit")
    due_date: datetime = Field(..., description="Goal due date")
    priority: Priority = Field(Priority.MEDIUM, description="Goal priority")
    category: str = Field(..., description="Goal category")

class GoalProgress(BaseModel):
    """Goal progress update schema"""
    current_value: float = Field(..., description="Current progress value")
    notes: Optional[str] = Field(None, description="Progress notes")
    milestone_reached: Optional[str] = Field(None, description="Milestone description")

class PerformanceReview(BaseModel):
    """Performance review schema"""
    id: str = Field(..., description="Review ID")
    user_id: str = Field(..., description="User ID")
    reviewer_id: str = Field(..., description="Reviewer ID")
    period_start: datetime = Field(..., description="Review period start")
    period_end: datetime = Field(..., description="Review period end")
    overall_rating: float = Field(..., description="Overall rating (1-5)")
    strengths: List[str] = Field(..., description="Identified strengths")
    improvement_areas: List[str] = Field(..., description="Areas for improvement")
    goals_for_next_period: List[str] = Field(..., description="Goals for next period")
    status: str = Field(..., description="Review status")

# Analytics Schemas
class TeamPerformanceMetrics(BaseModel):
    """Team performance metrics schema"""
    team_id: str = Field(..., description="Team ID")
    period: str = Field(..., description="Time period")
    total_members: int = Field(..., description="Total team members")
    active_members: int = Field(..., description="Active team members")
    productivity_score: float = Field(..., description="Team productivity score")
    collaboration_score: float = Field(..., description="Collaboration score")
    satisfaction_score: float = Field(..., description="Team satisfaction score")
    goals_completed: int = Field(..., description="Goals completed in period")
    training_completion_rate: float = Field(..., description="Training completion rate")

class SkillGap(BaseModel):
    """Skill gap analysis schema"""
    skill_name: str = Field(..., description="Skill name")
    required_level: int = Field(..., description="Required skill level (1-5)")
    current_avg_level: float = Field(..., description="Current average level")
    gap_size: float = Field(..., description="Skill gap size")
    affected_members: int = Field(..., description="Number of affected members")
    priority: Priority = Field(..., description="Gap priority")
    recommended_training: List[str] = Field(..., description="Recommended training programs")

class WorkloadAlert(BaseModel):
    """Workload alert schema"""
    id: str = Field(..., description="Alert ID")
    user_id: str = Field(..., description="User ID")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    created_at: datetime = Field(..., description="Alert timestamp")
    resolved: bool = Field(False, description="Whether alert is resolved")

# Dashboard Schemas
class TeamDashboardMetrics(BaseModel):
    """Team dashboard metrics schema"""
    total_members: int = Field(..., description="Total team members")
    active_today: int = Field(..., description="Members active today")
    on_break: int = Field(..., description="Members on break")
    offline: int = Field(..., description="Offline members")
    avg_performance: float = Field(..., description="Average performance score")
    total_calls_today: int = Field(..., description="Total calls today")
    avg_call_duration: int = Field(..., description="Average call duration")
    customer_satisfaction: float = Field(..., description="Customer satisfaction score")
    trainings_completed: int = Field(..., description="Trainings completed")
    certification_rate: float = Field(..., description="Certification rate")

class TeamMemberProfile(BaseModel):
    """Enhanced team member profile"""
    id: str = Field(..., description="Member ID")
    name: str = Field(..., description="Member name")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="Role/position")
    department: str = Field(..., description="Department")
    status: str = Field(..., description="Current status")
    avatar: Optional[str] = Field(None, description="Avatar URL")
    performance: float = Field(..., description="Performance score")
    calls_today: int = Field(..., description="Calls today")
    avg_call_duration: int = Field(..., description="Average call duration")
    satisfaction: float = Field(..., description="Customer satisfaction")
    join_date: datetime = Field(..., description="Join date")
    last_login: datetime = Field(..., description="Last login")
    location: str = Field(..., description="Location")
    timezone: str = Field(..., description="Timezone")
    skills: List[str] = Field(..., description="Skills")
    certifications: List[str] = Field(..., description="Certifications")
    phone_number: str = Field(..., description="Phone number")
    current_goals: List[Dict[str, Any]] = Field(default_factory=list, description="Current goals")
    recent_training: List[Dict[str, Any]] = Field(default_factory=list, description="Recent training")
