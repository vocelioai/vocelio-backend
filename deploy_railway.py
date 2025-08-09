#!/usr/bin/env python3
"""
Railway deployment script for Vocelio microservices.
Deploys services to Railway with proper configuration.
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path

class RailwayDeployer:
    def __init__(self):
        self.services = [
            "api-gateway",
            "overview", 
            "ai-agents",
            "smart-campaigns",
            "analytics-pro",
            "team-hub",
            "phone-numbers",
            "voice-lab",
            "settings",
            "flow-builder",
            "call-center",
            "integrations",
            "voice-marketplace",
            "billing-pro",
            "developer-api",
            "agent-store",
            "compliance",
            "white-label"
        ]
        
        self.environment_variables = {
            "ENVIRONMENT": "production",
            "DATABASE_URL": "${{Postgres.DATABASE_URL}}",
            "REDIS_URL": "${{Redis.REDIS_URL}}",
            "JWT_SECRET_KEY": "${{Railway.JWT_SECRET_KEY}}",
            "OPENAI_API_KEY": "${{Railway.OPENAI_API_KEY}}",
            "ANTHROPIC_API_KEY": "${{Railway.ANTHROPIC_API_KEY}}",
            "SUPABASE_URL": "${{Railway.SUPABASE_URL}}",
            "SUPABASE_ANON_KEY": "${{Railway.SUPABASE_ANON_KEY}}",
            "SUPABASE_SERVICE_ROLE_KEY": "${{Railway.SUPABASE_SERVICE_ROLE_KEY}}"
        }

    def check_railway_cli(self) -> bool:
        """Check if Railway CLI is installed."""
        try:
            result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Railway CLI found: {result.stdout.strip()}")
                return True
            else:
                print("❌ Railway CLI not found")
                return False
        except FileNotFoundError:
            print("❌ Railway CLI not installed")
            print("Install with: npm install -g @railway/cli")
            return False

    def login_to_railway(self) -> bool:
        """Login to Railway."""
        try:
            print("🔑 Logging into Railway...")
            result = subprocess.run(["railway", "login"], check=True)
            print("✅ Successfully logged into Railway")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to login to Railway")
            return False

    def create_project(self, project_name: str = "vocelio-backend") -> bool:
        """Create Railway project."""
        try:
            print(f"🏗️  Creating Railway project: {project_name}")
            result = subprocess.run(
                ["railway", "project", "create", project_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Project created successfully")
                return True
            else:
                print(f"⚠️  Project might already exist: {result.stderr}")
                # Try to link to existing project
                return self.link_project(project_name)
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create project: {e}")
            return False

    def link_project(self, project_name: str) -> bool:
        """Link to existing Railway project."""
        try:
            print(f"🔗 Linking to existing project: {project_name}")
            result = subprocess.run(
                ["railway", "link", project_name],
                check=True
            )
            print("✅ Successfully linked to project")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to link to project")
            return False

    def deploy_service(self, service_name: str) -> bool:
        """Deploy a single service to Railway."""
        service_path = Path(f"apps/{service_name}")
        
        if not service_path.exists():
            print(f"❌ Service path not found: {service_path}")
            return False
        
        railway_config = service_path / "railway.toml"
        if not railway_config.exists():
            print(f"❌ Railway config not found: {railway_config}")
            return False
        
        try:
            print(f"🚀 Deploying {service_name}...")
            
            # Change to service directory
            original_cwd = os.getcwd()
            os.chdir(service_path)
            
            # Deploy with Railway
            result = subprocess.run(
                ["railway", "up", "--detach"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Change back to original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                print(f"✅ {service_name} deployed successfully")
                # Extract deployment URL if available
                if "https://" in result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "https://" in line:
                            print(f"🌐 Service URL: {line.strip()}")
                            break
                return True
            else:
                print(f"❌ Failed to deploy {service_name}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Deployment timeout for {service_name}")
            os.chdir(original_cwd)
            return False
        except Exception as e:
            print(f"❌ Deployment error for {service_name}: {e}")
            os.chdir(original_cwd)
            return False

    def set_environment_variables(self) -> bool:
        """Set environment variables for the project."""
        try:
            print("🔧 Setting environment variables...")
            
            for key, value in self.environment_variables.items():
                print(f"Setting {key}...")
                result = subprocess.run(
                    ["railway", "variables", "set", f"{key}={value}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"⚠️  Warning: Failed to set {key}")
            
            print("✅ Environment variables configured")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set environment variables: {e}")
            return False

    def deploy_all_services(self, service_filter=None) -> dict:
        """Deploy all services or filtered subset."""
        services_to_deploy = self.services
        if service_filter:
            services_to_deploy = [s for s in self.services if s in service_filter]
        
        print(f"🚀 Deploying {len(services_to_deploy)} services to Railway...")
        print("=" * 60)
        
        results = {}
        successful_deployments = 0
        
        for service in services_to_deploy:
            success = self.deploy_service(service)
            results[service] = success
            if success:
                successful_deployments += 1
            
            # Brief pause between deployments
            time.sleep(5)
        
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 60)
        print(f"✅ Successful: {successful_deployments}")
        print(f"❌ Failed: {len(services_to_deploy) - successful_deployments}")
        print(f"📈 Success Rate: {(successful_deployments / len(services_to_deploy)) * 100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for service, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  {service:<20} {status}")
        
        return results

def main():
    """Main deployment execution."""
    deployer = RailwayDeployer()
    
    print("🚂 Vocelio Railway Deployment")
    print("=" * 40)
    
    # Check prerequisites
    if not deployer.check_railway_cli():
        sys.exit(1)
    
    if not deployer.login_to_railway():
        sys.exit(1)
    
    if not deployer.create_project():
        sys.exit(1)
    
    # Set environment variables
    deployer.set_environment_variables()
    
    # Check for service filter
    service_filter = None
    if len(sys.argv) > 1:
        service_filter = sys.argv[1:]
        print(f"Deploying filtered services: {', '.join(service_filter)}")
    
    # Deploy services
    results = deployer.deploy_all_services(service_filter)
    
    # Exit with appropriate code
    failed_count = len([r for r in results.values() if not r])
    if failed_count > 0:
        print(f"\n❌ {failed_count} deployments failed")
        sys.exit(1)
    else:
        print("\n🎉 All services deployed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
