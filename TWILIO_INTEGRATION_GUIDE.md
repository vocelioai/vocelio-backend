# 📞 Twilio Integration Configuration for Railway Services

## 🎯 Complete Twilio Setup for Production Backend

### 1. Server-Side Twilio Configuration

#### A. Update Environment Variables for All Services

Add these to your Railway service environment variables:

```bash
# Twilio Configuration (Server-side only - NEVER expose in frontend)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
TWILIO_WEBHOOK_BASE_URL=https://your-primary-service.up.railway.app

# Twilio Features
TWILIO_VOICE_ENABLED=true
TWILIO_SMS_ENABLED=true
TWILIO_RECORDING_ENABLED=true
TWILIO_TRANSCRIPTION_ENABLED=true
```

#### B. Services That Need Twilio Integration:

1. **Call Center Service** - Main voice operations
2. **Phone Numbers Service** - Number management
3. **SMS Service** - Text messaging
4. **Voice Lab Service** - Voice synthesis
5. **Smart Campaigns Service** - Automated calling
6. **Webhook Service** - Twilio callbacks

### 2. Twilio Integration Code Templates

#### A. Call Center Service Integration

```python
# call-center-service/main.py
import os
from twilio.rest import Client
from twilio.twiml import VoiceResponse, MessagingResponse

# Twilio client setup
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None
    print("⚠️ Twilio not configured - using demo mode")

@app.post("/make-call")
async def make_call(request: CallRequest):
    if not twilio_client:
        return {"status": "demo", "message": "Twilio not configured - using demo data"}
    
    try:
        call = twilio_client.calls.create(
            to=request.to_number,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{os.getenv('TWILIO_WEBHOOK_BASE_URL')}/voice-webhook",
            method='POST'
        )
        
        return {
            "status": "success",
            "call_sid": call.sid,
            "to": request.to_number,
            "from": TWILIO_PHONE_NUMBER
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/voice-webhook")
async def voice_webhook(request: Request):
    """Twilio voice webhook handler"""
    response = VoiceResponse()
    
    # Your AI voice logic here
    response.say("Hello from Vocelio AI! This is a real call.", voice='alice')
    response.gather(
        num_digits=1,
        action='/gather-response',
        method='POST'
    )
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/sms-webhook")
async def sms_webhook(request: Request):
    """Twilio SMS webhook handler"""
    response = MessagingResponse()
    
    # Your AI SMS logic here
    response.message("Thank you for your message! Vocelio AI received it.")
    
    return Response(content=str(response), media_type="application/xml")
```

#### B. Phone Numbers Service Integration

```python
# phone-numbers-service/main.py
@app.get("/available-numbers")
async def get_available_numbers(area_code: str = "415", country: str = "US"):
    if not twilio_client:
        return {"status": "demo", "numbers": ["Demo: +1-555-DEMO-001", "+1-555-DEMO-002"]}
    
    try:
        available_numbers = twilio_client.available_phone_numbers(country).local.list(
            area_code=area_code,
            limit=10
        )
        
        return {
            "status": "success",
            "numbers": [num.phone_number for num in available_numbers]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/purchase-number")
async def purchase_number(request: PurchaseRequest):
    if not twilio_client:
        return {"status": "demo", "message": "Demo mode - number purchase simulated"}
    
    try:
        number = twilio_client.incoming_phone_numbers.create(
            phone_number=request.phone_number,
            voice_url=f"{os.getenv('TWILIO_WEBHOOK_BASE_URL')}/voice-webhook",
            sms_url=f"{os.getenv('TWILIO_WEBHOOK_BASE_URL')}/sms-webhook"
        )
        
        return {
            "status": "success",
            "phone_number": number.phone_number,
            "sid": number.sid
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### 3. Railway Environment Setup Commands

```bash
# Set Twilio variables for call-center service
railway service call-center-production-7c3d
railway variables set TWILIO_ACCOUNT_SID=your_account_sid
railway variables set TWILIO_AUTH_TOKEN=your_auth_token
railway variables set TWILIO_PHONE_NUMBER=your_phone_number
railway variables set TWILIO_WEBHOOK_BASE_URL=https://call-center-production-7c3d.up.railway.app

# Set for phone-numbers service
railway service phone-numbers-production-1e6c
railway variables set TWILIO_ACCOUNT_SID=your_account_sid
railway variables set TWILIO_AUTH_TOKEN=your_auth_token

# Set for SMS service
railway service sms-service-production-6e2a
railway variables set TWILIO_ACCOUNT_SID=your_account_sid
railway variables set TWILIO_AUTH_TOKEN=your_auth_token

# Set for webhook service
railway service webhook-service-production-3a9e
railway variables set TWILIO_ACCOUNT_SID=your_account_sid
railway variables set TWILIO_AUTH_TOKEN=your_auth_token
```

### 4. Twilio Webhook Configuration

#### A. Configure Twilio Console Webhooks

1. **Voice Webhooks:**
   - Primary: `https://call-center-production-7c3d.up.railway.app/voice-webhook`
   - Fallback: `https://webhook-service-production-3a9e.up.railway.app/voice-fallback`

2. **SMS Webhooks:**
   - Primary: `https://sms-service-production-6e2a.up.railway.app/sms-webhook`
   - Fallback: `https://webhook-service-production-3a9e.up.railway.app/sms-fallback`

3. **Status Callbacks:**
   - Call Status: `https://call-center-production-7c3d.up.railway.app/call-status`
   - Message Status: `https://sms-service-production-6e2a.up.railway.app/message-status`

#### B. Update Your Twilio Phone Numbers

```python
# Script to update all Twilio numbers with Railway webhooks
from twilio.rest import Client

client = Client(account_sid, auth_token)

# Update all your Twilio numbers
numbers = client.incoming_phone_numbers.list()

for number in numbers:
    number.update(
        voice_url='https://call-center-production-7c3d.up.railway.app/voice-webhook',
        sms_url='https://sms-service-production-6e2a.up.railway.app/sms-webhook',
        voice_method='POST',
        sms_method='POST'
    )
    print(f"Updated {number.phone_number}")
```

### 5. Frontend Integration Update

#### A. Update Frontend to Use Real Twilio Data

```javascript
// src/lib/railwayAPI.js - Update to handle real Twilio responses
async getTwilioNumbers() {
  try {
    const response = await this.request('phoneNumbers', '/dashboard');
    
    // Check if real Twilio data or demo
    if (response.twilio_configured) {
      return {
        status: 'live',
        numbers: response.data.numbers,
        source: 'twilio'
      };
    } else {
      return {
        status: 'demo',
        numbers: response.data.numbers,
        source: 'demo'
      };
    }
  } catch (error) {
    return this.getMockData('/numbers');
  }
}

async makeCall(phoneNumber, campaign) {
  try {
    const response = await this.request('callCenter', '/make-call', {
      method: 'POST',
      body: JSON.stringify({
        to_number: phoneNumber,
        campaign_id: campaign.id,
        ai_agent_id: campaign.ai_agent_id
      })
    });
    
    return response;
  } catch (error) {
    console.error('Call failed:', error);
    return { status: 'error', message: error.message };
  }
}
```

### 6. Testing Your Twilio Integration

#### A. Test Commands

```bash
# Test call endpoint
curl -X POST https://call-center-production-7c3d.up.railway.app/make-call \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+1234567890", "campaign_id": "test"}'

# Test SMS endpoint
curl -X POST https://sms-service-production-6e2a.up.railway.app/send-sms \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+1234567890", "message": "Test from Vocelio"}'

# Test number lookup
curl https://phone-numbers-production-1e6c.up.railway.app/available-numbers?area_code=415
```

#### B. Frontend Testing Component

```javascript
// Add to your dashboard - Twilio Integration Tester
const TwilioTester = () => {
  const [testResults, setTestResults] = useState(null);
  
  const testTwilioIntegration = async () => {
    const tests = [
      { name: 'Available Numbers', endpoint: 'phoneNumbers', path: '/available-numbers' },
      { name: 'Call Center Status', endpoint: 'callCenter', path: '/status' },
      { name: 'SMS Service Status', endpoint: 'sms', path: '/status' }
    ];
    
    const results = {};
    
    for (const test of tests) {
      try {
        const result = await railwayAPI.request(test.endpoint, test.path);
        results[test.name] = { status: 'success', data: result };
      } catch (error) {
        results[test.name] = { status: 'error', error: error.message };
      }
    }
    
    setTestResults(results);
  };
  
  return (
    <div className="p-6 bg-gray-800 text-white rounded-lg">
      <h3 className="text-xl font-bold mb-4">🔧 Twilio Integration Tester</h3>
      
      <button
        onClick={testTwilioIntegration}
        className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded mb-4"
      >
        Test Twilio Integration
      </button>
      
      {testResults && (
        <div className="space-y-2">
          {Object.entries(testResults).map(([test, result]) => (
            <div key={test} className="flex items-center gap-2">
              <span className={result.status === 'success' ? 'text-green-400' : 'text-red-400'}>
                {result.status === 'success' ? '✅' : '❌'}
              </span>
              <span>{test}</span>
              {result.data?.twilio_configured && (
                <span className="bg-green-600 text-white px-2 py-1 text-xs rounded">LIVE</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### 7. Security Best Practices

```bash
# Environment variables security checklist:
✅ Twilio credentials only in Railway backend services (never frontend)
✅ Use Railway's environment variables (encrypted at rest)
✅ Webhook URLs use HTTPS only
✅ Validate webhook signatures from Twilio
✅ Rate limiting on webhook endpoints
✅ Monitor for unusual call/SMS patterns
```

### 8. Production Checklist

- [ ] Add Twilio credentials to Railway services
- [ ] Update webhook URLs in Twilio console
- [ ] Test voice calls end-to-end
- [ ] Test SMS messaging
- [ ] Verify call recordings work
- [ ] Test number purchasing
- [ ] Monitor webhook logs
- [ ] Set up Twilio usage alerts
- [ ] Configure failover numbers
- [ ] Test international calling (if needed)

### 🚀 Your Action Items:

1. **Get your Twilio credentials:**
   - Account SID from Twilio Console
   - Auth Token from Twilio Console
   - Your purchased Twilio phone number

2. **Add to Railway services:**
   ```bash
   railway login
   railway service [service-name]
   railway variables set TWILIO_ACCOUNT_SID=your_sid
   railway variables set TWILIO_AUTH_TOKEN=your_token
   ```

3. **Update Twilio webhooks** to point to your Railway URLs

4. **Test integration** using the frontend tester component

**Once you have your Twilio credentials, I can help you deploy these configurations to all your Railway services!**
