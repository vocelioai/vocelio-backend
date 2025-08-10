#!/usr/bin/env python3
"""
Add requirements.txt to all services that are missing it
"""

import os
from pathlib import Path

# Requirements content
requirements_content = """fastapi==0.112.2
uvicorn[standard]==0.30.6
python-multipart==0.0.9
pydantic==2.8.2
httpx==0.25.2
python-dotenv==1.0.1"""

# Services that need requirements.txt
services = [
    "ai-brain", "agents", "agent-store", "billing-pro", 
    "call-center", "voice-lab", "voice-marketplace",
    "flow-builder", "integrations", "settings", 
    "developer-api", "compliance", "white-label"
]

root_path = Path("c:/Users/SNC/OneDrive/Desktop/vocelio-backend")
apps_path = root_path / "apps"

print("Adding requirements.txt to all services...")

for service in services:
    service_path = apps_path / service
    requirements_path = service_path / "requirements.txt"
    
    if service_path.exists():
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        print(f"✅ Added requirements.txt to {service}")
    else:
        print(f"❌ {service} directory not found")

print("Done! All services now have requirements.txt")
