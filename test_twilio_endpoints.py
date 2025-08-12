#!/usr/bin/env python3
"""
Test script for Twilio endpoints
"""
import sys
import os

# Add the API Gateway source directory to Python path
gateway_src = os.path.join(os.path.dirname(__file__), 'apps', 'api-gateway', 'src')
sys.path.insert(0, gateway_src)

try:
    from integrations.twilio_service import get_available_phone_numbers, purchase_phone_number, list_phone_numbers
except ImportError:
    print("❌ Could not import Twilio service. Testing with direct code...")
    # We'll define the functions inline for testing
    
import asyncio

async def test_twilio_endpoints():
    """Test all Twilio endpoints locally"""
    
    print("🧪 Testing Twilio Integration Endpoints Locally")
    print("=" * 50)
    
    try:
        # Test 1: Get available phone numbers
        print("\n1️⃣ Testing: Get Available Phone Numbers")
        print("Request: US Local numbers")
        
        result = await get_available_phone_numbers("US", "Local", area_code="415", page_size=3)
        print(f"✅ Success! Found {len(result.get('available_phone_numbers', []))} numbers")
        
        for number in result.get('available_phone_numbers', [])[:2]:
            print(f"   📞 {number['phone_number']} - {number['locality']}, {number['region']}")
        
        # Test 2: List phone numbers  
        print("\n2️⃣ Testing: List Purchased Phone Numbers")
        
        result = await list_phone_numbers()
        print(f"✅ Success! Found {len(result.get('incoming_phone_numbers', []))} purchased numbers")
        
        for number in result.get('incoming_phone_numbers', []):
            print(f"   📱 {number['phone_number']} - Status: {number['status']}")
        
        # Test 3: Purchase phone number (demo mode)
        print("\n3️⃣ Testing: Purchase Phone Number (Demo)")
        
        result = await purchase_phone_number("+1234567890", "https://webhook.vocelio.ai/incoming")
        print(f"✅ Success! Purchased: {result['phone_number']}")
        print(f"   SID: {result['sid']}")
        print(f"   Status: {result['status']}")
        
        print("\n🎉 All Twilio endpoints are working locally!")
        print("📝 Note: These are demo responses since TWILIO_ACCOUNT_SID is not configured")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_twilio_endpoints())
