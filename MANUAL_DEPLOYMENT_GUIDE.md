# 🚀 Manual Railway Deployment Guide
# Enhanced Services v2.0.0 - Step by Step

## Prerequisites ✅
- Railway CLI installed and authenticated ✅ (confirmed)
- Git repository pushed to GitHub ✅ (confirmed) 
- Enhanced services ready ✅ (confirmed)

## 🔄 Manual Deployment Process

### Method 1: Railway Dashboard (Recommended for beginners)

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/dashboard
   - Login with your account (vocelioai@gmail.com)

2. **Create New Project for Each Service**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: vocelioai/vocelio-backend
   - Configure root directory for each service

3. **Service Configuration**
   For each service, set the root directory:
   - AI Agents: `apps/ai-agents-service`
   - Smart Campaigns: `apps/smart-campaigns`
   - Overview: `apps/overview`
   - Compliance: `apps/compliance`

### Method 2: Railway CLI (Step by Step)

#### Step 1: Deploy AI Agents Service
```bash
cd "C:\Users\SNC\OneDrive\Desktop\vocelio-backend\apps\ai-agents-service"

# Option A: Link to existing project
railway link

# Option B: Create new project
railway login
railway init
railway up
```

#### Step 2: Deploy Smart Campaigns Service
```bash
cd "C:\Users\SNC\OneDrive\Desktop\vocelio-backend\apps\smart-campaigns"
railway init
railway up
```

#### Step 3: Deploy Overview Service
```bash
cd "C:\Users\SNC\OneDrive\Desktop\vocelio-backend\apps\overview"
railway init
railway up
```

#### Step 4: Deploy Compliance Service
```bash
cd "C:\Users\SNC\OneDrive\Desktop\vocelio-backend\apps\compliance"
railway init
railway up
```

## 🎯 Simplified Single Command Deployment

### For Each Service Directory:
1. Open PowerShell/Terminal
2. Navigate to service directory
3. Run these commands:

```powershell
# Example for AI Agents Service
cd "C:\Users\SNC\OneDrive\Desktop\vocelio-backend\apps\ai-agents-service"
railway login  # if not logged in
railway init    # create new service
railway up      # deploy
```

## 🔧 Environment Variables Setup

After deployment, set these environment variables in Railway dashboard:

### All Services:
- `ENVIRONMENT=production`
- `DATABASE_URL` (from Railway PostgreSQL addon)
- `JWT_SECRET` (your secret key)

### Compliance Service Additional:
- `REDIS_URL` (from Railway Redis addon)
- `COMPLIANCE_FRAMEWORKS_ENABLED=GDPR,SOX,HIPAA,PCI_DSS,ISO27001,NIST,FISMA,CCPA`

### Overview Service Additional:
- `REDIS_URL` (from Railway Redis addon)

## 📋 Post-Deployment Checklist

1. **Verify Deployments**
   - Check Railway dashboard for all 4 services
   - Verify health endpoints: `/health`
   - Check logs for any errors

2. **Test Enhanced Features**
   - AI Agents: Test marketplace (200+ agents)
   - Smart Campaigns: Test templates (89+ available)
   - Overview: Test real-time dashboard
   - Compliance: Test frameworks (15+ supported)

3. **Database Setup**
   - Ensure PostgreSQL addon is connected
   - Run any necessary migrations
   - Verify Redis connection for caching

## 🚨 Common Issues & Solutions

### Issue 1: Build Fails
**Solution**: Check `railway.toml` configuration and `railway_start.py` file

### Issue 2: Port Binding Error
**Solution**: Ensure `railway_start.py` uses `PORT` environment variable

### Issue 3: Import Errors
**Solution**: Verify Python path and dependencies in `requirements.txt`

### Issue 4: Database Connection
**Solution**: Add PostgreSQL addon and set `DATABASE_URL`

## 🔗 Quick Links

- Railway Dashboard: https://railway.app/dashboard
- Health Check Template: `https://your-service.railway.app/health`
- Railway Docs: https://docs.railway.com

## 📞 Support

If you encounter issues:
1. Check Railway logs in dashboard
2. Verify environment variables
3. Test locally first with `python railway_start.py`
4. Check GitHub repository is up to date

---

**All enhanced services are ready for deployment! 🎉**
