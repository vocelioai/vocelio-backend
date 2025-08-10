#!/usr/bin/env python3
"""
Deploy Services to Railway with Project Linking
"""

import os
import subprocess
import time
from pathlib import Path

def deploy_service_to_railway(service_name, project_id="c4d5b487-c7f2-4d85-827e-0a5bc0f71799"):
    """Deploy a single service to Railway"""
    
    root_path = Path("c:/Users/SNC/OneDrive/Desktop/vocelio-backend")
    service_path = root_path / "apps" / service_name
    
    if not service_path.exists():
        print(f"❌ {service_name} - Directory not found")
        return False
    
    print(f"🚀 Deploying {service_name}...")
    
    try:
        # Change to service directory
        os.chdir(service_path)
        
        # Create or update Railway service
        print(f"  📡 Adding service {service_name}...")
        add_result = subprocess.run([
            "railway", "service", "--name", service_name
        ], capture_output=True, text=True, timeout=60)
        
        if add_result.returncode != 0:
            print(f"  ⚠️  Service might already exist: {add_result.stderr}")
        
        # Deploy the service
        print(f"  📦 Uploading and deploying...")
        deploy_result = subprocess.run([
            "railway", "up", "--detach", "--service", service_name
        ], capture_output=True, text=True, timeout=300)
        
        if deploy_result.returncode == 0:
            print(f"✅ {service_name} deployed successfully")
            print(f"  🔗 {deploy_result.stdout.strip()}")
            return True
        else:
            print(f"❌ {service_name} deployment failed:")
            print(f"  {deploy_result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {service_name} deployment timed out")
        return False
    except Exception as e:
        print(f"❌ {service_name} deployment error: {e}")
        return False
    finally:
        os.chdir(root_path)

def deploy_batch(services, delay=10):
    """Deploy a batch of services with delays"""
    successful = []
    failed = []
    
    for i, service in enumerate(services, 1):
        print(f"\n[{i}/{len(services)}] Deploying {service}...")
        
        if deploy_service_to_railway(service):
            successful.append(service)
            if i < len(services):  # Don't wait after the last service
                print(f"  ⏳ Waiting {delay}s before next deployment...")
                time.sleep(delay)
        else:
            failed.append(service)
    
    return successful, failed

def main():
    """Deploy all remaining services"""
    print("🚀 Railway Service Deployment")
    print("=" * 50)
    
    # Batch 1: Core AI Services
    ai_services = ["ai-brain", "agents", "agent-store"]
    print(f"\n📦 Batch 1: AI Services ({len(ai_services)} services)")
    ai_success, ai_failed = deploy_batch(ai_services)
    
    # Batch 2: Business Services  
    business_services = ["billing-pro", "call-center", "voice-lab"]
    print(f"\n📦 Batch 2: Business Services ({len(business_services)} services)")
    biz_success, biz_failed = deploy_batch(business_services)
    
    # Batch 3: Platform Services
    platform_services = ["flow-builder", "integrations", "settings"]
    print(f"\n📦 Batch 3: Platform Services ({len(platform_services)} services)")
    plat_success, plat_failed = deploy_batch(platform_services)
    
    # Batch 4: Enterprise Services
    enterprise_services = ["developer-api", "compliance", "white-label", "voice-marketplace"]
    print(f"\n📦 Batch 4: Enterprise Services ({len(enterprise_services)} services)")
    ent_success, ent_failed = deploy_batch(enterprise_services)
    
    # Summary
    all_successful = ai_success + biz_success + plat_success + ent_success
    all_failed = ai_failed + biz_failed + plat_failed + ent_failed
    
    print(f"\n📊 Deployment Summary")
    print("=" * 50)
    print(f"✅ Successfully deployed: {len(all_successful)} services")
    for service in all_successful:
        print(f"  ✅ {service}")
    
    print(f"\n❌ Failed deployments: {len(all_failed)} services")
    for service in all_failed:
        print(f"  ❌ {service}")
    
    print(f"\n🎯 Total services deployed: {len(all_successful)}/{len(all_successful) + len(all_failed)}")

if __name__ == "__main__":
    main()
