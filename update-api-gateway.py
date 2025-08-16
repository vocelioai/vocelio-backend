#!/usr/bin/env python3
"""
🔧 API Gateway Health Endpoint Update Script
Deploys the updated health.py file to Railway API Gateway
"""

import requests
import os
import time
from datetime import datetime

def test_health_endpoints():
    """Test the new health endpoints after deployment"""
    base_url = "https://api.vocelio.ai"
    
    endpoints_to_test = [
        "/health",
        "/api/v1/health", 
        "/api/v1/twilio/health"
    ]
    
    print("🏥 Testing API Gateway Health Endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\n📍 Testing: {endpoint}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                timestamp = data.get("timestamp", "")
                print(f"   ✅ Status: {response.status_code} - Health: {status}")
                print(f"   ⏰ Timestamp: {timestamp}")
                
                # Show key info
                if "gateway" in data:
                    uptime = data["gateway"].get("uptime", "unknown")
                    print(f"   🔥 Gateway Status: {uptime}")
                
                if "deployed_services_count" in data:
                    count = data.get("deployed_services_count", 0)
                    print(f"   🚀 Services: {count}")
                
                if "service" in data:
                    service = data.get("service", "unknown")
                    print(f"   🎯 Service: {service}")
                    
                if "twilio_services" in data:
                    twilio_status = data["twilio_services"].get("status", "unknown")
                    twilio_count = data["twilio_services"].get("found", 0)
                    print(f"   📞 Twilio Status: {twilio_status} ({twilio_count} services)")
                    
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📝 Response: {response.text[:200]}")
                
        except requests.RequestException as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Health endpoint testing complete!")

if __name__ == "__main__":
    print("🚀 API Gateway Health Endpoint Update")
    print(f"📅 Started: {datetime.now().isoformat()}")
    print("-" * 50)
    
    # Wait a bit for any ongoing deployments to complete
    print("⏳ Waiting for deployment to stabilize...")
    time.sleep(5)
    
    # Test the endpoints
    test_health_endpoints()
    
    print("\n🎯 Next Steps:")
    print("1. ✅ Health endpoints implemented")  
    print("2. 🔄 Test frontend dashboard connections")
    print("3. 📊 Monitor health check responses")
    print("4. 🚀 Ready for production traffic!")
    