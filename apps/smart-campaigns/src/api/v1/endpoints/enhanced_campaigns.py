# apps/smart-campaigns/src/api/v1/endpoints/enhanced_campaigns.py
"""
Enhanced Campaign Endpoints - Unified API combining smart-campaigns + smart-campaigns-service
Provides comprehensive campaign management with AI optimization features
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from services.enhanced_campaign_service import EnhancedCampaignService
from schemas.enhanced_campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse,
    CampaignFilter, OptimizationRequest, OptimizationResponse,
    ABTestRequest, ABTestResponse, CampaignAnalytics, CampaignPerformance,
    CampaignBulkAction, CampaignBulkResult, CampaignStatus, CampaignType,
    IndustryType, CampaignTemplateResponse
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
    summary="Create a new enhanced campaign",
    description="Create a new AI-powered campaign with optimization features"
)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Create a new enhanced campaign"""
    try:
        service = EnhancedCampaignService(db)
        campaign = await service.create_campaign(campaign_data, user_id, organization_id)
        
        # Schedule AI optimization in background if enabled
        if campaign_data.is_ai_optimized:
            background_tasks.add_task(
                _schedule_ai_optimization,
                campaign.id, service
            )
        
        return APIResponse(
            data=campaign,
            message="Enhanced campaign created successfully",
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
    summary="List enhanced campaigns",
    description="Get a paginated list of campaigns with advanced filtering and AI optimization status"
)
async def list_campaigns(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    status: Optional[List[CampaignStatus]] = Query(None, description="Filter by status"),
    priority: Optional[List[str]] = Query(None, description="Filter by priority"),
    industry: Optional[List[IndustryType]] = Query(None, description="Filter by industry"),
    campaign_type: Optional[List[CampaignType]] = Query(None, description="Filter by campaign type"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    is_ai_optimized: Optional[bool] = Query(None, description="Filter by AI optimization status"),
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """List enhanced campaigns with filtering and pagination"""
    try:
        # Build filters
        filters = CampaignFilter(
            status=status,
            priority=priority,
            industry=industry,
            campaign_type=campaign_type,
            agent_id=agent_id,
            is_ai_optimized=is_ai_optimized
        )
        
        service = EnhancedCampaignService(db)
        campaigns, total = await service.list_campaigns(
            user_id, organization_id, filters, page, per_page, sort_by, sort_order
        )
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        
        response_data = CampaignListResponse(
            campaigns=campaigns,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
        return APIResponse(
            data=response_data,
            message=f"Found {total} campaigns",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error listing campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list campaigns"
        )

@router.get(
    "/{campaign_id}",
    response_model=APIResponse[CampaignResponse],
    summary="Get campaign details",
    description="Get detailed information about a specific campaign including AI optimization data"
)
async def get_campaign(
    campaign_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get a specific campaign"""
    try:
        service = EnhancedCampaignService(db)
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
            detail="Failed to get campaign"
        )

@router.put(
    "/{campaign_id}",
    response_model=APIResponse[CampaignResponse],
    summary="Update campaign",
    description="Update an existing campaign with AI optimization support"
)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Update an existing campaign"""
    try:
        service = EnhancedCampaignService(db)
        campaign = await service.update_campaign(campaign_id, campaign_data, user_id, organization_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Trigger AI optimization if optimization settings changed
        if campaign_data.is_ai_optimized is not None and campaign_data.is_ai_optimized:
            background_tasks.add_task(
                _trigger_optimization,
                campaign_id, service
            )
        
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
    """Delete a campaign"""
    try:
        service = EnhancedCampaignService(db)
        success = await service.delete_campaign(campaign_id, user_id, organization_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return APIResponse(
            data={"message": "Campaign deleted successfully"},
            message="Campaign deleted successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error deleting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign"
        )

# AI Optimization Endpoints (from smart-campaigns-service)
@router.post(
    "/{campaign_id}/optimize",
    response_model=APIResponse[OptimizationResponse],
    summary="Optimize campaign with AI",
    description="Trigger AI optimization for improved campaign performance"
)
async def optimize_campaign(
    campaign_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Trigger AI optimization for a specific campaign"""
    try:
        service = EnhancedCampaignService(db)
        result = await service.optimize_campaign(campaign_id)
        
        return APIResponse(
            data=result,
            message="Campaign optimization completed",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Optimization error for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/{campaign_id}/ab-test",
    response_model=APIResponse[ABTestResponse],
    summary="Create A/B test",
    description="Create A/B test for campaign optimization"
)
async def create_ab_test(
    campaign_id: str,
    ab_test_data: ABTestRequest,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Create A/B test for campaign optimization"""
    try:
        ab_test_data.campaign_id = campaign_id
        service = EnhancedCampaignService(db)
        result = await service.create_ab_test(ab_test_data)
        
        return APIResponse(
            data=result,
            message="A/B test created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except ServiceException as e:
        logger.error(f"A/B test creation error for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{campaign_id}/performance",
    response_model=APIResponse[CampaignPerformance],
    summary="Get campaign performance",
    description="Get detailed performance metrics for a campaign"
)
async def get_campaign_performance(
    campaign_id: str,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get detailed performance metrics for a campaign"""
    try:
        service = EnhancedCampaignService(db)
        performance = await service.get_campaign_performance(campaign_id)
        
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return APIResponse(
            data=performance,
            message="Performance metrics retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Performance retrieval error for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics"
        )

# Analytics Endpoints
@router.get(
    "/analytics/overview",
    response_model=APIResponse[CampaignAnalytics],
    summary="Get campaign analytics",
    description="Get comprehensive campaign analytics and insights"
)
async def get_analytics(
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get comprehensive campaign analytics"""
    try:
        service = EnhancedCampaignService(db)
        analytics = await service.get_analytics(organization_id)
        
        return APIResponse(
            data=analytics,
            message="Analytics retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics"
        )

# Industry and Type Endpoints (from smart-campaigns-service)
@router.get(
    "/industries/{industry}/campaigns",
    response_model=APIResponse[List[CampaignResponse]],
    summary="Get campaigns by industry",
    description="Get all campaigns for a specific industry"
)
async def get_industry_campaigns(
    industry: IndustryType,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get all campaigns for a specific industry"""
    try:
        filters = CampaignFilter(industry=[industry])
        service = EnhancedCampaignService(db)
        campaigns, _ = await service.list_campaigns(
            user_id, organization_id, filters, 1, 1000
        )
        
        return APIResponse(
            data=campaigns,
            message=f"Found {len(campaigns)} campaigns for {industry.value}",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Industry campaigns error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get industry campaigns"
        )

@router.get(
    "/types",
    response_model=APIResponse[List[str]],
    summary="Get campaign types",
    description="Get all available campaign types"
)
async def get_campaign_types():
    """Get available campaign types"""
    return APIResponse(
        data=[campaign_type.value for campaign_type in CampaignType],
        message="Campaign types retrieved successfully",
        status_code=status.HTTP_200_OK
    )

@router.get(
    "/types/{campaign_type}/campaigns",
    response_model=APIResponse[List[CampaignResponse]],
    summary="Get campaigns by type",
    description="Get all campaigns of a specific type"
)
async def get_type_campaigns(
    campaign_type: CampaignType,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Get all campaigns of a specific type"""
    try:
        filters = CampaignFilter(campaign_type=[campaign_type])
        service = EnhancedCampaignService(db)
        campaigns, _ = await service.list_campaigns(
            user_id, organization_id, filters, 1, 1000
        )
        
        return APIResponse(
            data=campaigns,
            message=f"Found {len(campaigns)} {campaign_type.value} campaigns",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Type campaigns error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get type campaigns"
        )

# Bulk Operations (from smart-campaigns-service)
@router.post(
    "/batch/start",
    response_model=APIResponse[CampaignBulkResult],
    summary="Start multiple campaigns",
    description="Start multiple campaigns at once"
)
async def batch_start_campaigns(
    action_data: CampaignBulkAction,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Start multiple campaigns at once"""
    try:
        service = EnhancedCampaignService(db)
        results = []
        
        for campaign_id in action_data.campaign_ids:
            try:
                result = await service.update_campaign(
                    campaign_id,
                    CampaignUpdate(status=CampaignStatus.ACTIVE),
                    user_id,
                    organization_id
                )
                results.append({
                    "campaign_id": campaign_id,
                    "success": result is not None,
                    "status": "started" if result else "failed"
                })
            except Exception as e:
                results.append({
                    "campaign_id": campaign_id,
                    "success": False,
                    "status": "failed",
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        bulk_result = CampaignBulkResult(
            total_processed=len(action_data.campaign_ids),
            successful=successful,
            failed=failed,
            results=results,
            errors=[r for r in results if not r["success"]]
        )
        
        return APIResponse(
            data=bulk_result,
            message=f"Bulk start completed: {successful} successful, {failed} failed",
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Bulk start error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk operation failed"
        )

@router.post(
    "/batch/pause",
    response_model=APIResponse[CampaignBulkResult],
    summary="Pause multiple campaigns",
    description="Pause multiple campaigns at once"
)
async def batch_pause_campaigns(
    action_data: CampaignBulkAction,
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_database)
):
    """Pause multiple campaigns at once"""
    try:
        service = EnhancedCampaignService(db)
        results = []
        
        for campaign_id in action_data.campaign_ids:
            try:
                result = await service.update_campaign(
                    campaign_id,
                    CampaignUpdate(status=CampaignStatus.PAUSED),
                    user_id,
                    organization_id
                )
                results.append({
                    "campaign_id": campaign_id,
                    "success": result is not None,
                    "status": "paused" if result else "failed"
                })
            except Exception as e:
                results.append({
                    "campaign_id": campaign_id,
                    "success": False,
                    "status": "failed",
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        bulk_result = CampaignBulkResult(
            total_processed=len(action_data.campaign_ids),
            successful=successful,
            failed=failed,
            results=results,
            errors=[r for r in results if not r["success"]]
        )
        
        return APIResponse(
            data=bulk_result,
            message=f"Bulk pause completed: {successful} successful, {failed} failed",
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Bulk pause error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk operation failed"
        )

# Background task functions
async def _schedule_ai_optimization(campaign_id: str, service: EnhancedCampaignService):
    """Background task to schedule AI optimization"""
    try:
        await asyncio.sleep(5)  # Wait a bit for campaign to be fully created
        await service.optimize_campaign(campaign_id)
        logger.info(f"Completed background AI optimization for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Background optimization failed for campaign {campaign_id}: {str(e)}")

async def _trigger_optimization(campaign_id: str, service: EnhancedCampaignService):
    """Background task to trigger optimization after updates"""
    try:
        await service.optimize_campaign(campaign_id)
        logger.info(f"Completed optimization trigger for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Optimization trigger failed for campaign {campaign_id}: {str(e)}")
