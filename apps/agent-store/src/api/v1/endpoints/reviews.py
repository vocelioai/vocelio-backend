from fastapi import APIRouter, HTTPException, Depends
import structlog

from shared.auth.dependencies import get_current_user

router = APIRouter()
logger = structlog.get_logger()

@router.get("/{agent_id}", summary="Get agent reviews")
async def get_agent_reviews(agent_id: str):
    """Get reviews for a specific agent."""
    return {
        "agent_id": agent_id,
        "reviews": [
            {
                "id": "review_001",
                "user_name": "John D.",
                "rating": 5,
                "title": "Excellent sales agent!",
                "comment": "This agent has increased our conversion rate by 40%. Highly recommended!",
                "created_at": "2024-01-20T10:00:00Z",
                "verified_purchase": True
            },
            {
                "id": "review_002", 
                "user_name": "Sarah M.",
                "rating": 4,
                "title": "Good but could be better",
                "comment": "Works well for most cases, but struggles with complex objections.",
                "created_at": "2024-01-18T15:30:00Z",
                "verified_purchase": True
            }
        ],
        "summary": {
            "average_rating": 4.8,
            "total_reviews": 47,
            "rating_distribution": {
                "5": 32,
                "4": 12,
                "3": 2,
                "2": 1,
                "1": 0
            }
        }
    }

@router.post("/{agent_id}", summary="Submit agent review")
async def submit_review(
    agent_id: str,
    current_user = Depends(get_current_user)
):
    """Submit a review for an agent."""
    return {
        "message": "Review submitted successfully",
        "review_id": "review_new_001",
        "status": "pending_moderation"
    }
