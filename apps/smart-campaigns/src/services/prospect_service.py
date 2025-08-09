# apps/smart-campaigns/src/services/prospect_service.py
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
import uuid
import csv
import io
import logging

from models.prospect import Prospect
from models.campaign import Campaign
from schemas.prospect import (
    ProspectCreate, ProspectUpdate, ProspectResponse, ProspectFilter,
    ProspectBulkCreate, ProspectCallUpdate, ProspectAction
)
from core.config import get_settings, ProspectStatus
from shared.database.client import get_database
from shared.utils.service_client import ServiceClient
from shared.utils.phone_utils import format_phone_number, validate_phone_number
from shared.exceptions.service import ServiceException, ValidationException

logger = logging.getLogger(__name__)
settings = get_settings()

class ProspectService:
    """Service for managing prospects"""
    
    def __init__(self, db: Session = None):
        self.db = db or get_database()
        self.service_client = ServiceClient()
    
    async def create_prospect(self, prospect_data: ProspectCreate, user_id: str, organization_id: str) -> ProspectResponse:
        """Create a new prospect"""
        try:
            # Validate campaign exists and belongs to user
            campaign = await self._validate_campaign_access(prospect_data.campaign_id, user_id, organization_id)
            
            # Validate and format phone number
            formatted_phone = format_phone_number(prospect_data.phone_number)
            if not validate_phone_number(formatted_phone):
                raise ValidationException("Invalid phone number format")
            
            # Check for duplicates in the same campaign
            existing = self.db.query(Prospect).filter(
                Prospect.campaign_id == prospect_data.campaign_id,
                Prospect.phone_number == formatted_phone
            ).first()
            
            if existing:
                raise ValidationException(f"Prospect with phone number {formatted_phone} already exists in this campaign")
            
            # Build full name
            full_name = self._build_full_name(prospect_data.first_name, prospect_data.last_name)
            
            # Create prospect
            prospect = Prospect(
                id=f"prospect_{uuid.uuid4().hex[:12]}",
                campaign_id=prospect_data.campaign_id,
                first_name=prospect_data.first_name,
                last_name=prospect_data.last_name,
                full_name=full_name,
                email=prospect_data.email,
                phone_number=formatted_phone,
                company=prospect_data.company,
                job_title=prospect_data.job_title,
                industry=prospect_data.industry,
                address_line1=prospect_data.address_line1,
                address_line2=prospect_data.address_line2,
                city=prospect_data.city,
                state=prospect_data.state,
                zip_code=prospect_data.zip_code,
                country=prospect_data.country,
                priority=prospect_data.priority,
                lead_score=prospect_data.lead_score,
                custom_fields=prospect_data.custom_fields,
                tags=prospect_data.tags,
                notes=prospect_data.notes,
                best_time_to_call=prospect_data.best_time_to_call,
                timezone=prospect_data.timezone,
                source=prospect_data.source,
                source_campaign=prospect_data.source_campaign,
                utm_source=prospect_data.utm_source,
                utm_medium=prospect_data.utm_medium,
                utm_campaign=prospect_data.utm_campaign,
                consent_given=prospect_data.consent_given,
                status=ProspectStatus.NEW
            )
            
            self.db.add(prospect)
            
            # Update campaign prospect count
            campaign.total_prospects += 1
            
            await self.db.commit()
            await self.db.refresh(prospect)
            
            logger.info(f"Created prospect {prospect.id} for campaign {prospect_data.campaign_id}")
            return await self._build_prospect_response(prospect)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating prospect: {str(e)}")
            raise ServiceException(f"Failed to create prospect: {str(e)}")
    
    async def bulk_create_prospects(self, bulk_data: ProspectBulkCreate, user_id: str, organization_id: str) -> Dict[str, Any]:
        """Create multiple prospects in bulk"""
        try:
            # Validate campaign
            campaign = await self._validate_campaign_access(bulk_data.campaign_id, user_id, organization_id)
            
            created_prospects = []
            failed_prospects = []
            skipped_duplicates = []
            
            for i, prospect_data in enumerate(bulk_data.prospects):
                try:
                    # Format phone number
                    formatted_phone = format_phone_number(prospect_data.phone_number)
                    
                    # Validate phone if requested
                    if bulk_data.validate_phones and not validate_phone_number(formatted_phone):
                        failed_prospects.append({
                            "index": i,
                            "data": prospect_data.dict(),
                            "error": "Invalid phone number format"
                        })
                        continue
                    
                    # Check for duplicates if requested
                    if bulk_data.skip_duplicates:
                        existing = self.db.query(Prospect).filter(
                            Prospect.campaign_id == bulk_data.campaign_id,
                            Prospect.phone_number == formatted_phone
                        ).first()
                        
                        if existing:
                            skipped_duplicates.append({
                                "index": i,
                                "phone_number": formatted_phone,
                                "existing_id": existing.id
                            })
                            continue
                    
                    # Create prospect
                    full_name = self._build_full_name(prospect_data.first_name, prospect_data.last_name)
                    
                    prospect = Prospect(
                        id=f"prospect_{uuid.uuid4().hex[:12]}",
                        campaign_id=bulk_data.campaign_id,
                        first_name=prospect_data.first_name,
                        last_name=prospect_data.last_name,
                        full_name=full_name,
                        email=prospect_data.email,
                        phone_number=formatted_phone,
                        company=prospect_data.company,
                        job_title=prospect_data.job_title,
                        industry=prospect_data.industry,
                        address_line1=prospect_data.address_line1,
                        address_line2=prospect_data.address_line2,
                        city=prospect_data.city,
                        state=prospect_data.state,
                        zip_code=prospect_data.zip_code,
                        country=prospect_data.country,
                        priority=prospect_data.priority,
                        lead_score=prospect_data.lead_score,
                        custom_fields=prospect_data.custom_fields,
                        tags=prospect_data.tags,
                        notes=prospect_data.notes,
                        best_time_to_call=prospect_data.best_time_to_call,
                        timezone=prospect_data.timezone,
                        source=prospect_data.source or "bulk_import",
                        source_campaign=prospect_data.source_campaign,
                        utm_source=prospect_data.utm_source,
                        utm_medium=prospect_data.utm_medium,
                        utm_campaign=prospect_data.utm_campaign,
                        consent_given=prospect_data.consent_given,
                        status=ProspectStatus.NEW
                    )
                    
                    self.db.add(prospect)
                    created_prospects.append(prospect.id)
                    
                except Exception as e:
                    failed_prospects.append({
                        "index": i,
                        "data": prospect_data.dict(),
                        "error": str(e)
                    })
            
            # Update campaign prospect count
            campaign.total_prospects += len(created_prospects)
            
            await self.db.commit()
            
            result = {
                "campaign_id": bulk_data.campaign_id,
                "total_processed": len(bulk_data.prospects),
                "created": len(created_prospects),
                "failed": len(failed_prospects),
                "skipped_duplicates": len(skipped_duplicates),
                "created_prospect_ids": created_prospects,
                "failed_prospects": failed_prospects,
                "skipped_duplicates": skipped_duplicates
            }
            
            logger.info(f"Bulk created {len(created_prospects)} prospects for campaign {bulk_data.campaign_id}")
            return result
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk create prospects: {str(e)}")
            raise ServiceException(f"Failed to bulk create prospects: {str(e)}")
    
    async def get_prospect(self, prospect_id: str, user_id: str, organization_id: str) -> Optional[ProspectResponse]:
        """Get a single prospect by ID"""
        prospect = await self._get_user_prospect(prospect_id, user_id, organization_id)
        if not prospect:
            return None
        
        return await self._build_prospect_response(prospect)
    
    async def list_prospects(
        self,
        campaign_id: str,
        user_id: str,
        organization_id: str,
        filters: ProspectFilter = None,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[ProspectResponse], int]:
        """List prospects with filtering and pagination"""
        
        # Validate campaign access
        await self._validate_campaign_access(campaign_id, user_id, organization_id)
        
        query = self.db.query(Prospect).filter(Prospect.campaign_id == campaign_id)
        
        # Apply filters
        if filters:
            if filters.status:
                query = query.filter(Prospect.status.in_(filters.status))
            if filters.priority:
                query = query.filter(Prospect.priority.in_(filters.priority))
            if filters.industry:
                query = query.filter(Prospect.industry.in_(filters.industry))
            if filters.company:
                query = query.filter(Prospect.company.ilike(f"%{filters.company}%"))
            if filters.location:
                query = query.filter(
                    or_(
                        Prospect.city.ilike(f"%{filters.location}%"),
                        Prospect.state.ilike(f"%{filters.location}%")
                    )
                )
            if filters.tags:
                for tag in filters.tags:
                    query = query.filter(Prospect.tags.contains([tag]))
            if filters.lead_score_min is not None:
                query = query.filter(Prospect.lead_score >= filters.lead_score_min)
            if filters.lead_score_max is not None:
                query = query.filter(Prospect.lead_score <= filters.lead_score_max)
            if filters.created_after:
                query = query.filter(Prospect.created_at >= filters.created_after)
            if filters.created_before:
                query = query.filter(Prospect.created_at <= filters.created_before)
            if filters.last_contacted_after:
                query = query.filter(Prospect.last_call_date >= filters.last_contacted_after)
            if filters.last_contacted_before:
                query = query.filter(Prospect.last_call_date <= filters.last_contacted_before)
            if filters.converted is not None:
                query = query.filter(Prospect.is_converted == filters.converted)
            if filters.has_consent is not None:
                query = query.filter(Prospect.consent_given == filters.has_consent)
            if filters.dnc_listed is not None:
                query = query.filter(Prospect.dnc_listed == filters.dnc_listed)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Prospect, sort_by, Prospect.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * per_page
        prospects = query.offset(offset).limit(per_page).all()
        
        # Build responses
        prospect_responses = []
        for prospect in prospects:
            response = await self._build_prospect_response(prospect)
            prospect_responses.append(response)
        
        return prospect_responses, total
    
    async def update_prospect(self, prospect_id: str, prospect_data: ProspectUpdate, user_id: str, organization_id: str) -> ProspectResponse:
        """Update an existing prospect"""
        prospect = await self._get_user_prospect(prospect_id, user_id, organization_id)
        if not prospect:
            raise ValidationException("Prospect not found")
        
        try:
            # Update fields
            update_data = prospect_data.dict(exclude_unset=True)
            
            # Handle phone number update
            if 'phone_number' in update_data:
                formatted_phone = format_phone_number(update_data['phone_number'])
                if not validate_phone_number(formatted_phone):
                    raise ValidationException("Invalid phone number format")
                
                # Check for duplicates
                existing = self.db.query(Prospect).filter(
                    Prospect.campaign_id == prospect.campaign_id,
                    Prospect.phone_number == formatted_phone,
                    Prospect.id != prospect.id
                ).first()
                
                if existing:
                    raise ValidationException(f"Phone number {formatted_phone} already exists in this campaign")
                
                update_data['phone_number'] = formatted_phone
            
            # Update full name if first/last name changed
            if 'first_name' in update_data or 'last_name' in update_data:
                first_name = update_data.get('first_name', prospect.first_name)
                last_name = update_data.get('last_name', prospect.last_name)
                update_data['full_name'] = self._build_full_name(first_name, last_name)
            
            for field, value in update_data.items():
                if hasattr(prospect, field):
                    setattr(prospect, field, value)
            
            prospect.updated_at = func.now()
            
            await self.db.commit()
            await self.db.refresh(prospect)
            
            logger.info(f"Updated prospect {prospect_id}")
            return await self._build_prospect_response(prospect)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating prospect {prospect_id}: {str(e)}")
            raise ServiceException(f"Failed to update prospect: {str(e)}")
    
    async def delete_prospect(self, prospect_id: str, user_id: str, organization_id: str) -> bool:
        """Delete a prospect"""
        prospect = await self._get_user_prospect(prospect_id, user_id, organization_id)
        if not prospect:
            return False
        
        try:
            # Update campaign prospect count
            campaign = self.db.query(Campaign).filter(Campaign.id == prospect.campaign_id).first()
            if campaign:
                campaign.total_prospects = max(0, campaign.total_prospects - 1)
            
            await self.db.delete(prospect)
            await self.db.commit()
            
            logger.info(f"Deleted prospect {prospect_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting prospect {prospect_id}: {str(e)}")
            raise ServiceException(f"Failed to delete prospect: {str(e)}")
    
    async def update_call_result(self, prospect_id: str, call_update: ProspectCallUpdate, user_id: str, organization_id: str) -> ProspectResponse:
        """Update prospect after a call"""
        prospect = await self._get_user_prospect(prospect_id, user_id, organization_id)
        if not prospect:
            raise ValidationException("Prospect not found")
        
        try:
            # Update call statistics
            prospect.update_call_stats(call_update.status, call_update.duration, call_update.outcome)
            
            # Update specific fields
            prospect.last_call_id = call_update.call_id
            prospect.status = call_update.status
            
            if call_update.notes:
                if prospect.notes:
                    prospect.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {call_update.notes}"
                else:
                    prospect.notes = call_update.notes
            
            if call_update.next_call_scheduled:
                prospect.next_call_scheduled = call_update.next_call_scheduled
            
            # Handle conversion
            if call_update.converted:
                prospect.mark_converted(call_update.conversion_value, "call_conversion")
            
            prospect.updated_at = func.now()
            
            await self.db.commit()
            await self.db.refresh(prospect)
            
            logger.info(f"Updated call result for prospect {prospect_id}")
            return await self._build_prospect_response(prospect)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating call result for prospect {prospect_id}: {str(e)}")
            raise ServiceException(f"Failed to update call result: {str(e)}")
    
    async def execute_prospect_action(self, action: ProspectAction, user_id: str, organization_id: str) -> Dict[str, Any]:
        """Execute bulk action on prospects"""
        try:
            results = {
                "action": action.action,
                "total_prospects": len(action.prospect_ids),
                "successful": [],
                "failed": []
            }
            
            for prospect_id in action.prospect_ids:
                try:
                    prospect = await self._get_user_prospect(prospect_id, user_id, organization_id)
                    if not prospect:
                        results["failed"].append({
                            "prospect_id": prospect_id,
                            "error": "Prospect not found"
                        })
                        continue
                    
                    if action.action == "call":
                        await self._schedule_call(prospect, action.parameters)
                    elif action.action == "schedule":
                        await self._schedule_prospect(prospect, action.parameters)
                    elif action.action == "convert":
                        await self._convert_prospect(prospect, action.parameters)
                    elif action.action == "opt_out":
                        await self._opt_out_prospect(prospect)
                    elif action.action == "add_note":
                        await self._add_note_to_prospect(prospect, action.parameters.get("note", ""))
                    else:
                        raise ValidationException(f"Unknown action: {action.action}")
                    
                    results["successful"].append(prospect_id)
                    
                except Exception as e:
                    results["failed"].append({
                        "prospect_id": prospect_id,
                        "error": str(e)
                    })
            
            await self.db.commit()
            
            logger.info(f"Executed action '{action.action}' on {len(results['successful'])} prospects")
            return results
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error executing prospect action: {str(e)}")
            raise ServiceException(f"Failed to execute prospect action: {str(e)}")
    
    # Private helper methods
    async def _validate_campaign_access(self, campaign_id: str, user_id: str, organization_id: str) -> Campaign:
        """Validate that user has access to campaign"""
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
            Campaign.organization_id == organization_id
        ).first()
        
        if not campaign:
            raise ValidationException("Campaign not found or access denied")
        
        return campaign
    
    async def _get_user_prospect(self, prospect_id: str, user_id: str, organization_id: str) -> Optional[Prospect]:
        """Get prospect that belongs to user's campaign"""
        return self.db.query(Prospect).join(Campaign).filter(
            Prospect.id == prospect_id,
            Campaign.user_id == user_id,
            Campaign.organization_id == organization_id
        ).first()
    
    def _build_full_name(self, first_name: Optional[str], last_name: Optional[str]) -> str:
        """Build full name from first and last name"""
        parts = []
        if first_name:
            parts.append(first_name.strip())
        if last_name:
            parts.append(last_name.strip())
        return " ".join(parts) if parts else ""
    
    async def _build_prospect_response(self, prospect: Prospect) -> ProspectResponse:
        """Build prospect response with metrics"""
        # Calculate metrics
        from schemas.prospect import ProspectMetrics, ProspectAIPrediction
        
        metrics = ProspectMetrics(
            total_calls=prospect.total_calls,
            successful_calls=prospect.successful_calls,
            failed_calls=prospect.failed_calls,
            no_answer_count=prospect.no_answer_count,
            busy_count=prospect.busy_count,
            voicemail_count=prospect.voicemail_count,
            success_rate=prospect.success_rate,
            answer_rate=prospect.answer_rate,
            email_opens=prospect.email_opens,
            email_clicks=prospect.email_clicks,
            website_visits=prospect.website_visits
        )
        
        # AI predictions (if available)
        ai_predictions = None
        if prospect.ai_prediction_score is not None:
            ai_predictions = ProspectAIPrediction(
                prediction_score=prospect.ai_prediction_score,
                predicted_outcome=prospect.predicted_outcome,
                optimal_call_time=prospect.optimal_call_time,
                confidence=90.0  # Placeholder
            )
        
        # Build response
        response_data = prospect.to_dict()
        response_data["metrics"] = metrics
        response_data["ai_predictions"] = ai_predictions
        
        return ProspectResponse(**response_data)
    
    async def _schedule_call(self, prospect: Prospect, parameters: Dict[str, Any]):
        """Schedule a call for prospect"""
        # Integration with call center service
        await self.service_client.post(
            f"{settings.CALL_CENTER_SERVICE_URL}/api/v1/calls/schedule",
            json={
                "prospect_id": prospect.id,
                "campaign_id": prospect.campaign_id,
                "phone_number": prospect.phone_number,
                "scheduled_time": parameters.get("scheduled_time"),
                "priority": parameters.get("priority", "medium")
            }
        )
    
    async def _schedule_prospect(self, prospect: Prospect, parameters: Dict[str, Any]):
        """Schedule prospect for future calling"""
        scheduled_time = parameters.get("scheduled_time")
        if scheduled_time:
            prospect.next_call_scheduled = datetime.fromisoformat(scheduled_time)
        prospect.updated_at = func.now()
    
    async def _convert_prospect(self, prospect: Prospect, parameters: Dict[str, Any]):
        """Mark prospect as converted"""
        conversion_value = parameters.get("conversion_value")
        conversion_type = parameters.get("conversion_type", "manual")
        prospect.mark_converted(conversion_value, conversion_type)
    
    async def _opt_out_prospect(self, prospect: Prospect):
        """Opt out prospect from future calls"""
        prospect.opt_out()
    
    async def _add_note_to_prospect(self, prospect: Prospect, note: str):
        """Add note to prospect"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        if prospect.notes:
            prospect.notes += f"\n\n[{timestamp}] {note}"
        else:
            prospect.notes = f"[{timestamp}] {note}"
        prospect.updated_at = func.now()