#!/usr/bin/env python3
"""
Simple Service Deployment for Railway
Creates basic FastAPI services and deploys them
"""

import os
import subprocess
from pathlib import Path

def create_basic_service(service_name, service_path):
    """Create a basic FastAPI service"""
    
    # Create directory
    service_path.mkdir(exist_ok=True)
    
    # Create main.py
    main_content = f'''#!/usr/bin/env python3
"""
{service_name} Service for Vocelio.ai
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"{service_name} Service",
    version="1.0.0",
    description=f"Vocelio.ai {service_name} microservice"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{
        "service": "{service_name}",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }}

@app.get("/health")
async def health_check():
    return {{
        "status": "healthy",
        "service": "{service_name}",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting {service_name} Service on port {{port}}")
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
    
    with open(service_path / "main.py", 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    # Create railway.toml
    railway_content = f'''[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/health"

[env]
PORT = "8000"
ENVIRONMENT = "production"
'''
    
    with open(service_path / "railway.toml", 'w', encoding='utf-8') as f:
        f.write(railway_content)
    
    print(f"Created {service_name} service")

def main():
    """Create and deploy services"""
    root_path = Path("c:/Users/SNC/OneDrive/Desktop/vocelio-backend")
    apps_path = root_path / "apps"
    
    services = [
        "ai-brain", "agents", "agent-store", "billing-pro", 
        "call-center", "voice-lab", "voice-marketplace",
        "flow-builder", "integrations", "settings", 
        "developer-api", "compliance", "white-label"
    ]
    
    print(f"Setting up {len(services)} services...")
    
    for service in services:
        service_path = apps_path / service
        create_basic_service(service, service_path)
    
    print("All services created successfully!")
    print("You can now deploy them individually using:")
    print("cd apps/<service-name>")
    print("railway up")

if __name__ == "__main__":
    main()
