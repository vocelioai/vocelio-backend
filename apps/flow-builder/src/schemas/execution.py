# apps/flow-builder/src/schemas/execution.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class ExecutionRequest(BaseModel):
    input_data: Dict[str, Any] = {}
    variables: Optional[Dict[str, Any]] = {}
    context: Optional[Dict[str, Any]] = {}

class ExecutionStep(BaseModel):
    node_id: UUID
    node_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[int] = None
    
    class Config:
        from_attributes = True

class ExecutionResponse(BaseModel):
    execution_id: UUID
    flow_id: UUID
    status: ExecutionStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    steps: List[ExecutionStep] = []
    variables: Dict[str, Any] = {}
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    
    class Config:
        from_attributes = True

class FlowExecution(BaseModel):
    """Model for storing flow execution history"""
    id: UUID
    flow_id: UUID
    user_id: UUID
    status: ExecutionStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    variables: Dict[str, Any]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[int]
    
    class Config:
        from_attributes = True