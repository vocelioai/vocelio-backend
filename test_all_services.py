#!/usr/bin/env python3
"""
🩺 Vocelio Services Health Check
Tests all 21 deployed Railway services
"""

import requests
import time
from datetime import datetime
from typing import Dict, List

class ServiceHealthChecker:
    """Health checker for all Vocelio microservices"""
    
    def __init__(self):
        self.services = {
            # Original Services
            "overview": "https://overview-production.up.railway.app",
            "agents": "https://agents-production-768d.up.railway.app",
            "ai-agents-service": "https://ai-agents-service-production.up.railway.app",
            "smart-campaigns": "https://smart-campaigns-production.up.railway.app",
            "phone-numbers": "https://phone-numbers-production.up.railway.app",
            "analytics-pro": "https://analytics-pro-production.up.railway.app",
            "team-hub": "https://team-hub-production.up.railway.app",
            "api-gateway": "https://api-gateway-production-588d.up.railway.app",
            
            # New Services
            "call-center": "https://call-center-production-19af.up.railway.app",
            "voice-marketplace": "https://voice-marketplace-production.up.railway.app",
            "voice-lab": "https://voice-lab-production.up.railway.app",
            "flow-builder": "https://flow-builder-production.up.railway.app",
            "ai-brain": "https://ai-brain-production.up.railway.app",
            "integrations": "https://integrations-production-a079.up.railway.app",
            "agent-store": "https://agent-store-production.up.railway.app",
            "billing-pro": "https://billing-pro-production.up.railway.app",
            "compliance": "https://compliance-production-a432.up.railway.app",
            "white-label": "https://white-label-production-ab67.up.railway.app",
            "developer-api": "https://developer-api-production-a124.up.railway.app",
            "settings": "https://settings-production.up.railway.app",
        }
        
        self.results = {}
        
    def check_service_health(self, name: str, url: str) -> Dict:
        """Check health of a single service"""
        try:
            # Try health endpoint first
            health_url = f"{url}/health"
            start_time = time.time()
            
            response = requests.get(health_url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "status": "healthy",
                        "response_time": f"{response_time:.0f}ms",
                        "service_info": data,
                        "url": health_url
                    }
                except:
                    return {
                        "status": "healthy",
                        "response_time": f"{response_time:.0f}ms", 
                        "service_info": "Non-JSON response",
                        "url": health_url
                    }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": f"{response_time:.0f}ms",
                    "error": f"HTTP {response.status_code}",
                    "url": health_url
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "error": "Request timed out",
                "url": health_url
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error", 
                "error": "Could not connect to service",
                "url": health_url
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": health_url
            }
    
    def check_all_services(self) -> Dict:
        """Check health of all services"""
        print("🩺 Starting Vocelio Services Health Check...")
        print("=" * 60)
        
        healthy_count = 0
        total_count = len(self.services)
        
        for name, url in self.services.items():
            print(f"Checking {name:<20} ... ", end="", flush=True)
            
            result = self.check_service_health(name, url)
            self.results[name] = result
            
            if result["status"] == "healthy":
                print(f"✅ {result['response_time']}")
                healthy_count += 1
            elif result["status"] == "timeout":
                print("⏰ TIMEOUT")
            elif result["status"] == "connection_error":
                print("🔌 CONNECTION ERROR")
            else:
                print(f"❌ {result.get('error', 'Unknown error')}")
        
        print("=" * 60)
        print(f"📊 Health Check Summary:")
        print(f"✅ Healthy: {healthy_count}/{total_count} ({healthy_count/total_count*100:.1f}%)")
        print(f"❌ Unhealthy: {total_count - healthy_count}/{total_count}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate detailed health report"""
        if not self.results:
            return "No health check results available"
        
        report = f"""
# 🩺 Vocelio Services Health Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Summary
"""
        
        healthy = [name for name, result in self.results.items() if result["status"] == "healthy"]
        unhealthy = [name for name, result in self.results.items() if result["status"] != "healthy"]
        
        report += f"- ✅ **Healthy Services**: {len(healthy)}/{len(self.results)}\n"
        report += f"- ❌ **Unhealthy Services**: {len(unhealthy)}/{len(self.results)}\n\n"
        
        if healthy:
            report += "## ✅ Healthy Services\n"
            for name in healthy:
                result = self.results[name]
                report += f"- **{name}**: {result['response_time']} - {result['url']}\n"
            report += "\n"
        
        if unhealthy:
            report += "## ❌ Unhealthy Services\n"
            for name in unhealthy:
                result = self.results[name]
                report += f"- **{name}**: {result['status']} - {result.get('error', 'Unknown error')}\n"
            report += "\n"
        
        return report

def main():
    """Run health check and generate report"""
    checker = ServiceHealthChecker()
    results = checker.check_all_services()
    
    # Generate and save report
    report = checker.generate_report()
    with open('SERVICES_HEALTH_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: SERVICES_HEALTH_REPORT.md")
    
    # Show immediate next steps based on results
    healthy_count = len([r for r in results.values() if r["status"] == "healthy"])
    total_count = len(results)
    
    if healthy_count == total_count:
        print("\n🎉 ALL SERVICES HEALTHY! Ready for next steps:")
        print("1. Update enhanced gateway with service URLs")
        print("2. Set up monitoring and alerting")
        print("3. Begin feature development")
    else:
        print(f"\n⚠️  {total_count - healthy_count} services need attention")
        print("1. Check Railway deployment logs for failing services")
        print("2. Verify environment variables are set correctly")
        print("3. Check service dependencies")

if __name__ == "__main__":
    main()
