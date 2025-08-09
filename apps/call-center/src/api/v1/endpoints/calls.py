# apps/call-center/src/api/v1/endpoints/calls.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.call_service import CallService
from services.recording_service import RecordingService
from services.transfer_service import TransferService
from schemas.call import (
    CallResponse, CallCreate, CallUpdate, CallStatusUpdate,
    LiveMetrics, CallFilters, CallTransferRequest
)
from schemas.agent import AgentPerformance
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metrics/live", response_model=LiveMetrics)
async def get_live_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get real-time call center metrics"""
    call_service = CallService()
    return await call_service.get_live_metrics()

@router.get("/active", response_model=List[CallResponse])
async def get_active_calls(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get list of active calls with filtering"""
    call_service = CallService()
    
    # Build filters
    filters = {}
    if status and status != "all":
        filters["status"] = status
    if industry and industry != "all":
        filters["industry"] = industry
    if priority and priority != "all":
        filters["priority"] = priority
    if agent_name and agent_name != "all":
        filters["agent_name"] = agent_name
    if search:
        filters["search"] = search
    
    return await call_service.get_active_calls(limit=limit, offset=offset, filters=filters)

@router.get("/{call_id}", response_model=CallResponse)
async def get_call_detail(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information for a specific call"""
    call_service = CallService()
    call = await call_service.get_call_detail(call_id)
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return call

@router.post("/", response_model=CallResponse)
async def create_call(
    call_data: CallCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create a new call"""
    call_service = CallService()
    
    try:
        call = await call_service.create_call(call_data)
        
        # Start call processing in background
        background_tasks.add_task(call_service.process_call, call.id)
        
        return call
    except Exception as e:
        logger.error(f"Error creating call: {e}")
        raise HTTPException(status_code=500, detail="Failed to create call")

@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str,
    call_update: CallUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update call information"""
    call_service = CallService()
    
    call = await call_service.update_call_status(call_id, call_update)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return call

@router.post("/{call_id}/end")
async def end_call(
    call_id: str,
    outcome: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """End a call"""
    call_service = CallService()
    
    success = await call_service.end_call(call_id, outcome)
    if not success:
        raise HTTPException(status_code=404, detail="Call not found or already ended")
    
    return {"message": "Call ended successfully", "call_id": call_id}

@router.post("/{call_id}/transfer")
async def transfer_call(
    call_id: str,
    transfer_request: CallTransferRequest,
    current_user: User = Depends(get_current_user)
):
    """Transfer call to another agent or human"""
    call_service = CallService()
    transfer_service = TransferService()
    
    # Validate transfer request
    if transfer_request.target_type == "agent" and not transfer_request.target_agent_id:
        raise HTTPException(status_code=400, detail="Target agent ID required for agent transfer")
    
    success = await transfer_service.transfer_call(
        call_id=call_id,
        target_type=transfer_request.target_type,
        target_agent_id=transfer_request.target_agent_id,
        reason=transfer_request.reason
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Call not found or transfer failed")
    
    return {"message": "Call transferred successfully", "call_id": call_id}

@router.get("/{call_id}/transcript")
async def get_call_transcript(
    call_id: str,
    full: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """Get call transcript"""
    call_service = CallService()
    
    call = await call_service.get_call_detail(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    transcript = await call_service._get_call_transcript(call_id, full=full)
    return {"call_id": call_id, "transcript": transcript}

@router.post("/{call_id}/transcript/message")
async def add_transcript_message(
    call_id: str,
    message_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Add a message to call transcript"""
    call_service = CallService()
    
    # Validate message data
    required_fields = ["speaker", "text"]
    if not all(field in message_data for field in required_fields):
        raise HTTPException(status_code=400, detail="Missing required fields: speaker, text")
    
    success = await call_service.add_transcript_message(
        call_id=call_id,
        speaker=message_data["speaker"],
        text=message_data["text"]
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return {"message": "Transcript message added successfully"}

@router.get("/{call_id}/recording")
async def get_call_recording(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get call recording information"""
    recording_service = RecordingService()
    
    recording = await recording_service.get_recording(call_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return recording

@router.post("/{call_id}/recording/start")
async def start_call_recording(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Start call recording"""
    recording_service = RecordingService()
    
    recording = await recording_service.start_recording(call_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Call not found or recording failed to start")
    
    return {"message": "Recording started", "recording_id": recording.id}

@router.post("/{call_id}/recording/stop")
async def stop_call_recording(
    call_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stop call recording"""
    recording_service = RecordingService()
    
    success = await recording_service.stop_recording(call_id)
    if not success:
        raise HTTPException(status_code=404, detail="Call not found or no active recording")
    
    return {"message": "Recording stopped"}

@router.get("/analytics/funnel")
async def get_conversion_funnel(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get conversion funnel analytics"""
    call_service = CallService()
    
    funnel_data = await call_service.get_conversion_funnel(date_from, date_to)
    return funnel_data

@router.get("/analytics/outcomes")
async def get_call_outcomes(
    period: str = Query("hour", regex="^(hour|day|week|month)$"),
    current_user: User = Depends(get_current_user)
):
    """Get call outcomes statistics"""
    call_service = CallService()
    
    outcomes = await call_service.get_call_outcomes(period)
    return outcomes

@router.get("/agents/performance", response_model=List[AgentPerformance])
async def get_agent_performance(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Get agent performance metrics"""
    call_service = CallService()
    return await call_service.get_agent_performance(limit=limit)

@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(get_current_user)
):
    """Get system health status"""
    call_service = CallService()
    return await call_service.get_system_health()

@router.post("/emergency/stop-all")
async def emergency_stop_all_calls(
    reason: str = "Emergency stop initiated by admin",
    current_user: User = Depends(get_current_user)
):
    """Emergency stop all active calls"""
    # Verify admin permissions
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    call_service = CallService()
    
    stopped_calls = await call_service.emergency_stop_all_calls(reason)
    
    return {
        "message": "Emergency stop executed",
        "stopped_calls": stopped_calls,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/boost/performance")
async def boost_system_performance(
    boost_level: int = Query(1, ge=1, le=3),
    current_user: User = Depends(get_current_user)
):
    """Boost system performance temporarily"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    call_service = CallService()
    
    result = await call_service.boost_performance(boost_level)
    
    return {
        "message": "Performance boost activated",
        "boost_level": boost_level,
        "estimated_duration": "30 minutes",
        "result": result
    }

@router.get("/export/live-data")
async def export_live_data(
    format_type: str = Query("json", regex="^(json|csv|excel)$"),
    current_user: User = Depends(get_current_user)
):
    """Export live call data"""
    call_service = CallService()
    
    export_data = await call_service.export_live_data(format_type)
    
    return {
        "message": "Data export prepared",
        "format": format_type,
        "download_url": export_data.get("download_url"),
        "expires_at": export_data.get("expires_at")
    }