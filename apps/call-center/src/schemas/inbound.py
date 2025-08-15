# apps/call-center/src/schemas/inbound.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class QueueState(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"

class CallStatus(str, Enum):
    QUEUED = "queued"
    ROUTING = "routing"
    RINGING = "ringing"
    CONNECTED = "connected"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class RoutingType(str, Enum):
    AGENT = "agent"
    DEPARTMENT = "department"
    QUEUE = "queue"
    IVR = "ivr"
    VOICEMAIL = "voicemail"

class PriorityLevel(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10

# Queue Management
class QueueStatus(BaseModel):
    queue_id: str
    name: str
    state: QueueState
    calls_in_queue: int = 0
    average_wait_time: float = 0.0
    longest_wait_time: float = 0.0
    available_agents: int = 0
    busy_agents: int = 0
    total_agents: int = 0
    service_level: float = 0.0
    abandon_rate: float = 0.0
    last_updated: datetime

class QueueMetrics(BaseModel):
    queue_id: str
    period: str
    total_calls: int = 0
    answered_calls: int = 0
    abandoned_calls: int = 0
    average_wait_time: float = 0.0
    average_talk_time: float = 0.0
    service_level_20: float = 0.0  # % answered within 20 seconds
    service_level_30: float = 0.0  # % answered within 30 seconds
    max_wait_time: float = 0.0
    abandon_rate: float = 0.0
    first_call_resolution: float = 0.0
    customer_satisfaction: Optional[float] = None

class SLAMetrics(BaseModel):
    department: Optional[str] = None
    target_answer_time: int = 20  # seconds
    target_service_level: float = 95.0  # percentage
    current_service_level: float = 0.0
    calls_within_sla: int = 0
    total_calls: int = 0
    average_answer_time: float = 0.0
    compliance_percentage: float = 0.0
    period: str = "today"

# Department Configuration
class DepartmentConfig(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    phone_numbers: List[str] = []
    priority: int = Field(5, ge=1, le=10)
    max_queue_size: int = Field(100, ge=1, le=1000)
    max_wait_time: int = Field(600, ge=30, le=3600)  # seconds
    overflow_destination: Optional[str] = None
    overflow_threshold: int = Field(50, ge=1, le=100)
    business_hours: Dict[str, Any] = {}
    after_hours_action: str = "voicemail"
    skill_requirements: List[str] = []
    routing_strategy: str = "round_robin"  # round_robin, longest_idle, skills_based
    recording_enabled: bool = True
    quality_monitoring: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

# Call Routing
class CallRouting(BaseModel):
    call_id: str
    target_type: RoutingType
    target_id: str
    priority: PriorityLevel = PriorityLevel.NORMAL
    routing_reason: Optional[str] = None
    estimated_wait_time: Optional[int] = None
    customer_info: Optional[Dict[str, Any]] = None

class InboundCall(BaseModel):
    id: str
    caller_id: str
    caller_name: Optional[str] = None
    department: Optional[str] = None
    queue_id: Optional[str] = None
    agent_id: Optional[str] = None
    status: CallStatus
    priority: int = 5
    wait_time: float = 0.0
    talk_time: float = 0.0
    queue_position: Optional[int] = None
    estimated_wait: Optional[int] = None
    start_time: datetime
    answer_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    disposition: Optional[str] = None
    customer_satisfaction: Optional[int] = None
    transferred_from: Optional[str] = None
    transfer_count: int = 0
    recording_url: Optional[str] = None
    notes: Optional[str] = None

class QueueConfig(BaseModel):
    id: Optional[str] = None
    name: str
    department_id: str
    max_size: int = Field(100, ge=1, le=1000)
    priority_routing: bool = True
    skills_based_routing: bool = False
    overflow_queue_id: Optional[str] = None
    music_on_hold: Optional[str] = None
    periodic_announcements: List[str] = []
    announcement_interval: int = 30  # seconds
    wrap_up_time: int = 30  # seconds
    created_at: Optional[datetime] = None
    is_active: bool = True

# Analytics
class CallDistribution(BaseModel):
    department: str
    total_calls: int
    answered_calls: int
    abandoned_calls: int
    percentage_of_total: float
    average_wait_time: float
    service_level: float

class HourlyDistribution(BaseModel):
    hour: int
    call_count: int
    average_wait_time: float
    service_level: float
    abandon_rate: float

class AgentQueueAssignment(BaseModel):
    agent_id: str
    queue_id: str
    priority: int = 5
    max_concurrent_calls: int = 1
    skills: List[str] = []
    is_active: bool = True
    assigned_at: datetime

# Real-time updates
class QueueUpdate(BaseModel):
    queue_id: str
    event_type: str  # call_entered, call_answered, call_abandoned, agent_available, etc.
    timestamp: datetime
    data: Dict[str, Any]
