# apps/phone-numbers/src/services/number_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import logging

from models.phone_number import PhoneNumber, PhoneNumberUsage, PhoneNumberPurchase
from schemas.phone_number import (
    PhoneNumberCreate, PhoneNumberUpdate, PhoneNumberResponse,
    NumberSearchRequest, UsageStatsRequest, UsageStats
)
from services.twilio_service import TwilioService
from services.billing_service import BillingService
from shared.exceptions.service import ServiceException, NotFoundError
from shared.utils.phone_utils import format_phone_number, validate_phone_number

logger = logging.getLogger(__name__)


class NumberService:
    """Phone Number Management Service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.twilio = TwilioService()
        self.billing = BillingService()
    
    async def get_numbers(
        self,
        organization_id: str,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        number_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's phone numbers with filtering and pagination"""
        
        try:
            query = self.db.query(PhoneNumber).filter(
                PhoneNumber.organization_id == organization_id
            )
            
            # Apply filters
            if status:
                query = query.filter(PhoneNumber.status == status)
            
            if number_type:
                query = query.filter(PhoneNumber.number_type == number_type)
            
            if search:
                search_filter = or_(
                    PhoneNumber.phone_number.ilike(f"%{search}%"),
                    PhoneNumber.friendly_name.ilike(f"%{search}%"),
                    PhoneNumber.locality.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            numbers = query.order_by(desc(PhoneNumber.created_at)).offset(skip).limit(limit).all()
            
            # Format response
            return {
                "numbers": [self._format_number_response(num) for num in numbers],
                "total": total,
                "page": (skip // limit) + 1,
                "size": limit,
                "pages": (total + limit - 1) // limit
            }
            
        except Exception as e:
            logger.error(f"Error fetching numbers: {str(e)}")
            raise ServiceException(f"Failed to fetch phone numbers: {str(e)}")
    
    async def get_number(self, number_id: str, organization_id: str) -> PhoneNumberResponse:
        """Get a specific phone number"""
        
        number = self.db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.id == number_id,
                PhoneNumber.organization_id == organization_id
            )
        ).first()
        
        if not number:
            raise NotFoundError(f"Phone number {number_id} not found")
        
        return self._format_number_response(number)
    
    async def update_number(
        self,
        number_id: str,
        organization_id: str,
        update_data: PhoneNumberUpdate
    ) -> PhoneNumberResponse:
        """Update a phone number"""
        
        number = self.db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.id == number_id,
                PhoneNumber.organization_id == organization_id
            )
        ).first()
        
        if not number:
            raise NotFoundError(f"Phone number {number_id} not found")
        
        try:
            # Update database fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(number, field, value)
            
            number.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(number)
            
            # Update Twilio configuration if needed
            if any(field in update_dict for field in ['voice_url', 'sms_url', 'status']):
                await self.twilio.update_number_configuration(
                    number.twilio_sid,
                    voice_url=number.voice_url,
                    sms_url=number.sms_url,
                    status=number.status
                )
            
            logger.info(f"Updated phone number {number_id}")
            return self._format_number_response(number)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating number {number_id}: {str(e)}")
            raise ServiceException(f"Failed to update phone number: {str(e)}")
    
    async def release_number(self, number_id: str, organization_id: str) -> Dict[str, str]:
        """Release a phone number"""
        
        number = self.db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.id == number_id,
                PhoneNumber.organization_id == organization_id
            )
        ).first()
        
        if not number:
            raise NotFoundError(f"Phone number {number_id} not found")
        
        try:
            # Release from Twilio
            await self.twilio.release_number(number.twilio_sid)
            
            # Update database
            number.status = "released"
            number.released_at = datetime.utcnow()
            number.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Cancel billing subscription
            await self.billing.cancel_number_subscription(number_id)
            
            logger.info(f"Released phone number {number.phone_number}")
            return {"message": f"Phone number {number.phone_number} released successfully"}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error releasing number {number_id}: {str(e)}")
            raise ServiceException(f"Failed to release phone number: {str(e)}")
    
    async def get_usage_stats(
        self,
        organization_id: str,
        request: UsageStatsRequest
    ) -> List[UsageStats]:
        """Get usage statistics for phone numbers"""
        
        try:
            # Build query
            query = self.db.query(PhoneNumberUsage).join(PhoneNumber).filter(
                PhoneNumber.organization_id == organization_id
            )
            
            # Apply filters
            if request.phone_number_ids:
                query = query.filter(PhoneNumber.id.in_(request.phone_number_ids))
            
            if request.start_date:
                query = query.filter(PhoneNumberUsage.period_start >= request.start_date)
            
            if request.end_date:
                query = query.filter(PhoneNumberUsage.period_end <= request.end_date)
            
            usage_records = query.all()
            
            # Process and aggregate data
            stats = []
            for record in usage_records:
                avg_duration = (record.total_call_duration / max(record.inbound_calls + record.outbound_calls, 1))
                
                stats.append(UsageStats(
                    phone_number_id=record.phone_number_id,
                    phone_number=record.phone_number.phone_number,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    total_calls=record.inbound_calls + record.outbound_calls,
                    inbound_calls=record.inbound_calls,
                    outbound_calls=record.outbound_calls,
                    total_minutes=record.total_call_duration,
                    average_call_duration=avg_duration,
                    total_sms=record.inbound_sms + record.outbound_sms,
                    inbound_sms=record.inbound_sms,
                    outbound_sms=record.outbound_sms,
                    total_mms=record.inbound_mms + record.outbound_mms,
                    total_costs=record.total_costs,
                    call_costs=record.call_costs,
                    sms_costs=record.sms_costs,
                    mms_costs=record.mms_costs
                ))
            
            return stats
            
        except Exception as e:
            logger.error(f"Error fetching usage stats: {str(e)}")
            raise ServiceException(f"Failed to fetch usage statistics: {str(e)}")
    
    async def update_usage(self, phone_number_id: str, usage_data: Dict[str, Any]) -> None:
        """Update usage statistics for a phone number"""
        
        try:
            number = self.db.query(PhoneNumber).filter(
                PhoneNumber.id == phone_number_id
            ).first()
            
            if not number:
                raise NotFoundError(f"Phone number {phone_number_id} not found")
            
            # Update cumulative counters
            number.total_calls += usage_data.get('calls', 0)
            number.total_minutes += usage_data.get('minutes', 0)
            number.total_sms += usage_data.get('sms', 0)
            number.total_mms += usage_data.get('mms', 0)
            number.last_used_at = datetime.utcnow()
            number.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Updated usage for number {phone_number_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating usage for {phone_number_id}: {str(e)}")
            raise ServiceException(f"Failed to update usage: {str(e)}")
    
    def _format_number_response(self, number: PhoneNumber) -> PhoneNumberResponse:
        """Format phone number for response"""
        return PhoneNumberResponse(
            id=number.id,
            twilio_sid=number.twilio_sid,
            phone_number=number.phone_number,
            formatted_number=number.formatted_number,
            friendly_name=number.friendly_name,
            organization_id=number.organization_id,
            user_id=number.user_id,
            country_code=number.country_code,
            region=number.region,
            locality=number.locality,
            postal_code=number.postal_code,
            number_type=number.number_type,
            capabilities=number.capabilities,
            status=number.status,
            monthly_price=number.monthly_price,
            currency=number.currency,
            total_calls=number.total_calls,
            total_minutes=number.total_minutes,
            total_sms=number.total_sms,
            total_mms=number.total_mms,
            campaign_count=number.campaign_count,
            voice_url=number.voice_url,
            sms_url=number.sms_url,
            tags=number.tags or [],
            notes=number.notes,
            created_at=number.created_at,
            updated_at=number.updated_at,
            last_used_at=number.last_used_at
        )