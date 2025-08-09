# apps/smart-campaigns/src/services/campaign_service.py
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
import uuid
import asyncio
import logging

from models.campaign import Campaign, CampaignSchedule
from models.prospect import Prospect
from schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignFilter,
    CampaignAction, CampaignOptimization, CampaignMetrics
)
from core.config import get_settings, CampaignStatus, CampaignPriority
from shared.database.client import get_database
from shared.utils.service_client import ServiceClient
from shared.exceptions.service import ServiceException, ValidationException
from services.ai_optimization_service import AIOptimizationService
from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)
settings = get_settings()

class CampaignService:
    """Service for managing campaigns"""
    
    def __init__(self, db: Session = None):
        self.db = db or get_database()
        self.service_client = ServiceClient()
        self.ai_optimizer = AIOptimizationService()
        self.predictor = PredictionService()
    
    async def create_campaign(self, campaign_data: CampaignCreate, user_id: str, organization_id: str) -> CampaignResponse:
        """Create a new campaign"""
        try:
            # Validate agent exists
            agent_info = await self._validate_agent(campaign_data.agent_id, organization_id)
            
            # Create campaign record
            campaign = Campaign(
                id=f"camp_{uuid.uuid4().hex[:12]}",
                name=campaign_data.name,
                description=campaign_data.description,
                industry=campaign_data.industry,
                campaign_type=campaign_data.campaign_type,
                priority=campaign_data.priority,
                user_id=user_id,
                organization_id=organization_id,
                agent_id=campaign_data.agent_id,
                agent_name=agent_info.get('name'),
                voice_id=campaign_data.voice_id,
                location=campaign_data.location,
                target_demographics=campaign_data.target_demographics,
                start_time=campaign_data.start_time,
                end_time=campaign_data.end_time,
                timezone=campaign_data.timezone,
                settings=campaign_data.settings,
                tags=campaign_data.tags,
                ai_optimization_enabled=campaign_data.ai_optimization_enabled,
                status=CampaignStatus.DRAFT
            )
            
            # Generate AI predictions for new campaign
            if settings.ENABLE_PREDICTIVE_ANALYTICS:
                predictions = await self.predictor.predict_campaign_performance(campaign_data.dict())
                campaign.predicted_success_rate = predictions.get('success_rate')
                campaign.predicted_revenue = predictions.get('revenue')
                campaign.prediction_confidence = predictions.get('confidence')
            
            self.db.add(campaign)
            await self.db.commit()
            await self.db.refresh(campaign)
            
            logger.info(f"Created campaign {campaign.id} for user {user_id}")
            return await self._build_campaign_response(campaign)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating campaign: {str(e)}")
            raise ServiceException(f"Failed to create campaign: {str(e)}")
    
    async def get_campaign(self, campaign_id: str, user_id: str, organization_id: str) -> Optional[CampaignResponse]:
        """Get a single campaign by ID"""
        campaign = await self._get_user_campaign(campaign_id, user_id, organization_id)
        if not campaign:
            return None
        
        return await self._build_campaign_response(campaign)
    
    async def list_campaigns(
        self, 
        user_id: str, 
        organization_id: str,
        filters: CampaignFilter = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[CampaignResponse], int]:
        """List campaigns with filtering and pagination"""
        
        query = self.db.query(Campaign).filter(
            Campaign.organization_id == organization_id,
            Campaign.user_id == user_id
        )
        
        # Apply filters
        if filters:
            if filters.status:
                query = query.filter(Campaign.status.in_(filters.status))
            if filters.priority:
                query = query.filter(Campaign.priority.in_(filters.priority))
            if filters.campaign_type:
                query = query.filter(Campaign.campaign_type.in_(filters.campaign_type))
            if filters.industry:
                query = query.filter(Campaign.industry.in_(filters.industry))
            if filters.agent_id:
                query = query.filter(Campaign.agent_id == filters.agent_id)
            if filters.tags:
                # JSON array contains any of the specified tags
                for tag in filters.tags:
                    query = query.filter(Campaign.tags.contains([tag]))
            if filters.created_after:
                query = query.filter(Campaign.created_at >= filters.created_after)
            if filters.created_before:
                query = query.filter(Campaign.created_at <= filters.created_before)
            if filters.success_rate_min is not None:
                query = query.filter(Campaign.success_rate >= filters.success_rate_min)
            if filters.success_rate_max is not None:
                query = query.filter(Campaign.success_rate <= filters.success_rate_max)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Campaign, sort_by, Campaign.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * per_page
        campaigns = query.offset(offset).limit(per_page).all()
        
        # Build responses
        campaign_responses = []
        for campaign in campaigns:
            response = await self._build_campaign_response(campaign)
            campaign_responses.append(response)
        
        return campaign_responses, total
    
    async def update_campaign(self, campaign_id: str, campaign_data: CampaignUpdate, user_id: str, organization_id: str) -> CampaignResponse:
        """Update an existing campaign"""
        campaign = await self._get_user_campaign(campaign_id, user_id, organization_id)
        if not campaign:
            raise ValidationException("Campaign not found")
        
        # Check if campaign can be updated
        if campaign.status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            raise ValidationException("Cannot update completed or cancelled campaigns")
        
        try:
            # Update fields
            update_data = campaign_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(campaign, field):
                    setattr(campaign, field, value)
            
            # Validate agent if changed
            if campaign_data.agent_id and campaign_data.agent_id != campaign.agent_id:
                agent_info = await self._validate_agent(campaign_data.agent_id, organization_id)
                campaign.agent_name = agent_info.get('name')
            
            campaign.updated_at = func.now()
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            logger.info(f"Updated campaign {campaign_id}")
            return await self._build_campaign_response(campaign)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Failed to update campaign: {str(e)}")
    
    async def delete_campaign(self, campaign_id: str, user_id: str, organization_id: str) -> bool:
        """Delete a campaign"""
        campaign = await self._get_user_campaign(campaign_id, user_id, organization_id)
        if not campaign:
            return False
        
        # Check if campaign can be deleted
        if campaign.status in [CampaignStatus.ACTIVE, CampaignStatus.RUNNING]:
            raise ValidationException("Cannot delete active campaigns. Please pause or stop first.")
        
        try:
            await self.db.delete(campaign)
            await self.db.commit()
            
            logger.info(f"Deleted campaign {campaign_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Failed to delete campaign: {str(e)}")
    
    async def execute_campaign_action(self, campaign_id: str, action: CampaignAction, user_id: str, organization_id: str) -> CampaignResponse:
        """Execute an action on a campaign"""
        campaign = await self._get_user_campaign(campaign_id, user_id, organization_id)
        if not campaign:
            raise ValidationException("Campaign not found")
        
        try:
            if action.action == "start":
                await self._start_campaign(campaign, action.force)
            elif action.action == "pause":
                await self._pause_campaign(campaign)
            elif action.action == "resume":
                await self._resume_campaign(campaign)
            elif action.action == "stop":
                await self._stop_campaign(campaign)
            elif action.action == "cancel":
                await self._cancel_campaign(campaign)
            else:
                raise ValidationException(f"Unknown action: {action.action}")
            
            campaign.updated_at = func.now()
            campaign.last_activity_at = func.now()
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            logger.info(f"Executed action '{action.action}' on campaign {campaign_id}")
            return await self._build_campaign_response(campaign)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error executing action on campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Failed to execute action: {str(e)}")
    
    async def optimize_campaign(self, campaign_id: str, optimization: CampaignOptimization, user_id: str, organization_id: str) -> CampaignResponse:
        """Optimize campaign using AI"""
        campaign = await self._get_user_campaign(campaign_id, user_id, organization_id)
        if not campaign:
            raise ValidationException("Campaign not found")
        
        if not campaign.ai_optimization_enabled:
            raise ValidationException("AI optimization is disabled for this campaign")
        
        try:
            # Get optimization suggestions
            suggestions = await self.ai_optimizer.optimize_campaign(
                campaign.to_dict(),
                optimization.optimization_type,
                optimization.target_metric,
                optimization.constraints
            )
            
            # Update campaign with suggestions
            campaign.optimization_suggestions = suggestions.get('suggestions', [])
            campaign.ai_optimization_score = suggestions.get('score', campaign.ai_optimization_score)
            
            # Apply optimizations if requested
            if optimization.apply_immediately:
                await self._apply_optimizations(campaign, suggestions)
            
            campaign.updated_at = func.now()
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            logger.info(f"Optimized campaign {campaign_id}")
            return await self._build_campaign_response(campaign)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error optimizing campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Failed to optimize campaign: {str(e)}")
    
    async def get_campaign_analytics(self, campaign_id: str, user_id: str, organization_id: str, days: int = 30) -> Dict[str, Any]:
        """Get campaign analytics"""
        campaign = await self._get_user_campaign(campaign_id, user_id, organization_id)
        if not campaign:
            raise ValidationException("Campaign not found")
        
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get prospect statistics
            prospect_stats = await self._get_prospect_statistics(campaign_id, start_date, end_date)
            
            # Get call statistics from call center service
            call_stats = await self.service_client.get(
                f"{settings.CALL_CENTER_SERVICE_URL}/api/v1/analytics/campaign/{campaign_id}",
                params={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
            )
            
            # Build analytics response
            analytics = {
                "campaign_id": campaign_id,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "metrics": {
                    "total_prospects": campaign.total_prospects,
                    "calls_made": campaign.calls_made,
                    "success_rate": campaign.success_rate,
                    "conversion_rate": campaign.conversion_rate,
                    "revenue": campaign.revenue_generated,
                    "cost": campaign.total_cost,
                    "roi": campaign.roi
                },
                "prospects": prospect_stats,
                "calls": call_stats.get("data", {}) if call_stats else {},
                "trends": await self._calculate_trends(campaign_id, start_date, end_date),
                "insights": await self._generate_insights(campaign)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics for campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Failed to get campaign analytics: {str(e)}")
    
    # Private helper methods
    async def _get_user_campaign(self, campaign_id: str, user_id: str, organization_id: str) -> Optional[Campaign]:
        """Get campaign owned by user"""
        return self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
            Campaign.organization_id == organization_id
        ).first()
    
    async def _validate_agent(self, agent_id: str, organization_id: str) -> Dict[str, Any]:
        """Validate that agent exists and is available"""
        try:
            response = await self.service_client.get(
                f"{settings.API_GATEWAY_URL}/api/v1/agents/{agent_id}",
                headers={"X-Organization-ID": organization_id}
            )
            if not response:
                raise ValidationException(f"Agent {agent_id} not found")
            return response.get("data", {})
        except Exception as e:
            logger.error(f"Error validating agent {agent_id}: {str(e)}")
            raise ValidationException(f"Invalid agent: {agent_id}")
    
    async def _build_campaign_response(self, campaign: Campaign) -> CampaignResponse:
        """Build campaign response with metrics"""
        # Calculate current metrics
        metrics = CampaignMetrics(
            total_prospects=campaign.total_prospects,
            calls_made=campaign.calls_made,
            calls_answered=campaign.calls_answered,
            calls_completed=campaign.calls_completed,
            success_rate=campaign.success_rate,
            conversion_rate=campaign.conversion_rate,
            average_call_duration=campaign.average_call_duration,
            total_cost=campaign.total_cost,
            revenue_generated=campaign.revenue_generated,
            cost_per_lead=campaign.cost_per_lead,
            roi=campaign.roi,
            live_calls=campaign.live_calls,
            calls_today=campaign.calls_today,
            conversions_today=campaign.conversions_today
        )
        
        # Build response
        response_data = campaign.to_dict()
        response_data["metrics"] = metrics
        
        return CampaignResponse(**response_data)
    
    async def _start_campaign(self, campaign: Campaign, force: bool = False):
        """Start a campaign"""
        if not force and not campaign.can_be_started:
            raise ValidationException(f"Campaign cannot be started. Current status: {campaign.status}")
        
        # Validate campaign has prospects
        prospect_count = self.db.query(func.count(Prospect.id)).filter(
            Prospect.campaign_id == campaign.id
        ).scalar()
        
        if prospect_count == 0:
            raise ValidationException("Campaign must have prospects before starting")
        
        campaign.status = CampaignStatus.ACTIVE
        campaign.started_at = func.now()
        
        # Notify call center service
        await self.service_client.post(
            f"{settings.CALL_CENTER_SERVICE_URL}/api/v1/campaigns/{campaign.id}/start",
            json={"campaign_data": campaign.to_dict()}
        )
    
    async def _pause_campaign(self, campaign: Campaign):
        """Pause a campaign"""
        if not campaign.can_be_paused:
            raise ValidationException(f"Campaign cannot be paused. Current status: {campaign.status}")
        
        campaign.status = CampaignStatus.PAUSED
        
        # Notify call center service
        await self.service_client.post(
            f"{settings.CALL_CENTER_SERVICE_URL}/api/v1/campaigns/{campaign.id}/pause"
        )
    
    async def _resume_campaign(self, campaign: Campaign):
        """Resume a paused campaign"""
        if campaign.status != CampaignStatus.PAUSED:
            raise ValidationException("Only paused campaigns can be resumed")
        
        campaign.status = CampaignStatus.ACTIVE
        
        # Notify call center service
        await self.service_client.post(
            f"{settings.CALL_CENTER_SERVICE_URL}/api/v1/campaigns/{campaign.id}/resume"
        )
    
    async def _stop_campaign(self, campaign: Campaign):
        """Stop a campaign"""
        if campaign.status not in [CampaignStatus.ACTIVE, CampaignStatus.RUNNING, CampaignStatus.PAUSED]:
            raise ValidationException("Only active or paused campaigns can be stopped")
        
        campaign.status = CampaignStatus.COMPLETED
        campaign.completed_at = func.now()
        
        # Notify call center service
        await self.service_client.post(
            f"{settings.CALL_CENTER_SERVICE_URL}/api/v1/campaigns/{campaign.id}/stop"
        )
    
    async def _cancel_campaign(self, campaign: Campaign):
        """Cancel a campaign"""
        if campaign.status == CampaignStatus.COMPLETED:
            raise ValidationException("Cannot cancel completed campaigns")
        
        campaign.status = CampaignStatus.CANCELLED
        campaign.completed_at = func.now()
        
        # Notify call center service
        await self.service_client.post(
            f"{settings.CALL_CENTER_SERVICE_URL}/api/v1/campaigns/{campaign.id}/cancel"
        )
    
    async def _apply_optimizations(self, campaign: Campaign, suggestions: Dict[str, Any]):
        """Apply AI optimization suggestions"""
        optimizations = suggestions.get('optimizations', {})
        
        # Apply settings optimizations
        if 'settings' in optimizations:
            campaign.settings.update(optimizations['settings'])
        
        # Apply scheduling optimizations
        if 'schedule' in optimizations:
            schedule_opts = optimizations['schedule']
            if 'start_time' in schedule_opts:
                campaign.start_time = schedule_opts['start_time']
            if 'end_time' in schedule_opts:
                campaign.end_time = schedule_opts['end_time']
    
    async def _get_prospect_statistics(self, campaign_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get prospect statistics for date range"""
        prospects = self.db.query(Prospect).filter(
            Prospect.campaign_id == campaign_id,
            Prospect.created_at >= start_date,
            Prospect.created_at <= end_date
        )
        
        total_prospects = prospects.count()
        converted_prospects = prospects.filter(Prospect.is_converted == True).count()
        
        # Status breakdown
        status_breakdown = {}
        for status in [status.value for status in ProspectStatusEnum]:
            count = prospects.filter(Prospect.status == status).count()
            status_breakdown[status] = count
        
        return {
            "total": total_prospects,
            "converted": converted_prospects,
            "conversion_rate": (converted_prospects / total_prospects * 100) if total_prospects > 0 else 0,
            "status_breakdown": status_breakdown
        }
    
    async def _calculate_trends(self, campaign_id: str, start_date: datetime, end_date: datetime) -> Dict[str, List[float]]:
        """Calculate performance trends"""
        # This would typically involve more complex time-series analysis
        # For now, return placeholder data
        return {
            "success_rate": [20.5, 22.1, 24.3, 23.8, 25.2],
            "call_volume": [100, 150, 200, 180, 220],
            "conversion_rate": [15.2, 16.8, 18.1, 17.5, 19.3]
        }
    
    async def _generate_insights(self, campaign: Campaign) -> List[str]:
        """Generate AI insights for campaign"""
        insights = []
        
        if campaign.success_rate < 20:
            insights.append("Success rate is below average. Consider optimizing call timing or script.")
        
        if campaign.ai_optimization_score > 90:
            insights.append("Campaign is highly optimized. Great performance!")
        elif campaign.ai_optimization_score < 70:
            insights.append("Campaign could benefit from AI optimization.")
        
        if campaign.calls_today > campaign.calls_made * 0.1:
            insights.append("High call activity today. Monitor for quality.")
        
        return insights