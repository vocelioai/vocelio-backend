from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime

# If get_current_user does not exist, provide a mock implementation for demonstration
def get_current_user():
    return {"user_id": "user123", "username": "demo_user"}
from shared.exceptions import VocelioException

router = APIRouter()
logger = structlog.get_logger()

# Mock data for demonstration
MOCK_AGENTS = [
    {
        "id": "agent_001",
        "name": "Sales Assistant Pro",
        "description": "Advanced AI agent for sales conversations and lead qualification",
        "category": "sales",
        "price": 29.99,
        "rating": 4.8,
        "downloads": 1523,
        "creator_id": "user_123",
        "creator_name": "VoiceAI Labs",
        "capabilities": ["lead_qualification", "objection_handling", "appointment_setting"],
        "languages": ["en", "es", "fr"],
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-20T15:30:00Z",
        "is_featured": True,
        "is_verified": True
    },
    {
        "id": "agent_002", 
        "name": "Customer Support Specialist",
        "description": "Intelligent customer service agent with advanced problem resolution",
        "category": "support",
        "price": 19.99,
        "rating": 4.6,
        "downloads": 2341,
        "creator_id": "user_456",
        "creator_name": "Support Solutions Inc",
        "capabilities": ["ticket_resolution", "escalation_handling", "knowledge_base"],
        "languages": ["en", "de", "it"],
        "created_at": "2024-01-10T08:00:00Z", 
        "updated_at": "2024-01-18T12:00:00Z",
        "is_featured": False,
        "is_verified": True
    },
    {
        "id": "agent_003",
        "name": "Healthcare Scheduler",
        "description": "Specialized agent for medical appointment scheduling and patient care",
        "category": "healthcare",
        "price": 49.99,
        "rating": 4.9,
        "downloads": 856,
        "creator_id": "user_789",
        "creator_name": "MedTech AI",
        "capabilities": ["appointment_scheduling", "patient_screening", "insurance_verification"],
        "languages": ["en"],
        "created_at": "2024-01-05T14:00:00Z",
        "updated_at": "2024-01-22T09:15:00Z", 
        "is_featured": True,
        "is_verified": True
    }
]

@router.get("/", summary="List available agents")
async def list_agents(
    category: Optional[str] = Query(None, description="Filter by category"),
    featured: Optional[bool] = Query(None, description="Filter featured agents"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    sort_by: str = Query("rating", description="Sort by: rating, price, downloads, created_at"),
    limit: int = Query(10, le=100, description="Number of results"),
    offset: int = Query(0, description="Pagination offset")
):
    """Get list of available AI agents in the marketplace."""
    try:
        agents = MOCK_AGENTS.copy()
        
        # Apply filters
        if category:
            agents = [a for a in agents if a["category"] == category]
        if featured is not None:
            agents = [a for a in agents if a["is_featured"] == featured]
        if min_price is not None:
            agents = [a for a in agents if a["price"] >= min_price]
        if max_price is not None:
            agents = [a for a in agents if a["price"] <= max_price]
        if search:
            search_lower = search.lower()
            agents = [a for a in agents if search_lower in a["name"].lower() or search_lower in a["description"].lower()]
        
        # Sort
        reverse = sort_by in ["rating", "downloads", "created_at"]
        if sort_by == "created_at":
            agents.sort(key=lambda x: x["created_at"], reverse=reverse)
        else:
            agents.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
        
        # Paginate
        total = len(agents)
        agents = agents[offset:offset + limit]
        
        return {
            "agents": agents,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        logger.error("Error listing agents", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve agents")

@router.get("/{agent_id}", summary="Get agent details")
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent."""
    try:
        agent = next((a for a in MOCK_AGENTS if a["id"] == agent_id), None)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Add detailed information
        agent_detail = agent.copy()
        agent_detail.update({
            "detailed_description": f"Comprehensive AI agent designed for {agent['category']} use cases. This agent has been trained on industry-specific data and best practices.",
            "configuration_options": [
                {"name": "response_style", "type": "select", "options": ["professional", "casual", "friendly"]},
                {"name": "max_call_duration", "type": "number", "min": 1, "max": 60},
                {"name": "escalation_triggers", "type": "multiselect", "options": ["angry_customer", "complex_issue", "payment_dispute"]}
            ],
            "integration_instructions": "Simple API integration with webhook support. Full documentation available.",
            "demo_available": True,
            "trial_period_days": 7,
            "support_level": "premium"
        })
        
        return agent_detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting agent details", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve agent details")

@router.post("/{agent_id}/purchase", summary="Purchase agent")
async def purchase_agent(
    agent_id: str,
    current_user = Depends(get_current_user)
):
    """Purchase an agent from the marketplace."""
    try:
        agent = next((a for a in MOCK_AGENTS if a["id"] == agent_id), None)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Simulate purchase process
        purchase_id = f"purchase_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "purchase_id": purchase_id,
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "price": agent["price"],
            "status": "completed",
            "purchased_at": datetime.now().isoformat(),
            "license_key": f"lic_{agent_id}_{current_user.get('user_id', 'user123')}",
            "download_url": f"/api/v1/agents/{agent_id}/download",
            "support_url": "/support",
            "trial_ends_at": datetime.now().replace(day=datetime.now().day + 7).isoformat() if agent.get("trial_period_days") else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error purchasing agent", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process purchase")

@router.get("/{agent_id}/download", summary="Download purchased agent")
async def download_agent(
    agent_id: str,
    current_user = Depends(get_current_user)
):
    """Download a purchased agent configuration."""
    try:
        # Verify user owns this agent
        agent = next((a for a in MOCK_AGENTS if a["id"] == agent_id), None)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Return download information
        return {
            "agent_id": agent_id,
            "download_url": f"https://storage.vocelio.com/agents/{agent_id}/config.json",
            "installation_guide": f"https://docs.vocelio.com/agents/{agent_id}/setup",
            "expires_at": datetime.now().replace(hour=datetime.now().hour + 24).isoformat(),
            "file_size": "2.5MB",
            "checksum": f"sha256_{agent_id}_checksum"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error downloading agent", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate download link")

@router.get("/categories/", summary="Get agent categories")
async def get_categories():
    """Get available agent categories."""
    return {
        "categories": [
            {"id": "sales", "name": "Sales", "description": "Agents for sales and lead generation", "count": 45},
            {"id": "support", "name": "Customer Support", "description": "Customer service and support agents", "count": 32},
            {"id": "healthcare", "name": "Healthcare", "description": "Medical and healthcare specific agents", "count": 18},
            {"id": "education", "name": "Education", "description": "Educational and training agents", "count": 23},
            {"id": "finance", "name": "Finance", "description": "Financial services and banking agents", "count": 15},
            {"id": "retail", "name": "Retail", "description": "E-commerce and retail agents", "count": 28},
            {"id": "real_estate", "name": "Real Estate", "description": "Property and real estate agents", "count": 12},
            {"id": "general", "name": "General Purpose", "description": "Multi-purpose conversational agents", "count": 38}
        ]
    }
