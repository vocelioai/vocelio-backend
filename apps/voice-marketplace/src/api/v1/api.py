# apps/voice-marketplace/src/api/v1/api.py
"""
Voice Marketplace API Router
"""

from fastapi import APIRouter
from .endpoints import marketplace, purchase, reviews, categories

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
api_router.include_router(purchase.router, prefix="/purchases", tags=["purchases"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])


# apps/voice-marketplace/src/api/v1/endpoints/marketplace.py
"""
Marketplace Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from shared.database.client import get_database
from shared.auth.dependencies import get_current_user
from schemas.marketplace import (
    VoiceListingResponse, VoiceFilterRequest, VoiceComparisonRequest,
    VoiceComparisonResponse, MarketplaceStatsResponse, VoiceTiersResponse
)
from services.marketplace_service import MarketplaceService
from core.config import settings

router = APIRouter()


@router.get("/voices", response_model=List[VoiceListingResponse])
async def get_voices(
    tier: Optional[str] = Query(None, description="Filter by voice tier"),
    language: Optional[str] = Query("all", description="Filter by language"),
    gender: Optional[str] = Query("all", description="Filter by gender"),
    style: Optional[str] = Query(None, description="Filter by style"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per minute"),
    search_query: Optional[str] = Query(None, max_length=200, description="Search term"),
    is_featured: Optional[bool] = Query(None, description="Filter featured voices"),
    is_new: Optional[bool] = Query(None, description="Filter new voices"),
    is_popular: Optional[bool] = Query(None, description="Filter popular voices"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_database)
):
    """
    🎭 Get filtered voice listings
    
    Retrieve voices with filtering, sorting, and pagination.
    Supports filtering by tier, language, gender, style, rating, and price.
    """
    try:
        marketplace_service = MarketplaceService(db)
        
        # Create filter request
        filters = VoiceFilterRequest(
            tier=tier,
            language=language,
            gender=gender,
            style=style,
            min_rating=min_rating,
            max_price=max_price,
            search_query=search_query,
            is_featured=is_featured,
            is_new=is_new,
            is_popular=is_popular,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        voices, total = await marketplace_service.get_voices(filters)
        
        return {
            "voices": voices,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving voices: {str(e)}")


@router.get("/voices/{voice_id}", response_model=VoiceListingResponse)
async def get_voice_by_id(
    voice_id: str,
    db: Session = Depends(get_database)
):
    """
    🎙️ Get voice by ID
    
    Retrieve detailed information about a specific voice.
    """
    try:
        marketplace_service = MarketplaceService(db)
        voice = await marketplace_service.get_voice_by_id(voice_id)
        
        if not voice:
            raise HTTPException(status_code=404, detail="Voice not found")
        
        return voice
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving voice: {str(e)}")


@router.post("/voices/compare", response_model=VoiceComparisonResponse)
async def compare_voices(
    request: VoiceComparisonRequest,
    db: Session = Depends(get_database)
):
    """
    🔍 Compare multiple voices
    
    Compare 2-4 voices side by side with detailed metrics and recommendations.
    """
    try:
        marketplace_service = MarketplaceService(db)
        comparison = await marketplace_service.get_voice_comparison(request.voice_ids)
        
        return VoiceComparisonResponse(**comparison)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing voices: {str(e)}")


@router.get("/tiers", response_model=VoiceTiersResponse)
async def get_voice_tiers(
    db: Session = Depends(get_database)
):
    """
    🎯 Get voice tier information
    
    Retrieve information about all voice tiers including pricing, features, and voice counts.
    """
    try:
        marketplace_service = MarketplaceService(db)
        tiers = await marketplace_service.get_voice_tiers()
        
        return VoiceTiersResponse(**tiers)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tiers: {str(e)}")


@router.get("/stats", response_model=MarketplaceStatsResponse)
async def get_marketplace_stats(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """
    📊 Get marketplace statistics
    
    Retrieve comprehensive marketplace statistics including sales, popular voices, and trends.
    Requires authentication.
    """
    try:
        marketplace_service = MarketplaceService(db)
        stats = await marketplace_service.get_marketplace_stats()
        
        return MarketplaceStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.get("/featured")
async def get_featured_voices(
    limit: int = Query(6, ge=1, le=20, description="Number of featured voices"),
    db: Session = Depends(get_database)
):
    """
    ⭐ Get featured voices
    
    Retrieve featured voices for homepage and promotional displays.
    """
    try:
        marketplace_service = MarketplaceService(db)
        
        filters = VoiceFilterRequest(
            is_featured=True,
            page=1,
            page_size=limit,
            sort_by="average_rating",
            sort_order="desc"
        )
        
        voices, total = await marketplace_service.get_voices(filters)
        
        return {
            "featured_voices": voices,
            "total": total
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving featured voices: {str(e)}")


@router