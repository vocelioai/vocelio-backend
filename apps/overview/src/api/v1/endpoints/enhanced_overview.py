# apps/overview/src/api/v1/endpoints/enhanced_overview.py
"""
Enhanced Overview Endpoints - Unified API combining overview + overview-service
Provides comprehensive dashboard functionality with real-time features
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging
import asyncio
import json

from services.enhanced_overview_service import EnhancedOverviewService, get_enhanced_overview_service
from schemas.enhanced_overview import (
    DashboardOverview, LiveMetrics, SystemHealth, RevenueMetrics, AIInsight,
    GlobalStats, LiveStats, WebSocketMessage, LiveUpdateMessage,
    DashboardFilter, AnalyticsRequest, AnalyticsResponse, CacheStatus,
    PerformanceMetrics
)
from shared.auth.dependencies import get_current_user, get_organization_id
from shared.schemas.response import APIResponse, ErrorResponse
from shared.exceptions.service import ServiceException

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.organization_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, organization_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if organization_id not in self.organization_connections:
            self.organization_connections[organization_id] = []
        self.organization_connections[organization_id].append(websocket)
        
        logger.info(f"📡 WebSocket connected for org {organization_id}. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, organization_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if organization_id in self.organization_connections:
            if websocket in self.organization_connections[organization_id]:
                self.organization_connections[organization_id].remove(websocket)
        
        logger.info(f"📡 WebSocket disconnected for org {organization_id}. Total: {len(self.active_connections)}")
    
    async def broadcast_to_organization(self, organization_id: str, message: dict):
        """Broadcast message to all connections for an organization"""
        if organization_id not in self.organization_connections:
            return
        
        connections = self.organization_connections[organization_id].copy()
        disconnected = []
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"❌ Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, organization_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"❌ Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            # Find organization for this connection and disconnect properly
            for org_id, org_connections in self.organization_connections.items():
                if connection in org_connections:
                    self.disconnect(connection, org_id)
                    break

manager = ConnectionManager()

# Dashboard Overview Endpoints
@router.get(
    "/dashboard/overview",
    response_model=APIResponse[DashboardOverview],
    summary="Get dashboard overview",
    description="Get complete dashboard overview with live metrics, AI insights, and system health"
)
async def get_dashboard_overview(
    user_id: str = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get complete dashboard overview"""
    try:
        overview = await service.get_dashboard_overview(organization_id)
        
        return APIResponse(
            data=overview,
            message="Dashboard overview retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard overview"
        )

# Live Metrics Endpoints (from overview-service)
@router.get(
    "/metrics/live",
    response_model=APIResponse[LiveMetrics],
    summary="Get live metrics",
    description="Get real-time live metrics for the dashboard"
)
async def get_live_metrics(
    organization_id: str = Depends(get_organization_id),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get current live metrics"""
    try:
        metrics = await service.get_live_metrics(organization_id)
        
        return APIResponse(
            data=metrics,
            message="Live metrics retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting live metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get live metrics"
        )

@router.get(
    "/metrics/revenue",
    response_model=APIResponse[RevenueMetrics],
    summary="Get revenue metrics",
    description="Get detailed revenue tracking metrics"
)
async def get_revenue_metrics(
    organization_id: str = Depends(get_organization_id),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get revenue metrics"""
    try:
        metrics = await service.get_revenue_metrics(organization_id)
        
        return APIResponse(
            data=metrics,
            message="Revenue metrics retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting revenue metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get revenue metrics"
        )

# System Health Endpoints
@router.get(
    "/health/system",
    response_model=APIResponse[SystemHealth],
    summary="Get system health",
    description="Get comprehensive system health status and metrics"
)
async def get_system_health(
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get system health status"""
    try:
        health = await service.get_system_health()
        
        return APIResponse(
            data=health,
            message="System health retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting system health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health"
        )

# AI Insights Endpoints (enhanced from both services)
@router.get(
    "/insights/ai",
    response_model=APIResponse[List[AIInsight]],
    summary="Get AI insights",
    description="Get AI-generated insights and recommendations"
)
async def get_ai_insights(
    limit: int = 10,
    priority: Optional[str] = None,
    organization_id: str = Depends(get_organization_id),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get AI-generated insights"""
    try:
        insights = await service.get_ai_insights(organization_id, limit, priority)
        
        return APIResponse(
            data=insights,
            message=f"Retrieved {len(insights)} AI insights",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting AI insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI insights"
        )

# Live Stats Endpoints (from overview)
@router.get(
    "/stats/live",
    response_model=APIResponse[LiveStats],
    summary="Get live stats",
    description="Get live statistics for real-time updates"
)
async def get_live_stats(
    organization_id: str = Depends(get_organization_id),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get live statistics"""
    try:
        stats = await service.get_live_stats(organization_id)
        
        return APIResponse(
            data=stats,
            message="Live stats retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting live stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get live stats"
        )

# Global Stats Endpoints (from overview-service)
@router.get(
    "/stats/global",
    response_model=APIResponse[GlobalStats],
    summary="Get global stats",
    description="Get global platform statistics"
)
async def get_global_stats(
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get global platform statistics"""
    try:
        stats = await service.get_global_stats()
        
        return APIResponse(
            data=stats,
            message="Global stats retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting global stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get global stats"
        )

# Analytics Endpoints
@router.post(
    "/analytics/request",
    response_model=APIResponse[AnalyticsResponse],
    summary="Request analytics data",
    description="Request custom analytics data with specific parameters"
)
async def request_analytics(
    analytics_request: AnalyticsRequest,
    user_id: str = Depends(get_current_user),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Request custom analytics data"""
    try:
        # TODO: Implement analytics data generation based on request
        response = AnalyticsResponse(
            organization_id=analytics_request.organization_id,
            time_range=analytics_request.time_range,
            data_points=[],  # Implement based on requirements
            summary={}  # Implement based on requirements
        )
        
        return APIResponse(
            data=response,
            message="Analytics data generated successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error generating analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics"
        )

# Cache Management Endpoints
@router.get(
    "/cache/status",
    response_model=APIResponse[CacheStatus],
    summary="Get cache status",
    description="Get cache performance and status information"
)
async def get_cache_status(
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Get cache status"""
    try:
        status_info = await service.get_cache_status()
        
        return APIResponse(
            data=status_info,
            message="Cache status retrieved successfully",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error getting cache status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cache status"
        )

@router.post(
    "/cache/clear",
    response_model=APIResponse[Dict[str, bool]],
    summary="Clear cache",
    description="Clear cache entries (admin only)"
)
async def clear_cache(
    pattern: str = "*",
    user_id: str = Depends(get_current_user),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Clear cache entries"""
    try:
        # TODO: Add admin permission check
        success = await service.clear_cache(pattern)
        
        return APIResponse(
            data={"cleared": success},
            message="Cache cleared successfully" if success else "Failed to clear cache",
            status_code=status.HTTP_200_OK
        )
        
    except ServiceException as e:
        logger.error(f"Service error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )

# Background Task Triggers
@router.post(
    "/background/refresh-insights",
    response_model=APIResponse[Dict[str, str]],
    summary="Refresh AI insights",
    description="Trigger background refresh of AI insights"
)
async def refresh_ai_insights(
    background_tasks: BackgroundTasks,
    organization_id: str = Depends(get_organization_id),
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """Trigger AI insights refresh"""
    try:
        background_tasks.add_task(_refresh_insights_task, organization_id, service)
        
        return APIResponse(
            data={"status": "triggered"},
            message="AI insights refresh triggered",
            status_code=status.HTTP_202_ACCEPTED
        )
        
    except Exception as e:
        logger.error(f"Error triggering insights refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger insights refresh"
        )

# WebSocket Endpoints (from overview-service)
@router.websocket("/ws/{organization_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    organization_id: str,
    service: EnhancedOverviewService = Depends(get_enhanced_overview_service)
):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, organization_id)
    
    try:
        # Send initial data
        overview = await service.get_dashboard_overview(organization_id)
        await websocket.send_json({
            "type": "initial_data",
            "data": overview.dict(),
            "timestamp": overview.last_updated.isoformat()
        })
        
        # Keep connection alive and send updates
        while True:
            try:
                # Wait for any client message or timeout after 30 seconds
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send periodic update
                live_metrics = await service.get_live_metrics(organization_id)
                update_message = await service.generate_live_update_message(organization_id)
                await websocket.send_json(update_message.dict())
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, organization_id)

# Background task functions
async def _refresh_insights_task(organization_id: str, service: EnhancedOverviewService):
    """Background task to refresh AI insights"""
    try:
        # Clear cache and regenerate insights
        await service.clear_cache(f"ai_insights:{organization_id}")
        insights = await service.get_ai_insights(organization_id)
        
        # Broadcast new insights via WebSocket
        if insights:
            for insight in insights[:3]:  # Send top 3 new insights
                insight_message = await service.generate_insight_message(organization_id, insight)
                await manager.broadcast_to_organization(
                    organization_id, 
                    insight_message.dict()
                )
        
        logger.info(f"✅ Refreshed {len(insights)} AI insights for org {organization_id}")
        
    except Exception as e:
        logger.error(f"❌ Error refreshing insights: {e}")

# Periodic WebSocket updates (called by background tasks)
async def broadcast_live_updates():
    """Broadcast live updates to all connected clients"""
    try:
        service = await get_enhanced_overview_service()
        
        # Get all organizations with active connections
        for organization_id in manager.organization_connections.keys():
            if manager.organization_connections[organization_id]:  # Has active connections
                try:
                    update_message = await service.generate_live_update_message(organization_id)
                    await manager.broadcast_to_organization(
                        organization_id,
                        update_message.dict()
                    )
                except Exception as e:
                    logger.error(f"Error broadcasting to org {organization_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Error in broadcast_live_updates: {e}")

# Health check for the enhanced service
@router.get("/health/enhanced", tags=["health"])
async def enhanced_health_check():
    """Health check for enhanced overview service"""
    return {
        "status": "healthy",
        "service": "enhanced-overview",
        "version": "2.0.0",
        "features": [
            "Real-time WebSocket updates",
            "AI insights generation",
            "Advanced caching",
            "Live metrics tracking",
            "System health monitoring"
        ]
    }
