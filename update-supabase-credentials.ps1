# 🔄 Update Supabase Credentials Across All Railway Services
# This script updates the Supabase URL and Key for all Vocelio services

Write-Host "🚀 Updating Supabase credentials across all Railway services..." -ForegroundColor Cyan

# New Supabase credentials
$SUPABASE_URL = "https://bhzhgivqqnwvndzjthqv.supabase.co"
$SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJoemhnaXZxcW53dm5kemp0aHF2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyODQ5MjgsImV4cCI6MjA3MDg2MDkyOH0.1JyoU3xQG7McYRIWzJfTfwv6oH7FCIZkLTLUnahLtKI"

# List of all Vocelio services
$services = @(
    "api-gateway",
    "overview",
    "ai-agents-service", 
    "smart-campaigns",
    "analytics-pro",
    "team-hub",
    "phone-numbers",
    "voice-lab",
    "settings",
    "flow-builder",
    "call-center",
    "voice-marketplace",
    "ai-brain",
    "integrations",
    "ai-agent-platform",
    "billing-pro",
    "compliance",
    "white-label",
    "developer-api",
    "knowledge-base",
    "lead-management",
    "scheduling",
    "unified-campaigns",
    "data-warehouse",
    "notifications",
    "scripts",
    "webhooks",
    "recording",
    "monitoring"
)

$successCount = 0
$errorCount = 0

foreach ($service in $services) {
    Write-Host "📝 Updating service: $service" -ForegroundColor Yellow
    
    try {
        # Switch to service
        railway service $service
        
        if ($LASTEXITCODE -eq 0) {
            # Set Supabase variables
            railway variables --set "SUPABASE_URL=$SUPABASE_URL" --set "SUPABASE_KEY=$SUPABASE_KEY" --skip-deploys
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Successfully updated $service" -ForegroundColor Green
                $successCount++
            } else {
                Write-Host "❌ Failed to set variables for $service" -ForegroundColor Red
                $errorCount++
            }
        } else {
            Write-Host "⚠️  Service $service not found or not accessible" -ForegroundColor Orange
            $errorCount++
        }
    }
    catch {
        Write-Host "❌ Error updating $service`: $_" -ForegroundColor Red
        $errorCount++
    }
    
    Start-Sleep -Seconds 1
}

Write-Host "`n🎯 Update Summary:" -ForegroundColor Cyan
Write-Host "✅ Successfully updated: $successCount services" -ForegroundColor Green
Write-Host "❌ Failed updates: $errorCount services" -ForegroundColor Red

if ($errorCount -eq 0) {
    Write-Host "`n🚀 All services updated successfully with new Supabase credentials!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some services failed to update. Please check the logs above." -ForegroundColor Orange
}

Write-Host "`n📋 New Credentials Applied:" -ForegroundColor Cyan
Write-Host "🔗 SUPABASE_URL: $SUPABASE_URL" -ForegroundColor White
Write-Host "🔑 SUPABASE_KEY: ${SUPABASE_KEY.Substring(0,50)}..." -ForegroundColor White
