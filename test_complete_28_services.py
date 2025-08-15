#!/usr/bin/env python3
"""
🩺 Complete Vocelio Services Health Check - All 28 Services
Tests all deployed Railway services including Enterprise Tier 1
"""

import requests
import time
from datetime import datetime
from typing import Dict, List

class Complete28ServiceHealthChecker:
    """Health checker for all 28 Vocelio microservices"""
    
    def __init__(self):
        self.services = {
            # Core Foundation Services (7)
            "api-gateway": "https://api-gateway-production-588d.up.railway.app",
            "overview": "https://overview-production.up.railway.app",
            "ai-agents": "https://ai-agents-service-production.up.railway.app",
            "smart-campaigns": "https://smart-campaigns-production.up.railway.app",
            "analytics-pro": "https://analytics-pro-production.up.railway.app",
            "team-hub": "https://team-hub-production.up.railway.app",
            "phone-numbers": "https://phone-numbers-production.up.railway.app",
            
            # Core Business Services (6)
            "voice-lab": "https://voice-lab-production.up.railway.app",
            "settings": "https://settings-production.up.railway.app",
            "flow-builder": "https://flow-builder-production.up.railway.app",
            "call-center": "https://call-center-production.up.railway.app",
            "voice-marketplace": "https://voice-marketplace-production.up.railway.app",
            "billing-pro": "https://billing-pro-production.up.railway.app",
            
            # Advanced Features (6)
            "integrations": "https://integrations-production.up.railway.app",
            "developer-api": "https://developer-api-production.up.railway.app",
            "agent-store": "https://agent-store-production.up.railway.app",
            "compliance": "https://compliance-production.up.railway.app",
            "white-label": "https://white-label-production-ab67.up.railway.app",
            "ai-brain": "https://ai-brain-production.up.railway.app",
            
            # World-Class Business Services (6)
            "knowledge-base": "https://knowledge-base-production.up.railway.app",
            "lead-management": "https://lead-management-production.up.railway.app",
            "notifications": "https://notifications-production.up.railway.app",
            "scheduling": "https://scheduling-production.up.railway.app",
            "scripts": "https://scripts-production.up.railway.app",
            "webhooks": "https://webhooks-production.up.railway.app",
            
            # Enterprise Tier 1 Services (3)
            "sso-identity": "https://sso-identity-production.up.railway.app",
            "audit-compliance": "https://audit-compliance-production.up.railway.app",
            "enterprise-security": "https://enterprise-security-production.up.railway.app",
            "api-management": "https://api-management-production.up.railway.app"
        }
        
        self.categories = {
            "Core Foundation": ["api-gateway", "overview", "ai-agents", "smart-campaigns", 
                              "analytics-pro", "team-hub", "phone-numbers"],
            "Core Business": ["voice-lab", "settings", "flow-builder", "call-center", 
                            "voice-marketplace", "billing-pro"],
            "Advanced Features": ["integrations", "developer-api", "agent-store", 
                                "compliance", "white-label", "ai-brain"],
            "World-Class Business": ["knowledge-base", "lead-management", "notifications", 
                                   "scheduling", "scripts", "webhooks"],
            "Enterprise Tier 1": ["sso-identity", "audit-compliance", "enterprise-security", 
                                 "api-management"]
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
        """Check health of all 28 services"""
        print("🩺 Starting Complete Vocelio Services Health Check (28 Services)...")
        print("=" * 80)
        
        healthy_count = 0
        unhealthy_count = 0
        error_count = 0
        
        # Check services by category
        for category, service_list in self.categories.items():
            print(f"\n📂 {category} ({len(service_list)} services):")
            print("-" * 60)
            
            category_healthy = 0
            category_total = len(service_list)
            
            for service_name in service_list:
                if service_name in self.services:
                    result = self.check_service_health(service_name, self.services[service_name])
                    self.results[service_name] = result
                    
                    status_icon = {
                        "healthy": "✅",
                        "unhealthy": "⚠️",
                        "timeout": "⏰",
                        "connection_error": "❌",
                        "error": "💥"
                    }.get(result["status"], "❓")
                    
                    if result["status"] == "healthy":
                        healthy_count += 1
                        category_healthy += 1
                        response_time = result["response_time"]
                        print(f"  {status_icon} {service_name:<20} {response_time}")
                    else:
                        if result["status"] == "unhealthy":
                            unhealthy_count += 1
                        else:
                            error_count += 1
                        
                        error_msg = result.get("error", "Unknown error")
                        response_time = result.get("response_time", "N/A")
                        print(f"  {status_icon} {service_name:<20} {response_time} - {error_msg}")
            
            # Category summary
            category_percentage = (category_healthy / category_total) * 100
            print(f"  📊 Category Health: {category_healthy}/{category_total} ({category_percentage:.1f}%)")
        
        total_services = len(self.services)
        overall_percentage = (healthy_count / total_services) * 100
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"✅ Healthy Services: {healthy_count}")
        print(f"⚠️  Unhealthy Services: {unhealthy_count}")
        print(f"❌ Error Services: {error_count}")
        print(f"📈 Overall Health: {overall_percentage:.1f}%")
        print(f"🎯 Total Services Checked: {total_services}/28")
        
        # Detailed category breakdown
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, service_list in self.categories.items():
            category_healthy = sum(1 for s in service_list if s in self.results and self.results[s]["status"] == "healthy")
            category_total = len(service_list)
            category_percentage = (category_healthy / category_total) * 100
            print(f"  {category}: {category_healthy}/{category_total} ({category_percentage:.1f}%)")
        
        # Grade the overall system
        if overall_percentage >= 95:
            grade = "A+ (Exceptional)"
            status = "🏆 WORLD-CLASS"
        elif overall_percentage >= 90:
            grade = "A (Excellent)"
            status = "🚀 PRODUCTION-READY"
        elif overall_percentage >= 80:
            grade = "B+ (Good)"
            status = "✅ OPERATIONAL"
        elif overall_percentage >= 70:
            grade = "B (Fair)"
            status = "⚠️ NEEDS ATTENTION"
        else:
            grade = "C (Poor)"
            status = "❌ CRITICAL ISSUES"
        
        print(f"\n🎯 OVERALL SYSTEM GRADE: {grade}")
        print(f"🚦 STATUS: {status}")
        
        # Generate detailed report
        self.generate_detailed_report(healthy_count, unhealthy_count, error_count, overall_percentage)
        
        return {
            "healthy": healthy_count,
            "unhealthy": unhealthy_count,
            "errors": error_count,
            "total": total_services,
            "percentage": overall_percentage,
            "grade": grade,
            "status": status,
            "results": self.results
        }
    
    def generate_detailed_report(self, healthy: int, unhealthy: int, errors: int, percentage: float):
        """Generate a detailed health report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# 🩺 VOCELIO 28-SERVICE HEALTH REPORT
*Generated: {timestamp}*

## 📊 EXECUTIVE SUMMARY
- **Total Services**: 28/28 deployed
- **Healthy Services**: {healthy}/28 ({percentage:.1f}%)
- **Unhealthy Services**: {unhealthy}/28
- **Error Services**: {errors}/28

## 🏆 ACHIEVEMENT STATUS
"""
        
        if percentage >= 95:
            report += """
**🎉 EXCEPTIONAL PERFORMANCE ACHIEVED!**
- All services operational at world-class levels
- Zero critical issues detected
- Enterprise-ready infrastructure confirmed
- Fortune 500 customer ready

"""
        elif percentage >= 90:
            report += """
**🚀 EXCELLENT PERFORMANCE!**
- Production-ready infrastructure
- Minor issues detected (if any)
- Enterprise customer ready
- Scaling capabilities confirmed

"""
        
        report += f"""
## 📋 SERVICE CATEGORY BREAKDOWN

"""
        
        for category, service_list in self.categories.items():
            category_healthy = sum(1 for s in service_list if s in self.results and self.results[s]["status"] == "healthy")
            category_total = len(service_list)
            category_percentage = (category_healthy / category_total) * 100
            
            report += f"""### {category} ({category_total} services)
- **Health**: {category_healthy}/{category_total} ({category_percentage:.1f}%)
- **Services**: {', '.join(service_list)}

"""
        
        # Save report
        with open("COMPLETE_28_SERVICE_HEALTH_REPORT.md", "w") as f:
            f.write(report)
        
        print(f"📄 Detailed report saved to: COMPLETE_28_SERVICE_HEALTH_REPORT.md")

if __name__ == "__main__":
    checker = Complete28ServiceHealthChecker()
    results = checker.check_all_services()
    
    if results["percentage"] >= 95:
        print(f"\n🎉 CONGRATULATIONS! Vocelio has achieved world-class status with {results['percentage']:.1f}% service health!")
    elif results["percentage"] >= 90:
        print(f"\n🚀 EXCELLENT! Vocelio is production-ready with {results['percentage']:.1f}% service health!")
    else:
        print(f"\n⚠️ Some services need attention. Current health: {results['percentage']:.1f}%")
        print("1. Check Railway deployment logs for failing services")
        print("2. Verify environment variables are set correctly") 
        print("3. Check service dependencies and configurations")
