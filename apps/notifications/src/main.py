"""
Notifications Service - Vocelio AI Call Center
Comprehensive multi-channel notification and communication management
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import re
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Notification Models
class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    VOICE_CALL = "voice_call"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class NotificationTrigger(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    AUTOMATED = "automated"
    API = "api"

class MessageFormat(str, Enum):
    PLAIN_TEXT = "plain_text"
    HTML = "html"
    MARKDOWN = "markdown"
    RICH_TEXT = "rich_text"
    JSON = "json"

class DeliveryAttempt(BaseModel):
    attempt_number: int
    attempted_at: datetime
    status: NotificationStatus
    response_code: Optional[int] = None
    response_message: Optional[str] = None
    error_details: Optional[str] = None
    retry_after: Optional[datetime] = None

class NotificationTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Template content
    subject: Optional[str] = None  # For email/push notifications
    title: Optional[str] = None   # For in-app/push notifications
    body: str
    format: MessageFormat = MessageFormat.PLAIN_TEXT
    
    # Channel-specific content
    channel_variations: Dict[NotificationChannel, Dict[str, str]] = {}
    
    # Variables and personalization
    variables: List[str] = []  # List of variable names like {name}, {date}, etc.
    sample_data: Dict[str, str] = {}  # Sample values for testing
    
    # Template configuration
    category: str
    tags: List[str] = []
    supported_channels: List[NotificationChannel] = []
    
    # Localization
    language: str = "en"
    translations: Dict[str, Dict[str, str]] = {}  # language -> field -> translated text
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class NotificationPreference(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_type: str = "customer"  # "customer", "agent", "admin"
    
    # Channel preferences
    preferred_channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    blocked_channels: List[NotificationChannel] = []
    
    # Category preferences
    category_preferences: Dict[str, List[NotificationChannel]] = {}
    muted_categories: List[str] = []
    
    # Timing preferences
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"
    timezone: str = "UTC"
    max_daily_notifications: Optional[int] = None
    
    # Frequency preferences
    frequency_limits: Dict[str, int] = {}  # category -> max per day
    digest_preferences: Dict[str, str] = {}  # category -> "immediate", "hourly", "daily"
    
    # Contact information
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    push_token: Optional[str] = None
    slack_user_id: Optional[str] = None
    teams_user_id: Optional[str] = None
    
    # Status
    is_active: bool = True
    unsubscribed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Basic information
    title: Optional[str] = None
    subject: Optional[str] = None
    message: str
    format: MessageFormat = MessageFormat.PLAIN_TEXT
    
    # Targeting
    recipient_id: str
    recipient_type: str = "customer"  # "customer", "agent", "admin"
    recipient_info: Dict[str, str] = {}  # name, email, phone, etc.
    
    # Channel and delivery
    channel: NotificationChannel
    priority: NotificationPriority = NotificationPriority.NORMAL
    status: NotificationStatus = NotificationStatus.PENDING
    
    # Content and personalization
    template_id: Optional[str] = None
    template_variables: Dict[str, str] = {}
    personalized_content: Optional[str] = None
    
    # Scheduling
    trigger: NotificationTrigger = NotificationTrigger.MANUAL
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Delivery tracking
    delivery_attempts: List[DeliveryAttempt] = []
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    
    # Response tracking
    response_received: bool = False
    response_content: Optional[str] = None
    response_at: Optional[datetime] = None
    
    # Metadata
    category: str
    tags: List[str] = []
    source_system: Optional[str] = None  # "call_center", "leads", "scheduling", etc.
    reference_id: Optional[str] = None   # ID from source system
    
    # Campaign tracking
    campaign_id: Optional[str] = None
    batch_id: Optional[str] = None
    
    # Custom data
    custom_data: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class NotificationCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Campaign configuration
    template_id: str
    target_audience: Dict[str, Any] = {}  # Targeting criteria
    channels: List[NotificationChannel] = []
    
    # Scheduling
    schedule_type: str = "immediate"  # "immediate", "scheduled", "recurring"
    scheduled_at: Optional[datetime] = None
    timezone: str = "UTC"
    
    # Recurring configuration
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly"
    recurrence_end: Optional[datetime] = None
    
    # Content personalization
    dynamic_content: bool = True
    segmentation_rules: List[Dict[str, Any]] = []
    
    # Performance tracking
    total_recipients: int = 0
    sent_count: int = 0
    delivered_count: int = 0
    read_count: int = 0
    clicked_count: int = 0
    failed_count: int = 0
    
    # Campaign metrics
    delivery_rate: float = 0.0
    open_rate: float = 0.0
    click_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Status
    status: str = "draft"  # "draft", "scheduled", "sending", "completed", "paused", "cancelled"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    created_by: str
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)

class NotificationRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Trigger configuration
    trigger_event: str  # "lead_created", "appointment_scheduled", "call_completed", etc.
    trigger_conditions: Dict[str, Any] = {}
    
    # Notification configuration
    template_id: str
    channels: List[NotificationChannel] = []
    priority: NotificationPriority = NotificationPriority.NORMAL
    
    # Recipient targeting
    recipient_rules: Dict[str, Any] = {}  # Rules for determining recipients
    personalization_rules: Dict[str, str] = {}  # Variable mappings
    
    # Timing and delays
    delay_minutes: int = 0  # Delay before sending
    quiet_hours_respect: bool = True
    max_frequency_per_day: Optional[int] = None
    
    # Conditions and filters
    conditions: List[Dict[str, Any]] = []  # Additional conditions
    exclusion_rules: List[Dict[str, Any]] = []  # Rules to exclude sending
    
    # Status and control
    is_active: bool = True
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class NotificationProvider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    provider_type: NotificationChannel
    
    # Configuration
    config: Dict[str, str] = {}  # API keys, endpoints, etc.
    is_primary: bool = False
    is_active: bool = True
    
    # Rate limiting
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    
    # Performance metrics
    success_rate: float = 100.0
    average_delivery_time: float = 0.0  # seconds
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    # Status
    status: str = "active"  # "active", "degraded", "down", "maintenance"
    error_count_24h: int = 0
    
    created_at: datetime = Field(default_factory=datetime.now)

class NotificationAnalytics(BaseModel):
    time_period: str
    total_notifications: int
    sent_notifications: int
    delivered_notifications: int
    read_notifications: int
    failed_notifications: int
    
    # Performance metrics
    delivery_rate: float
    read_rate: float
    failure_rate: float
    average_delivery_time: float
    
    # Channel breakdown
    channel_performance: Dict[str, Dict[str, Any]] = {}
    
    # Category breakdown
    category_performance: Dict[str, Dict[str, Any]] = {}
    
    # Time-based analysis
    hourly_volume: List[Dict[str, Any]] = []
    daily_trends: List[Dict[str, Any]] = []
    
    # Provider performance
    provider_performance: Dict[str, Dict[str, Any]] = {}

# Sample data
SAMPLE_TEMPLATES = [
    NotificationTemplate(
        name="Appointment Reminder",
        description="Standard appointment reminder template",
        subject="Appointment Reminder - {appointment_type} on {date}",
        title="Upcoming Appointment",
        body="Hi {customer_name}, this is a friendly reminder about your {appointment_type} scheduled for {date} at {time}. Please reply to confirm your attendance.",
        format=MessageFormat.PLAIN_TEXT,
        channel_variations={
            NotificationChannel.EMAIL: {
                "body": "Dear {customer_name},\n\nThis is a friendly reminder about your upcoming {appointment_type} scheduled for {date} at {time}.\n\nPlease click here to confirm: {confirmation_link}\n\nBest regards,\n{agent_name}"
            },
            NotificationChannel.SMS: {
                "body": "Hi {customer_name}, reminder: {appointment_type} on {date} at {time}. Reply YES to confirm. {confirmation_link}"
            }
        },
        variables=["customer_name", "appointment_type", "date", "time", "agent_name", "confirmation_link"],
        sample_data={
            "customer_name": "John Doe",
            "appointment_type": "Product Demo",
            "date": "March 15, 2024",
            "time": "2:00 PM",
            "agent_name": "Sarah Johnson",
            "confirmation_link": "https://vocelio.com/confirm/123"
        },
        category="appointments",
        tags=["reminder", "appointment", "confirmation"],
        supported_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PUSH],
        created_by="system",
        usage_count=245
    ),
    NotificationTemplate(
        name="Lead Follow-up",
        description="Automated lead follow-up message",
        subject="Thank you for your interest in {product_name}",
        title="Follow-up Message",
        body="Thank you for your interest in {product_name}. We'd love to help you {primary_benefit}. Would you like to schedule a quick call to discuss your needs?",
        format=MessageFormat.PLAIN_TEXT,
        variables=["customer_name", "product_name", "primary_benefit", "agent_name", "contact_phone"],
        category="leads",
        tags=["follow-up", "lead", "sales"],
        supported_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
        created_by="sales_team",
        usage_count=167
    ),
    NotificationTemplate(
        name="Call Summary",
        description="Post-call summary notification",
        subject="Call Summary - {call_date}",
        title="Call Completed",
        body="Your call with {agent_name} has been completed. Duration: {duration} minutes. Next steps: {next_steps}. Rate your experience: {rating_link}",
        format=MessageFormat.PLAIN_TEXT,
        variables=["customer_name", "agent_name", "call_date", "duration", "next_steps", "rating_link"],
        category="calls",
        tags=["summary", "post-call", "feedback"],
        supported_channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        created_by="system",
        usage_count=892
    )
]

SAMPLE_PREFERENCES = [
    NotificationPreference(
        user_id="customer_001",
        user_type="customer",
        preferred_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
        category_preferences={
            "appointments": [NotificationChannel.EMAIL, NotificationChannel.SMS],
            "leads": [NotificationChannel.EMAIL],
            "calls": [NotificationChannel.EMAIL]
        },
        quiet_hours_start="22:00",
        quiet_hours_end="08:00",
        timezone="US/Eastern",
        max_daily_notifications=10,
        email_address="john.doe@example.com",
        phone_number="+1-555-0123"
    ),
    NotificationPreference(
        user_id="agent_001",
        user_type="agent",
        preferred_channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP, NotificationChannel.EMAIL],
        category_preferences={
            "system": [NotificationChannel.PUSH, NotificationChannel.IN_APP],
            "leads": [NotificationChannel.IN_APP],
            "appointments": [NotificationChannel.PUSH]
        },
        max_daily_notifications=50,
        email_address="agent@vocelio.com",
        push_token="agent_push_token_123"
    )
]

SAMPLE_PROVIDERS = [
    NotificationProvider(
        name="SendGrid Email",
        provider_type=NotificationChannel.EMAIL,
        config={"api_key": "sendgrid_key", "from_email": "noreply@vocelio.com"},
        is_primary=True,
        rate_limit_per_minute=100,
        rate_limit_per_hour=5000,
        success_rate=99.2,
        average_delivery_time=2.3
    ),
    NotificationProvider(
        name="Twilio SMS",
        provider_type=NotificationChannel.SMS,
        config={"account_sid": "twilio_sid", "auth_token": "twilio_token", "from_number": "+1-800-VOCELIO"},
        is_primary=True,
        rate_limit_per_minute=50,
        rate_limit_per_hour=1000,
        success_rate=97.8,
        average_delivery_time=1.1
    ),
    NotificationProvider(
        name="Firebase Push",
        provider_type=NotificationChannel.PUSH,
        config={"server_key": "firebase_key", "project_id": "vocelio-notifications"},
        is_primary=True,
        rate_limit_per_minute=200,
        success_rate=95.5,
        average_delivery_time=0.8
    )
]

# Global storage
notifications: List[Notification] = []
templates: List[NotificationTemplate] = []
preferences: List[NotificationPreference] = []
campaigns: List[NotificationCampaign] = []
rules: List[NotificationRule] = []
providers: List[NotificationProvider] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global templates, preferences, providers
    
    templates.extend(SAMPLE_TEMPLATES)
    preferences.extend(SAMPLE_PREFERENCES)
    providers.extend(SAMPLE_PROVIDERS)
    
    # Create sample notifications
    sample_notifications = [
        Notification(
            title="Appointment Reminder",
            subject="Reminder: Product Demo Tomorrow",
            message="Hi John, this is a reminder about your product demo scheduled for tomorrow at 2:00 PM.",
            recipient_id="customer_001",
            recipient_info={"name": "John Doe", "email": "john.doe@example.com"},
            channel=NotificationChannel.EMAIL,
            priority=NotificationPriority.NORMAL,
            status=NotificationStatus.DELIVERED,
            template_id=templates[0].id,
            category="appointments",
            sent_at=datetime.now() - timedelta(hours=2),
            delivered_at=datetime.now() - timedelta(hours=2, minutes=5),
            tags=["reminder", "demo"]
        ),
        Notification(
            title="Lead Follow-up",
            message="Thank you for your interest in our AI calling solution. Would you like to schedule a call?",
            recipient_id="customer_002",
            recipient_info={"name": "Sarah Wilson", "phone": "+1-555-0456"},
            channel=NotificationChannel.SMS,
            priority=NotificationPriority.HIGH,
            status=NotificationStatus.SENT,
            template_id=templates[1].id,
            category="leads",
            sent_at=datetime.now() - timedelta(minutes=30),
            tags=["follow-up", "sales"]
        )
    ]
    
    notifications.extend(sample_notifications)
    
    # Create sample campaign
    sample_campaign = NotificationCampaign(
        name="Q4 Product Update Campaign",
        description="Notify all customers about new Q4 product features",
        template_id=templates[2].id,
        channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH],
        schedule_type="scheduled",
        scheduled_at=datetime.now() + timedelta(days=1),
        total_recipients=1250,
        sent_count=1180,
        delivered_count=1156,
        read_count=734,
        clicked_count=198,
        delivery_rate=98.0,
        open_rate=63.5,
        click_rate=17.1,
        status="completed",
        created_by="marketing_team",
        tags=["product_update", "q4", "features"]
    )
    
    campaigns.append(sample_campaign)
    
    # Create sample notification rule
    sample_rule = NotificationRule(
        name="Appointment Reminder Rule",
        description="Send reminder 24 hours before scheduled appointments",
        trigger_event="appointment_scheduled",
        template_id=templates[0].id,
        channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
        priority=NotificationPriority.NORMAL,
        delay_minutes=0,
        recipient_rules={"type": "appointment_customer"},
        personalization_rules={
            "customer_name": "appointment.customer_name",
            "appointment_type": "appointment.type",
            "date": "appointment.date",
            "time": "appointment.time"
        },
        is_active=True,
        execution_count=156,
        created_by="system"
    )
    
    rules.append(sample_rule)
    
    logger.info("Sample notifications data initialized successfully")

async def personalize_message(template: NotificationTemplate, variables: Dict[str, str], channel: NotificationChannel) -> Dict[str, str]:
    """Personalize message content using template and variables"""
    
    # Get channel-specific content or use default
    if channel in template.channel_variations:
        content = template.channel_variations[channel]
        subject = content.get("subject", template.subject)
        title = content.get("title", template.title)
        body = content.get("body", template.body)
    else:
        subject = template.subject
        title = template.title
        body = template.body
    
    # Replace variables in all content fields
    for var_name, var_value in variables.items():
        placeholder = f"{{{var_name}}}"
        if subject:
            subject = subject.replace(placeholder, str(var_value))
        if title:
            title = title.replace(placeholder, str(var_value))
        if body:
            body = body.replace(placeholder, str(var_value))
    
    return {
        "subject": subject,
        "title": title,
        "body": body
    }

async def check_delivery_preferences(user_id: str, channel: NotificationChannel, category: str) -> bool:
    """Check if user allows notifications for this channel and category"""
    
    preference = next((p for p in preferences if p.user_id == user_id), None)
    if not preference or not preference.is_active:
        return True  # Default to allow if no preferences set
    
    # Check if channel is blocked
    if channel in preference.blocked_channels:
        return False
    
    # Check if category is muted
    if category in preference.muted_categories:
        return False
    
    # Check category-specific channel preferences
    if category in preference.category_preferences:
        allowed_channels = preference.category_preferences[category]
        return channel in allowed_channels
    
    # Check general preferred channels
    return channel in preference.preferred_channels

async def is_quiet_hours(user_id: str) -> bool:
    """Check if current time is within user's quiet hours"""
    
    preference = next((p for p in preferences if p.user_id == user_id), None)
    if not preference or not preference.quiet_hours_start or not preference.quiet_hours_end:
        return False
    
    # Simple quiet hours check (doesn't handle timezone properly for demo)
    current_hour = datetime.now().hour
    quiet_start = int(preference.quiet_hours_start.split(":")[0])
    quiet_end = int(preference.quiet_hours_end.split(":")[0])
    
    if quiet_start > quiet_end:  # Overnight quiet hours
        return current_hour >= quiet_start or current_hour < quiet_end
    else:
        return quiet_start <= current_hour < quiet_end

async def send_notification(notification: Notification) -> bool:
    """Send notification through appropriate provider"""
    
    try:
        # Find provider for channel
        provider = next((p for p in providers if p.provider_type == notification.channel and p.is_active), None)
        if not provider:
            raise Exception(f"No active provider found for channel {notification.channel}")
        
        # Create delivery attempt
        attempt = DeliveryAttempt(
            attempt_number=len(notification.delivery_attempts) + 1,
            attempted_at=datetime.now(),
            status=NotificationStatus.SENDING
        )
        
        notification.delivery_attempts.append(attempt)
        notification.status = NotificationStatus.SENDING
        
        # Mock sending logic based on channel
        await asyncio.sleep(0.1)  # Simulate network delay
        
        if notification.channel == NotificationChannel.EMAIL:
            logger.info(f"Sending email to {notification.recipient_info.get('email')}: {notification.subject}")
        elif notification.channel == NotificationChannel.SMS:
            logger.info(f"Sending SMS to {notification.recipient_info.get('phone')}: {notification.message[:50]}...")
        elif notification.channel == NotificationChannel.PUSH:
            logger.info(f"Sending push notification: {notification.title}")
        elif notification.channel == NotificationChannel.IN_APP:
            logger.info(f"Creating in-app notification for user {notification.recipient_id}")
        
        # Update attempt and notification status
        attempt.status = NotificationStatus.DELIVERED
        attempt.response_code = 200
        attempt.response_message = "Successfully delivered"
        
        notification.status = NotificationStatus.DELIVERED
        notification.sent_at = datetime.now()
        notification.delivered_at = datetime.now()
        
        # Update provider metrics
        provider.last_success = datetime.now()
        
        logger.info(f"Notification {notification.id} delivered successfully via {notification.channel}")
        return True
        
    except Exception as e:
        # Handle delivery failure
        if notification.delivery_attempts:
            notification.delivery_attempts[-1].status = NotificationStatus.FAILED
            notification.delivery_attempts[-1].error_details = str(e)
        
        notification.status = NotificationStatus.FAILED
        
        # Update provider metrics
        if provider:
            provider.error_count_24h += 1
            provider.last_failure = datetime.now()
        
        logger.error(f"Failed to send notification {notification.id}: {e}")
        return False

async def process_notification_queue():
    """Process pending notifications in the queue"""
    
    pending_notifications = [n for n in notifications if n.status == NotificationStatus.PENDING]
    
    for notification in pending_notifications:
        # Check if scheduled time has arrived
        if notification.scheduled_at and notification.scheduled_at > datetime.now():
            continue
        
        # Check if notification has expired
        if notification.expires_at and notification.expires_at <= datetime.now():
            notification.status = NotificationStatus.CANCELLED
            continue
        
        # Check user preferences
        if not await check_delivery_preferences(notification.recipient_id, notification.channel, notification.category):
            notification.status = NotificationStatus.CANCELLED
            logger.info(f"Notification {notification.id} cancelled due to user preferences")
            continue
        
        # Check quiet hours
        if await is_quiet_hours(notification.recipient_id):
            # Reschedule for later
            preference = next((p for p in preferences if p.user_id == notification.recipient_id), None)
            if preference and preference.quiet_hours_end:
                tomorrow = datetime.now().replace(hour=int(preference.quiet_hours_end.split(":")[0]), minute=0, second=0, microsecond=0)
                if tomorrow <= datetime.now():
                    tomorrow += timedelta(days=1)
                notification.scheduled_at = tomorrow
            continue
        
        # Send notification
        await send_notification(notification)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    
    # Start background task for notification processing
    async def notification_processor():
        while True:
            await process_notification_queue()
            await asyncio.sleep(10)  # Check every 10 seconds
    
    processor_task = asyncio.create_task(notification_processor())
    
    yield
    
    # Shutdown
    processor_task.cancel()

# FastAPI app
app = FastAPI(
    title="Notifications Service",
    description="Comprehensive multi-channel notification and communication management for Vocelio AI Call Center",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "notifications",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Notification Management Endpoints
@app.get("/notifications", response_model=List[Notification])
async def get_notifications(
    status: Optional[NotificationStatus] = None,
    channel: Optional[NotificationChannel] = None,
    priority: Optional[NotificationPriority] = None,
    recipient_id: Optional[str] = None,
    category: Optional[str] = None,
    template_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",  # "created_at", "sent_at", "priority"
    limit: int = 50,
    offset: int = 0
):
    """Get notifications with filtering and sorting options"""
    
    filtered_notifications = notifications.copy()
    
    # Apply filters
    if status:
        filtered_notifications = [n for n in filtered_notifications if n.status == status]
    
    if channel:
        filtered_notifications = [n for n in filtered_notifications if n.channel == channel]
    
    if priority:
        filtered_notifications = [n for n in filtered_notifications if n.priority == priority]
    
    if recipient_id:
        filtered_notifications = [n for n in filtered_notifications if n.recipient_id == recipient_id]
    
    if category:
        filtered_notifications = [n for n in filtered_notifications if n.category == category]
    
    if template_id:
        filtered_notifications = [n for n in filtered_notifications if n.template_id == template_id]
    
    if campaign_id:
        filtered_notifications = [n for n in filtered_notifications if n.campaign_id == campaign_id]
    
    if search:
        search_lower = search.lower()
        filtered_notifications = [
            n for n in filtered_notifications
            if (search_lower in n.message.lower() or 
                (n.subject and search_lower in n.subject.lower()) or
                (n.title and search_lower in n.title.lower()))
        ]
    
    # Apply sorting
    if sort_by == "created_at":
        filtered_notifications.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "sent_at":
        filtered_notifications.sort(key=lambda x: x.sent_at or datetime.min, reverse=True)
    elif sort_by == "priority":
        priority_order = {NotificationPriority.CRITICAL: 5, NotificationPriority.URGENT: 4, 
                         NotificationPriority.HIGH: 3, NotificationPriority.NORMAL: 2, NotificationPriority.LOW: 1}
        filtered_notifications.sort(key=lambda x: priority_order.get(x.priority, 0), reverse=True)
    
    # Apply pagination
    return filtered_notifications[offset:offset + limit]

@app.get("/notifications/{notification_id}", response_model=Notification)
async def get_notification(notification_id: str):
    """Get a specific notification by ID"""
    notification = next((n for n in notifications if n.id == notification_id), None)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.post("/notifications", response_model=Notification)
async def create_notification(notification_data: Notification):
    """Create a new notification"""
    
    # Personalize content if template is used
    if notification_data.template_id:
        template = next((t for t in templates if t.id == notification_data.template_id), None)
        if template:
            personalized = await personalize_message(template, notification_data.template_variables, notification_data.channel)
            notification_data.subject = personalized["subject"]
            notification_data.title = personalized["title"]
            notification_data.personalized_content = personalized["body"]
            
            # Update template usage
            template.usage_count += 1
            template.last_used = datetime.now()
    
    notifications.append(notification_data)
    logger.info(f"Created notification {notification_data.id} for {notification_data.recipient_id}")
    return notification_data

@app.post("/notifications/send")
async def send_notification_immediately(
    recipient_id: str,
    channel: NotificationChannel,
    message: str,
    subject: Optional[str] = None,
    title: Optional[str] = None,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    category: str = "general",
    template_id: Optional[str] = None,
    template_variables: Optional[Dict[str, str]] = None
):
    """Send a notification immediately"""
    
    # Get recipient info from preferences
    preference = next((p for p in preferences if p.user_id == recipient_id), None)
    recipient_info = {}
    if preference:
        recipient_info = {
            "email": preference.email_address,
            "phone": preference.phone_number
        }
    
    notification = Notification(
        subject=subject,
        title=title,
        message=message,
        recipient_id=recipient_id,
        recipient_info=recipient_info,
        channel=channel,
        priority=priority,
        category=category,
        template_id=template_id,
        template_variables=template_variables or {},
        trigger=NotificationTrigger.API
    )
    
    # Personalize if template provided
    if template_id:
        template = next((t for t in templates if t.id == template_id), None)
        if template:
            personalized = await personalize_message(template, template_variables or {}, channel)
            notification.subject = personalized["subject"]
            notification.title = personalized["title"]
            notification.personalized_content = personalized["body"]
    
    notifications.append(notification)
    
    # Send immediately
    success = await send_notification(notification)
    
    return {
        "notification_id": notification.id,
        "status": "sent" if success else "failed",
        "message": "Notification sent successfully" if success else "Failed to send notification"
    }

@app.put("/notifications/{notification_id}/status")
async def update_notification_status(notification_id: str, status: NotificationStatus):
    """Update notification status"""
    notification = next((n for n in notifications if n.id == notification_id), None)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    old_status = notification.status
    notification.status = status
    notification.updated_at = datetime.now()
    
    # Update timestamps based on status
    if status == NotificationStatus.READ and not notification.read_at:
        notification.read_at = datetime.now()
    elif status == NotificationStatus.DELIVERED and not notification.delivered_at:
        notification.delivered_at = datetime.now()
    
    logger.info(f"Updated notification {notification_id} status from {old_status} to {status}")
    return {"message": f"Notification status updated to {status}"}

@app.put("/notifications/{notification_id}/clicked")
async def mark_notification_clicked(notification_id: str):
    """Mark notification as clicked"""
    notification = next((n for n in notifications if n.id == notification_id), None)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.clicked_at = datetime.now()
    notification.updated_at = datetime.now()
    
    if notification.status == NotificationStatus.DELIVERED:
        notification.status = NotificationStatus.READ
    
    logger.info(f"Marked notification {notification_id} as clicked")
    return {"message": "Notification marked as clicked"}

# Template Management Endpoints
@app.get("/templates", response_model=List[NotificationTemplate])
async def get_templates(
    category: Optional[str] = None,
    channel: Optional[NotificationChannel] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Get notification templates"""
    
    filtered_templates = templates.copy()
    
    if category:
        filtered_templates = [t for t in filtered_templates if t.category == category]
    
    if channel:
        filtered_templates = [t for t in filtered_templates if channel in t.supported_channels]
    
    if is_active is not None:
        filtered_templates = [t for t in filtered_templates if t.is_active == is_active]
    
    if search:
        search_lower = search.lower()
        filtered_templates = [
            t for t in filtered_templates
            if (search_lower in t.name.lower() or 
                search_lower in t.description.lower() or
                search_lower in t.body.lower())
        ]
    
    # Sort by usage count
    filtered_templates.sort(key=lambda x: x.usage_count, reverse=True)
    
    return filtered_templates

@app.get("/templates/{template_id}", response_model=NotificationTemplate)
async def get_template(template_id: str):
    """Get a specific template"""
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.post("/templates", response_model=NotificationTemplate)
async def create_template(template_data: NotificationTemplate):
    """Create a new notification template"""
    templates.append(template_data)
    logger.info(f"Created template: {template_data.name}")
    return template_data

@app.put("/templates/{template_id}", response_model=NotificationTemplate)
async def update_template(template_id: str, template_data: NotificationTemplate):
    """Update an existing template"""
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update fields
    for field, value in template_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(template, field, value)
    
    template.updated_at = datetime.now()
    logger.info(f"Updated template: {template.name}")
    return template

@app.post("/templates/{template_id}/test")
async def test_template(
    template_id: str,
    channel: NotificationChannel,
    test_variables: Optional[Dict[str, str]] = None
):
    """Test a template with sample data"""
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Use provided variables or sample data
    variables = test_variables or template.sample_data
    
    # Personalize message
    personalized = await personalize_message(template, variables, channel)
    
    return {
        "template_id": template_id,
        "channel": channel.value,
        "variables_used": variables,
        "personalized_content": personalized
    }

# Preference Management Endpoints
@app.get("/preferences/{user_id}", response_model=NotificationPreference)
async def get_user_preferences(user_id: str):
    """Get notification preferences for a user"""
    preference = next((p for p in preferences if p.user_id == user_id), None)
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return preference

@app.post("/preferences", response_model=NotificationPreference)
async def create_user_preferences(preference_data: NotificationPreference):
    """Create notification preferences for a user"""
    # Check if preferences already exist
    existing = next((p for p in preferences if p.user_id == preference_data.user_id), None)
    if existing:
        raise HTTPException(status_code=409, detail="User preferences already exist")
    
    preferences.append(preference_data)
    logger.info(f"Created preferences for user {preference_data.user_id}")
    return preference_data

@app.put("/preferences/{user_id}", response_model=NotificationPreference)
async def update_user_preferences(user_id: str, preference_data: NotificationPreference):
    """Update notification preferences for a user"""
    preference = next((p for p in preferences if p.user_id == user_id), None)
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    # Update fields
    for field, value in preference_data.dict(exclude_unset=True).items():
        if field not in ["id", "user_id"]:
            setattr(preference, field, value)
    
    preference.updated_at = datetime.now()
    logger.info(f"Updated preferences for user {user_id}")
    return preference

@app.put("/preferences/{user_id}/unsubscribe")
async def unsubscribe_user(user_id: str, categories: Optional[List[str]] = None):
    """Unsubscribe user from notifications"""
    preference = next((p for p in preferences if p.user_id == user_id), None)
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    if categories:
        # Unsubscribe from specific categories
        preference.muted_categories.extend([cat for cat in categories if cat not in preference.muted_categories])
    else:
        # Unsubscribe from all notifications
        preference.is_active = False
        preference.unsubscribed_at = datetime.now()
    
    preference.updated_at = datetime.now()
    logger.info(f"Updated unsubscribe settings for user {user_id}")
    return {"message": "Unsubscribe preferences updated"}

# Campaign Management Endpoints
@app.get("/campaigns", response_model=List[NotificationCampaign])
async def get_campaigns(status: Optional[str] = None):
    """Get notification campaigns"""
    filtered_campaigns = campaigns.copy()
    
    if status:
        filtered_campaigns = [c for c in filtered_campaigns if c.status == status]
    
    # Sort by created date
    filtered_campaigns.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_campaigns

@app.get("/campaigns/{campaign_id}", response_model=NotificationCampaign)
async def get_campaign(campaign_id: str):
    """Get a specific campaign"""
    campaign = next((c for c in campaigns if c.id == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@app.post("/campaigns", response_model=NotificationCampaign)
async def create_campaign(campaign_data: NotificationCampaign):
    """Create a new notification campaign"""
    campaigns.append(campaign_data)
    logger.info(f"Created campaign: {campaign_data.name}")
    return campaign_data

@app.put("/campaigns/{campaign_id}/status")
async def update_campaign_status(campaign_id: str, status: str):
    """Update campaign status"""
    campaign = next((c for c in campaigns if c.id == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    old_status = campaign.status
    campaign.status = status
    
    if status == "sending" and not campaign.started_at:
        campaign.started_at = datetime.now()
    elif status == "completed" and not campaign.completed_at:
        campaign.completed_at = datetime.now()
    
    logger.info(f"Updated campaign {campaign_id} status from {old_status} to {status}")
    return {"message": f"Campaign status updated to {status}"}

# Provider Management Endpoints
@app.get("/providers", response_model=List[NotificationProvider])
async def get_providers(provider_type: Optional[NotificationChannel] = None, is_active: Optional[bool] = None):
    """Get notification providers"""
    filtered_providers = providers.copy()
    
    if provider_type:
        filtered_providers = [p for p in filtered_providers if p.provider_type == provider_type]
    
    if is_active is not None:
        filtered_providers = [p for p in filtered_providers if p.is_active == is_active]
    
    return filtered_providers

@app.post("/providers", response_model=NotificationProvider)
async def create_provider(provider_data: NotificationProvider):
    """Create a new notification provider"""
    providers.append(provider_data)
    logger.info(f"Created provider: {provider_data.name}")
    return provider_data

@app.put("/providers/{provider_id}/status")
async def update_provider_status(provider_id: str, status: str):
    """Update provider status"""
    provider = next((p for p in providers if p.id == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider.status = status
    logger.info(f"Updated provider {provider_id} status to {status}")
    return {"message": f"Provider status updated to {status}"}

# Analytics Endpoints
@app.get("/analytics/overview")
async def get_notifications_analytics():
    """Get comprehensive notifications analytics"""
    
    total_notifications = len(notifications)
    sent_notifications = len([n for n in notifications if n.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]])
    delivered_notifications = len([n for n in notifications if n.status == NotificationStatus.DELIVERED])
    read_notifications = len([n for n in notifications if n.read_at is not None])
    failed_notifications = len([n for n in notifications if n.status == NotificationStatus.FAILED])
    
    # Calculate rates
    delivery_rate = (delivered_notifications / sent_notifications * 100) if sent_notifications > 0 else 0
    read_rate = (read_notifications / delivered_notifications * 100) if delivered_notifications > 0 else 0
    failure_rate = (failed_notifications / total_notifications * 100) if total_notifications > 0 else 0
    
    # Channel breakdown
    channel_stats = {}
    for channel in NotificationChannel:
        channel_notifications = [n for n in notifications if n.channel == channel]
        if channel_notifications:
            delivered = len([n for n in channel_notifications if n.status == NotificationStatus.DELIVERED])
            channel_stats[channel.value] = {
                "total": len(channel_notifications),
                "delivered": delivered,
                "delivery_rate": (delivered / len(channel_notifications) * 100) if channel_notifications else 0
            }
    
    # Category breakdown
    category_stats = {}
    categories = list(set(n.category for n in notifications))
    for category in categories:
        category_notifications = [n for n in notifications if n.category == category]
        delivered = len([n for n in category_notifications if n.status == NotificationStatus.DELIVERED])
        category_stats[category] = {
            "total": len(category_notifications),
            "delivered": delivered,
            "delivery_rate": (delivered / len(category_notifications) * 100) if category_notifications else 0
        }
    
    # Recent activity
    recent_notifications = len([n for n in notifications if n.created_at > datetime.now() - timedelta(hours=24)])
    active_campaigns = len([c for c in campaigns if c.status in ["scheduled", "sending"]])
    
    return {
        "summary": {
            "total_notifications": total_notifications,
            "sent_notifications": sent_notifications,
            "delivered_notifications": delivered_notifications,
            "read_notifications": read_notifications,
            "failed_notifications": failed_notifications,
            "active_templates": len([t for t in templates if t.is_active]),
            "active_campaigns": active_campaigns,
            "registered_providers": len(providers)
        },
        "performance_metrics": {
            "delivery_rate": round(delivery_rate, 1),
            "read_rate": round(read_rate, 1),
            "failure_rate": round(failure_rate, 1),
            "average_delivery_time": 2.1,  # Mock data
            "click_through_rate": 15.7  # Mock data
        },
        "channel_performance": channel_stats,
        "category_performance": category_stats,
        "recent_activity": {
            "notifications_24h": recent_notifications,
            "campaigns_active": active_campaigns,
            "templates_used_24h": len(set(n.template_id for n in notifications if n.template_id and n.created_at > datetime.now() - timedelta(hours=24))),
            "providers_healthy": len([p for p in providers if p.status == "active"])
        },
        "provider_health": {
            provider.name: {
                "status": provider.status,
                "success_rate": provider.success_rate,
                "error_count_24h": provider.error_count_24h
            }
            for provider in providers
        }
    }

@app.get("/analytics/trends")
async def get_notification_trends(days: int = 30):
    """Get notification trends over time"""
    
    trend_data = []
    for i in range(days, 0, -1):
        date_obj = datetime.now() - timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Calculate daily metrics (simplified for demo)
        daily_notifications = len([n for n in notifications if n.created_at.date() == date_obj.date()])
        daily_delivered = len([n for n in notifications if n.delivered_at and n.delivered_at.date() == date_obj.date()])
        
        trend_data.append({
            "date": date_str,
            "notifications_sent": max(0, daily_notifications + (i % 5)),  # Add variation
            "notifications_delivered": max(0, daily_delivered + (i % 4)),
            "read_rate": min(100, 65 + (i % 20)),
            "failure_rate": max(0, 5 - (i % 8))
        })
    
    return {
        "period_days": days,
        "trend_data": trend_data,
        "summary": {
            "total_sent": sum(d["notifications_sent"] for d in trend_data),
            "total_delivered": sum(d["notifications_delivered"] for d in trend_data),
            "average_read_rate": sum(d["read_rate"] for d in trend_data) / len(trend_data),
            "average_failure_rate": sum(d["failure_rate"] for d in trend_data) / len(trend_data)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)
