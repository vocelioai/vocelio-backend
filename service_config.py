#!/usr/bin/env python3
"""
Service Discovery and Routing Configuration
Maps deployed Railway services to the API Gateway
"""

# Add your actual Railway service URLs here
DEPLOYED_SERVICES = {
    # All confirmed deployed services
    "team-hub": "https://team-hub-production.up.railway.app",
    "overview": "https://overview-production.up.railway.app",
    "api-gateway": "https://api-gateway-production-588d.up.railway.app",
    "ai-agents": "https://ai-agents-service-production.up.railway.app",
    "smart-campaigns": "https://smart-campaigns-production.up.railway.app",
    "phone-numbers": "https://phone-numbers-production.up.railway.app",
    "analytics-pro": "https://analytics-pro-production.up.railway.app"
}

# Service health check endpoints
SERVICE_HEALTH_PATHS = {
    "team-hub": "/health",
    "overview": "/health",
    "api-gateway": "/health",
    "ai-agents": "/health",
    "smart-campaigns": "/health",
    "phone-numbers": "/health",
    "analytics-pro": "/health"
}

# Service routing configuration
ROUTE_MAPPINGS = {
    "/api/v1/team": "team-hub",
    "/api/v1/overview": "overview",
    "/api/v1/gateway": "api-gateway",
    "/api/v1/agents": "ai-agents",
    "/api/v1/campaigns": "smart-campaigns",
    "/api/v1/phone": "phone-numbers",
    "/api/v1/analytics": "analytics-pro"
}
