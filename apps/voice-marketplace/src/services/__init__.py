# apps/voice-marketplace/src/services/__init__.py
from .marketplace_service import MarketplaceService
from .payment_service import PaymentService
from .review_service import ReviewService
from .category_service import CategoryService

__all__ = [
    "MarketplaceService",
    "PaymentService", 
    "ReviewService",
    "CategoryService"
]


# apps/voice-marketplace/src/services/marketplace_service.py
"""
Marketplace Business Logic Service
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import json

from models.voice_listing import VoiceListing, VoiceTier, VoiceGender, VoiceStatus
from models.purchase import Purchase, PurchaseItem
from models.review import Review
from schemas.marketplace import VoiceFilterRequest, VoiceListingResponse
from core.config import settings
from shared.utils.service_client import ServiceClient

logger = logging.getLogger(__name__)


class MarketplaceService:
    """Service for marketplace operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.service_client = ServiceClient()
    
    async def initialize_voice_data(self):
        """Initialize voice data if empty"""
        try:
            # Check if we have voices
            voice_count = self.db.query(VoiceListing).count()
            
            if voice_count == 0:
                logger.info("🎭 Initializing voice marketplace data...")
                await self._create_initial_voices()
                logger.info("✅ Voice marketplace data initialized")
            else:
                logger.info(f"📊 Found {voice_count} voices in marketplace")
                
        except Exception as e:
            logger.error(f"❌ Error initializing voice data: {e}")
            raise
    
    async def _create_initial_voices(self):
        """Create initial voice listings from frontend data"""
        
        # Standard voices (8 voices)
        standard_voices = [
            {
                "voice_id": "std_sarah_us", "name": "Sarah - Professional US", "tier": VoiceTier.STANDARD,
                "language": "EN-US", "gender": VoiceGender.FEMALE, "accent": "American", "style": "Professional",
                "quality": 85, "description": "Clear, professional American female voice perfect for appointment setting",
                "samples": 3, "reviews": 2847, "rating": 4.3, "price": 0.08,
                "tags": ["Professional", "Clear", "Trustworthy"], "avatar": "👩‍💼",
                "performance": {"success_rate": 68, "avg_duration": 3.2, "satisfaction": 4.1},
                "provider": "Piper TTS"
            },
            {
                "voice_id": "std_mike_us", "name": "Mike - Friendly US", "tier": VoiceTier.STANDARD,
                "language": "EN-US", "gender": VoiceGender.MALE, "accent": "American", "style": "Friendly",
                "quality": 82, "description": "Warm, approachable American male voice for cold calling campaigns",
                "samples": 4, "reviews": 1923, "rating": 4.1, "price": 0.08,
                "tags": ["Friendly", "Warm", "Persuasive"], "avatar": "👨‍💼",
                "performance": {"success_rate": 71, "avg_duration": 4.1, "satisfaction": 4.0},
                "provider": "Piper TTS"
            },
            {
                "voice_id": "std_emma_uk", "name": "Emma - Professional UK", "tier": VoiceTier.STANDARD,
                "language": "EN-GB", "gender": VoiceGender.FEMALE, "accent": "British", "style": "Professional",
                "quality": 83, "description": "Professional British female voice with clear diction",
                "samples": 3, "reviews": 1456, "rating": 4.2, "price": 0.08,
                "tags": ["Professional", "British", "Clear"], "avatar": "🇬🇧",
                "performance": {"success_rate": 69, "avg_duration": 3.8, "satisfaction": 4.2},
                "provider": "Piper TTS"
            },
            {
                "voice_id": "std_carlos_es", "name": "Carlos - Bilingual Pro", "tier": VoiceTier.STANDARD,
                "language": "ES-MX", "gender": VoiceGender.MALE, "accent": "Mexican", "style": "Professional",
                "quality": 80, "description": "Native Spanish speaker with clear English pronunciation",
                "samples": 3, "reviews": 987, "rating": 4.0, "price": 0.08,
                "tags": ["Bilingual", "Professional", "Clear"], "avatar": "🌎",
                "performance": {"success_rate": 67, "avg_duration": 4.2, "satisfaction": 3.9},
                "provider": "Piper TTS"
            },
            {
                "voice_id": "std_maria_es", "name": "Maria - Friendly Spanish", "tier": VoiceTier.STANDARD,
                "language": "ES-ES", "gender": VoiceGender.FEMALE, "accent": "Spanish", "style": "Friendly",
                "quality": 81, "description": "Warm Spanish female voice perfect for Hispanic markets",
                "samples": 3, "reviews": 743, "rating": 4.1, "price": 0.08,
                "tags": ["Friendly", "Spanish", "Warm"], "avatar": "🇪🇸",
                "performance": {"success_rate": 70, "avg_duration": 3.9, "satisfaction": 4.0},
                "provider": "Piper TTS"
            },
            {
                "voice_id": "std_james_uk", "name": "James - Formal UK", "tier": VoiceTier.STANDARD,
                "language": "EN-GB", "gender": VoiceGender.MALE, "accent": "British", "style": "Formal",
                "quality": 84, "description": "Formal British male voice for professional communications",
                "samples": 3, "reviews": 1234, "rating": 4.2, "price": 0.08,
                "tags": ["Formal", "British", "Professional"], "avatar": "🎩",
                "performance": {"success_rate": 72, "avg_duration": 3.6, "satisfaction": 4.1},
                "provider": "Piper TTS"
            },
            {
                "voice_id": "std_lisa_neutral", "name": "Lisa - Neutral Accent", "tier": VoiceTier.STANDARD,
                "language": "EN-US", "gender": VoiceGender.FEMALE, "accent": "Neutral", "style": "Professional",
                "quality": 83, "description": "Neutral accent female voice suitable for global audiences",
                "samples": 3, "reviews": 891, "rating": 4.0, "price": 0.08,
                "tags": ["Neutral", "Global", "Professional"], "avatar": "🌍",
                "performance": {"success_rate": 68, "avg_duration": 3.7, "satisfaction": 4.0},
                "provider": "Piper TTS"
            },
            {
                "voice_id": "std_david_energetic", "name": "David - Energetic US", "tier": VoiceTier.STANDARD,
                "language": "EN-US", "gender": VoiceGender.MALE, "accent": "American", "style": "Energetic",
                "quality": 82, "description": "High-energy American male voice for motivational calls",
                "samples": 3, "reviews": 678, "rating": 4.1, "price": 0.08,
                "tags": ["Energetic", "Motivational", "Dynamic"], "avatar": "⚡",
                "performance": {"success_rate": 74, "avg_duration": 4.0, "satisfaction": 4.2},
                "provider": "Piper TTS"
            }
        ]
        
        # Pro voices (12 voices)
        pro_voices = [
            {
                "voice_id": "pro_sophia_elegant", "name": "Sophia - Elegant US", "tier": VoiceTier.PRO,
                "language": "EN-US", "gender": VoiceGender.FEMALE, "accent": "American", "style": "Elegant",
                "quality": 94, "description": "Sophisticated American female voice for premium client interactions",
                "samples": 6, "reviews": 4821, "rating": 4.8, "price": 0.18,
                "tags": ["Elegant", "Sophisticated", "Premium"], "avatar": "👑",
                "performance": {"success_rate": 89, "avg_duration": 5.7, "satisfaction": 4.7},
                "provider": "Ramble.AI"
            },
            {
                "voice_id": "pro_alexander_formal", "name": "Alexander - Formal UK", "tier": VoiceTier.PRO,
                "language": "EN-GB", "gender": VoiceGender.MALE, "accent": "British", "style": "Formal",
                "quality": 93, "description": "Distinguished British male voice for executive communications",
                "samples": 5, "reviews": 3456, "rating": 4.7, "price": 0.18,
                "tags": ["Formal", "Executive", "Distinguished"], "avatar": "🎯",
                "performance": {"success_rate": 87, "avg_duration": 6.1, "satisfaction": 4.6},
                "provider": "Ramble.AI"
            }
            # ... Add more pro voices
        ]
        
        # Enterprise voices (18 voices) 
        enterprise_voices = [
            {
                "voice_id": "ent_victoria_executive", "name": "Victoria - C-Suite Executive", "tier": VoiceTier.ENTERPRISE,
                "language": "EN-US", "gender": VoiceGender.FEMALE, "accent": "American", "style": "Executive",
                "quality": 97, "description": "Authoritative female executive voice for C-level conversations",
                "samples": 4, "reviews": 1247, "rating": 4.9, "price": 0.25,
                "tags": ["Executive", "Authoritative", "C-Suite"], "avatar": "🏆",
                "performance": {"success_rate": 93, "avg_duration": 8.1, "satisfaction": 4.8},
                "provider": "ElevenLabs + Custom"
            }
            # ... Add more enterprise voices
        ]
        
        # Elite voices (25+ voices)
        elite_voices = [
            {
                "voice_id": "elite_aurora_ultra", "name": "Aurora - Ultra Premium", "tier": VoiceTier.ELITE,
                "language": "EN-US", "gender": VoiceGender.FEMALE, "accent": "American", "style": "Ultra-Realistic",
                "quality": 99, "description": "Ultra-realistic voice with perfect emotional intelligence and human-like nuances",
                "samples": 8, "reviews": 847, "rating": 4.95, "price": 0.35,
                "tags": ["Ultra-Realistic", "Emotional AI", "Human-Like"], "avatar": "💎",
                "performance": {"success_rate": 97, "avg_duration": 9.4, "satisfaction": 4.9},
                "provider": "ElevenLabs Premium"
            }
            # ... Add more elite voices
        ]
        
        # Create voice listings
        all_voices = standard_voices + pro_voices + enterprise_voices + elite_voices
        
        for voice_data in all_voices:
            voice = VoiceListing(
                voice_id=voice_data["voice_id"],
                name=voice_data["name"],
                tier=voice_data["tier"],
                language=voice_data["language"],
                gender=voice_data["gender"],
                accent=voice_data["accent"],
                style=voice_data["style"],
                price_per_minute=voice_data["price"],
                quality_score=voice_data["quality"],
                description=voice_data["description"],
                total_calls=voice_data.get("performance", {}).get("total_calls", 0),
                success_rate=voice_data.get("performance", {}).get("success_rate", 0),
                avg_duration=voice_data.get("performance", {}).get("avg_duration", 0),
                satisfaction_score=voice_data.get("performance", {}).get("satisfaction", 0),
                total_reviews=voice_data.get("reviews", 0),
                average_rating=voice_data.get("rating", 0),
                sample_count=voice_data.get("samples", 0),
                tags=voice_data.get("tags", []),
                avatar=voice_data.get("avatar"),
                provider=voice_data.get("provider", "Unknown"),
                status=VoiceStatus.ACTIVE,
                is_popular=voice_data.get("rating", 0) >= 4.5
            )
            self.db.add(voice)
        
        self.db.commit()
        logger.info(f"✅ Created {len(all_voices)} voice listings")
    
    async def get_voices(self, filters: VoiceFilterRequest) -> Tuple[List[VoiceListingResponse], int]:
        """Get filtered voices with pagination"""
        try:
            query = self.db.query(VoiceListing).filter(VoiceListing.status == VoiceStatus.ACTIVE)
            
            # Apply filters
            if filters.tier:
                query = query.filter(VoiceListing.tier == filters.tier)
            
            if filters.language and filters.language != "all":
                query = query.filter(VoiceListing.language.startswith(filters.language))
            
            if filters.gender and filters.gender != "all":
                query = query.filter(VoiceListing.gender == filters.gender)
            
            if filters.style:
                query = query.filter(VoiceListing.style.ilike(f"%{filters.style}%"))
            
            if filters.min_rating:
                query = query.filter(VoiceListing.average_rating >= filters.min_rating)
            
            if filters.max_price:
                query = query.filter(VoiceListing.price_per_minute <= filters.max_price)
            
            if filters.search_query:
                search_term = f"%{filters.search_query}%"
                query = query.filter(
                    or_(
                        VoiceListing.name.ilike(search_term),
                        VoiceListing.description.ilike(search_term),
                        VoiceListing.tags.op('@>')([filters.search_query])
                    )
                )
            
            if filters.is_featured is not None:
                query = query.filter(VoiceListing.is_featured == filters.is_featured)
            
            if filters.is_new is not None:
                query = query.filter(VoiceListing.is_new == filters.is_new)
            
            if filters.is_popular is not None:
                query = query.filter(VoiceListing.is_popular == filters.is_popular)
            
            # Count total
            total = query.count()
            
            # Apply sorting
            sort_field = getattr(VoiceListing, filters.sort_by, VoiceListing.name)
            if filters.sort_order == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(asc(sort_field))
            
            # Apply pagination
            offset = (filters.page - 1) * filters.page_size
            voices = query.offset(offset).limit(filters.page_size).all()
            
            # Convert to response schema
            voice_responses = []
            for voice in voices:
                voice_dict = voice.to_dict()
                voice_responses.append(VoiceListingResponse(**voice_dict))
            
            logger.info(f"📊 Retrieved {len(voice_responses)} voices (page {filters.page})")
            return voice_responses, total
            
        except Exception as e:
            logger.error(f"❌ Error getting voices: {e}")
            raise
    
    async def get_voice_by_id(self, voice_id: str) -> Optional[VoiceListingResponse]:
        """Get voice by ID"""
        try:
            voice = self.db.query(VoiceListing).filter(
                and_(
                    VoiceListing.voice_id == voice_id,
                    VoiceListing.status == VoiceStatus.ACTIVE
                )
            ).first()
            
            if not voice:
                return None
            
            voice_dict = voice.to_dict()
            return VoiceListingResponse(**voice_dict)
            
        except Exception as e:
            logger.error(f"❌ Error getting voice {voice_id}: {e}")
            raise
    
    async def get_voice_comparison(self, voice_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple voices"""
        try:
            voices = self.db.query(VoiceListing).filter(
                and_(
                    VoiceListing.voice_id.in_(voice_ids),
                    VoiceListing.status == VoiceStatus.ACTIVE
                )
            ).all()
            
            if len(voices) < 2:
                raise ValueError("At least 2 voices required for comparison")
            
            # Convert to response format
            voice_responses = []
            for voice in voices:
                voice_dict = voice.to_dict()
                voice_responses.append(VoiceListingResponse(**voice_dict))
            
            # Create comparison matrix
            comparison_matrix = {
                "price_range": {
                    "min": min(v.price for v in voice_responses),
                    "max": max(v.price for v in voice_responses),
                    "avg": sum(v.price for v in voice_responses) / len(voice_responses)
                },
                "quality_range": {
                    "min": min(v.quality for v in voice_responses),
                    "max": max(v.quality for v in voice_responses),
                    "avg": sum(v.quality for v in voice_responses) / len(voice_responses)
                },
                "performance_avg": {
                    "success_rate": sum(v.performance.success_rate for v in voice_responses) / len(voice_responses),
                    "satisfaction": sum(v.performance.satisfaction for v in voice_responses) / len(voice_responses)
                }
            }
            
            # Generate recommendations
            recommendations = []
            best_value = min(voice_responses, key=lambda v: v.price)
            best_quality = max(voice_responses, key=lambda v: v.quality)
            best_rated = max(voice_responses, key=lambda v: v.rating)
            
            recommendations.append(f"💰 Best Value: {best_value.name} at ${best_value.price}/min")
            recommendations.append(f"⭐ Highest Quality: {best_quality.name} ({best_quality.quality}% quality)")
            recommendations.append(f"👍 Best Rated: {best_rated.name} ({best_rated.rating}/5 stars)")
            
            return {
                "voices": voice_responses,
                "comparison_matrix": comparison_matrix,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"❌ Error comparing voices: {e}")
            raise
    
    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        try:
            # Total voices by tier
            tier_stats = self.db.query(
                VoiceListing.tier,
                func.count(VoiceListing.id).label('count')
            ).filter(VoiceListing.status == VoiceStatus.ACTIVE).group_by(VoiceListing.tier).all()
            
            voices_by_tier = {tier.value: count for tier, count in tier_stats}
            total_voices = sum(voices_by_tier.values())
            
            # Purchase stats
            today = datetime.utcnow().date()
            total_purchases = self.db.query(Purchase).count()
            
            revenue_today = self.db.query(func.sum(Purchase.total_amount)).filter(
                func.date(Purchase.created_at) == today,
                Purchase.status == "completed"
            ).scalar() or 0.0
            
            revenue_this_month = self.db.query(func.sum(Purchase.total_amount)).filter(
                Purchase.created_at >= datetime.utcnow().replace(day=1),
                Purchase.status == "completed"
            ).scalar() or 0.0
            
            # Most popular tier
            popular_tier_data = self.db.query(
                VoiceListing.tier,
                func.count(PurchaseItem.id).label('purchase_count')
            ).join(PurchaseItem).group_by(VoiceListing.tier).order_by(desc('purchase_count')).first()
            
            popular_tier = popular_tier_data[0].value if popular_tier_data else "pro"
            
            # Average rating
            avg_rating = self.db.query(func.avg(VoiceListing.average_rating)).filter(
                VoiceListing.status == VoiceStatus.ACTIVE
            ).scalar() or 0.0
            
            # Active users (users who made purchases in last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = self.db.query(func.count(func.distinct(Purchase.user_id))).filter(
                Purchase.created_at >= thirty_days_ago
            ).scalar() or 0
            
            # Top voices
            top_voices = self.db.query(VoiceListing).filter(
                VoiceListing.status == VoiceStatus.ACTIVE
            ).order_by(desc(VoiceListing.average_rating)).limit(5).all()
            
            top_voice_responses = []
            for voice in top_voices:
                voice_dict = voice.to_dict()
                top_voice_responses.append(VoiceListingResponse(**voice_dict))
            
            # Trending voices (most purchased in last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            trending_voices = self.db.query(VoiceListing).join(PurchaseItem).join(Purchase).filter(
                Purchase.created_at >= seven_days_ago,
                VoiceListing.status == VoiceStatus.ACTIVE
            ).group_by(VoiceListing.id).order_by(desc(func.count(PurchaseItem.id))).limit(5).all()
            
            trending_voice_responses = []
            for voice in trending_voices:
                voice_dict = voice.to_dict()
                trending_voice_responses.append(VoiceListingResponse(**voice_dict))
            
            return {
                "total_voices": total_voices,
                "voices_by_tier": voices_by_tier,
                "total_purchases": total_purchases,
                "revenue_today": revenue_today,
                "revenue_this_month": revenue_this_month,
                "popular_tier": popular_tier,
                "avg_rating": round(avg_rating, 2),
                "active_users": active_users,
                "top_voices": top_voice_responses,
                "trending_voices": trending_voice_responses
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting marketplace stats: {e}")
            raise
    
    async def get_voice_tiers(self) -> Dict[str, Any]:
        """Get voice tier information"""
        try:
            tiers = {}
            
            for tier_name, price in settings.VOICE_TIER_PRICING.items():
                # Count voices in this tier
                voice_count = self.db.query(VoiceListing).filter(
                    and_(
                        VoiceListing.tier == VoiceTier(tier_name),
                        VoiceListing.status == VoiceStatus.ACTIVE
                    )
                ).count()
                
                provider_info = settings.VOICE_PROVIDERS.get(tier_name, {})
                
                tiers[tier_name] = {
                    "name": tier_name.title(),
                    "price": price,
                    "voice_count": voice_count,
                    "languages": provider_info.get("languages", "Unknown"),
                    "features": provider_info.get("features", []),
                    "use_case": self._get_tier_use_case(tier_name),
                    "provider": provider_info.get("provider", "Unknown"),
                    "color": self._get_tier_color(tier_name),
                    "popular": tier_name == "pro"
                }
            
            total_voices = sum(tier["voice_count"] for tier in tiers.values())
            
            return {
                "tiers": tiers,
                "total_voices": total_voices,
                "supported_languages": 70
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting voice tiers: {e}")
            raise
    
    def _get_tier_use_case(self, tier: str) -> str:
        """Get use case for tier"""
        use_cases = {
            "standard": "Appointment setting & cold calling",
            "pro": "Sales calls & client follow-ups", 
            "enterprise": "Branded outbound campaigns",
            "elite": "VIP clients & high-stakes conversations"
        }
        return use_cases.get(tier, "General use")
    
    def _get_tier_color(self, tier: str) -> str:
        """Get color for tier"""
        colors = {
            "standard": "green",
            "pro": "blue",
            "enterprise": "purple", 
            "elite": "red"
        }
        return colors.get(tier, "gray")


# apps/voice-marketplace/src/services/payment_service.py
"""
Payment Processing Service
"""

import logging
import stripe
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from models.purchase import Purchase, PurchaseItem, PurchaseStatus, PaymentMethod
from models.voice_listing import VoiceListing
from schemas.purchase import PurchaseCreateRequest, PurchaseResponse
from core.config import settings
from shared.utils.service_client import ServiceClient

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Service for payment processing"""
    
    def __init__(self, db: Session):
        self.db = db
        self.service_client = ServiceClient()
    
    async def create_purchase(self, user_id: str, request: PurchaseCreateRequest) -> Dict[str, Any]:
        """Create a new purchase"""
        try:
            # Get voices
            voices = self.db.query(VoiceListing).filter(
                VoiceListing.voice_id.in_(request.voice_ids)
            ).all()
            
            if len(voices) != len(request.voice_ids):
                raise ValueError("Some voices not found")
            
            # Calculate total amount
            total_amount = sum(voice.price_per_minute for voice in voices)
            
            # Create purchase record
            purchase = Purchase(
                user_id=user_id,
                total_amount=total_amount,
                payment_method=request.payment_method,
                notes=request.notes
            )
            
            self.db.add(purchase)
            self.db.flush()  # Get the ID
            
            # Create purchase items
            for voice in voices:
                item = PurchaseItem(
                    purchase_id=purchase.id,
                    voice_id=voice.id,
                    voice_name=voice.name,
                    voice_tier=voice.tier.value,
                    price_per_minute=voice.price_per_minute
                )
                self.db.add(item)
            
            # Create Stripe payment intent if using Stripe
            payment_intent = None
            if request.payment_method == PaymentMethod.STRIPE:
                payment_intent = await self._create_stripe_payment_intent(
                    purchase.id, total_amount, request.billing_address
                )
                purchase.payment_provider_id = payment_intent["id"]
                purchase.payment_metadata = {"client_secret": payment_intent["client_secret"]}
            
            self.db.commit()
            
            # Convert to response
            purchase_dict = purchase.to_dict()
            purchase_response = PurchaseResponse(**purchase_dict)
            
            result = {
                "purchase": purchase_response,
                "payment_intent": payment_intent
            }
            
            logger.info(f"✅ Created purchase {purchase.id} for user {user_id} - ${total_amount}")
            return result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating purchase: {e}")
            raise
    
    async def _create_stripe_payment_intent(self, purchase_id: str, amount: float, billing_address: Optional[Dict]) -> Dict[str, Any]:
        """Create Stripe payment intent"""
        try:
            # Convert to cents
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                metadata={
                    "purchase_id": str(purchase_id),
                    "service": "voice-marketplace"
                },
                automatic_payment_methods={"enabled": True}
            )
            
            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount_cents,
                "currency": "usd"
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating Stripe payment intent: {e}")
            raise
    
    async def confirm_purchase(self, purchase_id: str, payment_intent_id: str) -> PurchaseResponse:
        """Confirm purchase payment"""
        try:
            purchase = self.db.query(Purchase).filter(Purchase.id == purchase_id).first()
            
            if not purchase:
                raise ValueError("Purchase not found")
            
            # Verify with Stripe
            if purchase.payment_method == PaymentMethod.STRIPE:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                
                if payment_intent.status == "succeeded":
                    purchase.status = PurchaseStatus.COMPLETED
                    purchase.completed_at = datetime.utcnow()
                    
                    # Activate purchase items
                    for item in purchase.items:
                        item.activated_at = datetime.utcnow()
                    
                    self.db.commit()
                    
                    # Notify billing service
                    await self._notify_billing_service(purchase)
                    
                    logger.info(f"✅ Purchase {purchase_id} confirmed and activated")
                else:
                    purchase.status = PurchaseStatus.FAILED
                    self.db.commit()
                    logger.warning(f"⚠️ Purchase {purchase_id} payment failed")
            
            purchase_dict = purchase.to_dict()
            return PurchaseResponse(**purchase_dict)
            
        except Exception as e:
            logger.error(f"❌ Error confirming purchase: {e}")
            raise
    
    async def _notify_billing_service(self, purchase: Purchase):
        """Notify billing service of completed purchase"""
        try:
            billing_data = {
                "user_id": str(purchase.user_id),
                "purchase_id": str(purchase.id),
                "amount": purchase.total_amount,
                "currency": purchase.currency,
                "voice_count": len(purchase.items),
                "completed_at": purchase.completed_at.isoformat()
            }
            
            await self.service_client.post(
                f"{settings.BILLING_SERVICE_URL}/api/v1/purchases",
                data=billing_data
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to notify billing service: {e}")
    
    async def get_user_purchases(self, user_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get user's purchase history"""
        try:
            query = self.db.query(Purchase).filter(Purchase.user_id == user_id)
            
            total = query.count()
            offset = (page - 1) * page_size
            purchases = query.order_by(Purchase.created_at.desc()).offset(offset).limit(page_size).all()
            
            purchase_responses = []
            for purchase in purchases:
                purchase_dict = purchase.to_dict()
                purchase_responses.append(PurchaseResponse(**purchase_dict))
            
            return {
                "purchases": purchase_responses,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user purchases: {e}")
            raise


# apps/voice-marketplace/src/services/review_service.py
"""
Review Management Service
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime

from models.review import Review
from models.voice_listing import VoiceListing
from models.purchase import Purchase, PurchaseItem
from schemas.review import ReviewCreateRequest, ReviewResponse, ReviewUpdateRequest
from shared.utils.service_client import ServiceClient

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for review management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.service_client = ServiceClient()
    
    async def create_review(self, user_id: str, request: ReviewCreateRequest) -> ReviewResponse:
        """Create a new review"""
        try:
            # Check if voice exists
            voice = self.db.query(VoiceListing).filter(
                VoiceListing.voice_id == request.voice_id
            ).first()
            
            if not voice:
                raise ValueError("Voice not found")
            
            # Check if user already reviewed this voice
            existing_review = self.db.query(Review).filter(
                and_(
                    Review.voice_id == voice.id,
                    Review.user_id == user_id
                )
            ).first()
            
            if existing_review:
                raise ValueError("You have already reviewed this voice")
            
            # Check if user purchased this voice
            has_purchased = self.db.query(PurchaseItem).join(Purchase).filter(
                and_(
                    PurchaseItem.voice_id == voice.id,
                    Purchase.user_id == user_id,
                    Purchase.status == "completed"
                )
            ).first()
            
            # Create review
            review = Review(
                voice_id=voice.id,
                user_id=user_id,
                rating=request.rating,
                title=request.title,
                content=request.content,
                use_case=request.use_case,
                industry=request.industry,
                call_volume=request.call_volume,
                is_verified=bool(has_purchased)
            )
            
            self.db.add(review)
            self.db.commit()
            
            # Update voice rating
            await self._update_voice_rating(voice.id)
            
            review_dict = review.to_dict()
            
            logger.info(f"✅ Created review for voice {request.voice_id} by user {user_id}")
            return ReviewResponse(**review_dict)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating review: {e}")
            raise
    
    async def _update_voice_rating(self, voice_id: str):
        """Update voice average rating and review count"""
        try:
            # Calculate new average rating
            rating_stats = self.db.query(
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('review_count')
            ).filter(
                and_(
                    Review.voice_id == voice_id,
                    Review.is_approved == True
                )
            ).first()
            
            # Update voice
            voice = self.db.query(VoiceListing).filter(VoiceListing.id == voice_id).first()
            if voice:
                voice.average_rating = round(rating_stats.avg_rating or 0.0, 2)
                voice.total_reviews = rating_stats.review_count or 0
                voice.updated_at = datetime.utcnow()
                
                # Update popularity based on rating
                voice.is_popular = voice.average_rating >= 4.5
                
                self.db.commit()
                
        except Exception as e:
            logger.error(f"❌ Error updating voice rating: {e}")
    
    async def get_voice_reviews(self, voice_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get reviews for a voice"""
        try:
            voice = self.db.query(VoiceListing).filter(
                VoiceListing.voice_id == voice_id
            ).first()
            
            if not voice:
                raise ValueError("Voice not found")
            
            query = self.db.query(Review).filter(
                and_(
                    Review.voice_id == voice.id,
                    Review.is_approved == True
                )
            )
            
            total = query.count()
            offset = (page - 1) * page_size
            reviews = query.order_by(desc(Review.created_at)).offset(offset).limit(page_size).all()
            
            review_responses = []
            for review in reviews:
                review_dict = review.to_dict()
                review_responses.append(ReviewResponse(**review_dict))
            
            # Get rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                count = self.db.query(Review).filter(
                    and_(
                        Review.voice_id == voice.id,
                        Review.rating == i,
                        Review.is_approved == True
                    )
                ).count()
                rating_distribution[i] = count
            
            return {
                "reviews": review_responses,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "average_rating": voice.average_rating,
                "rating_distribution": rating_distribution
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting voice reviews: {e}")
            raise


# apps/voice-marketplace/src/services/category_service.py
"""
Category Management Service
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from models.category import Category
from shared.utils.service_client import ServiceClient

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for category management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.service_client = ServiceClient()
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all active categories"""
        try:
            categories = self.db.query(Category).filter(
                Category.is_active == True
            ).order_by(Category.sort_order, Category.name).all()
            
            return [category.to_dict() for category in categories]
            
        except Exception as e:
            logger.error(f"❌ Error getting categories: {e}")
            raise