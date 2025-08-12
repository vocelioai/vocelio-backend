"""
Scheduling Service - Vocelio AI Call Center
Comprehensive appointment booking, calendar management, and scheduling automation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, time, date
from enum import Enum
import uuid
import asyncio
import json
import logging
import re
from decimal import Decimal
import calendar
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduling Models
class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    REMINDED = "reminded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class AppointmentType(str, Enum):
    SALES_CALL = "sales_call"
    DEMO = "demo"
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    DISCOVERY = "discovery"
    PROPOSAL = "proposal"
    CLOSING = "closing"
    SUPPORT = "support"
    ONBOARDING = "onboarding"
    TRAINING = "training"
    REVIEW = "review"
    OTHER = "other"

class RecurrenceType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class ReminderType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE_CALL = "phone_call"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"

class CalendarProvider(str, Enum):
    GOOGLE = "google"
    OUTLOOK = "outlook"
    OFFICE365 = "office365"
    APPLE = "apple"
    CALDAV = "caldav"
    INTERNAL = "internal"

class BookingSource(str, Enum):
    WEBSITE = "website"
    PHONE = "phone"
    EMAIL = "email"
    AGENT = "agent"
    API = "api"
    MOBILE_APP = "mobile_app"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"

class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    available: bool = True
    capacity: int = 1
    booked_count: int = 0
    
    # Slot configuration
    slot_type: str = "standard"  # "standard", "premium", "emergency"
    price: Optional[Decimal] = None
    agent_id: Optional[str] = None
    location: Optional[str] = None
    
    # Restrictions
    min_advance_hours: int = 2
    max_advance_days: int = 90
    booking_deadline: Optional[datetime] = None

class Reminder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reminder_type: ReminderType
    time_before_minutes: int
    
    # Message content
    subject: Optional[str] = None
    message: str
    template_id: Optional[str] = None
    
    # Delivery status
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    delivered: bool = False
    delivery_status: Optional[str] = None
    error_message: Optional[str] = None
    
    # Tracking
    opened: bool = False
    clicked: bool = False
    response_received: bool = False

class RecurrenceRule(BaseModel):
    recurrence_type: RecurrenceType
    interval: int = 1  # Every N days/weeks/months
    end_date: Optional[date] = None
    max_occurrences: Optional[int] = None
    
    # Weekly recurrence
    days_of_week: List[int] = []  # 0=Monday, 6=Sunday
    
    # Monthly recurrence
    day_of_month: Optional[int] = None
    week_of_month: Optional[int] = None  # 1st, 2nd, 3rd, 4th, last
    
    # Custom pattern
    custom_pattern: Optional[str] = None

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Basic information
    title: str
    description: Optional[str] = None
    appointment_type: AppointmentType
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    
    # Timing
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    timezone: str = "UTC"
    
    # Participants
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    
    # Additional attendees
    attendees: List[Dict[str, str]] = []  # [{"name": "", "email": "", "role": ""}]
    
    # Location and access
    location_type: str = "phone"  # "phone", "video", "in_person", "hybrid"
    location_details: Optional[str] = None
    meeting_link: Optional[str] = None
    dial_in_number: Optional[str] = None
    access_code: Optional[str] = None
    
    # Booking details
    booking_source: BookingSource
    booked_at: datetime = Field(default_factory=datetime.now)
    booked_by: Optional[str] = None  # User/agent who booked
    
    # Confirmation and reminders
    confirmation_sent: bool = False
    confirmation_sent_at: Optional[datetime] = None
    reminders: List[Reminder] = []
    
    # Recurrence
    is_recurring: bool = False
    recurrence_rule: Optional[RecurrenceRule] = None
    parent_appointment_id: Optional[str] = None  # For recurring instances
    recurring_series_id: Optional[str] = None
    
    # Preparation and requirements
    agenda: Optional[str] = None
    preparation_notes: Optional[str] = None
    required_documents: List[str] = []
    meeting_materials: List[Dict[str, str]] = []
    
    # Integration
    external_calendar_id: Optional[str] = None
    calendar_provider: Optional[CalendarProvider] = None
    sync_status: str = "pending"  # "pending", "synced", "failed"
    
    # Outcome and follow-up
    outcome: Optional[str] = None
    outcome_notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    next_appointment_id: Optional[str] = None
    
    # Feedback and rating
    customer_feedback: Optional[str] = None
    customer_rating: Optional[int] = None  # 1-5
    agent_feedback: Optional[str] = None
    
    # Metadata
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AvailabilityRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    
    # Agent/resource
    agent_id: Optional[str] = None
    resource_type: str = "agent"  # "agent", "room", "equipment"
    
    # Time patterns
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    
    # Date range
    effective_from: date
    effective_until: Optional[date] = None
    
    # Appointment configuration
    slot_duration_minutes: int = 30
    buffer_minutes: int = 15  # Buffer between appointments
    max_appointments_per_day: Optional[int] = None
    
    # Booking rules
    advance_booking_hours: int = 2
    max_advance_days: int = 30
    allow_back_to_back: bool = False
    
    # Capacity and pricing
    capacity: int = 1
    appointment_types: List[AppointmentType] = []
    
    # Status
    is_active: bool = True
    priority: int = 0  # Higher priority rules take precedence

class CalendarIntegration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    provider: CalendarProvider
    
    # Connection details
    agent_id: str
    external_calendar_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Sync configuration
    sync_enabled: bool = True
    sync_direction: str = "bidirectional"  # "import_only", "export_only", "bidirectional"
    sync_frequency_minutes: int = 15
    last_sync_at: Optional[datetime] = None
    
    # Mapping rules
    appointment_type_mapping: Dict[str, str] = {}
    calendar_settings: Dict[str, Any] = {}
    
    # Status
    status: str = "active"  # "active", "error", "disabled"
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class BookingPage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: str
    description: str
    
    # Configuration
    agent_id: Optional[str] = None
    appointment_types: List[AppointmentType] = []
    duration_options: List[int] = [30, 60]  # minutes
    
    # Availability
    timezone: str = "UTC"
    buffer_time_minutes: int = 15
    advance_notice_hours: int = 24
    max_advance_days: int = 30
    
    # Customization
    branding: Dict[str, Any] = {}
    custom_fields: List[Dict[str, Any]] = []
    confirmation_message: str = "Your appointment has been scheduled successfully!"
    
    # Integration
    redirect_url: Optional[str] = None
    webhook_url: Optional[str] = None
    calendar_integration_id: Optional[str] = None
    
    # Analytics
    page_views: int = 0
    bookings_count: int = 0
    conversion_rate: float = 0.0
    
    # Status
    is_public: bool = True
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class SchedulingAnalytics(BaseModel):
    time_period: str
    total_appointments: int
    confirmed_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_shows: int
    
    # Rates
    confirmation_rate: float
    completion_rate: float
    cancellation_rate: float
    no_show_rate: float
    
    # Utilization
    booking_utilization: float
    agent_utilization: Dict[str, float] = {}
    peak_booking_hours: List[int] = []
    
    # Performance
    average_lead_time: float  # Hours between booking and appointment
    popular_appointment_types: Dict[str, int] = {}
    booking_sources: Dict[str, int] = {}
    
    # Trends
    daily_bookings: List[Dict[str, Any]] = []
    weekly_patterns: Dict[str, int] = {}
    monthly_trends: List[Dict[str, Any]] = []

# Sample data
SAMPLE_APPOINTMENTS = [
    Appointment(
        title="Product Demo - Enterprise Solution",
        description="Comprehensive product demonstration for enterprise clients",
        appointment_type=AppointmentType.DEMO,
        status=AppointmentStatus.CONFIRMED,
        start_time=datetime.now() + timedelta(days=2, hours=2),
        end_time=datetime.now() + timedelta(days=2, hours=3),
        duration_minutes=60,
        customer_id="cust_001",
        customer_name="Sarah Johnson",
        customer_email="sarah.johnson@techcorp.com",
        customer_phone="+1-555-0123",
        agent_id="agent_001",
        agent_name="Michael Chen",
        location_type="video",
        meeting_link="https://meet.vocelio.com/demo-123",
        booking_source=BookingSource.WEBSITE,
        confirmation_sent=True,
        confirmation_sent_at=datetime.now() - timedelta(hours=2),
        agenda="1. Product overview\n2. Feature demonstration\n3. Q&A session\n4. Next steps discussion",
        preparation_notes="Review client requirements and prepare custom demo scenarios",
        reminders=[
            Reminder(
                reminder_type=ReminderType.EMAIL,
                time_before_minutes=1440,  # 24 hours
                subject="Reminder: Product Demo Tomorrow",
                message="This is a friendly reminder about your product demonstration scheduled for tomorrow.",
                scheduled_at=datetime.now() + timedelta(days=1, hours=2)
            ),
            Reminder(
                reminder_type=ReminderType.SMS,
                time_before_minutes=60,  # 1 hour
                message="Your demo starts in 1 hour. Join at: https://meet.vocelio.com/demo-123",
                scheduled_at=datetime.now() + timedelta(days=2, hours=1)
            )
        ],
        tags=["enterprise", "demo", "high_priority"]
    ),
    Appointment(
        title="Discovery Call - Sales Consultation",
        description="Initial discovery call to understand client needs",
        appointment_type=AppointmentType.DISCOVERY,
        status=AppointmentStatus.SCHEDULED,
        start_time=datetime.now() + timedelta(days=1, hours=4),
        end_time=datetime.now() + timedelta(days=1, hours=4, minutes=30),
        duration_minutes=30,
        customer_id="cust_002",
        customer_name="Robert Wilson",
        customer_email="robert.wilson@startup.com",
        customer_phone="+1-555-0456",
        agent_id="agent_002",
        agent_name="Lisa Rodriguez",
        location_type="phone",
        dial_in_number="+1-800-VOCELIO",
        booking_source=BookingSource.PHONE,
        confirmation_sent=True,
        agenda="1. Company background\n2. Current challenges\n3. Solution requirements\n4. Budget discussion",
        tags=["startup", "discovery", "sales"]
    ),
    Appointment(
        title="Follow-up Meeting - Proposal Review",
        description="Review proposal and address any questions",
        appointment_type=AppointmentType.PROPOSAL,
        status=AppointmentStatus.CONFIRMED,
        start_time=datetime.now() + timedelta(days=5, hours=3),
        end_time=datetime.now() + timedelta(days=5, hours=4),
        duration_minutes=60,
        customer_id="cust_003",
        customer_name="Jennifer Adams",
        customer_email="jennifer.adams@enterprise.com",
        customer_phone="+1-555-0789",
        agent_id="agent_003",
        agent_name="David Kim",
        location_type="video",
        meeting_link="https://meet.vocelio.com/proposal-456",
        booking_source=BookingSource.EMAIL,
        is_recurring=True,
        recurrence_rule=RecurrenceRule(
            recurrence_type=RecurrenceType.WEEKLY,
            interval=1,
            days_of_week=[1],  # Tuesdays
            max_occurrences=4
        ),
        tags=["enterprise", "proposal", "recurring"]
    )
]

SAMPLE_AVAILABILITY_RULES = [
    AvailabilityRule(
        name="Michael Chen - Weekday Morning",
        agent_id="agent_001",
        day_of_week=0,  # Monday
        start_time=time(9, 0),
        end_time=time(12, 0),
        effective_from=date.today(),
        slot_duration_minutes=30,
        buffer_minutes=15,
        max_appointments_per_day=6,
        appointment_types=[AppointmentType.DEMO, AppointmentType.CONSULTATION]
    ),
    AvailabilityRule(
        name="Lisa Rodriguez - Weekday Afternoon",
        agent_id="agent_002",
        day_of_week=1,  # Tuesday
        start_time=time(13, 0),
        end_time=time(17, 0),
        effective_from=date.today(),
        slot_duration_minutes=30,
        buffer_minutes=10,
        appointment_types=[AppointmentType.DISCOVERY, AppointmentType.FOLLOW_UP]
    )
]

SAMPLE_BOOKING_PAGES = [
    BookingPage(
        name="Enterprise Demo Booking",
        title="Schedule Your Product Demo",
        description="Book a personalized product demonstration with our enterprise solutions expert",
        agent_id="agent_001",
        appointment_types=[AppointmentType.DEMO, AppointmentType.CONSULTATION],
        duration_options=[30, 60, 90],
        advance_notice_hours=24,
        max_advance_days=30,
        custom_fields=[
            {"name": "company_size", "type": "select", "options": ["1-10", "11-50", "51-200", "200+"], "required": True},
            {"name": "use_case", "type": "text", "placeholder": "Describe your primary use case", "required": True}
        ],
        bookings_count=45,
        conversion_rate=23.5
    )
]

# Global storage
appointments: List[Appointment] = []
availability_rules: List[AvailabilityRule] = []
calendar_integrations: List[CalendarIntegration] = []
booking_pages: List[BookingPage] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global appointments, availability_rules, booking_pages
    
    appointments.extend(SAMPLE_APPOINTMENTS)
    availability_rules.extend(SAMPLE_AVAILABILITY_RULES)
    booking_pages.extend(SAMPLE_BOOKING_PAGES)
    
    # Create sample calendar integration
    sample_integration = CalendarIntegration(
        name="Michael's Google Calendar",
        provider=CalendarProvider.GOOGLE,
        agent_id="agent_001",
        external_calendar_id="michael.chen@vocelio.com",
        sync_enabled=True,
        last_sync_at=datetime.now() - timedelta(minutes=15),
        status="active"
    )
    
    calendar_integrations.append(sample_integration)
    
    logger.info("Sample scheduling data initialized successfully")

async def generate_available_slots(
    agent_id: Optional[str] = None,
    start_date: date = None,
    end_date: date = None,
    duration_minutes: int = 30,
    appointment_type: Optional[AppointmentType] = None
) -> List[TimeSlot]:
    """Generate available time slots based on availability rules and existing bookings"""
    
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=30)
    
    available_slots = []
    
    # Get relevant availability rules
    rules = availability_rules.copy()
    if agent_id:
        rules = [r for r in rules if r.agent_id == agent_id and r.is_active]
    
    # Get existing appointments for the period
    existing_appointments = [
        a for a in appointments
        if a.start_time.date() >= start_date and a.start_time.date() <= end_date
        and a.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]
    ]
    
    # Generate slots for each day
    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()
        
        # Find applicable rules for this day
        day_rules = [r for r in rules if r.day_of_week == day_of_week]
        
        for rule in day_rules:
            # Check if rule is effective
            if current_date < rule.effective_from:
                continue
            if rule.effective_until and current_date > rule.effective_until:
                continue
            
            # Filter by appointment type if specified
            if appointment_type and rule.appointment_types and appointment_type not in rule.appointment_types:
                continue
            
            # Generate time slots for this rule
            current_time = datetime.combine(current_date, rule.start_time)
            end_time = datetime.combine(current_date, rule.end_time)
            
            while current_time + timedelta(minutes=duration_minutes) <= end_time:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with existing appointments
                conflicts = [
                    a for a in existing_appointments
                    if (a.agent_id == rule.agent_id and
                        not (slot_end <= a.start_time or current_time >= a.end_time))
                ]
                
                # Check advance booking requirements
                hours_advance = (current_time - datetime.now()).total_seconds() / 3600
                if hours_advance >= rule.advance_booking_hours:
                    slot = TimeSlot(
                        start_time=current_time,
                        end_time=slot_end,
                        duration_minutes=duration_minutes,
                        available=len(conflicts) == 0,
                        capacity=rule.capacity,
                        booked_count=len(conflicts),
                        agent_id=rule.agent_id,
                        min_advance_hours=rule.advance_booking_hours
                    )
                    
                    available_slots.append(slot)
                
                # Move to next slot (including buffer time)
                current_time += timedelta(minutes=duration_minutes + rule.buffer_minutes)
        
        current_date += timedelta(days=1)
    
    # Sort slots by start time
    available_slots.sort(key=lambda x: x.start_time)
    
    return available_slots

async def send_appointment_reminder(appointment: Appointment, reminder: Reminder):
    """Send appointment reminder (mock implementation)"""
    try:
        # Mock sending logic based on reminder type
        if reminder.reminder_type == ReminderType.EMAIL:
            logger.info(f"Sending email reminder to {appointment.customer_email}")
        elif reminder.reminder_type == ReminderType.SMS:
            logger.info(f"Sending SMS reminder to {appointment.customer_phone}")
        elif reminder.reminder_type == ReminderType.PHONE_CALL:
            logger.info(f"Initiating reminder call to {appointment.customer_phone}")
        
        # Update reminder status
        reminder.sent_at = datetime.now()
        reminder.delivered = True
        reminder.delivery_status = "delivered"
        
        logger.info(f"Reminder sent successfully for appointment {appointment.id}")
        
    except Exception as e:
        reminder.delivery_status = "failed"
        reminder.error_message = str(e)
        logger.error(f"Failed to send reminder for appointment {appointment.id}: {e}")

async def process_scheduled_reminders():
    """Process and send scheduled reminders"""
    current_time = datetime.now()
    
    for appointment in appointments:
        if appointment.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
            continue
            
        for reminder in appointment.reminders:
            if (not reminder.sent_at and 
                reminder.scheduled_at <= current_time):
                await send_appointment_reminder(appointment, reminder)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    
    # Start background task for reminder processing
    async def reminder_task():
        while True:
            await process_scheduled_reminders()
            await asyncio.sleep(300)  # Check every 5 minutes
    
    reminder_task_handle = asyncio.create_task(reminder_task())
    
    yield
    
    # Shutdown
    reminder_task_handle.cancel()

# FastAPI app
app = FastAPI(
    title="Scheduling Service",
    description="Comprehensive appointment booking, calendar management, and scheduling automation for Vocelio AI Call Center",
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

# Calendar Integration Configuration
INTEGRATIONS_SERVICE_URL = "http://integrations:8010"  # Internal Docker network URL
INTEGRATIONS_SERVICE_URL_EXTERNAL = "http://localhost:8010"  # External URL for testing

# Calendar Integration Functions
async def get_calendar_providers():
    """Get available calendar providers from integrations service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{INTEGRATIONS_SERVICE_URL}/calendar/providers")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get calendar providers: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"Error connecting to integrations service: {str(e)}")
        # Fallback to external URL
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{INTEGRATIONS_SERVICE_URL_EXTERNAL}/calendar/providers")
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
        except Exception as fallback_error:
            logger.error(f"Fallback connection also failed: {str(fallback_error)}")
            return []

async def check_calendar_availability(integration_id: str, start_time: datetime, end_time: datetime):
    """Check availability in a specific calendar"""
    try:
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "time_zone": "UTC"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{INTEGRATIONS_SERVICE_URL}/calendar/availability/{integration_id}",
                params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to check calendar availability: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error checking calendar availability: {str(e)}")
        return None

async def create_calendar_event(integration_id: str, event_data: Dict[str, Any]):
    """Create an event in the specified calendar"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{INTEGRATIONS_SERVICE_URL}/calendar/events/{integration_id}",
                json=event_data
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to create calendar event: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error creating calendar event: {str(e)}")
        return None

async def update_calendar_event(integration_id: str, event_id: str, event_data: Dict[str, Any]):
    """Update an event in the specified calendar"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{INTEGRATIONS_SERVICE_URL}/calendar/events/{integration_id}/{event_id}",
                json=event_data
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to update calendar event: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error updating calendar event: {str(e)}")
        return None

async def delete_calendar_event(integration_id: str, event_id: str):
    """Delete an event from the specified calendar"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{INTEGRATIONS_SERVICE_URL}/calendar/events/{integration_id}/{event_id}"
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to delete calendar event: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error deleting calendar event: {str(e)}")
        return None

async def sync_appointment_to_calendar(appointment: 'Appointment'):
    """Sync an appointment to all configured calendar providers"""
    calendar_providers = await get_calendar_providers()
    results = []
    
    for provider in calendar_providers:
        if provider.get('status') == 'active':
            event_data = {
                "title": f"{appointment.appointment_type.value.replace('_', ' ').title()} - {appointment.customer_name}",
                "start_time": appointment.start_time.isoformat(),
                "end_time": appointment.end_time.isoformat(),
                "description": f"Appointment Details:\n"
                             f"Type: {appointment.appointment_type.value}\n"
                             f"Contact: {appointment.customer_name}\n"
                             f"Phone: {appointment.customer_phone}\n"
                             f"Email: {appointment.customer_email}\n"
                             f"Notes: {appointment.description or 'No additional notes'}",
                "location": appointment.location_details or "Virtual Meeting",
                "attendees": [
                    {"email": appointment.customer_email, "name": appointment.customer_name}
                ] if appointment.customer_email else []
            }
            
            result = await create_calendar_event(provider['id'], event_data)
            if result:
                results.append({
                    "provider": provider['name'],
                    "integration_id": provider['id'],
                    "event_id": result.get('event', {}).get('id'),
                    "success": True
                })
            else:
                results.append({
                    "provider": provider['name'],
                    "integration_id": provider['id'],
                    "success": False,
                    "error": "Failed to create calendar event"
                })
    
    return results

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "scheduling",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Calendar Integration Endpoints
@app.get("/calendar/providers")
async def get_calendar_integration_providers():
    """Get available calendar providers from integrations service"""
    providers = await get_calendar_providers()
    return {
        "providers": providers,
        "total_providers": len(providers),
        "active_providers": len([p for p in providers if p.get('status') == 'active']),
        "service_connection": "healthy" if providers else "unavailable"
    }

@app.get("/calendar/availability")
async def check_appointment_availability(
    start_time: datetime,
    end_time: datetime,
    integration_id: Optional[str] = None
):
    """Check availability across calendar providers for appointment scheduling"""
    calendar_providers = await get_calendar_providers()
    
    if integration_id:
        # Check specific calendar
        provider = next((p for p in calendar_providers if p['id'] == integration_id), None)
        if not provider:
            raise HTTPException(status_code=404, detail="Calendar provider not found")
        
        availability = await check_calendar_availability(integration_id, start_time, end_time)
        return {
            "provider": provider['name'],
            "availability": availability,
            "time_slot": {"start": start_time, "end": end_time}
        }
    else:
        # Check all active calendars
        availability_results = []
        for provider in calendar_providers:
            if provider.get('status') == 'active':
                availability = await check_calendar_availability(provider['id'], start_time, end_time)
                availability_results.append({
                    "provider": provider['name'],
                    "integration_id": provider['id'],
                    "availability": availability
                })
        
        return {
            "time_slot": {"start": start_time, "end": end_time},
            "providers_checked": len(availability_results),
            "availability_results": availability_results,
            "overall_available": all(
                result['availability'] and result['availability'].get('is_available', False)
                for result in availability_results
                if result['availability']
            )
        }

@app.post("/calendar/sync/{appointment_id}")
async def sync_appointment_to_calendars(appointment_id: str):
    """Manually sync an appointment to all configured calendar providers"""
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    sync_results = await sync_appointment_to_calendar(appointment)
    
    # Update appointment with calendar sync info
    appointment.custom_fields["calendar_sync"] = {
        "last_synced": datetime.now().isoformat(),
        "sync_results": sync_results,
        "synced_providers": [r['provider'] for r in sync_results if r['success']]
    }
    
    return {
        "appointment_id": appointment_id,
        "sync_results": sync_results,
        "successful_syncs": len([r for r in sync_results if r['success']]),
        "failed_syncs": len([r for r in sync_results if not r['success']]),
        "status": "success" if any(r['success'] for r in sync_results) else "failed"
    }

@app.get("/calendar/sync-status")
async def get_calendar_sync_status():
    """Get calendar sync status for all appointments"""
    synced_appointments = []
    unsynced_appointments = []
    
    for appointment in appointments:
        calendar_sync = appointment.custom_fields.get("calendar_sync")
        if calendar_sync:
            synced_appointments.append({
                "appointment_id": appointment.id,
                "contact_name": appointment.customer_name,
                "start_time": appointment.start_time,
                "last_synced": calendar_sync.get("last_synced"),
                "synced_providers": calendar_sync.get("synced_providers", [])
            })
        else:
            unsynced_appointments.append({
                "appointment_id": appointment.id,
                "contact_name": appointment.customer_name,
                "start_time": appointment.start_time,
                "status": appointment.status
            })
    
    return {
        "total_appointments": len(appointments),
        "synced_appointments": len(synced_appointments),
        "unsynced_appointments": len(unsynced_appointments),
        "sync_details": {
            "synced": synced_appointments,
            "unsynced": unsynced_appointments
        }
    }

# Appointment Management Endpoints
@app.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    status: Optional[AppointmentStatus] = None,
    appointment_type: Optional[AppointmentType] = None,
    agent_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    sort_by: str = "start_time",  # "start_time", "created_at", "status"
    limit: int = 50,
    offset: int = 0
):
    """Get appointments with filtering and sorting options"""
    
    filtered_appointments = appointments.copy()
    
    # Apply filters
    if status:
        filtered_appointments = [a for a in filtered_appointments if a.status == status]
    
    if appointment_type:
        filtered_appointments = [a for a in filtered_appointments if a.appointment_type == appointment_type]
    
    if agent_id:
        filtered_appointments = [a for a in filtered_appointments if a.agent_id == agent_id]
    
    if customer_id:
        filtered_appointments = [a for a in filtered_appointments if a.customer_id == customer_id]
    
    if start_date:
        filtered_appointments = [a for a in filtered_appointments if a.start_time.date() >= start_date]
    
    if end_date:
        filtered_appointments = [a for a in filtered_appointments if a.start_time.date() <= end_date]
    
    if search:
        search_lower = search.lower()
        filtered_appointments = [
            a for a in filtered_appointments
            if (search_lower in a.title.lower() or 
                search_lower in a.customer_name.lower() or
                search_lower in a.customer_email.lower() or
                (a.description and search_lower in a.description.lower()))
        ]
    
    # Apply sorting
    if sort_by == "start_time":
        filtered_appointments.sort(key=lambda x: x.start_time)
    elif sort_by == "created_at":
        filtered_appointments.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "status":
        filtered_appointments.sort(key=lambda x: x.status.value)
    
    # Apply pagination
    return filtered_appointments[offset:offset + limit]

@app.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID"""
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: Appointment):
    """Create a new appointment"""
    
    # Validate appointment time
    if appointment_data.start_time <= datetime.now():
        raise HTTPException(status_code=400, detail="Appointment time must be in the future")
    
    if appointment_data.end_time <= appointment_data.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Check for conflicts
    conflicts = [
        a for a in appointments
        if (a.agent_id == appointment_data.agent_id and
            a.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW] and
            not (appointment_data.end_time <= a.start_time or appointment_data.start_time >= a.end_time))
    ]
    
    if conflicts:
        raise HTTPException(status_code=409, detail="Time slot conflicts with existing appointment")
    
    # Set duration if not provided
    if not appointment_data.duration_minutes:
        appointment_data.duration_minutes = int((appointment_data.end_time - appointment_data.start_time).total_seconds() / 60)
    
    # Generate reminders if not provided
    if not appointment_data.reminders:
        # Default reminders: 24 hours and 1 hour before
        appointment_data.reminders = [
            Reminder(
                reminder_type=ReminderType.EMAIL,
                time_before_minutes=1440,  # 24 hours
                subject=f"Reminder: {appointment_data.title}",
                message=f"This is a reminder about your upcoming {appointment_data.appointment_type.value} scheduled for {appointment_data.start_time.strftime('%B %d, %Y at %I:%M %p')}.",
                scheduled_at=appointment_data.start_time - timedelta(hours=24)
            ),
            Reminder(
                reminder_type=ReminderType.SMS,
                time_before_minutes=60,  # 1 hour
                message=f"Your {appointment_data.appointment_type.value} starts in 1 hour.",
                scheduled_at=appointment_data.start_time - timedelta(hours=1)
            )
        ]
    
    appointments.append(appointment_data)
    logger.info(f"Created new appointment: {appointment_data.title} for {appointment_data.contact_name}")
    
    # Automatically sync to calendar providers
    try:
        sync_results = await sync_appointment_to_calendar(appointment_data)
        appointment_data.custom_fields["calendar_sync"] = {
            "last_synced": datetime.now().isoformat(),
            "sync_results": sync_results,
            "synced_providers": [r['provider'] for r in sync_results if r['success']]
        }
        logger.info(f"Synced appointment {appointment_data.id} to {len([r for r in sync_results if r['success']])} calendar providers")
    except Exception as e:
        logger.error(f"Failed to sync appointment to calendars: {str(e)}")
        appointment_data.custom_fields["calendar_sync"] = {
            "last_synced": datetime.now().isoformat(),
            "sync_error": str(e)
        }
    
    return appointment_data

@app.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment_data: Appointment):
    """Update an existing appointment"""
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update fields
    for field, value in appointment_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(appointment, field, value)
    
    appointment.updated_at = datetime.now()
    
    logger.info(f"Updated appointment: {appointment.title}")
    return appointment

@app.put("/appointments/{appointment_id}/status")
async def update_appointment_status(appointment_id: str, status: AppointmentStatus, notes: Optional[str] = None):
    """Update appointment status"""
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    old_status = appointment.status
    appointment.status = status
    appointment.updated_at = datetime.now()
    
    # Handle specific status changes
    if status == AppointmentStatus.CONFIRMED and not appointment.confirmation_sent:
        appointment.confirmation_sent = True
        appointment.confirmation_sent_at = datetime.now()
    
    if status == AppointmentStatus.COMPLETED and notes:
        appointment.outcome_notes = notes
    
    logger.info(f"Updated appointment {appointment_id} status from {old_status} to {status}")
    return {"message": f"Appointment status updated to {status}"}

@app.put("/appointments/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: str,
    new_start_time: datetime,
    new_end_time: Optional[datetime] = None,
    reason: Optional[str] = None
):
    """Reschedule an appointment"""
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if new_start_time <= datetime.now():
        raise HTTPException(status_code=400, detail="New appointment time must be in the future")
    
    # Calculate new end time if not provided
    if not new_end_time:
        duration = appointment.end_time - appointment.start_time
        new_end_time = new_start_time + duration
    
    # Check for conflicts
    conflicts = [
        a for a in appointments
        if (a.id != appointment_id and
            a.agent_id == appointment.agent_id and
            a.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW] and
            not (new_end_time <= a.start_time or new_start_time >= a.end_time))
    ]
    
    if conflicts:
        raise HTTPException(status_code=409, detail="New time slot conflicts with existing appointment")
    
    # Update appointment times
    old_start = appointment.start_time
    appointment.start_time = new_start_time
    appointment.end_time = new_end_time
    appointment.status = AppointmentStatus.RESCHEDULED
    appointment.updated_at = datetime.now()
    
    # Update reminders
    time_diff = new_start_time - old_start
    for reminder in appointment.reminders:
        if not reminder.sent_at:  # Only update unsent reminders
            reminder.scheduled_at += time_diff
    
    logger.info(f"Rescheduled appointment {appointment_id} from {old_start} to {new_start_time}")
    return {"message": "Appointment rescheduled successfully"}

# Availability Management Endpoints
@app.get("/availability/slots")
async def get_available_slots(
    agent_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    duration_minutes: int = 30,
    appointment_type: Optional[AppointmentType] = None
):
    """Get available time slots"""
    
    slots = await generate_available_slots(
        agent_id=agent_id,
        start_date=start_date or date.today(),
        end_date=end_date or (date.today() + timedelta(days=30)),
        duration_minutes=duration_minutes,
        appointment_type=appointment_type
    )
    
    # Filter only available slots
    available_slots = [s for s in slots if s.available]
    
    return {
        "total_slots": len(available_slots),
        "date_range": {
            "start": start_date or date.today(),
            "end": end_date or (date.today() + timedelta(days=30))
        },
        "filters": {
            "agent_id": agent_id,
            "duration_minutes": duration_minutes,
            "appointment_type": appointment_type.value if appointment_type else None
        },
        "slots": available_slots
    }

@app.get("/availability/rules", response_model=List[AvailabilityRule])
async def get_availability_rules(agent_id: Optional[str] = None):
    """Get availability rules"""
    rules = availability_rules.copy()
    if agent_id:
        rules = [r for r in rules if r.agent_id == agent_id]
    
    return rules

@app.post("/availability/rules", response_model=AvailabilityRule)
async def create_availability_rule(rule_data: AvailabilityRule):
    """Create a new availability rule"""
    availability_rules.append(rule_data)
    logger.info(f"Created availability rule: {rule_data.name}")
    return rule_data

@app.put("/availability/rules/{rule_id}", response_model=AvailabilityRule)
async def update_availability_rule(rule_id: str, rule_data: AvailabilityRule):
    """Update an availability rule"""
    rule = next((r for r in availability_rules if r.id == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Availability rule not found")
    
    # Update fields
    for field, value in rule_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(rule, field, value)
    
    logger.info(f"Updated availability rule: {rule.name}")
    return rule

@app.delete("/availability/rules/{rule_id}")
async def delete_availability_rule(rule_id: str):
    """Delete an availability rule"""
    rule = next((r for r in availability_rules if r.id == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Availability rule not found")
    
    availability_rules.remove(rule)
    logger.info(f"Deleted availability rule: {rule.name}")
    return {"message": "Availability rule deleted successfully"}

# Booking Pages Endpoints
@app.get("/booking-pages", response_model=List[BookingPage])
async def get_booking_pages(is_active: Optional[bool] = None):
    """Get booking pages"""
    pages = booking_pages.copy()
    if is_active is not None:
        pages = [p for p in pages if p.is_active == is_active]
    
    return pages

@app.get("/booking-pages/{page_id}", response_model=BookingPage)
async def get_booking_page(page_id: str):
    """Get a specific booking page"""
    page = next((p for p in booking_pages if p.id == page_id), None)
    if not page:
        raise HTTPException(status_code=404, detail="Booking page not found")
    return page

@app.post("/booking-pages", response_model=BookingPage)
async def create_booking_page(page_data: BookingPage):
    """Create a new booking page"""
    booking_pages.append(page_data)
    logger.info(f"Created booking page: {page_data.name}")
    return page_data

@app.post("/booking-pages/{page_id}/book")
async def book_appointment_via_page(
    page_id: str,
    customer_name: str,
    customer_email: str,
    customer_phone: Optional[str] = None,
    appointment_type: AppointmentType = AppointmentType.CONSULTATION,
    start_time: datetime = None,
    duration_minutes: int = 30,
    custom_fields: Optional[Dict[str, Any]] = None
):
    """Book an appointment through a booking page"""
    
    page = next((p for p in booking_pages if p.id == page_id), None)
    if not page:
        raise HTTPException(status_code=404, detail="Booking page not found")
    
    if not page.is_active:
        raise HTTPException(status_code=400, detail="Booking page is not active")
    
    if not start_time:
        raise HTTPException(status_code=400, detail="Start time is required")
    
    # Validate appointment type is allowed
    if page.appointment_types and appointment_type not in page.appointment_types:
        raise HTTPException(status_code=400, detail="Appointment type not allowed for this booking page")
    
    # Validate duration
    if duration_minutes not in page.duration_options:
        raise HTTPException(status_code=400, detail="Duration not available for this booking page")
    
    # Create appointment
    appointment = Appointment(
        title=f"{appointment_type.value.replace('_', ' ').title()} - {customer_name}",
        appointment_type=appointment_type,
        start_time=start_time,
        end_time=start_time + timedelta(minutes=duration_minutes),
        duration_minutes=duration_minutes,
        customer_id=f"cust_{uuid.uuid4().hex[:8]}",
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        agent_id=page.agent_id,
        booking_source=BookingSource.WEBSITE,
        booked_by=page_id,
        custom_fields=custom_fields or {}
    )
    
    # Check availability
    conflicts = [
        a for a in appointments
        if (a.agent_id == appointment.agent_id and
            a.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW] and
            not (appointment.end_time <= a.start_time or appointment.start_time >= a.end_time))
    ]
    
    if conflicts:
        raise HTTPException(status_code=409, detail="Selected time slot is no longer available")
    
    appointments.append(appointment)
    
    # Update booking page stats
    page.bookings_count += 1
    page.conversion_rate = (page.bookings_count / max(page.page_views, 1)) * 100
    
    logger.info(f"Booked appointment via page {page_id}: {appointment.title}")
    return {
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id,
        "confirmation_message": page.confirmation_message,
        "appointment_details": {
            "title": appointment.title,
            "start_time": appointment.start_time,
            "duration_minutes": appointment.duration_minutes,
            "location": appointment.location_details or "Details will be provided separately"
        }
    }

# Calendar Integration Endpoints
@app.get("/calendar/integrations", response_model=List[CalendarIntegration])
async def get_calendar_integrations(agent_id: Optional[str] = None):
    """Get calendar integrations"""
    integrations = calendar_integrations.copy()
    if agent_id:
        integrations = [i for i in integrations if i.agent_id == agent_id]
    
    return integrations

@app.post("/calendar/integrations", response_model=CalendarIntegration)
async def create_calendar_integration(integration_data: CalendarIntegration):
    """Create a new calendar integration"""
    calendar_integrations.append(integration_data)
    logger.info(f"Created calendar integration: {integration_data.name}")
    return integration_data

@app.put("/calendar/integrations/{integration_id}/sync")
async def sync_calendar_integration(integration_id: str):
    """Manually trigger calendar sync"""
    integration = next((i for i in calendar_integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Calendar integration not found")
    
    if not integration.sync_enabled:
        raise HTTPException(status_code=400, detail="Sync is disabled for this integration")
    
    # Mock sync process
    integration.last_sync_at = datetime.now()
    integration.status = "active"
    
    logger.info(f"Synced calendar integration: {integration.name}")
    return {"message": "Calendar sync completed successfully"}

# Analytics Endpoints
@app.get("/analytics/overview")
async def get_scheduling_analytics():
    """Get comprehensive scheduling analytics"""
    
    total_appointments = len(appointments)
    confirmed_appointments = len([a for a in appointments if a.status == AppointmentStatus.CONFIRMED])
    completed_appointments = len([a for a in appointments if a.status == AppointmentStatus.COMPLETED])
    cancelled_appointments = len([a for a in appointments if a.status == AppointmentStatus.CANCELLED])
    no_shows = len([a for a in appointments if a.status == AppointmentStatus.NO_SHOW])
    
    # Calculate rates
    confirmation_rate = (confirmed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    cancellation_rate = (cancelled_appointments / total_appointments * 100) if total_appointments > 0 else 0
    no_show_rate = (no_shows / total_appointments * 100) if total_appointments > 0 else 0
    
    # Booking sources
    booking_sources = {}
    for source in BookingSource:
        count = len([a for a in appointments if a.booking_source == source])
        if count > 0:
            booking_sources[source.value] = count
    
    # Appointment types
    appointment_types = {}
    for apt_type in AppointmentType:
        count = len([a for a in appointments if a.appointment_type == apt_type])
        if count > 0:
            appointment_types[apt_type.value] = count
    
    # Recent activity
    recent_bookings = len([a for a in appointments if a.booked_at > datetime.now() - timedelta(hours=24)])
    upcoming_appointments = len([a for a in appointments if a.start_time > datetime.now() and a.start_time < datetime.now() + timedelta(days=7)])
    
    return {
        "summary": {
            "total_appointments": total_appointments,
            "confirmed_appointments": confirmed_appointments,
            "completed_appointments": completed_appointments,
            "cancelled_appointments": cancelled_appointments,
            "no_shows": no_shows,
            "active_booking_pages": len([p for p in booking_pages if p.is_active]),
            "calendar_integrations": len(calendar_integrations)
        },
        "performance_metrics": {
            "confirmation_rate": round(confirmation_rate, 1),
            "completion_rate": round(completion_rate, 1),
            "cancellation_rate": round(cancellation_rate, 1),
            "no_show_rate": round(no_show_rate, 1),
            "average_lead_time_hours": 48.5,  # Mock data
            "booking_conversion_rate": 23.5  # Mock data
        },
        "distribution": {
            "by_status": {status.value: len([a for a in appointments if a.status == status]) for status in AppointmentStatus},
            "by_type": appointment_types,
            "by_booking_source": booking_sources
        },
        "recent_activity": {
            "bookings_24h": recent_bookings,
            "upcoming_7d": upcoming_appointments,
            "reminders_sent_24h": 12,  # Mock data
            "calendar_syncs_24h": 8  # Mock data
        },
        "capacity_utilization": {
            "overall_utilization": 67.3,  # Mock data
            "peak_hours": [9, 10, 14, 15],
            "available_slots_next_7d": 124  # Mock data
        }
    }

@app.get("/analytics/trends")
async def get_scheduling_trends(days: int = 30):
    """Get scheduling trends over time"""
    
    trend_data = []
    for i in range(days, 0, -1):
        date_obj = datetime.now() - timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Calculate daily metrics (simplified for demo)
        daily_appointments = len([a for a in appointments if a.booked_at.date() == date_obj.date()])
        daily_confirmations = len([a for a in appointments if a.confirmation_sent_at and a.confirmation_sent_at.date() == date_obj.date()])
        
        trend_data.append({
            "date": date_str,
            "appointments_booked": max(0, daily_appointments + (i % 4)),  # Add variation
            "appointments_confirmed": max(0, daily_confirmations + (i % 3)),
            "cancellations": max(0, (i % 7 == 0)),
            "no_shows": max(0, (i % 10 == 0)),
            "utilization_rate": min(100, 60 + (i % 25))
        })
    
    return {
        "period_days": days,
        "trend_data": trend_data,
        "summary": {
            "total_booked": sum(d["appointments_booked"] for d in trend_data),
            "total_confirmed": sum(d["appointments_confirmed"] for d in trend_data),
            "total_cancellations": sum(d["cancellations"] for d in trend_data),
            "total_no_shows": sum(d["no_shows"] for d in trend_data),
            "average_utilization": sum(d["utilization_rate"] for d in trend_data) / len(trend_data)
        }
    }

@app.get("/analytics/agent-performance")
async def get_agent_scheduling_performance():
    """Get agent-specific scheduling performance"""
    
    agent_stats = {}
    
    for appointment in appointments:
        if not appointment.agent_id:
            continue
            
        if appointment.agent_id not in agent_stats:
            agent_stats[appointment.agent_id] = {
                "agent_id": appointment.agent_id,
                "agent_name": appointment.agent_name,
                "total_appointments": 0,
                "completed": 0,
                "cancelled": 0,
                "no_shows": 0,
                "avg_rating": 0,
                "total_ratings": 0
            }
        
        stats = agent_stats[appointment.agent_id]
        stats["total_appointments"] += 1
        
        if appointment.status == AppointmentStatus.COMPLETED:
            stats["completed"] += 1
        elif appointment.status == AppointmentStatus.CANCELLED:
            stats["cancelled"] += 1
        elif appointment.status == AppointmentStatus.NO_SHOW:
            stats["no_shows"] += 1
        
        if appointment.customer_rating:
            stats["avg_rating"] = ((stats["avg_rating"] * stats["total_ratings"]) + appointment.customer_rating) / (stats["total_ratings"] + 1)
            stats["total_ratings"] += 1
    
    # Calculate rates
    for stats in agent_stats.values():
        if stats["total_appointments"] > 0:
            stats["completion_rate"] = (stats["completed"] / stats["total_appointments"]) * 100
            stats["cancellation_rate"] = (stats["cancelled"] / stats["total_appointments"]) * 100
            stats["no_show_rate"] = (stats["no_shows"] / stats["total_appointments"]) * 100
        else:
            stats["completion_rate"] = 0
            stats["cancellation_rate"] = 0
            stats["no_show_rate"] = 0
    
    # Sort by completion rate
    sorted_agents = sorted(agent_stats.values(), key=lambda x: x["completion_rate"], reverse=True)
    
    return {
        "total_agents": len(agent_stats),
        "agent_performance": sorted_agents
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8017)
