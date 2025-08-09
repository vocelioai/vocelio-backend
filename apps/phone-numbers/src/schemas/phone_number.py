# apps/phone-numbers/src/schemas/phone_number.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NumberType(str, Enum):
    LOCAL = "local"
    TOLL_FREE = "toll_free" 
    MOBILE = "mobile"


class NumberStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RELEASED = "released"
    PENDING = "pending"


class Capability(str, Enum):
    VOICE = "voice"
    SMS = "sms"
    MMS = "mms"
    FAX = "fax"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class ProvisioningStatus(str, Enum):
    PENDING = "pending"
    PROVISIONED = "provisioned"
    FAILED = "failed"


# Base schemas
class PhoneNumberBase(BaseModel):
    """Base phone number schema"""
    friendly_name: str = Field(..., min_length=1, max_length=100)
    number_type: NumberType
    capabilities: List[Capability] = Field(default=["voice"])
    voice_url: Optional[str] = None
    sms_url: Optional[str] = None
    tags: Optional[List[str]] = Field(default=[])
    notes: Optional[str] = None


class PhoneNumberCreate(PhoneNumberBase):
    """Schema for creating a phone number"""
    phone_number: str = Field(..., regex=r'^\+?[1-9]\d{1,14}$')
    country_code: str = Field(..., min_length=2, max_length=2)
    region: Optional[str] = None
    locality: Optional[str] = None
    postal_code: Optional[str] = None
    monthly_price: float = Field(..., gt=0)
    
    @validator('capabilities')
    def validate_capabilities(cls, v, values):
        """Validate capabilities based on number type"""
        if 'number_type' in values:
            number_type = values['number_type']
            if number_type == NumberType.TOLL_FREE and 'sms' in v:
                raise ValueError("Toll-free numbers don't support SMS")
            if number_type != NumberType.MOBILE and 'mms' in v:
                raise ValueError("MMS only supported on mobile numbers")
        return v


class PhoneNumberUpdate(BaseModel):
    """Schema for updating a phone number"""
    friendly_name: Optional[str] = Field(None, min_length=1, max_length=100)
    voice_url: Optional[str] = None
    sms_url: Optional[str] = None
    status: Optional[NumberStatus] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    emergency_enabled: Optional[bool] = None


class PhoneNumberResponse(PhoneNumberBase):
    """Schema for phone number response"""
    id: str
    twilio_sid: str
    phone_number: str
    formatted_number: str
    organization_id: str
    user_id: str
    
    country_code: str
    region: Optional[str]
    locality: Optional[str]
    postal_code: Optional[str]
    
    status: NumberStatus
    monthly_price: float
    currency: str
    
    # Usage summary
    total_calls: int
    total_minutes: float
    total_sms: int
    total_mms: int
    campaign_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PhoneNumberListResponse(BaseModel):
    """Schema for phone number list response"""
    numbers: List[PhoneNumberResponse]
    total: int
    page: int
    size: int
    pages: int


# Search schemas
class NumberSearchRequest(BaseModel):
    """Schema for number search request"""
    country_code: str = Field(..., min_length=2, max_length=2)
    number_type: NumberType = NumberType.LOCAL
    capabilities: List[Capability] = Field(default=["voice"])
    
    # Search filters
    area_code: Optional[str] = Field(None, regex=r'^\d{3}$')
    locality: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    contains: Optional[str] = Field(None, min_length=3, max_length=10)
    near_lat_long: Optional[str] = None  # "lat,long"
    
    # Search limits
    limit: int = Field(default=20, le=50)


class AvailableNumber(BaseModel):
    """Schema for available number from Twilio"""
    phone_number: str
    friendly_name: str
    locality: Optional[str]
    region: Optional[str]
    country: str
    capabilities: List[str]
    monthly_price: float
    latitude: Optional[float]
    longitude: Optional[float]
    postal_code: Optional[str]


class NumberSearchResponse(BaseModel):
    """Schema for number search response"""
    available_numbers: List[AvailableNumber]
    total_found: int
    search_params: NumberSearchRequest
    pricing_info: Dict[str, Any]


# Purchase schemas
class NumberPurchaseRequest(BaseModel):
    """Schema for number purchase request"""
    phone_number: str = Field(..., regex=r'^\+?[1-9]\d{1,14}$')
    friendly_name: str = Field(..., min_length=1, max_length=100)
    number_type: NumberType
    capabilities: List[Capability]
    
    # Configuration
    voice_url: Optional[str] = None
    sms_url: Optional[str] = None
    tags: Optional[List[str]] = Field(default=[])
    notes: Optional[str] = None
    
    # Payment
    payment_method_id: str  # Stripe payment method ID
    billing_address: Optional[Dict[str, str]] = None


class NumberPurchaseResponse(BaseModel):
    """Schema for number purchase response"""
    purchase_id: str
    phone_number_id: str
    phone_number: str
    status: str
    payment_status: PaymentStatus
    provisioning_status: ProvisioningStatus
    total_amount: float
    currency: str
    estimated_completion: datetime


# Usage schemas
class UsageStatsRequest(BaseModel):
    """Schema for usage statistics request"""
    phone_number_ids: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    group_by: Optional[str] = Field(None, regex=r'^(day|week|month)$')


class UsageStats(BaseModel):
    """Schema for usage statistics"""
    phone_number_id: str
    phone_number: str
    period_start: datetime
    period_end: datetime
    
    # Call statistics
    total_calls: int
    inbound_calls: int
    outbound_calls: int
    total_minutes: float
    average_call_duration: float
    
    # Messaging statistics
    total_sms: int
    inbound_sms: int
    outbound_sms: int
    total_mms: int
    
    # Cost statistics
    total_costs: float
    call_costs: float
    sms_costs: float
    mms_costs: float


class UsageStatsResponse(BaseModel):
    """Schema for usage statistics response"""
    usage_stats: List[UsageStats]
    summary: Dict[str, Any]
    period_start: datetime
    period_end: datetime


# Verification schemas
class VerificationRequest(BaseModel):
    """Schema for number verification request"""
    phone_number_id: str
    verification_type: str = Field(..., regex=r'^(ownership|compliance|carrier)
    )
    verification_method: str = Field(default="sms", regex=r'^(sms|voice|email)
    )


class VerificationResponse(BaseModel):
    """Schema for verification response"""
    verification_id: str
    status: str
    verification_code: Optional[str]
    expires_at: Optional[datetime]
    next_step: str


# Porting schemas
class PortingRequest(BaseModel):
    """Schema for number porting request"""
    external_phone_number: str = Field(..., regex=r'^\+?[1-9]\d{1,14}
    )
    current_carrier: str = Field(..., min_length=1, max_length=100)
    account_number: str = Field(..., min_length=1, max_length=50)
    pin_code: Optional[str] = Field(None, min_length=4, max_length=20)
    
    # Desired configuration
    friendly_name: str = Field(..., min_length=1, max_length=100)
    voice_url: Optional[str] = None
    sms_url: Optional[str] = None
    tags: Optional[List[str]] = Field(default=[])


class PortingResponse(BaseModel):
    """Schema for porting response"""
    porting_id: str
    status: str
    phone_number: str
    estimated_completion: Optional[datetime]
    required_documents: List[str]
    next_steps: List[str]


# Webhook schemas
class TwilioWebhookBase(BaseModel):
    """Base schema for Twilio webhooks"""
    AccountSid: str
    From: Optional[str]
    To: Optional[str]


class VoiceWebhook(TwilioWebhookBase):
    """Schema for Twilio voice webhooks"""
    CallSid: str
    CallStatus: str
    Direction: str
    ForwardedFrom: Optional[str]
    CallerName: Optional[str]
    Duration: Optional[str]
    RecordingUrl: Optional[str]


class SmsWebhook(TwilioWebhookBase):
    """Schema for Twilio SMS webhooks"""
    MessageSid: str
    MessageStatus: str
    Body: Optional[str]
    NumMedia: Optional[str]
    MediaUrl0: Optional[str]


# Country and pricing schemas
class CountryInfo(BaseModel):
    """Schema for country information"""
    code: str
    name: str
    flag: str
    pricing: Dict[str, float]
    features: List[str]
    area_codes_supported: bool


class PricingInfo(BaseModel):
    """Schema for pricing information"""
    country_code: str
    number_type: NumberType
    monthly_price: float
    setup_fee: float
    per_minute_cost: float
    per_sms_cost: float
    per_mms_cost: float
    currency: str


# Error schemas
class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses"""
    error: str = "validation_error"
    message: str
    field_errors: Dict[str, List[str]]


# Bulk operations schemas
class BulkNumberUpdate(BaseModel):
    """Schema for bulk number updates"""
    phone_number_ids: List[str] = Field(..., min_items=1, max_items=100)
    updates: PhoneNumberUpdate


class BulkNumberResponse(BaseModel):
    """Schema for bulk operation response"""
    success_count: int
    failed_count: int
    successful_ids: List[str]
    failed_ids: List[str]
    errors: Dict[str, str]


# Analytics schemas
class NumberAnalytics(BaseModel):
    """Schema for number analytics"""
    phone_number_id: str
    phone_number: str
    
    # Performance metrics
    success_rate: float
    answer_rate: float
    average_call_duration: float
    conversion_rate: float
    
    # Usage trends
    daily_usage: List[Dict[str, Any]]
    weekly_usage: List[Dict[str, Any]]
    monthly_usage: List[Dict[str, Any]]
    
    # Cost efficiency
    cost_per_call: float
    cost_per_conversion: float
    roi: float


class AnalyticsResponse(BaseModel):
    """Schema for analytics response"""
    analytics: List[NumberAnalytics]
    summary: Dict[str, Any]
    period: str
    generated_at: datetime
    