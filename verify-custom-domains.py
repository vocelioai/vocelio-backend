#!/usr/bin/env python3
"""
🌟 Vocelio AI - Custom Domain Verification Script
Verify all 29 custom vocelio.ai domains are working correctly
"""

import requests
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Tuple

# 🎯 All 29 Vocelio Custom Domains
CUSTOM_DOMAINS = {
    # Core Foundation Services (7)
    "API Gateway": "https://api.vocelio.ai",
    "Overview Service": "https://overview.vocelio.ai", 
    "AI Agents": "https://agents.vocelio.ai",
    "Smart Campaigns": "https://campaigns.vocelio.ai",
    "Analytics Pro": "https://analytics.vocelio.ai",
    "Team Hub": "https://team.vocelio.ai",
    "Phone Numbers": "https://numbers.vocelio.ai",
    
    # Business Services (6)
    "Voice Lab": "https://voicelab.vocelio.ai",
    "Settings": "https://settings.vocelio.ai",
    "Flow Builder": "https://flowbuilder.vocelio.ai",
    "Call Center": "https://call.vocelio.ai",
    "Voice Marketplace": "https://voicemarketplace.vocelio.ai",
    "AI Brain": "https://brain.vocelio.ai",
    
    # Enterprise Features (6)
    "Integrations": "https://integrations.vocelio.ai",
    "Backend Platform": "https://backend.vocelio.ai",
    "Billing Pro": "https://billing.vocelio.ai",
    "Compliance": "https://compliance.vocelio.ai",
    "White Label": "https://whitelabel.vocelio.ai",
    "Developer API": "https://developer.vocelio.ai",
    
    # AI & Automation Services (6)
    "Knowledge Base": "https://knowledge.vocelio.ai",
    "Lead Management": "https://lead.vocelio.ai", 
    "Scheduling": "https://scheduling.vocelio.ai",
    "Data Warehouse": "https://data.vocelio.ai",
    "Identity Service": "https://identity.vocelio.ai",
    "Security Service": "https://security.vocelio.ai",
    
    # Communication & Compliance (4)
    "Notifications": "https://notifications.vocelio.ai",
    "Scripts": "https://scripts.vocelio.ai",
    "Webhooks": "https://webhooks.vocelio.ai",
    "API Management": "https://apimanagement.vocelio.ai"
}

def print_header():
    """Print verification header"""
    print("="*80)
    print("🌟 VOCELIO AI - CUSTOM DOMAIN VERIFICATION")
    print("="*80)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Checking {len(CUSTOM_DOMAINS)} custom vocelio.ai domains")
    print(f"🚀 Professional branding verification")
    print("="*80)

async def check_domain_async(session: aiohttp.ClientSession, name: str, url: str) -> Tuple[str, str, bool, int, str]:
    """Async domain health check"""
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with session.get(url, timeout=timeout, ssl=False) as response:
            status_code = response.status
            content_type = response.headers.get('content-type', 'unknown')
            
            if status_code == 200:
                return (name, url, True, status_code, "✅ HEALTHY")
            elif status_code in [404, 503]:
                return (name, url, False, status_code, "⚠️ SERVICE_UNAVAILABLE")
            else:
                return (name, url, False, status_code, "🔸 REDIRECT/OTHER")
                
    except asyncio.TimeoutError:
        return (name, url, False, 0, "⏱️ TIMEOUT")
    except Exception as e:
        error_msg = str(e)[:50]
        return (name, url, False, 0, f"❌ ERROR: {error_msg}")

async def verify_all_domains():
    """Verify all custom domains"""
    print_header()
    
    results = []
    healthy_count = 0
    
    # Create connector with SSL verification disabled for testing
    connector = aiohttp.TCPConnector(ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Create tasks for concurrent checking
        tasks = []
        for name, url in CUSTOM_DOMAINS.items():
            task = check_domain_async(session, name, url)
            tasks.append(task)
        
        print("🔍 Checking all domains concurrently...")
        print("-" * 80)
        
        # Execute all checks concurrently
        results = await asyncio.gather(*tasks)
    
    # Sort results by status (healthy first)
    results.sort(key=lambda x: (not x[2], x[0]))
    
    # Print results
    for name, url, is_healthy, status_code, status_msg in results:
        if is_healthy:
            healthy_count += 1
            print(f"✅ {name:<20} | {url:<35} | {status_msg}")
        else:
            print(f"❌ {name:<20} | {url:<35} | {status_msg}")
    
    # Summary
    print("="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    print(f"✅ Healthy Domains: {healthy_count}/{len(CUSTOM_DOMAINS)}")
    print(f"❌ Unhealthy Domains: {len(CUSTOM_DOMAINS) - healthy_count}")
    print(f"📈 Success Rate: {(healthy_count/len(CUSTOM_DOMAINS)*100):.1f}%")
    
    if healthy_count == len(CUSTOM_DOMAINS):
        print("\n🎉 PERFECT! All custom domains are operational!")
        print("🌟 Your Vocelio AI platform is enterprise-ready!")
    elif healthy_count > len(CUSTOM_DOMAINS) * 0.8:
        print("\n✅ EXCELLENT! Most domains are operational.")
        print("🔧 Just a few domains need attention.")
    else:
        print("\n⚠️  Some domains need attention.")
        print("🛠️  Check Railway custom domain configuration.")
    
    print("\n💡 Next Steps:")
    if healthy_count == len(CUSTOM_DOMAINS):
        print("   • Update your Vercel dashboard with these domains")
        print("   • Test frontend integration")
        print("   • Launch marketing campaigns!")
    else:
        print("   • Check Railway domain configuration")
        print("   • Verify DNS settings")
        print("   • Re-run this verification script")
    
    print("="*80)
    print(f"🏁 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def main():
    """Main function"""
    try:
        asyncio.run(verify_all_domains())
    except KeyboardInterrupt:
        print("\n⏹️ Verification cancelled by user.")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")

if __name__ == "__main__":
    main()
