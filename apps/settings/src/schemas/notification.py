"""
Notification Settings Schemas
Pydantic models for notification settings requests and responses
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class EmailNotificationConfig(BaseModel):
    """Email notification configuration"""
    enabled: bool = Field(description="Enable email notifications")
    email_addresses: List[EmailStr] = Field(description="List of email addresses")
    campaign_alerts: bool = Field(description="Campaign completion alerts")
    system_alerts: bool = Field(description="System alerts")
    performance_alerts: bool = Field(description="Performance alerts")
    billing_alerts: bool = Field(description="Billing alerts")
    security_alerts: bool = Field(description="Security alerts")
    daily_summary: bool = Field(description="Daily summary emails")
    weekly_report: bool = Field(description="Weekly performance reports")

class SMSNotificationConfig(BaseModel):
    """SMS notification configuration"""
    enabled: bool = Field(description="Enable SMS notifications")
    phone_numbers: List[str] = Field(description="List of phone numbers")
    urgent_only: bool = Field(description="Only urgent notifications")
    system_down: bool = Field(description="System downtime alerts")
    security_breach: bool = Field(description="Security breach alerts")
    
    @validator('phone_numbers')
    def validate_phone_numbers(cls, v):
        """Validate phone number format"""
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        for phone in v:
            if not phone_pattern.match(phone.replace(' ', '').replace('-', '')):
                raise ValueError(f'Invalid phone number format: {phone}')
        return v

class PushNotificationConfig(BaseModel):
    """Push notification configuration"""
    enabled: bool = Field(description="Enable push notifications")
    browser_enabled: bool = Field(description="Browser push notifications")
    mobile_enabled: bool = Field(description="Mobile push notifications")
    campaign_completed: bool = Field(description="Campaign completion")
    call_answered: bool = Field(description="Call answered")
    new_leads: bool = Field(description="New leads generated")
    system_alerts: bool = Field(description="System alerts")

class WebhookConfig(BaseModel):
    """Webhook configuration"""
    enabled: bool = Field(description="Enable webhooks")
    webhook_url: str = Field(description="Webhook endpoint URL")
    secret_token: Optional[str] = Field(None, description="Secret token for verification")
    events: List[str] = Field(description="Events to send")
    retry_attempts: int = Field(default=3, ge=1, le=10, description="Retry attempts")
    timeout_seconds: int = Field(default=10, ge=5, le=60, description="Timeout in seconds")
    
    @validator('webhook_url')
    def validate_webhook_url(cls, v):
        """Validate webhook URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError('Invalid webhook URL format')
        return v

class SlackIntegration(BaseModel):
    """Slack integration configuration"""
    enabled: bool = Field(description="Enable Slack integration")
    webhook_url: Optional[str] = None
    channel: Optional[str] = None
    bot_token: Optional[str] = None
    campaign_alerts: bool = Field(default=True)
    system_alerts: bool = Field(default=True)
    performance_reports: bool = Field(default=False)

class NotificationSettingsResponse(BaseModel):
    """Notification settings response"""
    id: str
    organization_id: str
    email_notifications: EmailNotificationConfig
    sms_notifications: SMSNotificationConfig
    push_notifications: PushNotificationConfig
    webhook_config: WebhookConfig
    slack_integration: SlackIntegration
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmailNotificationUpdate(BaseModel):
    """Email notification update request"""
    enabled: Optional[bool] = None
    email_addresses: Optional[List[EmailStr]] = None
    campaign_alerts: Optional[bool] = None
    system_alerts: Optional[bool] = None
    performance_alerts: Optional[bool] = None
    billing_alerts: Optional[bool] = None
    security_alerts: Optional[bool] = None
    daily_summary: Optional[bool] = None
    weekly_report: Optional[bool] = None

class SMSNotificationUpdate(BaseModel):
    """SMS notification update request"""
    enabled: Optional[bool] = None
    phone_numbers: Optional[List[str]] = None
    urgent_only: Optional[bool] = None
    system_down: Optional[bool] = None
    security_breach: Optional[bool] = None

class PushNotificationUpdate(BaseModel):
    """Push notification update request"""
    enabled: Optional[bool] = None
    browser_enabled: Optional[bool] = None
    mobile_enabled: Optional[bool] = None
    campaign_completed: Optional[bool] = None
    call_answered: Optional[bool] = None
    new_leads: Optional[bool] = None
    system_alerts: Optional[bool] = None

class WebhookConfigUpdate(BaseModel):
    """Webhook configuration update request"""
    enabled: Optional[bool] = None
    webhook_url: Optional[str] = None
    secret_token: Optional[str] = None
    events: Optional[List[str]] = None
    retry_attempts: Optional[int] = Field(None, ge=1, le=10)
    timeout_seconds: Optional[int] = Field(None, ge=5, le=60)

class SlackIntegrationUpdate(BaseModel):
    """Slack integration update request"""
    enabled: Optional[bool] = None
    webhook_url: Optional[str] = None
    channel: Optional[str] = None
    bot_token: Optional[str] = None
    campaign_alerts: Optional[bool] = None
    system_alerts: Optional[bool] = None
    performance_reports: Optional[bool] = None

class NotificationSettingsUpdate(BaseModel):
    """Complete notification settings update"""
    email_notifications: Optional[EmailNotificationUpdate] = None
    sms_notifications: Optional[SMSNotificationUpdate] = None
    push_notifications: Optional[PushNotificationUpdate] = None
    webhook_config: Optional[WebhookConfigUpdate] = None
    slack_integration: Optional[SlackIntegrationUpdate] = None

class NotificationTestRequest(BaseModel):
    """Notification test request"""
    type: str = Field(..., description="Notification type (email, sms, push, webhook)")
    recipient: str = Field(..., description="Test recipient")
    message: Optional[str] = Field("Test notification", description="Test message")
    
    @validator('type')
    def validate_type(cls, v):
        """Validate notification type"""
        valid_types = ['email', 'sms', 'push', 'webhook', 'slack']
        if v not in valid_types:
            raise ValueError(f'Invalid notification type: {v}')
        return v

class NotificationDeliveryLog(BaseModel):
    """Notification delivery log entry"""
    id: str
    organization_id: str
    notification_type: str
    recipient: str
    subject: Optional[str]
    message: str
    status: str  # sent, delivered, failed, pending
    error_message: Optional[str]
    sent_at: datetime
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Default notification settings
DEFAULT_NOTIFICATION_SETTINGS = {
    "email_notifications": {
        "enabled": True,
        "email_addresses": [],
        "campaign_alerts": True,
        "system_alerts": True,
        "performance_alerts": True,
        "billing_alerts": True,
        "security_alerts": True,
        "daily_summary": false,
        "weekly_report": false
    },
    "sms_notifications": {
        "enabled": False,
        "phone_numbers": [],
        "urgent_only": True,
        "system_down": True,
        "security_breach": True
    },
    "push_notifications": {
        "enabled": True,
        "browser_enabled": True,
        "mobile_enabled": False,
        "campaign_completed": True,
        "call_answered": False,
        "new_leads": True,
        "system_alerts": True
    },
    "webhook_config": {
        "enabled": False,
        "webhook_url": "",
        "secret_token": None,
        "events": [],
        "retry_attempts": 3,
        "timeout_seconds": 10
    },
    "slack_integration": {
        "enabled": False,
        "webhook_url": None,
        "channel": None,
        "bot_token": None,
        "campaign_alerts": True,
        "system_alerts": True,
        "performance_reports": False
    }
}
