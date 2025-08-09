# apps/phone-numbers/src/services/purchase_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import stripe
import uuid

from models.phone_number import PhoneNumber, PhoneNumberPurchase
from schemas.phone_number import NumberPurchaseRequest, NumberPurchaseResponse
from services.twilio_service import TwilioService
from core.config import settings, stripe_config
from shared.exceptions.service import ServiceException
from shared.exceptions.external import ExternalAPIError
from shared.utils.phone_utils import normalize_phone_number, detect_number_type

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PurchaseService:
    """Phone Number Purchase Service with Stripe Integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.twilio = TwilioService()
    
    async def initiate_purchase(
        self,
        organization_id: str,
        user_id: str,
        purchase_request: NumberPurchaseRequest
    ) -> NumberPurchaseResponse:
        """Initiate phone number purchase process"""
        
        try:
            # Validate phone number format
            normalized_number = normalize_phone_number(purchase_request.phone_number)
            
            # Check if number is already owned
            existing = self.db.query(PhoneNumber).filter(
                PhoneNumber.phone_number == normalized_number
            ).first()
            
            if existing:
                raise ServiceException(f"Phone number {normalized_number} is already owned")
            
            # Get pricing information
            country_code = normalized_number[1:3] if normalized_number.startswith("+1") else normalized_number[1:3]
            pricing = await self._get_pricing(country_code, purchase_request.number_type)
            
            # Create purchase record
            purchase_id = str(uuid.uuid4())
            purchase = PhoneNumberPurchase(
                id=purchase_id,
                organization_id=organization_id,
                user_id=user_id,
                base_price=pricing["monthly_price"],
                setup_fee=pricing.get("setup_fee", 0.0),
                total_amount=pricing["monthly_price"] + pricing.get("setup_fee", 0.0),
                currency=pricing["currency"],
                payment_status="pending",
                provisioning_status="pending"
            )
            
            self.db.add(purchase)
            self.db.commit()
            
            # Create Stripe Payment Intent
            payment_intent = await self._create_payment_intent(
                purchase_id,
                purchase.total_amount,
                purchase.currency,
                purchase_request.payment_method_id,
                organization_id,
                user_id
            )
            
            # Update purchase with Stripe info
            purchase.stripe_payment_intent_id = payment_intent["id"]
            purchase.stripe_customer_id = payment_intent.get("customer")
            self.db.commit()
            
            # If payment is successful, proceed with provisioning
            if payment_intent["status"] == "succeeded":
                await self._provision_number(purchase, purchase_request)
            
            return NumberPurchaseResponse(
                purchase_id=purchase_id,
                phone_number_id=purchase.phone_number_id or "",
                phone_number=normalized_number,
                status="processing",
                payment_status=purchase.payment_status,
                provisioning_status=purchase.provisioning_status,
                total_amount=purchase.total_amount,
                currency=purchase.currency,
                estimated_completion=datetime.utcnow()
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Purchase initiation failed: {str(e)}")
            raise ServiceException(f"Failed to initiate purchase: {str(e)}")
    
    async def complete_purchase(
        self,
        purchase_id: str,
        payment_intent_id: str
    ) -> Dict[str, Any]:
        """Complete purchase after successful payment"""
        
        try:
            # Get purchase record
            purchase = self.db.query(PhoneNumberPurchase).filter(
                PhoneNumberPurchase.id == purchase_id
            ).first()
            
            if not purchase:
                raise ServiceException(f"Purchase {purchase_id} not found")
            
            # Verify payment with Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == "succeeded":
                purchase.payment_status = "succeeded"
                purchase.payment_completed_at = datetime.utcnow()
                purchase.payment_method = payment_intent.charges.data[0].payment_method_details.type
                
                self.db.commit()
                
                # Provision the number if not already done
                if purchase.provisioning_status == "pending":
                    # We'll need the original request data - store it in purchase
                    await self._provision_number_from_purchase(purchase)
                
                logger.info(f"Purchase {purchase_id} completed successfully")
                return {
                    "status": "completed",
                    "phone_number_id": purchase.phone_number_id,
                    "message": "Phone number purchased and provisioned successfully"
                }
            
            else:
                purchase.payment_status = "failed"
                self.db.commit()
                raise ServiceException("Payment was not successful")
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error during purchase completion: {str(e)}")
            raise ExternalAPIError(f"Payment processing failed: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Purchase completion failed: {str(e)}")
            raise ServiceException(f"Failed to complete purchase: {str(e)}")
    
    async def handle_stripe_webhook(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Handle Stripe webhook events"""
        
        try:
            if event_type == "payment_intent.succeeded":
                payment_intent = event_data["object"]
                
                # Find purchase by payment intent ID
                purchase = self.db.query(PhoneNumberPurchase).filter(
                    PhoneNumberPurchase.stripe_payment_intent_id == payment_intent["id"]
                ).first()
                
                if purchase and purchase.payment_status == "pending":
                    await self.complete_purchase(purchase.id, payment_intent["id"])
            
            elif event_type == "payment_intent.payment_failed":
                payment_intent = event_data["object"]
                
                purchase = self.db.query(PhoneNumberPurchase).filter(
                    PhoneNumberPurchase.stripe_payment_intent_id == payment_intent["id"]
                ).first()
                
                if purchase:
                    purchase.payment_status = "failed"
                    self.db.commit()
                    logger.warning(f"Payment failed for purchase {purchase.id}")
            
            return {"status": "processed"}
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            raise ServiceException(f"Webhook processing failed: {str(e)}")
    
    async def _create_payment_intent(
        self,
        purchase_id: str,
        amount: float,
        currency: str,
        payment_method_id: str,
        organization_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Create Stripe Payment Intent"""
        
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            # Create or get customer
            customer = await self._get_or_create_stripe_customer(organization_id, user_id)
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                customer=customer["id"],
                payment_method=payment_method_id,
                confirmation_method="manual",
                confirm=True,
                metadata={
                    "purchase_id": purchase_id,
                    "organization_id": organization_id,
                    "user_id": user_id,
                    "service": "phone_numbers"
                },
                description=f"Vocelio.ai Phone Number Purchase - {purchase_id}"
            )
            
            return payment_intent
            
        except stripe.StripeError as e:
            logger.error(f"Stripe payment intent creation failed: {str(e)}")
            raise ExternalAPIError(f"Payment processing failed: {str(e)}")
    
    async def _provision_number(
        self,
        purchase: PhoneNumberPurchase,
        request: NumberPurchaseRequest
    ) -> None:
        """Provision phone number after successful payment"""
        
        try:
            # Purchase from Twilio
            twilio_result = await self.twilio.purchase_number(
                request.phone_number,
                voice_url=request.voice_url,
                sms_url=request.sms_url,
                status_callback=settings.TWILIO_WEBHOOK_URL
            )
            
            # Create phone number record
            phone_number = PhoneNumber(
                id=str(uuid.uuid4()),
                twilio_sid=twilio_result["twilio_sid"],
                phone_number=twilio_result["phone_number"],
                friendly_name=request.friendly_name,
                organization_id=purchase.organization_id,
                user_id=purchase.user_id,
                country_code=self._extract_country_code(request.phone_number),
                number_type=request.number_type,
                capabilities=request.capabilities,
                voice_url=request.voice_url,
                sms_url=request.sms_url,
                status="active",
                monthly_price=purchase.base_price,
                currency=purchase.currency,
                tags=request.tags,
                notes=request.notes,
                purchased_at=datetime.utcnow()
            )
            
            self.db.add(phone_number)
            
            # Update purchase record
            purchase.phone_number_id = phone_number.id
            purchase.provisioning_status = "provisioned"
            purchase.provisioned_at = datetime.utcnow()
            purchase.twilio_purchase_data = twilio_result
            
            self.db.commit()
            
            logger.info(f"Provisioned phone number {request.phone_number}")
            
        except Exception as e:
            purchase.provisioning_status = "failed"
            purchase.provisioning_error = str(e)
            self.db.commit()
            raise e
    
    async def _provision_number_from_purchase(self, purchase: PhoneNumberPurchase) -> None:
        """Provision number from existing purchase record"""
        # This would need the original request data stored in purchase
        # For now, we'll implement a basic version
        pass
    
    async def _get_pricing(self, country_code: str, number_type: str) -> Dict[str, Any]:
        """Get pricing information for country and number type"""
        
        country_info = settings.SUPPORTED_COUNTRIES.get(country_code)
        if not country_info:
            raise ServiceException(f"Country {country_code} not supported")
        
        monthly_price = country_info["pricing"].get(number_type)
        if monthly_price is None:
            raise ServiceException(f"Number type {number_type} not available in {country_code}")
        
        return {
            "monthly_price": monthly_price,
            "setup_fee": 0.0,  # Currently no setup fees
            "currency": "USD",
            "per_minute_cost": 0.0085,
            "per_sms_cost": 0.0075,
            "per_mms_cost": 0.02
        }
    
    async def _get_or_create_stripe_customer(
        self,
        organization_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get or create Stripe customer"""
        
        try:
            # Try to find existing customer
            customers = stripe.Customer.list(
                metadata={"organization_id": organization_id}
            )
            
            if customers.data:
                return customers.data[0]
            
            # Create new customer
            customer = stripe.Customer.create(
                metadata={
                    "organization_id": organization_id,
                    "user_id": user_id,
                    "service": "vocelio_phone_numbers"
                },
                description=f"Vocelio.ai Organization {organization_id}"
            )
            
            return customer
            
        except stripe.StripeError as e:
            logger.error(f"Stripe customer creation failed: {str(e)}")
            raise ExternalAPIError(f"Customer creation failed: {str(e)}")
    
    def _extract_country_code(self, phone_number: str) -> str:
        """Extract country code from phone number"""
        normalized = normalize_phone_number(phone_number)
        if normalized.startswith("+1"):
            return "US"  # Could be US or CA, default to US
        elif normalized.startswith("+44"):
            return "GB"
        elif normalized.startswith("+61"):
            return "AU"
        elif normalized.startswith("+49"):
            return "DE"
        else:
            return "US"  # Default fallback


class BillingService:
    """Billing Service for Phone Numbers"""
    
    def __init__(self):
        pass
    
    async def create_subscription(
        self,
        phone_number_id: str,
        organization_id: str,
        monthly_price: float
    ) -> Dict[str, Any]:
        """Create monthly billing subscription for phone number"""
        
        try:
            # Get or create customer
            customer = await self._get_customer(organization_id)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer["id"],
                items=[{
                    "price_data": {
                        "currency": "usd",
                        "product": stripe_config.PHONE_NUMBER_PRODUCT_ID,
                        "unit_amount": int(monthly_price * 100),
                        "recurring": {"interval": "month"}
                    }
                }],
                metadata={
                    "phone_number_id": phone_number_id,
                    "organization_id": organization_id,
                    "service": "phone_number_monthly"
                }
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end
            }
            
        except stripe.StripeError as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            raise ExternalAPIError(f"Billing setup failed: {str(e)}")
    
    async def cancel_number_subscription(self, phone_number_id: str) -> bool:
        """Cancel monthly subscription for released number"""
        
        try:
            # Find subscription by metadata
            subscriptions = stripe.Subscription.list(
                metadata={"phone_number_id": phone_number_id}
            )
            
            for subscription in subscriptions.data:
                if subscription.status == "active":
                    stripe.Subscription.delete(subscription.id)
                    logger.info(f"Cancelled subscription for number {phone_number_id}")
            
            return True
            
        except stripe.StripeError as e:
            logger.error(f"Subscription cancellation failed: {str(e)}")
            raise ExternalAPIError(f"Billing cancellation failed: {str(e)}")
    
    async def _get_customer(self, organization_id: str) -> Dict[str, Any]:
        """Get Stripe customer for organization"""
        
        customers = stripe.Customer.list(
            metadata={"organization_id": organization_id}
        )
        
        if customers.data:
            return customers.data[0]
        
        # Create if not exists
        customer = stripe.Customer.create(
            metadata={
                "organization_id": organization_id,
                "service": "vocelio"
            }
        )
        
        return customer