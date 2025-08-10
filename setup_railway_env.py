#!/usr/bin/env python3
"""
🚀 Railway Environment Variables Setup Script
Automatically sets up all required environment variables for Railway deployment
"""

import subprocess
import json
import os
from typing import Dict, List

class RailwayEnvSetup:
    """Manages Railway environment variable setup"""
    
    def __init__(self):
        self.essential_vars = {
            # Core Application
            "ENVIRONMENT": "production",
            "PORT": "8000",
            "DEBUG": "false",
            
            # Security & Auth (REQUIRED - User must set these)
            "JWT_SECRET_KEY": "REQUIRED_USER_INPUT",
            "SECRET_KEY": "REQUIRED_USER_INPUT",
            "JWT_ALGORITHM": "HS256",
            "JWT_EXPIRE_MINUTES": "1440",
            
            # Database (REQUIRED - User must set these)
            "DATABASE_URL": "REQUIRED_USER_INPUT",
            "SUPABASE_URL": "REQUIRED_USER_INPUT", 
            "SUPABASE_KEY": "REQUIRED_USER_INPUT",
            
            # Redis/Caching (Optional - can use Railway Redis addon)
            "REDIS_URL": "OPTIONAL_RAILWAY_ADDON",
            
            # AI Services (REQUIRED for functionality)
            "OPENAI_API_KEY": "REQUIRED_USER_INPUT",
            "OPENAI_MODEL": "gpt-4o-mini",
            "ANTHROPIC_API_KEY": "REQUIRED_USER_INPUT",
            "ELEVENLABS_API_KEY": "REQUIRED_USER_INPUT",
            
            # Communication Services (REQUIRED for calls/SMS)
            "TWILIO_ACCOUNT_SID": "REQUIRED_USER_INPUT",
            "TWILIO_AUTH_TOKEN": "REQUIRED_USER_INPUT",
            
            # Payment Processing (REQUIRED for billing)
            "STRIPE_SECRET_KEY": "REQUIRED_USER_INPUT",
            "STRIPE_WEBHOOK_SECRET": "REQUIRED_USER_INPUT",
            "STRIPE_PUBLISHABLE_KEY": "REQUIRED_USER_INPUT",
            
            # CORS & Security
            "CORS_ORIGINS": "https://*.railway.app,https://*.vocelio.ai",
            "ALLOWED_ORIGINS": "https://*.railway.app,https://*.vocelio.ai",
            "ALLOWED_HOSTS": "*",
            
            # Service URLs (Your deployed Railway services)
            "TEAM_HUB_SERVICE_URL": "https://team-hub-production.up.railway.app",
            "OVERVIEW_SERVICE_URL": "https://overview-production.up.railway.app",
            "AI_AGENTS_SERVICE_URL": "https://ai-agents-service-production.up.railway.app",
            "SMART_CAMPAIGNS_SERVICE_URL": "https://smart-campaigns-production.up.railway.app",
            "PHONE_NUMBERS_SERVICE_URL": "https://phone-numbers-production.up.railway.app",
            "ANALYTICS_SERVICE_URL": "https://analytics-pro-production.up.railway.app",
            
            # Rate Limiting
            "RATE_LIMIT_REQUESTS": "1000",
            "RATE_LIMIT_WINDOW": "3600",
            
            # Monitoring
            "PROMETHEUS_ENABLED": "true",
            "PROMETHEUS_PORT": "9090",
            
            # Email (Optional)
            "DEFAULT_FROM_EMAIL": "support@vocelio.ai"
        }
        
        # Variables that need user input
        self.required_user_vars = [
            "JWT_SECRET_KEY", "SECRET_KEY", "DATABASE_URL", "SUPABASE_URL", 
            "SUPABASE_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", 
            "ELEVENLABS_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
            "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "STRIPE_PUBLISHABLE_KEY"
        ]

    def check_railway_cli(self) -> bool:
        """Check if Railway CLI is installed"""
        try:
            result = subprocess.run(['railway', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def install_railway_cli(self):
        """Install Railway CLI"""
        print("🔧 Installing Railway CLI...")
        if os.name == 'nt':  # Windows
            subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        else:  # Unix/macOS
            subprocess.run(['curl', '-fsSL', 'https://railway.app/install.sh'], 
                          shell=True, check=True)

    def login_railway(self):
        """Login to Railway"""
        print("🔐 Please login to Railway...")
        subprocess.run(['railway', 'login'], check=True)

    def set_env_var(self, key: str, value: str, project_id: str = None) -> bool:
        """Set a single environment variable on Railway"""
        try:
            cmd = ['railway', 'variables', 'set', f'{key}={value}']
            if project_id:
                cmd.extend(['--project', project_id])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Set {key}")
                return True
            else:
                print(f"❌ Failed to set {key}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error setting {key}: {e}")
            return False

    def bulk_set_variables(self, variables: Dict[str, str], project_id: str = None):
        """Set multiple environment variables"""
        print(f"🚀 Setting {len(variables)} environment variables...")
        
        success_count = 0
        for key, value in variables.items():
            if value not in ["REQUIRED_USER_INPUT", "OPTIONAL_RAILWAY_ADDON"]:
                if self.set_env_var(key, value, project_id):
                    success_count += 1
            else:
                print(f"⚠️  Skipping {key} - requires user input")
        
        print(f"✅ Successfully set {success_count}/{len(variables)} variables")

    def generate_env_template(self) -> str:
        """Generate a template for missing environment variables"""
        template = "# 🔐 Required Environment Variables for Railway\n"
        template += "# Copy these to Railway manually or use Railway CLI\n\n"
        
        for var in self.required_user_vars:
            template += f"{var}=your_{var.lower()}_here\n"
        
        return template

    def setup_project(self, project_name: str = None):
        """Complete Railway project setup"""
        print("🚀 Starting Railway Environment Setup...")
        
        # Check CLI
        if not self.check_railway_cli():
            print("Railway CLI not found. Installing...")
            self.install_railway_cli()
        
        # Login
        print("🔐 Ensuring Railway login...")
        try:
            # Check if already logged in
            result = subprocess.run(['railway', 'whoami'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.login_railway()
        except:
            self.login_railway()
        
        # Set variables
        safe_vars = {k: v for k, v in self.essential_vars.items() 
                    if v not in ["REQUIRED_USER_INPUT", "OPTIONAL_RAILWAY_ADDON"]}
        
        self.bulk_set_variables(safe_vars)
        
        # Generate template for missing vars
        template = self.generate_env_template()
        with open('railway_env_template.txt', 'w') as f:
            f.write(template)
        
        print("\n🎯 Setup Summary:")
        print(f"✅ Set {len(safe_vars)} automatic variables")
        print(f"⚠️  {len(self.required_user_vars)} variables need your input")
        print("📄 Created 'railway_env_template.txt' with required variables")
        print("\n🔗 Next steps:")
        print("1. Fill in railway_env_template.txt with your actual values")
        print("2. Set them manually in Railway dashboard or use:")
        print("   railway variables set KEY=value")

def main():
    """Main setup function"""
    setup = RailwayEnvSetup()
    setup.setup_project()

if __name__ == "__main__":
    main()
