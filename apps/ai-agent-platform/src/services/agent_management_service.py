"""
Agent Management Service
Handles CRUD operations for AI agents
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

try:
    from ..schemas.agent import AgentCreate, AgentResponse, AgentUpdate, AgentStatus
except ImportError:
    from schemas.agent import AgentCreate, AgentResponse, AgentUpdate, AgentStatus

logger = logging.getLogger(__name__)

class AgentManagementService:
    """Service for managing AI agents"""
    
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.agents: Dict[str, dict] = {}
        
    async def create_agent(self, agent_data: AgentCreate) -> AgentResponse:
        """Create a new AI agent"""
        agent_id = str(uuid.uuid4())
        
        agent = {
            "id": agent_id,
            "name": agent_data.name,
            "description": agent_data.description,
            "agent_type": agent_data.agent_type,
            "status": AgentStatus.DRAFT,
            "capabilities": [cap.dict() for cap in agent_data.capabilities],
            "configuration": agent_data.configuration.dict() if agent_data.configuration else None,
            "tags": agent_data.tags,
            "is_public": agent_data.is_public,
            "category": agent_data.category,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "usage_count": 0,
            "rating": 0.0,
            "owner_id": None  # Set based on authentication
        }
        
        self.agents[agent_id] = agent
        logger.info(f"Created agent: {agent_id}")
        
        return AgentResponse(**agent)
    
    async def get_agent(self, agent_id: str) -> Optional[AgentResponse]:
        """Get an agent by ID"""
        agent = self.agents.get(agent_id)
        if agent:
            return AgentResponse(**agent)
        return None
    
    async def list_agents(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        category: Optional[str] = None
    ) -> List[AgentResponse]:
        """List all agents with optional filtering"""
        agents = list(self.agents.values())
        
        # Filter by category if provided
        if category:
            agents = [agent for agent in agents if agent.get("category") == category]
        
        # Apply pagination
        agents = agents[skip:skip + limit]
        
        return [AgentResponse(**agent) for agent in agents]
    
    async def update_agent(self, agent_id: str, agent_update: AgentUpdate) -> Optional[AgentResponse]:
        """Update an existing agent"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        
        # Update fields that are provided
        update_data = agent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "capabilities" and value:
                agent[field] = [cap.dict() for cap in value]
            elif field == "configuration" and value:
                agent[field] = value.dict()
            else:
                agent[field] = value
        
        agent["updated_at"] = datetime.utcnow()
        
        logger.info(f"Updated agent: {agent_id}")
        return AgentResponse(**agent)
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Deleted agent: {agent_id}")
            return True
        return False
    
    async def activate_agent(self, agent_id: str) -> bool:
        """Activate an agent"""
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = AgentStatus.ACTIVE
            self.agents[agent_id]["updated_at"] = datetime.utcnow()
            logger.info(f"Activated agent: {agent_id}")
            return True
        return False
    
    async def deactivate_agent(self, agent_id: str) -> bool:
        """Deactivate an agent"""
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = AgentStatus.INACTIVE
            self.agents[agent_id]["updated_at"] = datetime.utcnow()
            logger.info(f"Deactivated agent: {agent_id}")
            return True
        return False
    
    async def increment_usage(self, agent_id: str) -> bool:
        """Increment usage count for an agent"""
        if agent_id in self.agents:
            self.agents[agent_id]["usage_count"] += 1
            logger.debug(f"Incremented usage for agent: {agent_id}")
            return True
        return False
    
    async def update_rating(self, agent_id: str, rating: float) -> bool:
        """Update agent rating"""
        if agent_id in self.agents and 0 <= rating <= 5:
            self.agents[agent_id]["rating"] = rating
            self.agents[agent_id]["updated_at"] = datetime.utcnow()
            logger.info(f"Updated rating for agent {agent_id}: {rating}")
            return True
        return False
    
    async def get_agents_by_type(self, agent_type: str) -> List[AgentResponse]:
        """Get all agents of a specific type"""
        agents = [
            agent for agent in self.agents.values() 
            if agent.get("agent_type") == agent_type
        ]
        return [AgentResponse(**agent) for agent in agents]
    
    async def search_agents(self, query: str) -> List[AgentResponse]:
        """Search agents by name, description, or tags"""
        query_lower = query.lower()
        matching_agents = []
        
        for agent in self.agents.values():
            # Search in name and description
            if (query_lower in agent.get("name", "").lower() or 
                query_lower in agent.get("description", "").lower()):
                matching_agents.append(agent)
                continue
            
            # Search in tags
            tags = agent.get("tags", [])
            if any(query_lower in tag.lower() for tag in tags):
                matching_agents.append(agent)
        
        return [AgentResponse(**agent) for agent in matching_agents]
