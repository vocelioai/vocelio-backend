# 🚀 Connecting Railway Backend to Vercel Dashboard

## 🎯 Overview
You'll connect your **Railway backend** (with 20 microservices + dashboard integration) to your **Vercel frontend dashboard** using the API Gateway as the single entry point.

## 📋 Prerequisites Checklist

### ✅ Backend (Railway) - Already Complete
- **API Gateway**: `https://api-gateway-production-588d.up.railway.app`
- **Dashboard Integration**: All 8 endpoints implemented
- **20 Microservices**: All deployed and accessible
- **Authentication**: Bearer token system ready

### 🔧 Frontend (Vercel) - What You Need
- **Next.js/React Dashboard** deployed on Vercel
- **Environment Variables** configured
- **API Client** setup for backend communication

---

## 🔗 Step 1: Configure API Base URL

### In Your Vercel Dashboard Project

**File: `.env.local` (for local development)**
```bash
# Railway Backend API Gateway
NEXT_PUBLIC_API_BASE_URL=https://api-gateway-production-588d.up.railway.app
NEXT_PUBLIC_API_VERSION=v1

# Dashboard Endpoints
NEXT_PUBLIC_OVERVIEW_SERVICE=overview
NEXT_PUBLIC_AGENT_STORE_SERVICE=agent-store

# Authentication (for now - replace with real JWT later)
NEXT_PUBLIC_AUTH_TOKEN=test-token
```

**File: `vercel.json` (for production environment)**
```json
{
  "env": {
    "NEXT_PUBLIC_API_BASE_URL": "https://api-gateway-production-588d.up.railway.app",
    "NEXT_PUBLIC_API_VERSION": "v1",
    "NEXT_PUBLIC_OVERVIEW_SERVICE": "overview", 
    "NEXT_PUBLIC_AGENT_STORE_SERVICE": "agent-store",
    "NEXT_PUBLIC_AUTH_TOKEN": "test-token"
  }
}
```

---

## 🛠 Step 2: Create API Client

**File: `lib/api-client.js` (or `.ts` for TypeScript)**
```javascript
// API Client for Railway Backend
class VocelioAPIClient {
  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;
    this.apiVersion = process.env.NEXT_PUBLIC_API_VERSION;
    this.authToken = process.env.NEXT_PUBLIC_AUTH_TOKEN;
  }

  // Generic API request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.authToken}`,
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Dashboard Overview Methods
  async getDashboardOverview() {
    return this.request(`/api/overview/${this.apiVersion}/integration/overview`);
  }

  async getDashboardAnalytics() {
    return this.request(`/api/overview/${this.apiVersion}/integration/analytics`);
  }

  async getServiceHealth() {
    return this.request(`/api/overview/${this.apiVersion}/integration/services/health`);
  }

  async getRecentActivity() {
    return this.request(`/api/overview/${this.apiVersion}/integration/recent-activity`);
  }

  async getNotifications() {
    return this.request(`/api/overview/${this.apiVersion}/integration/notifications`);
  }

  async getKPIs() {
    return this.request(`/api/overview/${this.apiVersion}/integration/kpis`);
  }

  // Agent Store Methods
  async getFeaturedAgents() {
    return this.request(`/api/agent-store/${this.apiVersion}/dashboard/featured`);
  }

  async getAgentCategories() {
    return this.request(`/api/agent-store/${this.apiVersion}/dashboard/categories`);
  }

  async getMarketplaceAnalytics() {
    return this.request(`/api/agent-store/${this.apiVersion}/dashboard/analytics`);
  }

  async getTrendingAgents() {
    return this.request(`/api/agent-store/${this.apiVersion}/dashboard/marketplace/trending`);
  }
}

// Export singleton instance
export const apiClient = new VocelioAPIClient();
export default apiClient;
```

---

## 📊 Step 3: Create Dashboard Components

### Main Dashboard Component
**File: `components/Dashboard/MainDashboard.jsx`**
```jsx
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

export default function MainDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Parallel fetch for better performance
      const [overview, analytics, health, activity] = await Promise.all([
        apiClient.getDashboardOverview(),
        apiClient.getDashboardAnalytics(), 
        apiClient.getServiceHealth(),
        apiClient.getRecentActivity()
      ]);

      setDashboardData({
        overview: overview.data,
        analytics: analytics.data,
        health: health.data,
        activity: activity.data
      });
    } catch (err) {
      setError(err.message);
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <DashboardSkeleton />;
  if (error) return <ErrorDisplay error={error} onRetry={loadDashboardData} />;

  return (
    <div className="dashboard-container">
      {/* Overview Stats */}
      <div className="stats-grid">
        <StatCard 
          title="Total Calls" 
          value={dashboardData.overview?.total_calls} 
          trend="+12%" 
        />
        <StatCard 
          title="Active Agents" 
          value={dashboardData.overview?.active_agents} 
          trend="+5%" 
        />
        <StatCard 
          title="Success Rate" 
          value={`${dashboardData.overview?.success_rate}%`} 
          trend="+2.1%" 
        />
        <StatCard 
          title="Revenue Today" 
          value={`$${dashboardData.overview?.revenue_today}`} 
          trend="+18%" 
        />
      </div>

      {/* Service Health */}
      <ServiceHealthPanel services={dashboardData.health?.services} />

      {/* Recent Activity */}
      <ActivityFeed activities={dashboardData.activity?.recent_activity} />

      {/* Analytics Charts */}
      <AnalyticsCharts data={dashboardData.analytics} />
    </div>
  );
}
```

### Agent Store Component
**File: `components/Dashboard/AgentStore.jsx`**
```jsx
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

export default function AgentStoreDashboard() {
  const [storeData, setStoreData] = useState(null);

  useEffect(() => {
    loadStoreData();
  }, []);

  const loadStoreData = async () => {
    try {
      const [featured, categories, analytics, trending] = await Promise.all([
        apiClient.getFeaturedAgents(),
        apiClient.getAgentCategories(),
        apiClient.getMarketplaceAnalytics(),
        apiClient.getTrendingAgents()
      ]);

      setStoreData({
        featured: featured.data.featured_agents,
        categories: categories.data.categories,
        analytics: analytics.data,
        trending: trending.data.trending_agents
      });
    } catch (error) {
      console.error('Store data load error:', error);
    }
  };

  return (
    <div className="agent-store-dashboard">
      {/* Featured Agents */}
      <FeaturedAgents agents={storeData?.featured} />
      
      {/* Categories Overview */}
      <CategoriesGrid categories={storeData?.categories} />
      
      {/* Marketplace Analytics */}
      <MarketplaceMetrics analytics={storeData?.analytics} />
      
      {/* Trending Agents */}
      <TrendingSection agents={storeData?.trending} />
    </div>
  );
}
```

---

## 🔄 Step 4: Real-time Updates (Optional)

**For live dashboard updates, add WebSocket or polling:**

```javascript
// Real-time updates with polling
export function useRealTimeDashboard(interval = 30000) {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const overview = await apiClient.getDashboardOverview();
        setData(overview.data);
      } catch (error) {
        console.error('Real-time update failed:', error);
      }
    };

    // Initial fetch
    fetchData();

    // Set up polling
    const intervalId = setInterval(fetchData, interval);

    return () => clearInterval(intervalId);
  }, [interval]);

  return data;
}
```

---

## 🚀 Step 5: Deploy to Vercel

### 1. **Environment Variables in Vercel Dashboard**
Go to your Vercel project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_BASE_URL = https://api-gateway-production-588d.up.railway.app
NEXT_PUBLIC_API_VERSION = v1
NEXT_PUBLIC_OVERVIEW_SERVICE = overview
NEXT_PUBLIC_AGENT_STORE_SERVICE = agent-store
NEXT_PUBLIC_AUTH_TOKEN = test-token
```

### 2. **Deploy Command**
```bash
# From your frontend repository
vercel --prod
```

### 3. **Custom Domain (Optional)**
- Add your custom domain in Vercel
- Update CORS settings in Railway if needed

---

## 🧪 Step 6: Test Connection

### Test API Connection
**File: `pages/api/test-connection.js`**
```javascript
import { apiClient } from '@/lib/api-client';

export default async function handler(req, res) {
  try {
    const overview = await apiClient.getDashboardOverview();
    res.status(200).json({ 
      success: true, 
      message: 'Railway backend connected successfully!',
      data: overview 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
}
```

**Test URL**: `https://your-vercel-app.vercel.app/api/test-connection`

---

## 🔒 Step 7: Add Authentication (Production)

### Replace Test Token with Real JWT
```javascript
// Enhanced API client with JWT
class AuthenticatedAPIClient extends VocelioAPIClient {
  async authenticate(credentials) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
    
    // Store JWT token
    localStorage.setItem('auth_token', response.token);
    this.authToken = response.token;
  }

  async request(endpoint, options = {}) {
    // Check token expiry and refresh if needed
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.authToken = token;
    }
    
    return super.request(endpoint, options);
  }
}
```

---

## 🎯 Quick Start Commands

### 1. **Test Backend Connection (Right Now)**
```bash
curl "https://api-gateway-production-588d.up.railway.app/" 
```

### 2. **Test Dashboard Endpoint**
```bash
curl "https://api-gateway-production-588d.up.railway.app/api/overview/v1/integration/overview" \
  -H "Authorization: Bearer test-token"
```

### 3. **Add to Your Frontend Package.json**
```json
{
  "scripts": {
    "test-backend": "curl https://api-gateway-production-588d.up.railway.app/",
    "dev": "next dev",
    "build": "next build",
    "deploy": "vercel --prod"
  }
}
```

---

## 🏆 Success Checklist

- ✅ **Environment variables** configured in Vercel
- ✅ **API client** created and tested
- ✅ **Dashboard components** built with Railway data
- ✅ **Error handling** implemented
- ✅ **Real-time updates** (optional) configured
- ✅ **Production deployment** to Vercel completed

## 🎉 Final Result

Your Vercel dashboard will now display:
- **Real-time call metrics** from your Railway backend
- **Service health status** across all 20 microservices  
- **Agent marketplace data** with live analytics
- **Activity feeds** and notifications
- **Performance KPIs** and business insights

**Your Dashboard URL**: `https://your-project.vercel.app`
**Your Backend API**: `https://api-gateway-production-588d.up.railway.app`

You now have a **world-class AI call center dashboard** with Railway backend + Vercel frontend! 🚀
