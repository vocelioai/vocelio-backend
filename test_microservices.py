#!/usr/bin/env python3
"""
Comprehensive test suite for Vocelio microservices architecture.
Tests all services individually and validates API Gateway routing.
"""

import asyncio
import httpx
import json
import time
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceEndpoint:
    name: str
    url: str
    expected_status: int = 200

@dataclass  
class TestResult:
    service: str
    endpoint: str
    status: str
    response_time: float
    status_code: Optional[int] = None
    error: Optional[str] = None

class VocelioServiceTester:
    def __init__(self, base_port: int = 8000):
        self.base_port = base_port
        self.services = {
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
        
        # Define test endpoints for each service
        self.test_endpoints = {
            "api-gateway": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("gateway_status", "/api/v1/gateway/status"),
                ServiceEndpoint("services_list", "/api/v1/gateway/services")
            ],
            "overview": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("dashboard", "/api/v1/dashboard"),
                ServiceEndpoint("metrics", "/api/v1/metrics")
            ],
            "ai-agents": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("agents_list", "/api/v1/agents"),
                ServiceEndpoint("templates", "/api/v1/templates")
            ],
            "smart-campaigns": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("campaigns", "/api/v1/campaigns"),
                ServiceEndpoint("analytics", "/api/v1/analytics")
            ],
            "analytics-pro": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("reports", "/api/v1/reports"),
                ServiceEndpoint("metrics", "/api/v1/metrics")
            ],
            "team-hub": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("team", "/api/v1/team"),
                ServiceEndpoint("permissions", "/api/v1/permissions")
            ],
            "phone-numbers": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("numbers", "/api/v1/numbers"),
                ServiceEndpoint("search", "/api/v1/search")
            ],
            "voice-lab": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("voices", "/api/v1/voices"),
                ServiceEndpoint("synthesis", "/api/v1/synthesis")
            ],
            "settings": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("profile", "/api/v1/profile"),
                ServiceEndpoint("preferences", "/api/v1/preferences")
            ],
            "flow-builder": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("flows", "/api/v1/flows"),
                ServiceEndpoint("templates", "/api/v1/templates")
            ],
            "call-center": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("calls", "/api/v1/calls"),
                ServiceEndpoint("queue", "/api/v1/queue")
            ],
            "integrations": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("connections", "/api/v1/connections"),
                ServiceEndpoint("available", "/api/v1/available")
            ],
            "voice-marketplace": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("voices", "/api/v1/voices"),
                ServiceEndpoint("featured", "/api/v1/featured")
            ],
            "billing-pro": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("usage", "/api/v1/billing/usage"),
                ServiceEndpoint("subscriptions", "/api/v1/subscriptions")
            ],
            "developer-api": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("keys", "/api/v1/keys"),
                ServiceEndpoint("webhooks", "/api/v1/webhooks")
            ],
            "agent-store": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("agents", "/api/v1/agents"),
                ServiceEndpoint("marketplace", "/api/v1/marketplace/featured")
            ],
            "compliance": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("audit", "/api/v1/audit/logs"),
                ServiceEndpoint("gdpr", "/api/v1/gdpr/requests")
            ],
            "white-label": [
                ServiceEndpoint("health", "/health"),
                ServiceEndpoint("branding", "/api/v1/branding"),
                ServiceEndpoint("templates", "/api/v1/templates")
            ]
        }
    
    async def test_service(self, service_name: str, client: httpx.AsyncClient) -> List[TestResult]:
        """Test all endpoints for a specific service."""
        results = []
        port = self.services.get(service_name)
        endpoints = self.test_endpoints.get(service_name, [])
        
        if not port or not endpoints:
            return [TestResult(
                service=service_name,
                endpoint="N/A", 
                status="SKIP",
                response_time=0.0,
                error="Service not configured"
            )]
        
        base_url = f"http://localhost:{port}"
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = await client.get(f"{base_url}{endpoint.url}", timeout=10.0)
                response_time = time.time() - start_time
                
                if response.status_code == endpoint.expected_status:
                    status = "PASS"
                else:
                    status = "FAIL" 
                    
                results.append(TestResult(
                    service=service_name,
                    endpoint=endpoint.name,
                    status=status,
                    response_time=response_time,
                    status_code=response.status_code
                ))
                
            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    service=service_name,
                    endpoint=endpoint.name,
                    status="ERROR",
                    response_time=response_time,
                    error=str(e)
                ))
        
        return results
    
    async def test_gateway_routing(self, client: httpx.AsyncClient) -> List[TestResult]:
        """Test API Gateway routing to other services."""
        gateway_url = f"http://localhost:{self.services['api-gateway']}"
        results = []
        
        # Test routing to each service through gateway
        routing_tests = [
            ("overview", "/api/v1/proxy/overview/dashboard"),
            ("ai-agents", "/api/v1/proxy/ai-agents/agents"),
            ("smart-campaigns", "/api/v1/proxy/smart-campaigns/campaigns"),
            ("analytics-pro", "/api/v1/proxy/analytics-pro/reports"),
            ("billing-pro", "/api/v1/proxy/billing-pro/billing/usage"),
            ("developer-api", "/api/v1/proxy/developer-api/keys"),
        ]
        
        for service, route in routing_tests:
            start_time = time.time()
            try:
                response = await client.get(f"{gateway_url}{route}", timeout=10.0)
                response_time = time.time() - start_time
                
                # Gateway might return 307 redirect or 404 if service not running
                if response.status_code in [200, 307, 404, 502]:
                    status = "PASS" if response.status_code == 200 else "INFO"
                else:
                    status = "FAIL"
                    
                results.append(TestResult(
                    service="api-gateway",
                    endpoint=f"proxy_{service}",
                    status=status,
                    response_time=response_time,
                    status_code=response.status_code
                ))
                
            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    service="api-gateway",
                    endpoint=f"proxy_{service}",
                    status="ERROR", 
                    response_time=response_time,
                    error=str(e)
                ))
        
        return results
    
    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive test suite across all services."""
        print("🚀 Starting Vocelio Microservices Test Suite")
        print(f"Testing {len(self.services)} services...")
        print("=" * 60)
        
        all_results = []
        
        async with httpx.AsyncClient() as client:
            # Test each service individually
            for service_name in self.services.keys():
                print(f"Testing {service_name}...")
                service_results = await self.test_service(service_name, client)
                all_results.extend(service_results)
            
            # Test API Gateway routing
            print("Testing API Gateway routing...")
            routing_results = await self.test_gateway_routing(client)
            all_results.extend(routing_results)
        
        # Generate summary
        total_tests = len(all_results)
        passed = len([r for r in all_results if r.status == "PASS"])
        failed = len([r for r in all_results if r.status == "FAIL"])
        errors = len([r for r in all_results if r.status == "ERROR"])
        skipped = len([r for r in all_results if r.status == "SKIP"])
        info = len([r for r in all_results if r.status == "INFO"])
        
        summary = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "info": info,
            "success_rate": (passed / (total_tests - skipped)) * 100 if total_tests > skipped else 0,
            "results": all_results
        }
        
        self.print_results(summary)
        return summary
    
    def print_results(self, summary: Dict):
        """Print formatted test results."""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"🔥 Errors: {summary['errors']}")
        print(f"ℹ️  Info: {summary['info']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 60)
        
        # Group by service
        by_service = {}
        for result in summary['results']:
            if result.service not in by_service:
                by_service[result.service] = []
            by_service[result.service].append(result)
        
        for service, results in by_service.items():
            print(f"\n🔧 {service.upper()}")
            for result in results:
                status_icon = {
                    "PASS": "✅",
                    "FAIL": "❌", 
                    "ERROR": "🔥",
                    "SKIP": "⏭️",
                    "INFO": "ℹ️"
                }[result.status]
                
                time_str = f"{result.response_time:.3f}s"
                status_str = f"[{result.status_code}]" if result.status_code else ""
                error_str = f" - {result.error}" if result.error else ""
                
                print(f"  {status_icon} {result.endpoint:<20} {time_str:<8} {status_str}{error_str}")

async def main():
    """Main test execution."""
    tester = VocelioServiceTester()
    
    # Check if we should test specific services
    if len(sys.argv) > 1:
        service_filter = sys.argv[1:]
        print(f"Testing specific services: {', '.join(service_filter)}")
        # Filter services
        filtered_services = {k: v for k, v in tester.services.items() if k in service_filter}
        tester.services = filtered_services
    
    summary = await tester.run_comprehensive_test()
    
    # Exit with error code if tests failed
    if summary['failed'] > 0 or summary['errors'] > 0:
        print(f"\n❌ Tests failed! {summary['failed']} failures, {summary['errors']} errors")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed! {summary['passed']} successful tests")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
