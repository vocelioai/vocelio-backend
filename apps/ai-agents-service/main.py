#!/usr/bin/env python3
"""
🤖 Vocelio.ai AI Agents Service - MERGED & ENHANCED
Enterprise-grade AI agent management and orchestration service with world-class AI capabilities

This service provides:
- 247 AI agents management with advanced AI integration
- Ultimate AI model orchestration (Claude Opus 4.1, Sonnet 4, etc.)
- Performance analytics and AI-powered optimization
- A/B testing capabilities with intelligent recommendations
- Voice and personality management with AI enhancement
- Industry-specific agent configurations
- Real-time AI conversation capabilities
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import redis
import asyncpg
import logging
from contextlib import asynccontextmanager
import os
import uuid
import random
import uvicorn
import time
import psutil

# Service start time for uptime calculation
start_time = time.time()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our enhanced AI capabilities
try:
    from .src.ai_models import vocelio_ai, TaskType, optimize_agent_performance
    from .src.demo import ultimate_demo
    AI_ENABLED = True
    logger.info("🤖 AI models loaded successfully - Enhanced AI capabilities enabled")
except ImportError:
    logger.warning("AI models not available - running in basic mode")
    AI_ENABLED = False

# Import enhanced marketplace and management services
try:
    from .src.api.enhanced_endpoints import router as enhanced_router
    ENHANCED_FEATURES_ENABLED = True
    logger.info("🛒 Enhanced marketplace and management features loaded")
except ImportError:
    logger.warning("Enhanced features not available - running in basic mode")
    ENHANCED_FEATURES_ENABLED = False

# Enums
class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    OPTIMIZING = "optimizing"
    PAUSED = "paused"

class IndustryType(str, Enum):
    SOLAR = "solar"
    INSURANCE = "insurance"
    REAL_ESTATE = "real_estate"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    AUTOMOTIVE = "automotive"
    EDUCATION = "education"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    OTHER = "other"

class VoiceType(str, Enum):
    CONFIDENT_MIKE = "confident_mike"
    FRIENDLY_SARAH = "friendly_sarah"
    PROFESSIONAL_DAVID = "professional_david"
    ENERGETIC_JESSICA = "energetic_jessica"
    CALM_ROBERT = "calm_robert"
    PERSUASIVE_ANNA = "persuasive_anna"

# Pydantic Models
class AIAgent(BaseModel):
    """AI Agent model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    industry: IndustryType = Field(..., description="Target industry")
    voice_type: VoiceType = Field(..., description="Voice personality")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    performance_score: float = Field(default=0.0, ge=0.0, le=100.0)
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    total_calls: int = Field(default=0, ge=0)
    revenue_generated: float = Field(default=0.0, ge=0.0)
    last_active: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AgentPerformance(BaseModel):
    """Agent performance metrics"""
    agent_id: str
    calls_today: int
    calls_this_week: int
    calls_this_month: int
    success_rate: float
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float
    avg_call_duration: float
    conversion_rate: float
    customer_satisfaction: float

class AgentOptimization(BaseModel):
    """Agent optimization recommendation"""
    agent_id: str
    recommendation_type: str
    description: str
    expected_improvement: float
    confidence: float
    estimated_revenue_impact: float

class AgentAnalytics(BaseModel):
    """Agent analytics summary"""
    total_agents: int = 247
    active_agents: int = 245
    top_performers: List[AIAgent]
    industry_breakdown: Dict[str, int]
    performance_trends: Dict[str, float]
    optimization_opportunities: List[AgentOptimization]

class CreateAgentRequest(BaseModel):
    """Request to create a new AI agent"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    industry: IndustryType
    voice_type: VoiceType

class UpdateAgentRequest(BaseModel):
    """Request to update an AI agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[IndustryType] = None
    voice_type: Optional[VoiceType] = None
    status: Optional[AgentStatus] = None

# Database Manager
class DatabaseManager:
    def __init__(self):
        self.pg_pool = None
        self.redis_client = None

    async def initialize(self):
        """Initialize database connections with POSTGRES_* fallback"""
        try:
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

            # Initialize Redis connection (simplified for demo)
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    password=os.getenv("REDIS_PASSWORD", None),
                    decode_responses=True,
                    socket_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Redis connection successful")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}")
                self.redis_client = None

            logger.info("✅ Database connections initialized successfully (ai-agents)")

        except Exception as e:
            logger.error(f"❌ Failed to initialize database connections: {e}")
            raise

    async def close(self):
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            try:
                # For synchronous Redis client, no await needed
                self.redis_client.close()
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")

db = DatabaseManager()

# Agent Service
class AgentService:
    """AI Agent management service"""
    
    def __init__(self):
        self.agents: Dict[str, AIAgent] = {}
        self._initialize_demo_agents()
    
    def _initialize_demo_agents(self):
        """Initialize with demo agents for development"""
        demo_agents = [
            {
                "name": "Solar Sales Pro",
                "description": "Expert solar energy sales specialist with 95% success rate",
                "industry": IndustryType.SOLAR,
                "voice_type": VoiceType.CONFIDENT_MIKE,
                "performance_score": 95.8,
                "success_rate": 94.2,
                "total_calls": 15847,
                "revenue_generated": 3200000
            },
            {
                "name": "Insurance Advisor",
                "description": "Professional insurance consultant specializing in life and health policies",
                "industry": IndustryType.INSURANCE,
                "voice_type": VoiceType.PROFESSIONAL_DAVID,
                "performance_score": 92.4,
                "success_rate": 89.7,
                "total_calls": 12456,
                "revenue_generated": 2800000
            },
            {
                "name": "Real Estate Expert",
                "description": "Experienced real estate agent for property sales and investments",
                "industry": IndustryType.REAL_ESTATE,
                "voice_type": VoiceType.FRIENDLY_SARAH,
                "performance_score": 91.2,
                "success_rate": 87.3,
                "total_calls": 9876,
                "revenue_generated": 2100000
            },
            {
                "name": "Healthcare Navigator",
                "description": "Compassionate healthcare services coordinator",
                "industry": IndustryType.HEALTHCARE,
                "voice_type": VoiceType.CALM_ROBERT,
                "performance_score": 93.7,
                "success_rate": 91.5,
                "total_calls": 8234,
                "revenue_generated": 1950000
            },
            {
                "name": "Financial Consultant",
                "description": "Expert financial advisor for investment and planning services",
                "industry": IndustryType.FINANCIAL,
                "voice_type": VoiceType.PERSUASIVE_ANNA,
                "performance_score": 94.1,
                "success_rate": 90.8,
                "total_calls": 7654,
                "revenue_generated": 2300000
            }
        ]
        
        for agent_data in demo_agents:
            agent = AIAgent(**agent_data)
            self.agents[agent.id] = agent
    
    async def get_all_agents(self, 
                           industry: Optional[IndustryType] = None,
                           status: Optional[AgentStatus] = None,
                           limit: int = 50,
                           offset: int = 0) -> List[AIAgent]:
        """Get all agents with optional filtering"""
        agents = list(self.agents.values())
        
        # Apply filters
        if industry:
            agents = [a for a in agents if a.industry == industry]
        if status:
            agents = [a for a in agents if a.status == status]
        
        # Apply pagination
        return agents[offset:offset + limit]
    
    async def get_agent(self, agent_id: str) -> Optional[AIAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    async def create_agent(self, request: CreateAgentRequest) -> AIAgent:
        """Create a new AI agent"""
        agent = AIAgent(
            name=request.name,
            description=request.description,
            industry=request.industry,
            voice_type=request.voice_type
        )
        
        self.agents[agent.id] = agent
        
        # Cache in Redis
        if db.redis_client:
            await db.redis_client.setex(
                f"agent:{agent.id}",
                3600,
                agent.model_dump_json()
            )
        
        logger.info(f"✅ Created new agent: {agent.name} ({agent.id})")
        return agent
    
    async def update_agent(self, agent_id: str, request: UpdateAgentRequest) -> Optional[AIAgent]:
        """Update an existing agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.updated_at = datetime.now()
        
        # Update cache
        if db.redis_client:
            await db.redis_client.setex(
                f"agent:{agent.id}",
                3600,
                agent.model_dump_json()
            )
        
        logger.info(f"✅ Updated agent: {agent.name} ({agent.id})")
        return agent
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            
            # Remove from cache
            if db.redis_client:
                await db.redis_client.delete(f"agent:{agent.id}")
            
            logger.info(f"✅ Deleted agent: {agent.name} ({agent.id})")
            return True
        return False
    
    async def get_agent_performance(self, agent_id: str) -> Optional[AgentPerformance]:
        """Get detailed performance metrics for an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        # Generate realistic performance data
        return AgentPerformance(
            agent_id=agent_id,
            calls_today=random.randint(50, 200),
            calls_this_week=random.randint(300, 1200),
            calls_this_month=random.randint(1000, 4000),
            success_rate=agent.success_rate + random.uniform(-5, 5),
            revenue_today=random.uniform(5000, 25000),
            revenue_this_week=random.uniform(30000, 150000),
            revenue_this_month=random.uniform(120000, 500000),
            avg_call_duration=random.uniform(3.5, 8.2),
            conversion_rate=random.uniform(15, 35),
            customer_satisfaction=random.uniform(8.5, 9.8)
        )
    
    async def get_analytics(self) -> AgentAnalytics:
        """Get comprehensive agent analytics"""
        agents = list(self.agents.values())
        active_agents = [a for a in agents if a.status == AgentStatus.ACTIVE]
        
        # Top performers (top 5 by performance score)
        top_performers = sorted(agents, key=lambda x: x.performance_score, reverse=True)[:5]
        
        # Industry breakdown
        industry_breakdown = {}
        for agent in agents:
            industry = agent.industry.value
            industry_breakdown[industry] = industry_breakdown.get(industry, 0) + 1
        
        # Performance trends (mock data)
        performance_trends = {
            "success_rate_trend": random.uniform(2.5, 8.3),
            "revenue_growth": random.uniform(15.2, 28.7),
            "efficiency_improvement": random.uniform(5.1, 12.4),
            "customer_satisfaction": random.uniform(3.2, 7.8)
        }
        
        # Optimization opportunities
        optimization_opportunities = [
            AgentOptimization(
                agent_id=random.choice(agents).id,
                recommendation_type="voice_optimization",
                description="Switch to Confident Mike voice for 34% performance boost",
                expected_improvement=34.0,
                confidence=97.0,
                estimated_revenue_impact=2300000
            ),
            AgentOptimization(
                agent_id=random.choice(agents).id,
                recommendation_type="timing_optimization",
                description="Optimize call timing for 67% better answer rates",
                expected_improvement=67.0,
                confidence=94.0,
                estimated_revenue_impact=1800000
            )
        ]
        
        return AgentAnalytics(
            total_agents=len(agents),
            active_agents=len(active_agents),
            top_performers=top_performers,
            industry_breakdown=industry_breakdown,
            performance_trends=performance_trends,
            optimization_opportunities=optimization_opportunities
        )
    
    async def ai_optimize_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Use advanced AI to optimize agent performance"""
        if not AI_ENABLED:
            return {"error": "AI optimization not available", "fallback": True}
            
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        # Get current performance metrics
        performance = await self.get_agent_performance(agent_id)
        if not performance:
            return None
        
        # Convert to AI-friendly format
        agent_data = {
            "name": agent.name,
            "industry": agent.industry.value,
            "voice_type": agent.voice_type.value,
            "status": agent.status.value,
            "performance_score": agent.performance_score
        }
        
        performance_data = {
            "success_rate": performance.success_rate,
            "calls_total": performance.calls_this_month,
            "revenue_generated": performance.revenue_this_month,
            "avg_call_duration": performance.avg_call_duration,
            "conversion_rate": performance.conversion_rate,
            "customer_satisfaction": performance.customer_satisfaction
        }
        
        try:
            # Use advanced AI for optimization recommendations
            optimization = await optimize_agent_performance(agent_data, performance_data)
            
            logger.info(f"🤖 AI optimization completed for agent: {agent.name}")
            return {
                "agent_id": agent_id,
                "ai_optimization": optimization,
                "ai_enabled": True,
                "optimization_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"AI optimization failed: {e}")
            return {"error": str(e), "ai_enabled": False}
    
    async def ai_conversation_test(self, agent_id: str, test_scenario: str) -> Dict[str, Any]:
        """Test agent conversation using advanced AI"""
        if not AI_ENABLED:
            return {"error": "AI conversation testing not available"}
            
        agent = self.agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        try:
            # Use VocelioAI for intelligent conversation simulation
            context = [
                {"role": "system", "content": f"You are {agent.name}, a {agent.voice_type.value} voice in the {agent.industry.value} industry."},
                {"role": "user", "content": test_scenario}
            ]
            
            response = await vocelio_ai.customer_conversation(
                test_scenario, 
                context=context,
                priority="quality"
            )
            
            # AI-powered sentiment analysis of the response
            sentiment = await vocelio_ai.sentiment_analysis(response)
            
            return {
                "agent_id": agent_id,
                "test_scenario": test_scenario,
                "ai_response": response,
                "sentiment_analysis": sentiment,
                "conversation_quality": "world_class",
                "ai_model_used": "claude-sonnet-4",
                "test_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"AI conversation test failed: {e}")
            return {"error": str(e)}
    
    async def get_ai_insights(self) -> Dict[str, Any]:
        """Get AI-powered insights about agent performance and opportunities"""
        if not AI_ENABLED:
            return {"error": "AI insights not available"}
            
        try:
            # Get AI system status
            ai_status = await vocelio_ai.get_ai_status()
            
            # Analyze overall agent portfolio
            agents = list(self.agents.values())
            portfolio_data = {
                "total_agents": len(agents),
                "industries": [a.industry.value for a in agents],
                "voice_types": [a.voice_type.value for a in agents],
                "performance_scores": [a.performance_score for a in agents],
                "success_rates": [a.success_rate for a in agents]
            }
            
            # Get strategic AI analysis
            portfolio_analysis = await vocelio_ai.strategic_planning(
                f"AI agent portfolio analysis: {portfolio_data}",
                "Optimize agent portfolio for maximum performance and revenue"
            )
            
            return {
                "ai_system_status": ai_status,
                "portfolio_analysis": portfolio_analysis,
                "ai_recommendations": {
                    "top_priority": "Implement voice optimization for underperforming agents",
                    "revenue_opportunity": "$2.5M+ annual increase potential",
                    "optimization_timeline": "30-90 days",
                    "confidence": "world_class"
                },
                "insights_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {"error": str(e)}

agent_service = AgentService()

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Vocelio AI Agents Service...")
    await db.initialize()
    
    logger.info("✅ AI Agents Service started successfully")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Agents Service...")
    await db.close()

# FastAPI app
app = FastAPI(
    title="🤖 Vocelio.ai AI Agents Service",
    description="Enterprise-grade AI agent management and orchestration service",
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

# API Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Service health check"""
    return {
        "service": "Vocelio AI Agents Service",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "description": "🤖 247 AI Agents Management System"
    }

@app.get("/health")
async def enhanced_health_check():
    """Enhanced health check endpoint with comprehensive diagnostics"""
    
    # Service uptime calculation (since startup)
    uptime_seconds = time.time() - start_time
    
    # Get system metrics safely
    try:
        memory_usage = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Quick check
    except Exception as e:
        logger.warning(f"Failed to get system metrics: {e}")
        memory_usage = None
        disk_usage = None
        cpu_percent = 0
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": {
            "name": "ai-agents-service",
            "version": "1.0.0",
            "uptime_seconds": uptime_seconds,
            "uptime_human": str(timedelta(seconds=int(uptime_seconds))),
            "environment": os.getenv("ENVIRONMENT", "production")
        },
        "checks": {},
        "metrics": {
            "total_agents": 0,
            "active_agents": 0,
            "total_requests": 0,
            "avg_response_time_ms": 0
        }
    }
    
    # Memory check
    if memory_usage:
        health_data["checks"]["memory"] = {
            "status": "healthy" if memory_usage.percent < 80 else "degraded" if memory_usage.percent < 95 else "unhealthy",
            "usage_percent": memory_usage.percent,
            "available_gb": round(memory_usage.available / (1024**3), 2)
        }
    
    # Disk check
    if disk_usage:
        health_data["checks"]["disk"] = {
            "status": "healthy" if disk_usage.percent < 90 else "degraded" if disk_usage.percent < 98 else "unhealthy",
            "usage_percent": disk_usage.percent,
            "free_gb": round(disk_usage.free / (1024**3), 2)
        }
    
    # CPU check
    health_data["checks"]["cpu"] = {
        "status": "healthy" if cpu_percent < 80 else "degraded" if cpu_percent < 95 else "unhealthy",
        "usage_percent": cpu_percent
    }
    
    # Database check
    try:
        if hasattr(db, 'pg_pool') and db.pg_pool:
            health_data["checks"]["database"] = {"status": "healthy", "connected": True}
        else:
            health_data["checks"]["database"] = {"status": "degraded", "connected": False}
    except Exception:
        health_data["checks"]["database"] = {"status": "unhealthy", "connected": False}
    
    # Redis check
    try:
        if hasattr(db, 'redis_client') and db.redis_client:
            db.redis_client.ping()
            health_data["checks"]["redis"] = {"status": "healthy", "connected": True}
        else:
            health_data["checks"]["redis"] = {"status": "degraded", "connected": False}
    except Exception:
        health_data["checks"]["redis"] = {"status": "degraded", "connected": False}
    
    # Agent metrics
    try:
        if 'agent_service' in globals() and agent_service:
            health_data["metrics"]["total_agents"] = len(agent_service.agents)
            health_data["metrics"]["active_agents"] = len([a for a in agent_service.agents.values() if a.status == AgentStatus.ACTIVE])
    except Exception as e:
        logger.warning(f"Failed to get agent metrics: {e}")
    
    # Determine overall status based on checks
    degraded_checks = [check for check in health_data["checks"].values() if check.get("status") == "degraded"]
    unhealthy_checks = [check for check in health_data["checks"].values() if check.get("status") == "unhealthy"]
    
    if unhealthy_checks:
        health_data["status"] = "unhealthy"
        return JSONResponse(health_data, status_code=503)
    elif degraded_checks:
        health_data["status"] = "degraded"
        logger.warning(f"Service health degraded: {len(degraded_checks)} checks failing")
    
    return health_data

@app.get("/agents", response_model=List[AIAgent])
async def get_agents(
    industry: Optional[IndustryType] = Query(None, description="Filter by industry"),
    status: Optional[AgentStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of agents to return"),
    offset: int = Query(0, ge=0, description="Number of agents to skip")
):
    """Get all AI agents with optional filtering"""
    return await agent_service.get_all_agents(industry, status, limit, offset)

@app.get("/agents/{agent_id}", response_model=AIAgent)
async def get_agent(agent_id: str):
    """Get a specific AI agent"""
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.post("/agents", response_model=AIAgent)
async def create_agent(request: CreateAgentRequest):
    """Create a new AI agent"""
    return await agent_service.create_agent(request)

@app.put("/agents/{agent_id}", response_model=AIAgent)
async def update_agent(agent_id: str, request: UpdateAgentRequest):
    """Update an existing AI agent"""
    agent = await agent_service.update_agent(agent_id, request)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an AI agent"""
    success = await agent_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}

@app.get("/agents/{agent_id}/performance", response_model=AgentPerformance)
async def get_agent_performance(agent_id: str):
    """Get detailed performance metrics for an agent"""
    performance = await agent_service.get_agent_performance(agent_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Agent not found")
    return performance

@app.get("/analytics", response_model=AgentAnalytics)
async def get_analytics():
    """Get comprehensive agent analytics"""
    return await agent_service.get_analytics()

@app.post("/agents/{agent_id}/optimize")
async def optimize_agent(agent_id: str):
    """Trigger AI optimization for a specific agent"""
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent status to optimizing
    await agent_service.update_agent(agent_id, UpdateAgentRequest(status=AgentStatus.OPTIMIZING))
    
    # In a real implementation, this would trigger ML optimization
    # For now, simulate optimization with improved performance
    new_score = min(100.0, agent.performance_score + random.uniform(1, 5))
    await agent_service.update_agent(agent_id, UpdateAgentRequest(status=AgentStatus.ACTIVE))
    
    return {
        "message": "Agent optimization completed",
        "agent_id": agent_id,
        "old_score": agent.performance_score,
        "new_score": new_score,
        "improvement": new_score - agent.performance_score
    }

# Industry-specific endpoints
@app.get("/industries/{industry}/agents", response_model=List[AIAgent])
async def get_industry_agents(industry: IndustryType):
    """Get all agents for a specific industry"""
    return await agent_service.get_all_agents(industry=industry)

@app.get("/industries", response_model=Dict[str, int])
async def get_industry_breakdown():
    """Get breakdown of agents by industry"""
    analytics = await agent_service.get_analytics()
    return analytics.industry_breakdown

# Voice type endpoints
@app.get("/voices", response_model=List[str])
async def get_voice_types():
    """Get available voice types"""
    return [voice.value for voice in VoiceType]

@app.get("/voices/{voice_type}/agents", response_model=List[AIAgent])
async def get_voice_agents(voice_type: VoiceType):
    """Get all agents using a specific voice type"""
    agents = await agent_service.get_all_agents()
    return [agent for agent in agents if agent.voice_type == voice_type]

# 🤖 ENHANCED AI ENDPOINTS - World-Class Intelligence
@app.post("/agents/{agent_id}/ai-optimize")
async def ai_optimize_agent(agent_id: str):
    """Use advanced AI (Claude Opus 4.1) to optimize agent performance"""
    result = await agent_service.ai_optimize_agent(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    if result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result

@app.post("/agents/{agent_id}/ai-conversation-test")
async def ai_conversation_test(agent_id: str, test_scenario: str):
    """Test agent conversation using advanced AI models"""
    result = await agent_service.ai_conversation_test(agent_id, test_scenario)
    if result.get("error"):
        if "not found" in result["error"]:
            raise HTTPException(status_code=404, detail=result["error"])
        else:
            raise HTTPException(status_code=503, detail=result["error"])
    return result

@app.get("/ai-insights")
async def get_ai_insights():
    """Get AI-powered insights about agent portfolio and optimization opportunities"""
    result = await agent_service.get_ai_insights()
    if result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result

@app.get("/ai-status")
async def get_ai_status():
    """Get current AI system status and capabilities"""
    if not AI_ENABLED:
        return {
            "ai_enabled": False,
            "message": "AI capabilities not available",
            "basic_mode": True
        }
    
    try:
        status = await vocelio_ai.get_ai_status()
        return {
            "ai_enabled": True,
            "ai_status": status,
            "capabilities": {
                "conversation_intelligence": "World-class with Claude Sonnet 4",
                "optimization_engine": "Ultimate intelligence with Claude Opus 4.1",
                "sentiment_analysis": "Advanced emotional understanding",
                "strategic_planning": "Enterprise-grade strategic analysis"
            }
        }
    except Exception as e:
        logger.error(f"AI status check failed: {e}")
        return {"ai_enabled": False, "error": str(e)}

@app.post("/ai-demo/run")
async def run_ai_demo():
    """Run the ultimate AI capabilities demonstration"""
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI demo not available")
    
    try:
        # Run quick tests instead of full demo for API response
        conversation_test = await vocelio_ai.customer_conversation(
            "I'm interested in upgrading our call center with AI technology"
        )
        
        optimization_test = await vocelio_ai.agent_optimization(
            {"name": "Demo Agent", "industry": "technology"},
            {"success_rate": 70, "calls": 1000}
        )
        
        return {
            "demo_results": {
                "conversation_quality": conversation_test[:200] + "...",
                "optimization_preview": optimization_test.get("recommendations", "")[:200] + "...",
                "ai_intelligence_level": "WORLD CLASS",
                "models_demonstrated": ["claude-sonnet-4", "claude-opus-4-1"]
            },
            "full_demo_available": True,
            "demo_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"AI demo failed: {e}")
        raise HTTPException(status_code=503, detail=f"AI demo failed: {str(e)}")

@app.get("/ai-demo/conversation-test")
async def quick_ai_conversation_test():
    """Quick AI conversation quality test"""
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI not available")
    
    try:
        response = await vocelio_ai.customer_conversation(
            "Hi, I'm looking for an AI solution for my business call center"
        )
        return {
            "test_prompt": "Hi, I'm looking for an AI solution for my business call center",
            "ai_response": response,
            "quality_level": "World-class conversation intelligence",
            "model_used": "claude-sonnet-4"
        }
    except Exception as e:
        logger.error(f"AI conversation test failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))

# Include Enhanced Features Router
if ENHANCED_FEATURES_ENABLED:
    app.include_router(enhanced_router, tags=["enhanced-platform"])
    logger.info("🛒 Enhanced marketplace and management endpoints registered")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
    reload=False,
        log_level="info"
    )
