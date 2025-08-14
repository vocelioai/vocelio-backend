"""
AI Agent Platform Service
Manages AI agents, their configurations, and marketplace functionality
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🤖 AI Agent Platform",
    version="1.0.0",
    description="Vocelio.ai AI Agent Management and Marketplace Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import services
try:
    from .services.agent_management_service import AgentManagementService
    from .services.marketplace_service import MarketplaceService
    from .services.analytics_service import AnalyticsService
    from .schemas.agent import AgentCreate, AgentResponse, AgentUpdate
except ImportError:
    from services.agent_management_service import AgentManagementService
    from services.marketplace_service import MarketplaceService
    from services.analytics_service import AnalyticsService
    from schemas.agent import AgentCreate, AgentResponse, AgentUpdate

# Initialize services
agent_service = AgentManagementService()
marketplace_service = MarketplaceService()
analytics_service = AnalyticsService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-agent-platform",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🤖 AI Agent Platform Service",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "agents": "/agents",
            "marketplace": "/marketplace",
            "analytics": "/analytics"
        }
    }

# Agent Management Endpoints
@app.post("/agents", response_model=AgentResponse)
async def create_agent(agent: AgentCreate):
    """Create a new AI agent"""
    try:
        return await agent_service.create_agent(agent)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None
):
    """List all AI agents"""
    try:
        return await agent_service.list_agents(skip=skip, limit=limit, category=category)
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get specific agent by ID"""
    try:
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent_update: AgentUpdate):
    """Update an existing agent"""
    try:
        agent = await agent_service.update_agent(agent_id, agent_update)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    try:
        success = await agent_service.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Marketplace Endpoints
@app.get("/marketplace")
async def get_marketplace():
    """Get marketplace agents"""
    try:
        return await marketplace_service.get_marketplace_agents()
    except Exception as e:
        logger.error(f"Error getting marketplace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/marketplace/{agent_id}/publish")
async def publish_to_marketplace(agent_id: str):
    """Publish agent to marketplace"""
    try:
        result = await marketplace_service.publish_agent(agent_id)
        return {"message": "Agent published to marketplace", "result": result}
    except Exception as e:
        logger.error(f"Error publishing agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/marketplace/{agent_id}/install")
async def install_from_marketplace(agent_id: str):
    """Install agent from marketplace"""
    try:
        result = await marketplace_service.install_agent(agent_id)
        return {"message": "Agent installed successfully", "result": result}
    except Exception as e:
        logger.error(f"Error installing agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@app.get("/analytics/usage")
async def get_usage_analytics():
    """Get agent usage analytics"""
    try:
        return await analytics_service.get_usage_analytics()
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/performance")
async def get_performance_analytics():
    """Get agent performance analytics"""
    try:
        return await analytics_service.get_performance_analytics()
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
