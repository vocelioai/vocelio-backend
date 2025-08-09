"""
Notification Settings Endpoints
Handles notification preferences and delivery settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from ..schemas.notification import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    EmailNotificationUpdate,
    SMSNotificationUpdate,
    PushNotificationUpdate,
    WebhookConfigUpdate,
    NotificationTestRequest
)
from ..services.notification_service import NotificationService
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Get current notification settings"""
    try:
        settings = await notification_service.get_notification_settings(
            current_user.organization_id
        )
        return settings
    except Exception as e:
        logger.error(f"Failed to get notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification settings"
        )

@router.put("/", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Update notification settings"""
    try:
        updated_settings = await notification_service.update_notification_settings(
            current_user.organization_id,
            settings_update
        )
        
        logger.info(f"Notification settings updated by user {current_user.id}")
        
        return updated_settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )

@router.put("/email", response_model=dict)
async def update_email_notifications(
    email_update: EmailNotificationUpdate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Update email notification settings"""
    try:
        await notification_service.update_email_notifications(
            current_user.organization_id,
            email_update
        )
        
        return {"message": "Email notification settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update email notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email notification settings"
        )

@router.put("/sms", response_model=dict)
async def update_sms_notifications(
    sms_update: SMSNotificationUpdate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Update SMS notification settings"""
    try:
        await notification_service.update_sms_notifications(
            current_user.organization_id,
            sms_update
        )
        
        return {"message": "SMS notification settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update SMS notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update SMS notification settings"
        )

@router.put("/push", response_model=dict)
async def update_push_notifications(
    push_update: PushNotificationUpdate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Update push notification settings"""
    try:
        await notification_service.update_push_notifications(
            current_user.organization_id,
            push_update
        )
        
        return {"message": "Push notification settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update push notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update push notification settings"
        )

@router.put("/webhooks", response_model=dict)
async def update_webhook_config(
    webhook_update: WebhookConfigUpdate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Update webhook configuration"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update webhook configuration"
            )
        
        await notification_service.update_webhook_config(
            current_user.organization_id,
            webhook_update
        )
        
        return {"message": "Webhook configuration updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update webhook config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update webhook configuration"
        )

@router.post("/test", response_model=dict)
async def test_notification(
    test_request: NotificationTestRequest,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Test notification delivery"""
    try:
        result = await notification_service.test_notification(
            current_user.organization_id,
            test_request
        )
        
        return {
            "message": f"Test {test_request.type} notification sent successfully",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test notification"
        )

@router.get("/channels", response_model=List[dict])
async def get_notification_channels():
    """Get available notification channels"""
    channels = [
        {
            "type": "email",
            "name": "Email",
            "description": "Email notifications",
            "icon": "mail",
            "supported_events": [
                "campaign_completed",
                "call_failed",
                "system_alert",
                "billing_alert",
                "security_alert"
            ]
        },
        {
            "type": "sms",
            "name": "SMS",
            "description": "Text message notifications",
            "icon": "message-square",
            "supported_events": [
                "urgent_alert",
                "system_down",
                "security_breach"
            ]
        },
        {
            "type": "push",
            "name": "Push Notifications",
            "description": "Browser and mobile push notifications",
            "icon": "bell",
            "supported_events": [
                "campaign_completed",
                "call_answered",
                "new_lead",
                "system_alert"
            ]
        },
        {
            "type": "webhook",
            "name": "Webhooks",
            "description": "HTTP POST notifications to your endpoint",
            "icon": "webhook",
            "supported_events": [
                "all_events"
            ]
        },
        {
            "type": "slack",
            "name": "Slack",
            "description": "Slack channel notifications",
            "icon": "slack",
            "supported_events": [
                "campaign_completed",
                "system_alert",
                "performance_report"
            ]
        }
    ]
    return channels

@router.get("/events", response_model=List[dict])
async def get_notification_events():
    """Get available notification events"""
    events = [
        {
            "type": "campaign_completed",
            "name": "Campaign Completed",
            "description": "When a campaign finishes execution",
            "category": "campaigns",
            "severity": "info"
        },
        {
            "type": "campaign_failed",
            "name": "Campaign Failed",
            "description": "When a campaign fails to execute",
            "category": "campaigns",
            "severity": "error"
        },
        {
            "type": "call_answered",
            "name": "Call Answered",
            "description": "When a call is answered by prospect",
            "category": "calls",
            "severity": "info"
        },
        {
            "type": "call_failed",
            "name": "Call Failed",
            "description": "When a call fails to connect",
            "category": "calls",
            "severity": "warning"
        },
        {
            "type": "high_success_rate",
            "name": "High Success Rate",
            "description": "When campaign success rate exceeds threshold",
            "category": "performance",
            "severity": "success"
        },
        {
            "type": "low_success_rate",
            "name": "Low Success Rate",
            "description": "When campaign success rate falls below threshold",
            "category": "performance",
            "severity": "warning"
        },
        {
            "type": "new_lead",
            "name": "New Lead Generated",
            "description": "When a new lead is generated",
            "category": "leads",
            "severity": "info"
        },
        {
            "type": "system_alert",
            "name": "System Alert",
            "description": "General system notifications",
            "category": "system",
            "severity": "warning"
        },
        {
            "type": "system_down",
            "name": "System Down",
            "description": "When system is experiencing downtime",
            "category": "system",
            "severity": "critical"
        },
        {
            "type": "billing_alert",
            "name": "Billing Alert",
            "description": "Billing and payment notifications",
            "category": "billing",
            "severity": "warning"
        },
        {
            "type": "security_alert",
            "name": "Security Alert",
            "description": "Security-related notifications",
            "category": "security",
            "severity": "critical"
        },
        {
            "type": "security_breach",
            "name": "Security Breach",
            "description": "Critical security breach notifications",
            "category": "security",
            "severity": "critical"
        }
    ]
    return events

@router.get("/templates", response_model=List[dict])
async def get_notification_templates():
    """Get notification templates"""
    templates = [
        {
            "id": "campaign_completed",
            "name": "Campaign Completed",
            "subject": "Campaign '{{campaign_name}}' has completed",
            "body": "Your campaign '{{campaign_name}}' has completed with {{success_rate}}% success rate.",
            "variables": ["campaign_name", "success_rate", "total_calls", "successful_calls"]
        },
        {
            "id": "system_alert",
            "name": "System Alert",
            "subject": "System Alert: {{alert_type}}",
            "body": "Alert: {{alert_message}} at {{timestamp}}",
            "variables": ["alert_type", "alert_message", "timestamp", "severity"]
        },
        {
            "id": "billing_alert",
            "name": "Billing Alert",
            "subject": "Billing Alert: {{alert_type}}",
            "body": "Billing notification: {{message}}. Current balance: ${{balance}}",
            "variables": ["alert_type", "message", "balance", "due_date"]
        }
    ]
    return templates

@router.get("/delivery-log", response_model=List[dict])
async def get_delivery_log(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends()
):
    """Get notification delivery log"""
    try:
        log = await notification_service.get_delivery_log(
            current_user.organization_id,
            limit=limit,
            offset=offset
        )
        return log
    except Exception as e:
        logger.error(f"Failed to get delivery log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve delivery log"
        )