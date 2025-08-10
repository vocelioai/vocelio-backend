"""
🏪 Agent Store Dashboard Integration Endpoints
Enhanced endpoints specifically designed for dashboard integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging

# Mock user dependency for now
def get_current_user():
    return {
        "user_id": "user_123",
        "name": "Dashboard User",
        "email": "user@vocelio.ai",
        "plan": "Pro"
    }

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced mock data for dashboard integration
DASHBOARD_AGENTS = [
    {
        "id": "agt_sales_pro_v2",
        "name": "Sales Pro AI Agent v2.0",
        "description": "Advanced sales assistant with lead qualification and objection handling",
        "category": "sales",
        "price": 79.99,
        "rating": 4.8,
        "downloads": 2845,
        "creator": {
            "id": "creator_vocelio",
            "name": "Vocelio AI Labs",
            "verified": True,
            "badge": "Official"
        },
        "capabilities": [
            "Lead Qualification",
            "Objection Handling", 
            "Product Demos",
            "CRM Integration",
            "Follow-up Automation"
        ],
        "languages": ["en", "es", "fr"],
        "industry_focus": ["SaaS", "Real Estate", "Insurance"],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:45:00Z",
        "featured": True,
        "verified": True,
        "performance_metrics": {
            "avg_conversion_rate": 24.5,
            "avg_call_duration": "8m 30s",
            "customer_satisfaction": 4.7,
            "success_rate": 89.2
        },
        "pricing": {
            "price": 79.99,
            "billing_cycle": "monthly",
            "trial_days": 14,
            "enterprise_pricing": True,
            "volume_discounts": True
        },
        "technical_specs": {
            "api_version": "v2.0",
            "response_time": "< 200ms",
            "concurrent_calls": 100,
            "integrations": ["Salesforce", "HubSpot", "Pipedrive"],
            "deployment": "cloud"
        }
    },
    {
        "id": "agt_support_specialist",
        "name": "Customer Support Specialist",
        "description": "24/7 customer support agent with multi-language capabilities",
        "category": "support",
        "price": 49.99,
        "rating": 4.9,
        "downloads": 3567,
        "creator": {
            "id": "creator_supportai",
            "name": "SupportAI Inc",
            "verified": True,
            "badge": "Verified"
        },
        "capabilities": [
            "Issue Resolution",
            "Ticket Management",
            "Escalation Handling",
            "Knowledge Base Search",
            "Multi-language Support"
        ],
        "languages": ["en", "es", "fr", "de", "pt"],
        "industry_focus": ["E-commerce", "SaaS", "Telecommunications"],
        "created_at": "2024-01-10T08:15:00Z",
        "updated_at": "2024-01-18T16:20:00Z",
        "featured": True,
        "verified": True,
        "performance_metrics": {
            "avg_resolution_time": "4m 15s",
            "first_call_resolution": 78.3,
            "customer_satisfaction": 4.9,
            "escalation_rate": 8.7
        },
        "pricing": {
            "price": 49.99,
            "billing_cycle": "monthly",
            "trial_days": 7,
            "enterprise_pricing": False,
            "volume_discounts": True
        },
        "technical_specs": {
            "api_version": "v1.8",
            "response_time": "< 150ms",
            "concurrent_calls": 250,
            "integrations": ["Zendesk", "Freshdesk", "Intercom"],
            "deployment": "cloud"
        }
    },
    {
        "id": "agt_healthcare_scheduler",
        "name": "Healthcare Appointment Scheduler",
        "description": "HIPAA-compliant medical appointment scheduling and patient screening",
        "category": "healthcare",
        "price": 129.99,
        "rating": 4.7,
        "downloads": 1234,
        "creator": {
            "id": "creator_medhealthai",
            "name": "MedHealth AI",
            "verified": True,
            "badge": "Healthcare Certified"
        },
        "capabilities": [
            "Appointment Scheduling",
            "Patient Screening",
            "Insurance Verification",
            "Prescription Reminders",
            "HIPAA Compliance"
        ],
        "languages": ["en", "es"],
        "industry_focus": ["Healthcare", "Medical Practices", "Telehealth"],
        "created_at": "2024-01-05T12:00:00Z",
        "updated_at": "2024-01-19T11:30:00Z",
        "featured": False,
        "verified": True,
        "performance_metrics": {
            "appointment_booking_rate": 67.8,
            "no_show_reduction": 23.5,
            "patient_satisfaction": 4.6,
            "compliance_score": 99.8
        },
        "pricing": {
            "price": 129.99,
            "billing_cycle": "monthly",
            "trial_days": 14,
            "enterprise_pricing": True,
            "volume_discounts": True
        },
        "technical_specs": {
            "api_version": "v1.5",
            "response_time": "< 300ms",
            "concurrent_calls": 50,
            "integrations": ["Epic", "Cerner", "AllScripts"],
            "deployment": "private_cloud"
        }
    }
]

@router.get("/dashboard/featured", summary="Featured Agents for Dashboard")
async def get_featured_agents_for_dashboard(
    limit: int = Query(6, ge=1, le=20),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get featured agents optimized for dashboard display."""
    try:
        featured_agents = [agent for agent in DASHBOARD_AGENTS if agent["featured"]][:limit]
        
        # Add dashboard-specific metadata
        for agent in featured_agents:
            agent["dashboard_display"] = {
                "featured_since": "2024-01-15",
                "trending": agent["downloads"] > 2000,
                "hot": agent["rating"] >= 4.8,
                "new": (datetime.now() - datetime.fromisoformat(agent["created_at"].replace('Z', ''))).days < 30,
                "quick_setup": agent["technical_specs"]["deployment"] == "cloud",
                "integration_ready": len(agent["technical_specs"]["integrations"]) > 0
            }
        
        return {
            "featured_agents": featured_agents,
            "metadata": {
                "total_featured": len(featured_agents),
                "last_updated": datetime.now().isoformat(),
                "refresh_interval": "1h"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting featured agents for dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get featured agents")

@router.get("/dashboard/categories", summary="Agent Categories for Dashboard")
async def get_agent_categories_for_dashboard():
    """Get agent categories with counts and metadata for dashboard."""
    try:
        categories = {
            "sales": {
                "name": "Sales & Marketing",
                "description": "AI agents for sales, lead generation, and marketing automation",
                "icon": "trending-up",
                "color": "#10B981",
                "agent_count": 45,
                "featured_count": 8,
                "avg_rating": 4.6,
                "most_popular": "Sales Pro AI Agent v2.0",
                "use_cases": ["Lead Qualification", "Cold Calling", "Demo Scheduling", "Follow-ups"]
            },
            "support": {
                "name": "Customer Support",
                "description": "24/7 customer service and support automation agents",
                "icon": "headphones",
                "color": "#3B82F6",
                "agent_count": 32,
                "featured_count": 5,
                "avg_rating": 4.8,
                "most_popular": "Customer Support Specialist",
                "use_cases": ["Issue Resolution", "Ticket Management", "FAQ Handling", "Escalation"]
            },
            "healthcare": {
                "name": "Healthcare & Medical",
                "description": "HIPAA-compliant agents for healthcare and medical practices",
                "icon": "heart",
                "color": "#EF4444",
                "agent_count": 18,
                "featured_count": 3,
                "avg_rating": 4.7,
                "most_popular": "Healthcare Appointment Scheduler",
                "use_cases": ["Appointment Booking", "Patient Screening", "Prescription Reminders"]
            },
            "education": {
                "name": "Education & Training",
                "description": "Educational institutions and training program agents",
                "icon": "graduation-cap",
                "color": "#8B5CF6",
                "agent_count": 23,
                "featured_count": 4,
                "avg_rating": 4.5,
                "most_popular": "Student Enrollment Assistant",
                "use_cases": ["Student Enrollment", "Course Information", "Tutoring Support"]
            },
            "finance": {
                "name": "Finance & Banking",
                "description": "Financial services and banking automation agents",
                "icon": "dollar-sign",
                "color": "#F59E0B",
                "agent_count": 15,
                "featured_count": 2,
                "avg_rating": 4.4,
                "most_popular": "Loan Processing Assistant",
                "use_cases": ["Loan Applications", "Account Inquiries", "Payment Processing"]
            },
            "retail": {
                "name": "Retail & E-commerce",
                "description": "Online shopping and retail customer service agents",
                "icon": "shopping-cart",
                "color": "#EC4899",
                "agent_count": 28,
                "featured_count": 6,
                "avg_rating": 4.6,
                "most_popular": "E-commerce Shopping Assistant",
                "use_cases": ["Product Recommendations", "Order Support", "Returns Processing"]
            }
        }
        
        return {
            "categories": categories,
            "summary": {
                "total_categories": len(categories),
                "total_agents": sum(cat["agent_count"] for cat in categories.values()),
                "total_featured": sum(cat["featured_count"] for cat in categories.values()),
                "overall_avg_rating": round(sum(cat["avg_rating"] for cat in categories.values()) / len(categories), 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent categories for dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agent categories")

@router.get("/dashboard/analytics", summary="Agent Store Analytics for Dashboard")
async def get_agent_store_analytics(
    timeRange: str = Query("7d", description="Time range: 1d, 7d, 30d"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get agent store analytics data for dashboard charts."""
    try:
        # Mock analytics data for dashboard
        analytics = {
            "overview": {
                "total_agents": 161,
                "active_agents": 145,
                "total_downloads": 15748,
                "total_revenue": 23567.89,
                "avg_rating": 4.6,
                "featured_agents": 28,
                "verified_creators": 45,
                "new_agents_this_month": 8
            },
            "performance": {
                "top_performing_agents": [
                    {
                        "id": "agt_support_specialist",
                        "name": "Customer Support Specialist",
                        "downloads": 3567,
                        "revenue": 8934.33,
                        "rating": 4.9,
                        "growth_rate": 23.5
                    },
                    {
                        "id": "agt_sales_pro_v2",
                        "name": "Sales Pro AI Agent v2.0",
                        "downloads": 2845,
                        "revenue": 11378.55,
                        "rating": 4.8,
                        "growth_rate": 18.7
                    }
                ],
                "trending_categories": [
                    {"category": "sales", "growth": 34.2, "downloads": 5890},
                    {"category": "support", "growth": 28.9, "downloads": 4567},
                    {"category": "healthcare", "growth": 19.5, "downloads": 2134}
                ]
            },
            "user_engagement": {
                "daily_active_users": 1234,
                "avg_session_duration": "12m 34s",
                "bounce_rate": 23.5,
                "conversion_rate": 8.7,
                "repeat_purchase_rate": 34.2
            },
            "revenue_metrics": {
                "total_revenue": 23567.89,
                "monthly_growth": 15.3,
                "avg_agent_price": 67.45,
                "commission_earned": 4713.58,
                "projected_monthly": 31245.67
            },
            "download_trends": {
                "daily_breakdown": [
                    {"date": "2024-01-01", "downloads": 234, "revenue": 1567.89},
                    {"date": "2024-01-02", "downloads": 298, "revenue": 1890.45},
                    {"date": "2024-01-03", "downloads": 187, "revenue": 1234.67},
                    {"date": "2024-01-04", "downloads": 312, "revenue": 2134.78},
                    {"date": "2024-01-05", "downloads": 267, "revenue": 1789.23},
                    {"date": "2024-01-06", "downloads": 198, "revenue": 1456.89},
                    {"date": "2024-01-07", "downloads": 245, "revenue": 1678.90}
                ]
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting agent store analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/dashboard/my-agents", summary="User's Purchased Agents")
async def get_user_agents_for_dashboard(
    status: Optional[str] = Query(None, description="Filter by status: active, inactive, trial"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's purchased agents for dashboard management."""
    try:
        # Mock user's purchased agents
        user_agents = [
            {
                "purchase_id": "purch_001",
                "agent": {
                    "id": "agt_sales_pro_v2",
                    "name": "Sales Pro AI Agent v2.0",
                    "category": "sales",
                    "version": "2.0.1"
                },
                "status": "active",
                "purchased_at": "2024-01-10T09:30:00Z",
                "expires_at": "2024-02-10T09:30:00Z",
                "usage_stats": {
                    "total_calls": 567,
                    "successful_calls": 489,
                    "avg_call_duration": "7m 45s",
                    "conversion_rate": 22.1
                },
                "billing": {
                    "amount_paid": 79.99,
                    "next_billing": "2024-02-10T09:30:00Z",
                    "auto_renew": True
                },
                "deployment": {
                    "status": "deployed",
                    "endpoint": "https://api.vocelio.ai/agents/agt_sales_pro_v2",
                    "api_key": "voc_agt_***********",
                    "last_active": "2024-01-20T14:30:00Z"
                }
            },
            {
                "purchase_id": "purch_002",
                "agent": {
                    "id": "agt_support_specialist",
                    "name": "Customer Support Specialist",
                    "category": "support",
                    "version": "1.8.3"
                },
                "status": "trial",
                "purchased_at": "2024-01-18T16:45:00Z",
                "expires_at": "2024-01-25T16:45:00Z",
                "usage_stats": {
                    "total_calls": 89,
                    "successful_calls": 84,
                    "avg_call_duration": "5m 12s",
                    "customer_satisfaction": 4.8
                },
                "billing": {
                    "amount_paid": 0,
                    "trial_ends": "2024-01-25T16:45:00Z",
                    "auto_convert": True
                },
                "deployment": {
                    "status": "deployed",
                    "endpoint": "https://api.vocelio.ai/agents/agt_support_specialist",
                    "api_key": "voc_agt_***********",
                    "last_active": "2024-01-20T11:15:00Z"
                }
            }
        ]
        
        # Filter by status if provided
        if status:
            user_agents = [agent for agent in user_agents if agent["status"] == status]
        
        return {
            "user_agents": user_agents,
            "summary": {
                "total_agents": len(user_agents),
                "active_agents": len([a for a in user_agents if a["status"] == "active"]),
                "trial_agents": len([a for a in user_agents if a["status"] == "trial"]),
                "total_spent": sum(a["billing"]["amount_paid"] for a in user_agents),
                "monthly_cost": sum(a["billing"]["amount_paid"] for a in user_agents if a["status"] == "active")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user agents for dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user agents")

@router.post("/dashboard/agents/{agent_id}/deploy", summary="Deploy Agent from Dashboard")
async def deploy_agent_from_dashboard(
    agent_id: str,
    deployment_config: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deploy a purchased agent with configuration from dashboard."""
    try:
        # Mock deployment process
        deployment = {
            "deployment_id": f"deploy_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "agent_id": agent_id,
            "status": "deploying",
            "progress": 0,
            "estimated_completion": (datetime.now() + timedelta(minutes=3)).isoformat(),
            "deployment_url": f"https://api.vocelio.ai/agents/{agent_id}",
            "api_key": f"voc_agt_{agent_id}_{''.join(['x' for _ in range(20)])}",
            "configuration": deployment_config or {
                "region": "us-east-1",
                "scaling": "auto",
                "max_concurrent": 100,
                "timeout": 30
            }
        }
        
        return deployment
        
    except Exception as e:
        logger.error(f"Error deploying agent from dashboard - agent_id: {agent_id}, error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to deploy agent")

@router.get("/dashboard/marketplace/trending", summary="Trending Agents")
async def get_trending_agents_for_dashboard(
    limit: int = Query(10, ge=1, le=20)
):
    """Get trending agents for dashboard marketplace section."""
    try:
        trending_agents = [
            {
                "agent": DASHBOARD_AGENTS[0],
                "trending_metrics": {
                    "download_growth": 45.6,
                    "rating_trend": "up",
                    "revenue_growth": 67.8,
                    "social_mentions": 234,
                    "trend_duration": "7 days"
                }
            },
            {
                "agent": DASHBOARD_AGENTS[1], 
                "trending_metrics": {
                    "download_growth": 38.2,
                    "rating_trend": "up",
                    "revenue_growth": 52.1,
                    "social_mentions": 189,
                    "trend_duration": "5 days"
                }
            }
        ][:limit]
        
        return {
            "trending_agents": trending_agents,
            "trend_factors": [
                "High download velocity",
                "Positive rating momentum", 
                "Strong revenue growth",
                "Social media buzz",
                "Industry adoption"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting trending agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trending agents")
