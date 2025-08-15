# 🌐 RAILWAY CUSTOM DOMAIN SETUP GUIDE

## 🎯 **SETTING UP CUSTOM DOMAINS FOR YOUR VOCELIO SERVICES**

Transform your Railway URLs from generic to branded professional domains!

---

## 🏗️ **RECOMMENDED DOMAIN STRUCTURE**

```bash
# Frontend (Vercel)
app.vocelio.ai          → Your dashboard
www.vocelio.ai          → Marketing site
vocelio.ai              → Landing page

# Backend APIs (Railway)
api.vocelio.ai          → Main API Gateway
agents.vocelio.ai       → AI Agents Service  
campaigns.vocelio.ai    → Campaign Management
voice.vocelio.ai        → Voice Synthesis
calls.vocelio.ai        → Call Management
analytics.vocelio.ai    → Analytics & Reports
data.vocelio.ai         → Data Warehouse
```

---

## ⚡ **STEP-BY-STEP SETUP**

### **Step 1: Railway Dashboard Setup (Per Service)**

For each of your 25 Railway services:

1. **Login to Railway** → Go to your project
2. **Select a service** (e.g., ai-agents)  
3. **Click "Settings"** → "Domains" tab
4. **Click "Custom Domain"**
5. **Enter your subdomain**: `agents.vocelio.ai`
6. **Copy the CNAME value** (e.g., `ai-agents-production.up.railway.app`)

### **Step 2: DNS Configuration**

Add these CNAME records to your domain provider (Cloudflare/GoDaddy/Namecheap):

```dns
# Core Services
api             CNAME    api-gateway-production.up.railway.app
agents          CNAME    ai-agents-production.up.railway.app
campaigns       CNAME    campaigns-service-production.up.railway.app
voice           CNAME    voice-service-production.up.railway.app
calls           CNAME    call-service-production.up.railway.app
analytics       CNAME    analytics-service-production.up.railway.app
data            CNAME    data-warehouse-production-f093.up.railway.app

# Additional Services
auth            CNAME    auth-service-production.up.railway.app
billing         CNAME    billing-service-production.up.railway.app
leads           CNAME    lead-management-production.up.railway.app
notifications   CNAME    notifications-production.up.railway.app
schedule        CNAME    scheduling-production.up.railway.app
webhooks        CNAME    webhooks-production.up.railway.app
```

### **Step 3: SSL Certificate Setup**

Railway automatically provides SSL certificates for custom domains:
- ✅ **Free SSL** from Let's Encrypt
- ✅ **Auto-renewal** 
- ✅ **HTTPS redirect** enabled by default

---

## 🔧 **PRIORITY ORDER - START WITH THESE:**

### **Essential Services (Set up first):**
1. `api.vocelio.ai` → API Gateway
2. `agents.vocelio.ai` → AI Agents  
3. `campaigns.vocelio.ai` → Campaigns
4. `voice.vocelio.ai` → Voice Service
5. `analytics.vocelio.ai` → Analytics

### **Secondary Services (Set up later):**
6. `calls.vocelio.ai` → Call Management
7. `data.vocelio.ai` → Data Warehouse
8. `auth.vocelio.ai` → Authentication  
9. `billing.vocelio.ai` → Billing
10. `leads.vocelio.ai` → Lead Management

---

## 🎯 **BENEFITS OF CUSTOM DOMAINS**

✅ **Professional Branding**: `agents.vocelio.ai` vs `ai-agents-production.up.railway.app`
✅ **Better SEO**: Custom domains rank higher
✅ **Trust & Credibility**: Customers trust branded domains
✅ **Consistent Experience**: Matches your app.vocelio.ai frontend
✅ **Easier Integrations**: Simpler API endpoints for developers
✅ **Analytics Tracking**: Better domain-based analytics

---

## 🚀 **UPDATE YOUR FRONTEND**

After setting up domains, update your Vercel environment variables:

```bash
# Old Railway URLs
NEXT_PUBLIC_API_GATEWAY=https://api-gateway-production.up.railway.app

# New Custom Domains  
NEXT_PUBLIC_API_GATEWAY=https://api.vocelio.ai
NEXT_PUBLIC_AI_AGENTS_API=https://agents.vocelio.ai
NEXT_PUBLIC_CAMPAIGNS_API=https://campaigns.vocelio.ai
NEXT_PUBLIC_VOICE_API=https://voice.vocelio.ai
NEXT_PUBLIC_ANALYTICS_API=https://analytics.vocelio.ai
```

---

## 💡 **PRO TIPS**

1. **Start with API Gateway**: Set up `api.vocelio.ai` first
2. **Test Incrementally**: Verify each domain before moving to the next
3. **Keep Railway URLs**: As backup in case of DNS issues  
4. **Monitor SSL**: Check that HTTPS works for all domains
5. **Document Changes**: Update your API documentation

---

## 🧪 **TESTING YOUR DOMAINS**

```bash
# Test each domain after setup
curl https://api.vocelio.ai/health
curl https://agents.vocelio.ai/health  
curl https://campaigns.vocelio.ai/health
curl https://voice.vocelio.ai/health
curl https://analytics.vocelio.ai/health
```

---

## ⏱️ **ESTIMATED TIME**

- **DNS Propagation**: 15 minutes - 24 hours
- **SSL Certificate**: 5-15 minutes after DNS
- **Setup per service**: 2-3 minutes
- **Total for 10 services**: 30-45 minutes

---

## 🎉 **RESULT**

After setup, your API calls will look like:
```javascript
// Before: Generic Railway URLs
fetch('https://ai-agents-production.up.railway.app/agents')

// After: Branded Custom Domains  
fetch('https://agents.vocelio.ai/agents')
```

**Much more professional and trustworthy!** 🌟

---

## 🆘 **TROUBLESHOOTING**

If domains don't work:
1. **Check DNS propagation**: Use DNS checker tools
2. **Verify CNAME records**: Make sure they point to correct Railway URL
3. **Wait for SSL**: Can take up to 24 hours
4. **Check Railway logs**: For any configuration issues

**Ready to make your platform look enterprise-grade?** 🚀
