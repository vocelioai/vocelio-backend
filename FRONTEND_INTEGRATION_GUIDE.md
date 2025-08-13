# 🚀 Vocelio.ai Frontend Integration Guide

## Complete guide for integrating your 31 Railway services with Next.js dashboard

### 📋 Table of Contents
1. [Environment Setup](#environment-setup)
2. [Frontend Configuration](#frontend-configuration)
3. [API Client Setup](#api-client-setup)
4. [Service Integration](#service-integration)
5. [Authentication Integration](#authentication-integration)
6. [Dashboard Components](#dashboard-components)
7. [Enterprise Features](#enterprise-features)
8. [Deployment](#deployment)

---

## 🔧 Environment Setup

### 1. Copy Environment Variables to Your Frontend

**For Next.js (Recommended):**
```bash
# Copy the enterprise environment file
cp .env.vercel.enterprise your-frontend-project/.env.local

# Or copy individual variables to your Vercel dashboard
```

**For React/Vue/Angular:**
```bash
# Use the standard vercel file and adapt variable names
cp .env.vercel your-frontend-project/.env
```

### 2. Install Required Dependencies

```bash
# Core HTTP client
npm install axios

# Authentication
npm install @auth0/nextjs-auth0  # or your preferred auth library

# State management
npm install @tanstack/react-query  # for data fetching
npm install zustand  # for state management

# UI Components (optional)
npm install @headlessui/react @heroicons/react
npm install tailwindcss  # for styling
```

---

## 🌐 Frontend Configuration

### 1. Create API Configuration File

```typescript
// lib/config.ts
export const API_CONFIG = {
  // Core Services
  OVERVIEW: process.env.NEXT_PUBLIC_OVERVIEW_API || 'https://overview-production.up.railway.app',
  ANALYTICS: process.env.NEXT_PUBLIC_ANALYTICS_API || 'https://analytics-pro-production.up.railway.app',
  TEAM_HUB: process.env.NEXT_PUBLIC_TEAM_HUB_API || 'https://team-hub-production.up.railway.app',
  
  // Enterprise Services
  SSO_IDENTITY: process.env.NEXT_PUBLIC_SSO_IDENTITY_API || 'https://sso-identity-production.up.railway.app',
  API_MANAGEMENT: process.env.NEXT_PUBLIC_API_MANAGEMENT_API || 'https://api-management-production.up.railway.app',
  ENTERPRISE_SECURITY: process.env.NEXT_PUBLIC_ENTERPRISE_SECURITY_API || 'https://enterprise-security-production.up.railway.app',
  AUDIT_COMPLIANCE: process.env.NEXT_PUBLIC_AUDIT_COMPLIANCE_API || 'https://audit-compliance-production.up.railway.app',
  
  // AI Services
  AI_AGENTS: process.env.NEXT_PUBLIC_AGENTS_API || 'https://ai-agents-service-production.up.railway.app',
  AI_BRAIN: process.env.NEXT_PUBLIC_AI_BRAIN_API || 'https://ai-brain-production.up.railway.app',
  VOICE_LAB: process.env.NEXT_PUBLIC_VOICE_LAB_API || 'https://voice-lab-production.up.railway.app',
  SMART_CAMPAIGNS: process.env.NEXT_PUBLIC_CAMPAIGNS_API || 'https://smart-campaigns-production.up.railway.app',
  
  // Communication Services
  CALL_CENTER: process.env.NEXT_PUBLIC_CALL_CENTER_API || 'https://call-center-production.up.railway.app',
  PHONE_NUMBERS: process.env.NEXT_PUBLIC_PHONE_NUMBERS_API || 'https://phone-numbers-production.up.railway.app',
  NOTIFICATIONS: process.env.NEXT_PUBLIC_NOTIFICATIONS_API || 'https://notifications-production.up.railway.app',
  
  // Business Services
  BILLING: process.env.NEXT_PUBLIC_BILLING_API || 'https://billing-pro-production.up.railway.app',
  LEAD_MANAGEMENT: process.env.NEXT_PUBLIC_LEAD_MANAGEMENT_API || 'https://lead-management-production.up.railway.app',
  SCHEDULING: process.env.NEXT_PUBLIC_SCHEDULING_API || 'https://scheduling-production.up.railway.app',
  
  // Main API Gateway
  API_GATEWAY: process.env.NEXT_PUBLIC_API_GATEWAY || 'https://api-gateway-production-588d.up.railway.app',
}

export const API_SETTINGS = {
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  VERSION: 'v1',
}
```

### 2. Create HTTP Client

```typescript
// lib/api-client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { API_CONFIG, API_SETTINGS } from './config'

class ApiClient {
  private client: AxiosInstance

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: API_SETTINGS.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  private getAuthToken(): string | null {
    // Get token from localStorage, cookies, or your auth provider
    return localStorage.getItem('auth_token')
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config)
    return response.data
  }
}

// Create service clients
export const overviewApi = new ApiClient(API_CONFIG.OVERVIEW)
export const analyticsApi = new ApiClient(API_CONFIG.ANALYTICS)
export const teamHubApi = new ApiClient(API_CONFIG.TEAM_HUB)
export const ssoApi = new ApiClient(API_CONFIG.SSO_IDENTITY)
export const aiAgentsApi = new ApiClient(API_CONFIG.AI_AGENTS)
export const billingApi = new ApiClient(API_CONFIG.BILLING)
// ... add more as needed
```

---

## 🔐 Authentication Integration

### 1. SSO Authentication Hook

```typescript
// hooks/useAuth.ts
import { useState, useEffect } from 'react'
import { ssoApi } from '../lib/api-client'

interface User {
  id: string
  email: string
  name: string
  tenantId: string
  permissions: string[]
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  })

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setAuthState({ user: null, isLoading: false, isAuthenticated: false })
        return
      }

      const user = await ssoApi.get<User>('/auth/me')
      setAuthState({ user, isLoading: false, isAuthenticated: true })
    } catch (error) {
      localStorage.removeItem('auth_token')
      setAuthState({ user: null, isLoading: false, isAuthenticated: false })
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await ssoApi.post<{ access_token: string; user: User }>('/auth/login', {
        username: email,
        password,
      })

      localStorage.setItem('auth_token', response.access_token)
      setAuthState({ user: response.user, isLoading: false, isAuthenticated: true })
      
      return { success: true }
    } catch (error: any) {
      return { success: false, error: error.response?.data?.message || 'Login failed' }
    }
  }

  const logout = async () => {
    try {
      await ssoApi.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('auth_token')
      setAuthState({ user: null, isLoading: false, isAuthenticated: false })
    }
  }

  return {
    ...authState,
    login,
    logout,
    refetch: checkAuthStatus,
  }
}
```

### 2. Protected Route Component

```typescript
// components/ProtectedRoute.tsx
import { ReactNode } from 'react'
import { useAuth } from '../hooks/useAuth'
import { LoadingSpinner } from './LoadingSpinner'
import { LoginForm } from './LoginForm'

interface ProtectedRouteProps {
  children: ReactNode
  requiredPermissions?: string[]
}

export const ProtectedRoute = ({ children, requiredPermissions = [] }: ProtectedRouteProps) => {
  const { isLoading, isAuthenticated, user } = useAuth()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return <LoginForm />
  }

  // Check permissions
  if (requiredPermissions.length > 0 && user) {
    const hasPermission = requiredPermissions.every(permission =>
      user.permissions.includes(permission)
    )
    
    if (!hasPermission) {
      return <div>Access denied. Insufficient permissions.</div>
    }
  }

  return <>{children}</>
}
```

---

## 📊 Dashboard Components

### 1. Overview Dashboard

```typescript
// components/OverviewDashboard.tsx
import { useQuery } from '@tanstack/react-query'
import { overviewApi } from '../lib/api-client'

interface DashboardStats {
  totalAgents: number
  activeCalls: number
  monthlyRevenue: number
  systemHealth: 'healthy' | 'warning' | 'critical'
}

export const OverviewDashboard = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => overviewApi.get<DashboardStats>('/dashboard/stats'),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) return <div>Loading dashboard...</div>
  if (error) return <div>Error loading dashboard</div>

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">Total Agents</h3>
        <p className="text-3xl font-bold text-blue-600">{stats?.totalAgents}</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">Active Calls</h3>
        <p className="text-3xl font-bold text-green-600">{stats?.activeCalls}</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">Monthly Revenue</h3>
        <p className="text-3xl font-bold text-purple-600">
          ${stats?.monthlyRevenue?.toLocaleString()}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">System Health</h3>
        <p className={`text-3xl font-bold ${
          stats?.systemHealth === 'healthy' ? 'text-green-600' :
          stats?.systemHealth === 'warning' ? 'text-yellow-600' : 'text-red-600'
        }`}>
          {stats?.systemHealth?.toUpperCase()}
        </p>
      </div>
    </div>
  )
}
```

### 2. Analytics Component

```typescript
// components/Analytics.tsx
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../lib/api-client'
import { LineChart, BarChart } from 'recharts' // or your preferred chart library

interface AnalyticsData {
  usage: Array<{ date: string; requests: number; errors: number }>
  topServices: Array<{ name: string; requests: number }>
  performance: Array<{ service: string; avgResponseTime: number }>
}

export const Analytics = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => analyticsApi.get<AnalyticsData>('/analytics/dashboard'),
    refetchInterval: 60000, // Refresh every minute
  })

  if (isLoading) return <div>Loading analytics...</div>

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">API Usage Trends</h3>
        <LineChart width={800} height={300} data={data?.usage}>
          {/* Add chart components */}
        </LineChart>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">Top Services</h3>
          <BarChart width={400} height={300} data={data?.topServices}>
            {/* Add chart components */}
          </BarChart>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">Performance Metrics</h3>
          <div className="space-y-2">
            {data?.performance?.map((metric) => (
              <div key={metric.service} className="flex justify-between">
                <span>{metric.service}</span>
                <span className="font-mono">{metric.avgResponseTime}ms</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 3. AI Agents Management

```typescript
// components/AIAgentsManager.tsx
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { aiAgentsApi } from '../lib/api-client'

interface Agent {
  id: string
  name: string
  type: string
  status: 'active' | 'inactive' | 'training'
  capabilities: string[]
  createdAt: string
}

export const AIAgentsManager = () => {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const queryClient = useQueryClient()

  const { data: agents, isLoading } = useQuery({
    queryKey: ['ai-agents'],
    queryFn: () => aiAgentsApi.get<Agent[]>('/agents'),
  })

  const createAgentMutation = useMutation({
    mutationFn: (newAgent: Omit<Agent, 'id' | 'createdAt'>) =>
      aiAgentsApi.post<Agent>('/agents', newAgent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-agents'] })
    },
  })

  const deployAgentMutation = useMutation({
    mutationFn: (agentId: string) =>
      aiAgentsApi.post(`/agents/${agentId}/deploy`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-agents'] })
    },
  })

  if (isLoading) return <div>Loading agents...</div>

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Agent List */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h3 className="text-xl font-semibold">AI Agents</h3>
            <button
              onClick={() => {/* Open create modal */}}
              className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Create New Agent
            </button>
          </div>
          
          <div className="divide-y">
            {agents?.map((agent) => (
              <div
                key={agent.id}
                className="p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedAgent(agent)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-semibold">{agent.name}</h4>
                    <p className="text-sm text-gray-600">{agent.type}</p>
                    <div className="flex gap-2 mt-2">
                      {agent.capabilities.map((cap) => (
                        <span
                          key={cap}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                        >
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <span className={`px-2 py-1 text-xs rounded ${
                      agent.status === 'active' ? 'bg-green-100 text-green-800' :
                      agent.status === 'training' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {agent.status}
                    </span>
                    
                    {agent.status === 'inactive' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deployAgentMutation.mutate(agent.id)
                        }}
                        className="ml-2 bg-green-600 text-white px-3 py-1 text-xs rounded hover:bg-green-700"
                        disabled={deployAgentMutation.isPending}
                      >
                        Deploy
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Agent Details */}
      <div className="bg-white rounded-lg shadow p-6">
        {selectedAgent ? (
          <div>
            <h3 className="text-xl font-semibold mb-4">Agent Details</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <p className="text-sm">{selectedAgent.name}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <p className="text-sm">{selectedAgent.type}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Status</label>
                <p className="text-sm">{selectedAgent.status}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Created</label>
                <p className="text-sm">{new Date(selectedAgent.createdAt).toLocaleDateString()}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500">
            Select an agent to view details
          </div>
        )}
      </div>
    </div>
  )
}
```

---

## 🏢 Enterprise Features Integration

### 1. Multi-Tenant Context

```typescript
// context/TenantContext.tsx
import { createContext, useContext, ReactNode } from 'react'
import { useAuth } from '../hooks/useAuth'

interface TenantContextType {
  tenantId: string | null
  tenantName: string | null
  isEnterprise: boolean
}

const TenantContext = createContext<TenantContextType | undefined>(undefined)

export const TenantProvider = ({ children }: { children: ReactNode }) => {
  const { user } = useAuth()
  
  const contextValue: TenantContextType = {
    tenantId: user?.tenantId || null,
    tenantName: user?.tenantName || null,
    isEnterprise: user?.plan === 'enterprise' || false,
  }

  return (
    <TenantContext.Provider value={contextValue}>
      {children}
    </TenantContext.Provider>
  )
}

export const useTenant = () => {
  const context = useContext(TenantContext)
  if (!context) {
    throw new Error('useTenant must be used within TenantProvider')
  }
  return context
}
```

### 2. Audit Logging Hook

```typescript
// hooks/useAudit.ts
import { useMutation } from '@tanstack/react-query'
import { API_CONFIG } from '../lib/config'
import axios from 'axios'

interface AuditEvent {
  action: string
  resource: string
  resourceId?: string
  metadata?: Record<string, any>
}

export const useAudit = () => {
  const auditClient = axios.create({
    baseURL: API_CONFIG.AUDIT_COMPLIANCE,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
    },
  })

  const logEventMutation = useMutation({
    mutationFn: (event: AuditEvent) =>
      auditClient.post('/audit/events', event),
    onError: (error) => {
      console.error('Audit logging failed:', error)
    },
  })

  const logEvent = (event: AuditEvent) => {
    logEventMutation.mutate({
      ...event,
      timestamp: new Date().toISOString(),
    })
  }

  return { logEvent }
}
```

---

## 🚀 Main App Layout

```typescript
// app/layout.tsx (Next.js App Router)
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TenantProvider } from '../context/TenantContext'
import { Sidebar } from '../components/Sidebar'
import { Header } from '../components/Header'
import { useState } from 'react'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 3,
    },
  },
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <QueryClientProvider client={queryClient}>
          <TenantProvider>
            <div className="flex h-screen bg-gray-100">
              <Sidebar />
              <div className="flex-1 flex flex-col overflow-hidden">
                <Header />
                <main className="flex-1 overflow-auto p-6">
                  {children}
                </main>
              </div>
            </div>
          </TenantProvider>
        </QueryClientProvider>
      </body>
    </html>
  )
}
```

### Page Examples

```typescript
// app/dashboard/page.tsx
import { ProtectedRoute } from '../../components/ProtectedRoute'
import { OverviewDashboard } from '../../components/OverviewDashboard'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <OverviewDashboard />
    </ProtectedRoute>
  )
}

// app/agents/page.tsx
import { ProtectedRoute } from '../../components/ProtectedRoute'
import { AIAgentsManager } from '../../components/AIAgentsManager'

export default function AgentsPage() {
  return (
    <ProtectedRoute requiredPermissions={['agents:read', 'agents:write']}>
      <AIAgentsManager />
    </ProtectedRoute>
  )
}

// app/analytics/page.tsx
import { ProtectedRoute } from '../../components/ProtectedRoute'
import { Analytics } from '../../components/Analytics'

export default function AnalyticsPage() {
  return (
    <ProtectedRoute requiredPermissions={['analytics:read']}>
      <Analytics />
    </ProtectedRoute>
  )
}
```

---

## 📦 Deployment

### 1. Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard or via CLI
vercel env add NEXT_PUBLIC_OVERVIEW_API
vercel env add NEXT_PUBLIC_SSO_IDENTITY_API
# ... add all other environment variables from .env.vercel.enterprise
```

### 2. Environment Variables Setup

**Copy these to your Vercel project:**
```bash
# From your .env.vercel.enterprise file
NEXT_PUBLIC_OVERVIEW_API=https://overview-production.up.railway.app
NEXT_PUBLIC_SSO_IDENTITY_API=https://sso-identity-production.up.railway.app
NEXT_PUBLIC_API_MANAGEMENT_API=https://api-management-production.up.railway.app
# ... (all 31 service URLs)
```

### 3. Build Configuration

```json
// package.json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  }
}
```

---

## 🎯 Quick Start Commands

```bash
# 1. Create new Next.js project
npx create-next-app@latest vocelio-dashboard --typescript --tailwind --app

# 2. Install dependencies
cd vocelio-dashboard
npm install axios @tanstack/react-query zustand

# 3. Copy environment variables
cp ../vocelio-backend/.env.vercel.enterprise ./.env.local

# 4. Create the files above in your project structure

# 5. Start development server
npm run dev
```

---

## 🔗 API Endpoints Reference

All your services are accessible at:
- **Main Gateway**: `https://api-gateway-production-588d.up.railway.app`
- **Documentation**: `https://api-gateway-production-588d.up.railway.app/docs`
- **Health Check**: `https://[service-url]/health`

### Common API Patterns:
```typescript
// GET requests
const data = await serviceApi.get('/endpoint')

// POST requests
const result = await serviceApi.post('/endpoint', payload)

// With authentication
const authResult = await ssoApi.post('/auth/login', { username, password })
```

---

## ✅ Your Integration Checklist

- [ ] Copy environment variables to frontend project
- [ ] Install required dependencies
- [ ] Set up API client configuration
- [ ] Implement authentication with SSO service
- [ ] Create protected routes
- [ ] Build dashboard components
- [ ] Add analytics integration
- [ ] Implement audit logging
- [ ] Test all service connections
- [ ] Deploy to Vercel
- [ ] Configure production environment variables

**🚀 Your Vocelio.ai dashboard is now ready to integrate with all 31 enterprise services!**
