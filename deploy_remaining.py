#!/usr/bin/env python3

import subprocess
import os
import time
from concurrent.futures import ThreadPoolExecutor

# Services that still need to be deployed
remaining_services = [
    "integrations",
    "settings", 
    "developer-api",
    "compliance",
    "white-label"
]

def deploy_service(service_name):
    """Deploy a single service to Railway"""
    try:
        service_path = f"apps/{service_name}"
        print(f"🚀 Starting deployment of {service_name}...")
        
        # Change to service directory and deploy
        result = subprocess.run(
            ["railway", "up"],
            cwd=service_path,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per service
        )
        
        if result.returncode == 0:
            print(f"✅ {service_name} deployed successfully!")
            return True
        else:
            print(f"❌ {service_name} deployment failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {service_name} deployment timed out")
        return False
    except Exception as e:
        print(f"💥 {service_name} deployment error: {e}")
        return False

def main():
    print("🔄 Starting batch deployment of remaining services...")
    print(f"Services to deploy: {', '.join(remaining_services)}")
    
    # Deploy services with a limited number of parallel deployments
    # Railway has rate limits, so we'll do 3 at a time
    max_workers = 3
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(deploy_service, remaining_services))
    
    # Count successful deployments
    successful = sum(results)
    total = len(remaining_services)
    
    print(f"\n📊 Deployment Summary:")
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 All services deployed successfully!")
    else:
        print("⚠️  Some services failed to deploy. Check logs above.")

if __name__ == "__main__":
    main()
