"""
Vocelio Call Center Service
Main entry point for the call center microservice
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🎧 Vocelio Call Center Service",
    version="1.0.0",
    description="AI-powered call center management and voice processing service",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CallRequest(BaseModel):
    phone_number: str
    message: Optional[str] = None
    agent_id: Optional[str] = None

class CallResponse(BaseModel):
    call_id: str
    status: str
    phone_number: str
    created_at: str
    message: Optional[str] = None

class CallStatus(BaseModel):
    call_id: str
    status: str
    duration: Optional[int] = None
    recording_url: Optional[str] = None

# In-memory storage for demo (replace with database in production)
active_calls: Dict[str, Dict[str, Any]] = {}
call_history: List[Dict[str, Any]] = []

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "vocelio-call-center",
        "status": "operational",
        "version": "1.0.0",
        "description": "AI-powered call center service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Voice call management",
            "Real-time call monitoring", 
            "Twilio webhook integration",
            "AI voice processing",
            "Call recording & transcription"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "calls": "/calls",
            "voice_webhook": "/voice-webhook"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "vocelio-call-center", 
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "active_calls": len(active_calls),
        "total_calls_today": len(call_history)
    }

@app.post("/calls", response_model=CallResponse)
async def initiate_call(call_request: CallRequest):
    """Initiate a new outbound call"""
    import uuid
    
    call_id = str(uuid.uuid4())
    
    call_data = {
        "call_id": call_id,
        "phone_number": call_request.phone_number,
        "status": "initiated",
        "created_at": datetime.utcnow().isoformat(),
        "message": call_request.message,
        "agent_id": call_request.agent_id,
        "direction": "outbound"
    }
    
    # Store in active calls
    active_calls[call_id] = call_data
    call_history.append(call_data.copy())
    
    logger.info(f"Initiated call {call_id} to {call_request.phone_number}")
    
    return CallResponse(
        call_id=call_id,
        status="initiated",
        phone_number=call_request.phone_number,
        created_at=call_data["created_at"],
        message=call_request.message
    )

@app.get("/calls", response_model=List[CallResponse])
async def list_calls(status: Optional[str] = None, limit: int = 50):
    """List recent calls with optional status filtering"""
    calls = call_history.copy()
    
    if status:
        calls = [call for call in calls if call.get("status") == status]
    
    # Sort by created_at desc and limit
    calls = sorted(calls, key=lambda x: x["created_at"], reverse=True)[:limit]
    
    return [
        CallResponse(
            call_id=call["call_id"],
            status=call["status"],
            phone_number=call["phone_number"],
            created_at=call["created_at"],
            message=call.get("message")
        )
        for call in calls
    ]

@app.get("/calls/{call_id}", response_model=CallStatus)
async def get_call_status(call_id: str):
    """Get status of a specific call"""
    # Check active calls first
    if call_id in active_calls:
        call = active_calls[call_id]
        return CallStatus(
            call_id=call_id,
            status=call["status"],
            duration=call.get("duration"),
            recording_url=call.get("recording_url")
        )
    
    # Check call history
    for call in call_history:
        if call["call_id"] == call_id:
            return CallStatus(
                call_id=call_id,
                status=call["status"],
                duration=call.get("duration"),
                recording_url=call.get("recording_url")
            )
    
    raise HTTPException(status_code=404, detail="Call not found")

@app.post("/voice-webhook", response_class=PlainTextResponse)
async def voice_webhook(request: Request):
    """Handle Twilio voice webhooks"""
    try:
        # Get form data from Twilio
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        
        logger.info(f"Voice webhook: {call_status} for call {call_sid}")
        
        # Update call status if we have it
        for call_id, call_data in active_calls.items():
            if call_data.get("twilio_sid") == call_sid:
                call_data["status"] = call_status.lower()
                break
        
        # Generate TwiML response based on call status
        if call_status in ["ringing", "in-progress"]:
            twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! Thank you for calling Vocelio AI. Your call is being processed by our AI assistant.</Say>
    <Pause length="1"/>
    <Say voice="alice">Please hold while we connect you to the appropriate service.</Say>
</Response>"""
        elif call_status == "completed":
            twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you for using Vocelio AI. Have a great day!</Say>
</Response>"""
        else:
            twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello from Vocelio AI Call Center!</Say>
</Response>"""
        
        return PlainTextResponse(twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing voice webhook: {e}")
        # Return a basic TwiML response on error
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">We're experiencing technical difficulties. Please try again later.</Say>
</Response>"""
        return PlainTextResponse(error_response, media_type="application/xml")

@app.post("/calls/{call_id}/complete")
async def complete_call(call_id: str):
    """Mark a call as completed"""
    if call_id in active_calls:
        active_calls[call_id]["status"] = "completed"
        active_calls[call_id]["completed_at"] = datetime.utcnow().isoformat()
        
        # Move to history if not already there
        call_data = active_calls[call_id]
        if not any(call["call_id"] == call_id for call in call_history):
            call_history.append(call_data.copy())
        
        # Remove from active calls
        del active_calls[call_id]
        
        logger.info(f"Completed call {call_id}")
        return {"message": "Call completed successfully", "call_id": call_id}
    
    raise HTTPException(status_code=404, detail="Call not found")

@app.get("/analytics")
async def get_call_analytics():
    """Get call center analytics"""
    total_calls = len(call_history)
    active_count = len(active_calls)
    
    # Calculate status distribution
    status_counts = {}
    for call in call_history:
        status = call.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_calls": total_calls,
        "active_calls": active_count,
        "status_distribution": status_counts,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test-voice")
async def test_voice_endpoint():
    """Test endpoint for voice functionality"""
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">This is a test from Vocelio AI Call Center. The service is working correctly!</Say>
</Response>"""
    return PlainTextResponse(twiml_response, media_type="application/xml")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    logger.info(f"Starting Vocelio Call Center Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
