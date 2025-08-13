Write-Host "🔧 CONFIGURING TWILIO FOR RAILWAY SERVICES" -ForegroundColor Cyan
Write-Host ""

# Twilio credentials
$ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
$AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
$PHONE_NUMBER = "YOUR_TWILIO_PHONE_NUMBER"

# Configure current service (api-management)
Write-Host "📞 Setting Twilio variables for current service..." -ForegroundColor Yellow

railway variables --set "TWILIO_ACCOUNT_SID=$ACCOUNT_SID" --set "TWILIO_AUTH_TOKEN=$AUTH_TOKEN" --set "TWILIO_PHONE_NUMBER=$PHONE_NUMBER" --set "TWILIO_WEBHOOK_BASE_URL=https://api-management-production.up.railway.app" --set "TWILIO_VOICE_ENABLED=true" --set "TWILIO_SMS_ENABLED=true" --set "TWILIO_RECORDING_ENABLED=true" --set "TWILIO_TRANSCRIPTION_ENABLED=true"

Write-Host ""
Write-Host "✅ API Management Service configured!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 TO CONFIGURE OTHER SERVICES:" -ForegroundColor Cyan
Write-Host "  Run these commands manually:"
Write-Host ""
Write-Host "  # Call Center Service"
Write-Host "  railway service call-center"
Write-Host "  railway variables --set 'TWILIO_ACCOUNT_SID=$ACCOUNT_SID' --set 'TWILIO_AUTH_TOKEN=$AUTH_TOKEN' --set 'TWILIO_PHONE_NUMBER=$PHONE_NUMBER'"
Write-Host ""
Write-Host "  # Phone Numbers Service"
Write-Host "  railway service phone-numbers"
Write-Host "  railway variables --set 'TWILIO_ACCOUNT_SID=$ACCOUNT_SID' --set 'TWILIO_AUTH_TOKEN=$AUTH_TOKEN' --set 'TWILIO_PHONE_NUMBER=$PHONE_NUMBER'"
Write-Host ""
Write-Host "  # SMS Service"
Write-Host "  railway service sms-service"
Write-Host "  railway variables --set 'TWILIO_ACCOUNT_SID=$ACCOUNT_SID' --set 'TWILIO_AUTH_TOKEN=$AUTH_TOKEN' --set 'TWILIO_PHONE_NUMBER=$PHONE_NUMBER'"
