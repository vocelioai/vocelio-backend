# apps/flow-builder/src/api/v1/endpoints/nodes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from uuid import UUID
from services.node_service import NodeService
from schemas.node import NodeCreate, NodeUpdate, NodeResponse, NodePosition
from shared.auth.dependencies import get_current_user
from shared.schemas.user import User

router = APIRouter()

@router.get("/flow/{flow_id}", response_model=List[NodeResponse])
async def get_flow_nodes(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Get all nodes for a specific flow"""
    return await node_service.get_flow_nodes(
        flow_id=flow_id,
        user_id=current_user.id
    )

@router.post("/", response_model=NodeResponse)
async def create_node(
    node_data: NodeCreate,
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Create a new node in a flow"""
    return await node_service.create_node(
        node_data=node_data,
        user_id=current_user.id
    )

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: UUID,
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Get a specific node by ID"""
    node = await node_service.get_node_by_id(
        node_id=node_id,
        user_id=current_user.id
    )
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: UUID,
    node_data: NodeUpdate,
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Update an existing node"""
    node = await node_service.update_node(
        node_id=node_id,
        node_data=node_data,
        user_id=current_user.id
    )
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.delete("/{node_id}")
async def delete_node(
    node_id: UUID,
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Delete a node"""
    success = await node_service.delete_node(
        node_id=node_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node deleted successfully"}

@router.post("/batch-update-positions")
async def batch_update_node_positions(
    positions: List[NodePosition],
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Batch update node positions for drag and drop"""
    await node_service.batch_update_positions(
        positions=positions,
        user_id=current_user.id
    )
    return {"message": "Node positions updated successfully"}

@router.post("/{node_id}/connect/{target_node_id}")
async def connect_nodes(
    node_id: UUID,
    target_node_id: UUID,
    connection_type: str = "default",
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Connect two nodes"""
    connection = await node_service.connect_nodes(
        source_node_id=node_id,
        target_node_id=target_node_id,
        connection_type=connection_type,
        user_id=current_user.id
    )
    if not connection:
        raise HTTPException(status_code=400, detail="Failed to create connection")
    return connection

@router.delete("/{node_id}/disconnect/{target_node_id}")
async def disconnect_nodes(
    node_id: UUID,
    target_node_id: UUID,
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Disconnect two nodes"""
    success = await node_service.disconnect_nodes(
        source_node_id=node_id,
        target_node_id=target_node_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"message": "Nodes disconnected successfully"}

@router.get("/types/available")
async def get_available_node_types():
    """Get all available node types and their configurations"""
    return await NodeService.get_available_node_types()

@router.post("/{node_id}/validate")
async def validate_node(
    node_id: UUID,
    current_user: User = Depends(get_current_user),
    node_service: NodeService = Depends()
):
    """Validate a node's configuration"""
    validation_result = await node_service.validate_node(
        node_id=node_id,
        user_id=current_user.id
    )
    if validation_result is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return validation_result