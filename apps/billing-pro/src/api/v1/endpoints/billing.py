# apps/billing-pro/src/api/v1/endpoints/billing.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/usage/{organization_id}")
async def get_usage_metrics(
    organization_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get detailed usage metrics for billing"""
    
    # Calculate date range
    if not end_date:
        end_date = datetime.utcnow()
    else:
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    if not start_date:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    
    # Mock usage data - replace with actual database queries
    usage_data = {
        "organization_id": organization_id,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "metrics": {
            "total_calls": 15420,
            "total_minutes": 38550.5,
            "ai_generations": 22840,
            "voice_generations": 8960,
            "sms_sent": 5670,
            "storage_gb": 125.8,
            "api_requests": 156780
        },
        "costs": {
            "calls": 462.60,
            "ai_processing": 228.40,
            "voice_synthesis": 179.20,
            "messaging": 56.70,
            "storage": 25.16,
            "api": 31.36,
            "total": 983.42
        },
        "breakdown_by_service": {
            "overview-service": {"requests": 12560, "cost": 12.56},
            "ai-agents-service": {"requests": 45680, "cost": 228.40},
            "smart-campaigns-service": {"requests": 34780, "cost": 173.90},
            "call-center-service": {"requests": 25890, "cost": 462.60},
            "voice-lab-service": {"requests": 17890, "cost": 179.20}
        }
    }
    
    return usage_data

@router.get("/plans")
async def get_billing_plans():
    """Get available billing plans"""
    
    plans = {
        "plans": [
            {
                "id": "free",
                "name": "Free Tier",
                "price": 0,
                "currency": "USD",
                "billing_period": "monthly",
                "features": {
                    "max_calls": 100,
                    "max_agents": 2,
                    "max_voice_generations": 1000,
                    "support": "Community",
                    "ai_models": ["gpt-3.5-turbo"],
                    "voice_cloning": False
                },
                "limits": {
                    "calls_per_month": 100,
                    "minutes_per_month": 500,
                    "storage_gb": 1,
                    "api_requests_per_day": 1000
                }
            },
            {
                "id": "starter",
                "name": "Starter",
                "price": 49,
                "currency": "USD",
                "billing_period": "monthly",
                "features": {
                    "max_calls": 1000,
                    "max_agents": 10,
                    "max_voice_generations": 10000,
                    "support": "Email",
                    "ai_models": ["gpt-3.5-turbo", "gpt-4"],
                    "voice_cloning": True
                },
                "limits": {
                    "calls_per_month": 1000,
                    "minutes_per_month": 5000,
                    "storage_gb": 10,
                    "api_requests_per_day": 10000
                }
            },
            {
                "id": "professional", 
                "name": "Professional",
                "price": 199,
                "currency": "USD",
                "billing_period": "monthly",
                "features": {
                    "max_calls": 10000,
                    "max_agents": 50,
                    "max_voice_generations": 100000,
                    "support": "Priority",
                    "ai_models": ["gpt-3.5-turbo", "gpt-4", "claude-3"],
                    "voice_cloning": True,
                    "custom_models": True
                },
                "limits": {
                    "calls_per_month": 10000,
                    "minutes_per_month": 50000,
                    "storage_gb": 100,
                    "api_requests_per_day": 100000
                }
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": "custom",
                "currency": "USD",
                "billing_period": "annual",
                "features": {
                    "max_calls": "unlimited",
                    "max_agents": "unlimited",
                    "max_voice_generations": "unlimited",
                    "support": "Dedicated",
                    "ai_models": "all",
                    "voice_cloning": True,
                    "custom_models": True,
                    "white_label": True,
                    "sla": "99.9%"
                },
                "limits": {
                    "calls_per_month": -1,
                    "minutes_per_month": -1,
                    "storage_gb": -1,
                    "api_requests_per_day": -1
                }
            }
        ]
    }
    
    return plans

@router.post("/calculate")
async def calculate_billing(
    organization_id: str,
    usage: Dict[str, Any]
):
    """Calculate billing amount based on usage"""
    
    # Pricing tiers (per unit)
    pricing = {
        "calls": 0.03,  # per call
        "minutes": 0.01,  # per minute
        "ai_requests": 0.005,  # per request
        "voice_generations": 0.02,  # per generation
        "sms": 0.01,  # per SMS
        "storage": 0.20,  # per GB per month
        "api_requests": 0.0002  # per API request
    }
    
    total_cost = 0
    breakdown = {}
    
    for service, amount in usage.items():
        if service in pricing:
            cost = amount * pricing[service]
            breakdown[service] = {
                "amount": amount,
                "rate": pricing[service],
                "cost": round(cost, 2)
            }
            total_cost += cost
    
    return {
        "organization_id": organization_id,
        "calculation": {
            "breakdown": breakdown,
            "subtotal": round(total_cost, 2),
            "tax": round(total_cost * 0.08, 2),  # 8% tax
            "total": round(total_cost * 1.08, 2)
        },
        "currency": "USD",
        "calculated_at": datetime.utcnow().isoformat()
    }

@router.get("/current/{organization_id}")
async def get_current_billing_period(organization_id: str):
    """Get current billing period information"""
    
    now = datetime.utcnow()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate next month
    if period_start.month == 12:
        period_end = period_start.replace(year=period_start.year + 1, month=1)
    else:
        period_end = period_start.replace(month=period_start.month + 1)
    
    return {
        "organization_id": organization_id,
        "current_period": {
            "start": period_start.isoformat(),
            "end": period_end.isoformat(),
            "days_remaining": (period_end - now).days
        },
        "plan": {
            "id": "professional",
            "name": "Professional",
            "price": 199,
            "currency": "USD"
        },
        "usage_summary": {
            "calls_used": 6780,
            "calls_limit": 10000,
            "minutes_used": 16950,
            "minutes_limit": 50000,
            "agents_used": 23,
            "agents_limit": 50
        },
        "estimated_cost": 847.50,
        "status": "active"
    }
