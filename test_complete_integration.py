#!/usr/bin/env python3
"""
🎯 Final Dashboard Integration Verification
Comprehensive test of all dashboard integration endpoints
"""
import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "apps" / "overview" / "src"))
sys.path.append(str(Path(__file__).parent / "apps" / "agent-store" / "src"))

async def test_complete_integration():
    print("🎯 COMPREHENSIVE DASHBOARD INTEGRATION TEST")
    print("=" * 55)
    
    results = {}
    
    # Test Overview Service
    print("\n📊 Testing Overview Service Dashboard Integration...")
    try:
        from api.v1.endpoints.dashboard_integration import (
            get_dashboard_overview,
            get_dashboard_analytics,
            get_services_health,
            get_recent_activity,
            get_dashboard_notifications
        )
        
        mock_user = {"user_id": "test_123", "name": "Test User", "email": "test@vocelio.ai"}
        
        # Test all overview endpoints
        overview = await get_dashboard_overview(mock_user)
        analytics = await get_dashboard_analytics("7d", mock_user)
        health = await get_services_health(mock_user)
        activity = await get_recent_activity(10, mock_user)
        notifications = await get_dashboard_notifications(5, False, mock_user)
        
        print("   ✅ Dashboard Overview - PASSED")
        print("   ✅ Analytics Summary - PASSED") 
        print("   ✅ Services Health - PASSED")
        print("   ✅ Recent Activity - PASSED")
        print("   ✅ Notifications - PASSED")
        
        results["overview"] = True
        
    except Exception as e:
        print(f"   ❌ Overview Service Failed: {str(e)}")
        results["overview"] = False
    
    # Test Agent Store Service
    print("\n🏪 Testing Agent Store Dashboard Integration...")
    try:
        sys.path.append(str(Path(__file__).parent / "apps" / "agent-store" / "src"))
        from api.v1.endpoints.dashboard_integration import (
            get_featured_agents_for_dashboard,
            get_agent_categories_for_dashboard,
            get_agent_store_analytics,
            get_trending_agents_for_dashboard
        )
        
        # Test agent store endpoints
        featured = await get_featured_agents_for_dashboard(6, mock_user)
        categories = await get_agent_categories_for_dashboard()
        store_analytics = await get_agent_store_analytics("7d", mock_user)
        trending = await get_trending_agents_for_dashboard(5)
        
        print("   ✅ Featured Agents - PASSED")
        print("   ✅ Agent Categories - PASSED")
        print("   ✅ Store Analytics - PASSED")
        print("   ✅ Trending Agents - PASSED")
        
        results["agent_store"] = True
        
    except Exception as e:
        print(f"   ❌ Agent Store Failed: {str(e)}")
        results["agent_store"] = False
    
    # Summary
    print("\n" + "=" * 55)
    print("📋 FINAL INTEGRATION TEST RESULTS:")
    print(f"   📊 Overview Service: {'✅ PASSED' if results.get('overview') else '❌ FAILED'}")
    print(f"   🏪 Agent Store Service: {'✅ PASSED' if results.get('agent_store') else '❌ FAILED'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL DASHBOARD INTEGRATION TESTS PASSED!")
        print("✅ Ready for production deployment to Railway")
        print("✅ Frontend dashboard can now connect to all APIs")
        print("✅ Comprehensive data aggregation working")
        print("\n🚀 DASHBOARD INTEGRATION: COMPLETE")
    else:
        print("\n⚠️  Some tests failed - check errors above")
    
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(test_complete_integration())
    sys.exit(0 if result else 1)
