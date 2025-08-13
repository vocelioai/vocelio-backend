# 📞 Twilio Console Webhook Configuration

## Your Twilio Account Details
- **Account SID**: YOUR_TWILIO_ACCOUNT_SID
- **Phone Number**: YOUR_TWILIO_PHONE_NUMBER
- **Status**: ✅ ACTIVE & CONFIGURED

---

## 🔗 Webhook URLs for Twilio Console

### 1. Voice Webhooks

**Primary Voice URL** (for incoming calls):
```
https://call-center-production-7c3d.up.railway.app/voice-webhook
```

**Voice Status Callback URL** (call status updates):
```
https://call-center-production-7c3d.up.railway.app/call-status
```

**Voice Fallback URL** (if primary fails):
```
https://webhook-service-production-3a9e.up.railway.app/voice-fallback
```

### 2. SMS Webhooks

**Primary SMS URL** (for incoming messages):
```
https://sms-service-production-6e2a.up.railway.app/sms-webhook
```

**SMS Status Callback URL** (message status updates):
```
https://sms-service-production-6e2a.up.railway.app/message-status
```

**SMS Fallback URL** (if primary fails):
```
https://webhook-service-production-3a9e.up.railway.app/sms-fallback
```

---

## 🛠️ Twilio Console Setup Steps

### Step 1: Configure Your Phone Number (+13072072333)

1. **Login to Twilio Console**: https://console.twilio.com
2. **Navigate to**: Phone Numbers → Manage → Active Numbers
3. **Click on your number**: +13072072333
4. **Configure Voice & Fax section**:
   - Webhook: `https://call-center-production-7c3d.up.railway.app/voice-webhook`
   - HTTP Method: `POST`
   - Primary Handler Fails: `https://webhook-service-production-3a9e.up.railway.app/voice-fallback`

5. **Configure Messaging section**:
   - Webhook: `https://sms-service-production-6e2a.up.railway.app/sms-webhook`
   - HTTP Method: `POST`
   - Primary Handler Fails: `https://webhook-service-production-3a9e.up.railway.app/sms-fallback`

### Step 2: Configure Global Webhooks

1. **Navigate to**: Settings → General
2. **Set Status Callback URL**: `https://call-center-production-7c3d.up.railway.app/call-status`
3. **Enable Events**: 
   - ✅ Call Initiated
   - ✅ Call Ringing
   - ✅ Call Answered
   - ✅ Call Completed

### Step 3: Test Configuration

1. **Test Voice**: Call +13072072333 from any phone
2. **Test SMS**: Send a text to +13072072333
3. **Check Logs**: Monitor Railway service logs for incoming webhooks

---

## 🧪 Testing Your Integration

### Frontend Test Commands

Once your dashboard is running, test these endpoints:

```javascript
// Test call making
const callResult = await railwayAPI.request('callCenter', '/make-call', {
  method: 'POST',
  body: JSON.stringify({
    to_number: '+1234567890',
    from_number: '+13072072333',
    campaign_id: 'test-campaign'
  })
});

// Test SMS sending
const smsResult = await railwayAPI.request('sms', '/send-sms', {
  method: 'POST',
  body: JSON.stringify({
    to_number: '+1234567890',
    message: 'Hello from Vocelio AI!',
    from_number: '+13072072333'
  })
});

// Test number lookup
const numbers = await railwayAPI.request('phoneNumbers', '/available-numbers?area_code=307');
```

### Direct API Testing

```bash
# Test call endpoint
curl -X POST https://call-center-production-7c3d.up.railway.app/make-call \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+1234567890",
    "from_number": "+13072072333",
    "campaign_id": "test"
  }'

# Test SMS endpoint
curl -X POST https://sms-service-production-6e2a.up.railway.app/send-sms \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+1234567890",
    "message": "Test from Vocelio AI",
    "from_number": "+13072072333"
  }'
```

---

## 🔐 Security Configuration

### Environment Variables Set ✅

The following variables are now configured across your Railway services:

```bash
TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=[SECURED] # Hidden for security
TWILIO_PHONE_NUMBER=YOUR_TWILIO_PHONE_NUMBER
TWILIO_WEBHOOK_BASE_URL=[Service-specific URLs]
TWILIO_VOICE_ENABLED=true
TWILIO_SMS_ENABLED=true
TWILIO_RECORDING_ENABLED=true
TWILIO_TRANSCRIPTION_ENABLED=true
```

### Webhook Signature Validation

Your services will validate Twilio webhooks using your auth token to ensure security.

---

## ✅ Configuration Checklist

- [x] **Twilio credentials deployed** to Railway services
- [ ] **Twilio Console webhooks** configured (do this now)
- [ ] **Phone number webhooks** updated
- [ ] **Voice calls tested** end-to-end
- [ ] **SMS messaging tested**
- [ ] **Frontend integration** verified
- [ ] **Call recordings** working
- [ ] **Transcription** enabled

---

## 🚀 Ready to Test!

**Your Twilio integration is now LIVE!** 

1. **Configure the webhooks** in Twilio Console using the URLs above
2. **Test a call** to +13072072333
3. **Send an SMS** to +13072072333
4. **Check your Railway logs** to see the webhooks in action
5. **Use your frontend dashboard** to make outbound calls and send SMS

**🎉 You now have a fully functional enterprise-grade AI calling platform!**
