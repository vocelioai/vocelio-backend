@echo off
REM Railway Deployment Script for Enhanced Services (Windows)
REM Run this script to deploy all enhanced services to Railway

echo 🚀 RAILWAY DEPLOYMENT - Enhanced Services v2.0.0
echo ==================================================
echo.

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Railway CLI not found. Please install: npm install -g @railway/cli
    pause
    exit /b 1
)

echo ✅ Railway CLI found
echo.

REM Login check
echo 🔐 Checking Railway authentication...
railway whoami
if errorlevel 1 (
    echo ❌ Not logged in to Railway. Please run: railway login
    pause
    exit /b 1
)

echo ✅ Railway authentication confirmed
echo.

REM Deploy each enhanced service
echo 🚀 Starting deployment of enhanced services...
echo.

REM Enhanced AI Agents Service
echo 🤖 Deploying Enhanced AI Agents Service v2.0.0...
cd apps\ai-agents-service
railway up
if %errorlevel% equ 0 (
    echo ✅ AI Agents Service deployed successfully
) else (
    echo ❌ AI Agents Service deployment failed
)
cd ..\..
echo.

REM Enhanced Smart Campaigns Service
echo 🎯 Deploying Enhanced Smart Campaigns Service v2.0.0...
cd apps\smart-campaigns
railway up
if %errorlevel% equ 0 (
    echo ✅ Smart Campaigns Service deployed successfully
) else (
    echo ❌ Smart Campaigns Service deployment failed
)
cd ..\..
echo.

REM Enhanced Overview Service
echo 📊 Deploying Enhanced Overview Service v2.0.0...
cd apps\overview
railway up
if %errorlevel% equ 0 (
    echo ✅ Overview Service deployed successfully
) else (
    echo ❌ Overview Service deployment failed
)
cd ..\..
echo.

REM Enhanced Compliance Service
echo 🔐 Deploying Enhanced Compliance Service v2.0.0...
cd apps\compliance
railway up
if %errorlevel% equ 0 (
    echo ✅ Compliance Service deployed successfully
) else (
    echo ❌ Compliance Service deployment failed
)
cd ..\..
echo.

echo 🎉 DEPLOYMENT COMPLETE!
echo =====================
echo.
echo 📋 Post-deployment checklist:
echo - [ ] Verify health checks for all services
echo - [ ] Test enhanced features (marketplace, templates, real-time updates)
echo - [ ] Validate compliance frameworks (15+)
echo - [ ] Check Redis cache performance
echo - [ ] Monitor service logs for any issues
echo.
echo 🔍 Health check URLs:
echo - AI Agents: https://^<your-domain^>/health
echo - Smart Campaigns: https://^<your-domain^>/health
echo - Overview: https://^<your-domain^>/health
echo - Compliance: https://^<your-domain^>/health
echo.
echo ✨ All enhanced services from 4-phase consolidation deployed!
pause
