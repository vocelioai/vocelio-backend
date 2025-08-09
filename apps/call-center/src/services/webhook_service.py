# apps/call-center/src/services/webhook_service.py
from typing import Dict, Any, Optional
import logging
import json
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from twilio.twiml import VoiceResponse
from twilio.request_validator import RequestValidator

from shared.database.client import get_database
from models.call import Call, CallStatus, CallRecording
from models.conversation import Conversation
from schemas.call import TwilioCallStatus, TwilioRecordingStatus
from services.ai_service import AIService
from services.recording_service import RecordingService
from core.config import settings

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self):
        self.ai_service = AIService()
        self.recording_service = RecordingService()
        self.twilio_validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    
    def validate_twilio_request(self, url: str, params: Dict[str, Any], signature: str) -> bool:
        """Validate that the request came from Twilio"""
        try:
            return self.twilio_validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Error validating Twilio request: {e}")
            return False
    
    async def handle_call_status_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Twilio call status webhooks"""
        try:
            call_sid = webhook_data.get('CallSid')
            call_status = webhook_data.get('CallStatus')
            
            logger.info(f"Received call status webhook: {call_sid} - {call_status}")
            
            async with get_database() as db:
                # Find the call by Twilio SID
                query = select(Call).where(Call.twilio_call_sid == call_sid)
                result = await db.execute(query)
                call = result.scalar_one_or_none()
                
                if not call:
                    logger.warning(f"Call not found for SID: {call_sid}")
                    return {"status": "call_not_found"}
                
                # Update call status based on Twilio status
                previous_status = call.status
                call.status = self._map_twilio_status(call_status)
                
                # Update timing fields
                now = datetime.utcnow()
                if call_status == 'ringing' and not call.started_at:
                    call.started_at = now
                elif call_status == 'in-progress' and not call.answered_at:
                    call.answered_at = now
                elif call_status in ['completed', 'failed', 'busy', 'no-answer'] and not call.ended_at:
                    call.ended_at = now
                    # Calculate duration
                    if call.answered_at:
                        call.duration = int((now - call.answered_at).total_seconds())
                
                # Add additional Twilio data
                if webhook_data.get('Duration'):
                    call.duration = int(webhook_data['Duration'])
                if webhook_data.get('RecordingUrl'):
                    call.recording_url = webhook_data['RecordingUrl']
                if webhook_data.get('RecordingSid'):
                    call.recording_sid = webhook_data['RecordingSid']
                
                call.updated_at = now
                
                await db.commit()
                await db.refresh(call)
                
                # Handle status-specific logic
                await self._handle_status_change(call, previous_status, call.status)
                
                logger.info(f"Updated call {call.id} status from {previous_status} to {call.status}")
                
                return {
                    "status": "success",
                    "call_id": str(call.id),
                    "previous_status": previous_status,
                    "new_status": call.status
                }
                
        except Exception as e:
            logger.error(f"Error handling call status webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_recording_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Twilio recording status webhooks"""
        try:
            recording_sid = webhook_data.get('RecordingSid')
            call_sid = webhook_data.get('CallSid')
            recording_status = webhook_data.get('RecordingStatus')
            recording_url = webhook_data.get('RecordingUrl')
            
            logger.info(f"Received recording webhook: {recording_sid} - {recording_status}")
            
            async with get_database() as db:
                # Find the call
                call_query = select(Call).where(Call.twilio_call_sid == call_sid)
                call_result = await db.execute(call_query)
                call = call_result.scalar_one_or_none()
                
                if not call:
                    logger.warning(f"Call not found for recording webhook: {call_sid}")
                    return {"status": "call_not_found"}
                
                # Update or create recording record
                recording_query = select(CallRecording).where(
                    CallRecording.twilio_recording_sid == recording_sid
                )
                recording_result = await db.execute(recording_query)
                recording = recording_result.scalar_one_or_none()
                
                if not recording:
                    # Create new recording record
                    recording = CallRecording(
                        call_id=call.id,
                        twilio_recording_sid=recording_sid,
                        recording_url=recording_url,
                        recording_status=recording_status,
                        started_at=datetime.utcnow()
                    )
                    db.add(recording)
                else:
                    # Update existing recording
                    recording.recording_status = recording_status
                    recording.recording_url = recording_url
                    recording.updated_at = datetime.utcnow()
                
                # Handle recording completion
                if recording_status == 'completed':
                    recording.ended_at = datetime.utcnow()
                    if webhook_data.get('RecordingDuration'):
                        recording.duration = int(webhook_data['RecordingDuration'])
                    
                    # Update call record
                    call.recording_url = recording_url
                    call.recording_sid = recording_sid
                    call.recording_status = recording_status
                    
                    # Schedule transcription processing
                    asyncio.create_task(
                        self.recording_service.process_recording(recording.id)
                    )
                
                await db.commit()
                
                return {
                    "status": "success",
                    "recording_id": str(recording.id),
                    "recording_status": recording_status
                }
                
        except Exception as e:
            logger.error(f"Error handling recording webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_transcription_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Twilio transcription webhooks"""
        try:
            transcription_sid = webhook_data.get('TranscriptionSid')
            recording_sid = webhook_data.get('RecordingSid')
            transcription_text = webhook_data.get('TranscriptionText')
            transcription_status = webhook_data.get('TranscriptionStatus')
            
            logger.info(f"Received transcription webhook: {transcription_sid} - {transcription_status}")
            
            async with get_database() as db:
                # Find the recording
                recording_query = select(CallRecording).where(
                    CallRecording.twilio_recording_sid == recording_sid
                )
                recording_result = await db.execute(recording_query)
                recording = recording_result.scalar_one_or_none()
                
                if not recording:
                    logger.warning(f"Recording not found for transcription: {recording_sid}")
                    return {"status": "recording_not_found"}
                
                # Update transcription status
                recording.transcription_status = transcription_status
                recording.updated_at = datetime.utcnow()
                
                if transcription_status == 'completed' and transcription_text:
                    # Process the transcription with AI
                    ai_analysis = await self.ai_service.analyze_transcription(
                        transcription_text, recording.call_id
                    )
                    
                    # Create conversation entries from transcription
                    await self._create_conversation_from_transcription(
                        recording.call_id, transcription_text, ai_analysis
                    )
                    
                    # Update call with AI insights
                    call_query = select(Call).where(Call.id == recording.call_id)
                    call_result = await db.execute(call_query)
                    call = call_result.scalar_one_or_none()
                    
                    if call and ai_analysis:
                        call.sentiment = ai_analysis.get('sentiment')
                        call.confidence_score = ai_analysis.get('confidence')
                        call.conversion_probability = ai_analysis.get('conversion_probability')
                        call.next_best_action = ai_analysis.get('next_best_action')
                        call.detected_objections = ai_analysis.get('objections', [])
                
                await db.commit()
                
                return {
                    "status": "success",
                    "transcription_status": transcription_status
                }
                
        except Exception as e:
            logger.error(f"Error handling transcription webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def generate_twiml_response(self, call_data: Dict[str, Any]) -> str:
        """Generate TwiML response for incoming calls"""
        try:
            response = VoiceResponse()
            
            # Get call configuration
            from_number = call_data.get('From')
            to_number = call_data.get('To')
            call_sid = call_data.get('CallSid')
            
            logger.info(f"Generating TwiML for call: {call_sid}")
            
            # Check if recording is enabled
            if settings.RECORDING_ENABLED:
                response.record(
                    action=f"{settings.WEBHOOK_BASE_URL}/webhooks/recording-status",
                    method="POST",
                    max_length=3600,  # 1 hour max
                    transcribe=True,
                    transcribe_callback=f"{settings.WEBHOOK_BASE_URL}/webhooks/transcription"
                )
            
            # Add greeting and start conversation
            response.say(
                "Hello! Thank you for calling. Please hold while we connect you with one of our AI specialists.",
                voice="alice",
                language="en-US"
            )
            
            # Connect to AI agent
            response.redirect(
                f"{settings.WEBHOOK_BASE_URL}/webhooks/ai-agent-connect",
                method="POST"
            )
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error generating TwiML response: {e}")
            # Fallback response
            response = VoiceResponse()
            response.say("We're sorry, but we're experiencing technical difficulties. Please try again later.")
            response.hangup()
            return str(response)
    
    async def handle_ai_agent_connect(self, call_data: Dict[str, Any]) -> str:
        """Handle AI agent connection for calls"""
        try:
            call_sid = call_data.get('CallSid')
            
            # This would integrate with your AI voice service
            # For now, we'll create a simple conversation flow
            
            response = VoiceResponse()
            
            # Gather customer input
            gather = response.gather(
                action=f"{settings.WEBHOOK_BASE_URL}/webhooks/process-speech",
                method="POST",
                speech_timeout="3",
                language="en-US",
                enhanced=True
            )
            
            gather.say(
                "Hi! I'm an AI assistant. How can I help you today?",
                voice="alice"
            )
            
            # Fallback if no input
            response.say("I didn't hear anything. Let me transfer you to a human agent.")
            response.dial(settings.FALLBACK_PHONE_NUMBER)
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error in AI agent connect: {e}")
            response = VoiceResponse()
            response.say("Let me transfer you to a human agent.")
            response.dial(settings.FALLBACK_PHONE_NUMBER)
            return str(response)
    
    async def handle_speech_processing(self, call_data: Dict[str, Any]) -> str:
        """Process speech input from customer"""
        try:
            call_sid = call_data.get('CallSid')
            speech_result = call_data.get('SpeechResult')
            confidence = float(call_data.get('Confidence', 0))
            
            logger.info(f"Processing speech for {call_sid}: {speech_result} (confidence: {confidence})")
            
            # Store conversation in database
            await self._store_conversation_message(call_sid, 'customer', speech_result)
            
            # Get AI response
            ai_response = await self.ai_service.generate_response(
                call_sid, speech_result, confidence
            )
            
            # Store AI response
            await self._store_conversation_message(call_sid, 'agent', ai_response['text'])
            
            response = VoiceResponse()
            
            # Speak AI response
            response.say(ai_response['text'], voice="alice")
            
            # Continue conversation or end call based on AI decision
            if ai_response.get('continue_conversation', True):
                gather = response.gather(
                    action=f"{settings.WEBHOOK_BASE_URL}/webhooks/process-speech",
                    method="POST",
                    speech_timeout="3",
                    language="en-US",
                    enhanced=True
                )
                gather.pause(length=1)
            else:
                # End call or transfer
                if ai_response.get('transfer_to_human'):
                    response.say("Let me transfer you to a human specialist.")
                    response.dial(settings.FALLBACK_PHONE_NUMBER)
                else:
                    response.say("Thank you for your time. Have a great day!")
                    response.hangup()
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}")
            response = VoiceResponse()
            response.say("I'm having trouble understanding. Let me transfer you to a human agent.")
            response.dial(settings.FALLBACK_PHONE_NUMBER)
            return str(response)
    
    def _map_twilio_status(self, twilio_status: str) -> CallStatus:
        """Map Twilio call status to our internal status"""
        status_mapping = {
            'queued': CallStatus.QUEUED,
            'ringing': CallStatus.RINGING,
            'in-progress': CallStatus.IN_PROGRESS,
            'completed': CallStatus.COMPLETED,
            'failed': CallStatus.FAILED,
            'busy': CallStatus.FAILED,
            'no-answer': CallStatus.FAILED,
            'canceled': CallStatus.CANCELLED
        }
        return status_mapping.get(twilio_status, CallStatus.ACTIVE)
    
    async def _handle_status_change(self, call: Call, previous_status: str, new_status: str):
        """Handle additional logic when call status changes"""
        try:
            # Trigger real-time updates to connected clients
            # This would be handled by the WebSocket manager
            
            # Update analytics
            await self._update_call_analytics(call, new_status)
            
            # Handle specific status transitions
            if new_status == CallStatus.COMPLETED:
                await self._handle_call_completion(call)
            elif new_status == CallStatus.FAILED:
                await self._handle_call_failure(call)
                
        except Exception as e:
            logger.error(f"Error handling status change: {e}")
    
    async def _create_conversation_from_transcription(
        self, call_id: str, transcription: str, ai_analysis: Dict[str, Any]
    ):
        """Create conversation entries from transcription"""
        try:
            # This is a simplified version - in practice, you'd need to
            # separate speaker segments from the transcription
            async with get_database() as db:
                conversation = Conversation(
                    call_id=call_id,
                    speaker='customer',  # This would be determined by speaker diarization
                    message=transcription,
                    sentiment=ai_analysis.get('sentiment'),
                    intent=ai_analysis.get('intent'),
                    entities=ai_analysis.get('entities'),
                    confidence=ai_analysis.get('confidence')
                )
                db.add(conversation)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error creating conversation from transcription: {e}")
    
    async def _store_conversation_message(self, call_sid: str, speaker: str, message: str):
        """Store conversation message in database"""
        try:
            async with get_database() as db:
                # Find call by SID
                call_query = select(Call).where(Call.twilio_call_sid == call_sid)
                call_result = await db.execute(call_query)
                call = call_result.scalar_one_or_none()
                
                if call:
                    conversation = Conversation(
                        call_id=call.id,
                        speaker=speaker,
                        message=message,
                        created_at=datetime.utcnow()
                    )
                    db.add(conversation)
                    await db.commit()
                    
        except Exception as e:
            logger.error(f"Error storing conversation message: {e}")
    
    async def _update_call_analytics(self, call: Call, status: str):
        """Update call analytics"""
        # This would update various analytics tables/caches
        pass
    
    async def _handle_call_completion(self, call: Call):
        """Handle call completion logic"""
        # Calculate final metrics, update agent performance, etc.
        pass
    
    async def _handle_call_failure(self, call: Call):
        """Handle call failure logic"""
        # Log failure reasons, update retry logic, etc.
        pass