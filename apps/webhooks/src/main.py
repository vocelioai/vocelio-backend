"""
Webhooks Service - Vocelio AI Call Center
Comprehensive webhook management and event delivery system
"""

# Add parent directories to Python path for Docker compatibility
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import hmac
import aiohttp
import time
from decimal import Decimal
import base64
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Webhook Models
class WebhookEvent(str, Enum):
    # Call Center Events
    CALL_STARTED = "call.started"
    CALL_ENDED = "call.ended"
    CALL_ANSWERED = "call.answered"
    CALL_MISSED = "call.missed"
    CALL_TRANSFERRED = "call.transferred"
    CALL_RECORDING_AVAILABLE = "call.recording_available"
    
    # Lead Events
    LEAD_CREATED = "lead.created"
    LEAD_UPDATED = "lead.updated"
    LEAD_CONVERTED = "lead.converted"
    LEAD_LOST = "lead.lost"
    LEAD_ASSIGNED = "lead.assigned"
    
    # Appointment Events
    APPOINTMENT_SCHEDULED = "appointment.scheduled"
    APPOINTMENT_CONFIRMED = "appointment.confirmed"
    APPOINTMENT_CANCELLED = "appointment.cancelled"
    APPOINTMENT_COMPLETED = "appointment.completed"
    APPOINTMENT_RESCHEDULED = "appointment.rescheduled"
    APPOINTMENT_REMINDER_SENT = "appointment.reminder_sent"
    
    # Agent Events
    AGENT_ONLINE = "agent.online"
    AGENT_OFFLINE = "agent.offline"
    AGENT_BUSY = "agent.busy"
    AGENT_AVAILABLE = "agent.available"
    AGENT_PERFORMANCE_UPDATED = "agent.performance_updated"
    
    # Campaign Events
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_COMPLETED = "campaign.completed"
    CAMPAIGN_PAUSED = "campaign.paused"
    CAMPAIGN_PERFORMANCE_UPDATED = "campaign.performance_updated"
    
    # Notification Events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_DELIVERED = "notification.delivered"
    NOTIFICATION_CLICKED = "notification.clicked"
    NOTIFICATION_FAILED = "notification.failed"
    
    # System Events
    SYSTEM_HEALTH_ALERT = "system.health_alert"
    SYSTEM_MAINTENANCE = "system.maintenance"
    SYSTEM_ERROR = "system.error"
    SYSTEM_BACKUP_COMPLETED = "system.backup_completed"
    
    # Integration Events
    CRM_SYNC_COMPLETED = "crm.sync_completed"
    CRM_SYNC_FAILED = "crm.sync_failed"
    API_RATE_LIMIT_EXCEEDED = "api.rate_limit_exceeded"
    API_ERROR = "api.error"
    
    # Custom Events
    CUSTOM_EVENT = "custom.event"

class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class SignatureMethod(str, Enum):
    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA1 = "hmac_sha1"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    API_KEY = "api_key"

class RetryPolicy(BaseModel):
    enabled: bool = True
    max_attempts: int = 5
    initial_delay_seconds: int = 1
    max_delay_seconds: int = 300
    backoff_multiplier: float = 2.0
    retry_on_status_codes: List[int] = [408, 429, 500, 502, 503, 504]

class WebhookFilter(BaseModel):
    field_path: str  # e.g., "data.lead.status", "event_type"
    operator: str = "equals"  # "equals", "not_equals", "contains", "starts_with", "in", "regex"
    value: Union[str, int, float, bool, List[Any]]
    case_sensitive: bool = True

class WebhookTransformation(BaseModel):
    enabled: bool = False
    template: Optional[str] = None  # Jinja2 template for transforming payload
    headers_template: Optional[Dict[str, str]] = None  # Transform headers
    custom_script: Optional[str] = None  # Python script for custom transformations

class DeliveryAttempt(BaseModel):
    attempt_number: int
    attempted_at: datetime
    status: DeliveryStatus
    response_status_code: Optional[int] = None
    response_headers: Dict[str, str] = {}
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: int = 0
    next_retry_at: Optional[datetime] = None

class WebhookEndpoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    url: HttpUrl
    
    # Configuration
    http_method: HttpMethod = HttpMethod.POST
    status: WebhookStatus = WebhookStatus.ACTIVE
    
    # Event filtering
    events: List[WebhookEvent] = []
    event_filters: List[WebhookFilter] = []
    
    # Security
    secret: Optional[str] = None
    signature_method: Optional[SignatureMethod] = None
    custom_headers: Dict[str, str] = {}
    
    # Delivery options
    timeout_seconds: int = 30
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    content_type: str = "application/json"
    
    # Transformation
    transformation: WebhookTransformation = Field(default_factory=WebhookTransformation)
    
    # Monitoring
    success_count: int = 0
    failure_count: int = 0
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    last_delivery_attempt: Optional[datetime] = None
    
    # Rate limiting
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    
    # Metadata
    tags: List[str] = []
    environment: str = "production"  # "development", "staging", "production"
    owner: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class WebhookDelivery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    webhook_id: str
    endpoint_url: str
    
    # Event data
    event_type: WebhookEvent
    event_id: str
    event_timestamp: datetime
    payload: Dict[str, Any]
    
    # Delivery tracking
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempts: List[DeliveryAttempt] = []
    
    # Processing
    filtered: bool = False  # True if event was filtered out
    transformed: bool = False  # True if payload was transformed
    
    # Timing
    scheduled_at: datetime = Field(default_factory=datetime.now)
    first_attempt_at: Optional[datetime] = None
    last_attempt_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Response data
    final_response_status: Optional[int] = None
    final_response_body: Optional[str] = None
    
    # Metadata
    source_service: Optional[str] = None
    user_agent: str = "Vocelio-Webhooks/1.0"
    created_at: datetime = Field(default_factory=datetime.now)

class WebhookSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Target configuration
    endpoint_id: str
    events: List[WebhookEvent] = []
    
    # Filtering and transformation
    filters: List[WebhookFilter] = []
    transformation_enabled: bool = False
    
    # Status
    is_active: bool = True
    paused_until: Optional[datetime] = None
    
    # Monitoring
    delivery_count: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class WebhookTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Template configuration
    event_type: WebhookEvent
    payload_template: str  # Jinja2 template
    headers_template: Dict[str, str] = {}
    
    # Sample data
    sample_payload: Dict[str, Any] = {}
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class WebhookAnalytics(BaseModel):
    time_period: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    average_response_time: float
    success_rate: float
    
    # Breakdown by endpoint
    endpoint_performance: Dict[str, Dict[str, Any]] = {}
    
    # Breakdown by event type
    event_performance: Dict[str, Dict[str, Any]] = {}
    
    # Error analysis
    error_breakdown: Dict[str, int] = {}
    status_code_breakdown: Dict[str, int] = {}
    
    # Trends
    hourly_volume: List[Dict[str, Any]] = []
    daily_trends: List[Dict[str, Any]] = []

# Sample data
SAMPLE_ENDPOINTS = [
    WebhookEndpoint(
        name="CRM Lead Sync",
        description="Sync lead data to external CRM system",
        url="https://api.crm-system.com/webhooks/leads",
        events=[WebhookEvent.LEAD_CREATED, WebhookEvent.LEAD_UPDATED, WebhookEvent.LEAD_CONVERTED],
        secret="crm_webhook_secret_123",
        signature_method=SignatureMethod.HMAC_SHA256,
        custom_headers={"X-CRM-Source": "Vocelio", "Authorization": "Bearer crm_token_123"},
        success_count=1250,
        failure_count=23,
        last_success_at=datetime.now() - timedelta(minutes=15),
        owner="integration_team",
        tags=["crm", "leads", "sync"],
        environment="production"
    ),
    WebhookEndpoint(
        name="Analytics Dashboard",
        description="Send real-time analytics to dashboard",
        url="https://dashboard.vocelio.com/api/webhooks/analytics",
        events=[WebhookEvent.CALL_ENDED, WebhookEvent.CAMPAIGN_PERFORMANCE_UPDATED],
        secret="dashboard_secret_456",
        signature_method=SignatureMethod.HMAC_SHA256,
        success_count=5847,
        failure_count=12,
        last_success_at=datetime.now() - timedelta(minutes=2),
        owner="analytics_team",
        tags=["analytics", "dashboard", "real-time"],
        rate_limit_per_minute=100
    ),
    WebhookEndpoint(
        name="Slack Notifications",
        description="Send important alerts to Slack",
        url="https://hooks.slack.com/services/T123/B456/xyz789",
        events=[WebhookEvent.SYSTEM_HEALTH_ALERT, WebhookEvent.SYSTEM_ERROR],
        custom_headers={"Content-Type": "application/json"},
        success_count=156,
        failure_count=3,
        last_success_at=datetime.now() - timedelta(hours=1),
        owner="devops_team",
        tags=["slack", "alerts", "monitoring"]
    )
]

SAMPLE_TEMPLATES = [
    WebhookTemplate(
        name="Lead Created Template",
        description="Standard template for lead creation events",
        event_type=WebhookEvent.LEAD_CREATED,
        payload_template=json.dumps({
            "event": "lead_created",
            "timestamp": "{{ timestamp }}",
            "lead": {
                "id": "{{ lead.id }}",
                "name": "{{ lead.name }}",
                "email": "{{ lead.email }}",
                "phone": "{{ lead.phone }}",
                "source": "{{ lead.source }}",
                "score": "{{ lead.score }}"
            },
            "agent": {
                "id": "{{ agent.id }}",
                "name": "{{ agent.name }}"
            }
        }, indent=2),
        headers_template={"X-Event-Type": "lead.created", "X-Source": "vocelio"},
        sample_payload={
            "timestamp": "2025-08-05T17:30:00Z",
            "lead": {
                "id": "lead_123",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "source": "website",
                "score": 85
            },
            "agent": {
                "id": "agent_456",
                "name": "Sarah Johnson"
            }
        },
        usage_count=423,
        created_by="system"
    ),
    WebhookTemplate(
        name="Call Ended Template",
        description="Template for call completion events",
        event_type=WebhookEvent.CALL_ENDED,
        payload_template=json.dumps({
            "event": "call_ended",
            "timestamp": "{{ timestamp }}",
            "call": {
                "id": "{{ call.id }}",
                "duration": "{{ call.duration }}",
                "outcome": "{{ call.outcome }}",
                "recording_url": "{{ call.recording_url }}"
            },
            "customer": {
                "id": "{{ customer.id }}",
                "name": "{{ customer.name }}"
            },
            "agent": {
                "id": "{{ agent.id }}",
                "name": "{{ agent.name }}"
            }
        }, indent=2),
        usage_count=892,
        created_by="system"
    )
]

# Global storage
webhook_endpoints: List[WebhookEndpoint] = []
webhook_deliveries: List[WebhookDelivery] = []
webhook_subscriptions: List[WebhookSubscription] = []
webhook_templates: List[WebhookTemplate] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global webhook_endpoints, webhook_templates
    
    webhook_endpoints.extend(SAMPLE_ENDPOINTS)
    webhook_templates.extend(SAMPLE_TEMPLATES)
    
    # Create sample deliveries
    sample_deliveries = []
    for i in range(10):
        endpoint = webhook_endpoints[i % len(webhook_endpoints)]
        event_type = endpoint.events[0] if endpoint.events else WebhookEvent.CUSTOM_EVENT
        
        delivery = WebhookDelivery(
            webhook_id=endpoint.id,
            endpoint_url=str(endpoint.url),
            event_type=event_type,
            event_id=f"event_{i + 1}",
            event_timestamp=datetime.now() - timedelta(hours=i),
            payload={
                "event_type": event_type.value,
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "data": {"sample": "data", "index": i}
            },
            status=DeliveryStatus.DELIVERED if i % 4 != 0 else DeliveryStatus.FAILED,
            delivered_at=datetime.now() - timedelta(hours=i, minutes=5) if i % 4 != 0 else None,
            source_service="sample_service"
        )
        
        # Add sample delivery attempt
        attempt = DeliveryAttempt(
            attempt_number=1,
            attempted_at=datetime.now() - timedelta(hours=i, minutes=1),
            status=DeliveryStatus.DELIVERED if i % 4 != 0 else DeliveryStatus.FAILED,
            response_status_code=200 if i % 4 != 0 else 500,
            response_headers={"Content-Type": "application/json"},
            response_body='{"status": "success"}' if i % 4 != 0 else '{"error": "Internal server error"}',
            duration_ms=250 + (i * 10)
        )
        
        delivery.attempts.append(attempt)
        sample_deliveries.append(delivery)
    
    webhook_deliveries.extend(sample_deliveries)
    
    # Create sample subscription
    sample_subscription = WebhookSubscription(
        name="Lead Management Subscription",
        description="Subscribe to all lead-related events",
        endpoint_id=webhook_endpoints[0].id,
        events=[WebhookEvent.LEAD_CREATED, WebhookEvent.LEAD_UPDATED, WebhookEvent.LEAD_CONVERTED],
        delivery_count=1250,
        success_rate=98.2,
        average_response_time=245.5,
        created_by="integration_team"
    )
    
    webhook_subscriptions.append(sample_subscription)
    
    logger.info("Sample webhook data initialized successfully")

def generate_signature(payload: str, secret: str, method: SignatureMethod) -> str:
    """Generate webhook signature based on method"""
    
    if method == SignatureMethod.HMAC_SHA256:
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    elif method == SignatureMethod.HMAC_SHA1:
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()
        return f"sha1={signature}"
    
    elif method == SignatureMethod.API_KEY:
        return secret
    
    return ""

def apply_filters(payload: Dict[str, Any], filters: List[WebhookFilter]) -> bool:
    """Apply filters to determine if webhook should be delivered"""
    
    if not filters:
        return True
    
    for filter_rule in filters:
        field_value = get_nested_value(payload, filter_rule.field_path)
        
        if filter_rule.operator == "equals":
            if field_value != filter_rule.value:
                return False
        elif filter_rule.operator == "not_equals":
            if field_value == filter_rule.value:
                return False
        elif filter_rule.operator == "contains":
            if isinstance(field_value, str) and isinstance(filter_rule.value, str):
                if not filter_rule.case_sensitive:
                    if filter_rule.value.lower() not in field_value.lower():
                        return False
                else:
                    if filter_rule.value not in field_value:
                        return False
        elif filter_rule.operator == "in":
            if isinstance(filter_rule.value, list) and field_value not in filter_rule.value:
                return False
    
    return True

def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """Get nested value from dictionary using dot notation"""
    
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current

async def transform_payload(payload: Dict[str, Any], transformation: WebhookTransformation) -> Dict[str, Any]:
    """Transform webhook payload using template or custom script"""
    
    if not transformation.enabled:
        return payload
    
    # Simple template transformation (would use Jinja2 in production)
    if transformation.template:
        # Simplified transformation for demo
        return payload
    
    return payload

async def deliver_webhook(delivery: WebhookDelivery, endpoint: WebhookEndpoint) -> bool:
    """Deliver webhook to endpoint"""
    
    try:
        # Prepare payload
        payload_str = json.dumps(delivery.payload)
        
        # Prepare headers
        headers = {
            "Content-Type": endpoint.content_type,
            "User-Agent": delivery.user_agent,
            "X-Webhook-Event": delivery.event_type.value,
            "X-Webhook-ID": delivery.id,
            "X-Webhook-Timestamp": delivery.event_timestamp.isoformat()
        }
        
        # Add custom headers
        headers.update(endpoint.custom_headers)
        
        # Add signature if configured
        if endpoint.secret and endpoint.signature_method:
            signature = generate_signature(payload_str, endpoint.secret, endpoint.signature_method)
            if endpoint.signature_method in [SignatureMethod.HMAC_SHA256, SignatureMethod.HMAC_SHA1]:
                headers["X-Webhook-Signature"] = signature
            elif endpoint.signature_method == SignatureMethod.API_KEY:
                headers["X-API-Key"] = signature
        
        # Create delivery attempt
        attempt = DeliveryAttempt(
            attempt_number=len(delivery.attempts) + 1,
            attempted_at=datetime.now(),
            status=DeliveryStatus.SENDING
        )
        
        delivery.attempts.append(attempt)
        delivery.status = DeliveryStatus.SENDING
        delivery.last_attempt_at = datetime.now()
        
        if not delivery.first_attempt_at:
            delivery.first_attempt_at = datetime.now()
        
        # Mock HTTP request (would use aiohttp in production)
        start_time = time.time()
        
        # Simulate network request
        await asyncio.sleep(0.1 + (len(delivery.attempts) * 0.05))  # Simulate increasing delays
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Mock response based on endpoint health
        if endpoint.status == WebhookStatus.ACTIVE and len(delivery.attempts) <= 2:
            # Success
            response_status = 200
            response_body = '{"status": "success", "received": true}'
            attempt.status = DeliveryStatus.DELIVERED
            delivery.status = DeliveryStatus.DELIVERED
            delivery.delivered_at = datetime.now()
            
            # Update endpoint metrics
            endpoint.success_count += 1
            endpoint.last_success_at = datetime.now()
            endpoint.last_delivery_attempt = datetime.now()
            
        else:
            # Failure
            response_status = 500 if len(delivery.attempts) > 2 else 408
            response_body = '{"error": "Internal server error"}' if response_status == 500 else '{"error": "Request timeout"}'
            attempt.status = DeliveryStatus.FAILED
            delivery.status = DeliveryStatus.FAILED
            
            # Update endpoint metrics
            endpoint.failure_count += 1
            endpoint.last_failure_at = datetime.now()
            endpoint.last_delivery_attempt = datetime.now()
        
        # Update attempt details
        attempt.response_status_code = response_status
        attempt.response_body = response_body
        attempt.response_headers = {"Content-Type": "application/json", "Server": "mock-server"}
        attempt.duration_ms = duration_ms
        
        delivery.final_response_status = response_status
        delivery.final_response_body = response_body
        
        # Schedule retry if needed
        if response_status != 200 and len(delivery.attempts) < endpoint.retry_policy.max_attempts:
            delay = min(
                endpoint.retry_policy.initial_delay_seconds * (endpoint.retry_policy.backoff_multiplier ** (len(delivery.attempts) - 1)),
                endpoint.retry_policy.max_delay_seconds
            )
            attempt.next_retry_at = datetime.now() + timedelta(seconds=delay)
            delivery.status = DeliveryStatus.RETRYING
        
        logger.info(f"Webhook delivery {delivery.id} to {endpoint.url}: {response_status}")
        return response_status == 200
        
    except Exception as e:
        # Handle delivery error
        if delivery.attempts:
            delivery.attempts[-1].status = DeliveryStatus.FAILED
            delivery.attempts[-1].error_message = str(e)
        
        delivery.status = DeliveryStatus.FAILED
        endpoint.failure_count += 1
        endpoint.last_failure_at = datetime.now()
        
        logger.error(f"Failed to deliver webhook {delivery.id}: {e}")
        return False

async def process_webhook_queue():
    """Process pending webhook deliveries"""
    
    pending_deliveries = [
        d for d in webhook_deliveries 
        if d.status in [DeliveryStatus.PENDING, DeliveryStatus.RETRYING]
    ]
    
    for delivery in pending_deliveries:
        # Check if it's time to retry
        if delivery.status == DeliveryStatus.RETRYING:
            last_attempt = delivery.attempts[-1] if delivery.attempts else None
            if last_attempt and last_attempt.next_retry_at and last_attempt.next_retry_at > datetime.now():
                continue
        
        # Check if delivery has expired
        if delivery.expires_at and delivery.expires_at <= datetime.now():
            delivery.status = DeliveryStatus.EXPIRED
            continue
        
        # Find corresponding endpoint
        endpoint = next((e for e in webhook_endpoints if e.id == delivery.webhook_id), None)
        if not endpoint or endpoint.status != WebhookStatus.ACTIVE:
            delivery.status = DeliveryStatus.CANCELLED
            continue
        
        # Deliver webhook
        await deliver_webhook(delivery, endpoint)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    
    # Start background task for webhook processing
    async def webhook_processor():
        while True:
            await process_webhook_queue()
            await asyncio.sleep(5)  # Check every 5 seconds
    
    processor_task = asyncio.create_task(webhook_processor())
    
    yield
    
    # Shutdown
    processor_task.cancel()

# FastAPI app
app = FastAPI(
    title="Webhooks Service",
    description="Comprehensive webhook management and event delivery system for Vocelio AI Call Center",
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
        "service": "webhooks",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Webhook Endpoint Management
@app.get("/endpoints", response_model=List[WebhookEndpoint])
async def get_webhook_endpoints(
    status: Optional[WebhookStatus] = None,
    event: Optional[WebhookEvent] = None,
    environment: Optional[str] = None,
    search: Optional[str] = None
):
    """Get webhook endpoints with filtering"""
    
    filtered_endpoints = webhook_endpoints.copy()
    
    if status:
        filtered_endpoints = [e for e in filtered_endpoints if e.status == status]
    
    if event:
        filtered_endpoints = [e for e in filtered_endpoints if event in e.events]
    
    if environment:
        filtered_endpoints = [e for e in filtered_endpoints if e.environment == environment]
    
    if search:
        search_lower = search.lower()
        filtered_endpoints = [
            e for e in filtered_endpoints
            if (search_lower in e.name.lower() or 
                search_lower in e.description.lower() or
                search_lower in str(e.url).lower())
        ]
    
    # Sort by created date
    filtered_endpoints.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_endpoints

@app.get("/endpoints/{endpoint_id}", response_model=WebhookEndpoint)
async def get_webhook_endpoint(endpoint_id: str):
    """Get a specific webhook endpoint"""
    endpoint = next((e for e in webhook_endpoints if e.id == endpoint_id), None)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    return endpoint

@app.post("/endpoints", response_model=WebhookEndpoint)
async def create_webhook_endpoint(endpoint_data: WebhookEndpoint):
    """Create a new webhook endpoint"""
    webhook_endpoints.append(endpoint_data)
    logger.info(f"Created webhook endpoint: {endpoint_data.name}")
    return endpoint_data

@app.put("/endpoints/{endpoint_id}", response_model=WebhookEndpoint)
async def update_webhook_endpoint(endpoint_id: str, endpoint_data: WebhookEndpoint):
    """Update an existing webhook endpoint"""
    endpoint = next((e for e in webhook_endpoints if e.id == endpoint_id), None)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    # Update fields
    for field, value in endpoint_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(endpoint, field, value)
    
    endpoint.updated_at = datetime.now()
    logger.info(f"Updated webhook endpoint: {endpoint.name}")
    return endpoint

@app.delete("/endpoints/{endpoint_id}")
async def delete_webhook_endpoint(endpoint_id: str):
    """Delete a webhook endpoint"""
    global webhook_endpoints
    endpoint = next((e for e in webhook_endpoints if e.id == endpoint_id), None)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    webhook_endpoints = [e for e in webhook_endpoints if e.id != endpoint_id]
    logger.info(f"Deleted webhook endpoint: {endpoint.name}")
    return {"message": "Webhook endpoint deleted successfully"}

@app.put("/endpoints/{endpoint_id}/status")
async def update_endpoint_status(endpoint_id: str, status: WebhookStatus):
    """Update webhook endpoint status"""
    endpoint = next((e for e in webhook_endpoints if e.id == endpoint_id), None)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    old_status = endpoint.status
    endpoint.status = status
    endpoint.updated_at = datetime.now()
    
    logger.info(f"Updated endpoint {endpoint_id} status from {old_status} to {status}")
    return {"message": f"Endpoint status updated to {status}"}

@app.post("/endpoints/{endpoint_id}/test")
async def test_webhook_endpoint(endpoint_id: str, test_payload: Optional[Dict[str, Any]] = None):
    """Test a webhook endpoint with sample data"""
    endpoint = next((e for e in webhook_endpoints if e.id == endpoint_id), None)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    # Create test delivery
    test_delivery = WebhookDelivery(
        webhook_id=endpoint.id,
        endpoint_url=str(endpoint.url),
        event_type=endpoint.events[0] if endpoint.events else WebhookEvent.CUSTOM_EVENT,
        event_id="test_event",
        event_timestamp=datetime.now(),
        payload=test_payload or {"test": True, "timestamp": datetime.now().isoformat()},
        source_service="webhooks_test"
    )
    
    # Deliver immediately
    success = await deliver_webhook(test_delivery, endpoint)
    
    return {
        "test_successful": success,
        "delivery_id": test_delivery.id,
        "response_status": test_delivery.final_response_status,
        "response_body": test_delivery.final_response_body,
        "attempts": len(test_delivery.attempts)
    }

# Webhook Delivery Management
@app.get("/deliveries", response_model=List[WebhookDelivery])
async def get_webhook_deliveries(
    webhook_id: Optional[str] = None,
    status: Optional[DeliveryStatus] = None,
    event_type: Optional[WebhookEvent] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get webhook deliveries with filtering"""
    
    filtered_deliveries = webhook_deliveries.copy()
    
    if webhook_id:
        filtered_deliveries = [d for d in filtered_deliveries if d.webhook_id == webhook_id]
    
    if status:
        filtered_deliveries = [d for d in filtered_deliveries if d.status == status]
    
    if event_type:
        filtered_deliveries = [d for d in filtered_deliveries if d.event_type == event_type]
    
    # Sort by created date
    filtered_deliveries.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    return filtered_deliveries[offset:offset + limit]

@app.get("/deliveries/{delivery_id}", response_model=WebhookDelivery)
async def get_webhook_delivery(delivery_id: str):
    """Get a specific webhook delivery"""
    delivery = next((d for d in webhook_deliveries if d.id == delivery_id), None)
    if not delivery:
        raise HTTPException(status_code=404, detail="Webhook delivery not found")
    return delivery

@app.post("/deliveries/retry/{delivery_id}")
async def retry_webhook_delivery(delivery_id: str):
    """Retry a failed webhook delivery"""
    delivery = next((d for d in webhook_deliveries if d.id == delivery_id), None)
    if not delivery:
        raise HTTPException(status_code=404, detail="Webhook delivery not found")
    
    if delivery.status not in [DeliveryStatus.FAILED, DeliveryStatus.EXPIRED]:
        raise HTTPException(status_code=400, detail="Only failed or expired deliveries can be retried")
    
    # Reset delivery status for retry
    delivery.status = DeliveryStatus.PENDING
    delivery.expires_at = datetime.now() + timedelta(hours=24)  # Extend expiry
    
    logger.info(f"Queued delivery {delivery_id} for retry")
    return {"message": "Delivery queued for retry"}

# Event Publishing
@app.post("/events/publish")
async def publish_webhook_event(
    event_type: WebhookEvent,
    payload: Dict[str, Any],
    event_id: Optional[str] = None,
    source_service: Optional[str] = None
):
    """Publish an event to trigger webhook deliveries"""
    
    if not event_id:
        event_id = str(uuid.uuid4())
    
    # Find matching endpoints
    matching_endpoints = [
        e for e in webhook_endpoints 
        if e.status == WebhookStatus.ACTIVE and (not e.events or event_type in e.events)
    ]
    
    created_deliveries = []
    
    for endpoint in matching_endpoints:
        # Apply filters
        if not apply_filters(payload, endpoint.event_filters):
            continue
        
        # Create delivery
        delivery = WebhookDelivery(
            webhook_id=endpoint.id,
            endpoint_url=str(endpoint.url),
            event_type=event_type,
            event_id=event_id,
            event_timestamp=datetime.now(),
            payload=payload,
            source_service=source_service,
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        # Apply transformation if configured
        if endpoint.transformation.enabled:
            delivery.payload = await transform_payload(payload, endpoint.transformation)
            delivery.transformed = True
        
        webhook_deliveries.append(delivery)
        created_deliveries.append(delivery.id)
    
    logger.info(f"Published event {event_type.value} - created {len(created_deliveries)} deliveries")
    
    return {
        "event_id": event_id,
        "event_type": event_type.value,
        "deliveries_created": len(created_deliveries),
        "delivery_ids": created_deliveries
    }

# Template Management
@app.get("/templates", response_model=List[WebhookTemplate])
async def get_webhook_templates(event_type: Optional[WebhookEvent] = None):
    """Get webhook templates"""
    filtered_templates = webhook_templates.copy()
    
    if event_type:
        filtered_templates = [t for t in filtered_templates if t.event_type == event_type]
    
    # Sort by usage count
    filtered_templates.sort(key=lambda x: x.usage_count, reverse=True)
    
    return filtered_templates

@app.get("/templates/{template_id}", response_model=WebhookTemplate)
async def get_webhook_template(template_id: str):
    """Get a specific webhook template"""
    template = next((t for t in webhook_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Webhook template not found")
    return template

@app.post("/templates", response_model=WebhookTemplate)
async def create_webhook_template(template_data: WebhookTemplate):
    """Create a new webhook template"""
    webhook_templates.append(template_data)
    logger.info(f"Created webhook template: {template_data.name}")
    return template_data

@app.post("/templates/{template_id}/test")
async def test_webhook_template(template_id: str, test_data: Optional[Dict[str, Any]] = None):
    """Test a webhook template with sample data"""
    template = next((t for t in webhook_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Webhook template not found")
    
    # Use provided test data or sample data
    data = test_data or template.sample_payload
    
    # Simple template rendering (would use Jinja2 in production)
    rendered_payload = template.payload_template
    for key, value in data.items():
        rendered_payload = rendered_payload.replace(f"{{{{{key}}}}}", str(value))
    
    try:
        parsed_payload = json.loads(rendered_payload)
    except json.JSONDecodeError:
        parsed_payload = {"error": "Invalid JSON in template"}
    
    return {
        "template_id": template_id,
        "test_data": data,
        "rendered_payload": parsed_payload,
        "headers": template.headers_template
    }

# Analytics Endpoints
@app.get("/analytics/overview")
async def get_webhook_analytics():
    """Get comprehensive webhook analytics"""
    
    total_deliveries = len(webhook_deliveries)
    successful_deliveries = len([d for d in webhook_deliveries if d.status == DeliveryStatus.DELIVERED])
    failed_deliveries = len([d for d in webhook_deliveries if d.status == DeliveryStatus.FAILED])
    
    success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Calculate average response time
    completed_deliveries = [d for d in webhook_deliveries if d.attempts]
    avg_response_time = 0
    if completed_deliveries:
        total_time = sum(
            sum(attempt.duration_ms for attempt in delivery.attempts) 
            for delivery in completed_deliveries
        )
        total_attempts = sum(len(delivery.attempts) for delivery in completed_deliveries)
        avg_response_time = total_time / total_attempts if total_attempts > 0 else 0
    
    # Endpoint performance
    endpoint_stats = {}
    for endpoint in webhook_endpoints:
        endpoint_deliveries = [d for d in webhook_deliveries if d.webhook_id == endpoint.id]
        successful = len([d for d in endpoint_deliveries if d.status == DeliveryStatus.DELIVERED])
        endpoint_stats[endpoint.name] = {
            "total_deliveries": len(endpoint_deliveries),
            "successful_deliveries": successful,
            "success_rate": (successful / len(endpoint_deliveries) * 100) if endpoint_deliveries else 0,
            "endpoint_url": str(endpoint.url)
        }
    
    # Event type performance
    event_stats = {}
    for event_type in WebhookEvent:
        event_deliveries = [d for d in webhook_deliveries if d.event_type == event_type]
        if event_deliveries:
            successful = len([d for d in event_deliveries if d.status == DeliveryStatus.DELIVERED])
            event_stats[event_type.value] = {
                "total_deliveries": len(event_deliveries),
                "successful_deliveries": successful,
                "success_rate": (successful / len(event_deliveries) * 100)
            }
    
    # Error analysis
    error_breakdown = {}
    status_code_breakdown = {}
    
    for delivery in webhook_deliveries:
        if delivery.status == DeliveryStatus.FAILED and delivery.attempts:
            last_attempt = delivery.attempts[-1]
            if last_attempt.error_message:
                error_type = "Network Error" if "timeout" in last_attempt.error_message.lower() else "Server Error"
                error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1
            
            if last_attempt.response_status_code:
                status_code = str(last_attempt.response_status_code)
                status_code_breakdown[status_code] = status_code_breakdown.get(status_code, 0) + 1
    
    return {
        "summary": {
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "pending_deliveries": len([d for d in webhook_deliveries if d.status == DeliveryStatus.PENDING]),
            "active_endpoints": len([e for e in webhook_endpoints if e.status == WebhookStatus.ACTIVE]),
            "total_endpoints": len(webhook_endpoints),
            "available_templates": len(webhook_templates)
        },
        "performance_metrics": {
            "success_rate": round(success_rate, 1),
            "average_response_time_ms": round(avg_response_time, 1),
            "retry_rate": round((len([d for d in webhook_deliveries if len(d.attempts) > 1]) / total_deliveries * 100) if total_deliveries > 0 else 0, 1)
        },
        "endpoint_performance": endpoint_stats,
        "event_performance": event_stats,
        "error_analysis": {
            "error_breakdown": error_breakdown,
            "status_code_breakdown": status_code_breakdown
        },
        "recent_activity": {
            "deliveries_24h": len([d for d in webhook_deliveries if d.created_at > datetime.now() - timedelta(hours=24)]),
            "errors_24h": len([d for d in webhook_deliveries if d.status == DeliveryStatus.FAILED and d.created_at > datetime.now() - timedelta(hours=24)]),
            "endpoints_healthy": len([e for e in webhook_endpoints if e.status == WebhookStatus.ACTIVE and e.last_success_at and e.last_success_at > datetime.now() - timedelta(hours=1)])
        }
    }

@app.get("/analytics/trends")
async def get_webhook_trends(days: int = 7):
    """Get webhook delivery trends over time"""
    
    trend_data = []
    for i in range(days, 0, -1):
        date_obj = datetime.now() - timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Calculate daily metrics
        daily_deliveries = len([d for d in webhook_deliveries if d.created_at.date() == date_obj.date()])
        daily_successful = len([d for d in webhook_deliveries if d.delivered_at and d.delivered_at.date() == date_obj.date()])
        daily_failed = len([d for d in webhook_deliveries if d.status == DeliveryStatus.FAILED and d.created_at.date() == date_obj.date()])
        
        success_rate = (daily_successful / daily_deliveries * 100) if daily_deliveries > 0 else 0
        
        trend_data.append({
            "date": date_str,
            "total_deliveries": daily_deliveries + (i % 5),  # Add variation for demo
            "successful_deliveries": daily_successful + (i % 4),
            "failed_deliveries": daily_failed + (i % 2),
            "success_rate": min(100, success_rate + (i % 15)),
            "average_response_time": 200 + (i % 100)
        })
    
    return {
        "period_days": days,
        "trend_data": trend_data,
        "summary": {
            "total_deliveries": sum(d["total_deliveries"] for d in trend_data),
            "average_success_rate": sum(d["success_rate"] for d in trend_data) / len(trend_data),
            "average_response_time": sum(d["average_response_time"] for d in trend_data) / len(trend_data)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)
