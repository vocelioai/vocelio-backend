#!/usr/bin/env python3
"""
Service Discovery and Routing Configuration
Maps deployed Railway services to the API Gateway
"""

# Add your actual Railway service URLs here
DEPLOYED_SERVICES = {
    # Confirmed deployed service
    "team-hub": "https://team-hub-production.up.railway.app",
    
    # Add the other 6 services here as you provide their URLs
    # "overview-service": "https://overview-service-production.up.railway.app",
    # "ai-agents-service": "https://ai-agents-service-production.up.railway.app", 
    # "smart-campaigns-service": "https://smart-campaigns-service-production.up.railway.app",
    # "phone-numbers": "https://phone-numbers-production.up.railway.app",
    # "analytics-pro": "https://analytics-pro-production.up.railway.app",
    # "voice-lab": "https://voice-lab-production.up.railway.app"
}

# Service health check endpoints
SERVICE_HEALTH_PATHS = {
    "team-hub": "/health"
    # Add other services as URLs are provided
}

# Service routing configuration
ROUTE_MAPPINGS = {
    "/api/v1/team": "team-hub"
    # Add other service routes as URLs are provided
    # "/api/v1/overview": "overview-service",
    # "/api/v1/agents": "ai-agents-service", 
    # "/api/v1/campaigns": "smart-campaigns-service",
    # "/api/v1/phone": "phone-numbers",
    # "/api/v1/analytics": "analytics-pro",
    # "/api/v1/voice": "voice-lab"
}
