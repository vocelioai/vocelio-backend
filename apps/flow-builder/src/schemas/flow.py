# apps/flow-builder/src/schemas/flow.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class FlowStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class FlowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    settings: Optional[Dict[str, Any]] = {}

class FlowCreate(FlowBase):
    flow_data: Optional[Dict[str, Any]] = {}
    viewport: Optional[Dict[str, Any]] = {}
    is_template: bool = False

class FlowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    flow_data: Optional[Dict[str, Any]] = None
    viewport: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

class FlowResponse(FlowBase):
    id: UUID
    status: FlowStatus
    version: int
    is_template: bool
    user_id: UUID
    organization_id: UUID
    
    # Performance metrics
    total_executions: int
    success_rate: int
    avg_duration: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    last_executed_at: Optional[datetime]
    
    # ReactFlow data
    flow_data: Dict[str, Any]
    viewport: Dict[str, Any]
    
    class Config:
        from_attributes = True

class FlowList(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: Optional[str]
    status: FlowStatus
    version: int
    is_template: bool
    total_executions: int
    success_rate: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class FlowVersion(BaseModel):
    id: UUID
    flow_id: UUID
    version_number: int
    version_name: Optional[str]
    description: Optional[str]
    created_by: UUID
    created_at: datetime
    flow_data: Dict[str, Any]
    viewport: Dict[str, Any]
    
    class Config:
        from_attributes = True