#!/usr/bin/env python3
"""
🌍 Vocelio.ai Overview Service
Enterprise-grade real-time metrics and dashboard data service

This service provides:
- Live metrics for the main dashboard
- Real-time performance tracking
- System health monitoring
- Revenue and client analytics
- AI optimization scoring
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json
import redis
import asyncpg
import logging
from contextlib import asynccontextmanager
import os
from dataclasses import dataclass
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
    status: str = Field(..., description="Overall system status")
    uptime: float = Field(..., description="System uptime percentage")
    services_online: int = Field(..., description="Number of services online")
    total_services: int = Field(..., description="Total number of services")
    last_check: datetime = Field(default_factory=datetime.now)

class RevenueMetrics(BaseModel):
    """Revenue tracking metrics"""
    daily_revenue: float
    monthly_revenue: float
    yearly_revenue: float
    revenue_growth: float
    top_revenue_sources: List[Dict[str, Any]]
    projected_monthly: float

class AIInsight(BaseModel):
    """AI-generated insights for optimization"""
    id: str
    title: str
    description: str
    confidence: float
    impact_estimate: str
    action_type: str
    priority: str
    timestamp: datetime = Field(default_factory=datetime.now)

class GlobalStats(BaseModel):
    """Global platform statistics"""
    total_ai_agents: int = 247
    industries_covered: int = 89
    global_success_rate: float = 94.7
    monthly_call_volume: int = 89500000
    total_revenue: float = 47000000
    system_uptime: float = 99.99

# Database and Redis connections
class DatabaseManager:
    def __init__(self):
        self.pg_pool = None
        self.redis_client = None
    
    async def initialize(self):
        """Initialize database connections"""
        try:
            # PostgreSQL connection
            # Support both legacy DATABASE_* and current POSTGRES_* naming, prefer POSTGRES_*
            pg_host = os.getenv("POSTGRES_HOST") or os.getenv("DATABASE_HOST") or "postgres"
            pg_port = int(os.getenv("POSTGRES_PORT") or os.getenv("DATABASE_PORT") or 5432)
            pg_user = os.getenv("POSTGRES_USER") or os.getenv("DATABASE_USER") or "postgres"
            pg_pass = os.getenv("POSTGRES_PASSWORD") or os.getenv("DATABASE_PASSWORD") or "password"
            pg_db   = os.getenv("POSTGRES_DB") or os.getenv("DATABASE_NAME") or "vocelio"

            self.pg_pool = await asyncpg.create_pool(
                host=pg_host,
                port=pg_port,
                user=pg_user,
                password=pg_pass,
                database=pg_db,
                min_size=2,
                max_size=10
            )
            
            # Redis connection
            redis_host = os.getenv("REDIS_HOST", "redis")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_pass = os.getenv("REDIS_PASSWORD", None)
            self.redis_client = redis.asyncio.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_pass,
                decode_responses=True
            )
            
            logger.info("✅ Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connections: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            await self.redis_client.close()

db = DatabaseManager()

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
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
            
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"❌ Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Vocelio Overview Service...")
    await db.initialize()
    
    # Start background tasks
    asyncio.create_task(live_metrics_updater())
    asyncio.create_task(ai_insights_generator())
    
    logger.info("✅ Overview Service started successfully")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Overview Service...")
    await db.close()

# FastAPI app
app = FastAPI(
    title="🌍 Vocelio.ai Overview Service",
    description="Enterprise-grade real-time metrics and dashboard data service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service functions
async def generate_live_metrics() -> LiveMetrics:
    """Generate realistic live metrics with some variance"""
    base_time = datetime.now()
    
    # Simulate realistic metrics with small variations
    return LiveMetrics(
        total_clients=random.randint(125000, 135000),
        active_calls=random.randint(8500, 12500),
        calls_today=random.randint(285000, 315000),
        revenue_today=random.uniform(1800000, 2200000),
        success_rate=random.uniform(92.5, 97.8),
        ai_optimization_score=random.uniform(94.0, 98.5),
        system_uptime=random.uniform(99.95, 99.99),
        monthly_call_volume=random.randint(88000000, 91000000),
        agents_active=random.randint(245, 247),
        campaigns_running=random.randint(87, 91),
        last_updated=base_time
    )

async def get_system_health() -> SystemHealth:
    """Get current system health status"""
    return SystemHealth(
        status="operational",
        uptime=random.uniform(99.95, 99.99),
        services_online=random.randint(17, 18),
        total_services=18,
        last_check=datetime.now()
    )

async def generate_ai_insights() -> List[AIInsight]:
    """Generate AI insights for optimization"""
    insights = [
        AIInsight(
            id="insight_1",
            title="🚀 Ultra Performance Boost",
            description='Switch 89% of Solar campaigns to "Confident Mike" voice for immediate 34% success boost',
            confidence=97.0,
            impact_estimate="+$2.3M revenue impact",
            action_type="voice_optimization",
            priority="high"
        ),
        AIInsight(
            id="insight_2",
            title="⏰ Global Timing Optimization",
            description="Peak performance window detected: 2:00-4:00 PM EST across all time zones",
            confidence=94.0,
            impact_estimate="+67% answer rate",
            action_type="timing_optimization",
            priority="medium"
        ),
        AIInsight(
            id="insight_3",
            title="🎯 High-Value Prospect Alert",
            description="2,847 ultra-high-value prospects detected with 95%+ booking probability",
            confidence=91.0,
            impact_estimate="$47M potential value",
            action_type="prospect_prioritization",
            priority="high"
        )
    ]
    return insights

async def live_metrics_updater():
    """Background task to update live metrics every 2 seconds"""
    while True:
        try:
            metrics = await generate_live_metrics()
            
            # Cache in Redis
            if db.redis_client:
                await db.redis_client.setex(
                    "live_metrics", 
                    10, 
                    metrics.model_dump_json()
                )
            
            # Broadcast to WebSocket clients
            await manager.broadcast({
                "type": "live_metrics",
                "data": metrics.model_dump()
            })
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"❌ Error updating live metrics: {e}")
            await asyncio.sleep(5)

async def ai_insights_generator():
    """Background task to generate AI insights every 30 seconds"""
    while True:
        try:
            insights = await generate_ai_insights()
            
            # Cache in Redis
            if db.redis_client:
                await db.redis_client.setex(
                    "ai_insights", 
                    60, 
                    json.dumps([insight.model_dump() for insight in insights], default=str)
                )
            
            # Broadcast to WebSocket clients
            await manager.broadcast({
                "type": "ai_insights",
                "data": [{**insight.model_dump(), "timestamp": insight.timestamp.isoformat()} for insight in insights]
            })
            
            await asyncio.sleep(30)  # Generate every 30 seconds
            
        except Exception as e:
            logger.exception(f"❌ Error generating AI insights: {e}")
            await asyncio.sleep(60)

# API Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Service health check"""
    return {
        "service": "Vocelio Overview Service",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "description": "🌍 World's #1 AI Call Center - Overview Service"
    }

@app.get("/health", response_model=SystemHealth)
async def health_check():
    """Get system health status"""
    return await get_system_health()

@app.get("/metrics/live", response_model=LiveMetrics)
async def get_live_metrics():
    """Get current live metrics"""
    try:
        # Try to get from Redis cache first
        if db.redis_client:
            cached = await db.redis_client.get("live_metrics")
            if cached:
                return LiveMetrics.model_validate_json(cached)
        
        # Generate fresh metrics if not cached
        return await generate_live_metrics()
        
    except Exception as e:
        logger.error(f"❌ Error getting live metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve live metrics")

@app.get("/metrics/revenue", response_model=RevenueMetrics)
async def get_revenue_metrics():
    """Get revenue metrics"""
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

@app.get("/insights/ai", response_model=List[AIInsight])
async def get_ai_insights():
    """Get AI-generated insights"""
    try:
        # Try to get from Redis cache first
        if db.redis_client:
            cached = await db.redis_client.get("ai_insights")
            if cached:
                insights_data = json.loads(cached)
                return [AIInsight.model_validate(data) for data in insights_data]
        
        # Generate fresh insights if not cached
        return await generate_ai_insights()
        
    except Exception as e:
        logger.error(f"❌ Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve AI insights")

@app.get("/stats/global", response_model=GlobalStats)
async def get_global_stats():
    """Get global platform statistics"""
    return GlobalStats()

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            try:
                data = await websocket.receive_text()
                # Handle any incoming WebSocket messages if needed
                logger.info(f"📡 Received WebSocket message: {data}")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

# Admin endpoints for testing
@app.post("/admin/test/broadcast")
async def test_broadcast(message: Dict[str, Any]):
    """Test endpoint to broadcast custom messages"""
    await manager.broadcast(message)
    return {"status": "Message broadcasted", "connections": len(manager.active_connections)}

@app.get("/admin/connections")
async def get_connections():
    """Get number of active WebSocket connections"""
    return {"active_connections": len(manager.active_connections)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
    reload=False,
        log_level="info"
    )
