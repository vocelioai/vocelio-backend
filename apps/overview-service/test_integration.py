#!/usr/bin/env python3
"""
🧪 Overview Service Integration Test
Test the Overview Service functionality and API Gateway integration
"""

import asyncio
import httpx
import websockets
import json
from datetime import datetime

# Test configuration
OVERVIEW_SERVICE_URL = "http://localhost:8001"
API_GATEWAY_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8001/ws/live"

async def test_service_health():
    """Test service health endpoint"""
    print("🏥 Testing service health...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OVERVIEW_SERVICE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Service Health: {data['status']}")
                print(f"📊 Uptime: {data['uptime']:.2f}%")
                print(f"🔧 Services: {data['services_online']}/{data['total_services']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_live_metrics():
    """Test live metrics endpoint"""
    print("\n📊 Testing live metrics...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OVERVIEW_SERVICE_URL}/metrics/live")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Live Metrics Retrieved")
                print(f"👥 Total Clients: {data['total_clients']:,}")
                print(f"📞 Active Calls: {data['active_calls']:,}")
                print(f"💰 Today's Revenue: ${data['revenue_today']:,.2f}")
                print(f"📈 Success Rate: {data['success_rate']:.1f}%")
                print(f"🤖 AI Score: {data['ai_optimization_score']:.1f}")
                print(f"⏰ System Uptime: {data['system_uptime']:.2f}%")
                return True
            else:
                print(f"❌ Live metrics failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Live metrics error: {e}")
        return False

async def test_ai_insights():
    """Test AI insights endpoint"""
    print("\n🧠 Testing AI insights...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OVERVIEW_SERVICE_URL}/insights/ai")
            if response.status_code == 200:
                insights = response.json()
                print(f"✅ AI Insights Retrieved: {len(insights)} insights")
                for insight in insights[:2]:  # Show first 2
                    print(f"  🎯 {insight['title']}")
                    print(f"     Confidence: {insight['confidence']:.1f}%")
                    print(f"     Impact: {insight['impact_estimate']}")
                return True
            else:
                print(f"❌ AI insights failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ AI insights error: {e}")
        return False

async def test_revenue_metrics():
    """Test revenue metrics endpoint"""
    print("\n💰 Testing revenue metrics...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OVERVIEW_SERVICE_URL}/metrics/revenue")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Revenue Metrics Retrieved")
                print(f"📅 Daily: ${data['daily_revenue']:,.2f}")
                print(f"📊 Monthly: ${data['monthly_revenue']:,.2f}")
                print(f"📈 Growth: {data['revenue_growth']:.1f}%")
                print(f"🏆 Top Source: {data['top_revenue_sources'][0]['source']}")
                return True
            else:
                print(f"❌ Revenue metrics failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Revenue metrics error: {e}")
        return False

async def test_websocket_connection():
    """Test WebSocket real-time updates"""
    print("\n📡 Testing WebSocket connection...")
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Wait for a few messages
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"📨 Received: {data['type']}")
                    
                    if data['type'] == 'live_metrics':
                        metrics = data['data']
                        print(f"  📊 Clients: {metrics['total_clients']:,}")
                        print(f"  📞 Calls: {metrics['active_calls']:,}")
                    
                except asyncio.TimeoutError:
                    print("⏰ WebSocket timeout - no messages received")
                    break
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

async def test_api_gateway_routing():
    """Test API Gateway routing to Overview Service"""
    print("\n🌉 Testing API Gateway routing...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test routing through API Gateway
            response = await client.get(f"{API_GATEWAY_URL}/api/v1/overview/health")
            if response.status_code == 200:
                print("✅ API Gateway routing successful")
                return True
            else:
                print(f"❌ API Gateway routing failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API Gateway routing error: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Vocelio Overview Service Integration Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Service Health", test_service_health),
        ("Live Metrics", test_live_metrics),
        ("AI Insights", test_ai_insights),
        ("Revenue Metrics", test_revenue_metrics),
        ("WebSocket Connection", test_websocket_connection),
        ("API Gateway Routing", test_api_gateway_routing),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 ALL TESTS PASSED! Overview Service is ready for production!")
    else:
        print("⚠️  Some tests failed. Check service configuration.")
    
    return passed == len(test_results)

if __name__ == "__main__":
    print("🌍 Vocelio.ai Overview Service Integration Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = asyncio.run(run_all_tests())
        exit_code = 0 if success else 1
        print(f"\n🏁 Test suite completed with exit code: {exit_code}")
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        exit(1)
