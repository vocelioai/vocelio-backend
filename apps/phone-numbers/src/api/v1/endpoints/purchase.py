# apps/phone-numbers/src/api/v1/endpoints/purchase.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from shared.database.client import get_db
from shared.auth.dependencies import get_current_user, get_organization_id
from schemas.phone_number import (
    NumberSearchRequest, NumberSearchResponse, AvailableNumber,
    NumberPurchaseRequest, NumberPurchaseResponse, CountryInfo, PricingInfo
)
from services.twilio_service import TwilioService
from services.purchase_service import PurchaseService
from core.config import settings
from shared.exceptions.service import ServiceException
from shared.exceptions.external import ExternalAPIError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/countries",
    response_model=List[CountryInfo],
    summary="Get Supported Countries",
    description="Get list of all supported countries with pricing information"
)
async def get_supported_countries():
    """
    Get all supported countries with pricing and feature information.
    
    Returns country codes, names, flags, pricing by number type, and available features.
    """
    try:
        countries = []
        for code, info in settings.SUPPORTED_COUNTRIES.items():
            countries.append(CountryInfo(
                code=code,
                name=info["name"],
                flag=info["flag"],
                pricing=info["pricing"],
                features=info["features"],
                area_codes_supported=info.get("area_codes", False)
            ))
        
        return countries
        
    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch countries")


@router.post(
    "/search",
    response_model=NumberSearchResponse,
    summary="Search Available Numbers",
    description="Search for available phone numbers with filters"
)
async def search_available_numbers(
    search_request: NumberSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search for available phone numbers based on criteria.
    
    - **country_code**: Two-letter country code (e.g., "US", "CA")
    - **number_type**: Type of number (local, toll_free, mobile)
    - **capabilities**: Required capabilities (voice, sms, mms)
    - **area_code**: Area code for local numbers (US/CA only)
    - **locality**: City name
    - **region**: State/province
    - **contains**: Pattern that number should contain
    - **limit**: Maximum number of results (max 50)
    """
    try:
        # Validate country support
        if search_request.country_code not in settings.SUPPORTED_COUNTRIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Country {search_request.country_code} is not supported"
            )
        
        # Validate number type for country
        country_info = settings.SUPPORTED_COUNTRIES[search_request.country_code]
        if search_request.number_type not in country_info["pricing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Number type {search_request.number_type} not available in {search_request.country_code}"
            )
        
        twilio_service = TwilioService()
        available_numbers = await twilio_service.search_available_numbers(search_request)
        
        # Get pricing info
        pricing_info = {
            "monthly_price": country_info["pricing"][search_request.number_type],
            "setup_fee": 0.0,
            "currency": "USD",
            "per_minute_cost": 0.0085,
            "per_sms_cost": 0.0075,
            "per_mms_cost": 0.02
        }
        
        return NumberSearchResponse(
            available_numbers=available_numbers,
            total_found=len(available_numbers),
            search_params=search_request,
            pricing_info=pricing_info
        )
        
    except HTTPException:
        raise
    except ExternalAPIError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in number search: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed")


@router.post(
    "/purchase",
    response_model=NumberPurchaseResponse,
    summary="Purchase Phone Number",
    description="Purchase a phone number with Stripe payment"
)
async def purchase_phone_number(
    purchase_request: NumberPurchaseRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Purchase a phone number with immediate Stripe payment processing.
    
    - **phone_number**: The phone number to purchase (e.g., "+15551234567")
    - **friendly_name**: Human-readable name for the number
    - **number_type**: Type of number (local, toll_free, mobile)
    - **capabilities**: Required capabilities (voice, sms, mms)
    - **payment_method_id**: Stripe payment method ID
    - **voice_url**: Optional webhook URL for voice calls
    - **sms_url**: Optional webhook URL for SMS messages
    """
    try:
        purchase_service = PurchaseService(db)
        
        result = await purchase_service.initiate_purchase(
            organization_id=organization_id,
            user_id=current_user["id"],
            purchase_request=purchase_request
        )
        
        return result
        
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Purchase failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Purchase failed")


@router.get(
    "/purchase/{purchase_id}/status",
    summary="Get Purchase Status",
    description="Get the current status of a phone number purchase"
)
async def get_purchase_status(
    purchase_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Get the current status of a purchase transaction.
    
    - **purchase_id**: Unique identifier of the purchase
    """
    try:
        from models.phone_number import PhoneNumberPurchase
        
        purchase = db.query(PhoneNumberPurchase).filter(
            PhoneNumberPurchase.id == purchase_id,
            PhoneNumberPurchase.organization_id == organization_id
        ).first()
        
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
        
        return {
            "purchase_id": purchase.id,
            "phone_number_id": purchase.phone_number_id,
            "payment_status": purchase.payment_status,
            "provisioning_status": purchase.provisioning_status,
            "total_amount": purchase.total_amount,
            "currency": purchase.currency,
            "created_at": purchase.created_at,
            "payment_completed_at": purchase.payment_completed_at,
            "provisioned_at": purchase.provisioned_at,
            "error": purchase.provisioning_error
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching purchase status: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch status")


@router.post(
    "/webhooks/stripe",
    summary="Stripe Webhook Handler",
    description="Handle Stripe webhook events for payment processing"
)
async def stripe_webhook_handler(
    request: Any = Body(...),
    stripe_signature: str = Depends(lambda req: req.headers.get("stripe-signature")),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events for payment processing.
    
    This endpoint processes payment confirmations, failures, and subscription events.
    """
    try:
        import stripe
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                request, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
        except stripe.SignatureVerificationError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
        
        # Process the event
        purchase_service = PurchaseService(db)
        result = await purchase_service.handle_stripe_webhook(
            event["type"],
            event["data"]
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook processing failed")


@router.get(
    "/pricing/{country_code}/{number_type}",
    response_model=PricingInfo,
    summary="Get Pricing Information",
    description="Get detailed pricing for a specific country and number type"
)
async def get_pricing_info(
    country_code: str,
    number_type: str
):
    """
    Get detailed pricing information for a specific country and number type.
    
    - **country_code**: Two-letter country code
    - **number_type**: Type of number (local, toll_free, mobile)
    """
    try:
        if country_code not in settings.SUPPORTED_COUNTRIES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Country {country_code} not supported"
            )
        
        country_info = settings.SUPPORTED_COUNTRIES[country_code]
        
        if number_type not in country_info["pricing"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Number type {number_type} not available in {country_code}"
            )
        
        return PricingInfo(
            country_code=country_code,
            number_type=number_type,
            monthly_price=country_info["pricing"][number_type],
            setup_fee=0.0,
            per_minute_cost=0.0085,
            per_sms_cost=0.0075,
            per_mms_cost=0.02,
            currency="USD"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pricing: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch pricing")


@router.post(
    "/validate",
    summary="Validate Phone Number",
    description="Validate a phone number format and availability"
)
async def validate_phone_number(
    phone_number: str = Body(..., embed=True),
    country_code: str = Query(..., description="Expected country code")
):
    """
    Validate a phone number format and check basic availability.
    
    - **phone_number**: Phone number to validate
    - **country_code**: Expected country code for validation
    """
    try:
        from shared.utils.phone_utils import validate_phone_number, normalize_phone_number
        
        # Validate format
        is_valid = validate_phone_number(phone_number, country_code)
        
        if not is_valid:
            return {
                "valid": False,
                "error": "Invalid phone number format",
                "suggestions": [
                    "Ensure the number includes country code",
                    "Check for correct number of digits",
                    "Remove any special characters except + and -"
                ]
            }
        
        normalized = normalize_phone_number(phone_number)
        
        return {
            "valid": True,
            "normalized": normalized,
            "formatted": normalized,  # You could add a format function here
            "country_code": country_code,
            "number_type": "unknown",  # Could detect this from number pattern
            "message": "Phone number format is valid"
        }
        
    except Exception as e:
        logger.error(f"Phone number validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Validation failed")


@router.get(
    "/inventory/stats",
    summary="Get Inventory Statistics",
    description="Get statistics about available numbers in different countries"
)
async def get_inventory_stats():
    """
    Get statistics about available phone number inventory.
    
    Provides counts and availability information for different countries and number types.
    """
    try:
        twilio_service = TwilioService()
        
        # Sample availability check for major countries
        inventory_stats = []
        
        for country_code, country_info in settings.SUPPORTED_COUNTRIES.items():
            country_stats = {
                "country_code": country_code,
                "country_name": country_info["name"],
                "flag": country_info["flag"],
                "number_types": {}
            }
            
            # Check availability for each number type
            for number_type, price in country_info["pricing"].items():
                try:
                    # Quick search to check availability
                    search_request = NumberSearchRequest(
                        country_code=country_code,
                        number_type=number_type,
                        limit=5
                    )
                    
                    available = await twilio_service.search_available_numbers(search_request)
                    
                    country_stats["number_types"][number_type] = {
                        "available": len(available) > 0,
                        "sample_count": len(available),
                        "monthly_price": price,
                        "features": country_info["features"]
                    }
                    
                except Exception as e:
                    # If search fails, mark as unavailable
                    country_stats["number_types"][number_type] = {
                        "available": False,
                        "sample_count": 0,
                        "monthly_price": price,
                        "features": country_info["features"],
                        "error": str(e)
                    }
            
            inventory_stats.append(country_stats)
        
        return {
            "inventory": inventory_stats,
            "total_countries": len(settings.SUPPORTED_COUNTRIES),
            "last_updated": "2025-08-04T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching inventory stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch inventory")


@router.post(
    "/quote",
    summary="Get Purchase Quote",
    description="Get a detailed quote for purchasing specific numbers"
)
async def get_purchase_quote(
    phone_numbers: List[str] = Body(..., description="List of phone numbers to quote"),
    country_code: str = Body(..., description="Country code"),
    number_type: str = Body(..., description="Number type"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Get a detailed purchase quote for multiple phone numbers.
    
    - **phone_numbers**: List of phone numbers to purchase
    - **country_code**: Country code for the numbers
    - **number_type**: Type of numbers (local, toll_free, mobile)
    """
    try:
        if len(phone_numbers) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot quote more than 100 numbers at once"
            )
        
        # Validate country and number type
        if country_code not in settings.SUPPORTED_COUNTRIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Country {country_code} not supported"
            )
        
        country_info = settings.SUPPORTED_COUNTRIES[country_code]
        if number_type not in country_info["pricing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Number type {number_type} not available in {country_code}"
            )
        
        # Calculate pricing
        monthly_price = country_info["pricing"][number_type]
        setup_fee = 0.0
        
        # Check if numbers are already owned
        from models.phone_number import PhoneNumber
        existing_numbers = db.query(PhoneNumber.phone_number).filter(
            PhoneNumber.phone_number.in_(phone_numbers)
        ).all()
        
        existing_set = {num[0] for num in existing_numbers}
        available_numbers = [num for num in phone_numbers if num not in existing_set]
        unavailable_numbers = [num for num in phone_numbers if num in existing_set]
        
        # Calculate totals
        count = len(available_numbers)
        subtotal = count * monthly_price
        setup_total = count * setup_fee
        total = subtotal + setup_total
        
        return {
            "quote_id": f"quote_{organization_id}_{int(datetime.utcnow().timestamp())}",
            "numbers": {
                "requested": phone_numbers,
                "available": available_numbers,
                "unavailable": unavailable_numbers,
                "available_count": count,
                "unavailable_count": len(unavailable_numbers)
            },
            "pricing": {
                "monthly_price_per_number": monthly_price,
                "setup_fee_per_number": setup_fee,
                "monthly_subtotal": subtotal,
                "setup_total": setup_total,
                "total_first_month": total,
                "total_monthly_recurring": subtotal,
                "currency": "USD"
            },
            "estimated_costs": {
                "first_month": total,
                "monthly_recurring": subtotal,
                "annual_estimate": subtotal * 12,
                "per_minute": 0.0085,
                "per_sms": 0.0075,
                "per_mms": 0.02
            },
            "next_steps": [
                "Review the quote details",
                "Ensure payment method is set up",
                "Proceed with bulk purchase",
                "Numbers will be provisioned within 60 seconds"
            ],
            "quote_expires_at": (datetime.utcnow().timestamp() + 3600),  # 1 hour
            "country_info": country_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quote generation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Quote generation failed")