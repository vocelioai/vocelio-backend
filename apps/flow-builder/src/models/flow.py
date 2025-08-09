# apps/flow-builder/src/models/flow.py
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from shared.database.models import Base

class Flow(Base):
    __tablename__ = "flows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    
    # Flow configuration
    flow_data = Column(JSON)  # Complete ReactFlow data structure
    viewport = Column(JSON)   # Viewport position and zoom
    
    # Status and versioning
    status = Column(String(50), default="draft")  # draft, published, archived
    version = Column(Integer, default=1)
    is_template = Column(Boolean, default=False)
    
    # Ownership
    user_id = Column(UUID(as_uuid=True), nullable=False)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Metadata
    tags = Column(JSON)  # Array of tags
    settings = Column(JSON)  # Flow-specific settings
    
    # Performance metrics
    total_executions = Column(Integer, default=0)
    success_rate = Column(Integer, default=0)  # Percentage
    avg_duration = Column(Integer, default=0)  # Seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    last_executed_at = Column(DateTime(timezone=True))
    
    # Relationships
    nodes = relationship("Node", back_populates="flow", cascade="all, delete-orphan")
    executions = relationship("FlowExecution", back_populates="flow")
    versions = relationship("FlowVersion", back_populates="flow")

class FlowVersion(Base):
    __tablename__ = "flow_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flow_id = Column(UUID(as_uuid=True), ForeignKey("flows.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_name = Column(String(255))
    
    # Snapshot of flow data at this version
    flow_data = Column(JSON)
    viewport = Column(JSON)
    
    # Version metadata
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text)
    
    # Relationships
    flow = relationship("Flow", back_populates="versions")