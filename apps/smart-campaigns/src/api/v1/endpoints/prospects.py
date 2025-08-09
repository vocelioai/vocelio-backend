# apps/smart-campaigns/src/api/v1/endpoints/prospects.py
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
import io

from services.prospect_service import ProspectService
from schemas.prospect import (
    ProspectCreate, ProspectUpdate, ProspectResponse, ProspectListResponse,
    ProspectFilter, ProspectBulkCreate, ProspectCallUpdate, ProspectAction,
    ProspectSearch, ProspectImport, ProspectExport
)
from shared.auth.dependencies import get_current_user, get_organization_id
from shared.database.client import get_database
from shared.schemas.response import APIResponse, ErrorResponse
from shared.exceptions.service import ServiceException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=APIResponse[ProspectResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new prospect",
    description="Add a new prospect to a campaign"
)
async def create_prospect(
    prospect_data: ProspectCreate,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Create a new prospect"""
    try:
        service = ProspectService(db)
        prospect = await service.create_prospect(prospect_data, user_id, organization_id)
        
        return APIResponse(
            data=prospect,
            message="Prospect created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error creating prospect: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error creating prospect: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prospect"
        )

@router.post(
    "/bulk",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple prospects",
    description="Bulk create prospects for a campaign"
)
async def bulk_create_prospects(
    bulk_data: ProspectBulkCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Bulk create prospects"""
    try:
        service = ProspectService(db)
        result = await service.bulk_create_prospects(bulk_data, user_id, organization_id)
        
        # Schedule AI analysis of new prospects
        if result["created"] > 0:
            background_tasks.add_task(
                _analyze_new_prospects,
                bulk_data.campaign_id,
                result["created_prospect_ids"]
            )
        
        return APIResponse(
            data=result,
            message=f"Bulk operation completed: {result['created']} created, {result['failed']} failed",
            status_code=status.HTTP_201_CREATED
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error in bulk create: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error in bulk create: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk create prospects"
        )

@router.get(
    "/campaign/{campaign_id}",
    response_model=APIResponse[ProspectListResponse],
    summary="List prospects in campaign",
    description="Get a paginated list of prospects in a specific campaign"
)
async def list_prospects(
    campaign_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    priority: Optional[List[str]] = Query(None, description="Filter by priority"),
    converted: Optional[bool] = Query(None, description="Filter by conversion status"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """List prospects with filtering and pagination"""
    try:
        # Build filters
        filters = ProspectFilter(
            status=status,
            priority=priority,
            converted=converted
        )
        
        service = ProspectService(db)
        prospects, total = await service.list_prospects(
            campaign_id, user_id, organization_id, filters, page, per_page, sort_by, sort_order
        )
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        response_data = ProspectListResponse(
            prospects=prospects,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return APIResponse(
            data=response_data,
            message=f"Retrieved {len(prospects)} prospects",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error listing prospects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prospects"
        )

@router.get(
    "/{prospect_id}",
    response_model=APIResponse[ProspectResponse],
    summary="Get prospect details",
    description="Get detailed information about a specific prospect"
)
async def get_prospect(
    prospect_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get prospect by ID"""
    try:
        service = ProspectService(db)
        prospect = await service.get_prospect(prospect_id, user_id, organization_id)
        
        if not prospect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prospect not found"
            )
        
        return APIResponse(
            data=prospect,
            message="Prospect retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting prospect {prospect_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prospect"
        )

@router.put(
    "/{prospect_id}",
    response_model=APIResponse[ProspectResponse],
    summary="Update prospect",
    description="Update an existing prospect"
)
async def update_prospect(
    prospect_id: str,
    prospect_data: ProspectUpdate,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Update prospect"""
    try:
        service = ProspectService(db)
        prospect = await service.update_prospect(prospect_id, prospect_data, user_id, organization_id)
        
        return APIResponse(
            data=prospect,
            message="Prospect updated successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error updating prospect {prospect_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error updating prospect {prospect_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update prospect"
        )

@router.delete(
    "/{prospect_id}",
    response_model=APIResponse[Dict[str, str]],
    summary="Delete prospect",
    description="Delete a prospect from the campaign"
)
async def delete_prospect(
    prospect_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Delete prospect"""
    try:
        service = ProspectService(db)
        success = await service.delete_prospect(prospect_id, user_id, organization_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prospect not found"
            )
        
        return APIResponse(
            data={"prospect_id": prospect_id, "status": "deleted"},
            message="Prospect deleted successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error deleting prospect {prospect_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prospect"
        )

@router.post(
    "/{prospect_id}/call-result",
    response_model=APIResponse[ProspectResponse],
    summary="Update call result",
    description="Update prospect with call outcome and statistics"
)
async def update_call_result(
    prospect_id: str,
    call_update: ProspectCallUpdate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Update prospect after a call"""
    try:
        service = ProspectService(db)
        prospect = await service.update_call_result(prospect_id, call_update, user_id, organization_id)
        
        # Schedule analytics update
        background_tasks.add_task(
            _update_campaign_analytics,
            prospect.campaign_id
        )
        
        return APIResponse(
            data=prospect,
            message="Call result updated successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error updating call result for {prospect_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error updating call result for {prospect_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update call result"
        )

@router.post(
    "/actions",
    response_model=APIResponse[Dict[str, Any]],
    summary="Execute prospect actions",
    description="Execute bulk actions on multiple prospects"
)
async def execute_prospect_action(
    action: ProspectAction,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Execute bulk prospect actions"""
    try:
        service = ProspectService(db)
        result = await service.execute_prospect_action(action, user_id, organization_id)
        
        # Schedule appropriate background tasks
        if action.action == "call" and len(result["successful"]) > 0:
            background_tasks.add_task(
                _schedule_prospect_calls,
                result["successful"],
                action.parameters
            )
        
        return APIResponse(
            data=result,
            message=f"Action executed on {len(result['successful'])} prospects",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error executing prospect action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error executing prospect action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute prospect action"
        )

@router.post(
    "/search",
    response_model=APIResponse[ProspectListResponse],
    summary="Search prospects",
    description="Search prospects with advanced filtering"
)
async def search_prospects(
    search_params: ProspectSearch,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Search prospects"""
    try:
        service = ProspectService(db)
        prospects, total = await service.search_prospects(search_params, user_id, organization_id)
        
        # Calculate pagination info
        total_pages = (total + search_params.per_page - 1) // search_params.per_page
        has_next = search_params.page < total_pages
        has_prev = search_params.page > 1
        
        response_data = ProspectListResponse(
            prospects=prospects,
            total=total,
            page=search_params.page,
            per_page=search_params.per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return APIResponse(
            data=response_data,
            message=f"Found {len(prospects)} prospects matching search criteria",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error searching prospects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search prospects"
        )

@router.post(
    "/import",
    response_model=APIResponse[Dict[str, Any]],
    summary="Import prospects from file",
    description="Import prospects from CSV, Excel, or JSON file"
)
async def import_prospects(
    campaign_id: str,
    file: UploadFile = File(..., description="Prospects file to import"),
    skip_duplicates: bool = Query(True, description="Skip duplicate phone numbers"),
    validate_data: bool = Query(True, description="Validate data before import"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Import prospects from file"""
    try:
        # Validate file type
        allowed_types = ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/json"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Please upload CSV, XLSX, or JSON file."
            )
        
        # Read file content
        content = await file.read()
        
        service = ProspectService(db)
        result = await service.import_prospects_from_file(
            campaign_id, content, file.content_type, skip_duplicates, validate_data, user_id, organization_id
        )
        
        # Schedule post-import analysis
        if result["created"] > 0:
            background_tasks.add_task(
                _analyze_imported_prospects,
                campaign_id,
                result["created_prospect_ids"]
            )
        
        return APIResponse(
            data=result,
            message=f"Import completed: {result['created']} prospects created",
            status_code=status.HTTP_201_CREATED
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error importing prospects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error importing prospects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import prospects"
        )

@router.get(
    "/campaign/{campaign_id}/export",
    summary="Export prospects",
    description="Export prospects from a campaign in various formats"
)
async def export_prospects(
    campaign_id: str,
    format: str = Query("csv", regex="^(csv|xlsx|json)$", description="Export format"),
    include_history: bool = Query(False, description="Include call history"),
    status_filter: Optional[List[str]] = Query(None, description="Filter by status"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Export prospects from campaign"""
    try:
        export_config = ProspectExport(
            format=format,
            include_history=include_history,
            filters={"status": status_filter} if status_filter else None
        )
        
        service = ProspectService(db)
        export_data = await service.export_prospects(
            campaign_id, export_config, user_id, organization_id
        )
        
        # Return appropriate response based on format
        if format == "json":
            return JSONResponse(
                content=export_data,
                headers={"Content-Disposition": f"attachment; filename=prospects_{campaign_id}.json"}
            )
        else:
            # For CSV/XLSX, return file stream
            return StreamingResponse(
                io.BytesIO(export_data),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename=prospects_{campaign_id}.{format}"}
            )
        
    except ValidationException as e:
        logger.warning(f"Validation error exporting prospects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error exporting prospects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export prospects"
        )

@router.get(
    "/{prospect_id}/history",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get prospect call history",
    description="Get detailed call history for a prospect"
)
async def get_prospect_history(
    prospect_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get prospect call history"""
    try:
        service = ProspectService(db)
        history = await service.get_prospect_history(prospect_id, user_id, organization_id, limit)
        
        return APIResponse(
            data=history,
            message="Prospect history retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error getting prospect history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error getting prospect history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prospect history"
        )

@router.post(
    "/{prospect_id}/schedule",
    response_model=APIResponse[ProspectResponse],
    summary="Schedule prospect call",
    description="Schedule a specific time to call this prospect"
)
async def schedule_prospect_call(
    prospect_id: str,
    scheduled_time: str = Query(..., description="ISO formatted datetime string"),
    priority: str = Query("medium", regex="^(low|medium|high|urgent)$", description="Call priority"),
    notes: Optional[str] = Query(None, description="Scheduling notes"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Schedule a call for prospect"""
    try:
        from datetime import datetime
        
        # Parse scheduled time
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
        
        service = ProspectService(db)
        prospect = await service.schedule_prospect_call(
            prospect_id, scheduled_datetime, priority, notes, user_id, organization_id
        )
        
        # Schedule the actual call
        background_tasks.add_task(
            _schedule_single_call,
            prospect_id,
            scheduled_datetime,
            priority
        )
        
        return APIResponse(
            data=prospect,
            message="Prospect call scheduled successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error scheduling prospect call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error scheduling prospect call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule prospect call"
        )

@router.get(
    "/campaign/{campaign_id}/analytics",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get prospect analytics",
    description="Get analytics and insights for prospects in a campaign"
)
async def get_prospect_analytics(
    campaign_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get prospect analytics for campaign"""
    try:
        service = ProspectService(db)
        analytics = await service.get_prospect_analytics(campaign_id, user_id, organization_id, days)
        
        return APIResponse(
            data=analytics,
            message="Prospect analytics retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error getting prospect analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error getting prospect analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prospect analytics"
        )

@router.post(
    "/campaign/{campaign_id}/segment",
    response_model=APIResponse[Dict[str, Any]],
    summary="Create prospect segment",
    description="Create a segment of prospects based on criteria"
)
async def create_prospect_segment(
    campaign_id: str,
    segment_name: str = Query(..., description="Name for the segment"),
    criteria: Dict[str, Any] = Query(..., description="Segmentation criteria"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Create prospect segment"""
    try:
        service = ProspectService(db)
        segment = await service.create_prospect_segment(
            campaign_id, segment_name, criteria, user_id, organization_id
        )
        
        return APIResponse(
            data=segment,
            message="Prospect segment created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error creating prospect segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error creating prospect segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prospect segment"
        )

# Background task functions
async def _analyze_new_prospects(campaign_id: str, prospect_ids: List[str]):
    """Analyze new prospects for AI insights"""
    try:
        # This would typically run AI analysis on new prospects
        logger.info(f"Analyzing {len(prospect_ids)} new prospects for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error analyzing new prospects: {str(e)}")

async def _update_campaign_analytics(campaign_id: str):
    """Update campaign analytics after call results"""
    try:
        # Update campaign-level metrics
        logger.info(f"Updating analytics for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error updating campaign analytics: {str(e)}")

async def _schedule_prospect_calls(prospect_ids: List[str], parameters: Dict[str, Any]):
    """Schedule calls for multiple prospects"""
    try:
        # Integration with call center service
        logger.info(f"Scheduling calls for {len(prospect_ids)} prospects")
    except Exception as e:
        logger.error(f"Error scheduling prospect calls: {str(e)}")

async def _analyze_imported_prospects(campaign_id: str, prospect_ids: List[str]):
    """Analyze imported prospects for data quality and insights"""
    try:
        logger.info(f"Analyzing {len(prospect_ids)} imported prospects for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error analyzing imported prospects: {str(e)}")

async def _schedule_single_call(prospect_id: str, scheduled_time, priority: str):
    """Schedule a single prospect call"""
    try:
        # Integration with call scheduling system
        logger.info(f"Scheduled call for prospect {prospect_id} at {scheduled_time}")
    except Exception as e:
        logger.error(f"Error scheduling single call: {str(e)}")