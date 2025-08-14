# apps/smart-campaigns/src/services/enhanced_campaign_service.py
"""
Enhanced Campaign Service - Unified service combining smart-campaigns + smart-campaigns-service
Provides comprehensive campaign management with AI optimization features
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
import uuid
import json

from models.enhanced_campaign import EnhancedCampaign, CampaignTemplate, CampaignOptimization, ABTest
from schemas.enhanced_campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignFilter,
    OptimizationRequest, OptimizationResponse, ABTestRequest, ABTestResponse,
    CampaignAnalytics, CampaignPerformance, CampaignStatus, CampaignType,
    IndustryType, OptimizationGoal
)
from shared.exceptions.service import ServiceException, ValidationException
from shared.database.client import get_database

logger = logging.getLogger(__name__)

class EnhancedCampaignService:
    """Enhanced Campaign Service with AI optimization capabilities"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_optimizer = AIOptimizer()  # AI optimization engine
        self.analytics_engine = AnalyticsEngine()  # Analytics processing
        
    async def create_campaign(
        self, 
        campaign_data: CampaignCreate, 
        user_id: str, 
        organization_id: str
    ) -> CampaignResponse:
        """Create a new enhanced campaign"""
        try:
            # Create campaign instance
            campaign = EnhancedCampaign(
                name=campaign_data.name,
                description=campaign_data.description,
                industry=campaign_data.industry.value,
                campaign_type=campaign_data.campaign_type.value,
                priority=campaign_data.priority.value,
                user_id=user_id,
                organization_id=organization_id,
                agent_id=campaign_data.agent_id,
                agent_name=campaign_data.agent_name,
                voice_id=campaign_data.voice_id,
                ai_agent_ids=campaign_data.ai_agent_ids,
                location=campaign_data.location,
                target_demographics=campaign_data.target_demographics,
                target_audience_size=campaign_data.target_audience_size,
                start_time=campaign_data.start_time,
                end_time=campaign_data.end_time,
                timezone=campaign_data.timezone,
                schedule_config=campaign_data.schedule_config,
                daily_call_limit=campaign_data.daily_call_limit,
                max_prospects=campaign_data.max_prospects,
                script_template=campaign_data.script_template,
                template_id=campaign_data.template_id,
                optimization_goal=campaign_data.optimization_goal.value,
                is_ai_optimized=campaign_data.is_ai_optimized,
                settings=campaign_data.settings
            )
            
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            
            # Initialize AI optimization if enabled
            if campaign_data.is_ai_optimized:
                await self._initialize_ai_optimization(campaign.id)
            
            logger.info(f"Created enhanced campaign {campaign.id} for user {user_id}")
            return self._to_response(campaign)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create campaign: {str(e)}")
            raise ServiceException(f"Failed to create campaign: {str(e)}")
    
    async def get_campaign(self, campaign_id: str, user_id: str, organization_id: str) -> Optional[CampaignResponse]:
        """Get a specific campaign"""
        campaign = self.db.query(EnhancedCampaign).filter(
            and_(
                EnhancedCampaign.id == campaign_id,
                EnhancedCampaign.user_id == user_id,
                EnhancedCampaign.organization_id == organization_id
            )
        ).first()
        
        if not campaign:
            return None
            
        return self._to_response(campaign)
    
    async def list_campaigns(
        self,
        user_id: str,
        organization_id: str,
        filters: CampaignFilter,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[CampaignResponse], int]:
        """List campaigns with filtering and pagination"""
        
        # Build base query
        query = self.db.query(EnhancedCampaign).filter(
            and_(
                EnhancedCampaign.user_id == user_id,
                EnhancedCampaign.organization_id == organization_id
            )
        )
        
        # Apply filters
        if filters.status:
            query = query.filter(EnhancedCampaign.status.in_([s.value for s in filters.status]))
        
        if filters.priority:
            query = query.filter(EnhancedCampaign.priority.in_([p.value for p in filters.priority]))
        
        if filters.industry:
            query = query.filter(EnhancedCampaign.industry.in_([i.value for i in filters.industry]))
        
        if filters.campaign_type:
            query = query.filter(EnhancedCampaign.campaign_type.in_([t.value for t in filters.campaign_type]))
        
        if filters.agent_id:
            query = query.filter(EnhancedCampaign.agent_id == filters.agent_id)
        
        if filters.is_ai_optimized is not None:
            query = query.filter(EnhancedCampaign.is_ai_optimized == filters.is_ai_optimized)
        
        if filters.date_from:
            query = query.filter(EnhancedCampaign.created_at >= filters.date_from)
        
        if filters.date_to:
            query = query.filter(EnhancedCampaign.created_at <= filters.date_to)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if hasattr(EnhancedCampaign, sort_by):
            order_column = getattr(EnhancedCampaign, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        # Apply pagination
        offset = (page - 1) * per_page
        campaigns = query.offset(offset).limit(per_page).all()
        
        return [self._to_response(campaign) for campaign in campaigns], total
    
    async def update_campaign(
        self,
        campaign_id: str,
        campaign_data: CampaignUpdate,
        user_id: str,
        organization_id: str
    ) -> Optional[CampaignResponse]:
        """Update an existing campaign"""
        
        campaign = self.db.query(EnhancedCampaign).filter(
            and_(
                EnhancedCampaign.id == campaign_id,
                EnhancedCampaign.user_id == user_id,
                EnhancedCampaign.organization_id == organization_id
            )
        ).first()
        
        if not campaign:
            return None
        
        try:
            # Update fields
            update_data = campaign_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(campaign, field) and value is not None:
                    # Handle enum values
                    if isinstance(value, str) and hasattr(value, 'value'):
                        setattr(campaign, field, value.value)
                    else:
                        setattr(campaign, field, value)
            
            campaign.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(campaign)
            
            # Trigger AI re-optimization if optimization settings changed
            if campaign_data.is_ai_optimized is not None and campaign_data.is_ai_optimized:
                await self._trigger_optimization(campaign.id)
            
            logger.info(f"Updated campaign {campaign_id}")
            return self._to_response(campaign)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Failed to update campaign: {str(e)}")
    
    async def delete_campaign(
        self,
        campaign_id: str,
        user_id: str,
        organization_id: str
    ) -> bool:
        """Delete a campaign"""
        
        campaign = self.db.query(EnhancedCampaign).filter(
            and_(
                EnhancedCampaign.id == campaign_id,
                EnhancedCampaign.user_id == user_id,
                EnhancedCampaign.organization_id == organization_id
            )
        ).first()
        
        if not campaign:
            return False
        
        try:
            # Delete related optimizations and AB tests
            self.db.query(CampaignOptimization).filter(
                CampaignOptimization.campaign_id == campaign_id
            ).delete()
            
            self.db.query(ABTest).filter(
                ABTest.campaign_id == campaign_id
            ).delete()
            
            # Delete campaign
            self.db.delete(campaign)
            self.db.commit()
            
            logger.info(f"Deleted campaign {campaign_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Failed to delete campaign: {str(e)}")
    
    # AI Optimization Methods (from smart-campaigns-service)
    async def optimize_campaign(self, campaign_id: str) -> OptimizationResponse:
        """Trigger AI optimization for a campaign"""
        
        campaign = self.db.query(EnhancedCampaign).filter(
            EnhancedCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise ServiceException("Campaign not found")
        
        try:
            # Create optimization record
            optimization = CampaignOptimization(
                campaign_id=campaign_id,
                optimization_type="comprehensive",
                optimization_goal=campaign.optimization_goal,
                status="running"
            )
            
            self.db.add(optimization)
            self.db.commit()
            
            # Trigger AI optimization
            result = await self.ai_optimizer.optimize_campaign(campaign)
            
            # Update optimization record with results
            optimization.metrics_after = result.get("metrics", {})
            optimization.improvement_percentage = result.get("improvement", 0.0)
            optimization.changes_made = result.get("changes", {})
            optimization.ai_recommendations = result.get("recommendations", [])
            optimization.status = "completed"
            optimization.completed_at = datetime.utcnow()
            optimization.is_successful = result.get("success", False)
            optimization.confidence_score = result.get("confidence", 0.0)
            
            self.db.commit()
            
            return OptimizationResponse(
                id=optimization.id,
                campaign_id=campaign_id,
                optimization_type="comprehensive",
                status="completed",
                improvements=result.get("metrics", {}),
                recommendations=result.get("recommendations", []),
                confidence_score=result.get("confidence", 0.0),
                started_at=optimization.started_at,
                completed_at=optimization.completed_at
            )
            
        except Exception as e:
            logger.error(f"Failed to optimize campaign {campaign_id}: {str(e)}")
            raise ServiceException(f"Optimization failed: {str(e)}")
    
    async def create_ab_test(self, ab_test_data: ABTestRequest) -> ABTestResponse:
        """Create A/B test for campaign optimization"""
        
        campaign = self.db.query(EnhancedCampaign).filter(
            EnhancedCampaign.id == ab_test_data.campaign_id
        ).first()
        
        if not campaign:
            raise ServiceException("Campaign not found")
        
        try:
            ab_test = ABTest(
                campaign_id=ab_test_data.campaign_id,
                test_name=ab_test_data.test_name,
                test_type=ab_test_data.test_type,
                variant_a_config=ab_test_data.variant_a_config,
                variant_b_config=ab_test_data.variant_b_config,
                traffic_split=ab_test_data.traffic_split,
                minimum_sample_size=ab_test_data.minimum_sample_size,
                confidence_level=ab_test_data.confidence_level,
                status="setup"
            )
            
            self.db.add(ab_test)
            self.db.commit()
            self.db.refresh(ab_test)
            
            logger.info(f"Created A/B test {ab_test.id} for campaign {ab_test_data.campaign_id}")
            
            return ABTestResponse(
                id=ab_test.id,
                campaign_id=ab_test.campaign_id,
                test_name=ab_test.test_name,
                test_type=ab_test.test_type,
                status=ab_test.status,
                variant_a_metrics={},
                variant_b_metrics={},
                statistical_significance=0.0
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create A/B test: {str(e)}")
            raise ServiceException(f"Failed to create A/B test: {str(e)}")
    
    async def get_analytics(self, organization_id: str) -> CampaignAnalytics:
        """Get comprehensive campaign analytics"""
        
        try:
            # Basic metrics
            total_campaigns = self.db.query(EnhancedCampaign).filter(
                EnhancedCampaign.organization_id == organization_id
            ).count()
            
            active_campaigns = self.db.query(EnhancedCampaign).filter(
                and_(
                    EnhancedCampaign.organization_id == organization_id,
                    EnhancedCampaign.status == CampaignStatus.ACTIVE.value
                )
            ).count()
            
            # Aggregate metrics
            result = self.db.query(
                func.sum(EnhancedCampaign.total_calls).label('total_calls'),
                func.sum(EnhancedCampaign.revenue_generated).label('total_revenue'),
                func.avg(EnhancedCampaign.conversion_rate).label('avg_conversion'),
                func.avg(EnhancedCampaign.roi_percentage).label('avg_roi')
            ).filter(
                EnhancedCampaign.organization_id == organization_id
            ).first()
            
            # Industry breakdown
            industry_performance = {}
            for industry in IndustryType:
                industry_stats = self.db.query(
                    func.count(EnhancedCampaign.id).label('count'),
                    func.avg(EnhancedCampaign.conversion_rate).label('avg_conversion'),
                    func.sum(EnhancedCampaign.revenue_generated).label('revenue')
                ).filter(
                    and_(
                        EnhancedCampaign.organization_id == organization_id,
                        EnhancedCampaign.industry == industry.value
                    )
                ).first()
                
                industry_performance[industry.value] = {
                    "campaigns": industry_stats.count or 0,
                    "avg_conversion_rate": float(industry_stats.avg_conversion or 0),
                    "total_revenue": float(industry_stats.revenue or 0)
                }
            
            # Campaign type performance
            type_performance = {}
            for campaign_type in CampaignType:
                type_stats = self.db.query(
                    func.count(EnhancedCampaign.id).label('count'),
                    func.avg(EnhancedCampaign.conversion_rate).label('avg_conversion'),
                    func.sum(EnhancedCampaign.revenue_generated).label('revenue')
                ).filter(
                    and_(
                        EnhancedCampaign.organization_id == organization_id,
                        EnhancedCampaign.campaign_type == campaign_type.value
                    )
                ).first()
                
                type_performance[campaign_type.value] = {
                    "campaigns": type_stats.count or 0,
                    "avg_conversion_rate": float(type_stats.avg_conversion or 0),
                    "total_revenue": float(type_stats.revenue or 0)
                }
            
            # Top performing campaigns
            top_campaigns = self.db.query(EnhancedCampaign).filter(
                EnhancedCampaign.organization_id == organization_id
            ).order_by(desc(EnhancedCampaign.roi_percentage)).limit(5).all()
            
            top_campaigns_data = [
                {
                    "id": campaign.id,
                    "name": campaign.name,
                    "roi_percentage": campaign.roi_percentage,
                    "revenue_generated": campaign.revenue_generated,
                    "conversion_rate": campaign.conversion_rate
                }
                for campaign in top_campaigns
            ]
            
            # AI optimization stats
            ai_optimized_count = self.db.query(EnhancedCampaign).filter(
                and_(
                    EnhancedCampaign.organization_id == organization_id,
                    EnhancedCampaign.is_ai_optimized == True
                )
            ).count()
            
            return CampaignAnalytics(
                total_campaigns=total_campaigns,
                active_campaigns=active_campaigns,
                total_calls=int(result.total_calls or 0),
                total_revenue=float(result.total_revenue or 0),
                average_conversion_rate=float(result.avg_conversion or 0),
                average_roi=float(result.avg_roi or 0),
                industry_performance=industry_performance,
                type_performance=type_performance,
                top_campaigns=top_campaigns_data,
                ai_optimized_campaigns=ai_optimized_count,
                optimization_improvements={},
                performance_timeline=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {str(e)}")
            raise ServiceException(f"Failed to get analytics: {str(e)}")
    
    async def get_campaign_performance(self, campaign_id: str) -> Optional[CampaignPerformance]:
        """Get detailed performance metrics for a specific campaign"""
        
        campaign = self.db.query(EnhancedCampaign).filter(
            EnhancedCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            return None
        
        try:
            return CampaignPerformance(
                campaign_id=campaign.id,
                campaign_name=campaign.name,
                total_calls=campaign.total_calls,
                successful_calls=campaign.successful_calls,
                failed_calls=campaign.total_calls - campaign.successful_calls,
                conversion_rate=campaign.conversion_rate,
                revenue_generated=campaign.revenue_generated,
                cost_per_call=campaign.cost_per_acquisition / max(campaign.successful_calls, 1),
                cost_per_acquisition=campaign.cost_per_acquisition,
                roi_percentage=campaign.roi_percentage,
                average_call_duration=0.0,  # TODO: Implement call duration tracking
                customer_satisfaction_score=0.0,  # TODO: Implement satisfaction tracking
                optimization_count=len(campaign.optimization_history),
                improvement_percentage=0.0,  # TODO: Calculate from optimization history
                daily_performance=[],  # TODO: Implement daily tracking
                hourly_performance=[],  # TODO: Implement hourly tracking
                vs_industry_average={},  # TODO: Implement industry comparison
                vs_previous_period={}  # TODO: Implement period comparison
            )
            
        except Exception as e:
            logger.error(f"Failed to get campaign performance: {str(e)}")
            raise ServiceException(f"Failed to get performance metrics: {str(e)}")
    
    # Helper methods
    def _to_response(self, campaign: EnhancedCampaign) -> CampaignResponse:
        """Convert campaign model to response schema"""
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            industry=IndustryType(campaign.industry),
            campaign_type=CampaignType(campaign.campaign_type),
            status=CampaignStatus(campaign.status),
            priority=campaign.priority,
            user_id=campaign.user_id,
            organization_id=campaign.organization_id,
            agent_id=campaign.agent_id,
            agent_name=campaign.agent_name,
            voice_id=campaign.voice_id,
            ai_agent_ids=campaign.ai_agent_ids or [],
            location=campaign.location,
            target_demographics=campaign.target_demographics or {},
            target_audience_size=campaign.target_audience_size,
            start_time=campaign.start_time,
            end_time=campaign.end_time,
            timezone=campaign.timezone,
            schedule_config=campaign.schedule_config or {},
            daily_call_limit=campaign.daily_call_limit,
            max_prospects=campaign.max_prospects,
            script_template=campaign.script_template,
            template_id=campaign.template_id,
            optimization_goal=OptimizationGoal(campaign.optimization_goal),
            is_ai_optimized=campaign.is_ai_optimized,
            settings=campaign.settings or {},
            total_calls=campaign.total_calls,
            successful_calls=campaign.successful_calls,
            conversion_rate=campaign.conversion_rate,
            revenue_generated=campaign.revenue_generated,
            cost_per_acquisition=campaign.cost_per_acquisition,
            roi_percentage=campaign.roi_percentage,
            is_ab_test=campaign.is_ab_test,
            ab_test_config=campaign.ab_test_config or {},
            parent_campaign_id=campaign.parent_campaign_id,
            analytics_data=campaign.analytics_data or {},
            performance_metrics=campaign.performance_metrics or {},
            optimization_history=campaign.optimization_history or [],
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            started_at=campaign.started_at,
            completed_at=campaign.completed_at
        )
    
    async def _initialize_ai_optimization(self, campaign_id: str):
        """Initialize AI optimization for a new campaign"""
        try:
            await self.ai_optimizer.initialize_campaign(campaign_id)
            logger.info(f"Initialized AI optimization for campaign {campaign_id}")
        except Exception as e:
            logger.error(f"Failed to initialize AI optimization: {str(e)}")
    
    async def _trigger_optimization(self, campaign_id: str):
        """Trigger optimization after campaign updates"""
        try:
            await self.optimize_campaign(campaign_id)
        except Exception as e:
            logger.error(f"Failed to trigger optimization: {str(e)}")

# AI Optimization Engine (placeholder - implement based on requirements)
class AIOptimizer:
    """AI optimization engine for campaigns"""
    
    async def optimize_campaign(self, campaign: EnhancedCampaign) -> Dict[str, Any]:
        """Optimize campaign using AI algorithms"""
        # TODO: Implement actual AI optimization logic
        return {
            "success": True,
            "improvement": 15.5,
            "confidence": 0.85,
            "metrics": {
                "conversion_rate": campaign.conversion_rate * 1.155,
                "roi_percentage": campaign.roi_percentage * 1.10
            },
            "recommendations": [
                "Optimize call timing for better conversion rates",
                "Adjust script for higher engagement",
                "Target high-value prospects during peak hours"
            ],
            "changes": {
                "script_optimized": True,
                "timing_adjusted": True,
                "targeting_refined": True
            }
        }
    
    async def initialize_campaign(self, campaign_id: str):
        """Initialize AI optimization for a campaign"""
        # TODO: Implement initialization logic
        pass

# Analytics Engine (placeholder - implement based on requirements)
class AnalyticsEngine:
    """Analytics processing engine"""
    
    def calculate_performance_metrics(self, campaign: EnhancedCampaign) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        # TODO: Implement analytics calculations
        return {}
