"""
Marketplace Service
Handles agent marketplace functionality
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from ..schemas.agent import AgentResponse, MarketplaceAgent
except ImportError:
    from schemas.agent import AgentResponse, MarketplaceAgent

logger = logging.getLogger(__name__)

class MarketplaceService:
    """Service for managing agent marketplace"""
    
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.marketplace_agents: Dict[str, dict] = {}
        self.featured_agents: List[str] = []
        
    async def get_marketplace_agents(self) -> List[MarketplaceAgent]:
        """Get all agents available in marketplace"""
        agents = list(self.marketplace_agents.values())
        return [MarketplaceAgent(**agent) for agent in agents]
    
    async def publish_agent(self, agent_id: str) -> Dict[str, Any]:
        """Publish an agent to the marketplace"""
        # In a real implementation, this would get the agent from the agent service
        # For demo, we'll create a sample marketplace entry
        
        marketplace_agent = {
            "id": agent_id,
            "name": f"Agent {agent_id[:8]}",
            "description": "A powerful AI agent for various tasks",
            "agent_type": "voice",
            "status": "active",
            "capabilities": [],
            "configuration": None,
            "tags": ["ai", "voice", "assistant"],
            "is_public": True,
            "category": "general",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "usage_count": 0,
            "rating": 4.5,
            "owner_id": "demo_owner",
            "downloads": 0,
            "reviews": [],
            "publisher": "Vocelio AI",
            "verified": True
        }
        
        self.marketplace_agents[agent_id] = marketplace_agent
        logger.info(f"Published agent to marketplace: {agent_id}")
        
        return {
            "agent_id": agent_id,
            "status": "published",
            "marketplace_url": f"/marketplace/agents/{agent_id}"
        }
    
    async def install_agent(self, agent_id: str) -> Dict[str, Any]:
        """Install an agent from marketplace"""
        if agent_id not in self.marketplace_agents:
            raise ValueError("Agent not found in marketplace")
        
        # Increment download count
        self.marketplace_agents[agent_id]["downloads"] += 1
        
        logger.info(f"Installed agent from marketplace: {agent_id}")
        
        return {
            "agent_id": agent_id,
            "status": "installed",
            "installation_id": f"install_{agent_id}_{datetime.utcnow().timestamp()}"
        }
    
    async def get_featured_agents(self) -> List[MarketplaceAgent]:
        """Get featured agents"""
        featured = [
            self.marketplace_agents[agent_id] 
            for agent_id in self.featured_agents 
            if agent_id in self.marketplace_agents
        ]
        return [MarketplaceAgent(**agent) for agent in featured]
    
    async def add_to_featured(self, agent_id: str) -> bool:
        """Add agent to featured list"""
        if agent_id in self.marketplace_agents and agent_id not in self.featured_agents:
            self.featured_agents.append(agent_id)
            logger.info(f"Added agent to featured: {agent_id}")
            return True
        return False
    
    async def remove_from_featured(self, agent_id: str) -> bool:
        """Remove agent from featured list"""
        if agent_id in self.featured_agents:
            self.featured_agents.remove(agent_id)
            logger.info(f"Removed agent from featured: {agent_id}")
            return True
        return False
    
    async def get_popular_agents(self, limit: int = 10) -> List[MarketplaceAgent]:
        """Get most popular agents by download count"""
        agents = list(self.marketplace_agents.values())
        agents.sort(key=lambda x: x.get("downloads", 0), reverse=True)
        agents = agents[:limit]
        return [MarketplaceAgent(**agent) for agent in agents]
    
    async def get_top_rated_agents(self, limit: int = 10) -> List[MarketplaceAgent]:
        """Get top-rated agents"""
        agents = list(self.marketplace_agents.values())
        agents.sort(key=lambda x: x.get("rating", 0), reverse=True)
        agents = agents[:limit]
        return [MarketplaceAgent(**agent) for agent in agents]
    
    async def search_marketplace(self, query: str) -> List[MarketplaceAgent]:
        """Search marketplace agents"""
        query_lower = query.lower()
        matching_agents = []
        
        for agent in self.marketplace_agents.values():
            # Search in name, description, and tags
            if (query_lower in agent.get("name", "").lower() or 
                query_lower in agent.get("description", "").lower()):
                matching_agents.append(agent)
                continue
            
            # Search in tags
            tags = agent.get("tags", [])
            if any(query_lower in tag.lower() for tag in tags):
                matching_agents.append(agent)
        
        return [MarketplaceAgent(**agent) for agent in matching_agents]
    
    async def add_review(self, agent_id: str, review: Dict[str, Any]) -> bool:
        """Add a review to an agent"""
        if agent_id not in self.marketplace_agents:
            return False
        
        review_data = {
            "id": f"review_{len(self.marketplace_agents[agent_id]['reviews'])}",
            "rating": review.get("rating", 5),
            "comment": review.get("comment", ""),
            "author": review.get("author", "Anonymous"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.marketplace_agents[agent_id]["reviews"].append(review_data)
        
        # Update average rating
        reviews = self.marketplace_agents[agent_id]["reviews"]
        if reviews:
            avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
            self.marketplace_agents[agent_id]["rating"] = round(avg_rating, 1)
        
        logger.info(f"Added review to agent: {agent_id}")
        return True
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all marketplace categories with agent counts"""
        categories = {}
        
        for agent in self.marketplace_agents.values():
            category = agent.get("category", "uncategorized")
            if category not in categories:
                categories[category] = {"name": category, "count": 0}
            categories[category]["count"] += 1
        
        return list(categories.values())
