#!/bin/bash
# 🚀 Vercel Environment Variables Setup Script
# Run this script to automatically set all environment variables in your Vercel project

# Set your Vercel project ID and team ID
VERCEL_PROJECT_ID="your-project-id"
VERCEL_TEAM_ID="your-team-id"

echo "🌟 Setting up Vocelio AI environment variables for Vercel..."

# Core Foundation Services (7)
vercel env add NEXT_PUBLIC_API_GATEWAY_URL production
echo "https://api.vocelio.ai" | vercel env add NEXT_PUBLIC_API_GATEWAY_URL production

vercel env add NEXT_PUBLIC_OVERVIEW_URL production  
echo "https://overview.vocelio.ai" | vercel env add NEXT_PUBLIC_OVERVIEW_URL production

vercel env add NEXT_PUBLIC_AI_AGENTS_URL production
echo "https://agents.vocelio.ai" | vercel env add NEXT_PUBLIC_AI_AGENTS_URL production

vercel env add NEXT_PUBLIC_SMART_CAMPAIGNS_URL production
echo "https://campaigns.vocelio.ai" | vercel env add NEXT_PUBLIC_SMART_CAMPAIGNS_URL production

vercel env add NEXT_PUBLIC_ANALYTICS_URL production
echo "https://analytics.vocelio.ai" | vercel env add NEXT_PUBLIC_ANALYTICS_URL production

vercel env add NEXT_PUBLIC_TEAM_HUB_URL production
echo "https://team.vocelio.ai" | vercel env add NEXT_PUBLIC_TEAM_HUB_URL production

vercel env add NEXT_PUBLIC_PHONE_NUMBERS_URL production
echo "https://numbers.vocelio.ai" | vercel env add NEXT_PUBLIC_PHONE_NUMBERS_URL production

# Business Services (6)
vercel env add NEXT_PUBLIC_VOICE_LAB_URL production
echo "https://voicelab.vocelio.ai" | vercel env add NEXT_PUBLIC_VOICE_LAB_URL production

vercel env add NEXT_PUBLIC_SETTINGS_URL production
echo "https://settings.vocelio.ai" | vercel env add NEXT_PUBLIC_SETTINGS_URL production

vercel env add NEXT_PUBLIC_FLOW_BUILDER_URL production
echo "https://flowbuilder.vocelio.ai" | vercel env add NEXT_PUBLIC_FLOW_BUILDER_URL production

vercel env add NEXT_PUBLIC_CALL_CENTER_URL production
echo "https://call.vocelio.ai" | vercel env add NEXT_PUBLIC_CALL_CENTER_URL production

vercel env add NEXT_PUBLIC_VOICE_MARKETPLACE_URL production
echo "https://voicemarketplace.vocelio.ai" | vercel env add NEXT_PUBLIC_VOICE_MARKETPLACE_URL production

vercel env add NEXT_PUBLIC_AI_BRAIN_URL production
echo "https://brain.vocelio.ai" | vercel env add NEXT_PUBLIC_AI_BRAIN_URL production

# Enterprise Features (6)
vercel env add NEXT_PUBLIC_INTEGRATIONS_URL production
echo "https://integrations.vocelio.ai" | vercel env add NEXT_PUBLIC_INTEGRATIONS_URL production

vercel env add NEXT_PUBLIC_AI_AGENT_PLATFORM_URL production
echo "https://backend.vocelio.ai" | vercel env add NEXT_PUBLIC_AI_AGENT_PLATFORM_URL production

vercel env add NEXT_PUBLIC_BILLING_URL production
echo "https://billing.vocelio.ai" | vercel env add NEXT_PUBLIC_BILLING_URL production

vercel env add NEXT_PUBLIC_COMPLIANCE_URL production
echo "https://compliance.vocelio.ai" | vercel env add NEXT_PUBLIC_COMPLIANCE_URL production

vercel env add NEXT_PUBLIC_WHITE_LABEL_URL production
echo "https://whitelabel.vocelio.ai" | vercel env add NEXT_PUBLIC_WHITE_LABEL_URL production

vercel env add NEXT_PUBLIC_DEVELOPER_API_URL production
echo "https://developer.vocelio.ai" | vercel env add NEXT_PUBLIC_DEVELOPER_API_URL production

# AI & Automation Services (6)
vercel env add NEXT_PUBLIC_KNOWLEDGE_BASE_URL production
echo "https://knowledge.vocelio.ai" | vercel env add NEXT_PUBLIC_KNOWLEDGE_BASE_URL production

vercel env add NEXT_PUBLIC_LEAD_MANAGEMENT_URL production
echo "https://lead.vocelio.ai" | vercel env add NEXT_PUBLIC_LEAD_MANAGEMENT_URL production

vercel env add NEXT_PUBLIC_SCHEDULING_URL production
echo "https://scheduling.vocelio.ai" | vercel env add NEXT_PUBLIC_SCHEDULING_URL production

vercel env add NEXT_PUBLIC_DATA_WAREHOUSE_URL production
echo "https://data.vocelio.ai" | vercel env add NEXT_PUBLIC_DATA_WAREHOUSE_URL production

vercel env add NEXT_PUBLIC_IDENTITY_URL production
echo "https://identity.vocelio.ai" | vercel env add NEXT_PUBLIC_IDENTITY_URL production

vercel env add NEXT_PUBLIC_SECURITY_URL production
echo "https://security.vocelio.ai" | vercel env add NEXT_PUBLIC_SECURITY_URL production

# Communication & Compliance (4)
vercel env add NEXT_PUBLIC_NOTIFICATIONS_URL production
echo "https://notifications.vocelio.ai" | vercel env add NEXT_PUBLIC_NOTIFICATIONS_URL production

vercel env add NEXT_PUBLIC_SCRIPTS_URL production
echo "https://scripts.vocelio.ai" | vercel env add NEXT_PUBLIC_SCRIPTS_URL production

vercel env add NEXT_PUBLIC_WEBHOOKS_URL production
echo "https://webhooks.vocelio.ai" | vercel env add NEXT_PUBLIC_WEBHOOKS_URL production

vercel env add NEXT_PUBLIC_API_MANAGEMENT_URL production
echo "https://apimanagement.vocelio.ai" | vercel env add NEXT_PUBLIC_API_MANAGEMENT_URL production

# Configuration Variables
vercel env add NEXT_PUBLIC_API_VERSION production
echo "v1" | vercel env add NEXT_PUBLIC_API_VERSION production

vercel env add NEXT_PUBLIC_ENVIRONMENT production
echo "production" | vercel env add NEXT_PUBLIC_ENVIRONMENT production

echo "✅ All environment variables set successfully!"
echo "🚀 Your Vocelio AI platform is ready for frontend deployment!"
