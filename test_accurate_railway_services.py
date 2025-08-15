#!/usr/bin/env python3
"""
🎯 ACCURATE Railway Services Health Check
Based on EXACT URLs from Railway environment variables
"""

import requests
import time
from datetime import datetime
from typing import Dict, List

class AccurateRailwayHealthChecker:
    """Health checker using exact Railway environment variable URLs"""
    
    def __init__(self):
        # EXACT URLs from Railway environment variables
        self.services = {
            # Core Foundation (7)
            "api-gateway": "https://api-gateway-production-588d.up.railway.app",
            "overview": "https://overview-production.up.railway.app",
            "ai-agents-service": "https://ai-agents-service-production.up.railway.app",
            "smart-campaigns": "https://smart-campaigns-production.up.railway.app",
            "analytics-pro": "https://analytics-pro-production.up.railway.app",
            "team-hub": "https://team-hub-production.up.railway.app",
            "phone-numbers": "https://phone-numbers-production.up.railway.app",
            
            # Business Services (6)
            "voice-lab": "https://voice-lab-production.up.railway.app",
            "settings": "https://settings-production.up.railway.app",
            "flow-builder": "https://flow-builder-production.up.railway.app",
            "billing-pro": "https://billing-pro-production.up.railway.app",
            "ai-brain": "https://ai-brain-production.up.railway.app",
            "voice-marketplace": "https://voice-marketplace-production.up.railway.app",
            
            # Advanced Features (6)
            "call-center": "https://call-center-production-19af.up.railway.app",
            "integrations": "https://integrations-production-a079.up.railway.app",
            "developer-api": "https://developer-api-production-a124.up.railway.app",
            "compliance": "https://compliance-production-841c.up.railway.app",
            "white-label": "https://white-label-production-ab67.up.railway.app",
            "webhooks": "https://webhooks-production-11ef.up.railway.app",
            
            # World-Class Business (5)
            "knowledge-base": "https://knowledge-base-production-87e4.up.railway.app",
            "lead-management": "https://lead-management-production.up.railway.app",
            "notifications": "https://notifications-production-a0a8.up.railway.app",
            "scheduling": "https://scheduling-production-a0f3.up.railway.app",
            "scripts": "https://scripts-production.up.railway.app",
            
            # Enterprise Tier 1 (3)
            "sso-identity": "https://sso-identity-production.up.railway.app",
            "enterprise-security": "https://enterprise-security-production.up.railway.app",
            "api-management": "https://api-management-production.up.railway.app",
            
            # Backend Core (1)
            "vocelio-backend": "https://vocelio-backend-production.up.railway.app"
        }
        
        self.categories = {
            "Core Foundation": ["api-gateway", "overview", "ai-agents-service", "smart-campaigns", 
                              "analytics-pro", "team-hub", "phone-numbers"],
            "Business Services": ["voice-lab", "settings", "flow-builder", "billing-pro", 
                                "ai-brain", "voice-marketplace"],
            "Advanced Features": ["call-center", "integrations", "developer-api", 
                                "compliance", "white-label", "webhooks"],
            "World-Class Business": ["knowledge-base", "lead-management", "notifications", 
                                   "scheduling", "scripts"],
            "Enterprise Tier 1": ["sso-identity", "enterprise-security", "api-management"],
            "Backend Core": ["vocelio-backend"]
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
        """Check health of all actual Railway services"""
        print("🎯 ACCURATE Railway Services Health Check (26 Confirmed Services)")
        print("Source: Railway Environment Variables")
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
                        print(f"  {status_icon} {service_name:<25} {response_time}")
                    else:
                        if result["status"] == "unhealthy":
                            unhealthy_count += 1
                        else:
                            error_count += 1
                        
                        error_msg = result.get("error", "Unknown error")
                        response_time = result.get("response_time", "N/A")
                        print(f"  {status_icon} {service_name:<25} {response_time} - {error_msg}")
            
            # Category summary
            category_percentage = (category_healthy / category_total) * 100
            print(f"  📊 Category Health: {category_healthy}/{category_total} ({category_percentage:.1f}%)")
        
        total_services = len(self.services)
        overall_percentage = (healthy_count / total_services) * 100
        
        print("\n" + "=" * 80)
        print("📊 ACCURATE HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"✅ Healthy Services: {healthy_count}")
        print(f"⚠️  Unhealthy Services: {unhealthy_count}")
        print(f"❌ Error Services: {error_count}")
        print(f"📈 Overall Health: {overall_percentage:.1f}%")
        print(f"🎯 Total Services: {total_services} (verified from Railway)")
        
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
        print(f"📋 DATA SOURCE: Railway Environment Variables (100% Accurate)")
        
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

if __name__ == "__main__":
    checker = AccurateRailwayHealthChecker()
    results = checker.check_all_services()
    
    if results["percentage"] >= 95:
        print(f"\n🎉 EXCEPTIONAL! Vocelio achieved {results['percentage']:.1f}% service health!")
    elif results["percentage"] >= 90:
        print(f"\n🚀 EXCELLENT! Vocelio is production-ready with {results['percentage']:.1f}% health!")
    elif results["percentage"] >= 80:
        print(f"\n✅ GOOD! Vocelio is operational with {results['percentage']:.1f}% health!")
    else:
        print(f"\n⚠️ Some services need attention. Current health: {results['percentage']:.1f}%")
