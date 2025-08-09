"""
Voice Lab - Voice Management Endpoints
Handles voice library, filtering, and management operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from services.voice_service import VoiceService
from schemas.voice import (
    VoiceResponse, 
    VoiceCreate, 
    VoiceUpdate,
    VoiceFilter,
    VoiceComparison
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

@router.get("/", response_model=List[VoiceResponse])
async def get_voices(
    language: Optional[str] = Query(None, description="Filter by language"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    category: Optional[str] = Query(None, description="Filter by category"),
    use_case: Optional[str] = Query(None, description="Filter by use case"),
    quality_min: Optional[int] = Query(None, description="Minimum quality score"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    limit: int = Query(50, description="Number of voices to return"),
    offset: int = Query(0, description="Pagination offset"),
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get filtered list of available voices"""
    filter_params = VoiceFilter(
        language=language,
        gender=gender,
        category=category,
        use_case=use_case,
        quality_min=quality_min,
        search=search,
        limit=limit,
        offset=offset
    )
    
    voices = await voice_service.get_voices(filter_params, current_user.id)
    return voices

@router.get("/{voice_id}", response_model=VoiceResponse)
async def get_voice(
    voice_id: str,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get specific voice details"""
    voice = await voice_service.get_voice(voice_id, current_user.id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice

@router.post("/", response_model=VoiceResponse)
async def create_voice(
    voice_data: VoiceCreate,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Create new custom voice"""
    voice = await voice_service.create_voice(voice_data, current_user.id)
    return voice

@router.put("/{voice_id}", response_model=VoiceResponse)
async def update_voice(
    voice_id: str,
    voice_data: VoiceUpdate,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Update voice settings"""
    voice = await voice_service.update_voice(voice_id, voice_data, current_user.id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice

@router.delete("/{voice_id}")
async def delete_voice(
    voice_id: str,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Delete custom voice"""
    success = await voice_service.delete_voice(voice_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")
    return {"message": "Voice deleted successfully"}

@router.post("/compare", response_model=VoiceComparison)
async def compare_voices(
    voice_ids: List[str],
    sample_text: str = "Hello, this is a comparison test to help you choose the best voice for your campaigns.",
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Compare multiple voices with sample text"""
    if len(voice_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 voices required for comparison")
    
    comparison = await voice_service.compare_voices(voice_ids, sample_text, current_user.id)
    return comparison

@router.get("/{voice_id}/preview")
async def get_voice_preview(
    voice_id: str,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get voice preview audio file"""
    file_path = await voice_service.get_voice_preview(voice_id, current_user.id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Preview not available")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=f"voice_{voice_id}_preview.mp3"
    )

@router.post("/{voice_id}/settings")
async def update_voice_settings(
    voice_id: str,
    stability: float = 0.7,
    similarity_boost: float = 0.8,
    style: float = 0.2,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Update voice generation settings"""
    settings_data = {
        "stability": stability,
        "similarity_boost": similarity_boost,
        "style": style
    }
    
    voice = await voice_service.update_voice_settings(voice_id, settings_data, current_user.id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {"message": "Voice settings updated successfully", "settings": settings_data}
