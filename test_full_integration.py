#!/usr/bin/env python3
"""
🧪 Vocelio.ai Services Integration Test Suite
Comprehensive testing for all Vocelio services

Services tested:
- Overview Service (Port 8001)
- AI Agents Service (Port 8002)  
- Smart Campaigns Service (Port 8003)
- API Gateway routing and integration
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List, Any

# Test configuration
SERVICES = {
    "overview": "http://localhost:8001",
    "ai-agents": "http://localhost:8002", 
    "smart-campaigns": "http://localhost:8003",
    "api-gateway": "http://localhost:8000"
}

class VocelioIntegrationTestSuite:
    def __init__(self):
        self.test_results = []
        self.test_data = {}
    
    async def log_test(self, service: str, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "service": service,
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} [{service}] {test_name}")
        if details:
            print(f"    {details}")
    
    async def test_service_health(self, service_name: str, url: str):
        """Test service health endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Status: {data.get('status', 'unknown')}"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test(service_name, "Health Check", success, details)
                return success
                
        except Exception as e:
            await self.log_test(service_name, "Health Check", False, str(e))
            return False
    
    async def test_overview_service(self):
        """Test Overview Service functionality"""
        service_url = SERVICES["overview"]
        
        # Health check
        await self.test_service_health("Overview", service_url)
        
        # Test live metrics
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/api/v1/metrics/live")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Clients: {data.get('total_clients', 0):,}, Uptime: {data.get('system_uptime', 0):.2f}%"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("Overview", "Live Metrics", success, details)
                
        except Exception as e:
            await self.log_test("Overview", "Live Metrics", False, str(e))
        
        # Test AI insights
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/api/v1/ai/insights")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Insights: {len(data)} recommendations"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("Overview", "AI Insights", success, details)
                
        except Exception as e:
            await self.log_test("Overview", "AI Insights", False, str(e))
        
        # Test revenue metrics
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/api/v1/revenue/metrics")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Monthly Revenue: ${data.get('monthly_revenue', 0):,.2f}"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("Overview", "Revenue Metrics", success, details)
                
        except Exception as e:
            await self.log_test("Overview", "Revenue Metrics", False, str(e))
    
    async def test_ai_agents_service(self):
        """Test AI Agents Service functionality"""
        service_url = SERVICES["ai-agents"]
        
        # Health check
        await self.test_service_health("AI Agents", service_url)
        
        # Test get all agents
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/api/v1/agents")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Agents: {len(data)} active"
                    self.test_data["agents"] = data[:1] if data else []  # Store first agent for later tests
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("AI Agents", "Get All Agents", success, details)
                
        except Exception as e:
            await self.log_test("AI Agents", "Get All Agents", False, str(e))
        
        # Test create agent
        try:
            async with httpx.AsyncClient() as client:
                new_agent = {
                    "name": "Test Agent Integration",
                    "description": "Integration test agent",
                    "industry": "technology",
                    "voice_type": "confident_mike"
                }
                
                response = await client.post(f"{service_url}/api/v1/agents", json=new_agent)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    self.test_data["created_agent_id"] = data.get("id")
                    details = f"Created agent: {data.get('name')} ({data.get('id')[:8]}...)"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("AI Agents", "Create Agent", success, details)
                
        except Exception as e:
            await self.log_test("AI Agents", "Create Agent", False, str(e))
        
        # Test agent performance (if we have an agent)
        if self.test_data.get("agents"):
            try:
                agent_id = self.test_data["agents"][0]["id"]
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{service_url}/agents/{agent_id}/performance")
                    success = response.status_code == 200
                    
                    if success:
                        data = response.json()
                        details = f"Performance: {data.get('success_rate', 0):.1f}% success rate"
                    else:
                        details = f"HTTP {response.status_code}"
                    
                    await self.log_test("AI Agents", "Agent Performance", success, details)
                    
            except Exception as e:
                await self.log_test("AI Agents", "Agent Performance", False, str(e))
        
        # Test analytics
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/api/v1/agents/analytics")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Analytics: {data.get('total_agents', 0)} total, {data.get('active_agents', 0)} active"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("AI Agents", "Analytics", success, details)
                
        except Exception as e:
            await self.log_test("AI Agents", "Analytics", False, str(e))
    
    async def test_smart_campaigns_service(self):
        """Test Smart Campaigns Service functionality"""
        service_url = SERVICES["smart-campaigns"]
        
        # Health check
        await self.test_service_health("Smart Campaigns", service_url)
        
        # Test get all campaigns
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/api/v1/campaigns")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Campaigns: {len(data)} found"
                    self.test_data["campaigns"] = data[:1] if data else []  # Store first campaign
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("Smart Campaigns", "Get All Campaigns", success, details)
                
        except Exception as e:
            await self.log_test("Smart Campaigns", "Get All Campaigns", False, str(e))
        
        # Test create campaign
        try:
            async with httpx.AsyncClient() as client:
                new_campaign = {
                    "name": "Integration Test Campaign",
                    "description": "Test campaign for integration testing",
                    "campaign_type": "outbound_calls",
                    "industry": "technology",
                    "optimization_goal": "maximize_revenue",
                    "target_audience_size": 10000,
                    "daily_call_limit": 500
                }
                
                response = await client.post(f"{service_url}/api/v1/campaigns", json=new_campaign)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    self.test_data["created_campaign_id"] = data.get("id")
                    details = f"Created: {data.get('name')} ({data.get('id')[:8]}...)"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("Smart Campaigns", "Create Campaign", success, details)
                
        except Exception as e:
            await self.log_test("Smart Campaigns", "Create Campaign", False, str(e))
        
        # Test campaign performance (if we have a campaign)
        if self.test_data.get("campaigns"):
            try:
                campaign_id = self.test_data["campaigns"][0]["id"]
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{service_url}/campaigns/{campaign_id}/performance")
                    success = response.status_code == 200
                    
                    if success:
                        data = response.json()
                        details = f"Performance: {data.get('conversion_rate', 0):.1f}% conversion"
                    else:
                        details = f"HTTP {response.status_code}"
                    
                    await self.log_test("Smart Campaigns", "Campaign Performance", success, details)
                    
            except Exception as e:
                await self.log_test("Smart Campaigns", "Campaign Performance", False, str(e))
        
        # Test campaign optimization
        if self.test_data.get("campaigns"):
            try:
                campaign_id = self.test_data["campaigns"][0]["id"]
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{service_url}/campaigns/{campaign_id}/optimize")
                    success = response.status_code == 200
                    
                    if success:
                        data = response.json()
                        improvement = data.get("improvements", {}).get("conversion_rate_improvement", 0)
                        details = f"Optimization: +{improvement:.1f}% conversion improvement"
                    else:
                        details = f"HTTP {response.status_code}"
                    
                    await self.log_test("Smart Campaigns", "Campaign Optimization", success, details)
                    
            except Exception as e:
                await self.log_test("Smart Campaigns", "Campaign Optimization", False, str(e))
        
        # Test analytics
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/api/v1/campaigns/analytics")
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    details = f"Analytics: {data.get('total_campaigns', 0)} total, ${data.get('total_revenue', 0):,.0f} revenue"
                else:
                    details = f"HTTP {response.status_code}"
                
                await self.log_test("Smart Campaigns", "Analytics", success, details)
                
        except Exception as e:
            await self.log_test("Smart Campaigns", "Analytics", False, str(e))
    
    async def test_api_gateway_routing(self):
        """Test API Gateway routing to all services"""
        gateway_url = SERVICES["api-gateway"]
        
        # Test routing to overview service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{gateway_url}/api/v1/overview/health")
                success = response.status_code == 200
                details = "Overview service routing" if success else f"HTTP {response.status_code}"
                await self.log_test("API Gateway", "Overview Routing", success, details)
                
        except Exception as e:
            await self.log_test("API Gateway", "Overview Routing", False, str(e))
        
        # Test routing to AI agents service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{gateway_url}/api/v1/ai-agents/health")
                success = response.status_code == 200
                details = "AI Agents service routing" if success else f"HTTP {response.status_code}"
                await self.log_test("API Gateway", "AI Agents Routing", success, details)
                
        except Exception as e:
            await self.log_test("API Gateway", "AI Agents Routing", False, str(e))
        
        # Test routing to smart campaigns service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{gateway_url}/api/v1/smart-campaigns/health")
                success = response.status_code == 200
                details = "Smart Campaigns service routing" if success else f"HTTP {response.status_code}"
                await self.log_test("API Gateway", "Smart Campaigns Routing", success, details)
                
        except Exception as e:
            await self.log_test("API Gateway", "Smart Campaigns Routing", False, str(e))
    
    async def test_cross_service_integration(self):
        """Test integration between services"""
        
        # Test: Create campaign with AI agent
        if self.test_data.get("created_agent_id") and self.test_data.get("created_campaign_id"):
            try:
                service_url = SERVICES["smart-campaigns"]
                campaign_id = self.test_data["created_campaign_id"]
                agent_id = self.test_data["created_agent_id"]
                
                async with httpx.AsyncClient() as client:
                    update_data = {
                        "ai_agent_ids": [agent_id]
                    }
                    response = await client.put(f"{service_url}/campaigns/{campaign_id}", json=update_data)
                    success = response.status_code == 200
                    
                    if success:
                        details = f"Assigned agent {agent_id[:8]}... to campaign {campaign_id[:8]}..."
                    else:
                        details = f"HTTP {response.status_code}"
                    
                    await self.log_test("Integration", "Agent-Campaign Assignment", success, details)
                    
            except Exception as e:
                await self.log_test("Integration", "Agent-Campaign Assignment", False, str(e))
    
    async def cleanup_test_data(self):
        """Clean up test data created during tests"""
        
        # Delete test agent
        if self.test_data.get("created_agent_id"):
            try:
                service_url = SERVICES["ai-agents"]
                agent_id = self.test_data["created_agent_id"]
                
                async with httpx.AsyncClient() as client:
                    response = await client.delete(f"{service_url}/agents/{agent_id}")
                    success = response.status_code == 200
                    details = f"Deleted agent {agent_id[:8]}..." if success else f"HTTP {response.status_code}"
                    await self.log_test("Cleanup", "Delete Test Agent", success, details)
                    
            except Exception as e:
                await self.log_test("Cleanup", "Delete Test Agent", False, str(e))
        
        # Delete test campaign
        if self.test_data.get("created_campaign_id"):
            try:
                service_url = SERVICES["smart-campaigns"]
                campaign_id = self.test_data["created_campaign_id"]
                
                async with httpx.AsyncClient() as client:
                    response = await client.delete(f"{service_url}/campaigns/{campaign_id}")
                    success = response.status_code == 200
                    details = f"Deleted campaign {campaign_id[:8]}..." if success else f"HTTP {response.status_code}"
                    await self.log_test("Cleanup", "Delete Test Campaign", success, details)
                    
            except Exception as e:
                await self.log_test("Cleanup", "Delete Test Campaign", False, str(e))
    
    async def run_all_tests(self):
        """Run complete integration test suite"""
        print("🚀 Starting Vocelio.ai Integration Test Suite")
        print("=" * 80)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test individual services
        print("📊 Testing Individual Services")
        print("-" * 40)
        await self.test_overview_service()
        print()
        
        await self.test_ai_agents_service()
        print()
        
        await self.test_smart_campaigns_service()
        print()
        
        # Test API Gateway
        print("🌉 Testing API Gateway")
        print("-" * 40)
        await self.test_api_gateway_routing()
        print()
        
        # Test cross-service integration
        print("🔗 Testing Cross-Service Integration")
        print("-" * 40)
        await self.test_cross_service_integration()
        print()
        
        # Cleanup
        print("🧹 Cleaning Up Test Data")
        print("-" * 40)
        await self.cleanup_test_data()
        print()
        
        # Generate summary
        await self.generate_summary()
    
    async def generate_summary(self):
        """Generate test summary report"""
        print("=" * 80)
        print("📋 INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        # Group results by service
        service_results = {}
        for result in self.test_results:
            service = result["service"]
            if service not in service_results:
                service_results[service] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                service_results[service]["passed"] += 1
            else:
                service_results[service]["failed"] += 1
            
            service_results[service]["tests"].append(result)
        
        # Print service-by-service results
        total_passed = 0
        total_tests = 0
        
        for service, results in service_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            
            total_passed += passed
            total_tests += total
            
            success_rate = (passed / total * 100) if total > 0 else 0
            status_icon = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
            
            print(f"{status_icon} {service}: {passed}/{total} passed ({success_rate:.1f}%)")
            
            # Show failed tests
            for test in results["tests"]:
                if not test["success"]:
                    print(f"    ❌ {test['test']}: {test['details']}")
        
        print()
        print("-" * 80)
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        if total_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Vocelio.ai services are ready for production!")
            print(f"✅ {total_passed}/{total_tests} tests passed (100%)")
        elif overall_success_rate >= 80:
            print("✅ Most tests passed! Services are mostly operational.")
            print(f"⚠️  {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
        else:
            print("❌ Multiple test failures detected. Check service configurations.")
            print(f"❌ {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return total_passed == total_tests

async def main():
    """Main test runner"""
    test_suite = VocelioIntegrationTestSuite()
    
    try:
        success = await test_suite.run_all_tests()
        exit_code = 0 if success else 1
        print(f"\n🏁 Test suite completed with exit code: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        return 1

if __name__ == "__main__":
    print("🌍 Vocelio.ai Services Integration Test Suite")
    print("Testing: Overview, AI Agents, Smart Campaigns, API Gateway")
    exit_code = asyncio.run(main())
    exit(exit_code)
