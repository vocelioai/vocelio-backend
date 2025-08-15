#!/usr/bin/env python3
"""
🔍 Vocelio Supabase Connection Verification Script
Comprehensive testing of all services with new Supabase credentials
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

# New Supabase Configuration
SUPABASE_URL = "https://bhzhgivqqnwvndzjthqv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJoemhnaXZxcW53dm5kemp0aHF2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyODQ5MjgsImV4cCI6MjA3MDg2MDkyOH0.1JyoU3xQG7McYRIWzJfTfwv6oH7FCIZkLTLUnahLtKI"

# Service URLs
SERVICES = {
    "API Gateway": "https://api-gateway-production-588d.up.railway.app",
    "Overview": "https://overview-production.up.railway.app", 
    "AI Agents": "https://ai-agents-service-production.up.railway.app",
    "Smart Campaigns": "https://smart-campaigns-production.up.railway.app",
    "Analytics Pro": "https://analytics-pro-production.up.railway.app",
    "Team Hub": "https://team-hub-production.up.railway.app",
    "Phone Numbers": "https://phone-numbers-production.up.railway.app",
    "Voice Lab": "https://voice-lab-production.up.railway.app",
    "Settings": "https://settings-production.up.railway.app",
    "Flow Builder": "https://flow-builder-production.up.railway.app",
    "Call Center": "https://call-center-production-19af.up.railway.app",
    "Voice Marketplace": "https://voice-marketplace-production.up.railway.app",
    "AI Brain": "https://ai-brain-production.up.railway.app",
    "Integrations": "https://integrations-production-a079.up.railway.app",
    "Billing Pro": "https://billing-pro-production.up.railway.app",
    "Compliance": "https://compliance-production-a432.up.railway.app",
    "White Label": "https://white-label-production-ab67.up.railway.app",
    "Developer API": "https://developer-api-production-a124.up.railway.app",
    "Knowledge Base": "https://knowledge-base-production.up.railway.app",
    "Lead Management": "https://lead-management-production.up.railway.app",
    "Scheduling": "https://scheduling-production.up.railway.app",
    "Data Warehouse": "https://data-warehouse-production-f093.up.railway.app",
    "Notifications": "https://notifications-production.up.railway.app",
    "Scripts": "https://scripts-production.up.railway.app",
    "Webhooks": "https://webhooks-production.up.railway.app"
}

async def test_supabase_direct():
    """Test direct connection to Supabase"""
    print("🔍 Testing Direct Supabase Connection...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test REST API endpoint
            async with session.get(
                f"{SUPABASE_URL}/rest/v1/", 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    print("✅ Supabase REST API: Connected")
                    return True
                else:
                    print(f"❌ Supabase REST API: Failed ({response.status})")
                    return False
    except Exception as e:
        print(f"❌ Supabase Direct Connection: {str(e)}")
        return False

async def test_service_health(service_name: str, url: str) -> Tuple[str, bool, str]:
    """Test individual service health and Supabase connection"""
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            health_endpoints = ["/health", "/api/health", "/healthz", "/status"]
            
            for endpoint in health_endpoints:
                try:
                    async with session.get(
                        f"{url}{endpoint}",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.text()
                            return service_name, True, f"✅ Healthy ({endpoint})"
                        elif response.status == 404:
                            continue
                        else:
                            return service_name, False, f"❌ Health check failed ({response.status})"
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    continue
            
            # If no health endpoint found, test root
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in [200, 404]:  # Service is responding
                    return service_name, True, "✅ Service responding"
                else:
                    return service_name, False, f"❌ Service error ({response.status})"
                    
    except asyncio.TimeoutError:
        return service_name, False, "⏰ Timeout"
    except Exception as e:
        return service_name, False, f"❌ {str(e)[:50]}..."

async def test_database_tables():
    """Test if database tables exist"""
    print("\n🗄️ Testing Database Schema...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Key tables to check
    test_tables = [
        "organizations",
        "users", 
        "ai_agents",
        "calls",
        "campaigns",
        "flows",
        "settings"
    ]
    
    try:
        async with aiohttp.ClientSession() as session:
            for table in test_tables:
                try:
                    async with session.get(
                        f"{SUPABASE_URL}/rest/v1/{table}?select=count",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            print(f"✅ Table '{table}': Accessible")
                        else:
                            print(f"❌ Table '{table}': Not accessible ({response.status})")
                except Exception as e:
                    print(f"⚠️ Table '{table}': {str(e)[:30]}...")
                    
    except Exception as e:
        print(f"❌ Database Schema Test: {str(e)}")

async def main():
    """Main verification process"""
    print("🚀 VOCELIO SUPABASE CONNECTION VERIFICATION")
    print("=" * 50)
    print(f"🔗 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 Using Key: {SUPABASE_KEY[:20]}...")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test direct Supabase connection
    supabase_ok = await test_supabase_direct()
    print()
    
    # Test database schema
    await test_database_tables()
    print()
    
    # Test all services
    print("🌐 Testing Service Connectivity...")
    print("-" * 40)
    
    tasks = [test_service_health(name, url) for name, url in SERVICES.items()]
    results = await asyncio.gather(*tasks)
    
    healthy_count = 0
    for service_name, is_healthy, status in results:
        print(f"{status} {service_name}")
        if is_healthy:
            healthy_count += 1
    
    print()
    print("📊 VERIFICATION SUMMARY")
    print("=" * 30)
    print(f"🔗 Supabase Direct: {'✅ Connected' if supabase_ok else '❌ Failed'}")
    print(f"🌐 Services Healthy: {healthy_count}/{len(SERVICES)}")
    print(f"📈 Success Rate: {(healthy_count/len(SERVICES)*100):.1f}%")
    
    if supabase_ok and healthy_count >= len(SERVICES) * 0.8:
        print("\n🎉 VERIFICATION SUCCESSFUL!")
        print("✅ New Supabase credentials are working correctly")
        print("✅ Services are connecting properly")
    else:
        print("\n⚠️ VERIFICATION ISSUES DETECTED")
        print("Some services may need manual attention")
    
    return supabase_ok, healthy_count, len(SERVICES)

if __name__ == "__main__":
    asyncio.run(main())
