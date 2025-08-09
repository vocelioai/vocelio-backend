# apps/flow-builder/src/services/node_service.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from shared.database.client import get_database_session
from models.node import Node, NodeConnection, NodeTemplate
from models.flow import Flow
from schemas.node import (
    NodeCreate, NodeUpdate, NodeResponse, NodePosition, 
    ValidationResult, ConnectionType
)

class NodeService:
    def __init__(self, db: Session = Depends(get_database_session)):
        self.db = db
    
    async def get_flow_nodes(
        self,
        flow_id: UUID,
        user_id: UUID
    ) -> List[NodeResponse]:
        """Get all nodes for a specific flow"""
        
        # Verify user has access to the flow
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        nodes = self.db.query(Node).filter(
            Node.flow_id == flow_id
        ).all()
        
        return [NodeResponse.from_orm(node) for node in nodes]
    
    async def create_node(
        self,
        node_data: NodeCreate,
        user_id: UUID
    ) -> NodeResponse:
        """Create a new node in a flow"""
        
        # Verify user has access to the flow
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == node_data.flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        # Create the node
        db_node = Node(
            flow_id=node_data.flow_id,
            node_id=node_data.node_id,
            node_type=node_data.node_type.value,
            label=node_data.label,
            data=node_data.data,
            style=node_data.style,
            position_x=node_data.position_x,
            position_y=node_data.position_y,
            width=node_data.width,
            height=node_data.height,
            is_entry_point=node_data.is_entry_point,
            is_exit_point=node_data.is_exit_point
        )
        
        self.db.add(db_node)
        self.db.commit()
        self.db.refresh(db_node)
        
        # Update flow's updated_at timestamp
        flow.updated_at = datetime.utcnow()
        self.db.commit()
        
        return NodeResponse.from_orm(db_node)
    
    async def get_node_by_id(
        self,
        node_id: UUID,
        user_id: UUID
    ) -> Optional[NodeResponse]:
        """Get a specific node by ID"""
        node = self.db.query(Node).join(Flow).filter(
            and_(
                Node.id == node_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if node:
            return NodeResponse.from_orm(node)
        return None
    
    async def update_node(
        self,
        node_id: UUID,
        node_data: NodeUpdate,
        user_id: UUID
    ) -> Optional[NodeResponse]:
        """Update an existing node"""
        node = self.db.query(Node).join(Flow).filter(
            and_(
                Node.id == node_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not node:
            return None
        
        # Update fields if provided
        update_data = node_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)
        
        node.updated_at = datetime.utcnow()
        
        # Update flow's updated_at timestamp
        node.flow.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(node)
        
        return NodeResponse.from_orm(node)
    
    async def delete_node(
        self,
        node_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a node"""
        node = self.db.query(Node).join(Flow).filter(
            and_(
                Node.id == node_id,
                Flow.user_id == user_id,
                Node.is_deletable == True
            )
        ).first()
        
        if not node:
            return False
        
        # Update flow's updated_at timestamp
        node.flow.updated_at = datetime.utcnow()
        
        self.db.delete(node)
        self.db.commit()
        return True
    
    async def batch_update_positions(
        self,
        positions: List[NodePosition],
        user_id: UUID
    ) -> None:
        """Batch update node positions for drag and drop"""
        
        node_ids = [pos.node_id for pos in positions]
        
        # Get all nodes and verify user access
        nodes = self.db.query(Node).join(Flow).filter(
            and_(
                Node.id.in_(node_ids),
                Flow.user_id == user_id
            )
        ).all()
        
        if len(nodes) != len(positions):
            raise HTTPException(status_code=400, detail="Some nodes not found or access denied")
        
        # Create position lookup
        position_map = {pos.node_id: pos for pos in positions}
        
        # Update positions
        for node in nodes:
            pos = position_map[node.id]
            node.position_x = pos.x
            node.position_y = pos.y
            node.updated_at = datetime.utcnow()
            
            # Update flow timestamp
            node.flow.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    async def connect_nodes(
        self,
        source_node_id: UUID,
        target_node_id: UUID,
        connection_type: str,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Connect two nodes"""
        
        # Verify both nodes exist and user has access
        source_node = self.db.query(Node).join(Flow).filter(
            and_(
                Node.id == source_node_id,
                Flow.user_id == user_id
            )
        ).first()
        
        target_node = self.db.query(Node).join(Flow).filter(
            and_(
                Node.id == target_node_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not source_node or not target_node:
            return None
        
        # Check if connection already exists
        existing = self.db.query(NodeConnection).filter(
            and_(
                NodeConnection.source_node_id == source_node_id,
                NodeConnection.target_node_id == target_node_id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Connection already exists")
        
        # Create connection
        connection = NodeConnection(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            connection_type=connection_type
        )
        
        self.db.add(connection)
        
        # Update flow timestamp
        source_node.flow.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(connection)
        
        return {
            "id": connection.id,
            "source": str(source_node_id),
            "target": str(target_node_id),
            "type": connection_type
        }
    
    async def disconnect_nodes(
        self,
        source_node_id: UUID,
        target_node_id: UUID,
        user_id: UUID
    ) -> bool:
        """Disconnect two nodes"""
        
        # Find the connection
        connection = self.db.query(NodeConnection).join(
            Node, NodeConnection.source_node_id == Node.id
        ).join(Flow).filter(
            and_(
                NodeConnection.source_node_id == source_node_id,
                NodeConnection.target_node_id == target_node_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not connection:
            return False
        
        # Update flow timestamp
        connection.source_node.flow.updated_at = datetime.utcnow()
        
        self.db.delete(connection)
        self.db.commit()
        return True
    
    @staticmethod
    async def get_available_node_types() -> Dict[str, Any]:
        """Get all available node types and their configurations"""
        return {
            "start": {
                "name": "Start",
                "description": "Entry point for the flow",
                "category": "control",
                "icon": "play-circle",
                "color": "#10b981",
                "inputs": 0,
                "outputs": 1,
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "trigger_type": {
                            "type": "string",
                            "enum": ["manual", "scheduled", "webhook"],
                            "default": "manual"
                        }
                    }
                }
            },
            "message": {
                "name": "Message",
                "description": "Send a message to the caller",
                "category": "communication",
                "icon": "message-square",
                "color": "#3b82f6",
                "inputs": 1,
                "outputs": 1,
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to send"
                        },
                        "voice_id": {
                            "type": "string",
                            "description": "Voice to use for TTS"
                        }
                    },
                    "required": ["message"]
                }
            },
            "condition": {
                "name": "Condition",
                "description": "Branch flow based on conditions",
                "category": "logic",
                "icon": "git-branch",
                "color": "#f59e0b",
                "inputs": 1,
                "outputs": 2,
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "condition_type": {
                            "type": "string",
                            "enum": ["user_input", "ai_analysis", "custom"]
                        },
                        "condition_logic": {
                            "type": "object"
                        }
                    }
                }
            },
            "ai_response": {
                "name": "AI Response",
                "description": "Generate AI-powered response",
                "category": "ai",
                "icon": "brain",
                "color": "#8b5cf6",
                "inputs": 1,
                "outputs": 1,
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "AI prompt template"
                        },
                        "model": {
                            "type": "string",
                            "default": "gpt-4"
                        },
                        "max_tokens": {
                            "type": "integer",
                            "default": 150
                        }
                    }
                }
            },
            "collect_input": {
                "name": "Collect Input",
                "description": "Collect input from caller",
                "category": "input",
                "icon": "mic",
                "color": "#ef4444",
                "inputs": 1,
                "outputs": 2,
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "input_type": {
                            "type": "string",
                            "enum": ["speech", "dtmf", "both"]
                        },
                        "timeout": {
                            "type": "integer",
                            "default": 5
                        },
                        "retries": {
                            "type": "integer",
                            "default": 3
                        }
                    }
                }
            },
            "transfer": {
                "name": "Transfer",
                "description": "Transfer call to another number",
                "category": "action",
                "icon": "phone-forwarded",
                "color": "#06b6d4",
                "inputs": 1,
                "outputs": 2,
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "transfer_number": {
                            "type": "string",
                            "description": "Number to transfer to"
                        },
                        "transfer_type": {
                            "type": "string",
                            "enum": ["warm", "cold"],
                            "default": "cold"
                        }
                    }
                }
            },
            "end": {
                "name": "End",
                "description": "End the flow",
                "category": "control",
                "icon": "stop-circle",
                "color": "#ef4444",
                "inputs": 1,
                "outputs": 0,
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "end_reason": {
                            "type": "string",
                            "default": "completed"
                        }
                    }
                }
            }
        }
    
    async def validate_node(
        self,
        node_id: UUID,
        user_id: UUID
    ) -> Optional[ValidationResult]:
        """Validate a node's configuration"""
        
        node = self.db.query(Node).join(Flow).filter(
            and_(
                Node.id == node_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not node:
            return None
        
        errors = []
        warnings = []
        
        # Get node type configuration
        node_types = await self.get_available_node_types()
        node_type_config = node_types.get(node.node_type)
        
        if not node_type_config:
            errors.append(f"Unknown node type: {node.node_type}")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Validate required fields
        config_schema = node_type_config.get("config_schema", {})
        required_fields = config_schema.get("required", [])
        
        for field in required_fields:
            if field not in node.data or not node.data[field]:
                errors.append(f"Required field '{field}' is missing")
        
        # Validate connections
        expected_inputs = node_type_config.get("inputs", 0)
        expected_outputs = node_type_config.get("outputs", 0)
        
        actual_inputs = self.db.query(NodeConnection).filter(
            NodeConnection.target_node_id == node_id
        ).count()
        
        actual_outputs = self.db.query(NodeConnection).filter(
            NodeConnection.source_node_id == node_id
        ).count()
        
        if expected_inputs > 0 and actual_inputs == 0:
            warnings.append("Node has no incoming connections")
        
        if expected_outputs > 0 and actual_outputs == 0:
            warnings.append("Node has no outgoing connections")
        
        # Update node validation status
        node.is_valid = len(errors) == 0
        node.validation_errors = errors
        self.db.commit()
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )