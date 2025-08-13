# Twilio Configuration Script for Railway Services
# Run this after setting up each service

# Service configurations
$services = @{
    "call-center" = "https://call-center-production-7c3d.up.railway.app"
    "phone-numbers" = "https://phone-numbers-production-1e6c.up.railway.app"
    "sms-service" = "https://sms-service-production-6e2a.up.railway.app"
    "voice-lab" = "https://voice-lab-production-8a9b.up.railway.app"
    "smart-campaigns" = "https://smart-campaigns-production-4a1d.up.railway.app"
    "webhook-service" = "https://webhook-service-production-3a9e.up.railway.app"
    "overview" = "https://overview-production-3f2e.up.railway.app"
    "api-gateway" = "https://api-gateway-production-588d.up.railway.app"
}

# Twilio credentials
$ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
$AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
$PHONE_NUMBER = "YOUR_TWILIO_PHONE_NUMBER"

Write-Host "🔧 CONFIGURING TWILIO FOR ALL RAILWAY SERVICES" -ForegroundColor Cyan
Write-Host ""

foreach ($service in $services.Keys) {
    Write-Host "📞 Configuring $service..." -ForegroundColor Yellow
    
    try {
        # Switch to service and set variables
        railway service $service
        
        railway variables --set "TWILIO_ACCOUNT_SID=$ACCOUNT_SID" `
                         --set "TWILIO_AUTH_TOKEN=$AUTH_TOKEN" `
                         --set "TWILIO_PHONE_NUMBER=$PHONE_NUMBER" `
                         --set "TWILIO_WEBHOOK_BASE_URL=$($services[$service])" `
                         --set "TWILIO_VOICE_ENABLED=true" `
                         --set "TWILIO_SMS_ENABLED=true" `
                         --set "TWILIO_RECORDING_ENABLED=true" `
                         --set "TWILIO_TRANSCRIPTION_ENABLED=true" `
                         --skip-deploys
        
        Write-Host "  ✅ $service configured successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Failed to configure $service" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🚀 TRIGGERING DEPLOYMENT FOR ALL SERVICES..." -ForegroundColor Cyan

# Trigger deployment for all services
foreach ($service in $services.Keys) {
    try {
        railway service $service
        railway up --detach
        Write-Host "  ✅ Deployed $service" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Failed to deploy $service" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ TWILIO CONFIGURATION COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Update Twilio Console webhooks"
Write-Host "  2. Test voice calls through frontend"
Write-Host "  3. Test SMS messaging"
Write-Host "  4. Verify call recordings"
