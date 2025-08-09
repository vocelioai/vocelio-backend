# apps/flow-builder/src/models/node.py
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from shared.database.models import Base

class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flow_id = Column(UUID(as_uuid=True), ForeignKey("flows.id"), nullable=False)
    
    # Node identification
    node_id = Column(String(255), nullable=False)  # ReactFlow node ID
    node_type = Column(String(100), nullable=False)  # start, message, condition, etc.
    
    # Visual properties
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    width = Column(Float)
    height = Column(Float)
    
    # Node configuration
    label = Column(String(255))
    data = Column(JSON)  # Node-specific data
    style = Column(JSON)  # Visual styling
    
    # Node behavior
    is_entry_point = Column(Boolean, default=False)
    is_exit_point = Column(Boolean, default=False)
    is_deletable = Column(Boolean, default=True)
    is_connectable = Column(Boolean, default=True)
    
    # Validation and status
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON)  # Array of validation errors
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    flow = relationship("Flow", back_populates="nodes")
    connections_from = relationship(
        "NodeConnection", 
        foreign_keys="NodeConnection.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan"
    )
    connections_to = relationship(
        "NodeConnection", 
        foreign_keys="NodeConnection.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan"
    )

class NodeConnection(Base):
    __tablename__ = "node_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Connection endpoints
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False)
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False)
    
    # Connection properties
    connection_type = Column(String(50), default="default")  # default, conditional, error
    source_handle = Column(String(100))  # Source handle ID
    target_handle = Column(String(100))  # Target handle ID
    
    # Connection configuration
    label = Column(String(255))
    condition = Column(JSON)  # Condition for conditional connections
    style = Column(JSON)  # Visual styling
    
    # Connection behavior
    is_animated = Column(Boolean, default=False)
    is_deletable = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="connections_from")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="connections_to")

class NodeTemplate(Base):
    __tablename__ = "node_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template identification
    name = Column(String(255), nullable=False)
    node_type = Column(String(100), nullable=False)
    category = Column(String(100))
    
    # Template configuration
    default_data = Column(JSON)  # Default node data
    default_style = Column(JSON)  # Default styling
    config_schema = Column(JSON)  # JSON schema for validation
    
    # Template metadata
    description = Column(Text)
    icon = Column(String(100))
    color = Column(String(50))
    tags = Column(JSON)
    
    # Template behavior
    is_system = Column(Boolean, default=False)  # System vs user template
    is_public = Column(Boolean, default=False)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    
    # Ownership
    created_by = Column(UUID(as_uuid=True))
    organization_id = Column(UUID(as_uuid=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())