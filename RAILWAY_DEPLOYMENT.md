# 🚀 Railway Deployment Guide for Vocelio.ai Services

## 📋 Prerequisites
- Railway account: https://railway.app
- GitHub repository connected
- Railway CLI (optional): `npm install -g @railway/cli`

## 🎯 Ready Services for Deployment

### ✅ Overview Service (Dashboard Metrics)
- **Port**: 8001 (Railway will override with PORT env var)
- **Health Check**: `/health`
- **Dockerfile**: `apps/overview/Dockerfile`
- **Start Script**: `apps/overview/start.sh`

### ✅ Smart Campaigns Service (AI Campaign Automation)
- **Port**: 8003 (Railway will override with PORT env var)  
- **Health Check**: `/health`
- **Dockerfile**: `apps/smart-campaigns/Dockerfile`
- **Start Script**: `apps/smart-campaigns/start.sh`

## 🚀 Deployment Steps

### Method 1: Railway Web Dashboard (Recommended)

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Create New Project**
3. **Deploy from GitHub repo**:
   - Repository: `vocelioai/vocelio-backend`
   - Branch: `main`

#### For Overview Service:
```bash
# Root Directory: apps/overview
# Build Command: (automatic via Dockerfile)
# Start Command: ./start.sh
# Port: $PORT (Railway sets automatically)
```

#### For Smart Campaigns Service:
```bash
# Root Directory: apps/smart-campaigns  
# Build Command: (automatic via Dockerfile)
# Start Command: ./start.sh
# Port: $PORT (Railway sets automatically)
```

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy Overview Service
cd apps/overview
railway deploy

# Deploy Smart Campaigns Service  
cd ../smart-campaigns
railway deploy
```

## 🔧 Environment Variables to Set in Railway

### For Both Services:
```env
ENVIRONMENT=production
DEBUG=false
```

### For Overview Service:
```env
SERVICE_NAME=vocelio-overview
SERVICE_VERSION=1.0.0
```

### For Smart Campaigns Service:
```env
SERVICE_NAME=smart-campaigns
```

## 🌐 Expected URLs After Deployment

Railway will provide URLs like:
- **Overview**: `https://vocelio-overview-production.up.railway.app`
- **Smart Campaigns**: `https://smart-campaigns-production.up.railway.app`

## ✅ Health Check Endpoints

Test these after deployment:
- `https://<your-service-url>/health`
- `https://<your-service-url>/docs` (API documentation)

## 🔍 Monitoring

Check Railway deployment logs for:
```
🚀 Starting Vocelio.ai Overview Service...
📍 Service: Overview Service
🌐 Port: <PORT>
📦 PYTHONPATH: .
✅ Service started successfully
```

## 🔄 Next Steps After Deployment

1. **Test health endpoints**
2. **Update API Gateway** to route to deployed services
3. **Deploy remaining services** (AI Agents, Call Center, etc.)
4. **Configure custom domains** (optional)

## 🛠️ Troubleshooting

If deployment fails:
1. Check Railway build logs
2. Verify Dockerfile and start.sh are executable
3. Ensure all dependencies in requirements.txt
4. Check PORT environment variable usage

## 📞 Support

- Railway Docs: https://docs.railway.app
- GitHub Issues: https://github.com/vocelioai/vocelio-backend/issues
