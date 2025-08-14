"""
Enhanced Models for Unified AI Agent Platform
Pydantic models for marketplace, purchases, and enhanced agent management
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for type safety
class PurchaseStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"

class LicenseType(str, Enum):
    PER_USER = "per_user"
    PER_ORGANIZATION = "per_organization"
    PER_FACILITY = "per_facility"
    ENTERPRISE = "enterprise"

class AgentStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    TRAINING = "training"
    TESTING = "testing"
    DEPLOYED = "deployed"
    MAINTENANCE = "maintenance"
    ARCHIVED = "archived"

class CapabilityType(str, Enum):
    CONVERSATION = "conversation"
    TASK_AUTOMATION = "task_automation"
    DATA_ANALYSIS = "data_analysis"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    MONITORING = "monitoring"

class DeploymentEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# Marketplace Models
class MarketplaceAgent(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price: float = Field(ge=0)
    rating: float = Field(ge=0, le=5)
    downloads: int = Field(ge=0)
    creator_id: str
    creator_name: str
    capabilities: List[str]
    languages: List[str]
    is_featured: bool = False
    is_verified: bool = False
    trial_period_days: int = Field(ge=0, le=365)
    license_type: LicenseType
    version: str
    created_at: datetime
    updated_at: datetime

    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price must be non-negative')
        return round(v, 2)
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 0 <= v <= 5:
            raise ValueError('Rating must be between 0 and 5')
        return round(v, 1)

class MarketplaceFilter(BaseModel):
    category: Optional[str] = None
    featured: Optional[bool] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    search: Optional[str] = None
    sort_by: str = "rating"
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

class AgentReview(BaseModel):
    id: str
    agent_id: str
    user_id: str
    rating: int = Field(ge=1, le=5)
    title: str
    comment: str
    created_at: datetime
    helpful_count: int = Field(ge=0)

class CreateReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: str = Field(max_length=200)
    comment: str = Field(max_length=2000)

# Purchase Models
class PurchaseItem(BaseModel):
    type: str  # "agent" or "subscription"
    agent_id: Optional[str] = None
    plan_id: Optional[str] = None
    price: float = Field(ge=0)
    quantity: int = Field(1, ge=1)
    license_type: Optional[LicenseType] = None

class BillingInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    currency: str = "USD"
    tax_rate: float = Field(0.08, ge=0, le=1)

class PaymentDetailsModel(BaseModel):
    payment_method: PaymentMethod
    card_number: Optional[str] = None
    expiry_month: Optional[int] = Field(None, ge=1, le=12)
    expiry_year: Optional[int] = None
    cvv: Optional[str] = None
    cardholder_name: Optional[str] = None
    paypal_email: Optional[str] = None
    bank_account: Optional[str] = None
    routing_number: Optional[str] = None

    @validator('card_number')
    def validate_card_number(cls, v, values):
        if values.get('payment_method') == PaymentMethod.CREDIT_CARD:
            if not v or len(v.replace(' ', '').replace('-', '')) < 13:
                raise ValueError('Valid card number required for credit card payments')
        return v
    
    @validator('cvv')
    def validate_cvv(cls, v, values):
        if values.get('payment_method') == PaymentMethod.CREDIT_CARD:
            if not v or not (3 <= len(v) <= 4):
                raise ValueError('Valid CVV required for credit card payments')
        return v

class PurchaseRequest(BaseModel):
    items: List[PurchaseItem]
    payment_method: PaymentMethod
    billing_info: BillingInfo
    metadata: Optional[Dict[str, Any]] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    total_amount: float
    currency: str
    expires_at: str
    payment_url: str
    status: str

class License(BaseModel):
    id: str
    type: str  # "agent" or "subscription"
    license_key: str
    user_id: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    agent_id: Optional[str] = None
    plan_id: Optional[str] = None
    usage_limits: Dict[str, Any]
    current_usage: Optional[Dict[str, Any]] = None

# Enhanced Agent Management Models
class AgentCapability(BaseModel):
    id: str
    name: str
    type: CapabilityType
    description: str
    required_models: List[str]
    configuration: Dict[str, Any]

class AgentTemplate(BaseModel):
    id: str
    name: str
    description: str
    capabilities: List[str]
    industry: str
    configuration: Dict[str, Any]

class EnhancedAgent(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    status: AgentStatus
    industry: str
    template_id: Optional[str] = None
    capabilities: List[str]
    version: str
    created_at: datetime
    updated_at: datetime
    last_deployed: Optional[datetime] = None
    deployment_environment: Optional[DeploymentEnvironment] = None
    performance_score: float = Field(ge=0, le=100)
    usage_stats: Dict[str, Any]
    configuration: Dict[str, Any]
    metadata: Dict[str, Any]

class CreateEnhancedAgentRequest(BaseModel):
    name: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    industry: str = "general"
    capabilities: Optional[List[str]] = None
    template_id: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('industry')
    def validate_industry(cls, v):
        valid_industries = ['sales', 'support', 'healthcare', 'financial', 'education', 'general']
        if v not in valid_industries:
            raise ValueError(f'Industry must be one of: {valid_industries}')
        return v

class ConfigureCapabilitiesRequest(BaseModel):
    capability_configs: Dict[str, Dict[str, Any]]

class DeployAgentRequest(BaseModel):
    environment: DeploymentEnvironment
    deployment_config: Optional[Dict[str, Any]] = None

class UpdateConfigurationRequest(BaseModel):
    configuration_updates: Dict[str, Any]

class AgentAnalyticsRequest(BaseModel):
    time_range: str = "7d"
    metrics: Optional[List[str]] = None

class CloneAgentRequest(BaseModel):
    new_name: str = Field(max_length=200)

# Marketplace Publication Models
class PublishToMarketplaceRequest(BaseModel):
    name: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    category: str
    price: float = Field(ge=0)
    creator_name: str = Field(max_length=100)
    capabilities: List[str]
    languages: List[str] = ["en"]
    trial_period_days: int = Field(7, ge=0, le=365)
    license_type: LicenseType = LicenseType.PER_USER
    version: str = "1.0.0"
    is_verified: bool = False

# Response Models
class AgentCreationResponse(BaseModel):
    agent_id: str
    status: str
    capabilities_configured: int
    deployment_ready: bool
    management_url: str

class DeploymentResponse(BaseModel):
    deployment_id: str
    agent_id: str
    environment: str
    status: str
    endpoint_url: str
    health_check_url: str
    deployed_at: str

class AnalyticsResponse(BaseModel):
    agent_id: str
    time_range: str
    generated_at: str
    metrics: Dict[str, Any]
    capability_metrics: Dict[str, Any]

class HealthCheckResponse(BaseModel):
    agent_id: str
    status: str
    overall_health: str
    last_check: str
    checks: Dict[str, Any]

class CapabilityCatalogResponse(BaseModel):
    total_capabilities: int
    categories: List[str]
    capabilities: List[Dict[str, Any]]

# Unified Service Response Models
class MarketplaceListResponse(BaseModel):
    agents: List[MarketplaceAgent]
    total: int
    limit: int
    offset: int

class PurchaseHistoryResponse(BaseModel):
    purchases: List[Dict[str, Any]]
    total: int

class LicenseValidationResponse(BaseModel):
    valid: bool
    license: Optional[License] = None
    remaining_usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class RefundResponse(BaseModel):
    refund_id: str
    status: str
    processing_time: str
    contact_support: str

# Error Models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
