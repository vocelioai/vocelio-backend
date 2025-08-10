#!/usr/bin/env python3
import sys
import os
import asyncio
from pathlib import Path

# Add agent store to path
sys.path.append(str(Path(__file__).parent / "apps" / "agent-store" / "src"))

async def test_agent_store():
    try:
        from api.v1.endpoints.dashboard_integration import get_featured_agents_for_dashboard
        
        mock_user = {"user_id": "test_123"}
        result = await get_featured_agents_for_dashboard(6, mock_user)
        
        print(f"✅ Agent Store Integration: PASSED")
        print(f"   Featured agents: {len(result['featured_agents'])}")
        return True
    except Exception as e:
        print(f"❌ Agent Store Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏪 Testing Agent Store Dashboard Integration...")
    result = asyncio.run(test_agent_store())
    print(f"Result: {'PASSED' if result else 'FAILED'}")
