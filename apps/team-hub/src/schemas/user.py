# apps/team-hub/src/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ONLINE = "online"
    ON_CALL = "on-call"
    BREAK = "break"
    TRAINING = "training"
    OFFLINE = "offline"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    avatar: str = Field("👤", max_length=10)
    role: str = Field(..., max_length=100)
    department: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    timezone: str = Field("UTC", max_length=50)
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

class UserCreate(UserBase):
    """Schema for creating a new user"""
    organization_id: str
    
    @validator('skills')
    def validate_skills(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 skills allowed')
        return v
    
    @validator('certifications')
    def validate_certifications(cls, v):
        if len(v) > 15:
            raise ValueError('Maximum 15 certifications allowed')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    avatar: Optional[str] = Field(None, max_length=10)
    role: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    organization_id: str
    status: UserStatus
    last_login: Optional[datetime]
    last_activity: datetime
    performance_score: float
    calls_today: int
    avg_call_duration: int
    customer_satisfaction: float
    join_date: datetime
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class UserSummary(BaseModel):
    """Lightweight user schema for lists"""
    id: str
    name: str
    email: str
    avatar: str
    role: str
    department: str
    status: UserStatus
    performance_score: float
    
    class Config:
        from_attributes = True

# apps/team-hub/src/schemas/team.py

class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    department: str = Field(..., max_length=100)

class TeamCreate(TeamBase):
    """Schema for creating a new team"""
    organization_id: str
    team_lead_id: Optional[str] = None

class TeamUpdate(BaseModel):
    """Schema for updating team information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    department: Optional[str] = Field(None, max_length=100)
    team_lead_id: Optional[str] = None

class TeamResponse(TeamBase):
    """Schema for team response"""
    id: str
    organization_id: str
    team_lead_id: Optional[str]
    performance_score: float
    total_calls_today: int
    avg_satisfaction: float
    member_count: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    # Optional nested data
    team_lead: Optional[UserSummary] = None
    members: Optional[List[UserSummary]] = None
    
    class Config:
        from_attributes = True

# apps/team-hub/src/schemas/invitation.py

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

class InvitationBase(BaseModel):
    email: EmailStr
    role: str = Field(..., max_length=100)
    department: str = Field(..., max_length=100)

class InvitationCreate(InvitationBase):
    """Schema for creating a new invitation"""
    organization_id: str
    invited_by_id: str
    expires_in_hours: int = Field(72, ge=1, le=168)  # 1 hour to 1 week

class InvitationUpdate(BaseModel):
    """Schema for updating invitation status"""
    status: InvitationStatus

class InvitationResponse(InvitationBase):
    """Schema for invitation response"""
    id: str
    organization_id: str
    invited_by_id: str
    status: InvitationStatus
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Optional nested data
    invited_by: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True

# apps/team-hub/src/schemas/role.py

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)

class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    organization_id: str

class RoleUpdate(BaseModel):
    """Schema for updating role information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleResponse(RoleBase):
    """Schema for role response"""
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# apps/team-hub/src/schemas/response.py

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[Any]
    meta: PaginationMeta

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class TeamMetrics(BaseModel):
    """Team metrics schema"""
    total_members: int
    active_today: int
    on_break: int
    offline: int
    avg_performance: float
    total_calls_today: int
    avg_call_duration: int
    customer_satisfaction: float
    trainings_completed: int
    certification_rate: float

class DepartmentSummary(BaseModel):
    """Department summary schema"""
    name: str
    count: int
    growth: float
    color: str
    avg_performance: float
    
class TeamStatusSummary(BaseModel):
    """Team status summary"""
    online: int
    on_call: int
    break: int
    training: int
    offline: int

# apps/team-hub/src/schemas/filters.py

class UserFilters(BaseModel):
    """User filtering and search parameters"""
    search: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    status: Optional[UserStatus] = None
    location: Optional[str] = Field(None, max_length=100)
    min_performance: Optional[float] = Field(None, ge=0, le=100)
    max_performance: Optional[float] = Field(None, ge=0, le=100)
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("name", regex="^(name|email|role|department|status|performance_score|join_date)$")
    sort_order: str = Field("asc", regex="^(asc|desc)$")

class TeamFilters(BaseModel):
    """Team filtering parameters"""
    search: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    min_size: Optional[int] = Field(None, ge=1)
    max_size: Optional[int] = Field(None, ge=1)
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("name", regex="^(name|department|member_count|performance_score|created_at)$")
    sort_order: str = Field("asc", regex="^(asc|desc)$")
