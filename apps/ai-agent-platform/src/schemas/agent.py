"""
Agent schemas for AI Agent Platform
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    VOICE = "voice"
    CHAT = "chat"
    EMAIL = "email"
    SMS = "sms"
    MULTI_CHANNEL = "multi_channel"

class AgentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class AgentCapability(BaseModel):
    name: str
    description: str
    enabled: bool = True

class AgentConfiguration(BaseModel):
    voice_settings: Optional[Dict[str, Any]] = None
    personality: Optional[Dict[str, Any]] = None
    knowledge_base: Optional[Dict[str, Any]] = None
    integrations: Optional[List[str]] = None
    custom_prompts: Optional[Dict[str, str]] = None

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    agent_type: AgentType
    capabilities: List[AgentCapability] = []
    configuration: Optional[AgentConfiguration] = None
    tags: List[str] = []
    is_public: bool = False
    category: Optional[str] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    agent_type: Optional[AgentType] = None
    capabilities: Optional[List[AgentCapability]] = None
    configuration: Optional[AgentConfiguration] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    status: Optional[AgentStatus] = None
    category: Optional[str] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    agent_type: AgentType
    status: AgentStatus
    capabilities: List[AgentCapability]
    configuration: Optional[AgentConfiguration]
    tags: List[str]
    is_public: bool
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    rating: float = 0.0
    owner_id: Optional[str] = None

    class Config:
        from_attributes = True

class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total: int
    skip: int
    limit: int

class MarketplaceAgent(AgentResponse):
    downloads: int = 0
    reviews: List[Dict[str, Any]] = []
    publisher: Optional[str] = None
    verified: bool = False

class AgentAnalytics(BaseModel):
    agent_id: str
    total_calls: int = 0
    successful_calls: int = 0
    average_duration: float = 0.0
    satisfaction_score: float = 0.0
    last_used: Optional[datetime] = None
    usage_by_day: Dict[str, int] = {}
    performance_metrics: Dict[str, Any] = {}
