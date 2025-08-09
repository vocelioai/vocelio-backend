# apps/call-center/src/api/v1/api.py
from fastapi import APIRouter
from api.v1.endpoints import calls, webhooks, transfer, recording

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(transfer.router, prefix="/transfer", tags=["transfer"])
api_router.include_router(recording.router, prefix="/recording", tags=["recording"])

---

# apps/call-center/src/api/v1/endpoints/webhooks.py
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from typing import Optional
import logging

from services.webhook_service import WebhookService
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/call-status")
async def twilio_call_status_webhook(
    request: Request,
    x_twilio_signature: Optional[str] = Header(None)
):
    """Handle Twilio call status webhooks"""
    webhook_service = WebhookService()
    
    try:
        # Get request data
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        # Validate Twilio signature in production
        if x_twilio_signature:
            url = str(request.url)
            is_valid = webhook_service.validate_twilio_request(
                url, webhook_data, x_twilio_signature
            )
            if not is_valid:
                logger.warning("Invalid Twilio signature")
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Process webhook
        result = await webhook_service.handle_call_status_webhook(webhook_data)
        return result
        
    except Exception as e:
        logger.error(f"Error processing call status webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/recording-status")
async def twilio_recording_status_webhook(
    request: Request,
    x_twilio_signature: Optional[str] = Header(None)
):
    """Handle Twilio recording status webhooks"""
    webhook_service = WebhookService()
    
    try:
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        # Validate signature
        if x_twilio_signature:
            url = str(request.url)
            is_valid = webhook_service.validate_twilio_request(
                url, webhook_data, x_twilio_signature
            )
            if not is_valid:
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        result = await webhook_service.handle_recording_webhook(webhook_data)
        return result
        
    except Exception as e:
        logger.error(f"Error processing recording webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/transcription")
async def twilio_transcription_webhook(
    request: Request,
    x_twilio_signature: Optional[str] = Header(None)
):
    """Handle Twilio transcription webhooks"""
    webhook_service = WebhookService()
    
    try:
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        # Validate signature
        if x_twilio_signature:
            url = str(request.url)
            is_valid = webhook_service.validate_twilio_request(
                url, webhook_data, x_twilio_signature
            )
            if not is_valid:
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        result = await webhook_service.handle_transcription_webhook(webhook_data)
        return result
        
    except Exception as e:
        logger.error(f"Error processing transcription webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """Handle incoming call TwiML generation"""
    webhook_service = WebhookService()
    
    try:
        form_data = await request.form()
        call_data = dict(form_data)
        
        twiml = await webhook_service.generate_twiml_response(call_data)
        
        from fastapi.responses import Response
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        # Return basic TwiML error response
        error_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, we are experiencing technical difficulties.</Say><Hangup/></Response>'
        from fastapi.responses import Response
        return Response(content=error_twiml, media_type="application/xml")

@router.post("/ai-agent-connect")
async def ai_agent_connect(request: Request):
    """Connect call to AI agent"""
    webhook_service = WebhookService()
    
    try:
        form_data = await request.form()
        call_data = dict(form_data)
        
        twiml = await webhook_service.handle_ai_agent_connect(call_data)
        
        from fastapi.responses import Response
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in AI agent connect: {e}")
        error_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Transferring to human agent.</Say><Dial>+1234567890</Dial></Response>'
        from fastapi.responses import Response
        return Response(content=error_twiml, media_type="application/xml")

@router.post("/process-speech")
async def process_speech(request: Request):
    """Process customer speech input"""
    webhook_service = WebhookService()
    
    try:
        form_data = await request.form()
        call_data = dict(form_data)
        
        twiml = await webhook_service.handle_speech_processing(call_data)
        
        from fastapi.responses import Response
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        error_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>I am having trouble understanding. Please hold.</Say><Hold/></Response>'
        from fastapi.responses import Response
        return Response(content=error_twiml, media_type="application/xml")

---

# apps/call-center/src/services/transfer_service.py
from typing import Optional, Dict, Any
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from shared.database.client import get_database
from models.call import Call, CallStatus
from models.agent import AIAgent
from services.call_service import CallService

logger = logging.getLogger(__name__)

class TransferService:
    def __init__(self):
        self.call_service = CallService()
    
    async def transfer_call(
        self, 
        call_id: str, 
        target_type: str, 
        target_agent_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """Transfer call to another agent or human"""
        try:
            async with get_database() as db:
                # Get the call
                query = select(Call).where(Call.id == call_id)
                result = await db.execute(query)
                call = result.scalar_one_or_none()
                
                if not call:
                    logger.error(f"Call {call_id} not found for transfer")
                    return False
                
                if call.status not in [CallStatus.ACTIVE, CallStatus.IN_PROGRESS]:
                    logger.error(f"Call {call_id} cannot be transferred - status: {call.status}")
                    return False
                
                # Store current agent as transferred_from
                call.transferred_from_agent_id = call.agent_id
                call.transfer_reason = reason
                call.transfer_type = target_type
                call.transferred_at = datetime.utcnow()
                
                if target_type == "agent" and target_agent_id:
                    # Transfer to specific AI agent
                    target_agent = await self._get_agent(db, target_agent_id)
                    if not target_agent:
                        logger.error(f"Target agent {target_agent_id} not found")
                        return False
                    
                    call.agent_id = target_agent_id
                    call.transferred_to_agent_id = target_agent_id
                    call.status = CallStatus.TRANSFERRED
                    
                    # Log transfer
                    await self._log_transfer(call_id, "agent", target_agent.name, reason)
                    
                elif target_type == "human":
                    # Transfer to human agent
                    call.status = CallStatus.TRANSFERRED
                    call.transfer_type = "human"
                    
                    # In a real implementation, this would integrate with
                    # your human agent queue system
                    await self._initiate_human_transfer(call)
                    
                    # Log transfer
                    await self._log_transfer(call_id, "human", "Human Agent", reason)
                    
                elif target_type == "queue":
                    # Transfer to queue
                    call.status = CallStatus.QUEUED
                    call.agent_id = None
                    
                    # Add to appropriate queue
                    await self._add_to_queue(call, reason)
                    
                    # Log transfer
                    await self._log_transfer(call_id, "queue", "Call Queue", reason)
                
                await db.commit()
                
                logger.info(f"Successfully transferred call {call_id} to {target_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error transferring call {call_id}: {e}")
            return False
    
    async def get_available_agents(self, specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available agents for transfer"""
        try:
            async with get_database() as db:
                query = select(AIAgent).where(AIAgent.status == "active")
                
                if specialty:
                    query = query.where(AIAgent.specialty == specialty)
                
                result = await db.execute(query)
                agents = result.scalars().all()
                
                available_agents = []
                for agent in agents:
                    # Check current workload
                    current_calls = await self._get_agent_current_calls(db, agent.id)
                    
                    available_agents.append({
                        "id": str(agent.id),
                        "name": agent.name,
                        "specialty": agent.specialty,
                        "performance_score": agent.performance_score,
                        "current_calls": current_calls,
                        "available": current_calls < 10  # Max 10 concurrent calls per agent
                    })
                
                return available_agents
                
        except Exception as e:
            logger.error(f"Error getting available agents: {e}")
            return []
    
    async def get_transfer_history(self, call_id: str) -> List[Dict[str, Any]]:
        """Get transfer history for a call"""
        try:
            async with get_database() as db:
                # This would query a transfer_history table in a real implementation
                # For now, we'll return the basic transfer info from the call record
                query = select(Call).where(Call.id == call_id)
                result = await db.execute(query)
                call = result.scalar_one_or_none()
                
                if not call:
                    return []
                
                history = []
                if call.transferred_at:
                    history.append({
                        "timestamp": call.transferred_at,
                        "from_agent_id": str(call.transferred_from_agent_id) if call.transferred_from_agent_id else None,
                        "to_agent_id": str(call.transferred_to_agent_id) if call.transferred_to_agent_id else None,
                        "transfer_type": call.transfer_type,
                        "reason": call.transfer_reason
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting transfer history for {call_id}: {e}")
            return []
    
    async def emergency_transfer_all(self, reason: str = "Emergency transfer") -> Dict[str, Any]:
        """Emergency transfer all active calls to human agents"""
        try:
            async with get_database() as db:
                # Get all active calls
                query = select(Call).where(
                    Call.status.in_([CallStatus.ACTIVE, CallStatus.IN_PROGRESS])
                )
                result = await db.execute(query)
                active_calls = result.scalars().all()
                
                transferred_count = 0
                failed_count = 0
                
                for call in active_calls:
                    success = await self.transfer_call(
                        str(call.id), 
                        "human", 
                        reason=f"Emergency: {reason}"
                    )
                    if success:
                        transferred_count += 1
                    else:
                        failed_count += 1
                
                return {
                    "total_calls": len(active_calls),
                    "transferred": transferred_count,
                    "failed": failed_count,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in emergency transfer: {e}")
            return {"error": str(e)}
    
    async def _get_agent(self, db: AsyncSession, agent_id: str) -> Optional[AIAgent]:
        """Get agent by ID"""
        query = select(AIAgent).where(AIAgent.id == agent_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_agent_current_calls(self, db: AsyncSession, agent_id: str) -> int:
        """Get current number of calls for an agent"""
        query = select(func.count(Call.id)).where(
            and_(
                Call.agent_id == agent_id,
                Call.status.in_([CallStatus.ACTIVE, CallStatus.IN_PROGRESS])
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def _log_transfer(self, call_id: str, transfer_type: str, target: str, reason: Optional[str]):
        """Log transfer event"""
        # In a real implementation, this would write to a transfer_log table
        logger.info(f"Call {call_id} transferred to {transfer_type}: {target}. Reason: {reason}")
    
    async def _initiate_human_transfer(self, call: Call):
        """Initiate transfer to human agent"""
        # This would integrate with your human agent system
        # For example, updating a queue system, notifying supervisors, etc.
        logger.info(f"Initiating human transfer for call {call.id}")
    
    async def _add_to_queue(self, call: Call, reason: Optional[str]):
        """Add call to appropriate queue"""
        # This would integrate with your call queue system
        logger.info(f"Adding call {call.id} to queue. Reason: {reason}")

---

# apps/call-center/src/services/recording_service.py
from typing import Optional, Dict, Any, List
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import httpx
import os

from shared.database.client import get_database
from models.call import Call, CallRecording
from services.ai_service import AIService
from core.config import settings

logger = logging.getLogger(__name__)

class RecordingService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def start_recording(self, call_id: str) -> Optional[CallRecording]:
        """Start recording for a call"""
        try:
            async with get_database() as db:
                # Get the call
                query = select(Call).where(Call.id == call_id)
                result = await db.execute(query)
                call = result.scalar_one_or_none()
                
                if not call:
                    logger.error(f"Call {call_id} not found")
                    return None
                
                # Check if recording already exists
                existing_query = select(CallRecording).where(
                    CallRecording.call_id == call_id
                )
                existing_result = await db.execute(existing_query)
                existing_recording = existing_result.scalar_one_or_none()
                
                if existing_recording:
                    logger.warning(f"Recording already exists for call {call_id}")
                    return existing_recording
                
                # Create recording record
                recording = CallRecording(
                    call_id=call_id,
                    recording_status="in-progress",
                    started_at=datetime.utcnow(),
                    consent_recorded=True  # Assuming consent was obtained
                )
                
                db.add(recording)
                await db.commit()
                await db.refresh(recording)
                
                logger.info(f"Started recording for call {call_id}")
                return recording
                
        except Exception as e:
            logger.error(f"Error starting recording for call {call_id}: {e}")
            return None
    
    async def stop_recording(self, call_id: str) -> bool:
        """Stop recording for a call"""
        try:
            async with get_database() as db:
                query = select(CallRecording).where(
                    CallRecording.call_id == call_id
                )
                result = await db.execute(query)
                recording = result.scalar_one_or_none()
                
                if not recording:
                    logger.error(f"No recording found for call {call_id}")
                    return False
                
                recording.recording_status = "completed"
                recording.ended_at = datetime.utcnow()
                
                if recording.started_at:
                    duration = recording.ended_at - recording.started_at
                    recording.duration = int(duration.total_seconds())
                
                await db.commit()
                
                # Process recording in background
                asyncio.create_task(self.process_recording(recording.id))
                
                logger.info(f"Stopped recording for call {call_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error stopping recording for call {call_id}: {e}")
            return False
    
    async def get_recording(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get recording information for a call"""
        try:
            async with get_database() as db:
                query = select(CallRecording).where(
                    CallRecording.call_id == call_id
                )
                result = await db.execute(query)
                recording = result.scalar_one_or_none()
                
                if not recording:
                    return None
                
                return {
                    "id": str(recording.id),
                    "call_id": str(recording.call_id),
                    "recording_url": recording.recording_url,
                    "recording_status": recording.recording_status,
                    "duration": recording.duration,
                    "file_size": recording.file_size,
                    "file_format": recording.file_format,
                    "started_at": recording.started_at,
                    "ended_at": recording.ended_at,
                    "transcription_status": recording.transcription_status,
                    "transcription_url": recording.transcription_url,
                    "processed": recording.processed
                }
                
        except Exception as e:
            logger.error(f"Error getting recording for call {call_id}: {e}")
            return None
    
    async def process_recording(self, recording_id: str):
        """Process recording - transcription, analysis, etc."""
        try:
            async with get_database() as db:
                query = select(CallRecording).where(CallRecording.id == recording_id)
                result = await db.execute(query)
                recording = result.scalar_one_or_none()
                
                if not recording:
                    logger.error(f"Recording {recording_id} not found")
                    return
                
                logger.info(f"Processing recording {recording_id}")
                
                # Download recording file
                recording_data = await self._download_recording(recording.recording_url)
                if not recording_data:
                    logger.error(f"Failed to download recording {recording_id}")
                    return
                
                # Transcribe audio
                transcription = await self._transcribe_audio(recording_data)
                if transcription:
                    recording.transcription_status = "completed"
                    
                    # Analyze transcription with AI
                    analysis = await self.ai_service.analyze_transcription(
                        transcription, recording.call_id
                    )
                    
                    # Update call with insights
                    await self._update_call_with_analysis(recording.call_id, analysis)
                
                # Calculate file info
                recording.file_size = len(recording_data) if recording_data else 0
                recording.file_format = "mp3"  # Default format
                recording.processed = True
                recording.processed_at = datetime.utcnow()
                
                await db.commit()
                
                logger.info(f"Completed processing recording {recording_id}")
                
        except Exception as e:
            logger.error(f"Error processing recording {recording_id}: {e}")
    
    async def get_recordings_for_cleanup(self, retention_days: int = 365) -> List[str]:
        """Get recordings that should be deleted based on retention policy"""
        try:
            async with get_database() as db:
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                
                query = select(CallRecording.id).where(
                    CallRecording.created_at < cutoff_date
                )
                result = await db.execute(query)
                recording_ids = [str(row[0]) for row in result.fetchall()]
                
                return recording_ids
                
        except Exception as e:
            logger.error(f"Error getting recordings for cleanup: {e}")
            return []
    
    async def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording and its files"""
        try:
            async with get_database() as db:
                query = select(CallRecording).where(CallRecording.id == recording_id)
                result = await db.execute(query)
                recording = result.scalar_one_or_none()
                
                if not recording:
                    return False
                
                # Delete file from storage
                if recording.recording_url:
                    await self._delete_recording_file(recording.recording_url)
                
                # Delete database record
                await db.delete(recording)
                await db.commit()
                
                logger.info(f"Deleted recording {recording_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting recording {recording_id}: {e}")
            return False
    
    async def _download_recording(self, url: str) -> Optional[bytes]:
        """Download recording file from URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Error downloading recording from {url}: {e}")
            return None
    
    async def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data to text"""
        try:
            # This would integrate with your speech-to-text service
            # For example, Google Speech-to-Text, AWS Transcribe, etc.
            
            # Placeholder implementation
            logger.info("Transcribing audio...")
            await asyncio.sleep(1)  # Simulate processing time
            
            # Return mock transcription
            return "This is a mock transcription of the call recording."
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def _update_call_with_analysis(self, call_id: str, analysis: Dict[str, Any]):
        """Update call record with analysis results"""
        try:
            async with get_database() as db:
                query = select(Call).where(Call.id == call_id)
                result = await db.execute(query)
                call = result.scalar_one_or_none()
                
                if call and analysis:
                    call.sentiment = analysis.get('sentiment')
                    call.confidence_score = analysis.get('confidence')
                    call.conversion_probability = analysis.get('conversion_probability')
                    call.next_best_action = analysis.get('next_best_action')
                    call.detected_objections = analysis.get('objections', [])
                    
                    await db.commit()
                    
        except Exception as e:
            logger.error(f"Error updating call {call_id} with analysis: {e}")
    
    async def _delete_recording_file(self, url: str):
        """Delete recording file from storage"""
        try:
            # This would delete the file from your storage system
            # (S3, Google Cloud Storage, etc.)
            logger.info(f"Deleting recording file: {url}")
        except Exception as e:
            logger.error(f"Error deleting recording file {url}: {e}")

---

# apps/call-center/src/api/v1/endpoints/transfer.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging

from services.transfer_service import TransferService
from schemas.call import CallTransferRequest
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{call_id}")
async def transfer_call(
    call_id: str,
    transfer_request: CallTransferRequest,
    current_user: User = Depends(get_current_user)
):
    """Transfer a call to another agent or human"""
    transfer_service = TransferService()
    
    success = await transfer_service.transfer_call(
        call_id=call_id,
        target_type=transfer_request.target_type,
        target_agent_id=transfer_request.target_agent_id,
        reason=transfer_request.reason
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Transfer failed")
    
    return {"message": "Call transferred successfully", "call_id": call_id}

@router.get("/agents/available")
async def get_available_agents(
    specialty: str = None,
    current_user: User = Depends(get_current_user)
):
    """Get list of available agents for transfer"""
    transfer_service = TransferService()
    
    agents = await transfer_service.get_available_agents(specialty=specialty)
    return {"agents": agents}

@router.get("/{call_id}/history")
async def get_transfer_history(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get transfer history for a call"""
    transfer_service = TransferService()
    
    history = await transfer_service.get_transfer_history(call_id)
    return {"call_id": call_id, "transfer_history": history}

@router.post("/emergency/all")
async def emergency_transfer_all(
    reason: str = "Emergency transfer",
    current_user: User = Depends(get_current_user)
):
    """Emergency transfer all active calls to human agents"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    transfer_service = TransferService()
    
    result = await transfer_service.emergency_transfer_all(reason)
    return result

---

# apps/call-center/src/api/v1/endpoints/recording.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
import logging

from services.recording_service import RecordingService
from schemas.call import CallRecordingResponse
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{call_id}/start")
async def start_recording(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Start recording for a call"""
    recording_service = RecordingService()
    
    recording = await recording_service.start_recording(call_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Failed to start recording")
    
    return {"message": "Recording started", "recording_id": str(recording.id)}

@router.post("/{call_id}/stop")
async def stop_recording(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stop recording for a call"""
    recording_service = RecordingService()
    
    success = await recording_service.stop_recording(call_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failed to stop recording")
    
    return {"message": "Recording stopped"}

@router.get("/{call_id}")
async def get_call_recording(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get recording information for a call"""
    recording_service = RecordingService()
    
    recording = await recording_service.get_recording(call_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return recording

@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a recording"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    recording_service = RecordingService()
    
    success = await recording_service.delete_recording(recording_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return {"message": "Recording deleted successfully"}

@router.post("/cleanup")
async def cleanup_old_recordings(
    retention_days: int = 365,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Cleanup old recordings based on retention policy"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    recording_service = RecordingService()
    
    # Get recordings to cleanup
    recording_ids = await recording_service.get_recordings_for_cleanup(retention_days)
    
    # Delete in background
    for recording_id in recording_ids:
        background_tasks.add_task(recording_service.delete_recording, recording_id)
    
    return {
        "message": "Cleanup initiated",
        "recordings_to_delete": len(recording_ids)
    }