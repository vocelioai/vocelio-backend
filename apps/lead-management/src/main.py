"""
Lead Management Service - Vocelio AI Call Center
Comprehensive lead tracking, scoring, nurturing, and pipeline management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Lead Management Models
class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    NURTURING = "nurturing"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    RECYCLED = "recycled"
    DISQUALIFIED = "disqualified"

class LeadSource(str, Enum):
    WEBSITE = "website"
    COLD_CALLING = "cold_calling"
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    TRADE_SHOW = "trade_show"
    WEBINAR = "webinar"
    CONTENT_DOWNLOAD = "content_download"
    PARTNER = "partner"
    ADVERTISING = "advertising"
    DIRECT_MAIL = "direct_mail"
    OTHER = "other"

class LeadPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class LeadTemperature(str, Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    BURNING = "burning"

class ScoringCriteria(str, Enum):
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    ENGAGEMENT = "engagement"
    FIRMOGRAPHIC = "firmographic"
    INTENT = "intent"

class NurturingStage(str, Enum):
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    EVALUATION = "evaluation"
    DECISION = "decision"
    RETENTION = "retention"

class ContactMethod(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"

class LeadScore(BaseModel):
    total_score: int = 0
    demographic_score: int = 0
    behavioral_score: int = 0
    engagement_score: int = 0
    firmographic_score: int = 0
    intent_score: int = 0
    
    # Score breakdown
    score_factors: Dict[str, int] = {}
    score_history: List[Dict[str, Any]] = []
    last_calculated: datetime = Field(default_factory=datetime.now)
    
    # Grade and classification
    grade: str = "D"  # A, B, C, D based on score ranges
    temperature: LeadTemperature = LeadTemperature.COLD
    priority: LeadPriority = LeadPriority.LOW

class ContactAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contact_method: ContactMethod
    attempted_at: datetime = Field(default_factory=datetime.now)
    attempted_by: str  # Agent ID
    
    # Contact details
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    
    # Outcome
    successful: bool = False
    connected: bool = False
    response_received: bool = False
    outcome_notes: Optional[str] = None
    call_duration: Optional[int] = None  # in seconds
    
    # Follow-up
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None

class LeadActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    activity_type: str  # "call", "email", "meeting", "note", "task", "score_change"
    activity_date: datetime = Field(default_factory=datetime.now)
    performed_by: str  # Agent or system ID
    
    # Activity details
    title: str
    description: str
    outcome: Optional[str] = None
    next_action: Optional[str] = None
    
    # Related data
    call_id: Optional[str] = None
    email_id: Optional[str] = None
    campaign_id: Optional[str] = None
    
    # Impact tracking
    score_impact: int = 0
    status_change: Optional[str] = None
    temperature_change: Optional[str] = None

class NurturingSequence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    stage: NurturingStage
    
    # Sequence configuration
    total_steps: int
    current_step: int = 1
    step_interval_days: int = 3
    
    # Content and automation
    steps: List[Dict[str, Any]] = []  # Sequence step definitions
    triggers: List[str] = []  # Trigger conditions
    success_criteria: List[str] = []
    exit_criteria: List[str] = []
    
    # Performance
    enrollment_count: int = 0
    completion_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Basic information
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    
    # Lead details
    status: LeadStatus = LeadStatus.NEW
    source: LeadSource
    priority: LeadPriority = LeadPriority.MEDIUM
    temperature: LeadTemperature = LeadTemperature.COLD
    
    # Scoring and qualification
    lead_score: LeadScore = Field(default_factory=LeadScore)
    qualification_score: int = 0
    budget_qualified: Optional[bool] = None
    authority_qualified: Optional[bool] = None
    need_qualified: Optional[bool] = None
    timeline_qualified: Optional[bool] = None
    
    # Assignment and ownership
    assigned_to: Optional[str] = None  # Agent ID
    assigned_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    next_contact_date: Optional[datetime] = None
    
    # Engagement tracking
    contact_attempts: List[ContactAttempt] = []
    activities: List[LeadActivity] = []
    total_touchpoints: int = 0
    engagement_score: int = 0
    
    # Company information (firmographic data)
    company_size: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    
    # Behavioral data
    website_visits: int = 0
    page_views: int = 0
    content_downloads: int = 0
    email_opens: int = 0
    email_clicks: int = 0
    social_engagement: int = 0
    
    # Nurturing and automation
    nurturing_sequence_id: Optional[str] = None
    nurturing_step: int = 0
    nurturing_started: Optional[datetime] = None
    
    # Sales pipeline
    pipeline_stage: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[float] = None
    expected_close_date: Optional[datetime] = None
    
    # Communication preferences
    preferred_contact_method: Optional[ContactMethod] = None
    contact_time_preference: Optional[str] = None  # "morning", "afternoon", "evening"
    timezone: str = "UTC"
    do_not_call: bool = False
    do_not_email: bool = False
    
    # Conversion tracking
    conversion_date: Optional[datetime] = None
    conversion_value: Optional[Decimal] = None
    conversion_source: Optional[str] = None
    
    # Custom fields and tags
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []
    notes: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None

class LeadPipeline(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Pipeline stages
    stages: List[Dict[str, Any]] = []  # Stage definitions with conversion rates
    default_stage: str
    
    # Pipeline metrics
    total_leads: int = 0
    total_value: Decimal = Decimal('0')
    average_deal_size: Decimal = Decimal('0')
    average_sales_cycle: int = 0  # days
    conversion_rate: float = 0.0
    
    # Stage metrics
    stage_metrics: Dict[str, Dict[str, Any]] = {}
    
    # Configuration
    is_active: bool = True
    organization_id: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class LeadCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    campaign_type: str  # "email", "calling", "multi_channel", "nurturing"
    
    # Campaign configuration
    target_audience: Dict[str, Any] = {}
    messaging: Dict[str, Any] = {}
    schedule: Dict[str, Any] = {}
    
    # Lead assignment
    assigned_leads: List[str] = []  # Lead IDs
    lead_criteria: Dict[str, Any] = {}
    
    # Performance tracking
    total_leads: int = 0
    contacted_leads: int = 0
    responded_leads: int = 0
    converted_leads: int = 0
    
    # Results
    response_rate: float = 0.0
    conversion_rate: float = 0.0
    cost_per_lead: Decimal = Decimal('0')
    roi: float = 0.0
    
    # Status and timing
    status: str = "draft"  # "draft", "active", "paused", "completed"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

class LeadAnalytics(BaseModel):
    time_period: str
    total_leads: int
    new_leads: int
    qualified_leads: int
    converted_leads: int
    
    # Conversion metrics
    qualification_rate: float
    conversion_rate: float
    average_lead_score: float
    average_sales_cycle: int
    
    # Source performance
    source_breakdown: Dict[str, int] = {}
    source_conversion_rates: Dict[str, float] = {}
    
    # Agent performance
    agent_performance: List[Dict[str, Any]] = []
    
    # Trends
    daily_leads: List[Dict[str, Any]] = []
    score_distribution: Dict[str, int] = {}
    status_distribution: Dict[str, int] = {}

# Sample data
SAMPLE_LEADS = [
    Lead(
        first_name="Sarah",
        last_name="Johnson",
        email="sarah.johnson@techcorp.com",
        phone="+1-555-0123",
        company="TechCorp Solutions",
        title="VP of Operations",
        source=LeadSource.WEBINAR,
        status=LeadStatus.QUALIFIED,
        priority=LeadPriority.HIGH,
        temperature=LeadTemperature.HOT,
        lead_score=LeadScore(
            total_score=89,
            demographic_score=18,
            behavioral_score=22,
            engagement_score=25,
            firmographic_score=15,
            intent_score=9,
            grade="A",
            temperature=LeadTemperature.HOT,
            priority=LeadPriority.HIGH
        ),
        qualification_score=92,
        budget_qualified=True,
        authority_qualified=True,
        need_qualified=True,
        timeline_qualified=True,
        company_size="500-1000",
        industry="Technology",
        annual_revenue="$50M-100M",
        website_visits=12,
        page_views=45,
        content_downloads=3,
        email_opens=8,
        email_clicks=5,
        estimated_value=Decimal('75000'),
        probability=0.75,
        assigned_to="agent_001",
        assigned_at=datetime.now() - timedelta(days=5),
        last_contacted=datetime.now() - timedelta(days=2),
        next_contact_date=datetime.now() + timedelta(days=1),
        tags=["enterprise", "decision_maker", "high_intent"]
    ),
    Lead(
        first_name="Michael",
        last_name="Chen",
        email="m.chen@startupinc.com",
        phone="+1-555-0456",
        company="StartupInc",
        title="CTO",
        source=LeadSource.CONTENT_DOWNLOAD,
        status=LeadStatus.NURTURING,
        priority=LeadPriority.MEDIUM,
        temperature=LeadTemperature.WARM,
        lead_score=LeadScore(
            total_score=67,
            demographic_score=15,
            behavioral_score=18,
            engagement_score=20,
            firmographic_score=10,
            intent_score=4,
            grade="B",
            temperature=LeadTemperature.WARM,
            priority=LeadPriority.MEDIUM
        ),
        qualification_score=78,
        budget_qualified=True,
        authority_qualified=True,
        need_qualified=True,
        timeline_qualified=False,
        company_size="50-100",
        industry="Software",
        annual_revenue="$5M-10M",
        website_visits=6,
        page_views=18,
        content_downloads=2,
        email_opens=4,
        email_clicks=2,
        estimated_value=Decimal('25000'),
        probability=0.45,
        nurturing_sequence_id="seq_001",
        nurturing_step=3,
        assigned_to="agent_002",
        tags=["startup", "tech_savvy", "budget_conscious"]
    ),
    Lead(
        first_name="Lisa",
        last_name="Rodriguez",
        email="lisa.r@enterprise.com",
        phone="+1-555-0789",
        company="Enterprise Corp",
        title="Director of Sales",
        source=LeadSource.COLD_CALLING,
        status=LeadStatus.CONTACTED,
        priority=LeadPriority.HIGH,
        temperature=LeadTemperature.WARM,
        lead_score=LeadScore(
            total_score=74,
            demographic_score=16,
            behavioral_score=15,
            engagement_score=18,
            firmographic_score=18,
            intent_score=7,
            grade="B",
            temperature=LeadTemperature.WARM,
            priority=LeadPriority.HIGH
        ),
        qualification_score=85,
        budget_qualified=True,
        authority_qualified=False,
        need_qualified=True,
        timeline_qualified=True,
        company_size="1000+",
        industry="Manufacturing",
        annual_revenue="$100M+",
        website_visits=8,
        page_views=25,
        content_downloads=1,
        email_opens=6,
        email_clicks=3,
        estimated_value=Decimal('120000'),
        probability=0.55,
        assigned_to="agent_003",
        last_contacted=datetime.now() - timedelta(hours=6),
        next_contact_date=datetime.now() + timedelta(days=3),
        tags=["enterprise", "manufacturing", "multiple_stakeholders"]
    )
]

SAMPLE_NURTURING_SEQUENCES = [
    NurturingSequence(
        id="seq_001",
        name="Software Solution Nurturing",
        description="7-step nurturing sequence for software solution prospects",
        stage=NurturingStage.CONSIDERATION,
        total_steps=7,
        current_step=1,
        step_interval_days=3,
        steps=[
            {"step": 1, "type": "email", "subject": "Welcome - Let's explore your needs", "template": "welcome_email"},
            {"step": 2, "type": "call", "purpose": "discovery", "script": "discovery_script"},
            {"step": 3, "type": "email", "subject": "Case study: Similar company success", "template": "case_study"},
            {"step": 4, "type": "call", "purpose": "demo_scheduling", "script": "demo_script"},
            {"step": 5, "type": "demo", "purpose": "product_demonstration", "duration": 45},
            {"step": 6, "type": "email", "subject": "Follow-up and proposal", "template": "proposal_email"},
            {"step": 7, "type": "call", "purpose": "closing", "script": "closing_script"}
        ],
        triggers=["content_download", "webinar_attendance"],
        success_criteria=["demo_completed", "proposal_requested"],
        exit_criteria=["unsubscribed", "not_qualified", "competitor_chosen"],
        enrollment_count=156,
        completion_rate=68.5,
        conversion_rate=23.7,
        is_active=True
    )
]

# Global storage
leads: List[Lead] = []
pipelines: List[LeadPipeline] = []
campaigns: List[LeadCampaign] = []
nurturing_sequences: List[NurturingSequence] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global leads, nurturing_sequences
    
    leads.extend(SAMPLE_LEADS)
    nurturing_sequences.extend(SAMPLE_NURTURING_SEQUENCES)
    
    # Create sample pipeline
    sample_pipeline = LeadPipeline(
        name="Standard Sales Pipeline",
        description="Default sales pipeline for lead progression",
        stages=[
            {"name": "New Lead", "order": 1, "conversion_rate": 100},
            {"name": "Contacted", "order": 2, "conversion_rate": 75},
            {"name": "Qualified", "order": 3, "conversion_rate": 60},
            {"name": "Proposal", "order": 4, "conversion_rate": 40},
            {"name": "Negotiation", "order": 5, "conversion_rate": 70},
            {"name": "Closed Won", "order": 6, "conversion_rate": 100}
        ],
        default_stage="New Lead",
        total_leads=len(leads),
        organization_id="vocelio_org",
        created_by="admin"
    )
    
    pipelines.append(sample_pipeline)
    
    # Create sample campaign
    sample_campaign = LeadCampaign(
        name="Q4 Enterprise Outreach",
        description="Targeted outreach to enterprise prospects for Q4 sales push",
        campaign_type="multi_channel",
        target_audience={"company_size": "500+", "industry": ["Technology", "Manufacturing"]},
        assigned_leads=[lead.id for lead in leads[:2]],
        total_leads=2,
        contacted_leads=2,
        responded_leads=1,
        converted_leads=0,
        response_rate=50.0,
        status="active",
        start_date=datetime.now() - timedelta(days=10)
    )
    
    campaigns.append(sample_campaign)
    
    logger.info("Sample lead management data initialized successfully")

async def calculate_lead_score(lead: Lead) -> LeadScore:
    """Calculate comprehensive lead score based on multiple factors"""
    
    score = LeadScore()
    
    # Demographic scoring (0-20 points)
    demographic_score = 0
    if lead.title and any(title in lead.title.lower() for title in ["vp", "director", "manager", "ceo", "cto", "cfo"]):
        demographic_score += 10
    if lead.company:
        demographic_score += 5
    if lead.phone:
        demographic_score += 3
    if lead.industry:
        demographic_score += 2
    score.demographic_score = min(demographic_score, 20)
    
    # Behavioral scoring (0-25 points)
    behavioral_score = 0
    behavioral_score += min(lead.website_visits * 2, 10)
    behavioral_score += min(lead.content_downloads * 5, 10)
    behavioral_score += min(lead.page_views, 5)
    score.behavioral_score = min(behavioral_score, 25)
    
    # Engagement scoring (0-25 points)
    engagement_score = 0
    engagement_score += min(lead.email_opens * 2, 10)
    engagement_score += min(lead.email_clicks * 3, 10)
    engagement_score += min(lead.social_engagement, 5)
    score.engagement_score = min(engagement_score, 25)
    
    # Firmographic scoring (0-20 points)
    firmographic_score = 0
    if lead.company_size:
        size_scores = {"1-10": 2, "11-50": 5, "51-200": 10, "201-500": 15, "500+": 20}
        firmographic_score += size_scores.get(lead.company_size, 0)
    if lead.annual_revenue:
        revenue_scores = {"<$1M": 2, "$1M-5M": 5, "$5M-10M": 8, "$10M-50M": 12, "$50M+": 15}
        for range_key, points in revenue_scores.items():
            if range_key in lead.annual_revenue:
                firmographic_score += points
                break
    score.firmographic_score = min(firmographic_score, 20)
    
    # Intent scoring (0-10 points)
    intent_score = 0
    if lead.source in [LeadSource.WEBINAR, LeadSource.CONTENT_DOWNLOAD]:
        intent_score += 5
    if lead.next_contact_date and lead.next_contact_date <= datetime.now() + timedelta(days=7):
        intent_score += 3
    if len(lead.contact_attempts) > 0:
        intent_score += 2
    score.intent_score = min(intent_score, 10)
    
    # Calculate total score
    score.total_score = (score.demographic_score + score.behavioral_score + 
                        score.engagement_score + score.firmographic_score + score.intent_score)
    
    # Assign grade and temperature
    if score.total_score >= 80:
        score.grade = "A"
        score.temperature = LeadTemperature.HOT
        score.priority = LeadPriority.URGENT
    elif score.total_score >= 60:
        score.grade = "B"
        score.temperature = LeadTemperature.WARM
        score.priority = LeadPriority.HIGH
    elif score.total_score >= 40:
        score.grade = "C"
        score.temperature = LeadTemperature.WARM
        score.priority = LeadPriority.MEDIUM
    else:
        score.grade = "D"
        score.temperature = LeadTemperature.COLD
        score.priority = LeadPriority.LOW
    
    score.last_calculated = datetime.now()
    
    # Store scoring factors
    score.score_factors = {
        "demographic": score.demographic_score,
        "behavioral": score.behavioral_score,
        "engagement": score.engagement_score,
        "firmographic": score.firmographic_score,
        "intent": score.intent_score
    }
    
    return score

async def update_lead_score(lead_id: str) -> Lead:
    """Update lead score and temperature"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        return None
    
    # Calculate new score
    new_score = await calculate_lead_score(lead)
    
    # Track score history
    old_score = lead.lead_score.total_score
    score_change = new_score.total_score - old_score
    
    new_score.score_history.append({
        "date": datetime.now().isoformat(),
        "old_score": old_score,
        "new_score": new_score.total_score,
        "change": score_change,
        "reason": "automatic_recalculation"
    })
    
    lead.lead_score = new_score
    lead.temperature = new_score.temperature
    lead.priority = new_score.priority
    lead.updated_at = datetime.now()
    
    # Add activity record
    activity = LeadActivity(
        activity_type="score_change",
        title="Lead Score Updated",
        description=f"Lead score changed from {old_score} to {new_score.total_score} (change: {score_change:+d})",
        performed_by="system",
        score_impact=score_change,
        temperature_change=f"{old_score} -> {new_score.total_score}"
    )
    
    lead.activities.append(activity)
    
    return lead

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Lead Management Service",
    description="Comprehensive lead tracking, scoring, nurturing, and pipeline management for Vocelio AI Call Center",
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
        "service": "lead-management",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Lead Management Endpoints
@app.get("/leads", response_model=List[Lead])
async def get_leads(
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    priority: Optional[LeadPriority] = None,
    temperature: Optional[LeadTemperature] = None,
    assigned_to: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "lead_score.total_score",  # "created_at", "lead_score.total_score", "last_activity"
    limit: int = 50,
    offset: int = 0
):
    """Get leads with filtering and sorting options"""
    
    filtered_leads = leads.copy()
    
    # Apply filters
    if status:
        filtered_leads = [l for l in filtered_leads if l.status == status]
    
    if source:
        filtered_leads = [l for l in filtered_leads if l.source == source]
    
    if priority:
        filtered_leads = [l for l in filtered_leads if l.priority == priority]
    
    if temperature:
        filtered_leads = [l for l in filtered_leads if l.temperature == temperature]
    
    if assigned_to:
        filtered_leads = [l for l in filtered_leads if l.assigned_to == assigned_to]
    
    if min_score:
        filtered_leads = [l for l in filtered_leads if l.lead_score.total_score >= min_score]
    
    if max_score:
        filtered_leads = [l for l in filtered_leads if l.lead_score.total_score <= max_score]
    
    if search:
        search_lower = search.lower()
        filtered_leads = [
            l for l in filtered_leads
            if (search_lower in l.first_name.lower() or 
                search_lower in l.last_name.lower() or
                search_lower in l.email.lower() or
                (l.company and search_lower in l.company.lower()))
        ]
    
    # Apply sorting
    if sort_by == "lead_score.total_score":
        filtered_leads.sort(key=lambda x: x.lead_score.total_score, reverse=True)
    elif sort_by == "created_at":
        filtered_leads.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "last_activity":
        filtered_leads.sort(key=lambda x: x.last_activity or x.created_at, reverse=True)
    
    # Apply pagination
    return filtered_leads[offset:offset + limit]

@app.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    """Get a specific lead by ID"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.post("/leads", response_model=Lead)
async def create_lead(lead_data: Lead):
    """Create a new lead"""
    # Calculate initial lead score
    lead_data.lead_score = await calculate_lead_score(lead_data)
    lead_data.temperature = lead_data.lead_score.temperature
    lead_data.priority = lead_data.lead_score.priority
    
    leads.append(lead_data)
    logger.info(f"Created new lead: {lead_data.first_name} {lead_data.last_name} ({lead_data.email})")
    return lead_data

@app.put("/leads/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, lead_data: Lead):
    """Update an existing lead"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update fields
    for field, value in lead_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(lead, field, value)
    
    # Recalculate score if relevant data changed
    lead.lead_score = await calculate_lead_score(lead)
    lead.temperature = lead.lead_score.temperature
    lead.priority = lead.lead_score.priority
    lead.updated_at = datetime.now()
    
    logger.info(f"Updated lead: {lead.first_name} {lead.last_name}")
    return lead

@app.put("/leads/{lead_id}/status")
async def update_lead_status(lead_id: str, status: LeadStatus, notes: Optional[str] = None):
    """Update lead status"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    old_status = lead.status
    lead.status = status
    lead.updated_at = datetime.now()
    lead.last_activity = datetime.now()
    
    # Add activity record
    activity = LeadActivity(
        activity_type="status_change",
        title=f"Status Changed: {old_status.value} → {status.value}",
        description=notes or f"Lead status updated from {old_status.value} to {status.value}",
        performed_by="agent",
        status_change=f"{old_status.value} -> {status.value}"
    )
    
    lead.activities.append(activity)
    
    logger.info(f"Updated lead {lead_id} status to {status}")
    return {"message": f"Lead status updated to {status}"}

@app.put("/leads/{lead_id}/assign")
async def assign_lead(lead_id: str, agent_id: str):
    """Assign lead to an agent"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    old_agent = lead.assigned_to
    lead.assigned_to = agent_id
    lead.assigned_at = datetime.now()
    lead.updated_at = datetime.now()
    
    # Add activity record
    activity = LeadActivity(
        activity_type="assignment",
        title="Lead Assigned",
        description=f"Lead assigned from {old_agent or 'unassigned'} to {agent_id}",
        performed_by=agent_id
    )
    
    lead.activities.append(activity)
    
    logger.info(f"Assigned lead {lead_id} to agent {agent_id}")
    return {"message": f"Lead assigned to {agent_id}"}

# Lead Scoring Endpoints
@app.put("/leads/{lead_id}/score/recalculate")
async def recalculate_lead_score(lead_id: str):
    """Recalculate lead score"""
    updated_lead = await update_lead_score(lead_id)
    if not updated_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "message": "Lead score recalculated",
        "lead_id": lead_id,
        "new_score": updated_lead.lead_score.total_score,
        "grade": updated_lead.lead_score.grade,
        "temperature": updated_lead.temperature.value
    }

@app.get("/leads/{lead_id}/score/history")
async def get_lead_score_history(lead_id: str):
    """Get lead score history"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "lead_id": lead_id,
        "current_score": lead.lead_score.total_score,
        "score_history": lead.lead_score.score_history,
        "score_breakdown": lead.lead_score.score_factors
    }

@app.get("/scoring/distribution")
async def get_score_distribution():
    """Get lead score distribution analytics"""
    
    score_ranges = {
        "A (80-100)": len([l for l in leads if l.lead_score.total_score >= 80]),
        "B (60-79)": len([l for l in leads if 60 <= l.lead_score.total_score < 80]),
        "C (40-59)": len([l for l in leads if 40 <= l.lead_score.total_score < 60]),
        "D (0-39)": len([l for l in leads if l.lead_score.total_score < 40])
    }
    
    temperature_distribution = {}
    for temp in LeadTemperature:
        temperature_distribution[temp.value] = len([l for l in leads if l.temperature == temp])
    
    priority_distribution = {}
    for priority in LeadPriority:
        priority_distribution[priority.value] = len([l for l in leads if l.priority == priority])
    
    return {
        "total_leads": len(leads),
        "average_score": sum(l.lead_score.total_score for l in leads) / len(leads) if leads else 0,
        "score_distribution": score_ranges,
        "temperature_distribution": temperature_distribution,
        "priority_distribution": priority_distribution,
        "score_factors_avg": {
            "demographic": sum(l.lead_score.demographic_score for l in leads) / len(leads) if leads else 0,
            "behavioral": sum(l.lead_score.behavioral_score for l in leads) / len(leads) if leads else 0,
            "engagement": sum(l.lead_score.engagement_score for l in leads) / len(leads) if leads else 0,
            "firmographic": sum(l.lead_score.firmographic_score for l in leads) / len(leads) if leads else 0,
            "intent": sum(l.lead_score.intent_score for l in leads) / len(leads) if leads else 0
        }
    }

# Contact Tracking Endpoints
@app.post("/leads/{lead_id}/contact")
async def record_contact_attempt(lead_id: str, contact_attempt: ContactAttempt):
    """Record a contact attempt for a lead"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.contact_attempts.append(contact_attempt)
    lead.total_touchpoints += 1
    lead.last_contacted = contact_attempt.attempted_at
    lead.updated_at = datetime.now()
    lead.last_activity = datetime.now()
    
    # Set next contact date if follow-up required
    if contact_attempt.follow_up_required and contact_attempt.follow_up_date:
        lead.next_contact_date = contact_attempt.follow_up_date
    
    # Add activity record
    activity = LeadActivity(
        activity_type="contact",
        title=f"{contact_attempt.contact_method.value.title()} Contact",
        description=contact_attempt.outcome_notes or f"Contact attempt via {contact_attempt.contact_method.value}",
        performed_by=contact_attempt.attempted_by,
        outcome="successful" if contact_attempt.successful else "unsuccessful"
    )
    
    lead.activities.append(activity)
    
    # Update lead score based on engagement
    if contact_attempt.successful:
        lead.engagement_score += 2
        await update_lead_score(lead_id)
    
    logger.info(f"Recorded contact attempt for lead {lead_id}")
    return {"message": "Contact attempt recorded successfully"}

@app.get("/leads/{lead_id}/contacts")
async def get_lead_contacts(lead_id: str):
    """Get all contact attempts for a lead"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "lead_id": lead_id,
        "total_attempts": len(lead.contact_attempts),
        "successful_attempts": len([c for c in lead.contact_attempts if c.successful]),
        "last_contact": lead.last_contacted,
        "next_contact": lead.next_contact_date,
        "contact_attempts": lead.contact_attempts
    }

# Lead Activities Endpoints
@app.post("/leads/{lead_id}/activity")
async def add_lead_activity(lead_id: str, activity: LeadActivity):
    """Add an activity to a lead"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.activities.append(activity)
    lead.updated_at = datetime.now()
    lead.last_activity = activity.activity_date
    
    # Update lead score if activity has score impact
    if activity.score_impact != 0:
        await update_lead_score(lead_id)
    
    logger.info(f"Added activity to lead {lead_id}: {activity.title}")
    return {"message": "Activity added successfully"}

@app.get("/leads/{lead_id}/activities")
async def get_lead_activities(lead_id: str, limit: int = 50):
    """Get activities for a lead"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Sort activities by date, most recent first
    sorted_activities = sorted(lead.activities, key=lambda x: x.activity_date, reverse=True)
    
    return {
        "lead_id": lead_id,
        "total_activities": len(lead.activities),
        "activities": sorted_activities[:limit]
    }

# Nurturing Sequences Endpoints
@app.get("/nurturing/sequences", response_model=List[NurturingSequence])
async def get_nurturing_sequences():
    """Get all nurturing sequences"""
    return nurturing_sequences

@app.post("/nurturing/sequences", response_model=NurturingSequence)
async def create_nurturing_sequence(sequence_data: NurturingSequence):
    """Create a new nurturing sequence"""
    nurturing_sequences.append(sequence_data)
    logger.info(f"Created nurturing sequence: {sequence_data.name}")
    return sequence_data

@app.put("/leads/{lead_id}/nurturing/enroll")
async def enroll_lead_in_nurturing(lead_id: str, sequence_id: str):
    """Enroll a lead in a nurturing sequence"""
    lead = next((l for l in leads if l.id == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    sequence = next((s for s in nurturing_sequences if s.id == sequence_id), None)
    if not sequence:
        raise HTTPException(status_code=404, detail="Nurturing sequence not found")
    
    lead.nurturing_sequence_id = sequence_id
    lead.nurturing_step = 1
    lead.nurturing_started = datetime.now()
    lead.updated_at = datetime.now()
    
    # Update sequence enrollment count
    sequence.enrollment_count += 1
    
    # Add activity record
    activity = LeadActivity(
        activity_type="nurturing",
        title="Enrolled in Nurturing Sequence",
        description=f"Enrolled in '{sequence.name}' nurturing sequence",
        performed_by="system"
    )
    
    lead.activities.append(activity)
    
    logger.info(f"Enrolled lead {lead_id} in nurturing sequence {sequence_id}")
    return {"message": f"Lead enrolled in nurturing sequence: {sequence.name}"}

# Pipeline Management Endpoints
@app.get("/pipelines", response_model=List[LeadPipeline])
async def get_pipelines():
    """Get all lead pipelines"""
    return pipelines

@app.get("/pipelines/{pipeline_id}/metrics")
async def get_pipeline_metrics(pipeline_id: str):
    """Get metrics for a specific pipeline"""
    pipeline = next((p for p in pipelines if p.id == pipeline_id), None)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    # Calculate pipeline metrics
    pipeline_leads = [l for l in leads if l.pipeline_stage]
    total_value = sum(l.estimated_value or 0 for l in pipeline_leads)
    
    stage_metrics = {}
    for stage in pipeline.stages:
        stage_leads = [l for l in pipeline_leads if l.pipeline_stage == stage["name"]]
        stage_value = sum(l.estimated_value or 0 for l in stage_leads)
        
        stage_metrics[stage["name"]] = {
            "lead_count": len(stage_leads),
            "total_value": float(stage_value),
            "average_value": float(stage_value / len(stage_leads)) if stage_leads else 0,
            "conversion_rate": stage.get("conversion_rate", 0)
        }
    
    return {
        "pipeline_id": pipeline_id,
        "pipeline_name": pipeline.name,
        "total_leads": len(pipeline_leads),
        "total_value": float(total_value),
        "average_deal_size": float(total_value / len(pipeline_leads)) if pipeline_leads else 0,
        "stage_metrics": stage_metrics
    }

# Campaign Management Endpoints
@app.get("/campaigns", response_model=List[LeadCampaign])
async def get_campaigns():
    """Get all lead campaigns"""
    return campaigns

@app.post("/campaigns", response_model=LeadCampaign)
async def create_campaign(campaign_data: LeadCampaign):
    """Create a new lead campaign"""
    campaigns.append(campaign_data)
    logger.info(f"Created campaign: {campaign_data.name}")
    return campaign_data

@app.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(campaign_id: str):
    """Get performance metrics for a campaign"""
    campaign = next((c for c in campaigns if c.id == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get leads associated with this campaign
    campaign_leads = [l for l in leads if l.id in campaign.assigned_leads]
    
    # Calculate performance metrics
    total_leads = len(campaign_leads)
    contacted_leads = len([l for l in campaign_leads if l.last_contacted])
    qualified_leads = len([l for l in campaign_leads if l.status == LeadStatus.QUALIFIED])
    converted_leads = len([l for l in campaign_leads if l.status == LeadStatus.CLOSED_WON])
    
    response_rate = (contacted_leads / total_leads * 100) if total_leads > 0 else 0
    qualification_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "performance_metrics": {
            "total_leads": total_leads,
            "contacted_leads": contacted_leads,
            "qualified_leads": qualified_leads,
            "converted_leads": converted_leads,
            "response_rate": round(response_rate, 1),
            "qualification_rate": round(qualification_rate, 1),
            "conversion_rate": round(conversion_rate, 1)
        },
        "lead_breakdown": {
            "by_status": {status.value: len([l for l in campaign_leads if l.status == status]) for status in LeadStatus},
            "by_score_grade": {grade: len([l for l in campaign_leads if l.lead_score.grade == grade]) for grade in ["A", "B", "C", "D"]},
            "by_temperature": {temp.value: len([l for l in campaign_leads if l.temperature == temp]) for temp in LeadTemperature}
        }
    }

# Analytics Endpoints
@app.get("/analytics/overview")
async def get_lead_analytics_overview():
    """Get comprehensive lead management analytics"""
    
    total_leads = len(leads)
    new_leads_24h = len([l for l in leads if l.created_at > datetime.now() - timedelta(hours=24)])
    qualified_leads = len([l for l in leads if l.status == LeadStatus.QUALIFIED])
    converted_leads = len([l for l in leads if l.status == LeadStatus.CLOSED_WON])
    
    # Calculate rates
    qualification_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    average_score = sum(l.lead_score.total_score for l in leads) / total_leads if total_leads > 0 else 0
    
    # Source performance
    source_breakdown = {}
    for source in LeadSource:
        source_leads = [l for l in leads if l.source == source]
        if source_leads:
            source_breakdown[source.value] = {
                "count": len(source_leads),
                "conversion_rate": len([l for l in source_leads if l.status == LeadStatus.CLOSED_WON]) / len(source_leads) * 100,
                "average_score": sum(l.lead_score.total_score for l in source_leads) / len(source_leads)
            }
    
    # Agent performance
    agent_performance = {}
    assigned_leads_by_agent = {}
    for lead in leads:
        if lead.assigned_to:
            if lead.assigned_to not in assigned_leads_by_agent:
                assigned_leads_by_agent[lead.assigned_to] = []
            assigned_leads_by_agent[lead.assigned_to].append(lead)
    
    for agent_id, agent_leads in assigned_leads_by_agent.items():
        converted = len([l for l in agent_leads if l.status == LeadStatus.CLOSED_WON])
        agent_performance[agent_id] = {
            "total_leads": len(agent_leads),
            "converted_leads": converted,
            "conversion_rate": (converted / len(agent_leads) * 100) if agent_leads else 0,
            "average_score": sum(l.lead_score.total_score for l in agent_leads) / len(agent_leads) if agent_leads else 0
        }
    
    return {
        "summary": {
            "total_leads": total_leads,
            "new_leads_24h": new_leads_24h,
            "qualified_leads": qualified_leads,
            "converted_leads": converted_leads,
            "active_campaigns": len([c for c in campaigns if c.status == "active"]),
            "nurturing_sequences": len(nurturing_sequences)
        },
        "performance_metrics": {
            "qualification_rate": round(qualification_rate, 1),
            "conversion_rate": round(conversion_rate, 1),
            "average_lead_score": round(average_score, 1),
            "average_sales_cycle": 45,  # Mock data
            "pipeline_velocity": 12.5  # Mock data
        },
        "distribution": {
            "by_status": {status.value: len([l for l in leads if l.status == status]) for status in LeadStatus},
            "by_source": {source.value: len([l for l in leads if l.source == source]) for source in LeadSource},
            "by_temperature": {temp.value: len([l for l in leads if l.temperature == temp]) for temp in LeadTemperature},
            "by_priority": {priority.value: len([l for l in leads if l.priority == priority]) for priority in LeadPriority}
        },
        "source_performance": source_breakdown,
        "agent_performance": list(agent_performance.values())[:5],  # Top 5 agents
        "recent_activity": {
            "leads_created_7d": len([l for l in leads if l.created_at > datetime.now() - timedelta(days=7)]),
            "leads_contacted_24h": len([l for l in leads if l.last_contacted and l.last_contacted > datetime.now() - timedelta(hours=24)]),
            "status_changes_24h": len([l for l in leads if l.updated_at > datetime.now() - timedelta(hours=24)])
        }
    }

@app.get("/analytics/trends")
async def get_lead_trends(days: int = 30):
    """Get lead management trends over time"""
    
    trend_data = []
    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Calculate daily metrics (simplified for demo)
        leads_created = len([l for l in leads if l.created_at.date() == date.date()])
        leads_qualified = len([l for l in leads if l.status == LeadStatus.QUALIFIED and l.updated_at.date() == date.date()])
        leads_converted = len([l for l in leads if l.status == LeadStatus.CLOSED_WON and l.updated_at.date() == date.date()])
        
        trend_data.append({
            "date": date_str,
            "leads_created": max(0, leads_created + (i % 3)),  # Add some variation
            "leads_qualified": max(0, leads_qualified + (i % 2)),
            "leads_converted": max(0, leads_converted + (i % 5 == 0)),
            "average_score": min(100, 65 + (i % 20))
        })
    
    return {
        "period_days": days,
        "trend_data": trend_data,
        "summary": {
            "total_created": sum(d["leads_created"] for d in trend_data),
            "total_qualified": sum(d["leads_qualified"] for d in trend_data),
            "total_converted": sum(d["leads_converted"] for d in trend_data),
            "average_daily_score": sum(d["average_score"] for d in trend_data) / len(trend_data)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
