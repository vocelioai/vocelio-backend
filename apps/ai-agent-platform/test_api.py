"""
Test script for AI Agent Platform API
"""
import httpx
import json

def test_ai_agent_platform():
    print('Testing AI Agent Platform API...')
    print('=' * 50)

    try:
        # Test health endpoint
        response = httpx.get('http://127.0.0.1:8000/health')
        print(f'Health Check: {response.status_code}')
        print(json.dumps(response.json(), indent=2))
        print()

        # Test root endpoint  
        response = httpx.get('http://127.0.0.1:8000/')
        print(f'Root Endpoint: {response.status_code}')
        print(json.dumps(response.json(), indent=2))
        print()

        # Test listing agents (should be empty initially)
        response = httpx.get('http://127.0.0.1:8000/agents')
        print(f'List Agents: {response.status_code}')
        print(f'Initial agents: {len(response.json())}')
        print()

        # Test creating an agent
        agent_data = {
            'name': 'Test Voice Agent',
            'description': 'A test agent for voice interactions',
            'agent_type': 'voice',
            'capabilities': [
                {'name': 'voice_recognition', 'description': 'Can understand speech', 'enabled': True},
                {'name': 'text_to_speech', 'description': 'Can generate speech', 'enabled': True}
            ],
            'tags': ['voice', 'ai', 'test'],
            'is_public': True,
            'category': 'voice'
        }

        response = httpx.post('http://127.0.0.1:8000/agents', json=agent_data)
        print(f'Create Agent: {response.status_code}')
        if response.status_code == 200:
            agent = response.json()
            agent_id = agent['id']
            print(f'Created agent: {agent["name"]} (ID: {agent_id})')
            print()
            
            # Test getting the specific agent
            response = httpx.get(f'http://127.0.0.1:8000/agents/{agent_id}')
            print(f'Get Agent: {response.status_code}')
            if response.status_code == 200:
                print(f'Retrieved agent: {response.json()["name"]}')
            print()
            
            # Test marketplace endpoints
            response = httpx.get('http://127.0.0.1:8000/marketplace')
            print(f'Get Marketplace: {response.status_code}')
            print(f'Marketplace agents: {len(response.json())}')
            print()
            
            # Test analytics endpoints
            response = httpx.get('http://127.0.0.1:8000/analytics/usage')
            print(f'Get Usage Analytics: {response.status_code}')
            analytics = response.json()
            print(f'Total agents in analytics: {analytics["total_agents"]}')
            
        else:
            print(f'Error creating agent: {response.text}')

    except Exception as e:
        print(f'Error testing API: {e}')

    print()
    print('✅ API Testing Complete!')

if __name__ == "__main__":
    test_ai_agent_platform()
