# apps/call-center/src/api/v1/endpoints/phone_system.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.phone_system_service import PhoneSystemService
from schemas.phone_system import (
    PhoneNumber, PhoneNumberCreate, PhoneNumberUpdate,
    Extension, ExtensionCreate, SystemStatus, CapacityMetrics
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/numbers", response_model=List[PhoneNumber])
async def get_phone_numbers(
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Get list of phone numbers with filtering"""
    phone_service = PhoneSystemService()
    
    try:
        filters = {}
        if status and status != "all":
            filters["status"] = status
        if assigned_to and assigned_to != "all":
            filters["assigned_to"] = assigned_to
        if type and type != "all":
            filters["type"] = type
        
        numbers = await phone_service.get_phone_numbers(
            limit=limit, offset=offset, filters=filters
        )
        return numbers
        
    except Exception as e:
        logger.error(f"Error getting phone numbers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get phone numbers")

@router.post("/numbers", response_model=PhoneNumber)
async def create_phone_number(
    phone_data: PhoneNumberCreate,
    current_user: User = Depends(get_current_user)
):
    """Add new phone number to system"""
    phone_service = PhoneSystemService()
    
    try:
        # Validate phone number format
        if not await phone_service.validate_phone_number(phone_data.number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Check if number already exists
        if await phone_service.phone_number_exists(phone_data.number):
            raise HTTPException(status_code=409, detail="Phone number already exists")
        
        phone_number = await phone_service.create_phone_number(phone_data, current_user.id)
        logger.info(f"Phone number {phone_data.number} created by user {current_user.id}")
        return phone_number
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating phone number: {e}")
        raise HTTPException(status_code=500, detail="Failed to create phone number")

@router.get("/numbers/{number_id}", response_model=PhoneNumber)
async def get_phone_number(
    number_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific phone number details"""
    phone_service = PhoneSystemService()
    
    try:
        phone_number = await phone_service.get_phone_number(number_id)
        if not phone_number:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        return phone_number
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting phone number: {e}")
        raise HTTPException(status_code=500, detail="Failed to get phone number")

@router.put("/numbers/{number_id}", response_model=PhoneNumber)
async def update_phone_number(
    number_id: str,
    phone_update: PhoneNumberUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update phone number configuration"""
    phone_service = PhoneSystemService()
    
    try:
        updated_number = await phone_service.update_phone_number(
            number_id, phone_update, current_user.id
        )
        if not updated_number:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        logger.info(f"Phone number {number_id} updated by user {current_user.id}")
        return updated_number
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating phone number: {e}")
        raise HTTPException(status_code=500, detail="Failed to update phone number")

@router.delete("/numbers/{number_id}")
async def delete_phone_number(
    number_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete phone number from system"""
    phone_service = PhoneSystemService()
    
    try:
        # Check if number is in use
        if await phone_service.is_phone_number_in_use(number_id):
            raise HTTPException(
                status_code=409, 
                detail="Cannot delete phone number that is currently in use"
            )
        
        success = await phone_service.delete_phone_number(number_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        logger.info(f"Phone number {number_id} deleted by user {current_user.id}")
        return {"message": "Phone number deleted successfully", "number_id": number_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting phone number: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete phone number")

@router.get("/extensions", response_model=List[Extension])
async def get_extensions(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get list of extensions"""
    phone_service = PhoneSystemService()
    
    try:
        filters = {}
        if status and status != "all":
            filters["status"] = status
        if department and department != "all":
            filters["department"] = department
        
        extensions = await phone_service.get_extensions(filters)
        return extensions
        
    except Exception as e:
        logger.error(f"Error getting extensions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get extensions")

@router.post("/extensions", response_model=Extension)
async def create_extension(
    extension_data: ExtensionCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new extension"""
    phone_service = PhoneSystemService()
    
    try:
        # Check if extension number already exists
        if await phone_service.extension_exists(extension_data.number):
            raise HTTPException(status_code=409, detail="Extension number already exists")
        
        extension = await phone_service.create_extension(extension_data, current_user.id)
        logger.info(f"Extension {extension_data.number} created by user {current_user.id}")
        return extension
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating extension: {e}")
        raise HTTPException(status_code=500, detail="Failed to create extension")

@router.put("/extensions/{extension_id}", response_model=Extension)
async def update_extension(
    extension_id: str,
    extension_update: ExtensionCreate,
    current_user: User = Depends(get_current_user)
):
    """Update extension configuration"""
    phone_service = PhoneSystemService()
    
    try:
        updated_extension = await phone_service.update_extension(
            extension_id, extension_update, current_user.id
        )
        if not updated_extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        return updated_extension
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating extension: {e}")
        raise HTTPException(status_code=500, detail="Failed to update extension")

@router.delete("/extensions/{extension_id}")
async def delete_extension(
    extension_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete extension"""
    phone_service = PhoneSystemService()
    
    try:
        success = await phone_service.delete_extension(extension_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        return {"message": "Extension deleted successfully", "extension_id": extension_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting extension: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete extension")

@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    current_user: User = Depends(get_current_user)
):
    """Get phone system status"""
    phone_service = PhoneSystemService()
    
    try:
        status = await phone_service.get_system_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@router.get("/capacity", response_model=CapacityMetrics)
async def get_capacity_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get phone system capacity metrics"""
    phone_service = PhoneSystemService()
    
    try:
        metrics = await phone_service.get_capacity_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting capacity metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get capacity metrics")

@router.post("/test/{number_id}")
async def test_phone_number(
    number_id: str,
    test_type: str = Query("connectivity", regex="^(connectivity|audio|full)$"),
    current_user: User = Depends(get_current_user)
):
    """Test phone number functionality"""
    phone_service = PhoneSystemService()
    
    try:
        result = await phone_service.test_phone_number(number_id, test_type)
        if not result:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing phone number: {e}")
        raise HTTPException(status_code=500, detail="Failed to test phone number")

@router.post("/assign")
async def assign_phone_number(
    number_id: str,
    assignment_type: str = Query(..., regex="^(agent|department|queue|ivr)$"),
    assignment_id: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """Assign phone number to agent, department, queue, or IVR"""
    phone_service = PhoneSystemService()
    
    try:
        success = await phone_service.assign_phone_number(
            number_id, assignment_type, assignment_id, current_user.id
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to assign phone number")
        
        return {
            "message": "Phone number assigned successfully",
            "number_id": number_id,
            "assignment_type": assignment_type,
            "assignment_id": assignment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning phone number: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign phone number")
