# apps/voice-marketplace/src/schemas/__init__.py
from .marketplace import *
from .purchase import *
from .review import *

__all__ = [
    # Marketplace schemas
    "VoiceListingResponse",
    "VoiceFilterRequest", 
    "VoiceComparisonRequest",
    "MarketplaceStatsResponse",
    
    # Purchase schemas
    "PurchaseCreateRequest",
    "PurchaseResponse",
    "PurchaseItemResponse",
    "CartItem",
    "CartResponse",
    
    # Review schemas
    "ReviewCreateRequest",
    "ReviewResponse",
    "ReviewUpdateRequest"
]


# apps/voice-marketplace/src/schemas/marketplace.py
"""
Marketplace Pydantic Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VoiceTierEnum(str, Enum):
    """Voice tier enumeration for API"""
    STANDARD = "standard"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ELITE = "elite"


class VoiceGenderEnum(str, Enum):
    """Voice gender enumeration for API"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"
    ALL = "all"


class VoiceLanguageEnum(str, Enum):
    """Voice language enumeration for API"""
    ALL = "all"
    EN = "EN"  # English
    ES = "ES"  # Spanish
    FR = "FR"  # French
    DE = "DE"  # German
    IT = "IT"  # Italian
    JA = "JA"  # Japanese
    MULTI = "MULTI"  # Multilingual


class PerformanceMetrics(BaseModel):
    """Voice performance metrics"""
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    avg_duration: float = Field(..., ge=0, description="Average call duration in minutes")
    satisfaction: float = Field(..., ge=0, le=5, description="Customer satisfaction score")


class VoiceListingResponse(BaseModel):
    """Voice listing response schema"""
    id: str
    voice_id: str
    name: str
    tier: VoiceTierEnum
    language: str
    gender: VoiceGenderEnum
    accent: str
    style: str
    price: float = Field(..., description="Price per minute in USD")
    quality: int = Field(..., ge=0, le=100, description="Quality score")
    description: str
    performance: PerformanceMetrics
    rating: float = Field(..., ge=0, le=5, description="Average rating")
    reviews: int = Field(..., ge=0, description="Total number of reviews")
    samples: int = Field(..., ge=0, description="Number of audio samples")
    tags: List[str] = Field(default_factory=list)
    avatar: Optional[str] = None
    provider: str
    status: str
    is_featured: bool = False
    is_new: bool = False
    is_popular: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VoiceFilterRequest(BaseModel):
    """Voice filtering request schema"""
    tier: Optional[VoiceTierEnum] = None
    language: Optional[VoiceLanguageEnum] = VoiceLanguageEnum.ALL
    gender: Optional[VoiceGenderEnum] = VoiceGenderEnum.ALL
    style: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_price: Optional[float] = Field(None, ge=0)
    search_query: Optional[str] = Field(None, max_length=200)
    is_featured: Optional[bool] = None
    is_new: Optional[bool] = None
    is_popular: Optional[bool] = None
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    # Sorting
    sort_by: Optional[str] = Field("name", description="Sort field")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$")


class VoiceComparisonRequest(BaseModel):
    """Voice comparison request schema"""
    voice_ids: List[str] = Field(..., min_items=2, max_items=4, description="Voice IDs to compare")


class VoiceComparisonResponse(BaseModel):
    """Voice comparison response schema"""
    voices: List[VoiceListingResponse]
    comparison_matrix: Dict[str, Any]
    recommendations: List[str]


class MarketplaceStatsResponse(BaseModel):
    """Marketplace statistics response"""
    total_voices: int
    voices_by_tier: Dict[str, int]
    total_purchases: int
    revenue_today: float
    revenue_this_month: float
    popular_tier: str
    avg_rating: float
    active_users: int
    top_voices: List[VoiceListingResponse]
    trending_voices: List[VoiceListingResponse]


class VoiceTierInfo(BaseModel):
    """Voice tier information"""
    name: str
    price: float = Field(..., description="Price per minute")
    voice_count: int = Field(..., description="Number of voices available")
    languages: str = Field(..., description="Supported languages")
    features: List[str] = Field(..., description="Tier features")
    use_case: str = Field(..., description="Recommended use case")
    provider: str = Field(..., description="Technology provider")
    color: str = Field(..., description="UI color scheme")
    popular: bool = False


class VoiceTiersResponse(BaseModel):
    """Voice tiers overview response"""
    tiers: Dict[str, VoiceTierInfo]
    total_voices: int
    supported_languages: int


# apps/voice-marketplace/src/schemas/purchase.py
"""
Purchase Pydantic Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PaymentMethodEnum(str, Enum):
    """Payment method enumeration"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    CREDIT = "credit"
    TRIAL = "trial"


class PurchaseStatusEnum(str, Enum):
    """Purchase status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class CartItem(BaseModel):
    """Shopping cart item schema"""
    voice_id: str
    voice_name: str
    tier: str
    price_per_minute: float
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Shopping cart response schema"""
    items: List[CartItem]
    total_items: int
    estimated_cost: str = Field(..., description="Estimated monthly cost")
    
    @validator('estimated_cost', pre=True)
    def format_estimated_cost(cls, v, values):
        """Calculate estimated cost based on average usage"""
        if 'items' in values:
            total_price = sum(item.price_per_minute for item in values['items'])
            # Estimate 100 minutes usage per voice per month
            estimated = total_price * 100
            return f"${estimated:.2f}/month (estimated for 100 min/voice)"
        return "$0.00/month"


class PurchaseItemCreate(BaseModel):
    """Purchase item creation schema"""
    voice_id: str
    
    @validator('voice_id')
    def validate_voice_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Voice ID cannot be empty')
        return v.strip()


class PurchaseCreateRequest(BaseModel):
    """Purchase creation request schema"""
    voice_ids: List[str] = Field(..., min_items=1, max_items=20)
    payment_method: PaymentMethodEnum = PaymentMethodEnum.STRIPE
    billing_address: Optional[Dict[str, str]] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('voice_ids')
    def validate_voice_ids(cls, v):
        if not v:
            raise ValueError('At least one voice must be selected')
        unique_ids = list(set(v))
        if len(unique_ids) != len(v):
            raise ValueError('Duplicate voice IDs are not allowed')
        return unique_ids


class PurchaseItemResponse(BaseModel):
    """Purchase item response schema"""
    id: str
    voice_id: str
    voice_name: str
    voice_tier: str
    price_per_minute: float
    total_minutes_used: float = 0.0
    total_calls_made: int = 0
    created_at: datetime
    activated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PurchaseResponse(BaseModel):
    """Purchase response schema"""
    id: str
    user_id: str
    organization_id: Optional[str] = None
    total_amount: float
    currency: str = "USD"
    payment_method: PaymentMethodEnum
    status: PurchaseStatusEnum
    total_voices: int
    items: List[PurchaseItemResponse]
    created_at: datetime
    completed_at: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseListResponse(BaseModel):
    """Purchase list response schema"""
    purchases: List[PurchaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaymentIntentResponse(BaseModel):
    """Stripe payment intent response"""
    client_secret: str
    payment_intent_id: str
    amount: int  # Amount in cents
    currency: str = "usd"


# apps/voice-marketplace/src/schemas/review.py
"""
Review Pydantic Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class ReviewCreateRequest(BaseModel):
    """Review creation request schema"""
    voice_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, max_length=2000)
    use_case: Optional[str] = Field(None, max_length=100, description="What you used the voice for")
    industry: Optional[str] = Field(None, max_length=100, description="Your industry")
    call_volume: Optional[str] = Field(None, regex="^(Low|Medium|High)$", description="Your typical call volume")
    
    @validator('content')
    def validate_content(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Review content must be at least 10 characters long')
        return v.strip() if v else None
    
    @validator('title')
    def validate_title(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('Review title must be at least 3 characters long')
        return v.strip() if v else None


class ReviewUpdateRequest(BaseModel):
    """Review update request schema"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, max_length=2000)
    use_case: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    call_volume: Optional[str] = Field(None, regex="^(Low|Medium|High)$")


class ReviewResponse(BaseModel):
    """Review response schema"""
    id: str
    voice_id: str
    user_id: str
    rating: int
    title: Optional[str] = None
    content: Optional[str] = None
    use_case: Optional[str] = None
    industry: Optional[str] = None
    call_volume: Optional[str] = None
    helpful_votes: int = 0
    total_votes: int = 0
    helpfulness_ratio: float = 0.0
    is_verified: bool = False
    is_approved: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Review list response schema"""
    reviews: List[ReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}


class ReviewHelpfulnessRequest(BaseModel):
    """Review helpfulness vote request"""
    helpful: bool = Field(..., description="True if helpful, False if not helpful")