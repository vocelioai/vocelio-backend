"""
Test script for Call Center Service
"""
import httpx
import json

def test_call_center_service():
    print('Testing Call Center Service...')
    print('=' * 60)
    
    base_url = "http://127.0.0.1:8002"
    
    try:
        # Test health endpoint
        response = httpx.get(f'{base_url}/health')
        print(f'Health Check: {response.status_code}')
        print(json.dumps(response.json(), indent=2))
        print()

        # Test root endpoint  
        response = httpx.get(f'{base_url}/')
        print(f'Root Endpoint: {response.status_code}')
        root_data = response.json()
        print(f'Service: {root_data["service"]}')
        print(f'Status: {root_data["status"]}')
        print(f'Features: {len(root_data["features"])} features available')
        print()

        # Test listing calls (should be empty initially)
        response = httpx.get(f'{base_url}/calls')
        print(f'List Calls: {response.status_code}')
        calls = response.json()
        print(f'Initial calls: {len(calls)}')
        print()

        # Test initiating a call
        call_data = {
            'phone_number': '+1234567890',
            'message': 'This is a test call from Vocelio AI',
            'agent_id': 'test-agent-001'
        }

        response = httpx.post(f'{base_url}/calls', json=call_data)
        print(f'Initiate Call: {response.status_code}')
        if response.status_code == 200:
            call_response = response.json()
            call_id = call_response['call_id']
            print(f'Created call: {call_id}')
            print(f'Phone: {call_response["phone_number"]}')
            print(f'Status: {call_response["status"]}')
            print()
            
            # Test getting specific call status
            response = httpx.get(f'{base_url}/calls/{call_id}')
            print(f'Get Call Status: {response.status_code}')
            if response.status_code == 200:
                call_status = response.json()
                print(f'Call ID: {call_status["call_id"]}')
                print(f'Status: {call_status["status"]}')
            print()
            
            # Test completing the call
            response = httpx.post(f'{base_url}/calls/{call_id}/complete')
            print(f'Complete Call: {response.status_code}')
            if response.status_code == 200:
                complete_response = response.json()
                print(f'Completed: {complete_response["message"]}')
            print()
            
        else:
            print(f'Error creating call: {response.text}')

        # Test analytics endpoint
        response = httpx.get(f'{base_url}/analytics')
        print(f'Get Analytics: {response.status_code}')
        if response.status_code == 200:
            analytics = response.json()
            print(f'Total calls: {analytics["total_calls"]}')
            print(f'Active calls: {analytics["active_calls"]}')
            print(f'Status distribution: {analytics["status_distribution"]}')
        print()

        # Test voice webhook endpoint
        response = httpx.get(f'{base_url}/test-voice')
        print(f'Test Voice Endpoint: {response.status_code}')
        print(f'Response type: {response.headers.get("content-type")}')
        if 'xml' in response.headers.get("content-type", ""):
            print(f'TwiML Response: Valid XML returned')
        print()

    except Exception as e:
        print(f'Error testing service: {e}')

    print('✅ Call Center Service Testing Complete!')

if __name__ == "__main__":
    test_call_center_service()
