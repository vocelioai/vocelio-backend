# apps/flow-builder/src/api/v1/endpoints/execution.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from services.execution_service import FlowExecutionService
from schemas.execution import ExecutionRequest, ExecutionResponse, FlowExecution
from shared.auth.dependencies import get_current_user
from shared.schemas.user import User

router = APIRouter()

@router.post("/{flow_id}/execute", response_model=ExecutionResponse)
async def execute_flow(
    flow_id: UUID,
    execution_data: ExecutionRequest,
    current_user: User = Depends(get_current_user),
    execution_service: FlowExecutionService = Depends()
):
    """Execute a flow with given input data"""
    return await execution_service.execute_flow(
        flow_id=flow_id,
        execution_data=execution_data,
        user_id=current_user.id
    )

@router.post("/{flow_id}/test", response_model=ExecutionResponse)
async def test_flow(
    flow_id: UUID,
    execution_data: ExecutionRequest,
    current_user: User = Depends(get_current_user),
    execution_service: FlowExecutionService = Depends()
):
    """Test execute a flow (same as execute but marked as test)"""
    # Add test flag to context
    execution_data.context = execution_data.context or {}
    execution_data.context["is_test"] = True
    
    return await execution_service.execute_flow(
        flow_id=flow_id,
        execution_data=execution_data,
        user_id=current_user.id
    )

@router.get("/{flow_id}/executions", response_model=List[FlowExecution])
async def get_flow_executions(
    flow_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    execution_service: FlowExecutionService = Depends()
):
    """Get execution history for a flow"""
    return await execution_service.get_flow_executions(
        flow_id=flow_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )

@router.get("/execution/{execution_id}", response_model=ExecutionResponse)
async def get_execution_details(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    execution_service: FlowExecutionService = Depends()
):
    """Get detailed execution information"""
    execution = await execution_service.get_execution_by_id(
        execution_id=execution_id,
        user_id=current_user.id
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.post("/execution/{execution_id}/cancel")
async def cancel_execution(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    execution_service: FlowExecutionService = Depends()
):
    """Cancel a running execution"""
    success = await execution_service.cancel_execution(
        execution_id=execution_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
    return {"message": "Execution cancelled successfully"}

@router.get("/{flow_id}/validate")
async def validate_flow(
    flow_id: UUID,
    current_user: User = Depends(get_current_user),
    execution_service: FlowExecutionService = Depends()
):
    """Validate a flow for execution"""
    validation_result = await execution_service.validate_flow_for_execution(
        flow_id=flow_id,
        user_id=current_user.id
    )
    if validation_result is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    return validation_result

@router.get("/{flow_id}/analytics")
async def get_flow_analytics(
    flow_id: UUID,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    execution_service: FlowExecutionService = Depends()
):
    """Get flow execution analytics"""
    analytics = await execution_service.get_flow_analytics(
        flow_id=flow_id,
        user_id=current_user.id,
        days=days
    )
    if analytics is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    return analytics