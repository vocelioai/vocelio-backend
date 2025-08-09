#!/usr/bin/env python3
"""
🌍 Vocelio.ai Overview Service - Test Version
Simplified version for testing without database dependencies
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json
import logging
from contextlib import asynccontextmanager
import random
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class LiveMetrics(BaseModel):
    """Real-time metrics for the dashboard"""
    total_clients: int = Field(..., description="Total active clients")
    active_calls: int = Field(..., description="Current active calls")
    calls_today: int = Field(..., description="Calls made today")
    revenue_today: float = Field(..., description="Revenue generated today")
    success_rate: float = Field(..., description="Overall success rate percentage")
    ai_optimization_score: float = Field(..., description="AI optimization score")
    system_uptime: float = Field(..., description="System uptime percentage")
    monthly_call_volume: int = Field(..., description="Monthly call volume")
    agents_active: int = Field(..., description="Number of active AI agents")
    campaigns_running: int = Field(..., description="Number of running campaigns")
    last_updated: datetime = Field(default_factory=datetime.now)

class SystemHealth(BaseModel):
    """System health status"""
    status: str = Field(..., description="System status")
    uptime: float = Field(..., description="System uptime percentage")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    active_connections: int = Field(..., description="Active database connections")

class AIInsight(BaseModel):
    """AI-generated insights"""
    insight_id: str = Field(..., description="Unique insight identifier")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact_score: float = Field(..., description="Potential impact score")
    category: str = Field(..., description="Insight category")
    suggested_action: str = Field(..., description="Suggested action")
    created_at: datetime = Field(default_factory=datetime.now)

class RevenueMetrics(BaseModel):
    """Revenue tracking metrics"""
    total_revenue: float = Field(..., description="Total revenue")
    revenue_today: float = Field(..., description="Today's revenue")
    revenue_this_month: float = Field(..., description="This month's revenue")
    revenue_growth: float = Field(..., description="Revenue growth percentage")
    avg_revenue_per_call: float = Field(..., description="Average revenue per call")
    top_performing_campaigns: List[Dict[str, Any]] = Field(default_factory=list)

# Mock data generators
def generate_live_metrics() -> LiveMetrics:
    """Generate realistic live metrics data"""
    return LiveMetrics(
        total_clients=random.randint(850, 950),
        active_calls=random.randint(45, 85),
        calls_today=random.randint(1200, 1800),
        revenue_today=round(random.uniform(8500, 12500), 2),
        success_rate=round(random.uniform(78, 95), 2),
        ai_optimization_score=round(random.uniform(85, 98), 2),
        system_uptime=round(random.uniform(99.5, 99.9), 2),
        monthly_call_volume=random.randint(28000, 35000),
        agents_active=random.randint(200, 247),
        campaigns_running=random.randint(25, 45)
    )

def generate_system_health() -> SystemHealth:
    """Generate system health data"""
    return SystemHealth(
        status="healthy",
        uptime=round(random.uniform(99.5, 99.9), 2),
        cpu_usage=round(random.uniform(15, 45), 2),
        memory_usage=round(random.uniform(25, 65), 2),
        active_connections=random.randint(10, 25)
    )

def generate_ai_insights() -> List[AIInsight]:
    """Generate AI insights"""
    insights = [
        {
            "title": "Peak Call Volume Optimization",
            "description": "Detected 23% higher success rates during 2-4 PM window",
            "category": "performance",
            "suggested_action": "Increase agent allocation during peak hours"
        },
        {
            "title": "Campaign A/B Test Results",
            "description": "Script variant B showing 18% better conversion rates",
            "category": "optimization",
            "suggested_action": "Deploy script variant B to all campaigns"
        },
        {
            "title": "Client Retention Opportunity",
            "description": "3 high-value clients showing decreased engagement",
            "category": "retention",
            "suggested_action": "Schedule personalized outreach calls"
        }
    ]
    
    return [
        AIInsight(
            insight_id=f"insight_{i+1}",
            title=insight["title"],
            description=insight["description"],
            impact_score=round(random.uniform(7.5, 9.5), 1),
            category=insight["category"],
            suggested_action=insight["suggested_action"]
        )
        for i, insight in enumerate(insights)
    ]

def generate_revenue_metrics() -> RevenueMetrics:
    """Generate revenue metrics"""
    return RevenueMetrics(
        total_revenue=round(random.uniform(245000, 285000), 2),
        revenue_today=round(random.uniform(8500, 12500), 2),
        revenue_this_month=round(random.uniform(78000, 95000), 2),
        revenue_growth=round(random.uniform(12, 28), 2),
        avg_revenue_per_call=round(random.uniform(6.50, 9.25), 2),
        top_performing_campaigns=[
            {"name": "Tech Startup Outreach", "revenue": 15680, "calls": 2840},
            {"name": "Healthcare Follow-ups", "revenue": 12340, "calls": 1920},
            {"name": "E-commerce Leads", "revenue": 9870, "calls": 1560}
        ]
    )

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"📡 WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"📡 WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection)

manager = ConnectionManager()

# Background task for real-time updates
async def update_metrics_task():
    """Background task to broadcast real-time metrics"""
    while True:
        try:
            metrics = generate_live_metrics()
            metrics_dict = metrics.model_dump()
            # Convert datetime to ISO format string
            metrics_dict['last_updated'] = metrics_dict['last_updated'].isoformat() if isinstance(metrics_dict['last_updated'], datetime) else metrics_dict['last_updated']
            
            await manager.broadcast(json.dumps({
                "type": "metrics_update",
                "data": metrics_dict,
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"❌ Error in metrics update task: {e}")
        
        await asyncio.sleep(5)  # Update every 5 seconds

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("🚀 Starting Vocelio Overview Service (Test Mode)...")
    
    # Start background tasks
    metrics_task = asyncio.create_task(update_metrics_task())
    
    yield
    
    # Cleanup
    metrics_task.cancel()
    logger.info("🛑 Vocelio Overview Service stopped")

# Initialize FastAPI app
app = FastAPI(
    title="Vocelio.ai Overview Service",
    description="Real-time metrics and dashboard data service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "overview",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Live metrics endpoint
@app.get("/api/v1/metrics/live", response_model=LiveMetrics)
async def get_live_metrics():
    """Get current live metrics"""
    return generate_live_metrics()

# System health endpoint
@app.get("/api/v1/system/health", response_model=SystemHealth)
async def get_system_health():
    """Get system health status"""
    return generate_system_health()

# AI insights endpoint
@app.get("/api/v1/ai/insights", response_model=List[AIInsight])
async def get_ai_insights():
    """Get AI-generated insights"""
    return generate_ai_insights()

# Revenue metrics endpoint
@app.get("/api/v1/revenue/metrics", response_model=RevenueMetrics)
async def get_revenue_metrics():
    """Get revenue metrics"""
    return generate_revenue_metrics()

# WebSocket endpoint for real-time updates
@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main_test:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
