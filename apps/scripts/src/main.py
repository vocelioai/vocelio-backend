"""
Scripts Service - Vocelio AI Call Center
Dynamic conversation script generation, template management, and personalized call flows
"""

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

# Scripts Models
class ScriptType(str, Enum):
    SALES = "sales"
    CUSTOMER_SERVICE = "customer_service"
    LEAD_QUALIFICATION = "lead_qualification"
    APPOINTMENT_SETTING = "appointment_setting"
    FOLLOW_UP = "follow_up"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    GREETING = "greeting"
    ESCALATION = "escalation"
    SURVEY = "survey"
    COLLECTION = "collection"
    ONBOARDING = "onboarding"
    RETENTION = "retention"
    UPSELL = "upsell"
    CROSS_SELL = "cross_sell"

class ScriptStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"

class ConversationFlow(str, Enum):
    LINEAR = "linear"
    BRANCHING = "branching"
    ADAPTIVE = "adaptive"
    CONTEXTUAL = "contextual"

class PersonalizationLevel(str, Enum):
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    AI_POWERED = "ai_powered"

class ScriptVariable(BaseModel):
    name: str
    type: str = "string"  # "string", "number", "boolean", "date", "list"
    default_value: Optional[str] = None
    description: str
    required: bool = False
    validation_pattern: Optional[str] = None
    possible_values: Optional[List[str]] = None

class ConversationBranch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    condition: str  # Condition logic for branching
    next_section_id: Optional[str] = None
    script_content: str
    variables: List[ScriptVariable] = []
    suggested_responses: List[str] = []
    escalation_triggers: List[str] = []

class ScriptSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    order_index: int
    content: str
    purpose: str  # "opening", "information_gathering", "presentation", "objection_handling", "closing"
    
    # Branching logic
    branches: List[ConversationBranch] = []
    fallback_content: Optional[str] = None
    
    # Timing and pacing
    estimated_duration_seconds: int = 30
    pause_points: List[int] = []  # Character positions for natural pauses
    emphasis_points: List[int] = []  # Character positions for emphasis
    
    # Variables and personalization
    variables: List[ScriptVariable] = []
    personalization_tags: List[str] = []
    
    # Performance metrics
    success_rate: float = 0.0
    average_duration: float = 0.0
    conversion_impact: float = 0.0

class ScriptTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    script_type: ScriptType
    industry: str
    use_case: str
    
    # Structure
    sections: List[ScriptSection] = []
    flow_type: ConversationFlow = ConversationFlow.LINEAR
    personalization_level: PersonalizationLevel = PersonalizationLevel.BASIC
    
    # Configuration
    variables: List[ScriptVariable] = []
    required_data: List[str] = []  # Required customer data fields
    optional_data: List[str] = []  # Optional customer data fields
    
    # Quality and performance
    status: ScriptStatus = ScriptStatus.DRAFT
    version: str = "1.0.0"
    effectiveness_score: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    
    # Metadata
    created_by: str
    approved_by: Optional[str] = None
    tags: List[str] = []
    category: str
    language: str = "en-US"
    
    # Compliance and guidelines
    compliance_notes: List[str] = []
    legal_requirements: List[str] = []
    do_not_say: List[str] = []
    must_say: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

class GeneratedScript(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    customer_id: str
    agent_id: str
    campaign_id: Optional[str] = None
    
    # Generated content
    personalized_content: str
    variables_used: Dict[str, Any] = {}
    personalization_data: Dict[str, Any] = {}
    
    # Context
    call_context: Dict[str, Any] = {}
    customer_history: Dict[str, Any] = {}
    previous_interactions: List[str] = []
    
    # Performance tracking
    used_in_call: bool = False
    call_outcome: Optional[str] = None
    effectiveness_rating: Optional[float] = None
    agent_feedback: Optional[str] = None
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    used_at: Optional[datetime] = None

class ScriptPerformance(BaseModel):
    template_id: str
    time_period: str  # "24h", "7d", "30d", "90d"
    
    # Usage metrics
    total_generations: int
    total_calls: int
    success_rate: float
    conversion_rate: float
    
    # Quality metrics
    average_rating: float
    agent_satisfaction: float
    customer_satisfaction: float
    
    # Performance data
    section_performance: Dict[str, float] = {}
    common_objections: List[Dict[str, Any]] = []
    successful_variations: List[str] = []
    
    # Optimization suggestions
    recommended_improvements: List[str] = []
    a_b_test_suggestions: List[str] = []

class ScriptLibrary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    organization_id: str
    
    # Content
    templates: List[str] = []  # Template IDs
    categories: List[str] = []
    total_scripts: int = 0
    
    # Access control
    is_public: bool = False
    access_level: str = "organization"  # "public", "organization", "team", "private"
    allowed_users: List[str] = []
    allowed_teams: List[str] = []
    
    # Usage
    downloads: int = 0
    rating: float = 0.0
    reviews: int = 0
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class ScriptAnalytics(BaseModel):
    script_template_id: str
    analytics_period: str
    
    # Core metrics
    total_uses: int
    successful_calls: int
    failed_calls: int
    average_call_duration: float
    conversion_rate: float
    
    # Quality metrics
    script_adherence_rate: float
    improvisation_rate: float
    objection_handling_success: float
    closing_effectiveness: float
    
    # Trend data
    daily_usage: List[Dict[str, Any]] = []
    performance_trend: List[Dict[str, Any]] = []
    success_by_section: Dict[str, float] = {}
    
    # Insights
    top_performing_sections: List[str] = []
    underperforming_sections: List[str] = []
    recommended_optimizations: List[str] = []

# Sample script templates
SAMPLE_SCRIPT_TEMPLATES = [
    ScriptTemplate(
        name="Professional Sales Introduction",
        description="A professional and engaging sales call opening script",
        script_type=ScriptType.SALES,
        industry="Technology",
        use_case="Cold calling for B2B software sales",
        sections=[
            ScriptSection(
                name="Opening Greeting",
                order_index=1,
                content="Hi {customer_name}, this is {agent_name} from {company_name}. I hope you're having a great {time_of_day}. I'm calling because we've been helping companies like {customer_company} {main_benefit}. Do you have about 3 minutes for me to share how we might be able to help you as well?",
                purpose="opening",
                estimated_duration_seconds=20,
                variables=[
                    ScriptVariable(name="customer_name", type="string", description="Customer's first name", required=True),
                    ScriptVariable(name="agent_name", type="string", description="Agent's name", required=True),
                    ScriptVariable(name="company_name", type="string", description="Our company name", required=True),
                    ScriptVariable(name="time_of_day", type="string", description="Morning/afternoon/evening", required=False, default_value="day"),
                    ScriptVariable(name="customer_company", type="string", description="Customer's company name", required=True),
                    ScriptVariable(name="main_benefit", type="string", description="Primary value proposition", required=True)
                ],
                branches=[
                    ConversationBranch(
                        condition="customer_response == 'yes' or 'interested'",
                        script_content="Great! Let me start by asking you a quick question about {specific_pain_point}...",
                        suggested_responses=["Yes, go ahead", "Sure, I have a few minutes", "What's this about?"]
                    ),
                    ConversationBranch(
                        condition="customer_response == 'no' or 'busy'",
                        script_content="I completely understand you're busy. Would there be a better time for me to call you back? I promise it will be worth your time.",
                        suggested_responses=["Not right now", "I'm in a meeting", "Call me later"]
                    )
                ],
                success_rate=78.5,
                conversion_impact=0.23
            ),
            ScriptSection(
                name="Value Proposition",
                order_index=2,
                content="What we do is help {industry} companies like yours {primary_value}. In fact, {customer_company_similar} recently saw {specific_result} after implementing our solution. Based on what I know about {customer_company}, I believe we could help you achieve similar results.",
                purpose="presentation",
                estimated_duration_seconds=30,
                variables=[
                    ScriptVariable(name="industry", type="string", description="Customer's industry", required=True),
                    ScriptVariable(name="primary_value", type="string", description="Main value we provide", required=True),
                    ScriptVariable(name="customer_company_similar", type="string", description="Similar customer company", required=False),
                    ScriptVariable(name="specific_result", type="string", description="Specific outcome achieved", required=True)
                ],
                success_rate=82.1,
                conversion_impact=0.31
            )
        ],
        flow_type=ConversationFlow.BRANCHING,
        personalization_level=PersonalizationLevel.ADVANCED,
        variables=[
            ScriptVariable(name="industry_focus", type="string", description="Primary industry focus", required=True),
            ScriptVariable(name="product_name", type="string", description="Product or service name", required=True),
            ScriptVariable(name="value_metric", type="string", description="Key success metric", required=True)
        ],
        status=ScriptStatus.APPROVED,
        effectiveness_score=8.7,
        usage_count=245,
        success_rate=76.3,
        created_by="sales_manager",
        approved_by="sales_director",
        tags=["sales", "cold_calling", "b2b", "opening"],
        category="Sales Scripts",
        compliance_notes=["Follow TCPA guidelines", "Respect do-not-call lists"],
        must_say=["This call may be recorded for quality purposes"],
        approved_at=datetime.now() - timedelta(days=15)
    ),
    ScriptTemplate(
        name="Customer Service Issue Resolution",
        description="Empathetic customer service script for handling complaints and issues",
        script_type=ScriptType.CUSTOMER_SERVICE,
        industry="General",
        use_case="Inbound customer service for issue resolution",
        sections=[
            ScriptSection(
                name="Empathetic Greeting",
                order_index=1,
                content="Thank you for calling {company_name}, {customer_name}. I'm {agent_name} and I'm here to help you today. I see that you're calling about {issue_category}. I understand how {emotion_acknowledgment} this must be, and I want to make sure we get this resolved for you right away.",
                purpose="opening",
                estimated_duration_seconds=25,
                variables=[
                    ScriptVariable(name="issue_category", type="string", description="Type of issue customer is experiencing", required=True),
                    ScriptVariable(name="emotion_acknowledgment", type="string", description="Acknowledge customer's emotional state", required=True)
                ],
                success_rate=91.2,
                conversion_impact=0.18
            ),
            ScriptSection(
                name="Information Gathering",
                order_index=2,
                content="To make sure I fully understand the situation and can provide you with the best solution, could you please tell me more about {specific_issue_detail}? Also, when did you first notice this issue?",
                purpose="information_gathering",
                estimated_duration_seconds=45,
                branches=[
                    ConversationBranch(
                        condition="issue_severity == 'high'",
                        script_content="I can see this is urgent. Let me escalate this to our priority support team right away while we work on an immediate solution.",
                        escalation_triggers=["urgent", "critical", "losing money", "can't work"]
                    )
                ],
                success_rate=88.7,
                conversion_impact=0.25
            )
        ],
        status=ScriptStatus.ACTIVE,
        effectiveness_score=9.1,
        usage_count=892,
        success_rate=89.4,
        created_by="support_manager",
        approved_by="customer_success_director",
        tags=["customer_service", "issue_resolution", "empathy"],
        category="Support Scripts",
        must_say=["I apologize for any inconvenience", "Let me make this right for you"],
        do_not_say=["That's not my department", "I can't help with that"],
        approved_at=datetime.now() - timedelta(days=30)
    ),
    ScriptTemplate(
        name="Lead Qualification Framework",
        description="Systematic lead qualification script using BANT methodology",
        script_type=ScriptType.LEAD_QUALIFICATION,
        industry="B2B Services",
        use_case="Qualifying inbound leads for sales team",
        sections=[
            ScriptSection(
                name="Qualification Questions",
                order_index=1,
                content="Thanks for your interest in {product_service}, {customer_name}. To make sure I connect you with the right specialist who can best help you, I'd like to ask you a few quick questions. First, what specifically prompted you to look into {product_category} solutions?",
                purpose="information_gathering",
                estimated_duration_seconds=60,
                variables=[
                    ScriptVariable(name="product_service", type="string", description="Specific product or service", required=True),
                    ScriptVariable(name="product_category", type="string", description="Product category", required=True)
                ],
                branches=[
                    ConversationBranch(
                        condition="budget_qualification_needed",
                        script_content="And in terms of budget, what range were you considering for this type of solution? This helps me recommend the most appropriate options for you.",
                        suggested_responses=["Budget questions", "Investment range", "Pricing inquiry"]
                    )
                ],
                success_rate=84.3,
                conversion_impact=0.42
            )
        ],
        status=ScriptStatus.APPROVED,
        effectiveness_score=8.9,
        usage_count=156,
        success_rate=82.7,
        created_by="lead_qualification_team",
        tags=["lead_qualification", "bant", "discovery"],
        category="Qualification Scripts",
        approved_at=datetime.now() - timedelta(days=8)
    )
]

# Global storage
script_templates: List[ScriptTemplate] = []
generated_scripts: List[GeneratedScript] = []
script_libraries: List[ScriptLibrary] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global script_templates
    
    script_templates.extend(SAMPLE_SCRIPT_TEMPLATES)
    
    # Create sample script library
    sample_library = ScriptLibrary(
        name="Vocelio Standard Scripts",
        description="Official Vocelio script library with proven high-performing templates",
        organization_id="vocelio_official",
        templates=[t.id for t in script_templates],
        categories=["Sales Scripts", "Support Scripts", "Qualification Scripts"],
        total_scripts=len(script_templates),
        is_public=True,
        downloads=1247,
        rating=4.8,
        reviews=89,
        created_by="vocelio_team"
    )
    
    script_libraries.append(sample_library)
    
    logger.info("Sample scripts data initialized successfully")

async def personalize_script_content(template: ScriptTemplate, customer_data: Dict[str, Any], agent_data: Dict[str, Any]) -> str:
    """Personalize script content with customer and agent data"""
    
    personalized_sections = []
    
    for section in template.sections:
        content = section.content
        
        # Replace variables with actual data
        for variable in section.variables:
            placeholder = f"{{{variable.name}}}"
            value = customer_data.get(variable.name) or agent_data.get(variable.name) or variable.default_value or f"[{variable.name}]"
            content = content.replace(placeholder, str(value))
        
        # Replace global template variables
        for variable in template.variables:
            placeholder = f"{{{variable.name}}}"
            value = customer_data.get(variable.name) or agent_data.get(variable.name) or variable.default_value or f"[{variable.name}]"
            content = content.replace(placeholder, str(value))
        
        personalized_sections.append(f"## {section.name}\n{content}")
    
    return "\n\n".join(personalized_sections)

async def analyze_script_performance(template_id: str, time_period: str = "30d") -> ScriptPerformance:
    """Analyze script performance metrics"""
    
    template = next((t for t in script_templates if t.id == template_id), None)
    if not template:
        return None
    
    # Get generated scripts for this template
    template_scripts = [s for s in generated_scripts if s.template_id == template_id]
    
    # Calculate metrics
    total_generations = len(template_scripts)
    total_calls = len([s for s in template_scripts if s.used_in_call])
    successful_calls = len([s for s in template_scripts if s.call_outcome == "success"])
    
    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
    conversion_rate = success_rate  # Simplified for demo
    
    # Mock additional metrics
    average_rating = 4.2 + (hash(template_id) % 8) / 10
    agent_satisfaction = 4.0 + (hash(template_id) % 10) / 10
    customer_satisfaction = 3.8 + (hash(template_id) % 12) / 10
    
    return ScriptPerformance(
        template_id=template_id,
        time_period=time_period,
        total_generations=total_generations,
        total_calls=total_calls,
        success_rate=success_rate,
        conversion_rate=conversion_rate,
        average_rating=average_rating,
        agent_satisfaction=agent_satisfaction,
        customer_satisfaction=customer_satisfaction,
        section_performance={section.name: section.success_rate for section in template.sections},
        common_objections=[
            {"objection": "Too expensive", "frequency": 23, "success_rate": 67},
            {"objection": "Not the right time", "frequency": 18, "success_rate": 45},
            {"objection": "Need to think about it", "frequency": 15, "success_rate": 52}
        ],
        successful_variations=[
            "Added customer success story",
            "Emphasized ROI calculation",
            "Used urgency language"
        ],
        recommended_improvements=[
            "Strengthen value proposition in section 2",
            "Add more objection handling options",
            "Include customer testimonials"
        ],
        a_b_test_suggestions=[
            "Test different opening hooks",
            "Vary the timing of price mention",
            "Test emotional vs. logical appeals"
        ]
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Scripts Service",
    description="Dynamic conversation script generation, template management, and personalized call flows for Vocelio AI Call Center",
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
        "service": "scripts",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Script Template Endpoints
@app.get("/templates", response_model=List[ScriptTemplate])
async def get_script_templates(
    script_type: Optional[ScriptType] = None,
    industry: Optional[str] = None,
    status: Optional[ScriptStatus] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "effectiveness_score",  # "effectiveness_score", "usage_count", "success_rate", "created_at"
    limit: int = 50,
    offset: int = 0
):
    """Get script templates with filtering and sorting options"""
    
    filtered_templates = script_templates.copy()
    
    # Apply filters
    if script_type:
        filtered_templates = [t for t in filtered_templates if t.script_type == script_type]
    
    if industry:
        filtered_templates = [t for t in filtered_templates if industry.lower() in t.industry.lower()]
    
    if status:
        filtered_templates = [t for t in filtered_templates if t.status == status]
    
    if category:
        filtered_templates = [t for t in filtered_templates if category.lower() in t.category.lower()]
    
    if search:
        search_lower = search.lower()
        filtered_templates = [
            t for t in filtered_templates
            if (search_lower in t.name.lower() or 
                search_lower in t.description.lower() or
                any(search_lower in tag.lower() for tag in t.tags))
        ]
    
    # Apply sorting
    if sort_by == "effectiveness_score":
        filtered_templates.sort(key=lambda x: x.effectiveness_score, reverse=True)
    elif sort_by == "usage_count":
        filtered_templates.sort(key=lambda x: x.usage_count, reverse=True)
    elif sort_by == "success_rate":
        filtered_templates.sort(key=lambda x: x.success_rate, reverse=True)
    elif sort_by == "created_at":
        filtered_templates.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    return filtered_templates[offset:offset + limit]

@app.get("/templates/{template_id}", response_model=ScriptTemplate)
async def get_script_template(template_id: str):
    """Get a specific script template by ID"""
    template = next((t for t in script_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Script template not found")
    return template

@app.post("/templates", response_model=ScriptTemplate)
async def create_script_template(template_data: ScriptTemplate):
    """Create a new script template"""
    script_templates.append(template_data)
    logger.info(f"Created new script template: {template_data.name}")
    return template_data

@app.put("/templates/{template_id}", response_model=ScriptTemplate)
async def update_script_template(template_id: str, template_data: ScriptTemplate):
    """Update an existing script template"""
    template = next((t for t in script_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Script template not found")
    
    # Update fields
    for field, value in template_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(template, field, value)
    
    template.updated_at = datetime.now()
    logger.info(f"Updated script template: {template.name}")
    return template

@app.put("/templates/{template_id}/status")
async def update_template_status(template_id: str, status: ScriptStatus, approved_by: Optional[str] = None):
    """Update script template status"""
    template = next((t for t in script_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Script template not found")
    
    template.status = status
    template.updated_at = datetime.now()
    
    if status == ScriptStatus.APPROVED and approved_by:
        template.approved_by = approved_by
        template.approved_at = datetime.now()
    
    logger.info(f"Updated template {template.name} status to {status}")
    return {"message": f"Template status updated to {status}"}

# Script Generation Endpoints
@app.post("/generate", response_model=GeneratedScript)
async def generate_personalized_script(
    template_id: str,
    customer_id: str,
    agent_id: str,
    customer_data: Dict[str, Any],
    agent_data: Dict[str, Any],
    campaign_id: Optional[str] = None,
    call_context: Optional[Dict[str, Any]] = None
):
    """Generate a personalized script from a template"""
    
    template = next((t for t in script_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Script template not found")
    
    if template.status != ScriptStatus.ACTIVE and template.status != ScriptStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Template is not active")
    
    # Generate personalized content
    personalized_content = await personalize_script_content(template, customer_data, agent_data)
    
    # Create generated script record
    generated_script = GeneratedScript(
        template_id=template_id,
        customer_id=customer_id,
        agent_id=agent_id,
        campaign_id=campaign_id,
        personalized_content=personalized_content,
        variables_used={**customer_data, **agent_data},
        personalization_data=customer_data,
        call_context=call_context or {}
    )
    
    generated_scripts.append(generated_script)
    
    # Update template usage
    template.usage_count += 1
    template.last_used = datetime.now()
    
    logger.info(f"Generated personalized script for customer {customer_id}")
    return generated_script

@app.get("/generated", response_model=List[GeneratedScript])
async def get_generated_scripts(
    template_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    used_only: Optional[bool] = None,
    limit: int = 50
):
    """Get generated scripts with filtering options"""
    
    filtered_scripts = generated_scripts.copy()
    
    if template_id:
        filtered_scripts = [s for s in filtered_scripts if s.template_id == template_id]
    
    if customer_id:
        filtered_scripts = [s for s in filtered_scripts if s.customer_id == customer_id]
    
    if agent_id:
        filtered_scripts = [s for s in filtered_scripts if s.agent_id == agent_id]
    
    if campaign_id:
        filtered_scripts = [s for s in filtered_scripts if s.campaign_id == campaign_id]
    
    if used_only is not None:
        filtered_scripts = [s for s in filtered_scripts if s.used_in_call == used_only]
    
    # Sort by generation time, most recent first
    filtered_scripts.sort(key=lambda x: x.generated_at, reverse=True)
    
    return filtered_scripts[:limit]

@app.get("/generated/{script_id}", response_model=GeneratedScript)
async def get_generated_script(script_id: str):
    """Get a specific generated script"""
    script = next((s for s in generated_scripts if s.id == script_id), None)
    if not script:
        raise HTTPException(status_code=404, detail="Generated script not found")
    return script

@app.put("/generated/{script_id}/feedback")
async def update_script_feedback(
    script_id: str,
    used_in_call: bool,
    call_outcome: Optional[str] = None,
    effectiveness_rating: Optional[float] = None,
    agent_feedback: Optional[str] = None
):
    """Update feedback for a generated script"""
    script = next((s for s in generated_scripts if s.id == script_id), None)
    if not script:
        raise HTTPException(status_code=404, detail="Generated script not found")
    
    script.used_in_call = used_in_call
    if call_outcome:
        script.call_outcome = call_outcome
    if effectiveness_rating:
        script.effectiveness_rating = effectiveness_rating
    if agent_feedback:
        script.agent_feedback = agent_feedback
    
    if used_in_call:
        script.used_at = datetime.now()
    
    logger.info(f"Updated feedback for script {script_id}")
    return {"message": "Script feedback updated successfully"}

# Script Libraries Endpoints
@app.get("/libraries", response_model=List[ScriptLibrary])
async def get_script_libraries(
    organization_id: Optional[str] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None
):
    """Get script libraries"""
    
    filtered_libraries = script_libraries.copy()
    
    if organization_id:
        filtered_libraries = [l for l in filtered_libraries if l.organization_id == organization_id]
    
    if is_public is not None:
        filtered_libraries = [l for l in filtered_libraries if l.is_public == is_public]
    
    if search:
        search_lower = search.lower()
        filtered_libraries = [
            l for l in filtered_libraries
            if search_lower in l.name.lower() or search_lower in l.description.lower()
        ]
    
    # Sort by rating, then by downloads
    filtered_libraries.sort(key=lambda x: (x.rating, x.downloads), reverse=True)
    
    return filtered_libraries

@app.get("/libraries/{library_id}", response_model=ScriptLibrary)
async def get_script_library(library_id: str):
    """Get a specific script library"""
    library = next((l for l in script_libraries if l.id == library_id), None)
    if not library:
        raise HTTPException(status_code=404, detail="Script library not found")
    return library

@app.post("/libraries", response_model=ScriptLibrary)
async def create_script_library(library_data: ScriptLibrary):
    """Create a new script library"""
    script_libraries.append(library_data)
    logger.info(f"Created new script library: {library_data.name}")
    return library_data

# Performance Analytics Endpoints
@app.get("/templates/{template_id}/performance", response_model=ScriptPerformance)
async def get_template_performance(template_id: str, time_period: str = "30d"):
    """Get performance analytics for a script template"""
    performance = await analyze_script_performance(template_id, time_period)
    if not performance:
        raise HTTPException(status_code=404, detail="Script template not found")
    return performance

@app.get("/analytics/overview")
async def get_scripts_overview():
    """Get scripts service overview analytics"""
    
    total_templates = len(script_templates)
    active_templates = len([t for t in script_templates if t.status == ScriptStatus.ACTIVE])
    total_generated = len(generated_scripts)
    scripts_used = len([s for s in generated_scripts if s.used_in_call])
    
    # Calculate success rates
    successful_calls = len([s for s in generated_scripts if s.call_outcome == "success"])
    usage_rate = (scripts_used / total_generated * 100) if total_generated > 0 else 0
    success_rate = (successful_calls / scripts_used * 100) if scripts_used > 0 else 0
    
    # Script type distribution
    type_distribution = {}
    for script_type in ScriptType:
        count = len([t for t in script_templates if t.script_type == script_type])
        if count > 0:
            type_distribution[script_type.value] = count
    
    # Top performing templates
    top_templates = sorted(script_templates, key=lambda x: x.effectiveness_score, reverse=True)[:5]
    
    # Recent activity
    recent_generations = len([s for s in generated_scripts if s.generated_at > datetime.now() - timedelta(hours=24)])
    recent_templates = len([t for t in script_templates if t.created_at > datetime.now() - timedelta(days=7)])
    
    return {
        "summary": {
            "total_templates": total_templates,
            "active_templates": active_templates,
            "total_generated_scripts": total_generated,
            "scripts_used_in_calls": scripts_used,
            "script_libraries": len(script_libraries)
        },
        "performance_metrics": {
            "usage_rate": round(usage_rate, 1),
            "success_rate": round(success_rate, 1),
            "average_effectiveness": round(sum(t.effectiveness_score for t in script_templates) / total_templates, 1) if total_templates > 0 else 0,
            "average_template_usage": round(sum(t.usage_count for t in script_templates) / total_templates, 1) if total_templates > 0 else 0
        },
        "script_type_distribution": type_distribution,
        "top_performing_templates": [
            {
                "id": t.id,
                "name": t.name,
                "type": t.script_type.value,
                "effectiveness_score": t.effectiveness_score,
                "usage_count": t.usage_count,
                "success_rate": t.success_rate
            }
            for t in top_templates
        ],
        "recent_activity": {
            "scripts_generated_24h": recent_generations,
            "new_templates_7d": recent_templates,
            "templates_updated_24h": len([t for t in script_templates if t.updated_at > datetime.now() - timedelta(hours=24)])
        },
        "quality_metrics": {
            "templates_approved": len([t for t in script_templates if t.status == ScriptStatus.APPROVED]),
            "templates_in_review": len([t for t in script_templates if t.status == ScriptStatus.REVIEW]),
            "average_script_rating": 4.3,  # Mock average rating
            "compliance_adherence": 98.7  # Mock compliance score
        }
    }

@app.get("/analytics/trends")
async def get_script_trends(days: int = 30):
    """Get script usage and performance trends"""
    
    # Generate trend data
    trend_data = []
    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Mock trend calculations
        scripts_generated = max(0, 20 - i + (i % 3) * 5)
        scripts_used = max(0, scripts_generated - (i % 4))
        
        trend_data.append({
            "date": date_str,
            "scripts_generated": scripts_generated,
            "scripts_used": scripts_used,
            "success_rate": min(100, 70 + (i % 20)),
            "average_effectiveness": min(10, 7.5 + (i % 15) / 10)
        })
    
    return {
        "period_days": days,
        "trend_data": trend_data,
        "summary": {
            "total_generated": sum(d["scripts_generated"] for d in trend_data),
            "total_used": sum(d["scripts_used"] for d in trend_data),
            "average_success_rate": sum(d["success_rate"] for d in trend_data) / len(trend_data),
            "trend_direction": "increasing"  # Mock trend analysis
        }
    }

# Script Categories Endpoint
@app.get("/categories")
async def get_script_categories():
    """Get available script categories and types"""
    
    # Count templates by type
    type_counts = {}
    for script_type in ScriptType:
        count = len([t for t in script_templates if t.script_type == script_type])
        type_counts[script_type.value] = count
    
    # Get unique categories
    categories = list(set(t.category for t in script_templates))
    category_counts = {}
    for category in categories:
        category_counts[category] = len([t for t in script_templates if t.category == category])
    
    return {
        "script_types": [
            {
                "type": script_type.value,
                "display_name": script_type.value.replace("_", " ").title(),
                "count": type_counts.get(script_type.value, 0),
                "description": f"Scripts for {script_type.value.replace('_', ' ')} scenarios"
            }
            for script_type in ScriptType
        ],
        "categories": [
            {
                "name": category,
                "count": count,
                "templates": [t.name for t in script_templates if t.category == category]
            }
            for category, count in category_counts.items()
        ],
        "industries": list(set(t.industry for t in script_templates)),
        "flow_types": [flow_type.value for flow_type in ConversationFlow],
        "personalization_levels": [level.value for level in PersonalizationLevel]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
