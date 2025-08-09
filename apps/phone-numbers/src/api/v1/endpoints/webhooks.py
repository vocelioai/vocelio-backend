# apps/phone-numbers/src/api/v1/endpoints/webhooks.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Header
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from shared.database.client import get_db
from services.twilio_service import TwilioService
from services.number_service import NumberService
from schemas.phone_number import VoiceWebhook, SmsWebhook
from models.phone_number import PhoneNumber
from shared.exceptions.service import ServiceException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/twilio/voice",
    summary="Twilio Voice Webhook",
    description="Handle incoming voice call webhooks from Twilio"
)
async def twilio_voice_webhook(
    request: Request,
    CallSid: str = Form(...),
    AccountSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...),
    Direction: str = Form(...),
    ForwardedFrom: Optional[str] = Form(None),
    CallerName: Optional[str] = Form(None),
    Duration: Optional[str] = Form(None),
    RecordingUrl: Optional[str] = Form(None),
    x_twilio_signature: str = Header(..., alias="X-Twilio-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Twilio voice webhooks for call events.
    
    Processes call status updates, recordings, and usage tracking.
    """
    try:
        twilio_service = TwilioService()
        
        # Verify webhook signature
        url = str(request.url)
        form_data = await request.form()
        post_vars = dict(form_data)
        
        is_valid = await twilio_service.validate_webhook_signature(
            url, post_vars, x_twilio_signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook signature"
            )
        
        # Find the phone number
        phone_number = db.query(PhoneNumber).filter(
            PhoneNumber.phone_number == To
        ).first()
        
        if not phone_number:
            logger.warning(f"Received webhook for unknown number: {To}")
            return {"message": "Number not found, webhook ignored"}
        
        # Process the webhook based on call status
        if CallStatus == "completed" and Duration:
            # Update usage statistics
            duration_minutes = float(Duration) / 60.0
            usage_data = {
                "calls": 1,
                "minutes": duration_minutes
            }
            
            number_service = NumberService(db)
            await number_service.update_usage(phone_number.id, usage_data)
            
            logger.info(f"Updated usage for {To}: {duration_minutes} minutes")
        
        # Log the call event
        logger.info(f"Voice webhook: {CallSid} - {CallStatus} - {From} -> {To}")
        
        # Return TwiML response for call handling
        from twilio.twiml import VoiceResponse
        
        response = VoiceResponse()
        
        if CallStatus == "ringing":
            # Handle incoming call - could route to AI agent
            response.say("Thank you for calling. Please hold while we connect you to our AI assistant.")
            response.redirect(url=f"https://api.vocelio.ai/voice/handle/{phone_number.id}")
        
        return str(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice webhook error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook processing failed")


@router.post(
    "/twilio/sms",
    summary="Twilio SMS Webhook", 
    description="Handle incoming SMS webhooks from Twilio"
)
async def twilio_sms_webhook(
    request: Request,
    MessageSid: str = Form(...),
    AccountSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: Optional[str] = Form(None),
    NumMedia: Optional[str] = Form("0"),
    MessageStatus: str = Form(...),
    x_twilio_signature: str = Header(..., alias="X-Twilio-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Twilio SMS webhooks for message events.
    
    Processes incoming/outgoing SMS and MMS messages and updates usage statistics.
    """
    try:
        twilio_service = TwilioService()
        
        # Verify webhook signature
        url = str(request.url)
        form_data = await request.form()
        post_vars = dict(form_data)
        
        is_valid = await twilio_service.validate_webhook_signature(
            url, post_vars, x_twilio_signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook signature"
            )
        
        # Find the phone number
        phone_number = db.query(PhoneNumber).filter(
            PhoneNumber.phone_number == To
        ).first()
        
        if not phone_number:
            logger.warning(f"Received SMS webhook for unknown number: {To}")
            return {"message": "Number not found, webhook ignored"}
        
        # Update usage statistics
        is_mms = int(NumMedia or "0") > 0
        usage_data = {
            "sms": 0 if is_mms else 1,
            "mms": 1 if is_mms else 0
        }
        
        number_service = NumberService(db)
        await number_service.update_usage(phone_number.id, usage_data)
        
        logger.info(f"SMS webhook: {MessageSid} - {MessageStatus} - {From} -> {To}")
        
        # Return TwiML response for SMS handling
        from twilio.twiml import MessagingResponse
        
        response = MessagingResponse()
        
        # Auto-reply with AI or forward to appropriate service
        if Body and "stop" not in Body.lower():
            response.message("Thank you for your message. Our AI will process this and respond shortly.")
        
        return str(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SMS webhook error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SMS webhook processing failed")


@router.post(
    "/twilio/status",
    summary="Twilio Status Webhook",
    description="Handle call and message status updates from Twilio"
)
async def twilio_status_webhook(
    request: Request,
    CallSid: Optional[str] = Form(None),
    MessageSid: Optional[str] = Form(None),
    AccountSid: str = Form(...),
    To: str = Form(...),
    CallStatus: Optional[str] = Form(None),
    MessageStatus: Optional[str] = Form(None),
    ErrorCode: Optional[str] = Form(None),
    ErrorMessage: Optional[str] = Form(None),
    x_twilio_signature: str = Header(..., alias="X-Twilio-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Twilio status callback webhooks.
    
    Processes status updates for calls and messages, including error conditions.
    """
    try:
        twilio_service = TwilioService()
        
        # Verify webhook signature
        url = str(request.url)
        form_data = await request.form()
        post_vars = dict(form_data)
        
        is_valid = await twilio_service.validate_webhook_signature(
            url, post_vars, x_twilio_signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook signature"
            )
        
        # Log status update
        if CallSid and CallStatus:
            logger.info(f"Call status update: {CallSid} - {CallStatus}")
            if ErrorCode:
                logger.warning(f"Call error {ErrorCode}: {ErrorMessage}")
        
        if MessageSid and MessageStatus:
            logger.info(f"Message status update: {MessageSid} - {MessageStatus}")
            if ErrorCode:
                logger.warning(f"Message error {ErrorCode}: {ErrorMessage}")
        
        # Could implement detailed status tracking here
        # For now, just acknowledge receipt
        
        return {"message": "Status update processed"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status webhook error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Status webhook processing failed")


# apps/phone-numbers/src/api/v1/endpoints/verification.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from shared.database.client import get_db
from shared.auth.dependencies import get_current_user, get_organization_id
from schemas.phone_number import VerificationRequest, VerificationResponse
from services.verification_service import VerificationService
from shared.exceptions.service import ServiceException, NotFoundError

router = APIRouter()


@router.post(
    "/verify",
    response_model=VerificationResponse,
    summary="Start Number Verification",
    description="Initiate verification process for a phone number"
)
async def start_verification(
    verification_request: VerificationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Start verification process for a phone number.
    
    - **phone_number_id**: ID of the phone number to verify
    - **verification_type**: Type of verification (ownership, compliance, carrier)
    - **verification_method**: Method to use (sms, voice, email)
    """
    try:
        verification_service = VerificationService(db)
        
        result = await verification_service.start_verification(
            phone_number_id=verification_request.phone_number_id,
            organization_id=organization_id,
            user_id=current_user["id"],
            verification_type=verification_request.verification_type,
            verification_method=verification_request.verification_method
        )
        
        return result
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/verify/{verification_id}/status",
    summary="Get Verification Status",
    description="Get the current status of a verification process"
)
async def get_verification_status(
    verification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Get the current status of a verification process.
    
    - **verification_id**: ID of the verification process
    """
    try:
        verification_service = VerificationService(db)
        
        result = await verification_service.get_verification_status(
            verification_id=verification_id,
            organization_id=organization_id
        )
        
        return result
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))_BAD_REQUEST, detail=str(e))


@router.post(
    "/verify/{verification_id}/confirm",
    summary="Confirm Verification",
    description="Confirm verification with provided code"
)
async def confirm_verification(
    verification_id: str,
    verification_code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Confirm verification with the provided verification code.
    
    - **verification_id**: ID of the verification process
    - **verification_code**: Code received via SMS/voice/email
    """
    try:
        verification_service = VerificationService(db)
        
        result = await verification_service.confirm_verification(
            verification_id=verification_id,
            verification_code=verification_code,
            organization_id=organization_id
        )
        
        return result
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400