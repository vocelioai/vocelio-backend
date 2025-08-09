# apps/smart-campaigns/src/api/v1/endpoints/campaigns.py
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from services.campaign_service import CampaignService
from schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse,
    CampaignFilter, CampaignAction, CampaignOptimization, CampaignBulkAction,
    CampaignSearch, CampaignAnalytics
)
from shared.auth.dependencies import get_current_user, get_organization_id
from shared.database.client import get_database
from shared.schemas.response import APIResponse, ErrorResponse
from shared.exceptions.service import ServiceException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=APIResponse[CampaignResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new campaign",
    description="Create a new AI-powered calling campaign"
)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Create a new campaign"""
    try:
        service = CampaignService(db)
        campaign = await service.create_campaign(campaign_data, user_id, organization_id)
        
        # Schedule AI optimization in background
        background_tasks.add_task(
            _schedule_ai_optimization, 
            campaign.id, user_id, organization_id
        )
        
        return APIResponse(
            data=campaign,
            message="Campaign created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign"
        )

@router.get(
    "/",
    response_model=APIResponse[CampaignListResponse],
    summary="List campaigns",
    description="Get a paginated list of campaigns with optional filtering"
)
async def list_campaigns(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    priority: Optional[List[str]] = Query(None, description="Filter by priority"),
    industry: Optional[List[str]] = Query(None, description="Filter by industry"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """List campaigns with filtering and pagination"""
    try:
        # Build filters
        filters = CampaignFilter(
            status=status,
            priority=priority,
            industry=industry,
            agent_id=agent_id
        )
        
        service = CampaignService(db)
        campaigns, total = await service.list_campaigns(
            user_id, organization_id, filters, page, per_page, sort_by, sort_order
        )
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        response_data = CampaignListResponse(
            campaigns=campaigns,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return APIResponse(
            data=response_data,
            message=f"Retrieved {len(campaigns)} campaigns",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error listing campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaigns"
        )

@router.get(
    "/{campaign_id}",
    response_model=APIResponse[CampaignResponse],
    summary="Get campaign details",
    description="Get detailed information about a specific campaign"
)
async def get_campaign(
    campaign_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get campaign by ID"""
    try:
        service = CampaignService(db)
        campaign = await service.get_campaign(campaign_id, user_id, organization_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return APIResponse(
            data=campaign,
            message="Campaign retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaign"
        )

@router.put(
    "/{campaign_id}",
    response_model=APIResponse[CampaignResponse],
    summary="Update campaign",
    description="Update an existing campaign"
)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Update campaign"""
    try:
        service = CampaignService(db)
        campaign = await service.update_campaign(campaign_id, campaign_data, user_id, organization_id)
        
        return APIResponse(
            data=campaign,
            message="Campaign updated successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error updating campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error updating campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campaign"
        )

@router.delete(
    "/{campaign_id}",
    response_model=APIResponse[Dict[str, str]],
    summary="Delete campaign",
    description="Delete a campaign and all associated data"
)
async def delete_campaign(
    campaign_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Delete campaign"""
    try:
        service = CampaignService(db)
        success = await service.delete_campaign(campaign_id, user_id, organization_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return APIResponse(
            data={"campaign_id": campaign_id, "status": "deleted"},
            message="Campaign deleted successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error deleting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error deleting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign"
        )

@router.post(
    "/{campaign_id}/actions",
    response_model=APIResponse[CampaignResponse],
    summary="Execute campaign action",
    description="Execute actions like start, pause, resume, stop, or cancel on a campaign"
)
async def execute_campaign_action(
    campaign_id: str,
    action: CampaignAction,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Execute campaign action"""
    try:
        service = CampaignService(db)
        campaign = await service.execute_campaign_action(campaign_id, action, user_id, organization_id)
        
        # Schedule background tasks based on action
        if action.action == "start":
            background_tasks.add_task(
                _notify_campaign_started,
                campaign_id, user_id, organization_id
            )
        
        return APIResponse(
            data=campaign,
            message=f"Campaign action '{action.action}' executed successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error executing action on campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error executing action on campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute campaign action"
        )

@router.post(
    "/bulk-actions",
    response_model=APIResponse[Dict[str, Any]],
    summary="Execute bulk campaign actions",
    description="Execute actions on multiple campaigns at once"
)
async def execute_bulk_campaign_action(
    bulk_action: CampaignBulkAction,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Execute bulk campaign actions"""
    try:
        service = CampaignService(db)
        results = {
            "action": bulk_action.action,
            "total_campaigns": len(bulk_action.campaign_ids),
            "successful": [],
            "failed": []
        }
        
        for campaign_id in bulk_action.campaign_ids:
            try:
                action = CampaignAction(action=bulk_action.action, reason=bulk_action.reason)
                await service.execute_campaign_action(campaign_id, action, user_id, organization_id)
                results["successful"].append(campaign_id)
            except Exception as e:
                results["failed"].append({
                    "campaign_id": campaign_id,
                    "error": str(e)
                })
        
        return APIResponse(
            data=results,
            message=f"Bulk action executed on {len(results['successful'])} campaigns",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error executing bulk action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute bulk action"
        )

@router.post(
    "/{campaign_id}/optimize",
    response_model=APIResponse[CampaignResponse],
    summary="Optimize campaign with AI",
    description="Use AI to optimize campaign performance"
)
async def optimize_campaign(
    campaign_id: str,
    optimization: CampaignOptimization,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Optimize campaign using AI"""
    try:
        service = CampaignService(db)
        campaign = await service.optimize_campaign(campaign_id, optimization, user_id, organization_id)
        
        return APIResponse(
            data=campaign,
            message="Campaign optimized successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error optimizing campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error optimizing campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize campaign"
        )

@router.get(
    "/{campaign_id}/analytics",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get campaign analytics",
    description="Get detailed analytics and performance metrics for a campaign"
)
async def get_campaign_analytics(
    campaign_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get campaign analytics"""
    try:
        service = CampaignService(db)
        analytics = await service.get_campaign_analytics(campaign_id, user_id, organization_id, days)
        
        return APIResponse(
            data=analytics,
            message="Campaign analytics retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ValidationException as e:
        logger.warning(f"Validation error getting analytics for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error getting analytics for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )

@router.post(
    "/search",
    response_model=APIResponse[CampaignListResponse],
    summary="Search campaigns",
    description="Search campaigns with advanced filtering and sorting"
)
async def search_campaigns(
    search_params: CampaignSearch,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Search campaigns"""
    try:
        service = CampaignService(db)
        campaigns, total = await service.search_campaigns(
            search_params, user_id, organization_id
        )
        
        # Calculate pagination info
        total_pages = (total + search_params.per_page - 1) // search_params.per_page
        has_next = search_params.page < total_pages
        has_prev = search_params.page > 1
        
        response_data = CampaignListResponse(
            campaigns=campaigns,
            total=total,
            page=search_params.page,
            per_page=search_params.per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return APIResponse(
            data=response_data,
            message=f"Found {len(campaigns)} campaigns matching search criteria",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error searching campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search campaigns"
        )

@router.get(
    "/{campaign_id}/export",
    summary="Export campaign data",
    description="Export campaign data in various formats"
)
async def export_campaign_data(
    campaign_id: str,
    format: str = Query("csv", regex="^(csv|xlsx|json)$", description="Export format"),
    include_prospects: bool = Query(True, description="Include prospect data"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Export campaign data"""
    try:
        service = CampaignService(db)
        export_data = await service.export_campaign_data(
            campaign_id, user_id, organization_id, format, include_prospects
        )
        
        # Return appropriate response based on format
        if format == "json":
            return JSONResponse(
                content=export_data,
                headers={"Content-Disposition": f"attachment; filename=campaign_{campaign_id}.json"}
            )
        else:
            # For CSV/XLSX, return file content
            return Response(
                content=export_data,
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename=campaign_{campaign_id}.{format}"}
            )
        
    except ValidationException as e:
        logger.warning(f"Validation error exporting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ServiceException as e:
        logger.error(f"Service error exporting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export campaign data"
        )

# Background task functions
async def _schedule_ai_optimization(campaign_id: str, user_id: str, organization_id: str):
    """Schedule AI optimization for new campaign"""
    try:
        # This would typically schedule optimization after some initial data is collected
        logger.info(f"Scheduled AI optimization for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Error scheduling AI optimization: {str(e)}")

async def _notify_campaign_started(campaign_id: str, user_id: str, organization_id: str):
    """Notify relevant services that campaign has started"""
    try:
        # Notify analytics service, monitoring, etc.
        logger.info(f"Campaign {campaign_id} started, notifications sent")
    except Exception as e:
        logger.error(f"Error sending campaign start notifications: {str(e)}")