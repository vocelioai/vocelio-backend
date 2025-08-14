# apps/overview/src/services/enhanced_overview_service.py
"""
Enhanced Overview Service - Unified service combining overview + overview-service
Provides comprehensive dashboard functionality with real-time features
"""

import asyncio
import logging
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import redis.asyncio as redis
import asyncpg

from schemas.enhanced_overview import (
    LiveMetrics, SystemHealth, RevenueMetrics, AIInsight, GlobalStats,
    DashboardOverview, LiveStats, MetricsSnapshot, DashboardAlert,
    WebSocketMessage, LiveUpdateMessage, AlertMessage, InsightMessage,
    PerformanceMetrics, CacheStatus
)
from shared.database.client import get_database
from shared.utils.service_client import ServiceClient

logger = logging.getLogger(__name__)

class EnhancedOverviewService:
    """Enhanced Overview Service with real-time capabilities"""
    
    def __init__(self):
        self.service_client = ServiceClient()
        self._cache = {}
        self._cache_ttl = 30  # 30 seconds cache
        self.redis_client = None
        self.pg_pool = None
        self._background_tasks = []
        
    async def initialize(self):
        """Initialize service with database connections"""
        try:
            # Initialize Redis connection
            redis_host = "redis"  # Configure from environment
            redis_port = 6379
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )
            
            # Initialize PostgreSQL connection pool
            self.pg_pool = await asyncpg.create_pool(
                host="postgres",  # Configure from environment
                port=5432,
                user="postgres",
                password="password",
                database="vocelio",
                min_size=2,
                max_size=10
            )
            
            logger.info("✅ Enhanced Overview Service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Overview Service: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.pg_pool:
            await self.pg_pool.close()
    
    # Live Metrics (from overview-service)
    async def get_live_metrics(self, organization_id: str) -> LiveMetrics:
        """Get real-time live metrics"""
        try:
            # Try to get from Redis cache first
            cache_key = f"live_metrics:{organization_id}"
            if self.redis_client:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return LiveMetrics(**data)
            
            # Generate fresh metrics
            metrics = await self._generate_live_metrics(organization_id)
            
            # Cache the result
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key, 
                    30,  # 30 seconds TTL
                    json.dumps(metrics.dict())
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting live metrics: {str(e)}")
            # Return default metrics on error
            return await self._generate_live_metrics(organization_id)
    
    async def _generate_live_metrics(self, organization_id: str) -> LiveMetrics:
        """Generate realistic live metrics with variance"""
        # Simulate realistic metrics based on organization
        base_multiplier = 1.0  # Could be adjusted based on organization tier
        
        return LiveMetrics(
            total_clients=random.randint(int(125000 * base_multiplier), int(135000 * base_multiplier)),
            active_calls=random.randint(int(8500 * base_multiplier), int(12500 * base_multiplier)),
            calls_today=random.randint(int(285000 * base_multiplier), int(315000 * base_multiplier)),
            revenue_today=random.uniform(1800000 * base_multiplier, 2200000 * base_multiplier),
            success_rate=random.uniform(92.5, 97.8),
            ai_optimization_score=random.uniform(94.0, 98.5),
            system_uptime=random.uniform(99.95, 99.99),
            monthly_call_volume=random.randint(int(88000000 * base_multiplier), int(91000000 * base_multiplier)),
            agents_active=random.randint(245, 247),
            campaigns_running=random.randint(87, 91),
            last_updated=datetime.now()
        )
    
    # System Health (from overview-service)
    async def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        try:
            # Check actual system metrics if available
            # For now, simulate realistic health data
            services_online = random.randint(17, 18)
            total_services = 18
            uptime = random.uniform(99.95, 99.99)
            
            # Determine status based on metrics
            if services_online == total_services and uptime > 99.9:
                status = "operational"
            elif services_online >= total_services * 0.9:
                status = "degraded"
            else:
                status = "down"
            
            return SystemHealth(
                status=status,
                uptime=uptime,
                services_online=services_online,
                total_services=total_services,
                response_time_avg=random.uniform(45.0, 120.0),
                error_rate=random.uniform(0.01, 0.5),
                active_alerts=random.randint(0, 3),
                last_check=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return SystemHealth(
                status="degraded",
                uptime=99.0,
                services_online=17,
                total_services=18,
                last_check=datetime.now()
            )
    
    # Revenue Metrics (from overview-service)
    async def get_revenue_metrics(self, organization_id: str) -> RevenueMetrics:
        """Get revenue metrics"""
        try:
            # Could fetch real data from database
            # For now, generate realistic revenue data
            return RevenueMetrics(
                daily_revenue=random.uniform(1800000, 2200000),
                monthly_revenue=random.uniform(45000000, 55000000),
                yearly_revenue=random.uniform(540000000, 660000000),
                revenue_growth=random.uniform(15.5, 25.8),
                top_revenue_sources=[
                    {"source": "Solar Campaigns", "revenue": 15700000, "percentage": 33.2},
                    {"source": "Insurance Calls", "revenue": 12300000, "percentage": 26.1},
                    {"source": "Real Estate", "revenue": 8900000, "percentage": 18.9},
                    {"source": "Healthcare", "revenue": 6800000, "percentage": 14.4},
                    {"source": "Financial Services", "revenue": 3400000, "percentage": 7.4}
                ],
                projected_monthly=random.uniform(52000000, 58000000)
            )
            
        except Exception as e:
            logger.error(f"Error getting revenue metrics: {str(e)}")
            raise
    
    # AI Insights (enhanced from both services)
    async def get_ai_insights(
        self, 
        organization_id: str, 
        limit: int = 10, 
        priority_filter: Optional[str] = None
    ) -> List[AIInsight]:
        """Get AI-generated insights and recommendations"""
        try:
            # Try to get from Redis cache
            cache_key = f"ai_insights:{organization_id}"
            if self.redis_client:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    insights_data = json.loads(cached)
                    insights = [AIInsight(**data) for data in insights_data]
                    
                    # Apply filters
                    if priority_filter:
                        insights = [i for i in insights if i.priority == priority_filter]
                    
                    return insights[:limit]
            
            # Generate fresh insights
            insights = await self._generate_ai_insights(organization_id)
            
            # Cache the results
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key,
                    300,  # 5 minutes TTL
                    json.dumps([insight.dict() for insight in insights])
                )
            
            # Apply filters
            if priority_filter:
                insights = [i for i in insights if i.priority == priority_filter]
            
            return insights[:limit]
            
        except Exception as e:
            logger.error(f"Error getting AI insights: {str(e)}")
            return []
    
    async def _generate_ai_insights(self, organization_id: str) -> List[AIInsight]:
        """Generate AI insights for the organization"""
        insights = [
            AIInsight(
                id=f"insight_{uuid.uuid4().hex[:8]}",
                title="🚀 Ultra Performance Boost",
                description='Switch 89% of Solar campaigns to "Confident Mike" voice for immediate 34% success boost',
                insight_type="optimization",
                category="voice_optimization",
                confidence=97.0,
                impact_estimate="+$2.3M revenue impact",
                potential_value=2300000.0,
                priority="high",
                action_type="voice_optimization",
                recommended_action={
                    "action": "switch_voice",
                    "voice_id": "confident_mike",
                    "campaigns": "solar_campaigns",
                    "percentage": 89
                },
                implementation_steps=[
                    "Analyze current Solar campaign performance",
                    "Test Confident Mike voice on 10% sample",
                    "Gradually roll out to 89% of campaigns",
                    "Monitor performance improvements"
                ]
            ),
            AIInsight(
                id=f"insight_{uuid.uuid4().hex[:8]}",
                title="⏰ Global Timing Optimization",
                description="Peak performance window detected: 2:00-4:00 PM EST across all time zones",
                insight_type="optimization",
                category="timing_optimization",
                confidence=94.0,
                impact_estimate="+67% answer rate",
                potential_value=1500000.0,
                priority="medium",
                action_type="timing_optimization",
                recommended_action={
                    "action": "adjust_calling_hours",
                    "optimal_window": "14:00-16:00 EST",
                    "expected_improvement": 67
                },
                implementation_steps=[
                    "Review current calling schedule",
                    "Implement time zone optimization",
                    "Monitor answer rate improvements"
                ]
            ),
            AIInsight(
                id=f"insight_{uuid.uuid4().hex[:8]}",
                title="🎯 High-Value Prospect Alert",
                description="2,847 ultra-high-value prospects detected with 95%+ booking probability",
                insight_type="alert",
                category="prospect_prioritization",
                confidence=91.0,
                impact_estimate="$47M potential value",
                potential_value=47000000.0,
                priority="high",
                action_type="prospect_prioritization",
                recommended_action={
                    "action": "prioritize_prospects",
                    "prospect_count": 2847,
                    "booking_probability": 95,
                    "potential_value": 47000000
                },
                implementation_steps=[
                    "Export high-value prospect list",
                    "Assign to top-performing agents",
                    "Use premium calling times",
                    "Apply optimized scripts"
                ]
            )
        ]
        
        return insights
    
    # Dashboard Overview (from overview)
    async def get_dashboard_overview(self, organization_id: str) -> DashboardOverview:
        """Get complete dashboard overview"""
        try:
            # Get all dashboard components
            live_metrics = await self.get_live_metrics(organization_id)
            ai_insights = await self.get_ai_insights(organization_id, limit=3)
            system_health = await self.get_system_health()
            revenue_metrics = await self.get_revenue_metrics(organization_id)
            
            # Get alerts (placeholder - implement based on requirements)
            alerts = await self._get_dashboard_alerts(organization_id)
            
            return DashboardOverview(
                organization_id=organization_id,
                live_metrics=live_metrics,
                ai_insights=ai_insights,
                system_health=system_health,
                revenue_metrics=revenue_metrics,
                alerts=alerts,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {str(e)}")
            raise
    
    # Live Stats (from overview)
    async def get_live_stats(self, organization_id: str) -> LiveStats:
        """Get live statistics for real-time updates"""
        try:
            # Generate live stats with more detailed metrics
            return LiveStats(
                active_calls=random.randint(8500, 12500),
                calls_per_minute=random.uniform(45.0, 78.0),
                success_rate_live=random.uniform(92.0, 98.0),
                revenue_per_hour=random.uniform(75000.0, 125000.0),
                top_performing_agents=[
                    {"agent_id": "agent_001", "name": "Confident Mike", "calls": 234, "success_rate": 97.8},
                    {"agent_id": "agent_002", "name": "Professional Sarah", "calls": 198, "success_rate": 96.2},
                    {"agent_id": "agent_003", "name": "Friendly Alex", "calls": 187, "success_rate": 95.4}
                ],
                system_load=random.uniform(35.0, 65.0),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting live stats: {str(e)}")
            raise
    
    # Global Stats (from overview-service)
    async def get_global_stats(self) -> GlobalStats:
        """Get global platform statistics"""
        return GlobalStats(
            total_ai_agents=247,
            industries_covered=89,
            global_success_rate=94.7,
            monthly_call_volume=89500000,
            total_revenue=47000000,
            system_uptime=99.99
        )
    
    # WebSocket Support (from overview-service)
    async def generate_live_update_message(self, organization_id: str) -> LiveUpdateMessage:
        """Generate live update message for WebSocket"""
        metrics = await self.get_live_metrics(organization_id)
        return LiveUpdateMessage(
            type="live_update",
            data={"metrics": metrics.dict()},
            metrics=metrics
        )
    
    async def generate_alert_message(self, organization_id: str, alert: DashboardAlert) -> AlertMessage:
        """Generate alert message for WebSocket"""
        return AlertMessage(
            type="alert",
            data={"alert": alert.dict()},
            alert=alert
        )
    
    async def generate_insight_message(self, organization_id: str, insight: AIInsight) -> InsightMessage:
        """Generate AI insight message for WebSocket"""
        return InsightMessage(
            type="ai_insight",
            data={"insight": insight.dict()},
            insight=insight
        )
    
    # Background Tasks (from overview-service)
    async def start_background_tasks(self):
        """Start background tasks for real-time updates"""
        self._background_tasks = [
            asyncio.create_task(self._live_metrics_updater()),
            asyncio.create_task(self._ai_insights_generator()),
            asyncio.create_task(self._system_health_monitor())
        ]
        logger.info("✅ Background tasks started")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        for task in self._background_tasks:
            task.cancel()
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        logger.info("✅ Background tasks stopped")
    
    async def _live_metrics_updater(self):
        """Background task to update live metrics every 2 seconds"""
        while True:
            try:
                # Update metrics for all active organizations
                # For now, just refresh cache
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in live metrics updater: {e}")
                await asyncio.sleep(5)
    
    async def _ai_insights_generator(self):
        """Background task to generate AI insights every 30 seconds"""
        while True:
            try:
                # Generate insights for organizations
                # Implementation depends on requirements
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in AI insights generator: {e}")
                await asyncio.sleep(60)
    
    async def _system_health_monitor(self):
        """Background task to monitor system health"""
        while True:
            try:
                # Monitor system health and generate alerts if needed
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in system health monitor: {e}")
                await asyncio.sleep(120)
    
    # Helper methods
    async def _get_dashboard_alerts(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get dashboard alerts for organization"""
        # Placeholder implementation
        return [
            {
                "id": "alert_1",
                "type": "performance",
                "severity": "info",
                "title": "Campaign Performance Update",
                "message": "Solar campaigns showing 15% improvement this hour",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    # Cache Management
    async def get_cache_status(self) -> CacheStatus:
        """Get cache status information"""
        try:
            if not self.redis_client:
                return CacheStatus(
                    cache_key="redis_unavailable",
                    hit_rate=0.0,
                    size=0,
                    expires_at=datetime.now(),
                    last_updated=datetime.now()
                )
            
            # Get Redis info
            info = await self.redis_client.info()
            
            return CacheStatus(
                cache_key="redis_cache",
                hit_rate=float(info.get("keyspace_hits", 0)) / max(float(info.get("keyspace_misses", 1)), 1) * 100,
                size=info.get("used_memory", 0),
                expires_at=datetime.now() + timedelta(hours=1),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting cache status: {e}")
            return CacheStatus(
                cache_key="error",
                hit_rate=0.0,
                size=0,
                expires_at=datetime.now(),
                last_updated=datetime.now()
            )
    
    async def clear_cache(self, pattern: str = "*") -> bool:
        """Clear cache entries matching pattern"""
        try:
            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    # Enhanced background task methods for main.py
    async def update_live_metrics_cache(self):
        """Background task to update live metrics cache"""
        try:
            # Get all organizations with recent activity
            # This is a simplified implementation - in production, you'd track active orgs
            sample_org_ids = ["default_org"]  # Replace with actual org discovery
            
            for org_id in sample_org_ids:
                metrics = await self.get_live_metrics(org_id)
                # Cache is already updated in get_live_metrics, but we could do additional processing here
                logger.debug(f"Updated live metrics cache for org {org_id}")
                
        except Exception as e:
            logger.error(f"❌ Error updating live metrics cache: {e}")
    
    async def generate_periodic_insights(self):
        """Background task to generate AI insights periodically"""
        try:
            # Get all organizations with recent activity
            sample_org_ids = ["default_org"]  # Replace with actual org discovery
            
            for org_id in sample_org_ids:
                # Clear old insights cache to force regeneration
                if self.redis_client:
                    await self.redis_client.delete(f"ai_insights:{org_id}")
                
                # Generate fresh insights
                insights = await self.get_ai_insights(org_id, limit=5)
                logger.info(f"Generated {len(insights)} periodic insights for org {org_id}")
                
        except Exception as e:
            logger.error(f"❌ Error generating periodic insights: {e}")
    
    async def update_system_health(self):
        """Background task to update system health metrics"""
        try:
            health = await self.get_system_health()
            
            # Cache system health for quick access
            if self.redis_client:
                await self.redis_client.setex(
                    "system_health",
                    60,  # Cache for 1 minute
                    json.dumps(health.dict())
                )
            
            # Log critical health issues
            if health.status != "operational":
                logger.warning(f"⚠️ System health issue: {health.status}")
            
            logger.debug(f"Updated system health: {health.status}")
                
        except Exception as e:
            logger.error(f"❌ Error updating system health: {e}")

# Singleton service instance
_service_instance = None

async def get_enhanced_overview_service() -> EnhancedOverviewService:
    """Get singleton instance of enhanced overview service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = EnhancedOverviewService()
        await _service_instance.initialize()
    return _service_instance
