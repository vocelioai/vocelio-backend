# apps/call-center/src/api/v1/endpoints/inbound.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.inbound_service import InboundService
from schemas.inbound import (
    QueueStatus, QueueMetrics, SLAMetrics, DepartmentConfig,
    CallRouting, InboundCall, QueueConfig
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/queue", response_model=QueueStatus)
async def get_queue_status(
    queue_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get current inbound queue status"""
    inbound_service = InboundService()
    
    try:
        status = await inbound_service.get_queue_status(queue_id)
        return status
        
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get queue status")

@router.get("/queue/metrics", response_model=QueueMetrics)
async def get_queue_metrics(
    queue_id: Optional[str] = None,
    period: str = Query("today", regex="^(today|week|month)$"),
    current_user: User = Depends(get_current_user)
):
    """Get queue performance metrics"""
    inbound_service = InboundService()
    
    try:
        metrics = await inbound_service.get_queue_metrics(queue_id, period)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting queue metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get queue metrics")

@router.get("/sla-metrics", response_model=SLAMetrics)
async def get_sla_metrics(
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get Service Level Agreement metrics"""
    inbound_service = InboundService()
    
    try:
        sla_metrics = await inbound_service.get_sla_metrics(department)
        return sla_metrics
        
    except Exception as e:
        logger.error(f"Error getting SLA metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SLA metrics")

@router.get("/departments", response_model=List[DepartmentConfig])
async def get_departments(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user)
):
    """Get department configurations for call routing"""
    inbound_service = InboundService()
    
    try:
        departments = await inbound_service.get_departments(active_only)
        return departments
        
    except Exception as e:
        logger.error(f"Error getting departments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get departments")

@router.post("/departments", response_model=DepartmentConfig)
async def create_department(
    department: DepartmentConfig,
    current_user: User = Depends(get_current_user)
):
    """Create new department configuration"""
    inbound_service = InboundService()
    
    try:
        created_dept = await inbound_service.create_department(department, current_user.id)
        logger.info(f"Department {department.name} created by user {current_user.id}")
        return created_dept
        
    except Exception as e:
        logger.error(f"Error creating department: {e}")
        raise HTTPException(status_code=500, detail="Failed to create department")

@router.put("/departments/{department_id}", response_model=DepartmentConfig)
async def update_department(
    department_id: str,
    department_update: DepartmentConfig,
    current_user: User = Depends(get_current_user)
):
    """Update department configuration"""
    inbound_service = InboundService()
    
    try:
        updated_dept = await inbound_service.update_department(
            department_id, department_update, current_user.id
        )
        if not updated_dept:
            raise HTTPException(status_code=404, detail="Department not found")
        
        return updated_dept
        
    except Exception as e:
        logger.error(f"Error updating department: {e}")
        raise HTTPException(status_code=500, detail="Failed to update department")

@router.post("/route-call")
async def route_inbound_call(
    routing: CallRouting,
    current_user: User = Depends(get_current_user)
):
    """Route incoming call to appropriate department/agent"""
    inbound_service = InboundService()
    
    try:
        result = await inbound_service.route_call(routing)
        logger.info(f"Call {routing.call_id} routed to {routing.target_type}: {routing.target_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error routing call: {e}")
        raise HTTPException(status_code=500, detail="Failed to route call")

@router.get("/calls", response_model=List[InboundCall])
async def get_inbound_calls(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Get list of inbound calls with filtering"""
    inbound_service = InboundService()
    
    try:
        filters = {}
        if status and status != "all":
            filters["status"] = status
        if department and department != "all":
            filters["department"] = department
        
        calls = await inbound_service.get_inbound_calls(
            limit=limit, offset=offset, filters=filters
        )
        return calls
        
    except Exception as e:
        logger.error(f"Error getting inbound calls: {e}")
        raise HTTPException(status_code=500, detail="Failed to get inbound calls")

@router.post("/queue/priority")
async def update_call_priority(
    call_id: str,
    priority: int = Query(..., ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """Update call priority in queue"""
    inbound_service = InboundService()
    
    try:
        success = await inbound_service.update_call_priority(call_id, priority)
        if not success:
            raise HTTPException(status_code=404, detail="Call not found in queue")
        
        return {"message": "Call priority updated successfully", "call_id": call_id, "priority": priority}
        
    except Exception as e:
        logger.error(f"Error updating call priority: {e}")
        raise HTTPException(status_code=500, detail="Failed to update call priority")

@router.get("/analytics/distribution")
async def get_call_distribution(
    period: str = Query("today", regex="^(today|week|month)$"),
    current_user: User = Depends(get_current_user)
):
    """Get call distribution analytics by department"""
    inbound_service = InboundService()
    
    try:
        distribution = await inbound_service.get_call_distribution(period)
        return distribution
        
    except Exception as e:
        logger.error(f"Error getting call distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to get call distribution")

@router.post("/agents/assign")
async def assign_agent_to_queue(
    agent_id: str,
    queue_id: str,
    priority: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """Assign agent to inbound queue"""
    inbound_service = InboundService()
    
    try:
        success = await inbound_service.assign_agent_to_queue(agent_id, queue_id, priority)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to assign agent to queue")
        
        return {"message": "Agent assigned to queue successfully", "agent_id": agent_id, "queue_id": queue_id}
        
    except Exception as e:
        logger.error(f"Error assigning agent to queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign agent to queue")

@router.delete("/agents/{agent_id}/queue/{queue_id}")
async def remove_agent_from_queue(
    agent_id: str,
    queue_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove agent from inbound queue"""
    inbound_service = InboundService()
    
    try:
        success = await inbound_service.remove_agent_from_queue(agent_id, queue_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent assignment not found")
        
        return {"message": "Agent removed from queue successfully", "agent_id": agent_id, "queue_id": queue_id}
        
    except Exception as e:
        logger.error(f"Error removing agent from queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove agent from queue")
