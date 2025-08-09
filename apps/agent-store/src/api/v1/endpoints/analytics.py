from fastapi import APIRouter, Depends
import structlog

from shared.auth.dependencies import get_current_user

router = APIRouter()
logger = structlog.get_logger()

@router.get("/sales", summary="Get sales analytics")
async def get_sales_analytics(current_user = Depends(get_current_user)):
    """Get marketplace sales analytics."""
    return {
        "total_sales": 15420,
        "revenue": 524800.00,
        "top_selling_agents": [
            {"id": "agent_002", "name": "Customer Support Specialist", "sales": 2341},
            {"id": "agent_001", "name": "Sales Assistant Pro", "sales": 1523},
            {"id": "agent_003", "name": "Healthcare Scheduler", "sales": 856}
        ],
        "sales_by_category": {
            "sales": 145600.00,
            "support": 98200.00,
            "healthcare": 76400.00,
            "general": 204600.00
        },
        "monthly_trends": [
            {"month": "2024-01", "sales": 1250, "revenue": 42300.00},
            {"month": "2023-12", "sales": 1180, "revenue": 38900.00},
            {"month": "2023-11", "sales": 1090, "revenue": 35200.00}
        ]
    }

@router.get("/creators", summary="Get creator analytics")
async def get_creator_analytics(current_user = Depends(get_current_user)):
    """Get creator performance analytics."""
    return {
        "total_creators": 156,
        "active_creators": 134,
        "top_creators": [
            {"id": "user_456", "name": "Support Solutions Inc", "total_sales": 2341, "revenue": 45820.00},
            {"id": "user_123", "name": "VoiceAI Labs", "total_sales": 1523, "revenue": 38075.00},
            {"id": "user_789", "name": "MedTech AI", "total_sales": 856, "revenue": 35644.00}
        ],
        "creator_metrics": {
            "average_agents_per_creator": 1.6,
            "average_monthly_revenue": 2850.00,
            "new_creators_this_month": 8
        }
    }
