# apps/flow-builder/src/api/v1/endpoints/flows.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from services.flow_service import FlowService
from schemas.flow import FlowCreate, FlowUpdate, FlowResponse, FlowList
from shared.auth.dependencies import get_current_user
from shared.schemas.user import User

router = APIRouter()

@router.get("/", response_model=List[FlowResponse])
async def get_flows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Get all flows for the current user/organization"""
    return await flow_service.get_flows(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        search=search,
        category=category
    )

@router.post("/", response_model=FlowResponse)
async def create_flow(
    flow_data: FlowCreate,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Create a new flow"""
    return await flow_service.create_flow(
        flow_data=flow_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )

@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Get a specific flow by ID"""
    flow = await flow_service.get_flow_by_id(
        flow_id=flow_id,
        user_id=current_user.id
    )
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow

@router.put("/{flow_id}", response_model=FlowResponse)
async def update_flow(
    flow_id: UUID,
    flow_data: FlowUpdate,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Update an existing flow"""
    flow = await flow_service.update_flow(
        flow_id=flow_id,
        flow_data=flow_data,
        user_id=current_user.id
    )
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow

@router.delete("/{flow_id}")
async def delete_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Delete a flow"""
    success = await flow_service.delete_flow(
        flow_id=flow_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Flow not found")
    return {"message": "Flow deleted successfully"}

@router.post("/{flow_id}/duplicate", response_model=FlowResponse)
async def duplicate_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Duplicate an existing flow"""
    flow = await flow_service.duplicate_flow(
        flow_id=flow_id,
        user_id=current_user.id
    )
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow

@router.post("/{flow_id}/publish")
async def publish_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Publish a flow for production use"""
    success = await flow_service.publish_flow(
        flow_id=flow_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Flow not found")
    return {"message": "Flow published successfully"}

@router.post("/{flow_id}/unpublish")
async def unpublish_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Unpublish a flow"""
    success = await flow_service.unpublish_flow(
        flow_id=flow_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Flow not found")
    return {"message": "Flow unpublished successfully"}

@router.get("/{flow_id}/versions")
async def get_flow_versions(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Get all versions of a flow"""
    versions = await flow_service.get_flow_versions(
        flow_id=flow_id,
        user_id=current_user.id
    )
    return versions

@router.post("/{flow_id}/save-version")
async def save_flow_version(
    flow_id: UUID,
    version_name: str,
    current_user: User = Depends(get_current_user),
    flow_service: FlowService = Depends()
):
    """Save current flow state as a new version"""
    version = await flow_service.save_flow_version(
        flow_id=flow_id,
        version_name=version_name,
        user_id=current_user.id
    )
    if not version:
        raise HTTPException(status_code=404, detail="Flow not found")
    return version