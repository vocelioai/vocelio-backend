"""
Settings Service Database Models
SQLAlchemy models for settings data
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class OrganizationSettings(Base):
    """Organization settings model"""
    __tablename__ = "organization_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, unique=True)
    
    # General settings (JSON field)
    general = Column(JSON, nullable=False, default={
        "organization_name": "",
        "timezone": "America/New_York",
        "language": "en-US",
        "date_format": "MM/DD/YYYY",
        "currency": "USD"
    })
    
    # Business hours (JSON field)
    business_hours = Column(JSON, nullable=False, default={
        "start": "09:00",
        "end": "18:00",
        "timezone": "America/New_York",
        "workdays": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    })
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SecuritySettings(Base):
    """Security settings model"""
    __tablename__ = "security_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, unique=True)
    
    # Two-factor authentication settings
    two_factor_auth = Column(JSON, nullable=False, default={
        "enabled": False,
        "enforced": False,
        "methods": ["totp", "email"],
        "backup_codes": True
    })
    
    # Password policy settings
    password_policy = Column(JSON, nullable=False, default={
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": False,
        "max_age_days": None,
        "prevent_reuse": None
    })
    
    # Session security settings
    session_security = Column(JSON, nullable=False, default={
        "timeout_minutes": 60,
        "max_concurrent_sessions": 3,
        "secure_cookies": True,
        "same_site_policy": "lax"
    })
    
    # IP whitelist settings
    ip_whitelist = Column(JSON, nullable=False, default={
        "enabled": False,
        "ip_addresses": []
    })
    
    # Data encryption settings
    data_encryption = Column(JSON, nullable=False, default={
        "at_rest": True,
        "in_transit": True,
        "key_rotation_days": 90,
        "algorithm": "AES-256"
    })
    
    # Audit logging
    audit_logging = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class NotificationSettings(Base):
    """Notification settings model"""
    __tablename__ = "notification_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, unique=True)
    
    # Email notification settings
    email_notifications = Column(JSON, nullable=False, default={
        "enabled": True,
        "email_addresses": [],
        "campaign_alerts": True,
        "system_alerts": True,
        "performance_alerts": True,
        "billing_alerts": True,
        "security_alerts": True,
        "daily_summary": False,
        "weekly_report": False
    })
    
    # SMS notification settings
    sms_notifications = Column(JSON, nullable=False, default={
        "enabled": False,
        "phone_numbers": [],
        "urgent_only": True,
        "system_down": True,
        "security_breach": True
    })
    
    # Push notification settings
    push_notifications = Column(JSON, nullable=False, default={
        "enabled": True,
        "browser_enabled": True,
        "mobile_enabled": False,
        "campaign_completed": True,
        "call_answered": False,
        "new_leads": True,
        "system_alerts": True
    })
    
    # Webhook configuration
    webhook_config = Column(JSON, nullable=False, default={
        "enabled": False,
        "webhook_url": "",
        "secret_token": None,
        "events": [],
        "retry_attempts": 3,
        "timeout_seconds": 10
    })
    
    # Slack integration
    slack_integration = Column(JSON, nullable=False, default={
        "enabled": False,
        "webhook_url": None,
        "channel": None,
        "bot_token": None,
        "campaign_alerts": True,
        "system_alerts": True,
        "performance_reports": False
    })
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UserSettings(Base):
    """User-specific settings model"""
    __tablename__ = "user_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True)
    organization_id = Column(String, nullable=False)
    
    # Theme and display preferences
    preferences = Column(JSON, nullable=False, default={
        "theme": "dark",
        "language": "en-US",
        "timezone": "America/New_York",
        "date_format": "MM/DD/YYYY",
        "time_format": "12h",
        "dashboard_layout": "default",
        "notifications_sound": True,
        "auto_refresh": True,
        "items_per_page": 25
    })
    
    # Notification preferences (user-specific overrides)
    notification_preferences = Column(JSON, nullable=False, default={
        "email_enabled": True,
        "push_enabled": True,
        "sound_enabled": True,
        "desktop_notifications": True,
        "campaign_notifications": True,
        "system_notifications": True,
        "marketing_emails": False
    })
    
    # Privacy settings
    privacy_settings = Column(JSON, nullable=False, default={
        "profile_visibility": "organization",
        "activity_tracking": True,
        "data_sharing": False,
        "analytics_opt_out": False
    })
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SecurityAuditLog(Base):
    """Security audit log model"""
    __tablename__ = "security_audit_log"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    
    # Event details
    event_type = Column(String, nullable=False)
    event_description = Column(Text, nullable=False)
    
    # Request details
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    
    # Additional event data
    details = Column(JSON, nullable=True, default={})
    
    # Severity level
    severity = Column(String, nullable=False, default="info")  # info, warning, error, critical
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class NotificationDeliveryLog(Base):
    """Notification delivery log model"""
    __tablename__ = "notification_delivery_log"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False)
    
    # Notification details
    notification_type = Column(String, nullable=False)  # email, sms, push, webhook
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    
    # Delivery status
    status = Column(String, nullable=False, default="pending")  # pending, sent, delivered, failed
    error_message = Column(Text, nullable=True)
    
    # Timing
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True, default={})

class SettingsBackup(Base):
    """Settings backup model for version control"""
    __tablename__ = "settings_backup"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    
    # Backup details
    backup_type = Column(String, nullable=False)  # organization, security, notification, user
    settings_data = Column(JSON, nullable=False)
    
    # Version info
    version = Column(Integer, nullable=False, default=1)
    description = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
