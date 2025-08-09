"""
Preferences Endpoints
Handles user preferences and customization settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from ..schemas.preferences import (
    PreferencesResponse,
    PreferencesUpdate,
    DashboardPreferencesUpdate,
    AccessibilityPreferencesUpdate,
    WorkflowPreferencesUpdate
)
from ..services.preference_service import PreferenceService
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Get user preferences"""
    try:
        preferences = await preference_service.get_preferences(current_user.id)
        return preferences
    except Exception as e:
        logger.error(f"Failed to get preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve preferences"
        )

@router.put("/", response_model=PreferencesResponse)
async def update_preferences(
    preferences_update: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Update user preferences"""
    try:
        updated_preferences = await preference_service.update_preferences(
            current_user.id,
            preferences_update
        )
        
        logger.info(f"Preferences updated for user {current_user.id}")
        
        return updated_preferences
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

@router.put("/dashboard", response_model=dict)
async def update_dashboard_preferences(
    dashboard_update: DashboardPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Update dashboard preferences"""
    try:
        await preference_service.update_dashboard_preferences(
            current_user.id,
            dashboard_update
        )
        
        return {"message": "Dashboard preferences updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dashboard preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dashboard preferences"
        )

@router.put("/accessibility", response_model=dict)
async def update_accessibility_preferences(
    accessibility_update: AccessibilityPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Update accessibility preferences"""
    try:
        await preference_service.update_accessibility_preferences(
            current_user.id,
            accessibility_update
        )
        
        return {"message": "Accessibility preferences updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update accessibility preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update accessibility preferences"
        )

@router.put("/workflow", response_model=dict)
async def update_workflow_preferences(
    workflow_update: WorkflowPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Update workflow preferences"""
    try:
        await preference_service.update_workflow_preferences(
            current_user.id,
            workflow_update
        )
        
        return {"message": "Workflow preferences updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workflow preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workflow preferences"
        )

@router.get("/widgets", response_model=List[dict])
async def get_available_widgets():
    """Get available dashboard widgets"""
    widgets = [
        {
            "id": "active_calls",
            "name": "Active Calls",
            "description": "Real-time active call count",
            "category": "calls",
            "size": "small",
            "configurable": True,
            "refresh_interval": 5
        },
        {
            "id": "daily_revenue",
            "name": "Daily Revenue",
            "description": "Today's revenue tracking",
            "category": "revenue",
            "size": "medium",
            "configurable": True,
            "refresh_interval": 30
        },
        {
            "id": "success_rate",
            "name": "Success Rate",
            "description": "Campaign success rate metrics",
            "category": "performance",
            "size": "medium",
            "configurable": True,
            "refresh_interval": 60
        },
        {
            "id": "campaign_status",
            "name": "Campaign Status",
            "description": "Active campaign overview",
            "category": "campaigns",
            "size": "large",
            "configurable": True,
            "refresh_interval": 30
        },
        {
            "id": "system_health",
            "name": "System Health",
            "description": "System performance indicators",
            "category": "system",
            "size": "small",
            "configurable": False,
            "refresh_interval": 10
        },
        {
            "id": "recent_calls",
            "name": "Recent Calls",
            "description": "Latest call activity",
            "category": "calls",
            "size": "large",
            "configurable": True,
            "refresh_interval": 15
        },
        {
            "id": "ai_insights",
            "name": "AI Insights",
            "description": "AI-generated recommendations",
            "category": "ai",
            "size": "large",
            "configurable": True,
            "refresh_interval": 300
        },
        {
            "id": "performance_chart",
            "name": "Performance Chart",
            "description": "Performance trends over time",
            "category": "analytics",
            "size": "large",
            "configurable": True,
            "refresh_interval": 60
        }
    ]
    return widgets

@router.get("/shortcuts", response_model=List[dict])
async def get_keyboard_shortcuts():
    """Get available keyboard shortcuts"""
    shortcuts = [
        {
            "category": "Navigation",
            "shortcuts": [
                {"key": "Ctrl+1", "action": "Go to Dashboard", "description": "Navigate to main dashboard"},
                {"key": "Ctrl+2", "action": "Go to Campaigns", "description": "Navigate to campaigns page"},
                {"key": "Ctrl+3", "action": "Go to Call Center", "description": "Navigate to call center"},
                {"key": "Ctrl+4", "action": "Go to Analytics", "description": "Navigate to analytics"},
                {"key": "Ctrl+/", "action": "Show Help", "description": "Open help documentation"}
            ]
        },
        {
            "category": "Actions",
            "shortcuts": [
                {"key": "Ctrl+N", "action": "New Campaign", "description": "Create new campaign"},
                {"key": "Ctrl+S", "action": "Save", "description": "Save current changes"},
                {"key": "Ctrl+R", "action": "Refresh", "description": "Refresh current page"},
                {"key": "Ctrl+F", "action": "Search", "description": "Open search dialog"},
                {"key": "Esc", "action": "Close Modal", "description": "Close current modal/dialog"}
            ]
        },
        {
            "category": "Call Management",
            "shortcuts": [
                {"key": "Space", "action": "Play/Pause", "description": "Play or pause current call"},
                {"key": "Ctrl+Enter", "action": "Start Call", "description": "Start new call"},
                {"key": "Ctrl+Shift+H", "action": "Hang Up", "description": "End current call"},
                {"key": "Ctrl+M", "action": "Mute/Unmute", "description": "Toggle mute"}
            ]
        }
    ]
    return shortcuts

@router.post("/shortcuts/custom", response_model=dict)
async def create_custom_shortcut(
    shortcut_data: dict,
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Create custom keyboard shortcut"""
    try:
        await preference_service.create_custom_shortcut(
            current_user.id,
            shortcut_data
        )
        
        return {"message": "Custom shortcut created successfully"}
    except Exception as e:
        logger.error(f"Failed to create custom shortcut: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create custom shortcut"
        )

@router.get("/integrations", response_model=List[dict])
async def get_integration_preferences(
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Get user integration preferences"""
    try:
        integrations = await preference_service.get_integration_preferences(current_user.id)
        return integrations
    except Exception as e:
        logger.error(f"Failed to get integration preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve integration preferences"
        )

@router.put("/integrations/{integration_id}", response_model=dict)
async def update_integration_preference(
    integration_id: str,
    settings: dict,
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Update specific integration preference"""
    try:
        await preference_service.update_integration_preference(
            current_user.id,
            integration_id,
            settings
        )
        
        return {"message": f"Integration {integration_id} preferences updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update integration preference: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update integration preference"
        )

@router.get("/quick-actions", response_model=List[dict])
async def get_quick_actions(
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Get user's configured quick actions"""
    try:
        quick_actions = await preference_service.get_quick_actions(current_user.id)
        return quick_actions
    except Exception as e:
        logger.error(f"Failed to get quick actions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quick actions"
        )

@router.put("/quick-actions", response_model=dict)
async def update_quick_actions(
    quick_actions: List[dict],
    current_user: User = Depends(get_current_user),
    preference_service: PreferenceService = Depends()
):
    """Update user's quick actions"""
    try:
        await preference_service.update_quick_actions(
            current_user.id,
            quick_actions
        )
        
        return {"message": "Quick actions updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update quick actions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quick actions"
        )
