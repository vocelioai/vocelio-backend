#!/usr/bin/env python3
"""
Dashboard Integration Test Script
Tests the new dashboard endpoints
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "apps" / "overview" / "src"))

async def test_dashboard_integration():
    """Test the dashboard integration endpoints"""
    print("🚀 Testing Dashboard Integration Endpoints...")
    
    try:
        # Import dashboard integration module
        from api.v1.endpoints.dashboard_integration import (
            get_dashboard_overview,
            get_dashboard_analytics,
            get_services_health
        )
        
        # Mock user for testing
        mock_user = {
            'user_id': 'test_123',
            'name': 'Test User', 
            'email': 'test@vocelio.ai',
            'plan': 'Pro',
            'access_token': 'mock_token'
        }
        
        print("\n1️⃣ Testing Dashboard Overview...")
        overview = await get_dashboard_overview(mock_user)
        assert 'user_info' in overview
        assert 'quick_stats' in overview
        assert 'recent_activity' in overview
        assert 'performance_metrics' in overview
        assert 'system_status' in overview
        print("   ✅ Dashboard Overview: PASSED")
        
        print("\n2️⃣ Testing Dashboard Analytics...")
        analytics = await get_dashboard_analytics("7d", mock_user)
        assert 'time_range' in analytics
        assert 'call_volume' in analytics
        assert 'performance_metrics' in analytics
        assert 'revenue_metrics' in analytics
        print("   ✅ Dashboard Analytics: PASSED")
        
        print("\n3️⃣ Testing Services Health...")
        health = await get_services_health(mock_user)
        assert 'system_health' in health
        assert 'services' in health
        assert 'summary' in health
        print("   ✅ Services Health: PASSED")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test Failed: {str(e)}")
        return False

async def test_agent_store_integration():
    """Test the agent store dashboard integration"""
    print("\n🏪 Testing Agent Store Dashboard Integration...")
    
    try:
        # Add agent store to path
        sys.path.append(str(Path(__file__).parent / "apps" / "agent-store" / "src"))
        
        from api.v1.endpoints.dashboard_integration import (
            get_featured_agents_for_dashboard,
            get_agent_categories_for_dashboard,
            get_agent_store_analytics
        )
        
        mock_user = {'user_id': 'test_123', 'name': 'Test User'}
        
        print("\n1️⃣ Testing Featured Agents...")
        featured = await get_featured_agents_for_dashboard(6, mock_user)
        assert 'featured_agents' in featured
        assert 'metadata' in featured
        print("   ✅ Featured Agents: PASSED")
        
        print("\n2️⃣ Testing Agent Categories...")
        categories = await get_agent_categories_for_dashboard()
        assert 'categories' in categories
        assert 'summary' in categories
        print("   ✅ Agent Categories: PASSED")
        
        print("\n3️⃣ Testing Agent Store Analytics...")
        analytics = await get_agent_store_analytics("7d", mock_user)
        assert 'overview' in analytics
        assert 'performance' in analytics
        print("   ✅ Agent Store Analytics: PASSED")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent Store Test Failed: {str(e)}")
        return False

async def main():
    """Run all dashboard integration tests"""
    print("🎯 DASHBOARD INTEGRATION TEST SUITE")
    print("=" * 50)
    
    # Test overview service integration
    overview_result = await test_dashboard_integration()
    
    # Test agent store integration
    agent_store_result = await test_agent_store_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"   Overview Service: {'✅ PASSED' if overview_result else '❌ FAILED'}")
    print(f"   Agent Store Service: {'✅ PASSED' if agent_store_result else '❌ FAILED'}")
    
    if overview_result and agent_store_result:
        print("\n🎉 ALL DASHBOARD INTEGRATION TESTS PASSED!")
        print("✅ Ready for production deployment")
    else:
        print("\n⚠️  Some tests failed - review errors above")
    
    return overview_result and agent_store_result

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
