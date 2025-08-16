# voice_integration.py - FastAPI Twilio Voice Integration for Call Center
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime, timedelta
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.rest import Client

# Import your existing auth
# from shared.auth.dependencies import get_current_user
# from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Twilio Client
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_API_KEY = os.getenv('TWILIO_API_KEY')
TWILIO_API_SECRET = os.getenv('TWILIO_API_SECRET')
TWILIO_TWIML_APP_SID = os.getenv('TWILIO_TWIML_APP_SID')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None
    logger.warning("⚠️ Twilio not configured - using demo mode")

# Request Models
class VoiceTokenRequest(BaseModel):
    identity: Optional[str] = None

class OutboundCallRequest(BaseModel):
    to: str
    from_: Optional[str] = None

class CallStatusResponse(BaseModel):
    success: bool
    call: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Voice Token Generation Endpoint
@router.post("/token")
async def generate_voice_token(request: VoiceTokenRequest):
    """Generate Twilio Access Token for Voice SDK"""
    
    try:
        identity = request.identity or f'user_{int(datetime.now().timestamp())}'
        
        if not all([TWILIO_ACCOUNT_SID, TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_TWIML_APP_SID]):
            return {
                'success': False,
                'error': 'Missing Twilio voice credentials',
                'required': ['TWILIO_API_KEY', 'TWILIO_API_SECRET', 'TWILIO_TWIML_APP_SID']
            }
        
        # Create access token
        token = AccessToken(
            TWILIO_ACCOUNT_SID,
            TWILIO_API_KEY,
            TWILIO_API_SECRET,
            identity=identity,
            ttl=3600
        )
        
        # Add Voice grant
        voice_grant = VoiceGrant(
            outgoing_application_sid=TWILIO_TWIML_APP_SID,
            incoming_allow=True
        )
        
        token.add_grant(voice_grant)
        
        return {
            'success': True,
            'token': token.to_jwt(),
            'identity': identity,
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Voice token error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                'success': False,
                'error': 'Failed to generate voice token',
                'message': str(e)
            }
        )

@router.post("/make-call")
async def make_outbound_call(request: OutboundCallRequest):
    """Initiate outbound call"""
    
    if not twilio_client:
        return {
            'success': False,
            'error': 'Twilio not configured'
        }
    
    try:
        to_number = request.to
        from_number = request.from_ or TWILIO_PHONE_NUMBER
        
        if not to_number or not from_number:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Missing phone numbers'
                }
            )
        
        # Create call using Twilio client
        call = twilio_client.calls.create(
            to=to_number,
            from_=from_number,
            url=f"https://call.vocelio.ai/api/v1/voice/twiml/outbound",
            method='POST'
        )
        
        return {
            'success': True,
            'call_sid': call.sid,
            'status': call.status,
            'to': to_number,
            'from': from_number
        }
        
    except Exception as e:
        logger.error(f"Make call error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                'success': False,
                'error': 'Failed to make call',
                'message': str(e)
            }
        )

@router.post("/twiml/outbound")
async def handle_outbound_twiml(request: Request):
    """Handle outbound call TwiML"""
    try:
        response = VoiceResponse()
        dial = Dial()
        dial.client('vocelio_dashboard')
        response.append(dial)
        
        return Response(content=str(response), media_type="text/xml")
        
    except Exception as e:
        logger.error(f"Outbound TwiML error: {e}")
        response = VoiceResponse()
        response.say("Call connection failed.")
        return Response(content=str(response), media_type="text/xml")

@router.post("/twiml/incoming")
async def handle_incoming_twiml(request: Request):
    """Handle incoming call TwiML"""
    try:
        form_data = await request.form()
        from_number = form_data.get('From')
        response = VoiceResponse()
        
        response.say("Welcome to Vocelio. Connecting you now.")
        
        dial = Dial()
        dial.client('vocelio_dashboard')
        response.append(dial)
        
        return Response(content=str(response), media_type="text/xml")
        
    except Exception as e:
        logger.error(f"Incoming TwiML error: {e}")
        response = VoiceResponse()
        response.say("Sorry, all agents are busy.")
        return Response(content=str(response), media_type="text/xml")

@router.get("/status/{call_sid}")
async def get_call_status(call_sid: str):
    """Get call status"""
    
    if not twilio_client:
        return {
            'success': False,
            'error': 'Twilio not configured'
        }
    
    try:
        call = twilio_client.calls(call_sid).fetch()
        
        return {
            'success': True,
            'call': {
                'sid': call.sid,
                'status': call.status,
                'duration': call.duration,
                'start_time': call.start_time.isoformat() if call.start_time else None,
                'end_time': call.end_time.isoformat() if call.end_time else None,
                'from': call.from_,
                'to': call.to
            }
        }
        
    except Exception as e:
        logger.error(f"Call status error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                'success': False,
                'error': 'Failed to get call status',
                'message': str(e)
            }
        )

@router.get("/health")
async def voice_health():
    """Voice service health check"""
    return {
        "service": "voice",
        "status": "healthy",
        "twilio_configured": twilio_client is not None,
        "endpoints": [
            "/api/v1/voice/token",
            "/api/v1/voice/make-call", 
            "/api/v1/voice/status/{call_sid}",
            "/api/v1/voice/twiml/outbound",
            "/api/v1/voice/twiml/incoming"
        ]
    }

# For integration into your main FastAPI app:
# from voice_integration import router as voice_router
# app.include_router(voice_router, prefix="/api/v1/voice", tags=["voice"])
