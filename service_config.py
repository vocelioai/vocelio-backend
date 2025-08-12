#!/usr/bin/env python3
"""
Service Discovery and Routing Configuration
Maps deployed Railway services to the API Gateway
"""

# Add your actual Railway service URLs here
DEPLOYED_SERVICES = {
    # Currently deployed and verified services
    "team-hub": "https://team-hub-production.up.railway.app",
    "overview": "https://overview-production.up.railway.app",
    "api-gateway": "https://api-gateway-production-588d.up.railway.app",
    "ai-agents": "https://ai-agents-service-production.up.railway.app",
    "smart-campaigns": "https://smart-campaigns-production.up.railway.app",
    "phone-numbers": "https://phone-numbers-production.up.railway.app",
    "analytics-pro": "https://analytics-pro-production.up.railway.app",
    
    # Ready to deploy services (have Dockerfile + main.py + requirements.txt)
    "overview-service": "https://overview-service-production.up.railway.app",
    "smart-campaigns-service": "https://smart-campaigns-service-production.up.railway.app",
    
    # Services with main.py + requirements.txt (need Dockerfiles for deployment)
    "agent-store": "https://agent-store-production.up.railway.app",
    "ai-brain": "https://ai-brain-production.up.railway.app",
    "billing-pro": "https://billing-pro-production.up.railway.app",
    "call-center": "https://call-center-production.up.railway.app",
    "compliance": "https://compliance-production.up.railway.app",
    "developer-api": "https://developer-api-production.up.railway.app",
    "flow-builder": "https://flow-builder-production.up.railway.app",
    "integrations": "https://integrations-production.up.railway.app",
    "settings": "https://settings-production.up.railway.app",
    "voice-lab": "https://voice-lab-production.up.railway.app",
    "voice-marketplace": "https://voice-marketplace-production.up.railway.app",
    "white-label": "https://white-label-production.up.railway.app"
}

# Service health check endpoints
SERVICE_HEALTH_PATHS = {
    # Currently deployed services
    "team-hub": "/health",
    "overview": "/health",
    "api-gateway": "/health",
    "ai-agents": "/health",
    "smart-campaigns": "/health",
    "phone-numbers": "/health",
    "analytics-pro": "/health",
    
    # Ready to deploy services
    "overview-service": "/health",
    "smart-campaigns-service": "/health",
    
    # Services pending Dockerfiles
    "agent-store": "/health",
    "ai-brain": "/health",
    "billing-pro": "/health",
    "call-center": "/health",
    "compliance": "/health",
    "developer-api": "/health",
    "flow-builder": "/health",
    "integrations": "/health",
    "settings": "/health",
    "voice-lab": "/health",
    "voice-marketplace": "/health",
    "white-label": "/health"
}

# Service routing configuration
ROUTE_MAPPINGS = {
    # Currently deployed services
    "/api/v1/team": "team-hub",
    "/api/v1/overview": "overview",
    "/api/v1/gateway": "api-gateway",
    "/api/v1/agents": "ai-agents",
    "/api/v1/campaigns": "smart-campaigns",
    "/api/v1/phone": "phone-numbers",
    "/api/v1/analytics": "analytics-pro",
    
    # Ready to deploy services
    "/api/v1/overview-service": "overview-service",
    "/api/v1/campaigns-service": "smart-campaigns-service",
    
    # Services pending Dockerfiles
    "/api/v1/agent-store": "agent-store",
    "/api/v1/ai-brain": "ai-brain",
    "/api/v1/billing": "billing-pro",
    "/api/v1/call-center": "call-center",
    "/api/v1/compliance": "compliance",
    "/api/v1/developer": "developer-api",
    "/api/v1/flow-builder": "flow-builder",
    "/api/v1/integrations": "integrations",
    "/api/v1/settings": "settings",
    "/api/v1/voice-lab": "voice-lab",
    "/api/v1/voice-marketplace": "voice-marketplace",
    "/api/v1/white-label": "white-label"
}
