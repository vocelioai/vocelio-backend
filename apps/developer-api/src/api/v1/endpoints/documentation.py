# apps/developer-api/src/api/v1/endpoints/documentation.py
from fastapi import APIRouter
from typing import Dict, Any, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_api_documentation():
    """Get comprehensive API documentation"""
    
    documentation = {
        "api_info": {
            "name": "Vocelio.ai API",
            "version": "v1",
            "base_url": "https://api.vocelio.ai/v1",
            "authentication": "Bearer token (API key)",
            "rate_limits": {
                "default": "1000 requests/hour",
                "premium": "10000 requests/hour", 
                "enterprise": "unlimited"
            }
        },
        "endpoints": [
            {
                "category": "Calls",
                "base_path": "/calls",
                "description": "Manage AI-powered phone calls",
                "methods": [
                    {"method": "GET", "path": "/calls", "description": "List all calls"},
                    {"method": "POST", "path": "/calls", "description": "Create new call"},
                    {"method": "GET", "path": "/calls/{id}", "description": "Get call details"},
                    {"method": "PUT", "path": "/calls/{id}", "description": "Update call"},
                    {"method": "DELETE", "path": "/calls/{id}", "description": "Cancel call"}
                ]
            },
            {
                "category": "AI Agents",
                "base_path": "/agents", 
                "description": "Create and manage AI agents",
                "methods": [
                    {"method": "GET", "path": "/agents", "description": "List all agents"},
                    {"method": "POST", "path": "/agents", "description": "Create new agent"},
                    {"method": "GET", "path": "/agents/{id}", "description": "Get agent details"},
                    {"method": "PUT", "path": "/agents/{id}", "description": "Update agent"},
                    {"method": "DELETE", "path": "/agents/{id}", "description": "Delete agent"}
                ]
            },
            {
                "category": "Campaigns",
                "base_path": "/campaigns",
                "description": "Manage calling campaigns", 
                "methods": [
                    {"method": "GET", "path": "/campaigns", "description": "List all campaigns"},
                    {"method": "POST", "path": "/campaigns", "description": "Create new campaign"},
                    {"method": "GET", "path": "/campaigns/{id}", "description": "Get campaign details"},
                    {"method": "PUT", "path": "/campaigns/{id}", "description": "Update campaign"},
                    {"method": "DELETE", "path": "/campaigns/{id}", "description": "Delete campaign"}
                ]
            }
        ],
        "authentication": {
            "type": "API Key",
            "header": "Authorization: Bearer voc_live_your_api_key",
            "get_key": "Create API key at /developer-api/keys"
        },
        "error_codes": {
            "400": "Bad Request - Invalid parameters",
            "401": "Unauthorized - Invalid API key", 
            "403": "Forbidden - Insufficient permissions",
            "404": "Not Found - Resource doesn't exist",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Something went wrong"
        }
    }
    
    return documentation

@router.get("/guides")
async def get_integration_guides():
    """Get step-by-step integration guides"""
    
    guides = {
        "getting_started": {
            "title": "Getting Started with Vocelio.ai API",
            "steps": [
                {
                    "step": 1,
                    "title": "Get API Key",
                    "description": "Create account and generate API key",
                    "code": "# Get your API key from dashboard\napi_key = 'voc_live_your_key_here'"
                },
                {
                    "step": 2, 
                    "title": "Install SDK",
                    "description": "Install SDK for your language",
                    "code": "pip install vocelio-sdk  # Python\nnpm install @vocelio/sdk  # JavaScript"
                },
                {
                    "step": 3,
                    "title": "Make First Call",
                    "description": "Create your first AI call",
                    "code": "from vocelio import VocelioClient\n\nclient = VocelioClient(api_key)\ncall = client.calls.create(to='+1234567890', agent_id='agent_123')"
                }
            ]
        },
        "use_cases": [
            {
                "title": "Sales Outreach",
                "description": "Automate sales calls with AI agents",
                "example_code": "# Configure sales agent\nagent = client.agents.create(\n    name='Sales Pro',\n    voice='confident_mike',\n    script='Hi, I'm calling about solar savings...'\n)"
            },
            {
                "title": "Lead Qualification", 
                "description": "Qualify leads automatically",
                "example_code": "# Qualify leads with smart questions\ncampaign = client.campaigns.create(\n    type='lead_qualification',\n    qualification_criteria=['budget', 'timeline', 'authority']\n)"
            },
            {
                "title": "Appointment Setting",
                "description": "Book appointments automatically", 
                "example_code": "# Book appointments with calendar integration\nagent.set_calendar_integration('google_calendar')\nagent.book_appointments = True"
            }
        ]
    }
    
    return guides
