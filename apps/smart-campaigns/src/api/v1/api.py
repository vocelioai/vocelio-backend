# apps/smart-campaigns/src/api/v1/api.py
from fastapi import APIRouter

from api.v1.endpoints import campaigns, prospects, scheduling, automation

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    campaigns.router,
    prefix="/campaigns",
    tags=["campaigns"]
)

api_router.include_router(
    prospects.router,
    prefix="/prospects",
    tags=["prospects"]
)

api_router.include_router(
    scheduling.router,
    prefix="/scheduling",
    tags=["scheduling"]
)

api_router.include_router(
    automation.router,
    prefix="/automation",
    tags=["automation"]
)

# Health check endpoint for this service
@api_router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for Smart Campaigns service"""
    return {
        "status": "healthy",
        "service": "smart-campaigns",
        "version": "1.0.0"
    }


# apps/smart-campaigns/src/api/v1/endpoints/scheduling.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from services.scheduler_service import SchedulerService
from schemas.campaign import CampaignScheduleConfig
from shared.auth.dependencies import get_current_user, get_organization_id
from shared.database.client import get_database
from shared.schemas.response import APIResponse
from shared.exceptions.service import ServiceException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/campaigns/{campaign_id}/schedule",
    response_model=APIResponse[Dict[str, Any]],
    summary="Schedule campaign",
    description="Schedule a campaign with specific timing and recurrence settings"
)
async def schedule_campaign(
    campaign_id: str,
    schedule_config: CampaignScheduleConfig,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Schedule a campaign"""
    try:
        service = SchedulerService(db)
        result = await service.schedule_campaign(campaign_id, schedule_config, user_id, organization_id)
        
        return APIResponse(
            data=result,
            message="Campaign scheduled successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error scheduling campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error scheduling campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule campaign"
        )

@router.get(
    "/campaigns/{campaign_id}/schedule",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get campaign schedule",
    description="Get the current schedule configuration for a campaign"
)
async def get_campaign_schedule(
    campaign_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get campaign schedule"""
    try:
        service = SchedulerService(db)
        schedule = await service.get_campaign_schedule(campaign_id, user_id, organization_id)
        
        return APIResponse(
            data=schedule,
            message="Campaign schedule retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error getting campaign schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error getting campaign schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign schedule"
        )


# apps/smart-campaigns/src/api/v1/endpoints/automation.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from services.automation_service import AutomationService
from shared.auth.dependencies import get_current_user, get_organization_id
from shared.database.client import get_database
from shared.schemas.response import APIResponse
from shared.exceptions.service import ServiceException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/campaigns/{campaign_id}/auto-optimize",
    response_model=APIResponse[Dict[str, Any]],
    summary="Auto-optimize campaign",
    description="Enable automatic AI optimization for a campaign"
)
async def enable_auto_optimization(
    campaign_id: str,
    optimization_settings: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Enable auto-optimization for campaign"""
    try:
        service = AutomationService(db)
        result = await service.enable_auto_optimization(
            campaign_id, optimization_settings, user_id, organization_id
        )
        
        return APIResponse(
            data=result,
            message="Auto-optimization enabled successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error enabling auto-optimization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error enabling auto-optimization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable auto-optimization"
        )

@router.get(
    "/campaigns/{campaign_id}/automation-status",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get automation status",
    description="Get the current automation status and settings for a campaign"
)
async def get_automation_status(
    campaign_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get automation status"""
    try:
        service = AutomationService(db)
        status_info = await service.get_automation_status(campaign_id, user_id, organization_id)
        
        return APIResponse(
            data=status_info,
            message="Automation status retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error getting automation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error getting automation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get automation status"
        )


# apps/smart-campaigns/src/services/scheduler_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from models.campaign import Campaign, CampaignSchedule
from schemas.campaign import CampaignScheduleConfig
from shared.database.client import get_database
from shared.exceptions.service import ServiceException, ValidationException

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for campaign scheduling"""
    
    def __init__(self, db: Session = None):
        self.db = db or get_database()
    
    async def schedule_campaign(
        self, 
        campaign_id: str, 
        schedule_config: CampaignScheduleConfig, 
        user_id: str, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Schedule a campaign"""
        try:
            # Validate campaign exists and belongs to user
            campaign = self.db.query(Campaign).filter(
                Campaign.id == campaign_id,
                Campaign.user_id == user_id,
                Campaign.organization_id == organization_id
            ).first()
            
            if not campaign:
                raise ValidationException("Campaign not found")
            
            # Create or update schedule
            existing_schedule = self.db.query(CampaignSchedule).filter(
                CampaignSchedule.campaign_id == campaign_id
            ).first()
            
            if existing_schedule:
                # Update existing schedule
                for field, value in schedule_config.dict().items():
                    setattr(existing_schedule, field, value)
                schedule = existing_schedule
            else:
                # Create new schedule
                schedule = CampaignSchedule(
                    campaign_id=campaign_id,
                    **schedule_config.dict()
                )
                self.db.add(schedule)
            
            await self.db.commit()
            await self.db.refresh(schedule)
            
            return schedule.to_dict()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error scheduling campaign: {str(e)}")
            raise ServiceException(f"Failed to schedule campaign: {str(e)}")
    
    async def get_campaign_schedule(
        self, 
        campaign_id: str, 
        user_id: str, 
        organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get campaign schedule"""
        try:
            # Validate campaign access
            campaign = self.db.query(Campaign).filter(
                Campaign.id == campaign_id,
                Campaign.user_id == user_id,
                Campaign.organization_id == organization_id
            ).first()
            
            if not campaign:
                raise ValidationException("Campaign not found")
            
            # Get schedule
            schedule = self.db.query(CampaignSchedule).filter(
                CampaignSchedule.campaign_id == campaign_id
            ).first()
            
            return schedule.to_dict() if schedule else None
            
        except Exception as e:
            logger.error(f"Error getting campaign schedule: {str(e)}")
            raise ServiceException(f"Failed to get campaign schedule: {str(e)}")


# apps/smart-campaigns/src/services/automation_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from models.campaign import Campaign
from shared.database.client import get_database
from shared.exceptions.service import ServiceException, ValidationException

logger = logging.getLogger(__name__)

class AutomationService:
    """Service for campaign automation"""
    
    def __init__(self, db: Session = None):
        self.db = db or get_database()
    
    async def enable_auto_optimization(
        self, 
        campaign_id: str, 
        optimization_settings: Dict[str, Any], 
        user_id: str, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Enable auto-optimization for campaign"""
        try:
            # Validate campaign exists and belongs to user
            campaign = self.db.query(Campaign).filter(
                Campaign.id == campaign_id,
                Campaign.user_id == user_id,
                Campaign.organization_id == organization_id
            ).first()
            
            if not campaign:
                raise ValidationException("Campaign not found")
            
            # Enable auto-optimization
            campaign.ai_optimization_enabled = True
            campaign.settings.update({
                "auto_optimization": True,
                "optimization_settings": optimization_settings
            })
            
            await self.db.commit()
            
            return {
                "campaign_id": campaign_id,
                "auto_optimization_enabled": True,
                "settings": optimization_settings
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error enabling auto-optimization: {str(e)}")
            raise ServiceException(f"Failed to enable auto-optimization: {str(e)}")
    
    async def get_automation_status(
        self, 
        campaign_id: str, 
        user_id: str, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Get automation status for campaign"""
        try:
            # Validate campaign access
            campaign = self.db.query(Campaign).filter(
                Campaign.id == campaign_id,
                Campaign.user_id == user_id,
                Campaign.organization_id == organization_id
            ).first()
            
            if not campaign:
                raise ValidationException("Campaign not found")
            
            return {
                "campaign_id": campaign_id,
                "ai_optimization_enabled": campaign.ai_optimization_enabled,
                "ai_optimization_score": campaign.ai_optimization_score,
                "auto_optimization": campaign.settings.get("auto_optimization", False),
                "optimization_settings": campaign.settings.get("optimization_settings", {}),
                "last_optimization": campaign.updated_at.isoformat() if campaign.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting automation status: {str(e)}")
            raise ServiceException(f"Failed to get automation status: {str(e)}")