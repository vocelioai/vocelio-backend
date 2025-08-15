# apps/call-center/src/api/v1/endpoints/dialer.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.dialer_service import DialerService
from schemas.dialer import (
    DialerConfig, DialerStatus, DialerMetrics, 
    CampaignConfig, DialerModeUpdate
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start", response_model=DialerStatus)
async def start_dialer(
    config: DialerConfig,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Start auto dialer with specified configuration"""
    dialer_service = DialerService()
    
    try:
        # Validate configuration
        await dialer_service.validate_config(config)
        
        # Start dialer in background
        status = await dialer_service.start_dialer(config, current_user.id)
        background_tasks.add_task(dialer_service.run_dialer_campaign, status.session_id)
        
        logger.info(f"Dialer started by user {current_user.id} with mode {config.mode}")
        return status
        
    except Exception as e:
        logger.error(f"Error starting dialer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start dialer: {str(e)}")

@router.post("/stop")
async def stop_dialer(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Stop auto dialer"""
    dialer_service = DialerService()
    
    try:
        success = await dialer_service.stop_dialer(session_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Active dialer session not found")
        
        logger.info(f"Dialer stopped by user {current_user.id}")
        return {"message": "Dialer stopped successfully", "stopped_at": datetime.utcnow()}
        
    except Exception as e:
        logger.error(f"Error stopping dialer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop dialer: {str(e)}")

@router.post("/pause")
async def pause_dialer(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Pause auto dialer"""
    dialer_service = DialerService()
    
    try:
        success = await dialer_service.pause_dialer(session_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Active dialer session not found")
        
        return {"message": "Dialer paused successfully", "paused_at": datetime.utcnow()}
        
    except Exception as e:
        logger.error(f"Error pausing dialer: {e}")
        raise HTTPException(status_code=500, detail="Failed to pause dialer")

@router.post("/resume")
async def resume_dialer(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Resume paused auto dialer"""
    dialer_service = DialerService()
    
    try:
        success = await dialer_service.resume_dialer(session_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Paused dialer session not found")
        
        return {"message": "Dialer resumed successfully", "resumed_at": datetime.utcnow()}
        
    except Exception as e:
        logger.error(f"Error resuming dialer: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume dialer")

@router.put("/mode", response_model=DialerStatus)
async def update_dialer_mode(
    mode_update: DialerModeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update dialer mode (predictive, progressive, preview, manual)"""
    dialer_service = DialerService()
    
    try:
        status = await dialer_service.update_mode(mode_update, current_user.id)
        if not status:
            raise HTTPException(status_code=404, detail="Active dialer session not found")
        
        logger.info(f"Dialer mode updated to {mode_update.mode} by user {current_user.id}")
        return status
        
    except Exception as e:
        logger.error(f"Error updating dialer mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to update dialer mode")

@router.get("/status", response_model=DialerStatus)
async def get_dialer_status(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get current dialer status"""
    dialer_service = DialerService()
    
    try:
        status = await dialer_service.get_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="No active dialer session found")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting dialer status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dialer status")

@router.get("/metrics", response_model=DialerMetrics)
async def get_dialer_metrics(
    session_id: Optional[str] = None,
    period: str = "today",
    current_user: User = Depends(get_current_user)
):
    """Get dialer performance metrics"""
    dialer_service = DialerService()
    
    try:
        metrics = await dialer_service.get_metrics(session_id, period)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting dialer metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dialer metrics")

@router.get("/campaigns", response_model=List[CampaignConfig])
async def get_dialer_campaigns(
    active_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get available dialer campaigns"""
    dialer_service = DialerService()
    
    try:
        campaigns = await dialer_service.get_campaigns(active_only)
        return campaigns
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get campaigns")

@router.post("/campaigns", response_model=CampaignConfig)
async def create_dialer_campaign(
    campaign: CampaignConfig,
    current_user: User = Depends(get_current_user)
):
    """Create new dialer campaign"""
    dialer_service = DialerService()
    
    try:
        created_campaign = await dialer_service.create_campaign(campaign, current_user.id)
        logger.info(f"Campaign {campaign.name} created by user {current_user.id}")
        return created_campaign
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail="Failed to create campaign")

@router.put("/campaigns/{campaign_id}", response_model=CampaignConfig)
async def update_dialer_campaign(
    campaign_id: str,
    campaign_update: CampaignConfig,
    current_user: User = Depends(get_current_user)
):
    """Update existing dialer campaign"""
    dialer_service = DialerService()
    
    try:
        updated_campaign = await dialer_service.update_campaign(
            campaign_id, campaign_update, current_user.id
        )
        if not updated_campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return updated_campaign
        
    except Exception as e:
        logger.error(f"Error updating campaign: {e}")
        raise HTTPException(status_code=500, detail="Failed to update campaign")

@router.delete("/campaigns/{campaign_id}")
async def delete_dialer_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete dialer campaign"""
    dialer_service = DialerService()
    
    try:
        success = await dialer_service.delete_campaign(campaign_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {"message": "Campaign deleted successfully", "campaign_id": campaign_id}
        
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete campaign")
