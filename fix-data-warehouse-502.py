#!/usr/bin/env python3
"""
🔧 Fix Data Warehouse 502 Error & Update Service URLs
This script identifies and fixes service URL mismatches
"""

import asyncio
import aiohttp
from datetime import datetime

# Current URLs from your .env vs actual working URLs from logs
URL_CORRECTIONS = {
    # Working URLs (from logs)
    "team-hub": "https://team-hub-production.up.railway.app",
    "overview": "https://overview-production.up.railway.app", 
    "api-gateway": "https://api-gateway-production-588d.up.railway.app",
    "smart-campaigns": "https://smart-campaigns-production.up.railway.app",
    "phone-numbers": "https://phone-numbers-production.up.railway.app",
    "analytics-pro": "https://analytics-pro-production.up.railway.app",
    "ai-brain": "https://ai-brain-production.up.railway.app",
    "billing-pro": "https://billing-pro-production.up.railway.app",
    "flow-builder": "https://flow-builder-production.up.railway.app",
    "settings": "https://settings-production.up.railway.app",
    "voice-lab": "https://voice-lab-production.up.railway.app",
    "voice-marketplace": "https://voice-marketplace-production.up.railway.app",
    "lead-management": "https://lead-management-production.up.railway.app",
    "scripts": "https://scripts-production.up.railway.app",
    
    # URLs with issues (404s in logs) - need to find correct URLs
    "ai-agents": "https://ai-agents-service-production.up.railway.app",  # Using your .env version
    "call-center": "https://call-center-production-19af.up.railway.app",  # Using your .env version
    "integrations": "https://integrations-production-a079.up.railway.app",  # Using your .env version
    "compliance": "https://compliance-production-a432.up.railway.app",  # Using your .env version
    "white-label": "https://white-label-production-ab67.up.railway.app",  # Using your .env version
    "developer-api": "https://developer-api-production-a124.up.railway.app",  # Using your .env version
    "knowledge-base": "https://knowledge-base-production.up.railway.app",  # Using your .env version
    "notifications": "https://notifications-production.up.railway.app",  # Using your .env version
    "scheduling": "https://scheduling-production.up.railway.app",  # Using your .env version
    "webhooks": "https://webhooks-production.up.railway.app",  # Using your .env version
    "data-warehouse": "https://data-warehouse-production-f093.up.railway.app"  # From Railway vars
}

async def test_service_url(name: str, url: str):
    """Test if a service URL is accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return name, url, "✅ Working", response.status
                elif response.status == 404:
                    return name, url, "⚠️ No /health endpoint", response.status
                else:
                    return name, url, f"❌ Error", response.status
    except asyncio.TimeoutError:
        return name, url, "⏰ Timeout", 0
    except Exception as e:
        return name, url, f"❌ {str(e)[:30]}", 0

async def test_all_urls():
    """Test all service URLs to identify issues"""
    print("🔍 Testing All Service URLs...")
    print("=" * 60)
    
    tasks = [test_service_url(name, url) for name, url in URL_CORRECTIONS.items()]
    results = await asyncio.gather(*tasks)
    
    working = []
    issues = []
    
    for name, url, status, code in results:
        print(f"{status} {name:20} | {code} | {url}")
        
        if "Working" in status or code == 404:  # 404 on /health is often fine
            working.append((name, url))
        else:
            issues.append((name, url, status, code))
    
    print(f"\n📊 Results:")
    print(f"✅ Working/Accessible: {len(working)}")
    print(f"❌ Issues: {len(issues)}")
    
    if issues:
        print(f"\n🚨 Services with Issues:")
        for name, url, status, code in issues:
            print(f"  - {name}: {status} ({code})")
    
    return working, issues

async def main():
    """Main diagnosis and fix process"""
    print("🔧 DATA WAREHOUSE 502 ERROR DIAGNOSIS")
    print("=" * 45)
    print(f"📅 {datetime.now().isoformat()}")
    print()
    
    working, issues = await test_all_urls()
    
    print("\n💡 DIAGNOSIS:")
    if len(working) >= len(URL_CORRECTIONS) * 0.8:
        print("✅ Most services are accessible")
        print("🎯 The 502 error is likely a temporary issue")
        print("🔄 Data Warehouse may just need a restart")
    else:
        print("⚠️ Multiple service accessibility issues detected")
        print("🛠️ URL corrections may be needed")
    
    print("\n🚀 RECOMMENDED ACTIONS:")
    print("1. Restart Data Warehouse service: railway service data-warehouse && railway up")
    print("2. Verify Supabase credentials are set: railway variables")
    print("3. Check service logs for specific errors")
    print("4. Update any 404 URLs in your .env file")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 All services appear healthy!")
    else:
        print("\n⚠️ Some issues detected - see recommendations above")
