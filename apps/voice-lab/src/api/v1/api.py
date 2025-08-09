"""
Voice Lab API Router
Combines all voice lab endpoints
"""

from fastapi import APIRouter
from api.v1.endpoints import voices, generation, cloning, testing, analytics

api_router = APIRouter()

# Include all voice lab endpoints
api_router.include_router(
    voices.router, 
    prefix="/voices", 
    tags=["Voice Management"]
)

api_router.include_router(
    generation.router, 
    prefix="/generation", 
    tags=["Speech Generation"]
)

api_router.include_router(
    cloning.router, 
    prefix="/cloning", 
    tags=["Voice Cloning"]
)

api_router.include_router(
    testing.router, 
    prefix="/testing", 
    tags=["Voice Testing"]
)

api_router.include_router(
    analytics.router, 
    prefix="/analytics", 
    tags=["Voice Analytics"]
)
