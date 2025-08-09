# apps/voice-marketplace/src/models/__init__.py
from .voice_listing import VoiceListing
from .purchase import Purchase, PurchaseItem
from .review import Review
from .category import Category

__all__ = [
    "VoiceListing",
    "Purchase", 
    "PurchaseItem",
    "Review",
    "Category"
]


# apps/voice-marketplace/src/models/voice_listing.py
"""
Voice Listing Database Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from shared.database.models import Base


class VoiceTier(str, enum.Enum):
    """Voice tier enumeration"""
    STANDARD = "standard"
    PRO = "pro" 
    ENTERPRISE = "enterprise"
    ELITE = "elite"


class VoiceGender(str, enum.Enum):
    """Voice gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class VoiceStatus(str, enum.Enum):
    """Voice status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DEPRECATED = "deprecated"


class VoiceListing(Base):
    """Voice listing model for marketplace"""
    
    __tablename__ = "voice_listings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic info
    voice_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    tier = Column(Enum(VoiceTier), nullable=False, index=True)
    
    # Voice characteristics
    language = Column(String(10), nullable=False, index=True)  # EN-US, ES-ES, etc.
    gender = Column(Enum(VoiceGender), nullable=False, index=True)
    accent = Column(String(100), nullable=False)
    style = Column(String(100), nullable=False, index=True)
    
    # Pricing
    price_per_minute = Column(Float, nullable=False)
    
    # Quality metrics
    quality_score = Column(Integer, nullable=False)  # 0-100
    
    # Descriptions
    description = Column(Text, nullable=False)
    short_description = Column(String(500))
    
    # Performance metrics
    total_calls = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Percentage
    avg_duration = Column(Float, default=0.0)  # Minutes
    satisfaction_score = Column(Float, default=0.0)  # 0-5 scale
    
    # Reviews and ratings
    total_reviews = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)  # 0-5 scale
    
    # Sample data
    sample_count = Column(Integer, default=0)
    sample_urls = Column(JSON)  # List of sample audio URLs
    
    # Tags and metadata
    tags = Column(JSON)  # List of tags like ['Professional', 'Friendly']
    personality_traits = Column(JSON)  # List of personality traits
    use_cases = Column(JSON)  # Recommended use cases
    
    # Technical specs
    supported_emotions = Column(JSON)  # Emotions this voice supports
    emotional_range = Column(Integer, default=1)  # 1-5 scale
    languages_supported = Column(JSON)  # Additional languages
    
    # Provider info
    provider = Column(String(100), nullable=False)
    provider_voice_id = Column(String(200))
    provider_metadata = Column(JSON)
    
    # Avatar and display
    avatar = Column(String(10))  # Emoji avatar
    thumbnail_url = Column(String(500))
    demo_url = Column(String(500))
    
    # Status and availability
    status = Column(Enum(VoiceStatus), default=VoiceStatus.ACTIVE, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    is_new = Column(Boolean, default=False, index=True)
    is_popular = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchases = relationship("PurchaseItem", back_populates="voice")
    reviews = relationship("Review", back_populates="voice")
    
    def __repr__(self):
        return f"<VoiceListing {self.name} ({self.tier}) - {self.language}>"
    
    @property
    def tier_display(self):
        """Get display name for tier"""
        tier_names = {
            VoiceTier.STANDARD: "Standard",
            VoiceTier.PRO: "Pro",
            VoiceTier.ENTERPRISE: "Enterprise", 
            VoiceTier.ELITE: "Elite"
        }
        return tier_names.get(self.tier, self.tier.value)
    
    @property
    def performance_metrics(self):
        """Get performance metrics as dict"""
        return {
            "success_rate": self.success_rate,
            "avg_duration": self.avg_duration,
            "satisfaction": self.satisfaction_score
        }
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "voice_id": self.voice_id,
            "name": self.name,
            "tier": self.tier.value,
            "language": self.language,
            "gender": self.gender.value,
            "accent": self.accent,
            "style": self.style,
            "price": self.price_per_minute,
            "quality": self.quality_score,
            "description": self.description,
            "performance": self.performance_metrics,
            "rating": self.average_rating,
            "reviews": self.total_reviews,
            "samples": self.sample_count,
            "tags": self.tags or [],
            "avatar": self.avatar,
            "provider": self.provider,
            "status": self.status.value,
            "is_featured": self.is_featured,
            "is_new": self.is_new,
            "is_popular": self.is_popular,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# apps/voice-marketplace/src/models/purchase.py
"""
Purchase Database Models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from shared.database.models import Base


class PurchaseStatus(str, enum.Enum):
    """Purchase status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    CREDIT = "credit"
    TRIAL = "trial"


class Purchase(Base):
    """Purchase order model"""
    
    __tablename__ = "purchases"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User info
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), index=True)
    
    # Purchase details
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Payment info
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_provider_id = Column(String(200))  # Stripe payment intent ID
    payment_metadata = Column(JSON)
    
    # Status
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.PENDING, index=True)
    
    # Notes and metadata
    notes = Column(Text)
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Purchase {self.id} - ${self.total_amount} ({self.status})>"
    
    @property
    def total_voices(self):
        """Get total number of voices in purchase"""
        return len(self.items)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "payment_method": self.payment_method.value,
            "status": self.status.value,
            "total_voices": self.total_voices,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat()
        }


class PurchaseItem(Base):
    """Individual voice purchase item"""
    
    __tablename__ = "purchase_items"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False)
    voice_id = Column(UUID(as_uuid=True), ForeignKey("voice_listings.id"), nullable=False)
    
    # Item details
    voice_name = Column(String(200), nullable=False)
    voice_tier = Column(String(50), nullable=False)
    price_per_minute = Column(Float, nullable=False)
    
    # Usage tracking
    total_minutes_used = Column(Float, default=0.0)
    total_calls_made = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    activated_at = Column(DateTime)
    
    # Relationships
    purchase = relationship("Purchase", back_populates="items")
    voice = relationship("VoiceListing", back_populates="purchases")
    
    def __repr__(self):
        return f"<PurchaseItem {self.voice_name} - ${self.price_per_minute}/min>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "voice_id": str(self.voice_id),
            "voice_name": self.voice_name,
            "voice_tier": self.voice_tier,
            "price_per_minute": self.price_per_minute,
            "total_minutes_used": self.total_minutes_used,
            "total_calls_made": self.total_calls_made,
            "created_at": self.created_at.isoformat(),
            "activated_at": self.activated_at.isoformat() if self.activated_at else None
        }


# apps/voice-marketplace/src/models/review.py
"""
Review Database Models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from shared.database.models import Base


class Review(Base):
    """Voice review model"""
    
    __tablename__ = "voice_reviews"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    voice_id = Column(UUID(as_uuid=True), ForeignKey("voice_listings.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200))
    content = Column(Text)
    
    # Usage context
    use_case = Column(String(100))  # What they used it for
    industry = Column(String(100))  # Their industry
    call_volume = Column(String(50))  # Low/Medium/High
    
    # Helpful votes
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Moderation
    is_verified = Column(Boolean, default=False)  # Verified purchase
    is_approved = Column(Boolean, default=True)
    moderation_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    voice = relationship("VoiceListing", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review {self.rating}/5 for Voice {self.voice_id}>"
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio"""
        if self.total_votes == 0:
            return 0.0
        return self.helpful_votes / self.total_votes
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "voice_id": str(self.voice_id),
            "user_id": str(self.user_id),
            "rating": self.rating,
            "title": self.title,
            "content": self.content,
            "use_case": self.use_case,
            "industry": self.industry,
            "call_volume": self.call_volume,
            "helpful_votes": self.helpful_votes,
            "total_votes": self.total_votes,
            "helpfulness_ratio": self.helpfulness_ratio,
            "is_verified": self.is_verified,
            "is_approved": self.is_approved,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# apps/voice-marketplace/src/models/category.py
"""
Category Database Models
"""

from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from shared.database.models import Base


class Category(Base):
    """Voice category model for organization"""
    
    __tablename__ = "voice_categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Category info
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Display
    icon = Column(String(50))  # Icon name or emoji
    color = Column(String(7))  # Hex color code
    sort_order = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Category {self.name}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }