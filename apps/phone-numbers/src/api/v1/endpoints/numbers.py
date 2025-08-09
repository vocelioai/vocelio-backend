# apps/phone-numbers/src/api/v1/endpoints/numbers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from shared.database.client import get_db
from shared.auth.dependencies import get_current_user, get_organization_id
from schemas.phone_number import (
    PhoneNumberResponse, PhoneNumberCreate, PhoneNumberUpdate,
    PhoneNumberListResponse, UsageStatsRequest, UsageStatsResponse,
    BulkNumberUpdate, BulkNumberResponse
)
from services.number_service import NumberService
from shared.exceptions.service import ServiceException, NotFoundError

router = APIRouter()


@router.get(
    "/",
    response_model=PhoneNumberListResponse,
    summary="Get Phone Numbers",
    description="Get all phone numbers for the organization with filtering and pagination"
)
async def get_phone_numbers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    number_type: Optional[str] = Query(None, description="Filter by number type"),
    search: Optional[str] = Query(None, description="Search in number, name, or location"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Get phone numbers with advanced filtering and pagination.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **status**: Filter by number status (active, inactive, released)
    - **number_type**: Filter by type (local, toll_free, mobile)
    - **search**: Search in phone number, friendly name, or location
    """
    try:
        service = NumberService(db)
        result = await service.get_numbers(
            organization_id=organization_id,
            user_id=current_user["id"],
            skip=skip,
            limit=limit,
            status=status,
            number_type=number_type,
            search=search
        )
        return result
        
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/{number_id}",
    response_model=PhoneNumberResponse,
    summary="Get Phone Number",
    description="Get detailed information about a specific phone number"
)
async def get_phone_number(
    number_id: str = Path(..., description="Phone number ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Get detailed information about a specific phone number.
    
    - **number_id**: Unique identifier of the phone number
    """
    try:
        service = NumberService(db)
        return await service.get_number(number_id, organization_id)
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{number_id}",
    response_model=PhoneNumberResponse,
    summary="Update Phone Number",
    description="Update phone number configuration and settings"
)
async def update_phone_number(
    number_id: str = Path(..., description="Phone number ID"),
    update_data: PhoneNumberUpdate = ...,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Update phone number configuration.
    
    - **number_id**: Unique identifier of the phone number
    - **update_data**: Fields to update
    """
    try:
        service = NumberService(db)
        return await service.update_number(number_id, organization_id, update_data)
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{number_id}",
    summary="Release Phone Number",
    description="Release a phone number and cancel billing"
)
async def release_phone_number(
    number_id: str = Path(..., description="Phone number ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Release a phone number from your account.
    
    - **number_id**: Unique identifier of the phone number
    
    **Warning**: This action cannot be undone. The number will be released back to Twilio's inventory.
    """
    try:
        service = NumberService(db)
        result = await service.release_number(number_id, organization_id)
        return result
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{number_id}/usage",
    response_model=UsageStatsResponse,
    summary="Get Number Usage Stats",
    description="Get detailed usage statistics for a phone number"
)
async def get_number_usage(
    number_id: str = Path(..., description="Phone number ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: Optional[str] = Query("day", regex=r"^(day|week|month)$", description="Group by period"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Get usage statistics for a specific phone number.
    
    - **number_id**: Unique identifier of the phone number
    - **start_date**: Start date for statistics (defaults to 30 days ago)
    - **end_date**: End date for statistics (defaults to today)
    - **group_by**: How to group the data (day, week, month)
    """
    try:
        from datetime import datetime, timedelta
        
        # Parse dates
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        else:
            start_dt = datetime.utcnow() - timedelta(days=30)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.utcnow()
        
        service = NumberService(db)
        stats_request = UsageStatsRequest(
            phone_number_ids=[number_id],
            start_date=start_dt,
            end_date=end_dt,
            group_by=group_by
        )
        
        usage_stats = await service.get_usage_stats(organization_id, stats_request)
        
        # Calculate summary
        summary = {
            "total_calls": sum(stat.total_calls for stat in usage_stats),
            "total_minutes": sum(stat.total_minutes for stat in usage_stats),
            "total_sms": sum(stat.total_sms for stat in usage_stats),
            "total_costs": sum(stat.total_costs for stat in usage_stats),
            "average_daily_calls": sum(stat.total_calls for stat in usage_stats) / max(len(usage_stats), 1)
        }
        
        return UsageStatsResponse(
            usage_stats=usage_stats,
            summary=summary,
            period_start=start_dt,
            period_end=end_dt
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date format: {str(e)}")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/bulk-update",
    response_model=BulkNumberResponse,
    summary="Bulk Update Numbers",
    description="Update multiple phone numbers at once"
)
async def bulk_update_numbers(
    bulk_update: BulkNumberUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Update multiple phone numbers with the same changes.
    
    - **phone_number_ids**: List of phone number IDs to update
    - **updates**: The updates to apply to all numbers
    """
    try:
        service = NumberService(db)
        
        successful_ids = []
        failed_ids = []
        errors = {}
        
        for number_id in bulk_update.phone_number_ids:
            try:
                await service.update_number(number_id, organization_id, bulk_update.updates)
                successful_ids.append(number_id)
            except Exception as e:
                failed_ids.append(number_id)
                errors[number_id] = str(e)
        
        return BulkNumberResponse(
            success_count=len(successful_ids),
            failed_count=len(failed_ids),
            successful_ids=successful_ids,
            failed_ids=failed_ids,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/analytics/summary",
    summary="Get Numbers Analytics Summary",
    description="Get analytics summary for all phone numbers"
)
async def get_numbers_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """
    Get analytics summary for all phone numbers in the organization.
    
    - **days**: Number of days to include in the analysis
    """
    try:
        service = NumberService(db)
        
        # Get all numbers for organization
        numbers_result = await service.get_numbers(
            organization_id=organization_id,
            user_id=current_user["id"],
            limit=1000  # Get all numbers
        )
        
        # Calculate summary analytics
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        stats_request = UsageStatsRequest(
            start_date=start_date,
            end_date=end_date
        )
        
        usage_stats = await service.get_usage_stats(organization_id, stats_request)
        
        # Aggregate statistics
        total_numbers = len(numbers_result["numbers"])
        active_numbers = len([n for n in numbers_result["numbers"] if n.status == "active"])
        total_calls = sum(stat.total_calls for stat in usage_stats)
        total_minutes = sum(stat.total_minutes for stat in usage_stats)
        total_sms = sum(stat.total_sms for stat in usage_stats)
        total_costs = sum(stat.total_costs for stat in usage_stats)
        
        # Calculate monthly costs
        monthly_costs = sum(number.monthly_price for number in numbers_result["numbers"] if number.status == "active")
        
        return {
            "summary": {
                "total_numbers": total_numbers,
                "active_numbers": active_numbers,
                "inactive_numbers": total_numbers - active_numbers,
                "monthly_base_cost": round(monthly_costs, 2),
                "usage_period_days": days
            },
            "usage": {
                "total_calls": total_calls,
                "total_minutes": round(total_minutes, 2),
                "total_sms": total_sms,
                "total_usage_costs": round(total_costs, 2),
                "average_calls_per_day": round(total_calls / max(days, 1), 1),
                "average_minutes_per_call": round(total_minutes / max(total_calls, 1), 2)
            },
            "performance": {
                "numbers_with_usage": len([s for s in usage_stats if s.total_calls > 0]),
                "most_active_number": max(usage_stats, key=lambda x: x.total_calls).phone_number if usage_stats else None,
                "cost_per_call": round(total_costs / max(total_calls, 1), 4) if total_calls > 0 else 0
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            }
        }
        
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")