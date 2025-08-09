#!/usr/bin/env python3
"""
📢 Vocelio.ai Smart Campaigns Service - Test Version
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
class SmartCampaign(BaseModel):
    """Smart Campaign model"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    name: str = Field(..., description="Campaign name")
    status: str = Field(..., description="Campaign status")
    industry: str = Field(..., description="Target industry")
    ai_optimization_level: float = Field(..., description="AI optimization level")
    target_audience: str = Field(..., description="Target audience description")
    calls_made: int = Field(..., description="Total calls made")
    success_rate: float = Field(..., description="Success rate percentage")
    conversion_rate: float = Field(..., description="Conversion rate percentage")
    revenue_generated: float = Field(..., description="Revenue generated")
    cost_per_acquisition: float = Field(..., description="Cost per acquisition")
    roi: float = Field(..., description="Return on investment")
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

class CampaignAnalytics(BaseModel):
    """Campaign analytics data"""
    total_campaigns: int = Field(..., description="Total number of campaigns")
    active_campaigns: int = Field(..., description="Currently active campaigns")
    total_calls: int = Field(..., description="Total calls made")
    avg_success_rate: float = Field(..., description="Average success rate")
    total_revenue: float = Field(..., description="Total revenue generated")
    avg_roi: float = Field(..., description="Average ROI")
    top_performing: List[Dict[str, Any]] = Field(default_factory=list)

# Mock data
INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Real Estate", "E-commerce",
    "Education", "Manufacturing", "Retail", "Professional Services",
    "Automotive", "Energy", "Media", "Legal", "Insurance", "Hospitality"
]

AUDIENCES = [
    "Small Business Owners", "C-Level Executives", "IT Managers", 
    "Marketing Directors", "HR Professionals", "Startup Founders",
    "Real Estate Agents", "Healthcare Providers", "Financial Advisors"
]

def generate_campaign(campaign_id: str) -> SmartCampaign:
    """Generate a mock campaign"""
    # Handle campaign_id that might not have underscore
    parts = campaign_id.split('_')
    campaign_name = f"Campaign {parts[-1]}" if len(parts) > 1 else f"Campaign {campaign_id}"
    
    calls_made = random.randint(500, 5000)
    success_rate = round(random.uniform(15, 85), 1)
    conversion_rate = round(random.uniform(5, 25), 1)
    revenue = round(calls_made * random.uniform(2, 15), 2)
    cost = round(calls_made * random.uniform(0.5, 3), 2)
    roi = round((revenue - cost) / cost * 100, 1) if cost > 0 else 0
    
    return SmartCampaign(
        campaign_id=campaign_id,
        name=campaign_name,
        status=random.choice(["active", "paused", "completed", "draft"]),
        industry=random.choice(INDUSTRIES),
        ai_optimization_level=round(random.uniform(65, 98), 1),
        target_audience=random.choice(AUDIENCES),
        calls_made=calls_made,
        success_rate=success_rate,
        conversion_rate=conversion_rate,
        revenue_generated=revenue,
        cost_per_acquisition=round(cost / max(calls_made * conversion_rate / 100, 1), 2),
        roi=roi
    )

def generate_analytics() -> CampaignAnalytics:
    """Generate campaign analytics"""
    top_performing = [
        {"name": "Tech Startup Outreach", "roi": 245.6, "revenue": 18450},
        {"name": "Healthcare Follow-ups", "roi": 189.3, "revenue": 14230},
        {"name": "E-commerce Leads", "roi": 167.8, "revenue": 12680},
        {"name": "Financial Services", "roi": 156.4, "revenue": 11890},
        {"name": "Real Estate Prospecting", "roi": 143.2, "revenue": 10340}
    ]
    
    return CampaignAnalytics(
        total_campaigns=random.randint(35, 50),
        active_campaigns=random.randint(15, 25),
        total_calls=random.randint(25000, 45000),
        avg_success_rate=round(random.uniform(45, 75), 1),
        total_revenue=round(random.uniform(125000, 185000), 2),
        avg_roi=round(random.uniform(150, 220), 1),
        top_performing=top_performing
    )

# Initialize FastAPI app
app = FastAPI(
    title="Vocelio.ai Smart Campaigns Service",
    description="Campaign management and optimization service",
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
        "service": "smart-campaigns",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Get all campaigns endpoint
@app.get("/api/v1/campaigns", response_model=List[Dict[str, Any]])
async def get_all_campaigns(limit: int = 20, offset: int = 0):
    """Get all campaigns"""
    campaigns = [generate_campaign(f"campaign_{i+1+offset}") for i in range(min(limit, 20))]
    # Add id field for compatibility
    campaign_dicts = []
    for campaign in campaigns:
        campaign_dict = campaign.model_dump()
        campaign_dict['id'] = campaign.campaign_id
        campaign_dicts.append(campaign_dict)
    return campaign_dicts

# Get campaign analytics endpoint (must be before {campaign_id} route)
@app.get("/api/v1/campaigns/analytics", response_model=CampaignAnalytics)
async def get_campaign_analytics():
    """Get campaign analytics"""
    return generate_analytics()

# Get single campaign endpoint
@app.get("/api/v1/campaigns/{campaign_id}", response_model=SmartCampaign)
async def get_campaign(campaign_id: str):
    """Get a specific campaign"""
    return generate_campaign(campaign_id)

# Create campaign endpoint
@app.post("/api/v1/campaigns", response_model=Dict[str, Any])
async def create_campaign(campaign_data: Dict[str, Any]):
    """Create a new campaign"""
    campaign_id = f"campaign_{random.randint(1000, 9999)}"
    campaign = generate_campaign(campaign_id)
    campaign.name = campaign_data.get("name", campaign.name)
    campaign.industry = campaign_data.get("industry", campaign.industry)
    campaign.target_audience = campaign_data.get("target_audience", campaign.target_audience)
    # Return the campaign with an 'id' field for compatibility
    campaign_dict = campaign.model_dump()
    campaign_dict['id'] = campaign.campaign_id
    return campaign_dict

# Get campaign analytics endpoint
@app.get("/api/v1/campaigns/analytics", response_model=CampaignAnalytics)
async def get_campaign_analytics():
    """Get campaign analytics"""
    return generate_analytics()

# Update campaign endpoint
@app.put("/api/v1/campaigns/{campaign_id}", response_model=SmartCampaign)
async def update_campaign(campaign_id: str, campaign_data: Dict[str, Any]):
    """Update a campaign"""
    campaign = generate_campaign(campaign_id)
    if "name" in campaign_data:
        campaign.name = campaign_data["name"]
    if "status" in campaign_data:
        campaign.status = campaign_data["status"]
    if "industry" in campaign_data:
        campaign.industry = campaign_data["industry"]
    return campaign

# Optimize campaign endpoint
@app.post("/api/v1/campaigns/{campaign_id}/optimize")
async def optimize_campaign(campaign_id: str):
    """Optimize a campaign using AI"""
    campaign = generate_campaign(campaign_id)
    # Simulate optimization improvements
    campaign.ai_optimization_level = min(98.0, campaign.ai_optimization_level + random.uniform(5, 15))
    campaign.success_rate = min(95.0, campaign.success_rate + random.uniform(2, 8))
    campaign.conversion_rate = min(30.0, campaign.conversion_rate + random.uniform(1, 5))
    
    return {
        "status": "optimized",
        "campaign_id": campaign_id,
        "improvements": {
            "ai_optimization_level": f"+{random.uniform(5, 15):.1f}%",
            "success_rate": f"+{random.uniform(2, 8):.1f}%",
            "conversion_rate": f"+{random.uniform(1, 5):.1f}%"
        },
        "updated_campaign": campaign
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_test:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
