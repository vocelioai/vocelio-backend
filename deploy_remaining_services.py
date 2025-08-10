#!/usr/bin/env python3
"""
🚀 Deploy Remaining 15 Vocelio Services to Railway
Systematic deployment of all microservices with proper configuration
"""

import os
import subprocess
import time
from pathlib import Path

class ServiceDeployer:
    """Deploys Vocelio microservices to Railway"""
    
    def __init__(self):
        self.root_path = Path("c:/Users/SNC/OneDrive/Desktop/vocelio-backend")
        self.apps_path = self.root_path / "apps"
        
        # Services to deploy (excluding already deployed ones)
        self.remaining_services = [
            # Core AI Services
            "ai-brain",
            "agents", 
            "agent-store",
            
            # Business Services
            "billing-pro",
            "call-center",
            "voice-lab",
            "voice-marketplace",
            
            # Platform Services
            "flow-builder",
            "integrations",
            "settings",
            "developer-api",
            
            # Enterprise Services
            "compliance",
            "white-label",
        ]
        
        # Services that might need special handling
        self.special_services = {
            "ai-agents": "ai-agents",  # Different from ai-agents-service
            "overview": "overview",    # Different from overview-service  
        }
        
        # Already deployed services (skip these)
        self.deployed_services = [
            "team-hub",
            "overview-service", 
            "api-gateway",
            "ai-agents-service",
            "smart-campaigns-service",
            "phone-numbers",
            "analytics-pro"
        ]

    def check_service_structure(self, service_name: str) -> dict:
        """Check if service has proper structure for deployment"""
        service_path = self.apps_path / service_name
        
        if not service_path.exists():
            return {"exists": False, "reason": "Directory not found"}
        
        # Check for main files
        has_main = any([
            (service_path / "main.py").exists(),
            (service_path / "app.py").exists(),
            (service_path / "server.py").exists(),
            (service_path / "__init__.py").exists()
        ])
        
        # Check for requirements
        has_requirements = any([
            (service_path / "requirements.txt").exists(),
            (service_path / "pyproject.toml").exists(),
            (self.root_path / "requirements.txt").exists()
        ])
        
        # Check for Railway config
        has_railway_config = (service_path / "railway.toml").exists()
        
        return {
            "exists": True,
            "has_main": has_main,
            "has_requirements": has_requirements,
            "has_railway_config": has_railway_config,
            "path": str(service_path),
            "ready": has_main and has_requirements
        }

    def create_railway_config(self, service_name: str, service_path: Path):
        """Create railway.toml for service"""
        config_content = f'''[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"

[env]
PORT = "8000"
ENVIRONMENT = "production"

[environments.production]
[environments.production.variables]
ENVIRONMENT = "production"
PORT = "8000"
DEBUG = "false"

# Database and External Services
DATABASE_URL = "${{Railway.DATABASE_URL}}"
SUPABASE_URL = "${{Railway.SUPABASE_URL}}"
SUPABASE_KEY = "${{Railway.SUPABASE_KEY}}"
REDIS_URL = "${{Railway.REDIS_URL}}"

# Authentication
JWT_SECRET_KEY = "${{Railway.JWT_SECRET_KEY}}"
SECRET_KEY = "${{Railway.SECRET_KEY}}"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = "1440"

# AI Services
OPENAI_API_KEY = "${{Railway.OPENAI_API_KEY}}"
ANTHROPIC_API_KEY = "${{Railway.ANTHROPIC_API_KEY}}"
ELEVENLABS_API_KEY = "${{Railway.ELEVENLABS_API_KEY}}"
RAMBLE_API_KEY = "${{Railway.RAMBLE_API_KEY}}"

# Communication
TWILIO_ACCOUNT_SID = "${{Railway.TWILIO_ACCOUNT_SID}}"
TWILIO_AUTH_TOKEN = "${{Railway.TWILIO_AUTH_TOKEN}}"

# Payment
STRIPE_SECRET_KEY = "${{Railway.STRIPE_SECRET_KEY}}"
STRIPE_WEBHOOK_SECRET = "${{Railway.STRIPE_WEBHOOK_SECRET}}"
STRIPE_PUBLISHABLE_KEY = "${{Railway.STRIPE_PUBLISHABLE_KEY}}"

# Service URLs
TEAM_HUB_SERVICE_URL = "https://team-hub-production.up.railway.app"
OVERVIEW_SERVICE_URL = "https://overview-production.up.railway.app"
AI_AGENTS_SERVICE_URL = "https://ai-agents-service-production.up.railway.app"
SMART_CAMPAIGNS_SERVICE_URL = "https://smart-campaigns-production.up.railway.app"
PHONE_NUMBERS_SERVICE_URL = "https://phone-numbers-production.up.railway.app"
ANALYTICS_SERVICE_URL = "https://analytics-pro-production.up.railway.app"

# CORS and Security
CORS_ORIGINS = "https://*.railway.app,https://*.vocelio.ai"
ALLOWED_ORIGINS = "https://*.railway.app,https://*.vocelio.ai"
ALLOWED_HOSTS = "*"
'''
        
        config_path = service_path / "railway.toml"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Created railway.toml for {service_name}")

    def create_simple_main_py(self, service_name: str, service_path: Path):
        """Create a simple main.py if none exists"""
        main_content = f'''#!/usr/bin/env python3
"""
{service_name.title().replace('-', ' ')} Service
Vocelio.ai Microservice for {service_name}
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=f"🚀 {service_name.title().replace('-', ' ')} Service",
    version="1.0.0",
    description=f"Vocelio.ai {service_name} microservice",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "service": "{service_name}",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": ["/health", "/docs", "/redoc"]
    }}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "service": "{service_name}",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting {{'{service_name}'.title().replace('-', ' ')}} Service on port {{port}}")
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
        
        main_path = service_path / "main.py"
        with open(main_path, 'w') as f:
            f.write(main_content)
        
        print(f"✅ Created main.py for {service_name}")

    def analyze_all_services(self):
        """Analyze all services for deployment readiness"""
        print("🔍 Analyzing service deployment readiness...")
        print("=" * 60)
        
        ready_services = []
        needs_setup = []
        
        for service in self.remaining_services:
            analysis = self.check_service_structure(service)
            
            if analysis["exists"]:
                if analysis["ready"]:
                    ready_services.append(service)
                    print(f"✅ {service:<20} - Ready for deployment")
                else:
                    needs_setup.append(service)
                    print(f"⚠️  {service:<20} - Needs setup (main: {analysis['has_main']}, req: {analysis['has_requirements']})")
            else:
                print(f"❌ {service:<20} - Directory not found")
        
        print(f"\n📊 Summary:")
        print(f"✅ Ready: {len(ready_services)} services")
        print(f"⚠️  Needs setup: {len(needs_setup)} services")
        
        return ready_services, needs_setup

    def setup_service(self, service_name: str):
        """Set up a service for deployment"""
        service_path = self.apps_path / service_name
        
        print(f"🔧 Setting up {service_name}...")
        
        # Create directory if it doesn't exist
        service_path.mkdir(exist_ok=True)
        
        # Create main.py if it doesn't exist
        if not any([
            (service_path / "main.py").exists(),
            (service_path / "app.py").exists(),
            (service_path / "server.py").exists()
        ]):
            self.create_simple_main_py(service_name, service_path)
        
        # Create railway.toml
        self.create_railway_config(service_name, service_path)
        
        print(f"✅ {service_name} setup complete")

    def deploy_service(self, service_name: str):
        """Deploy a single service to Railway"""
        service_path = self.apps_path / service_name
        
        print(f"🚀 Deploying {service_name}...")
        
        try:
            # Change to service directory
            os.chdir(service_path)
            
            # Deploy using Railway CLI
            result = subprocess.run([
                "railway", "up", "--detach"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {service_name} deployed successfully")
                return True
            else:
                print(f"❌ {service_name} deployment failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {service_name} deployment timed out")
            return False
        except Exception as e:
            print(f"❌ {service_name} deployment error: {e}")
            return False
        finally:
            os.chdir(self.root_path)

    def deploy_all(self, setup_missing=True):
        """Deploy all remaining services"""
        print("🚀 Starting deployment of remaining services...")
        
        ready_services, needs_setup = self.analyze_all_services()
        
        if setup_missing and needs_setup:
            print(f"\n🔧 Setting up {len(needs_setup)} services...")
            for service in needs_setup:
                self.setup_service(service)
                ready_services.append(service)
        
        print(f"\n🚀 Deploying {len(ready_services)} services...")
        successful = []
        failed = []
        
        for service in ready_services:
            if self.deploy_service(service):
                successful.append(service)
                time.sleep(5)  # Brief pause between deployments
            else:
                failed.append(service)
        
        print(f"\n📊 Deployment Summary:")
        print(f"✅ Successful: {len(successful)} services")
        if successful:
            for service in successful:
                print(f"  ✅ {service}")
        
        print(f"❌ Failed: {len(failed)} services")
        if failed:
            for service in failed:
                print(f"  ❌ {service}")

def main():
    """Main deployment function"""
    deployer = ServiceDeployer()
    deployer.deploy_all(setup_missing=True)

if __name__ == "__main__":
    main()
