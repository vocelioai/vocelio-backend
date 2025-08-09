# apps/phone-numbers/src/services/twilio_service.py
from typing import List, Dict, Any, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging
from datetime import datetime

from core.config import settings, twilio_config
from schemas.phone_number import AvailableNumber, NumberSearchRequest
from shared.exceptions.external import ExternalAPIError
from shared.utils.phone_utils import normalize_phone_number

logger = logging.getLogger(__name__)


class TwilioService:
    """Twilio API Integration Service"""
    
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.account_sid = settings.TWILIO_ACCOUNT_SID
    
    async def search_available_numbers(
        self,
        search_request: NumberSearchRequest
    ) -> List[AvailableNumber]:
        """Search for available phone numbers"""
        
        try:
            # Determine the Twilio number type
            twilio_type = twilio_config.NUMBER_TYPES[search_request.number_type]["twilio_type"]
            
            # Build search parameters
            search_params = {
                "limit": search_request.limit,
                "country": search_request.country_code
            }
            
            # Add type-specific parameters
            if search_request.number_type == "local":
                if search_request.area_code:
                    search_params["area_code"] = search_request.area_code
                if search_request.locality:
                    search_params["in_locality"] = search_request.locality
                if search_request.region:
                    search_params["in_region"] = search_request.region
                if search_request.postal_code:
                    search_params["in_postal_code"] = search_request.postal_code
                if search_request.contains:
                    search_params["contains"] = search_request.contains
                if search_request.near_lat_long:
                    search_params["near_lat_long"] = search_request.near_lat_long
            
            # Search based on number type
            if search_request.number_type == "local":
                available_numbers = self.client.available_phone_numbers(
                    search_request.country_code
                ).local.list(**search_params)
            
            elif search_request.number_type == "toll_free":
                available_numbers = self.client.available_phone_numbers(
                    search_request.country_code
                ).toll_free.list(**search_params)
            
            elif search_request.number_type == "mobile":
                available_numbers = self.client.available_phone_numbers(
                    search_request.country_code
                ).mobile.list(**search_params)
            
            else:
                raise ValueError(f"Unsupported number type: {search_request.number_type}")
            
            # Convert to our format
            results = []
            country_pricing = settings.SUPPORTED_COUNTRIES.get(search_request.country_code, {})
            monthly_price = country_pricing.get("pricing", {}).get(search_request.number_type, 0)
            
            for number in available_numbers:
                # Get capabilities
                capabilities = []
                if hasattr(number, 'capabilities'):
                    if number.capabilities.get('voice'):
                        capabilities.append("voice")
                    if number.capabilities.get('SMS'):
                        capabilities.append("sms")
                    if number.capabilities.get('MMS'):
                        capabilities.append("mms")
                else:
                    # Default capabilities based on type
                    capabilities = ["voice"]
                    if search_request.number_type != "toll_free":
                        capabilities.append("sms")
                    if search_request.number_type == "mobile":
                        capabilities.append("mms")
                
                results.append(AvailableNumber(
                    phone_number=number.phone_number,
                    friendly_name=self._format_friendly_name(number.phone_number),
                    locality=getattr(number, 'locality', None),
                    region=getattr(number, 'region', None),
                    country=search_request.country_code,
                    capabilities=capabilities,
                    monthly_price=monthly_price,
                    latitude=getattr(number, 'latitude', None),
                    longitude=getattr(number, 'longitude', None),
                    postal_code=getattr(number, 'postal_code', None)
                ))
            
            logger.info(f"Found {len(results)} available numbers for {search_request.country_code}")
            return results
            
        except TwilioException as e:
            logger.error(f"Twilio API error during search: {str(e)}")
            raise ExternalAPIError(f"Twilio search failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during number search: {str(e)}")
            raise ServiceException(f"Number search failed: {str(e)}")
    
    async def purchase_number(
        self,
        phone_number: str,
        voice_url: Optional[str] = None,
        sms_url: Optional[str] = None,
        status_callback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Purchase a phone number from Twilio"""
        
        try:
            # Normalize phone number
            normalized_number = normalize_phone_number(phone_number)
            
            # Purchase parameters
            purchase_params = {
                "phone_number": normalized_number,
                "voice_url": voice_url or settings.DEFAULT_VOICE_URL,
                "voice_method": "POST",
                "sms_url": sms_url or settings.DEFAULT_SMS_URL,
                "sms_method": "POST"
            }
            
            if status_callback:
                purchase_params["status_callback"] = status_callback
                purchase_params["status_callback_method"] = "POST"
            
            # Purchase the number
            incoming_number = self.client.incoming_phone_numbers.create(**purchase_params)
            
            # Get detailed information about the purchased number
            number_details = self.client.incoming_phone_numbers(incoming_number.sid).fetch()
            
            result = {
                "twilio_sid": incoming_number.sid,
                "phone_number": incoming_number.phone_number,
                "friendly_name": incoming_number.friendly_name,
                "account_sid": incoming_number.account_sid,
                "capabilities": {
                    "voice": number_details.capabilities.get('voice', False),
                    "sms": number_details.capabilities.get('SMS', False),
                    "mms": number_details.capabilities.get('MMS', False)
                },
                "status": "active",
                "date_created": incoming_number.date_created,
                "voice_url": incoming_number.voice_url,
                "sms_url": incoming_number.sms_url
            }
            
            logger.info(f"Successfully purchased number {phone_number} with SID {incoming_number.sid}")
            return result
            
        except TwilioException as e:
            logger.error(f"Twilio purchase error for {phone_number}: {str(e)}")
            raise ExternalAPIError(f"Failed to purchase number: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error purchasing {phone_number}: {str(e)}")
            raise ServiceException(f"Number purchase failed: {str(e)}")
    
    async def update_number_configuration(
        self,
        twilio_sid: str,
        voice_url: Optional[str] = None,
        sms_url: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update Twilio number configuration"""
        
        try:
            update_params = {}
            
            if voice_url is not None:
                update_params["voice_url"] = voice_url
                update_params["voice_method"] = "POST"
            
            if sms_url is not None:
                update_params["sms_url"] = sms_url
                update_params["sms_method"] = "POST"
            
            # Update the number
            number = self.client.incoming_phone_numbers(twilio_sid).update(**update_params)
            
            logger.info(f"Updated Twilio configuration for {twilio_sid}")
            return {
                "twilio_sid": number.sid,
                "voice_url": number.voice_url,
                "sms_url": number.sms_url,
                "status": "updated"
            }
            
        except TwilioException as e:
            logger.error(f"Twilio update error for {twilio_sid}: {str(e)}")
            raise ExternalAPIError(f"Failed to update number configuration: {str(e)}")
    
    async def release_number(self, twilio_sid: str) -> bool:
        """Release a phone number from Twilio"""
        
        try:
            self.client.incoming_phone_numbers(twilio_sid).delete()
            logger.info(f"Released Twilio number {twilio_sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Twilio release error for {twilio_sid}: {str(e)}")
            raise ExternalAPIError(f"Failed to release number: {str(e)}")
    
    async def get_number_details(self, twilio_sid: str) -> Dict[str, Any]:
        """Get detailed information about a Twilio number"""
        
        try:
            number = self.client.incoming_phone_numbers(twilio_sid).fetch()
            
            return {
                "sid": number.sid,
                "phone_number": number.phone_number,
                "friendly_name": number.friendly_name,
                "capabilities": number.capabilities,
                "voice_url": number.voice_url,
                "sms_url": number.sms_url,
                "status": "active",
                "date_created": number.date_created,
                "date_updated": number.date_updated
            }
            
        except TwilioException as e:
            logger.error(f"Error fetching Twilio number details {twilio_sid}: {str(e)}")
            raise ExternalAPIError(f"Failed to fetch number details: {str(e)}")
    
    async def validate_webhook_signature(
        self,
        url: str,
        post_vars: Dict[str, Any],
        signature: str
    ) -> bool:
        """Validate Twilio webhook signature"""
        
        try:
            from twilio.request_validator import RequestValidator
            
            validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
            return validator.validate(url, post_vars, signature)
            
        except Exception as e:
            logger.error(f"Webhook signature validation error: {str(e)}")
            return False
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get Twilio account balance"""
        
        try:
            balance = self.client.balance.fetch()
            
            return {
                "balance": float(balance.balance),
                "currency": balance.currency,
                "account_sid": balance.account_sid
            }
            
        except TwilioException as e:
            logger.error(f"Error fetching account balance: {str(e)}")
            raise ExternalAPIError(f"Failed to fetch account balance: {str(e)}")
    
    def _format_friendly_name(self, phone_number: str) -> str:
        """Format phone number as friendly name"""
        try:
            # Remove + and format for US/CA numbers
            clean = phone_number.replace("+", "")
            if len(clean) == 11 and clean.startswith("1"):
                area = clean[1:4]
                exchange = clean[4:7]
                number = clean[7:11]
                return f"+1 ({area}) {exchange}-{number}"
            else:
                return phone_number
        except:
            return phone_number