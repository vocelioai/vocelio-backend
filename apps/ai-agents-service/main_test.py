#!/usr/bin/env python3
"""
🤖 Vocelio.ai AI Agents Service - Test Version
Simplified version for testing without database dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import uvicorn

# Pydantic Models
class AIAgent(BaseModel):
    """AI Agent model"""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    industry: str = Field(..., description="Industry specialization")
    status: str = Field(..., description="Agent status")
    performance_score: float = Field(..., description="Performance score")
    calls_today: int = Field(..., description="Calls made today")
    success_rate: float = Field(..., description="Success rate percentage")
    revenue_generated: float = Field(..., description="Revenue generated")
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)

class AgentAnalytics(BaseModel):
    """Agent analytics data"""
    total_agents: int = Field(..., description="Total number of agents")
    active_agents: int = Field(..., description="Currently active agents")
    avg_performance: float = Field(..., description="Average performance score")
    total_calls_today: int = Field(..., description="Total calls today")
    total_revenue: float = Field(..., description="Total revenue generated")
    industry_breakdown: Dict[str, int] = Field(default_factory=dict)

# Mock data
INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Real Estate", "E-commerce",
    "Education", "Manufacturing", "Retail", "Professional Services",
    "Automotive", "Energy", "Media", "Legal", "Insurance", "Hospitality"
]

def generate_agent(agent_id: str) -> AIAgent:
    """Generate a mock AI agent"""
    # Handle agent_id that might not have underscore
    parts = agent_id.split('_')
    agent_name = f"Agent {parts[-1]}" if len(parts) > 1 else f"Agent {agent_id}"
    
    return AIAgent(
        agent_id=agent_id,
        name=agent_name,
        industry=random.choice(INDUSTRIES),
        status=random.choice(["active", "idle", "training"]),
        performance_score=round(random.uniform(75, 98), 1),
        calls_today=random.randint(15, 85),
        success_rate=round(random.uniform(65, 95), 1),
        revenue_generated=round(random.uniform(500, 2500), 2)
    )

def generate_analytics() -> AgentAnalytics:
    """Generate agent analytics"""
    industry_breakdown = {industry: random.randint(5, 25) for industry in INDUSTRIES[:10]}
    
    return AgentAnalytics(
        total_agents=247,
        active_agents=random.randint(180, 220),
        avg_performance=round(random.uniform(82, 92), 1),
        total_calls_today=random.randint(3500, 5500),
        total_revenue=round(random.uniform(35000, 55000), 2),
        industry_breakdown=industry_breakdown
    )

# Initialize FastAPI app
app = FastAPI(
    title="Vocelio.ai AI Agents Service",
    description="AI agent management and optimization service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-agents",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Get all agents endpoint
@app.get("/api/v1/agents", response_model=List[Dict[str, Any]])
async def get_all_agents(limit: int = 50, offset: int = 0):
    """Get all AI agents"""
    agents = [generate_agent(f"agent_{i+1+offset}") for i in range(min(limit, 50))]
    # Add id field for compatibility
    agent_dicts = []
    for agent in agents:
        agent_dict = agent.model_dump()
        agent_dict['id'] = agent.agent_id
        agent_dicts.append(agent_dict)
    return agent_dicts

# Get agent analytics endpoint (must be before {agent_id} route)
@app.get("/api/v1/agents/analytics", response_model=AgentAnalytics)
async def get_agent_analytics():
    """Get agent analytics"""
    return generate_analytics()

# Get single agent endpoint
@app.get("/api/v1/agents/{agent_id}", response_model=AIAgent)
async def get_agent(agent_id: str):
    """Get a specific AI agent"""
    return generate_agent(agent_id)

# Create agent endpoint
@app.post("/api/v1/agents", response_model=AIAgent)
async def create_agent(agent_data: Dict[str, Any]):
    """Create a new AI agent"""
    agent_id = f"agent_{random.randint(1000, 9999)}"
    agent = generate_agent(agent_id)
    agent.name = agent_data.get("name", agent.name)
    agent.industry = agent_data.get("industry", agent.industry)
    # Return the agent with an 'id' field for compatibility
    agent_dict = agent.model_dump()
    agent_dict['id'] = agent.agent_id
    return agent_dict

# Update agent endpoint
@app.put("/api/v1/agents/{agent_id}", response_model=AIAgent)
async def update_agent(agent_id: str, agent_data: Dict[str, Any]):
    """Update an AI agent"""
    agent = generate_agent(agent_id)
    if "name" in agent_data:
        agent.name = agent_data["name"]
    if "industry" in agent_data:
        agent.industry = agent_data["industry"]
    if "status" in agent_data:
        agent.status = agent_data["status"]
    return agent

if __name__ == "__main__":
    uvicorn.run(
        "main_test:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
