#!/bin/bash
# Railway Deployment Script for Enhanced Services
# Run this script to deploy all enhanced services to Railway

echo "🚀 RAILWAY DEPLOYMENT - Enhanced Services v2.0.0"
echo "=================================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Login check
echo "🔐 Checking Railway authentication..."
railway whoami
if [ $? -ne 0 ]; then
    echo "❌ Not logged in to Railway. Please run: railway login"
    exit 1
fi

echo "✅ Railway authentication confirmed"
echo ""

# Deploy each enhanced service
echo "🚀 Starting deployment of enhanced services..."
echo ""

# Enhanced AI Agents Service
echo "🤖 Deploying Enhanced AI Agents Service v2.0.0..."
cd apps/ai-agents-service
railway up
if [ $? -eq 0 ]; then
    echo "✅ AI Agents Service deployed successfully"
else
    echo "❌ AI Agents Service deployment failed"
fi
cd ../..
echo ""

# Enhanced Smart Campaigns Service  
echo "🎯 Deploying Enhanced Smart Campaigns Service v2.0.0..."
cd apps/smart-campaigns
railway up
if [ $? -eq 0 ]; then
    echo "✅ Smart Campaigns Service deployed successfully"
else
    echo "❌ Smart Campaigns Service deployment failed"
fi
cd ../..
echo ""

# Enhanced Overview Service
echo "📊 Deploying Enhanced Overview Service v2.0.0..."
cd apps/overview
railway up
if [ $? -eq 0 ]; then
    echo "✅ Overview Service deployed successfully"
else
    echo "❌ Overview Service deployment failed"
fi
cd ../..
echo ""

# Enhanced Compliance Service
echo "🔐 Deploying Enhanced Compliance Service v2.0.0..."
cd apps/compliance
railway up
if [ $? -eq 0 ]; then
    echo "✅ Compliance Service deployed successfully"
else
    echo "❌ Compliance Service deployment failed"
fi
cd ../..
echo ""

echo "🎉 DEPLOYMENT COMPLETE!"
echo "====================="
echo ""
echo "📋 Post-deployment checklist:"
echo "- [ ] Verify health checks for all services"
echo "- [ ] Test enhanced features (marketplace, templates, real-time updates)"
echo "- [ ] Validate compliance frameworks (15+)"
echo "- [ ] Check Redis cache performance"
echo "- [ ] Monitor service logs for any issues"
echo ""
echo "🔍 Health check URLs:"
echo "- AI Agents: https://<your-domain>/health"
echo "- Smart Campaigns: https://<your-domain>/health"
echo "- Overview: https://<your-domain>/health"
echo "- Compliance: https://<your-domain>/health"
echo ""
echo "✨ All enhanced services from 4-phase consolidation deployed!"
