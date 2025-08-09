"""
User Settings Endpoints
Handles user-specific settings and preferences
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from ..schemas.user import (
    UserSettingsResponse,
    UserSettingsUpdate,
    UserPreferencesUpdate,
    NotificationPreferencesUpdate,
    PrivacySettingsUpdate,
    ThemeSettingsUpdate
)
from ..services.user_service import UserService
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Get current user settings"""
    try:
        settings = await user_service.get_user_settings(current_user.id)
        return settings
    except Exception as e:
        logger.error(f"Failed to get user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user settings"
        )

@router.put("/", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Update user settings"""
    try:
        updated_settings = await user_service.update_user_settings(
            current_user.id,
            settings_update
        )
        
        logger.info(f"User settings updated for user {current_user.id}")
        
        return updated_settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user settings"
        )

@router.put("/preferences", response_model=dict)
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Update user preferences"""
    try:
        await user_service.update_user_preferences(
            current_user.id,
            preferences_update
        )
        
        return {"message": "User preferences updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences"
        )

@router.put("/notifications", response_model=dict)
async def update_notification_preferences(
    notification_update: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Update user notification preferences"""
    try:
        await user_service.update_notification_preferences(
            current_user.id,
            notification_update
        )
        
        return {"message": "Notification preferences updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update notification preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )

@router.put("/privacy", response_model=dict)
async def update_privacy_settings(
    privacy_update: PrivacySettingsUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Update user privacy settings"""
    try:
        await user_service.update_privacy_settings(
            current_user.id,
            privacy_update
        )
        
        return {"message": "Privacy settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update privacy settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update privacy settings"
        )

@router.put("/theme", response_model=dict)
async def update_theme_settings(
    theme_update: ThemeSettingsUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Update user theme settings"""
    try:
        await user_service.update_theme_settings(
            current_user.id,
            theme_update
        )
        
        return {"message": "Theme settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update theme settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update theme settings"
        )

@router.get("/themes", response_model=List[dict])
async def get_available_themes():
    """Get available themes"""
    themes = [
        {
            "id": "light",
            "name": "Light Theme",
            "description": "Clean light interface",
            "preview": "/themes/light-preview.png",
            "colors": {
                "primary": "#3B82F6",
                "secondary": "#6B7280",
                "background": "#FFFFFF",
                "surface": "#F9FAFB"
            }
        },
        {
            "id": "dark",
            "name": "Dark Theme",
            "description": "Modern dark interface",
            "preview": "/themes/dark-preview.png",
            "colors": {
                "primary": "#3B82F6",
                "secondary": "#9CA3AF",
                "background": "#111827",
                "surface": "#1F2937"
            }
        },
        {
            "id": "system",
            "name": "System Theme",
            "description": "Follow system preference",
            "preview": "/themes/system-preview.png",
            "colors": {
                "primary": "#3B82F6",
                "secondary": "#6B7280",
                "background": "var(--system-bg)",
                "surface": "var(--system-surface)"
            }
        },
        {
            "id": "high-contrast",
            "name": "High Contrast",
            "description": "Enhanced accessibility",
            "preview": "/themes/high-contrast-preview.png",
            "colors": {
                "primary": "#000000",
                "secondary": "#666666",
                "background": "#FFFFFF",
                "surface": "#F0F0F0"
            }
        }
    ]
    return themes

@router.get("/dashboard-layouts", response_model=List[dict])
async def get_dashboard_layouts():
    """Get available dashboard layouts"""
    layouts = [
        {
            "id": "default",
            "name": "Default Layout",
            "description": "Standard dashboard layout",
            "preview": "/layouts/default-preview.png",
            "features": ["sidebar", "top-nav", "widgets"]
        },
        {
            "id": "compact",
            "name": "Compact Layout",
            "description": "Space-efficient layout",
            "preview": "/layouts/compact-preview.png",
            "features": ["collapsed-sidebar", "compact-widgets"]
        },
        {
            "id": "minimal",
            "name": "Minimal Layout",
            "description": "Clean, distraction-free interface",
            "preview": "/layouts/minimal-preview.png",
            "features": ["hidden-sidebar", "focus-mode"]
        },
        {
            "id": "dashboard-focused",
            "name": "Dashboard Focused",
            "description": "Optimized for dashboard viewing",
            "preview": "/layouts/dashboard-focused-preview.png",
            "features": ["expanded-widgets", "auto-refresh"]
        }
    ]
    return layouts

@router.post("/reset", response_model=dict)
async def reset_user_settings(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Reset user settings to defaults"""
    try:
        await user_service.reset_to_defaults(current_user.id)
        
        logger.info(f"User settings reset to defaults for user {current_user.id}")
        
        return {"message": "User settings reset to defaults successfully"}
    except Exception as e:
        logger.error(f"Failed to reset user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user settings"
        )

@router.post("/export", response_model=dict)
async def export_user_settings(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Export user settings as JSON"""
    try:
        export_data = await user_service.export_settings(current_user.id)
        
        return {
            "message": "Settings exported successfully",
            "data": export_data,
            "exported_at": "2024-01-20T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"Failed to export user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export user settings"
        )

@router.post("/import", response_model=dict)
async def import_user_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Import user settings from JSON"""
    try:
        await user_service.import_settings(current_user.id, settings_data)
        
        logger.info(f"User settings imported for user {current_user.id}")
        
        return {"message": "Settings imported successfully"}
    except Exception as e:
        logger.error(f"Failed to import user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import user settings"
        )

@router.get("/activity-log", response_model=List[dict])
async def get_user_activity_log(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Get user activity log"""
    try:
        activity_log = await user_service.get_activity_log(
            current_user.id,
            limit=limit,
            offset=offset
        )
        return activity_log
    except Exception as e:
        logger.error(f"Failed to get user activity log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity log"
        )
