# apps/api-gateway/src/main.py
from fastapi import FastAPI, Request, Response, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import json

# Support running both as `python -m src.main` (package) and `python src/main.py` (script)
try:  # pragma: no cover - import flexibility
    from src.middleware.auth import auth_middleware
    from src.middleware.rate_limiting import rate_limit_middleware
    from src.middleware.logging import request_logging_middleware
    from src.routes.health import router as health_router
    from src.routes.proxy import router as proxy_router
    from src.utils.service_discovery import ServiceDiscovery
    from src.utils.load_balancer import LoadBalancer
    from src.config import settings
except ImportError:  # Fallback to absolute imports if relative fails
    # Ensure current directory on path
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).resolve().parent))
    from middleware.auth import auth_middleware
    from middleware.rate_limiting import rate_limit_middleware
    from middleware.logging import request_logging_middleware
    from routes.health import router as health_router
    from routes.proxy import router as proxy_router
    from utils.service_discovery import ServiceDiscovery
    from utils.load_balancer import LoadBalancer
    from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🔥 Vocelio.ai API Gateway",
    version="2.0.0",
    description="World's Best AI Call Center Platform - Microservices Gateway",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(request_logging_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(auth_middleware)

# Active service URLs (limit to currently deployed stack to reduce noisy health logs)
# Expand this map as additional services come online.
SERVICES = {
    "overview-service": os.getenv("OVERVIEW_SERVICE_URL", "http://overview-service:8001"),
    "ai-agents-service": os.getenv("AI_AGENTS_SERVICE_URL", "http://ai-agents-service:8002"),
    "smart-campaigns-service": os.getenv("SMART_CAMPAIGNS_SERVICE_URL", "http://smart-campaigns-service:8003"),
    # Dashboard Integration Services
    "overview": os.getenv("OVERVIEW_SERVICE_URL", "https://overview-production.up.railway.app"),
    "agent-store": os.getenv("AGENT_STORE_SERVICE_URL", "https://agent-store-production.up.railway.app"),
    "ai-brain": os.getenv("AI_BRAIN_SERVICE_URL", "https://ai-brain-production.up.railway.app"),
    "billing-pro": os.getenv("BILLING_PRO_SERVICE_URL", "https://billing-pro-production.up.railway.app"),
    "flow-builder": os.getenv("FLOW_BUILDER_SERVICE_URL", "https://flow-builder-production.up.railway.app"),
    "phone-numbers": os.getenv("PHONE_NUMBERS_SERVICE_URL", "https://phone-numbers-production.up.railway.app"),
    "white-label": os.getenv("WHITE_LABEL_SERVICE_URL", "https://white-label-production-ab67.up.railway.app"),
    "ai-agents": os.getenv("AI_AGENTS_SERVICE_URL", "https://ai-agents-service-production.up.railway.app"),
}

# Initialize service discovery and load balancer
service_discovery = ServiceDiscovery(SERVICES)
load_balancer = LoadBalancer(SERVICES)

# Performance monitoring middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Powered-By"] = "Vocelio.ai Gateway v2.0"
    response.headers["X-Service-Count"] = str(len(SERVICES))
    return response

# Include routers
app.include_router(health_router, tags=["Health"])  # No prefix - routes defined in health.py will be direct
app.include_router(proxy_router, tags=["Proxy"])

@app.get("/")
async def root():
    """Gateway root endpoint with service information"""
    return {
        "message": "🔥 Vocelio.ai - World's Best AI Call Center Platform",
        "version": "2.0.0",
        "architecture": "microservices",
        "gateway": {
            "status": "operational",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "local"),
            "total_services": len(SERVICES),
            "active_services": await service_discovery.get_active_services_count(),
        },
        "services": {
            "overview-service": "📊 Command Center Dashboard",
            "ai-agents-service": "🤖 AI Agent Management",
            "smart-campaigns-service": "🎯 Smart Campaign Engine",
            "overview": "📊 Dashboard Integration API",
            "agent-store": "🛒 AI Agent Marketplace",
            "ai-brain": "🧠 AI Processing Engine",
            "billing-pro": "💰 Billing & Payments",
            "flow-builder": "🔧 Conversation Flow Builder",
            "phone-numbers": "📞 Phone Number Management",
            "white-label": "🏷️ White Label Solutions",
            "ai-agents": "🤖 AI Agent Services"
        },
        "features": {
            "ai_brain": "✅ GPT-4 + Multi-Model Support",
            "voice_system": "✅ ElevenLabs + 13 Languages", 
            "phone_system": "✅ Twilio + Global Coverage",
            "live_transfer": "✅ Human Handoff Ready",
            "visual_builder": "✅ Drag & Drop Scripts",
            "analytics": "✅ Real-time Dashboard",
            "compliance": "✅ TCPA/GDPR Ready",
            "billing": "✅ Usage-based + Subscriptions",
            "deployment": "✅ Railway Cloud Ready"
        },
        "docs": f"{os.getenv('RAILWAY_STATIC_URL', 'http://localhost:8000')}/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

# Test endpoint to verify deployment
@app.get("/api/v1/test", tags=["Test"])
async def test_endpoint():
    """Test endpoint to verify deployment is working"""
    return {
        "status": "success",
        "message": "✅ Updated API Gateway is deployed and working!",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2024-08-12-latest"
    }

# Twilio integration endpoints - Direct implementation
@app.get("/api/v1/twilio/available-phone-numbers/{country_code}/{type}", tags=["Twilio Integration"])
async def get_twilio_available_numbers(
    country_code: str,
    type: str,
    area_code: Optional[str] = Query(None),
    contains: Optional[str] = Query(None),
    page_size: int = Query(20, le=1000)
):
    """Get available phone numbers from Twilio"""
    from integrations.twilio_service import get_available_phone_numbers
    return await get_available_phone_numbers(country_code, type, area_code, contains, page_size)

@app.post("/api/v1/twilio/incoming-phone-numbers", tags=["Twilio Integration"])
async def purchase_twilio_number(phone_number: str, webhook_url: Optional[str] = None):
    """Purchase a phone number from Twilio"""
    from integrations.twilio_service import purchase_phone_number
    return await purchase_phone_number(phone_number, webhook_url)

@app.get("/api/v1/twilio/incoming-phone-numbers", tags=["Twilio Integration"])
async def list_twilio_numbers():
    """List all purchased phone numbers"""
    from integrations.twilio_service import list_phone_numbers
    return await list_phone_numbers()

# Twilio API routing - route to phone-numbers service
@app.api_route("/api/v1/twilio/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def twilio_route(
    path: str, 
    request: Request,
    background_tasks: BackgroundTasks
):
    """Route Twilio API requests to phone-numbers service with fallback to direct handling"""
    
    # Handle available phone numbers request directly
    if path.startswith("available-phone-numbers/"):
        parts = path.split("/")
        if len(parts) >= 3:
            country_code = parts[1]
            number_type = parts[2]
            
            # Get query parameters
            query_params = dict(request.query_params)
            area_code = query_params.get("area_code")
            contains = query_params.get("contains")
            page_size = int(query_params.get("page_size", 20))
            
            from integrations.twilio_service import get_available_phone_numbers
            return await get_available_phone_numbers(country_code, number_type, area_code, contains, page_size)
    
    service_name = "phone-numbers"
    
    try:
        # Get optimal service URL using load balancer
        service_url = await load_balancer.get_service_url(service_name)
        target_url = f"{service_url}/api/v1/twilio/{path}"
        
        # Prepare headers (remove host header to avoid conflicts)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers["X-Forwarded-For"] = request.client.host
        headers["X-Gateway-Version"] = "2.0.0"
        headers["X-Service-Route"] = service_name
        headers["X-Twilio-Route"] = "true"
        
        # Get request body
        body = await request.body()
        
        # Log request for analytics
        logger.info(f"🔄 Routing Twilio request: {request.method} /api/v1/twilio/{path} → {service_name}")
        
        # Make request to target service with timeout and retry logic
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=dict(request.query_params)
                )
                
                # Log successful response
                logger.info(
                    f"✅ Twilio request completed: {service_name} - {response.status_code} - {response.elapsed.total_seconds():.3f}s"
                )
                
                # Return response with additional headers
                response_headers = dict(response.headers)
                response_headers["X-Service-Name"] = service_name
                response_headers["X-Service-Response-Time"] = str(response.elapsed.total_seconds())
                response_headers["X-Twilio-Gateway"] = "true"
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response_headers.get("content-type", "application/json")
                )
                
            except httpx.TimeoutException:
                logger.error(f"⏰ Timeout calling {service_name} service for Twilio request")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "Service timeout",
                        "service": service_name,
                        "message": "The Twilio service took too long to respond. Please try again."
                    }
                )
                
            except httpx.ConnectError:
                logger.error(f"🔌 Connection error to {service_name} service for Twilio request")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Service unavailable",
                        "service": service_name,
                        "message": "Cannot connect to the Twilio service. Please try again later."
                    }
                )
                
    except Exception as e:
        logger.error(f"💥 Error in Twilio routing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal gateway error",
                "message": "Failed to route Twilio request"
            }
        )

# Main service routing endpoint
@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_route(
    service_name: str, 
    path: str, 
    request: Request,
    background_tasks: BackgroundTasks
):
    """Route requests to appropriate microservice with intelligent load balancing"""
    try:
        # Validate service exists
        if service_name not in SERVICES:
            logger.warning(f"Unknown service requested: {service_name}")
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Service not found",
                    "service": service_name,
                    "available_services": list(SERVICES.keys())
                }
            )
        
        # Get optimal service URL using load balancer
        service_url = await load_balancer.get_service_url(service_name)
        target_url = f"{service_url}/api/v1/{path}"
        
        # Prepare headers (remove host header to avoid conflicts)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers["X-Forwarded-For"] = request.client.host
        headers["X-Gateway-Version"] = "2.0.0"
        headers["X-Service-Route"] = service_name
        
        # Get request body
        body = await request.body()
        
        # Log request for analytics
        logger.info(f"🌐 Routing {request.method} {service_name}/{path} -> {target_url}")
        
        # Make request to target service with timeout and retry logic
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=dict(request.query_params)
                )
                
                # Log successful request
                logger.info(f"✅ {service_name} responded with {response.status_code} in {response.elapsed.total_seconds():.3f}s")
                
                # Update service health metrics
                background_tasks.add_task(
                    service_discovery.update_service_health,
                    service_name,
                    response.status_code,
                    response.elapsed.total_seconds()
                )
                
                # Return response with additional headers
                response_headers = dict(response.headers)
                response_headers["X-Service-Name"] = service_name
                response_headers["X-Service-Response-Time"] = str(response.elapsed.total_seconds())
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response_headers.get("content-type", "application/json")
                )
                
            except httpx.TimeoutException:
                logger.error(f"⏰ Timeout calling {service_name} service")
                
                # Mark service as unhealthy
                background_tasks.add_task(
                    service_discovery.mark_service_unhealthy,
                    service_name,
                    "timeout"
                )
                
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "Service timeout",
                        "service": service_name,
                        "message": "The service took too long to respond. Please try again."
                    }
                )
                
            except httpx.ConnectError:
                logger.error(f"🔌 Connection error to {service_name} service")
                
                # Mark service as unhealthy
                background_tasks.add_task(
                    service_discovery.mark_service_unhealthy,
                    service_name,
                    "connection_error"
                )
                
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Service unavailable",
                        "service": service_name,
                        "message": "The service is currently unavailable. Please try again later."
                    }
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error routing to {service_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Gateway error",
                "service": service_name,
                "message": "An unexpected error occurred in the gateway."
            }
        )

# Webhook routing (special handling for webhooks)
@app.api_route("/webhooks/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def webhook_route(service_name: str, path: str, request: Request):
    """Special routing for webhooks with enhanced reliability"""
    try:
        if service_name not in SERVICES:
            raise HTTPException(status_code=404, detail="Webhook service not found")
        
        service_url = SERVICES[service_name]
        target_url = f"{service_url}/webhooks/{path}"
        
        # Webhook-specific headers
        headers = dict(request.headers)
        headers.pop("host", None)
        headers["X-Webhook-Gateway"] = "vocelio-2.0"
        headers["X-Webhook-Service"] = service_name
        
        body = await request.body()
        
        logger.info(f"🪝 Webhook {request.method} {service_name}/{path}")
        
        # Webhooks need faster timeout but with retry
        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(3):  # 3 retry attempts
                try:
                    response = await client.request(
                        method=request.method,
                        url=target_url,
                        headers=headers,
                        content=body,
                        params=dict(request.query_params)
                    )
                    
                    logger.info(f"✅ Webhook {service_name} responded {response.status_code}")
                    
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                    
                except (httpx.TimeoutException, httpx.ConnectError) as e:
                    if attempt == 2:  # Last attempt
                        logger.error(f"❌ Webhook {service_name} failed after 3 attempts: {e}")
                        raise HTTPException(
                            status_code=502,
                            detail=f"Webhook service {service_name} unavailable"
                        )
                    
                    logger.warning(f"⚠️ Webhook {service_name} attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Webhook routing error: {e}")
        raise HTTPException(status_code=500, detail="Webhook gateway error")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize gateway services on startup"""
    logger.info("🚀 Starting Vocelio.ai API Gateway v2.0")
    logger.info("=" * 60)
    logger.info("🔥 WORLD'S BEST AI CALL CENTER PLATFORM")
    logger.info("🌐 Microservices Architecture")
    logger.info(f"⚡ {len(SERVICES)} Services Configured")
    logger.info("☁️ Railway Cloud Optimized")
    logger.info("=" * 60)
    
    # Initialize service discovery
    await service_discovery.initialize()
    
    # Health check all services
    healthy_services = await service_discovery.health_check_all_services()
    logger.info(f"✅ {healthy_services}/{len(SERVICES)} services healthy")
    
    # Start background tasks
    asyncio.create_task(service_discovery.periodic_health_check())
    asyncio.create_task(load_balancer.update_metrics())
    
    logger.info("🎯 API Gateway ready to route traffic!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Vocelio.ai API Gateway...")
    await service_discovery.cleanup()

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc} - {request.url}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal gateway error",
            "message": "Something went wrong in the API gateway. Our team has been notified.",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🔥 VOCELIO.AI API GATEWAY v2.0 🔥")
    print("")
    print("🚀 MICROSERVICES FEATURES:")
    print("✅ Intelligent Service Routing")
    print("✅ Load Balancing & Health Checks")
    print("✅ Rate Limiting & Security")
    print("✅ Request Logging & Analytics")
    print("✅ Auto-Retry & Circuit Breaker")
    print("✅ Webhook Reliability")
    print("✅ Real-time Service Discovery")
    print("✅ Railway Cloud Integration")
    print("")
    print("🌟 WORLD'S BEST AI CALL CENTER GATEWAY IS LIVE! 🌟")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RAILWAY_ENVIRONMENT") != "production"
    )