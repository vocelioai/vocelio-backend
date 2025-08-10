# 🚀 Vocelio.ai Production Environment Setup

## 📋 Environment Variables Checklist

### ✅ Completed Configuration

Your `.env` file has been configured with the following production-ready settings:

#### 🔐 **Authentication & Security**
- `JWT_SECRET_KEY` - Secure JWT token generation
- `JWT_ALGORITHM` - HS256 encryption
- `SECRET_KEY` - Application secret key
- `WEBHOOK_SECRET` - Webhook validation

#### 🗄️ **Database Configuration** 
- `DATABASE_URL` - PostgreSQL connection
- `SUPABASE_URL` - Supabase backend service
- `SUPABASE_KEY` - Supabase authentication key
- `REDIS_URL` - Redis caching service

#### 🤖 **AI Service Integration**
- `OPENAI_API_KEY` ✅ **Configured** - GPT-4o-mini model access
- `ELEVENLABS_API_KEY` ✅ **Configured** - Voice synthesis
- `RAMBLE_API_KEY` ✅ **Configured** - Voice services
- `ANTHROPIC_API_KEY` - Claude AI (optional)

#### 📞 **Communication Services**
- `TWILIO_ACCOUNT_SID` ✅ **Configured** - SMS/Voice calls
- `TWILIO_AUTH_TOKEN` ✅ **Configured** - Twilio authentication

#### 💳 **Payment Processing**
- `STRIPE_SECRET_KEY` ✅ **Configured** - Payment processing
- `STRIPE_WEBHOOK_SECRET` ✅ **Configured** - Payment webhooks
- `STRIPE_PUBLISHABLE_KEY` ✅ **Configured** - Frontend integration

#### 🌐 **Railway Production Services**
- `OVERVIEW_SERVICE_URL` ✅ **Deployed** - https://overview-production.up.railway.app
- `AGENTS_SERVICE_URL` ✅ **Deployed** - https://ai-agents-service-production.up.railway.app
- `CAMPAIGNS_SERVICE_URL` ✅ **Deployed** - https://smart-campaigns-production.up.railway.app
- `PHONE_NUMBERS_SERVICE_URL` ✅ **Deployed** - https://phone-numbers-production.up.railway.app
- `ANALYTICS_SERVICE_URL` ✅ **Deployed** - https://analytics-pro-production.up.railway.app
- `TEAM_HUB_SERVICE_URL` ✅ **Deployed** - https://team-hub-production.up.railway.app

## 🔧 **Deployment Instructions**

### 1. **Local Environment Setup**
```bash
# Copy production environment template
cp .env.production .env

# Install dependencies
pip install -r requirements.txt

# Start services locally for testing
python -m uvicorn apps.api-gateway.src.main:app --host 0.0.0.0 --port 8000
```

### 2. **Railway Deployment**
```bash
# Deploy individual services
cd apps/api-gateway && railway up
cd apps/overview && railway up
cd apps/smart-campaigns && railway up
cd apps/ai-agents-service && railway up
cd apps/phone-numbers && railway up
cd apps/team-hub && railway up
cd apps/analytics-pro && railway up
```

### 3. **Environment Variable Management**

#### **Railway Environment Variables**
Set these variables in Railway dashboard for each service:

**Critical Variables:**
- `OPENAI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `STRIPE_SECRET_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

#### **Security Best Practices**
- ✅ Never commit `.env` to version control
- ✅ Use Railway's environment variable system
- ✅ Rotate API keys regularly
- ✅ Use different keys for development/production

## 🧪 **Testing & Validation**

### **Health Check URLs**
- API Gateway: https://api-gateway-production-588d.up.railway.app/health
- Overview: https://overview-production.up.railway.app/health
- Smart Campaigns: https://smart-campaigns-production.up.railway.app/health
- AI Agents: https://ai-agents-service-production.up.railway.app/health
- Phone Numbers: https://phone-numbers-production.up.railway.app/health
- Team Hub: https://team-hub-production.up.railway.app/health
- Analytics Pro: https://analytics-pro-production.up.railway.app/health

### **API Documentation**
- API Gateway Docs: https://api-gateway-production-588d.up.railway.app/docs
- Service Discovery: All services auto-detected by API Gateway

## 🔍 **Monitoring & Logging**

### **Available Metrics**
- Service health status
- Response times
- Error rates
- Circuit breaker status
- Load balancing metrics

### **Logging Configuration**
- Log Level: `info`
- Format: `json`
- Prometheus metrics enabled on port 9090

## 🚨 **Troubleshooting**

### **Common Issues**
1. **Service Discovery Failures**
   - Check Railway service URLs in environment
   - Verify health endpoints responding
   
2. **Authentication Errors**
   - Validate JWT_SECRET_KEY configuration
   - Check API key permissions

3. **Database Connection Issues**
   - Verify SUPABASE_URL and SUPABASE_KEY
   - Check PostgreSQL connection string

### **Support Resources**
- Railway Documentation: https://docs.railway.app
- FastAPI Documentation: https://fastapi.tiangolo.com
- Service Health Dashboard: API Gateway `/health` endpoint

## ✅ **Production Readiness Checklist**

- ✅ All 6 microservices deployed to Railway
- ✅ API Gateway configured with production URLs
- ✅ Environment variables configured
- ✅ Health checks passing
- ✅ Service discovery working
- ✅ Authentication configured
- ✅ Payment processing ready
- ✅ AI services integrated
- ✅ Communication services active
- ✅ Monitoring enabled

**🎉 Your Vocelio.ai backend is production-ready!**
