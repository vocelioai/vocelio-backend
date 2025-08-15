"""
Agent Management Schema Definitions for Call Center
Comprehensive data models for agent management, performance tracking, and scheduling
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, time
from datetime import date as date_type
from enum import Enum


class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    ON_CALL = "on_call"
    BREAK = "break"
    LUNCH = "lunch"
    TRAINING = "training"
    MEETING = "meeting"
    OFFLINE = "offline"
    AWAY = "away"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ShiftType(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    ROTATING = "rotating"
    FLEXIBLE = "flexible"


class TrainingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class AgentBase(BaseModel):
    employee_id: str = Field(..., description="Employee identification number")
    first_name: str = Field(..., description="Agent's first name")
    last_name: str = Field(..., description="Agent's last name")
    email: EmailStr = Field(..., description="Agent's email address")
    phone: str = Field(..., description="Agent's phone number")
    department: str = Field(..., description="Department assignment")
    team: Optional[str] = Field(None, description="Team assignment")
    hire_date: date_type = Field(..., description="Date of hire")
    shift_type: ShiftType = Field(..., description="Assigned shift type")


class AgentCreate(AgentBase):
    initial_skills: List[str] = Field(default_factory=list, description="Initial skill assignments")
    supervisor_id: Optional[str] = Field(None, description="Assigned supervisor ID")
    extension: Optional[str] = Field(None, description="Phone extension")


class AgentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    shift_type: Optional[ShiftType] = None
    supervisor_id: Optional[str] = None
    extension: Optional[str] = None
    is_active: Optional[bool] = None


class Agent(AgentBase):
    id: str = Field(..., description="Unique agent identifier")
    status: AgentStatus = Field(..., description="Current agent status")
    is_active: bool = Field(True, description="Whether agent is active")
    supervisor_id: Optional[str] = Field(None, description="Supervisor's agent ID")
    extension: Optional[str] = Field(None, description="Phone extension")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    total_experience_months: int = Field(0, description="Total experience in months")

    class Config:
        from_attributes = True


class AgentSkill(BaseModel):
    skill_id: str = Field(..., description="Skill identifier")
    skill_name: str = Field(..., description="Skill name")
    level: SkillLevel = Field(..., description="Proficiency level")
    certified: bool = Field(False, description="Whether agent is certified")
    certification_date: Optional[date_type] = Field(None, description="Certification date")
    expiry_date: Optional[date_type] = Field(None, description="Certification expiry")
    score: float = Field(0.0, description="Skill assessment score (0-100)")


class AgentSkillAssignment(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    skill_id: str = Field(..., description="Skill identifier")
    level: SkillLevel = Field(..., description="Assigned proficiency level")
    priority: int = Field(1, description="Skill priority (1-10)")
    notes: Optional[str] = Field(None, description="Additional notes")


class AgentPerformanceMetrics(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    period_start: date_type = Field(..., description="Performance period start")
    period_end: date_type = Field(..., description="Performance period end")
    
    # Call metrics
    total_calls: int = Field(0, description="Total calls handled")
    inbound_calls: int = Field(0, description="Inbound calls handled")
    outbound_calls: int = Field(0, description="Outbound calls made")
    average_call_duration: float = Field(0.0, description="Average call duration in minutes")
    total_talk_time: float = Field(0.0, description="Total talk time in minutes")
    
    # Quality metrics
    customer_satisfaction_score: float = Field(0.0, description="Customer satisfaction score")
    quality_score: float = Field(0.0, description="Quality assessment score")
    first_call_resolution_rate: float = Field(0.0, description="First call resolution rate")
    call_completion_rate: float = Field(0.0, description="Call completion rate")
    
    # Productivity metrics
    calls_per_hour: float = Field(0.0, description="Calls handled per hour")
    schedule_adherence: float = Field(0.0, description="Schedule adherence percentage")
    utilization_rate: float = Field(0.0, description="Agent utilization rate")
    idle_time_percentage: float = Field(0.0, description="Idle time percentage")
    
    # Sales metrics
    conversions: int = Field(0, description="Number of successful conversions")
    conversion_rate: float = Field(0.0, description="Conversion rate percentage")
    revenue_generated: float = Field(0.0, description="Revenue generated")
    average_deal_size: float = Field(0.0, description="Average deal size")


class AgentStatusUpdate(BaseModel):
    status: AgentStatus = Field(..., description="New agent status")
    reason: Optional[str] = Field(None, description="Reason for status change")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    auto_return: bool = Field(False, description="Auto-return to available after duration")


class AgentSchedule(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    schedule_date: date_type = Field(..., description="Schedule date")
    shift_start: time = Field(..., description="Shift start time")
    shift_end: time = Field(..., description="Shift end time")
    break_times: List[Dict[str, time]] = Field(default_factory=list, description="Break periods")
    lunch_start: Optional[time] = Field(None, description="Lunch break start")
    lunch_end: Optional[time] = Field(None, description="Lunch break end")
    is_working_day: bool = Field(True, description="Whether it's a working day")
    notes: Optional[str] = Field(None, description="Schedule notes")


class AgentScheduleUpdate(BaseModel):
    shift_start: Optional[time] = None
    shift_end: Optional[time] = None
    break_times: Optional[List[Dict[str, time]]] = None
    lunch_start: Optional[time] = None
    lunch_end: Optional[time] = None
    is_working_day: Optional[bool] = None
    notes: Optional[str] = None


class AgentTraining(BaseModel):
    training_id: str = Field(..., description="Training identifier")
    agent_id: str = Field(..., description="Agent identifier")
    training_name: str = Field(..., description="Training program name")
    description: str = Field(..., description="Training description")
    status: TrainingStatus = Field(..., description="Training status")
    assigned_date: date_type = Field(..., description="Assignment date")
    start_date: Optional[date_type] = Field(None, description="Training start date")
    completion_date: Optional[date_type] = Field(None, description="Completion date")
    due_date: date_type = Field(..., description="Due date")
    score: Optional[float] = Field(None, description="Training score (0-100)")
    attempts: int = Field(0, description="Number of attempts")
    max_attempts: int = Field(3, description="Maximum allowed attempts")
    trainer_id: Optional[str] = Field(None, description="Trainer's ID")
    notes: Optional[str] = Field(None, description="Training notes")


class AgentTrainingAssignment(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    training_program_id: str = Field(..., description="Training program identifier")
    due_date: date_type = Field(..., description="Training due date")
    priority: int = Field(1, description="Training priority (1-10)")
    mandatory: bool = Field(True, description="Whether training is mandatory")
    notes: Optional[str] = Field(None, description="Assignment notes")


class AgentListResponse(BaseModel):
    agents: List[Agent] = Field(..., description="List of agents")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    has_more: bool = Field(..., description="More results available")


class AgentMetricsResponse(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    current_metrics: AgentPerformanceMetrics = Field(..., description="Current period metrics")
    historical_metrics: List[AgentPerformanceMetrics] = Field(..., description="Historical metrics")
    benchmarks: Dict[str, float] = Field(..., description="Performance benchmarks")
    ranking: Dict[str, int] = Field(..., description="Agent ranking in various categories")


class AgentOverviewStats(BaseModel):
    total_agents: int = Field(..., description="Total number of agents")
    active_agents: int = Field(..., description="Currently active agents")
    available_agents: int = Field(..., description="Available agents")
    busy_agents: int = Field(..., description="Busy agents")
    on_break_agents: int = Field(..., description="Agents on break")
    offline_agents: int = Field(..., description="Offline agents")
    average_experience: float = Field(..., description="Average experience in months")
    top_performers: List[Dict[str, Union[str, float]]] = Field(..., description="Top performing agents")
    skill_distribution: Dict[str, int] = Field(..., description="Distribution of skills")
    department_distribution: Dict[str, int] = Field(..., description="Agents by department")
    last_updated: datetime = Field(..., description="Last update timestamp")


class AgentAvailabilityStatus(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent full name")
    current_status: AgentStatus = Field(..., description="Current status")
    status_since: datetime = Field(..., description="Status start time")
    estimated_available_at: Optional[datetime] = Field(None, description="Estimated availability time")
    current_call_duration: Optional[float] = Field(None, description="Current call duration in minutes")
    queue_position: Optional[int] = Field(None, description="Position in assignment queue")
    skills: List[str] = Field(..., description="Agent skills")
    extension: Optional[str] = Field(None, description="Phone extension")


class BulkAgentUpdate(BaseModel):
    agent_ids: List[str] = Field(..., description="List of agent IDs to update")
    updates: Dict[str, Any] = Field(..., description="Updates to apply")
    reason: str = Field(..., description="Reason for bulk update")


class BulkUpdateResponse(BaseModel):
    updated_count: int = Field(..., description="Number of agents updated")
    failed_count: int = Field(..., description="Number of failed updates")
    errors: List[Dict[str, str]] = Field(..., description="List of errors encountered")
    updated_agent_ids: List[str] = Field(..., description="Successfully updated agent IDs")
