"""
Voice Lab - Voice Cloning Endpoints
Handles voice cloning, training, and custom voice creation
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional
import asyncio

from services.cloning_service import CloningService
from schemas.cloning import (
    CloningRequest,
    CloningResponse,
    CloningStatus,
    CloneValidation
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

@router.post("/clone", response_model=CloningResponse)
async def clone_voice(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(..., description="Audio file for voice cloning"),
    voice_name: str = Form(..., description="Name for the cloned voice"),
    description: str = Form(..., description="Description of the voice"),
    language: str = Form("en", description="Voice language"),
    gender: str = Form(..., description="Voice gender (male/female)"),
    use_case: str = Form("general", description="Intended use case"),
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Start voice cloning process"""
    # Validate file
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="Invalid audio file format")
    
    if audio_file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    try:
        # Create cloning request
        clone_request = CloningRequest(
            voice_name=voice_name,
            description=description,
            language=language,
            gender=gender,
            use_case=use_case
        )
        
        # Start cloning process
        clone_id = await cloning_service.start_cloning(
            audio_file=audio_file,
            request=clone_request,
            user_id=current_user.id
        )
        
        # Add background task for processing
        background_tasks.add_task(
            cloning_service.process_voice_cloning,
            clone_id,
            current_user.id
        )
        
        return CloningResponse(
            clone_id=clone_id,
            status="processing",
            voice_name=voice_name,
            estimated_completion="3-5 minutes",
            message="Voice cloning started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloning failed: {str(e)}")

@router.get("/status/{clone_id}", response_model=CloningStatus)
async def get_cloning_status(
    clone_id: str,
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get voice cloning status"""
    status = await cloning_service.get_cloning_status(clone_id, current_user.id)
    if not status:
        raise HTTPException(status_code=404, detail="Cloning job not found")
    return status

@router.get("/jobs", response_model=List[CloningStatus])
async def get_cloning_jobs(
    status: Optional[str] = None,
    limit: int = 20,
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get user's voice cloning jobs"""
    jobs = await cloning_service.get_user_cloning_jobs(
        user_id=current_user.id,
        status=status,
        limit=limit
    )
    return jobs

@router.post("/validate")
async def validate_cloning_audio(
    audio_file: UploadFile = File(...),
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Validate audio file for voice cloning"""
    try:
        validation = await cloning_service.validate_audio_file(audio_file)
        return validation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

@router.post("/enhance-audio")
async def enhance_audio_for_cloning(
    audio_file: UploadFile = File(...),
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Enhance audio quality for better cloning results"""
    try:
        enhanced_file_path = await cloning_service.enhance_audio(
            audio_file=audio_file,
            user_id=current_user.id
        )
        
        return {
            "message": "Audio enhanced successfully",
            "enhanced_file": enhanced_file_path,
            "improvements": [
                "Noise reduction applied",
                "Frequency normalization",
                "Volume optimization",
                "Quality enhancement"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

@router.delete("/{clone_id}")
async def cancel_cloning(
    clone_id: str,
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Cancel ongoing voice cloning process"""
    success = await cloning_service.cancel_cloning(clone_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Cloning job not found")
    
    return {"message": "Cloning job cancelled successfully"}

@router.post("/{clone_id}/approve")
async def approve_cloned_voice(
    clone_id: str,
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Approve and finalize cloned voice"""
    try:
        voice = await cloning_service.approve_cloned_voice(clone_id, current_user.id)
        return {
            "message": "Voice cloning approved and finalized",
            "voice_id": voice.voice_id,
            "voice_name": voice.name,
            "status": "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@router.get("/requirements")
async def get_cloning_requirements():
    """Get voice cloning requirements and guidelines"""
    return {
        "audio_requirements": {
            "min_duration": "60 seconds",
            "max_duration": "10 minutes", 
            "optimal_duration": "2-5 minutes",
            "sample_rate": "16kHz or higher",
            "format": ["mp3", "wav", "m4a"],
            "max_file_size": "10MB"
        },
        "quality_guidelines": [
            "Clear, noise-free recording",
            "Single speaker only",
            "Consistent volume level",
            "No background music or sounds",
            "Natural speech patterns",
            "Variety of phonemes and emotions"
        ],
        "privacy_notice": "All audio files are processed securely and deleted after cloning",
        "estimated_time": "3-5 minutes for standard cloning",
        "accuracy_rating": "95%+ similarity with high-quality input"
    }

@router.post("/batch-clone")
async def batch_clone_voices(
    background_tasks: BackgroundTasks,
    audio_files: List[UploadFile] = File(...),
    voice_names: List[str] = Form(...),
    descriptions: List[str] = Form(...),
    cloning_service: CloningService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Clone multiple voices in batch"""
    if len(audio_files) != len(voice_names) or len(audio_files) != len(descriptions):
        raise HTTPException(status_code=400, detail="Mismatched arrays length")
    
    if len(audio_files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 voices per batch")
    
    try:
        batch_id = await cloning_service.start_batch_cloning(
            audio_files=audio_files,
            voice_names=voice_names,
            descriptions=descriptions,
            user_id=current_user.id
        )
        
        background_tasks.add_task(
            cloning_service.process_batch_cloning,
            batch_id,
            current_user.id
        )
        
        return {
            "batch_id": batch_id,
            "status": "processing",
            "total_voices": len(audio_files),
            "estimated_completion": f"{len(audio_files) * 4} minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch cloning failed: {str(e)}")
