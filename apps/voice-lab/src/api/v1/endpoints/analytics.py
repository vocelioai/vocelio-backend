# api/v1/endpoints/__init__.py
from .voices import router as voices_router
from .generation import router as generation_router
from .cloning import router as cloning_router
from .testing import router as testing_router
from .analytics import router as analytics_router

__all__ = [
    "voices_router",
    "generation_router", 
    "cloning_router",
    "testing_router",
    "analytics_router"
]

# api/v1/endpoints/voices.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os

from ...dependencies import get_db, get_current_user
from ...services.voice_service import VoiceService
from ...schemas.voice import (
    Voice, VoiceCreate, VoiceUpdate, VoiceListResponse, 
    VoiceFilter, VoiceSettings, VoiceSettingsUpdate
)
from ...schemas.generation import GenerationRequestCreate, GenerationResponse
from ...core.config import settings

router = APIRouter(prefix="/voices", tags=["voices"])

@router.get("/", response_model=VoiceListResponse)
async def get_voices(
    skip: int = Query(0, ge=0, description="Number of voices to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of voices to return"),
    language: Optional[str] = Query(None, description="Filter by language code"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    category: Optional[str] = Query(None, description="Filter by category"),
    use_case: Optional[str] = Query(None, description="Filter by use case"),
    min_quality_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum quality score"),
    available_for_tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get paginated list of voices with filtering options"""
    
    voice_service = VoiceService(db)
    
    filters = VoiceFilter(
        language=language,
        gender=gender,
        category=category,
        use_case=use_case,
        min_quality_score=min_quality_score,
        available_for_tier=available_for_tier,
        search=search,
        is_active=is_active
    )
    
    result = await voice_service.get_voices(skip=skip, limit=limit, filters=filters)
    return result

@router.get("/{voice_id}", response_model=Voice)
async def get_voice(
    voice_id: str = Path(..., description="Voice ID"),
    db: Session = Depends(get_db)
):
    """Get a specific voice by ID"""
    
    voice_service = VoiceService(db)
    voice = await voice_service.get_voice_by_id(voice_id)
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return voice

@router.post("/", response_model=Voice, status_code=201)
async def create_voice(
    voice_data: VoiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new voice (Admin only)"""
    
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    voice_service = VoiceService(db)
    voice = await voice_service.create_voice(voice_data)
    
    return voice

@router.put("/{voice_id}", response_model=Voice)
async def update_voice(
    voice_id: str = Path(..., description="Voice ID"),
    voice_data: VoiceUpdate = ...,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing voice (Admin only)"""
    
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    voice_service = VoiceService(db)
    voice = await voice_service.update_voice(voice_id, voice_data)
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return voice

@router.delete("/{voice_id}")
async def delete_voice(
    voice_id: str = Path(..., description="Voice ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a voice (Admin only)"""
    
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    voice_service = VoiceService(db)
    success = await voice_service.delete_voice(voice_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {"message": "Voice deleted successfully"}

@router.get("/{voice_id}/settings", response_model=VoiceSettings)
async def get_voice_settings(
    voice_id: str = Path(..., description="Voice ID"),
    db: Session = Depends(get_db)
):
    """Get voice settings"""
    
    voice_service = VoiceService(db)
    voice = await voice_service.get_voice_by_id(voice_id)
    
    if not voice or not voice.settings:
        raise HTTPException(status_code=404, detail="Voice or settings not found")
    
    return voice.settings

@router.put("/{voice_id}/settings", response_model=VoiceSettings)
async def update_voice_settings(
    voice_id: str = Path(..., description="Voice ID"),
    settings_data: VoiceSettingsUpdate = ...,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update voice settings"""
    
    voice_service = VoiceService(db)
    
    # Get existing settings
    voice = await voice_service.get_voice_by_id(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    settings = voice.settings
    if not settings:
        raise HTTPException(status_code=404, detail="Voice settings not found")
    
    # Update only provided fields
    for field, value in settings_data.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings

@router.post("/{voice_id}/preview")
async def generate_voice_preview(
    voice_id: str = Path(..., description="Voice ID"),
    text: str = Query("Hello, this is a preview of this voice.", max_length=200),
    db: Session = Depends(get_db)
):
    """Generate a quick preview of the voice"""
    
    voice_service = VoiceService(db)
    
    preview_request = GenerationRequestCreate(
        voice_id=voice_id,
        text=text,
        settings={"preview": True}
    )
    
    try:
        result = await voice_service.generate_speech(preview_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{voice_id}/upload-preview")
async def upload_voice_preview(
    voice_id: str = Path(..., description="Voice ID"),
    file: UploadFile = File(..., description="Audio preview file"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload a preview audio file for a voice (Admin only)"""
    
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate file type
    if not file.filename.lower().endswith(('.mp3', '.wav', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid file format. Supported: mp3, wav, m4a")
    
    # Save file
    preview_filename = f"{voice_id}_preview.mp3"
    preview_path = settings.PREVIEWS_DIR / preview_filename
    
    with open(preview_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update voice preview URL
    voice_service = VoiceService(db)
    voice = await voice_service.get_voice_by_id(voice_id)
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    voice.preview_url = f"/static/previews/{preview_filename}"
    db.commit()
    
    return {"message": "Preview uploaded successfully", "preview_url": voice.preview_url}

# api/v1/endpoints/generation.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ...dependencies import get_db, get_current_user, rate_limit
from ...services.voice_service import VoiceService
from ...schemas.generation import (
    GenerationRequestCreate, GenerationResponse, BatchGenerationRequest, 
    BatchGenerationResponse, VoiceTestRequest, VoiceTestResult,
    VoiceComparisonRequest, VoiceComparisonResult
)

router = APIRouter(prefix="/generation", tags=["generation"])

@router.post("/generate", response_model=GenerationResponse)
async def generate_speech(
    request: GenerationRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(rate_limit)
):
    """Generate speech from text using specified voice"""
    
    voice_service = VoiceService(db)
    
    # Add user context to request
    request.user_id = current_user.get("user_id")
    
    try:
        result = await voice_service.generate_speech(request)
        
        # Add background task for analytics
        background_tasks.add_task(
            update_usage_analytics, 
            request.voice_id, 
            current_user.get("user_id")
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Generation failed")

@router.post("/batch", response_model=BatchGenerationResponse)
async def batch_generate_speech(
    request: BatchGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate speech for multiple texts using the same voice"""
    
    # Check user permissions for batch operations
    user_tier = current_user.get("subscription_tier", "free")
    if user_tier == "free":
        raise HTTPException(status_code=403, detail="Batch operations require paid subscription")
    
    voice_service = VoiceService(db)
    batch_id = str(uuid.uuid4())
    request_ids = []
    
    # Create individual generation requests
    for text in request.texts:
        gen_request = GenerationRequestCreate(
            voice_id=request.voice_id,
            text=text,
            settings=request.settings,
            user_id=request.user_id or current_user.get("user_id")
        )
        
        try:
            result = await voice_service.generate_speech(gen_request)
            request_ids.append(result["request_id"])
        except Exception as e:
            print(f"Failed to generate speech for text: {e}")
            continue
    
    # Estimate completion time (rough calculation)
    estimated_time = len(request_ids) * 2.0  # 2 seconds per generation
    
    return {
        "batch_id": batch_id,
        "request_ids": request_ids,
        "total_requests": len(request_ids),
        "estimated_completion_time": estimated_time
    }

@router.post("/test", response_model=VoiceTestResult)
async def test_voice_quality(
    request: VoiceTestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test voice quality with standard phrases"""
    
    voice_service = VoiceService(db)
    
    try:
        result = await voice_service.test_voice_quality(request)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Voice testing failed")

@router.post("/compare", response_model=VoiceComparisonResult)
async def compare_voices(
    request: VoiceComparisonRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Compare multiple voices using the same sample text"""
    
    # Check user permissions
    user_tier = current_user.get("subscription_tier", "free")
    if user_tier == "free" and len(request.voice_ids) > 2:
        raise HTTPException(status_code=403, detail="Free tier limited to 2 voice comparison")
    
    voice_service = VoiceService(db)
    
    try:
        result = await voice_service.compare_voices(
            voice_ids=request.voice_ids,
            sample_text=request.sample_text,
            settings=request.settings
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Voice comparison failed")

async def update_usage_analytics(voice_id: str, user_id: str):
    """Background task to update usage analytics"""
    # This would update analytics tables
    pass

# api/v1/endpoints/cloning.py
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import uuid
import os

from ...dependencies import get_db, get_current_user
from ...services.cloning_service import CloningService
from ...schemas.cloning import (
    CloneRequest, CloneRequestCreate, VoiceClone, CloneResponse,
    CloneListResponse, CloneResult
)
from ...core.config import settings

router = APIRouter(prefix="/cloning", tags=["cloning"])

@router.post("/upload", response_model=CloneResponse)
async def upload_voice_sample(
    name: str = Form(..., description="Clone name"),
    description: str = Form(None, description="Clone description"),
    file: UploadFile = File(..., description="Voice sample audio file"),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload voice sample for cloning"""
    
    # Check user permissions
    user_tier = current_user.get("subscription_tier", "free")
    if user_tier not in ["pro", "enterprise"]:
        raise HTTPException(status_code=403, detail="Voice cloning requires Pro or Enterprise subscription")
    
    # Validate file
    if not file.filename.lower().endswith(('.mp3', '.wav', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid file format. Supported: mp3, wav, m4a")
    
    if file.size > settings.MAX_VOICE_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {settings.MAX_VOICE_FILE_SIZE / 1024 / 1024}MB")
    
    cloning_service = CloningService(db)
    
    # Create clone request
    clone_request_data = CloneRequestCreate(
        name=name,
        description=description,
        user_id=current_user["user_id"]
    )
    
    try:
        result = await cloning_service.create_clone_request(clone_request_data, file)
        
        # Start cloning process in background
        background_tasks.add_task(
            cloning_service.process_voice_clone,
            result["clone_id"]
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clone upload failed: {str(e)}")

@router.get("/", response_model=CloneListResponse)
async def get_user_clones(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's voice clones"""
    
    cloning_service = CloningService(db)
    result = await cloning_service.get_user_clones(
        user_id=current_user["user_id"],
        skip=skip,
        limit=limit
    )
    
    return result

@router.get("/{clone_id}", response_model=VoiceClone)
async def get_clone(
    clone_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific voice clone"""
    
    cloning_service = CloningService(db)
    clone = await cloning_service.get_clone_by_id(clone_id)
    
    if not clone:
        raise HTTPException(status_code=404, detail="Clone not found")
    
    # Check ownership
    if clone.source_user_id != current_user["user_id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return clone

@router.delete("/{clone_id}")
async def delete_clone(
    clone_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a voice clone"""
    
    cloning_service = CloningService(db)
    clone = await cloning_service.get_clone_by_id(clone_id)
    
    if not clone:
        raise HTTPException(status_code=404, detail="Clone not found")
    
    # Check ownership
    if clone.source_user_id != current_user["user_id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await cloning_service.delete_clone(clone_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete clone")
    
    return {"message": "Clone deleted successfully"}

@router.get("/{clone_id}/result", response_model=CloneResult)
async def get_clone_result(
    clone_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get voice clone result"""
    
    cloning_service = CloningService(db)
    result = await cloning_service.get_clone_result(clone_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Clone result not found")
    
    # Check ownership
    clone = await cloning_service.get_clone_by_id(clone_id)
    if clone.source_user_id != current_user["user_id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return result

# api/v1/endpoints/testing.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ...dependencies import get_db, get_current_user
from ...services.testing_service import TestingService
from ...schemas.generation import VoiceTestRequest, VoiceTestResult, VoiceComparisonRequest

router = APIRouter(prefix="/testing", tags=["testing"])

@router.post("/voice/{voice_id}", response_model=VoiceTestResult)
async def test_single_voice(
    voice_id: str,
    test_phrases: Optional[List[str]] = None,
    settings: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test a single voice with custom or default phrases"""
    
    testing_service = TestingService(db)
    
    request = VoiceTestRequest(
        voice_id=voice_id,
        test_phrases=test_phrases,
        settings=settings
    )
    
    try:
        result = await testing_service.test_voice_comprehensive(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice testing failed: {str(e)}")

@router.post("/batch")
async def batch_test_voices(
    voice_ids: List[str],
    test_phrases: Optional[List[str]] = None,
    settings: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test multiple voices with the same criteria"""
    
    # Check user permissions for batch operations
    user_tier = current_user.get("subscription_tier", "free")
    if user_tier == "free":
        raise HTTPException(status_code=403, detail="Batch testing requires paid subscription")
    
    testing_service = TestingService(db)
    
    try:
        results = await testing_service.batch_test_voices(
            voice_ids=voice_ids,
            test_phrases=test_phrases,
            settings=settings
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch testing failed: {str(e)}")

# api/v1/endpoints/analytics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from ...dependencies import get_db, get_current_user
from ...services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/voice/{voice_id}")
async def get_voice_analytics(
    voice_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed analytics for a specific voice"""
    
    analytics_service = AnalyticsService(db)
    
    try:
        result = await analytics_service.get_voice_analytics(voice_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@router.get("/user/summary")
async def get_user_analytics_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's overall voice usage analytics"""
    
    analytics_service = AnalyticsService(db)
    
    try:
        result = await analytics_service.get_user_analytics_summary(
            user_id=current_user["user_id"],
            days=days
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@router.get("/performance/trends")
async def get_performance_trends(
    voice_ids: Optional[List[str]] = Query(None),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get performance trends for voices"""
    
    # Check permissions for advanced analytics
    user_tier = current_user.get("subscription_tier", "free")
    if user_tier not in ["pro", "enterprise"]:
        raise HTTPException(status_code=403, detail="Advanced analytics require Pro or Enterprise subscription")
    
    analytics_service = AnalyticsService(db)
    
    try:
        result = await analytics_service.get_performance_trends(
            voice_ids=voice_ids,
            days=days,
            user_id=current_user["user_id"]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trends analysis failed: {str(e)}")