#!/usr/bin/env python3
"""
Quick health check for all Vocelio microservices.
Tests basic connectivity and health endpoints.
"""

import asyncio
import httpx
import time
import sys
from typing import Dict, List

async def check_service_health(service: str, port: int, timeout: float = 5.0) -> Dict:
    """Check health of a single service."""
    url = f"http://localhost:{port}/health"
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            return {
                "service": service,
                "port": port,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": response_time,
                "response": response.json() if response.status_code == 200 else None,
                "error": None
            }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "service": service,
            "port": port, 
            "status": "error",
            "status_code": None,
            "response_time": response_time,
            "response": None,
            "error": str(e)
        }

async def check_all_services() -> List[Dict]:
    """Check health of all services."""
    services = {
        "api-gateway": 8000,
        "overview": 8001,
        "ai-agents": 8002,
        "smart-campaigns": 8003,
        "analytics-pro": 8004,
        "team-hub": 8005,
        "phone-numbers": 8006,
        "voice-lab": 8007,
        "settings": 8008,
        "flow-builder": 8009,
        "call-center": 8010,
        "integrations": 8011,
        "voice-marketplace": 8012,
        "billing-pro": 8013,
        "developer-api": 8014,
        "agent-store": 8015,
        "compliance": 8016,
        "white-label": 8017
    }
    
    print("🔍 Checking health of all services...")
    print("=" * 60)
    
    # Check all services concurrently
    tasks = [check_service_health(name, port) for name, port in services.items()]
    results = await asyncio.gather(*tasks)
    
    # Print results
    healthy_count = 0
    unhealthy_count = 0
    error_count = 0
    
    for result in results:
        status_icon = {
            "healthy": "✅",
            "unhealthy": "⚠️",
            "error": "❌"
        }[result["status"]]
        
        service_name = result["service"]
        port = result["port"]
        response_time = result["response_time"]
        
        if result["status"] == "healthy":
            healthy_count += 1
            print(f"{status_icon} {service_name:<20} Port {port:<5} {response_time:.3f}s")
        elif result["status"] == "unhealthy":
            unhealthy_count += 1
            status_code = result["status_code"]
            print(f"{status_icon} {service_name:<20} Port {port:<5} {response_time:.3f}s [HTTP {status_code}]")
        else:
            error_count += 1
            error = result["error"]
            print(f"{status_icon} {service_name:<20} Port {port:<5} {response_time:.3f}s - {error}")
    
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    print(f"✅ Healthy Services: {healthy_count}")
    print(f"⚠️  Unhealthy Services: {unhealthy_count}")
    print(f"❌ Error Services: {error_count}")
    print(f"📈 Overall Health: {(healthy_count / len(services)) * 100:.1f}%")
    
    if error_count > 0:
        print("\n🔧 TROUBLESHOOTING:")
        print("- Make sure services are running (use launch_services.py)")
        print("- Check for port conflicts")
        print("- Verify service dependencies are installed")
        print("- Check service logs for specific errors")
    
    return results

async def main():
    """Main health check execution."""
    results = await check_all_services()
    
    # Exit with appropriate code
    error_count = len([r for r in results if r["status"] == "error"])
    unhealthy_count = len([r for r in results if r["status"] == "unhealthy"])
    
    if error_count > 0 or unhealthy_count > 0:
        sys.exit(1)
    else:
        print("\n🎉 All services are healthy!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
