#!/bin/bash
# Update Supabase Credentials Across All Railway Services

echo "🚀 Updating Supabase credentials across all Railway services..."

SUPABASE_URL="https://bhzhgivqqnwvndzjthqv.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJoemhnaXZxcW53dm5kemp0aHF2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyODQ5MjgsImV4cCI6MjA3MDg2MDkyOH0.1JyoU3xQG7McYRIWzJfTfwv6oH7FCIZkLTLUnahLtKI"

services=(
    "api-gateway"
    "overview" 
    "ai-agents-service"
    "smart-campaigns"
    "analytics-pro"
    "team-hub"
    "phone-numbers"
    "voice-lab"
    "settings"
    "flow-builder"
    "call-center"
    "voice-marketplace"
    "ai-brain"
    "integrations"
    "billing-pro"
    "compliance"
    "white-label"
    "developer-api"
    "knowledge-base"
    "lead-management"
    "scheduling"
    "data-warehouse"
    "notifications"
    "scripts"
    "webhooks"
)

success_count=0
error_count=0

for service in "${services[@]}"; do
    echo "📝 Updating service: $service"
    
    railway service $service 2>/dev/null
    if [ $? -eq 0 ]; then
        railway variables --set "SUPABASE_URL=$SUPABASE_URL" --set "SUPABASE_KEY=$SUPABASE_KEY" --skip-deploys 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Successfully updated $service"
            ((success_count++))
        else
            echo "❌ Failed to set variables for $service"
            ((error_count++))
        fi
    else
        echo "⚠️ Service $service not found"
        ((error_count++))
    fi
    
    sleep 1
done

echo ""
echo "🎯 Update Summary:"
echo "✅ Successfully updated: $success_count services"
echo "❌ Failed updates: $error_count services"
