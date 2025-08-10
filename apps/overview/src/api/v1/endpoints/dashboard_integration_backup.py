"""
🎯 Dashboard Integration Endpoints
Comprehensive API endpoints that aggregate data from all microservices
for the Vocelio dashboard frontend integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import httpx
import logging

# Mock user dependency for testing - replace with real auth in production
def get_current_user():
    return {
        "user_id": "user_123",
        "name": "Dashboard User",
        "email": "user@vocelio.ai",
        "plan": "Pro",
        "access_token": "mock_token_123"
    }

logger = logging.getLogger(__name__)
router = APIRouter()

# Service URLs (these should come from environment variables in production)
SERVICE_URLS = {
    "agents": "https://ai-agents-production.up.railway.app",
    "campaigns": "https://smart-campaigns-production.up.railway.app", 
    "call_center": "https://call-center-production.up.railway.app",
    "voice_lab": "https://voice-lab-production.up.railway.app",
    "analytics": "https://analytics-pro-production.up.railway.app",
    "billing": "https://billing-pro-production.up.railway.app",
    "agent_store": "https://agent-store-production.up.railway.app",
    "integrations": "https://integrations-production.up.railway.app",
    "team_hub": "https://team-hub-production.up.railway.app",
    "phone_numbers": "https://phone-numbers-production.up.railway.app",
    "flow_builder": "https://flow-builder-production.up.railway.app",
    "ai_brain": "https://ai-brain-production.up.railway.app",
    "voice_marketplace": "https://voice-marketplace-production.up.railway.app",
    "lead_qualification": "https://lead-qualification-production.up.railway.app",
    "appointment_booking": "https://appointment-booking-production.up.railway.app",
    "inbound_calls": "https://inbound-calls-production.up.railway.app",
    "outbound_calls": "https://outbound-calls-production.up.railway.app",
    "knowledge_base": "https://knowledge-base-production.up.railway.app",
    "workflows": "https://workflows-production.up.railway.app",
    "developer_api": "https://developer-api-production.up.railway.app"
}

async def make_service_request(service: str, endpoint: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Make an HTTP request to a microservice"""
    try:
        base_url = SERVICE_URLS.get(service)
        if not base_url:
            logger.warning(f"Service URL not found for: {service}")
            return {"error": f"Service {service} not available"}
        
        url = f"{base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers or {})
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Service {service} returned {response.status_code}")
                return {"error": f"Service {service} error: {response.status_code}"}
    except Exception as e:
        logger.error(f"Error calling service {service}: {str(e)}")
        return {"error": f"Service {service} unavailable"}

@router.get("/overview", summary="Complete Dashboard Overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard overview aggregating data from all services.
    This is the main endpoint that powers the dashboard home page.
    """
    try:
        # Prepare headers with user authentication
        headers = {
            "Authorization": f"Bearer {current_user.get('access_token', '')}",
            "X-User-ID": str(current_user.get("user_id", ""))
        }
        
        # Make concurrent requests to all services
        tasks = []
        
        # Core metrics from various services
        tasks.extend([
            make_service_request("agents", "/api/v1/agents?limit=5", headers),
            make_service_request("campaigns", "/api/v1/campaigns?limit=5", headers),
            make_service_request("call_center", "/api/v1/calls/recent?limit=10", headers),
            make_service_request("analytics", "/api/v1/analytics/summary", headers),
            make_service_request("billing", "/api/v1/billing/usage", headers),
            make_service_request("voice_lab", "/api/v1/voices?limit=3", headers),
            make_service_request("integrations", "/api/v1/integrations/status", headers),
            make_service_request("team_hub", "/api/v1/team/members", headers),
            make_service_request("phone_numbers", "/api/v1/numbers", headers),
            make_service_request("ai_brain", "/api/v1/brain/status", headers)
        ])
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        (agents_data, campaigns_data, calls_data, analytics_data, 
         billing_data, voices_data, integrations_data, team_data, 
         numbers_data, ai_brain_data) = results
        
        # Build comprehensive overview response
        overview = {
            "user_info": {
                "user_id": current_user.get("user_id"),
                "name": current_user.get("name", "User"),
                "email": current_user.get("email"),
                "plan": current_user.get("plan", "Pro"),
                "last_login": datetime.now().isoformat()
            },
            "quick_stats": {
                "total_agents": len(agents_data.get("agents", [])) if isinstance(agents_data, dict) else 0,
                "active_campaigns": len(campaigns_data.get("campaigns", [])) if isinstance(campaigns_data, dict) else 0,
                "total_calls_today": calls_data.get("total_today", 0) if isinstance(calls_data, dict) else 0,
                "monthly_usage": billing_data.get("current_usage", 0) if isinstance(billing_data, dict) else 0,
                "available_voices": len(voices_data.get("voices", [])) if isinstance(voices_data, dict) else 0,
                "active_integrations": len(integrations_data.get("active", [])) if isinstance(integrations_data, dict) else 0,
                "team_members": len(team_data.get("members", [])) if isinstance(team_data, dict) else 0,
                "phone_numbers": len(numbers_data.get("numbers", [])) if isinstance(numbers_data, dict) else 0
            },
            "recent_activity": {
                "recent_calls": calls_data.get("recent_calls", [])[:5] if isinstance(calls_data, dict) else [],
                "latest_agents": agents_data.get("agents", [])[:3] if isinstance(agents_data, dict) else [],
                "active_campaigns": campaigns_data.get("campaigns", [])[:3] if isinstance(campaigns_data, dict) else []
            },
            "performance_metrics": {
                "call_success_rate": analytics_data.get("call_success_rate", 0) if isinstance(analytics_data, dict) else 0,
                "average_call_duration": analytics_data.get("avg_call_duration", 0) if isinstance(analytics_data, dict) else 0,
                "conversion_rate": analytics_data.get("conversion_rate", 0) if isinstance(analytics_data, dict) else 0,
                "customer_satisfaction": analytics_data.get("satisfaction_score", 0) if isinstance(analytics_data, dict) else 0
            },
            "system_status": {
                "ai_brain_status": "online" if ai_brain_data.get("status") == "healthy" else "offline",
                "call_center_status": "online" if calls_data.get("status") == "healthy" else "offline", 
                "billing_status": "online" if billing_data.get("status") == "healthy" else "offline",
                "last_updated": datetime.now().isoformat()
            },
            "alerts_notifications": [
                {
                    "id": 1,
                    "type": "info",
                    "title": "System Update",
                    "message": "New AI models available in Voice Lab",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": 2, 
                    "type": "warning",
                    "title": "Usage Alert",
                    "message": "Approaching monthly limit (85% used)",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
                }
            ]
        }
        
        return overview
        
    except Exception as e:
        logger.error("Error generating dashboard overview", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate dashboard overview")

@router.get("/analytics", summary="Dashboard Analytics Summary")
async def get_dashboard_analytics(
    timeRange: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d"),
    current_user: User = Depends(get_current_user)
):
    """Get analytics data for dashboard charts and metrics."""
    try:
        headers = {
            "Authorization": f"Bearer {current_user.get('access_token', '')}",
            "X-User-ID": str(current_user.get("user_id", ""))
        }
        
        # Get analytics from multiple services
        tasks = [
            make_service_request("analytics", f"/api/v1/analytics/calls?range={timeRange}", headers),
            make_service_request("analytics", f"/api/v1/analytics/performance?range={timeRange}", headers),
            make_service_request("billing", f"/api/v1/billing/usage?range={timeRange}", headers),
            make_service_request("campaigns", f"/api/v1/campaigns/metrics?range={timeRange}", headers),
            make_service_request("call_center", f"/api/v1/calls/analytics?range={timeRange}", headers)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        calls_analytics, performance_analytics, billing_analytics, campaign_metrics, call_metrics = results
        
        # Generate mock data for demonstration (replace with real data)
        analytics = {
            "time_range": timeRange,
            "call_volume": {
                "total_calls": call_metrics.get("total_calls", 1250) if isinstance(call_metrics, dict) else 1250,
                "successful_calls": call_metrics.get("successful_calls", 1187) if isinstance(call_metrics, dict) else 1187,
                "failed_calls": call_metrics.get("failed_calls", 63) if isinstance(call_metrics, dict) else 63,
                "daily_breakdown": [
                    {"date": "2024-01-01", "calls": 178, "successful": 169, "failed": 9},
                    {"date": "2024-01-02", "calls": 195, "successful": 185, "failed": 10},
                    {"date": "2024-01-03", "calls": 156, "successful": 148, "failed": 8},
                    {"date": "2024-01-04", "calls": 203, "successful": 194, "failed": 9},
                    {"date": "2024-01-05", "calls": 187, "successful": 177, "failed": 10},
                    {"date": "2024-01-06", "calls": 165, "successful": 157, "failed": 8},
                    {"date": "2024-01-07", "calls": 166, "successful": 157, "failed": 9}
                ]
            },
            "performance_metrics": {
                "average_call_duration": performance_analytics.get("avg_duration", 185) if isinstance(performance_analytics, dict) else 185,
                "conversion_rate": performance_analytics.get("conversion_rate", 23.5) if isinstance(performance_analytics, dict) else 23.5,
                "customer_satisfaction": performance_analytics.get("satisfaction", 4.2) if isinstance(performance_analytics, dict) else 4.2,
                "response_time": performance_analytics.get("response_time", 1.8) if isinstance(performance_analytics, dict) else 1.8
            },
            "revenue_metrics": {
                "total_revenue": billing_analytics.get("revenue", 12450) if isinstance(billing_analytics, dict) else 12450,
                "cost_per_call": billing_analytics.get("cost_per_call", 0.85) if isinstance(billing_analytics, dict) else 0.85,
                "roi": billing_analytics.get("roi", 340) if isinstance(billing_analytics, dict) else 340
            },
            "campaign_performance": {
                "active_campaigns": campaign_metrics.get("active", 8) if isinstance(campaign_metrics, dict) else 8,
                "best_performing": campaign_metrics.get("best", "Sales Q1 Outreach") if isinstance(campaign_metrics, dict) else "Sales Q1 Outreach",
                "total_leads": campaign_metrics.get("leads", 456) if isinstance(campaign_metrics, dict) else 456,
                "qualified_leads": campaign_metrics.get("qualified", 234) if isinstance(campaign_metrics, dict) else 234
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error("Error generating dashboard analytics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate analytics")

@router.get("/services/health", summary="All Services Health Check")
async def get_services_health(current_user: User = Depends(get_current_user)):
    """Get health status of all microservices for dashboard monitoring."""
    try:
        # Check health of all services concurrently
        health_tasks = []
        for service_name, base_url in SERVICE_URLS.items():
            health_tasks.append(make_service_request(service_name, "/health"))
        
        results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        # Process health check results
        services_health = {}
        for i, (service_name, base_url) in enumerate(SERVICE_URLS.items()):
            result = results[i]
            if isinstance(result, dict) and not result.get("error"):
                services_health[service_name] = {
                    "status": "healthy",
                    "response_time": result.get("response_time", 0),
                    "last_check": datetime.now().isoformat(),
                    "url": base_url
                }
            else:
                services_health[service_name] = {
                    "status": "unhealthy", 
                    "error": result.get("error", "Unknown error"),
                    "last_check": datetime.now().isoformat(),
                    "url": base_url
                }
        
        # Calculate overall system health
        healthy_services = sum(1 for s in services_health.values() if s["status"] == "healthy")
        total_services = len(services_health)
        system_health_percentage = (healthy_services / total_services) * 100
        
        return {
            "system_health": {
                "overall_status": "healthy" if system_health_percentage >= 80 else "degraded" if system_health_percentage >= 60 else "unhealthy",
                "health_percentage": round(system_health_percentage, 1),
                "healthy_services": healthy_services,
                "total_services": total_services,
                "last_updated": datetime.now().isoformat()
            },
            "services": services_health,
            "summary": {
                "critical_services": ["agents", "call_center", "billing", "ai_brain"],
                "optional_services": ["agent_store", "voice_marketplace", "integrations"],
                "maintenance_windows": [],
                "incidents": []
            }
        }
        
    except Exception as e:
        logger.error("Error checking services health", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to check services health")

@router.get("/recent-activity", summary="Recent Activity Feed")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get recent activity across all services for dashboard activity feed."""
    try:
        headers = {
            "Authorization": f"Bearer {current_user.get('access_token', '')}",
            "X-User-ID": str(current_user.get("user_id", ""))
        }
        
        # Get recent activity from various services
        tasks = [
            make_service_request("call_center", f"/api/v1/calls/recent?limit={limit//4}", headers),
            make_service_request("agents", f"/api/v1/agents/recent?limit={limit//4}", headers),
            make_service_request("campaigns", f"/api/v1/campaigns/activity?limit={limit//4}", headers),
            make_service_request("team_hub", f"/api/v1/team/activity?limit={limit//4}", headers)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate activity from all services
        activities = []
        
        # Mock recent activity data (replace with real data from services)
        activities.extend([
            {
                "id": "act_001",
                "type": "call_completed",
                "title": "Call completed successfully",
                "description": "Sales call with John Doe completed with positive outcome",
                "service": "call_center",
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "user": "Sarah Wilson",
                "metadata": {"duration": "8m 45s", "outcome": "positive"}
            },
            {
                "id": "act_002", 
                "type": "agent_created",
                "title": "New AI agent deployed",
                "description": "Customer Support Agent v2.1 deployed successfully",
                "service": "agents",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "user": "Mike Johnson",
                "metadata": {"agent_id": "agt_123", "version": "2.1"}
            },
            {
                "id": "act_003",
                "type": "campaign_started", 
                "title": "Campaign launched",
                "description": "Q1 Lead Generation campaign started with 500 contacts",
                "service": "campaigns",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "user": "Emily Chen",
                "metadata": {"campaign_id": "camp_456", "contacts": 500}
            },
            {
                "id": "act_004",
                "type": "team_member_added",
                "title": "Team member added",
                "description": "Alex Rodriguez joined the Sales team",
                "service": "team_hub", 
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "user": "Admin",
                "metadata": {"team": "Sales", "role": "Agent"}
            }
        ])
        
        # Sort by timestamp (most recent first) and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:limit]
        
        return {
            "activities": activities,
            "total_count": len(activities),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting recent activity", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get recent activity")

@router.post("/refresh-data", summary="Refresh Dashboard Data")
async def refresh_dashboard_data(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Trigger refresh of dashboard data from all services."""
    try:
        # Add background task to refresh cached data
        background_tasks.add_task(refresh_all_service_data, current_user)
        
        return {
            "message": "Dashboard data refresh initiated",
            "status": "processing",
            "estimated_completion": (datetime.now() + timedelta(seconds=30)).isoformat()
        }
        
    except Exception as e:
        logger.error("Error initiating dashboard refresh", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to initiate data refresh")

async def refresh_all_service_data(user: User):
    """Background task to refresh data from all services."""
    try:
        logger.info(f"Starting dashboard data refresh for user {user.get('user_id')}")
        
        headers = {
            "Authorization": f"Bearer {user.get('access_token', '')}",
            "X-User-ID": str(user.get("user_id", ""))
        }
        
        # Refresh data from all services
        refresh_tasks = []
        for service_name in SERVICE_URLS.keys():
            refresh_tasks.append(make_service_request(service_name, "/api/v1/refresh", headers))
        
        await asyncio.gather(*refresh_tasks, return_exceptions=True)
        
        logger.info(f"Dashboard data refresh completed for user {user.get('user_id')}")
        
    except Exception as e:
        logger.error(f"Error during dashboard data refresh: {str(e)}")

@router.get("/notifications", summary="Dashboard Notifications")
async def get_dashboard_notifications(
    limit: int = Query(10, ge=1, le=50),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """Get notifications for dashboard notification center."""
    try:
        # Mock notifications (replace with real notification service)
        notifications = [
            {
                "id": "notif_001",
                "type": "system",
                "priority": "high",
                "title": "System Maintenance Scheduled",
                "message": "Scheduled maintenance on Jan 15th, 2-4 AM EST",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "read": False,
                "action_url": "/maintenance"
            },
            {
                "id": "notif_002",
                "type": "billing",
                "priority": "medium", 
                "title": "Usage Alert",
                "message": "You've used 85% of your monthly call minutes",
                "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                "read": False,
                "action_url": "/billing/usage"
            },
            {
                "id": "notif_003",
                "type": "feature",
                "priority": "low",
                "title": "New Feature Available",
                "message": "Enhanced voice cloning is now available in Voice Lab",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "read": True,
                "action_url": "/voice-lab"
            }
        ]
        
        # Filter unread if requested
        if unread_only:
            notifications = [n for n in notifications if not n["read"]]
        
        # Limit results
        notifications = notifications[:limit]
        
        return {
            "notifications": notifications,
            "unread_count": sum(1 for n in notifications if not n["read"]),
            "total_count": len(notifications)
        }
        
    except Exception as e:
        logger.error("Error getting notifications", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get notifications")
