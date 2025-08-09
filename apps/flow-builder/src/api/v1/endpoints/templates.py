# apps/flow-builder/src/api/v1/endpoints/templates.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from services.template_service import TemplateService
from schemas.template import (
    FlowTemplateCreate, FlowTemplateUpdate, FlowTemplateResponse,
    NodeTemplateResponse
)
from shared.auth.dependencies import get_current_user
from shared.schemas.user import User

router = APIRouter()

@router.get("/flows", response_model=List[FlowTemplateResponse])
async def get_flow_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    template_service: TemplateService = Depends()
):
    """Get available flow templates"""
    return await template_service.get_flow_templates(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        category=category,
        search=search
    )

@router.post("/flows", response_model=FlowTemplateResponse)
async def create_flow_template(
    template_data: FlowTemplateCreate,
    current_user: User = Depends(get_current_user),
    template_service: TemplateService = Depends()
):
    """Create a new flow template"""
    return await template_service.create_flow_template(
        template_data=template_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )

@router.get("/flows/{template_id}", response_model=FlowTemplateResponse)
async def get_flow_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    template_service: TemplateService = Depends()
):
    """Get a specific flow template"""
    template = await template_service.get_flow_template_by_id(
        template_id=template_id,
        user_id=current_user.id
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/flows/{template_id}/use")
async def use_flow_template(
    template_id: UUID,
    flow_name: str,
    current_user: User = Depends(get_current_user),
    template_service: TemplateService = Depends()
):
    """Create a new flow from a template"""
    flow = await template_service.create_flow_from_template(
        template_id=template_id,
        flow_name=flow_name,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    if not flow:
        raise HTTPException(status_code=404, detail="Template not found")
    return flow

@router.get("/nodes", response_model=List[NodeTemplateResponse])
async def get_node_templates(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    template_service: TemplateService = Depends()
):
    """Get available node templates"""
    return await template_service.get_node_templates(
        category=category,
        organization_id=current_user.organization_id
    )

@router.post("/nodes", response_model=NodeTemplateResponse)
async def create_node_template(
    template_data: dict,
    current_user: User = Depends(get_current_user),
    template_service: TemplateService = Depends()
):
    """Create a new node template"""
    return await template_service.create_node_template(
        template_data=template_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )

@router.get("/categories")
async def get_template_categories():
    """Get available template categories"""
    return {
        "flow_categories": [
            "Sales & Lead Qualification",
            "Customer Support",
            "Appointment Scheduling",
            "Survey & Feedback",
            "Order Processing",
            "Technical Support",
            "Emergency Response",
            "Marketing & Promotions"
        ],
        "node_categories": [
            "control",
            "communication", 
            "logic",
            "ai",
            "input",
            "action",
            "integration"
        ]
    }

@router.get("/flows/featured", response_model=List[FlowTemplateResponse])
async def get_featured_templates(
    current_user: User = Depends(get_current_user),
    template_service: TemplateService = Depends()
):
    """Get featured flow templates"""
    return await template_service.get_featured_templates(
        organization_id=current_user.organization_id
    )