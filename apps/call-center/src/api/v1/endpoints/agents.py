# apps/call-center/src/api/v1/endpoints/agents.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.agent_service import AgentService
from schemas.agent import (
    Agent, AgentCreate, AgentUpdate, AgentStatus, 
    AgentPerformance, AgentMetrics, StatusUpdate
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[Agent])
async def get_agents(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    agent_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Get list of agents with filtering"""
    agent_service = AgentService()
    
    try:
        filters = {}
        if status and status != "all":
            filters["status"] = status
        if department and department != "all":
            filters["department"] = department
        if agent_type and agent_type != "all":
            filters["agent_type"] = agent_type
        
        agents = await agent_service.get_agents(
            limit=limit, offset=offset, filters=filters
        )
        return agents
        
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agents")

@router.post("/", response_model=Agent)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new agent"""
    agent_service = AgentService()
    
    try:
        # Validate agent data
        if agent_data.agent_type == "human" and not agent_data.user_id:
            raise HTTPException(status_code=400, detail="User ID required for human agents")
        
        agent = await agent_service.create_agent(agent_data, current_user.id)
        logger.info(f"Agent {agent_data.name} created by user {current_user.id}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create agent")

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific agent details"""
    agent_service = AgentService()
    
    try:
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent")

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update agent information"""
    agent_service = AgentService()
    
    try:
        updated_agent = await agent_service.update_agent(
            agent_id, agent_update, current_user.id
        )
        if not updated_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        logger.info(f"Agent {agent_id} updated by user {current_user.id}")
        return updated_agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to update agent")

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete agent"""
    agent_service = AgentService()
    
    try:
        # Check if agent is currently active
        if await agent_service.is_agent_active(agent_id):
            raise HTTPException(
                status_code=409, 
                detail="Cannot delete active agent. Please set status to inactive first."
            )
        
        success = await agent_service.delete_agent(agent_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        logger.info(f"Agent {agent_id} deleted by user {current_user.id}")
        return {"message": "Agent deleted successfully", "agent_id": agent_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete agent")

@router.put("/{agent_id}/status", response_model=AgentStatus)
async def update_agent_status(
    agent_id: str,
    status_update: StatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update agent status (available, busy, break, offline)"""
    agent_service = AgentService()
    
    try:
        status = await agent_service.update_status(
            agent_id, status_update, current_user.id
        )
        if not status:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        logger.info(f"Agent {agent_id} status updated to {status_update.status} by user {current_user.id}")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update agent status")

@router.get("/{agent_id}/performance", response_model=AgentPerformance)
async def get_agent_performance(
    agent_id: str,
    period: str = Query("today", regex="^(today|week|month|quarter|year)$"),
    include_details: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """Get agent performance metrics"""
    agent_service = AgentService()
    
    try:
        performance = await agent_service.get_performance(
            agent_id, period, include_details
        )
        if not performance:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent performance")

@router.get("/{agent_id}/metrics", response_model=AgentMetrics)
async def get_agent_metrics(
    agent_id: str,
    period: str = Query("today", regex="^(today|week|month)$"),
    current_user: User = Depends(get_current_user)
):
    """Get detailed agent metrics"""
    agent_service = AgentService()
    
    try:
        metrics = await agent_service.get_metrics(agent_id, period)
        if not metrics:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent metrics")

@router.post("/{agent_id}/assign-skill")
async def assign_skill_to_agent(
    agent_id: str,
    skill_id: str,
    proficiency_level: int = Query(..., ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """Assign skill to agent with proficiency level"""
    agent_service = AgentService()
    
    try:
        success = await agent_service.assign_skill(
            agent_id, skill_id, proficiency_level, current_user.id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Agent or skill not found")
        
        return {
            "message": "Skill assigned successfully",
            "agent_id": agent_id,
            "skill_id": skill_id,
            "proficiency_level": proficiency_level
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning skill to agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign skill")

@router.delete("/{agent_id}/skills/{skill_id}")
async def remove_skill_from_agent(
    agent_id: str,
    skill_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove skill from agent"""
    agent_service = AgentService()
    
    try:
        success = await agent_service.remove_skill(agent_id, skill_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent skill assignment not found")
        
        return {"message": "Skill removed successfully", "agent_id": agent_id, "skill_id": skill_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing skill from agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove skill")

@router.post("/{agent_id}/schedule")
async def update_agent_schedule(
    agent_id: str,
    schedule_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update agent work schedule"""
    agent_service = AgentService()
    
    try:
        # Validate schedule data
        required_fields = ["start_time", "end_time", "days_of_week"]
        if not all(field in schedule_data for field in required_fields):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: start_time, end_time, days_of_week"
            )
        
        success = await agent_service.update_schedule(
            agent_id, schedule_data, current_user.id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {"message": "Schedule updated successfully", "agent_id": agent_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to update schedule")

@router.post("/{agent_id}/training")
async def assign_training_to_agent(
    agent_id: str,
    training_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Assign training module to agent"""
    agent_service = AgentService()
    
    try:
        # Validate training data
        required_fields = ["training_module_id", "due_date"]
        if not all(field in training_data for field in required_fields):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: training_module_id, due_date"
            )
        
        success = await agent_service.assign_training(
            agent_id, training_data, current_user.id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Agent or training module not found")
        
        # Send training notification in background
        background_tasks.add_task(
            agent_service.send_training_notification, 
            agent_id, 
            training_data["training_module_id"]
        )
        
        return {"message": "Training assigned successfully", "agent_id": agent_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning training: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign training")

@router.get("/stats/overview")
async def get_agents_overview(
    department: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get overview statistics for all agents"""
    agent_service = AgentService()
    
    try:
        overview = await agent_service.get_agents_overview(department)
        return overview
        
    except Exception as e:
        logger.error(f"Error getting agents overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agents overview")
