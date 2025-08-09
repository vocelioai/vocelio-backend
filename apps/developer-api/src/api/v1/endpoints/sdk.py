# apps/developer-api/src/api/v1/endpoints/sdk.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Dict, Any
import io
import zipfile
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported SDK languages"""
    
    languages = {
        "supported_languages": [
            {
                "language": "python",
                "version": "1.0.0",
                "status": "stable",
                "install_command": "pip install vocelio-sdk",
                "github_url": "https://github.com/vocelioai/vocelio-python-sdk"
            },
            {
                "language": "javascript",
                "version": "1.0.0", 
                "status": "stable",
                "install_command": "npm install @vocelio/sdk",
                "github_url": "https://github.com/vocelioai/vocelio-js-sdk"
            },
            {
                "language": "typescript",
                "version": "1.0.0",
                "status": "stable", 
                "install_command": "npm install @vocelio/sdk-typescript",
                "github_url": "https://github.com/vocelioai/vocelio-ts-sdk"
            },
            {
                "language": "php",
                "version": "0.9.0",
                "status": "beta",
                "install_command": "composer require vocelio/sdk",
                "github_url": "https://github.com/vocelioai/vocelio-php-sdk"
            },
            {
                "language": "ruby",
                "version": "0.8.0",
                "status": "beta",
                "install_command": "gem install vocelio-sdk",
                "github_url": "https://github.com/vocelioai/vocelio-ruby-sdk"
            }
        ]
    }
    
    return languages

@router.get("/download/{language}")
async def download_sdk(language: str):
    """Download SDK for specified language"""
    
    if language not in ["python", "javascript", "typescript", "php", "ruby"]:
        raise HTTPException(status_code=404, detail="SDK not available for this language")
    
    # Mock SDK content
    sdk_content = f"""
# Vocelio.ai SDK for {language.title()}
# Version 1.0.0

class VocelioClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.vocelio.ai"
    
    def create_call(self, to_number, agent_id):
        # Implementation here
        pass
    
    def get_agents(self):
        # Implementation here  
        pass
        
    def create_campaign(self, campaign_data):
        # Implementation here
        pass

# Example usage:
client = VocelioClient("voc_live_your_api_key")
agents = client.get_agents()
"""
    
    # Create zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"vocelio-{language}-sdk/client.py", sdk_content)
        zip_file.writestr(f"vocelio-{language}-sdk/README.md", f"# Vocelio {language.title()} SDK")
        zip_file.writestr(f"vocelio-{language}-sdk/examples/quickstart.py", "# Quickstart example")
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=vocelio-{language}-sdk.zip"}
    )

@router.get("/examples/{language}")
async def get_code_examples(language: str):
    """Get code examples for specific language"""
    
    examples = {
        "language": language,
        "examples": [
            {
                "title": "Make a Call",
                "description": "Create and start an AI-powered call",
                "code": f"""
# {language.title()} - Make a Call
client = VocelioClient("your_api_key")

call = client.calls.create(
    to="+1234567890",
    agent_id="agent_123",
    campaign_id="camp_456"
)

print(f"Call started: {{call.id}}")
"""
            },
            {
                "title": "Create AI Agent",
                "description": "Create a new AI agent",
                "code": f"""
# {language.title()} - Create AI Agent
agent = client.agents.create(
    name="Sales Agent",
    voice="confident_mike",
    personality="professional and friendly",
    industry="solar_sales"
)

print(f"Agent created: {{agent.id}}")
"""
            },
            {
                "title": "Start Campaign", 
                "description": "Launch a new campaign",
                "code": f"""
# {language.title()} - Start Campaign
campaign = client.campaigns.create(
    name="Q4 Solar Campaign",
    agent_id=agent.id,
    phone_numbers=["+1234567890", "+0987654321"],
    schedule="immediate"
)

print(f"Campaign started: {{campaign.id}}")
"""
            }
        ]
    }
    
    return examples
