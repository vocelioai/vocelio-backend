# apps/phone-numbers/src/services/verification_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import random
import string

from models.phone_number import PhoneNumber, PhoneNumberVerification
from schemas.phone_number import VerificationResponse
from services.twilio_service import TwilioService
from shared.exceptions.service import ServiceException, NotFoundError
from shared.utils.email_utils import send_verification_email

logger = logging.getLogger(__name__)


class VerificationService:
    """Phone Number Verification Service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.twilio = TwilioService()
    
    async def start_verification(
        self,
        phone_number_id: str,
        organization_id: str,
        user_id: str,
        verification_type: str,
        verification_method: str
    ) -> VerificationResponse:
        """Start verification process for a phone number"""
        
        try:
            # Get phone number
            phone_number = self.db.query(PhoneNumber).filter(
                PhoneNumber.id == phone_number_id,
                PhoneNumber.organization_id == organization_id
            ).first()
            
            if not phone_number:
                raise NotFoundError(f"Phone number {phone_number_id} not found")
            
            # Generate verification code
            verification_code = self._generate_verification_code()
            expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10-minute expiry
            
            # Create verification record
            verification = PhoneNumberVerification(
                phone_number_id=phone_number_id,
                verification_type=verification_type,
                verification_method=verification_method,
                verification_code=verification_code,
                status="pending",
                requested_by=user_id,
                expires_at=expires_at
            )
            
            self.db.add(verification)
            self.db.commit()
            self.db.refresh(verification)
            
            # Send verification based on method
            if verification_method == "sms":
                await self._send_sms_verification(phone_number.phone_number, verification_code)
                next_step = "Enter the 6-digit code sent to your phone via SMS"
            
            elif verification_method == "voice":
                await self._send_voice_verification(phone_number.phone_number, verification_code)
                next_step = "Answer the call and listen for the 6-digit verification code"
            
            elif verification_method == "email":
                # Would need user email from user service
                await self._send_email_verification(user_id, verification_code)
                next_step = "Check your email for the 6-digit verification code"
            
            else:
                raise ServiceException(f"Unsupported verification method: {verification_method}")
            
            logger.info(f"Started {verification_type} verification for {phone_number_id}")
            
            return VerificationResponse(
                verification_id=verification.id,
                status="pending",
                verification_code=None,  # Never return the actual code
                expires_at=expires_at,
                next_step=next_step
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Verification start failed: {str(e)}")
            raise ServiceException(f"Failed to start verification: {str(e)}")
    
    async def confirm_verification(
        self,
        verification_id: str,
        verification_code: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Confirm verification with provided code"""
        
        try:
            # Get verification record
            verification = self.db.query(PhoneNumberVerification).join(PhoneNumber).filter(
                PhoneNumberVerification.id == verification_id,
                PhoneNumber.organization_id == organization_id
            ).first()
            
            if not verification:
                raise NotFoundError(f"Verification {verification_id} not found")
            
            # Check if verification has expired
            if verification.expires_at and datetime.utcnow() > verification.expires_at:
                verification.status = "expired"
                self.db.commit()
                raise ServiceException("Verification code has expired")
            
            # Check if already verified
            if verification.status == "verified":
                return {
                    "status": "already_verified",
                    "message": "This verification was already completed",
                    "verified_at": verification.verified_at
                }
            
            # Validate code
            if verification.verification_code != verification_code:
                # Could implement rate limiting for failed attempts here
                raise ServiceException("Invalid verification code")
            
            # Mark as verified
            verification.status = "verified"
            verification.verified_at = datetime.utcnow()
            verification.verification_data = {
                "confirmed_at": datetime.utcnow().isoformat(),
                "method_used": verification.verification_method,
                "verification_type": verification.verification_type
            }
            
            self.db.commit()
            
            logger.info(f"Verification {verification_id} completed successfully")
            
            return {
                "status": "verified",
                "message": "Phone number verified successfully",
                "verified_at": verification.verified_at,
                "verification_type": verification.verification_type
            }
            
        except Exception as e:
            if "Invalid verification code" in str(e) or "expired" in str(e):
                raise e
            
            self.db.rollback()
            logger.error(f"Verification confirmation failed: {str(e)}")
            raise ServiceException(f"Failed to confirm verification: {str(e)}")
    
    async def get_verification_status(
        self,
        verification_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get current verification status"""
        
        try:
            verification = self.db.query(PhoneNumberVerification).join(PhoneNumber).filter(
                PhoneNumberVerification.id == verification_id,
                PhoneNumber.organization_id == organization_id
            ).first()
            
            if not verification:
                raise NotFoundError(f"Verification {verification_id} not found")
            
            return {
                "verification_id": verification.id,
                "phone_number_id": verification.phone_number_id,
                "phone_number": verification.phone_number.phone_number,
                "verification_type": verification.verification_type,
                "verification_method": verification.verification_method,
                "status": verification.status,
                "created_at": verification.created_at,
                "expires_at": verification.expires_at,
                "verified_at": verification.verified_at,
                "error_message": verification.error_message
            }
            
        except Exception as e:
            logger.error(f"Error fetching verification status: {str(e)}")
            raise ServiceException(f"Failed to fetch verification status: {str(e)}")
    
    async def _send_sms_verification(self, phone_number: str, code: str) -> None:
        """Send SMS verification code"""
        
        try:
            message = f"Your Vocelio.ai verification code is: {code}. This code expires in 10 minutes."
            
            # Use Twilio to send SMS
            # Note: This would need a verified Twilio number to send from
            # For now, we'll log it (in production, implement actual SMS sending)
            logger.info(f"SMS verification code {code} would be sent to {phone_number}")
            
            # In production:
            # self.twilio.client.messages.create(
            #     body=message,
            #     from_=settings.TWILIO_VERIFICATION_NUMBER,
            #     to=phone_number
            # )
            
        except Exception as e:
            logger.error(f"Failed to send SMS verification: {str(e)}")
            raise ServiceException("Failed to send SMS verification")
    
    async def _send_voice_verification(self, phone_number: str, code: str) -> None:
        """Send voice verification code"""
        
        try:
            # Format code for voice (e.g., "1-2-3-4-5-6")
            formatted_code = "-".join(code)
            message = f"Your Vocelio verification code is {formatted_code}. I repeat, {formatted_code}."
            
            logger.info(f"Voice verification code {code} would be called to {phone_number}")
            
            # In production:
            # call = self.twilio.client.calls.create(
            #     twiml=f'<Response><Say>{message}</Say></Response>',
            #     from_=settings.TWILIO_VERIFICATION_NUMBER,
            #     to=phone_number
            # )
            
        except Exception as e:
            logger.error(f"Failed to send voice verification: {str(e)}")
            raise ServiceException("Failed to send voice verification")
    
    async def _send_email_verification(self, user_id: str, code: str) -> None:
        """Send email verification code"""
        
        try:
            # Would need to get user email from user service
            logger.info(f"Email verification code {code} would be sent to user {user_id}")
            
            # In production:
            # await send_verification_email(user_email, code)
            
        except Exception as e:
            logger.error(f"Failed to send email verification: {str(e)}")
            raise ServiceException("Failed to send email verification")
    
    def _generate_verification_code(self, length: int = 6) -> str:
        """Generate random verification code"""
        return ''.join(random.choices(string.digits, k=length))