"""
Organization Settings Endpoints
Handles organization-level settings management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from ..schemas.organization import (
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    BusinessHoursUpdate,
    GeneralSettingsUpdate
)
from ..services.organization_service import OrganizationService
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=OrganizationSettingsResponse)
async def get_organization_settings(
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends()
):
    """Get current organization settings"""
    try:
        settings = await org_service.get_organization_settings(current_user.organization_id)
        return settings
    except Exception as e:
        logger.error(f"Failed to get organization settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve organization settings"
        )

@router.put("/", response_model=OrganizationSettingsResponse)
async def update_organization_settings(
    settings_update: OrganizationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends()
):
    """Update organization settings"""
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update organization settings"
            )
        
        updated_settings = await org_service.update_organization_settings(
            current_user.organization_id,
            settings_update
        )
        
        # Log the update
        logger.info(f"Organization settings updated by user {current_user.id}")
        
        return updated_settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update organization settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization settings"
        )

@router.put("/general", response_model=dict)
async def update_general_settings(
    general_update: GeneralSettingsUpdate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends()
):
    """Update general organization settings"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update general settings"
            )
        
        await org_service.update_general_settings(
            current_user.organization_id,
            general_update
        )
        
        return {"message": "General settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update general settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update general settings"
        )

@router.put("/business-hours", response_model=dict)
async def update_business_hours(
    business_hours: BusinessHoursUpdate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends()
):
    """Update organization business hours"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update business hours"
            )
        
        await org_service.update_business_hours(
            current_user.organization_id,
            business_hours
        )
        
        return {"message": "Business hours updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update business hours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update business hours"
        )

@router.get("/timezones", response_model=List[dict])
async def get_available_timezones():
    """Get list of available timezones"""
    timezones = [
        {"value": "America/New_York", "label": "Eastern Time (ET)"},
        {"value": "America/Chicago", "label": "Central Time (CT)"},
        {"value": "America/Denver", "label": "Mountain Time (MT)"},
        {"value": "America/Los_Angeles", "label": "Pacific Time (PT)"},
        {"value": "America/Anchorage", "label": "Alaska Time (AKT)"},
        {"value": "Pacific/Honolulu", "label": "Hawaii Time (HT)"},
        {"value": "UTC", "label": "Coordinated Universal Time (UTC)"},
        {"value": "Europe/London", "label": "Greenwich Mean Time (GMT)"},
        {"value": "Europe/Paris", "label": "Central European Time (CET)"},
        {"value": "Asia/Tokyo", "label": "Japan Standard Time (JST)"},
        {"value": "Asia/Shanghai", "label": "China Standard Time (CST)"},
        {"value": "Australia/Sydney", "label": "Australian Eastern Time (AET)"}
    ]
    return timezones

@router.get("/currencies", response_model=List[dict])
async def get_available_currencies():
    """Get list of available currencies"""
    currencies = [
        {"value": "USD", "label": "US Dollar ($)", "symbol": "$"},
        {"value": "EUR", "label": "Euro (€)", "symbol": "€"},
        {"value": "GBP", "label": "British Pound (£)", "symbol": "£"},
        {"value": "CAD", "label": "Canadian Dollar (C$)", "symbol": "C$"},
        {"value": "AUD", "label": "Australian Dollar (A$)", "symbol": "A$"},
        {"value": "JPY", "label": "Japanese Yen (¥)", "symbol": "¥"},
        {"value": "CHF", "label": "Swiss Franc (CHF)", "symbol": "CHF"},
        {"value": "CNY", "label": "Chinese Yuan (¥)", "symbol": "¥"}
    ]
    return currencies

@router.get("/languages", response_model=List[dict])
async def get_available_languages():
    """Get list of available languages"""
    languages = [
        {"value": "en-US", "label": "English (US)", "flag": "🇺🇸"},
        {"value": "en-GB", "label": "English (UK)", "flag": "🇬🇧"},
        {"value": "es-ES", "label": "Spanish (Spain)", "flag": "🇪🇸"},
        {"value": "es-MX", "label": "Spanish (Mexico)", "flag": "🇲🇽"},
        {"value": "fr-FR", "label": "French (France)", "flag": "🇫🇷"},
        {"value": "fr-CA", "label": "French (Canada)", "flag": "🇨🇦"},
        {"value": "de-DE", "label": "German (Germany)", "flag": "🇩🇪"},
        {"value": "it-IT", "label": "Italian (Italy)", "flag": "🇮🇹"},
        {"value": "pt-PT", "label": "Portuguese (Portugal)", "flag": "🇵🇹"},
        {"value": "pt-BR", "label": "Portuguese (Brazil)", "flag": "🇧🇷"},
        {"value": "ja-JP", "label": "Japanese (Japan)", "flag": "🇯🇵"},
        {"value": "zh-CN", "label": "Chinese (Simplified)", "flag": "🇨🇳"},
        {"value": "ko-KR", "label": "Korean (South Korea)", "flag": "🇰🇷"}
    ]
    return languages

@router.post("/reset", response_model=dict)
async def reset_organization_settings(
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends()
):
    """Reset organization settings to defaults"""
    try:
        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super administrators can reset organization settings"
            )
        
        await org_service.reset_to_defaults(current_user.organization_id)
        
        logger.warning(f"Organization settings reset to defaults by user {current_user.id}")
        
        return {"message": "Organization settings reset to defaults successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset organization settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset organization settings"
        )
