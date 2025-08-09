# apps/flow-builder/src/schemas/node.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class NodeType(str, Enum):
    START = "start"
    MESSAGE = "message"
    CONDITION = "condition"
    ACTION = "action"
    END = "end"
    WAIT = "wait"
    TRANSFER = "transfer"
    API_CALL = "api_call"
    WEBHOOK = "webhook"
    VOICE_PROMPT = "voice_prompt"
    COLLECT_INPUT = "collect_input"
    AI_RESPONSE = "ai_response"

class ConnectionType(str, Enum):
    DEFAULT = "default"
    CONDITIONAL = "conditional"
    ERROR = "error"
    SUCCESS = "success"
    TIMEOUT = "timeout"

class NodePosition(BaseModel):
    node_id: UUID
    x: float
    y: float

class NodeBase(BaseModel):
    node_id: str = Field(..., min_length=1, max_length=255)
    node_type: NodeType
    label: Optional[str] = None
    data: Dict[str, Any] = {}
    style: Optional[Dict[str, Any]] = {}

class NodeCreate(NodeBase):
    flow_id: UUID
    position_x: float = 0
    position_y: float = 0
    width: Optional[float] = None
    height: Optional[float] = None
    is_entry_point: bool = False
    is_exit_point: bool = False

class NodeUpdate(BaseModel):
    label: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    style: Optional[Dict[str, Any]] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    is_entry_point: Optional[bool] = None
    is_exit_point: Optional[bool] = None

class NodeResponse(NodeBase):
    id: UUID
    flow_id: UUID
    position_x: float
    position_y: float
    width: Optional[float]
    height: Optional[float]
    is_entry_point: bool
    is_exit_point: bool
    is_deletable: bool
    is_connectable: bool
    is_valid: bool
    validation_errors: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class NodeConnection(BaseModel):
    id: UUID
    source_node_id: UUID
    target_node_id: UUID
    connection_type: ConnectionType
    source_handle: Optional[str]
    target_handle: Optional[str]
    label: Optional[str]
    condition: Optional[Dict[str, Any]]
    style: Optional[Dict[str, Any]]
    is_animated: bool
    is_deletable: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NodeTemplate(BaseModel):
    id: UUID
    name: str
    node_type: NodeType
    category: Optional[str]
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    tags: Optional[List[str]]
    default_data: Dict[str, Any]
    default_style: Dict[str, Any]
    config_schema: Dict[str, Any]
    is_system: bool
    is_public: bool
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []