#!/usr/bin/env python3
"""
Service Discovery and Routing Configuration
Maps deployed Railway services to the API Gateway
"""

# Add your actual Vocelio custom domain service URLs here
DEPLOYED_SERVICES = {
    # Core Foundation Services (7) - Custom vocelio.ai domains
    "team-hub": "https://team.vocelio.ai",
    "overview": "https://overview.vocelio.ai", 
    "api-gateway": "https://api.vocelio.ai",
    "ai-agents": "https://agents.vocelio.ai",
    "smart-campaigns": "https://campaigns.vocelio.ai",
    "phone-numbers": "https://numbers.vocelio.ai",
    "analytics-pro": "https://analytics.vocelio.ai",
    
    # Business Services (6) - Professional branding
    "overview-service": "https://overview.vocelio.ai",
    "smart-campaigns-service": "https://campaigns.vocelio.ai",
    "agent-store": "https://backend.vocelio.ai",
    "ai-brain": "https://brain.vocelio.ai",
    "billing-pro": "https://billing.vocelio.ai",
    "call-center": "https://call.vocelio.ai",
    
    # Enterprise Features (6) - Custom domains
    "compliance": "https://compliance.vocelio.ai",
    "developer-api": "https://developer.vocelio.ai", 
    "flow-builder": "https://flowbuilder.vocelio.ai",
    "integrations": "https://integrations.vocelio.ai",
    "settings": "https://settings.vocelio.ai",
    "voice-lab": "https://voicelab.vocelio.ai",
    "voice-marketplace": "https://voicemarketplace.vocelio.ai",
    "white-label": "https://whitelabel.vocelio.ai",
    
    # AI & Automation Services (6) - Advanced domains
    "agents": "https://agents.vocelio.ai",
    "knowledge-base": "https://knowledge.vocelio.ai",
    "lead-management": "https://lead.vocelio.ai", 
    "scheduling": "https://scheduling.vocelio.ai",
    "data-warehouse": "https://data.vocelio.ai",
    "identity": "https://identity.vocelio.ai",
    "security": "https://security.vocelio.ai",
    
    # Communication & Compliance (4) - Professional endpoints
    "notifications": "https://notifications.vocelio.ai",
    "scripts": "https://scripts.vocelio.ai",
    "webhooks": "https://webhooks.vocelio.ai",
    "api-management": "https://apimanagement.vocelio.ai"
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
    "white-label": "/health",
    
    # Final 2 services
    "agents": "/health",
    "ai-agents": "/health",
    
    # World-class AI platform services
    "knowledge-base": "/health",
    "lead-management": "/health",
    "notifications": "/health", 
    "scheduling": "/health",
    "scripts": "/health",
    "webhooks": "/health"
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
    "/api/v1/white-label": "white-label",
    
    # Final 2 services for 100% completion
    "/api/v1/agents-mgmt": "agents",
    "/api/v1/ai-agents": "ai-agents",
    
    # WORLD-CLASS AI PLATFORM ROUTES
    "/api/v1/knowledge": "knowledge-base",
    "/api/v1/leads": "lead-management", 
    "/api/v1/notifications": "notifications",
    "/api/v1/scheduling": "scheduling",
    "/api/v1/scripts": "scripts",
    "/api/v1/webhooks": "webhooks"
}
