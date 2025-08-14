// DASHBOARD FIXES NEEDED

## 1. ADD MISSING API ENDPOINTS TO config.js

Add these to API_CONFIG:
```javascript
// Missing Services
AI_AGENT_PLATFORM: process.env.REACT_APP_AI_AGENT_PLATFORM_API || 'https://ai-agent-platform-production.up.railway.app',
UNIFIED_CAMPAIGNS: process.env.REACT_APP_UNIFIED_CAMPAIGNS_API || 'https://unified-campaigns-production.up.railway.app',
AGENTS: process.env.REACT_APP_AGENTS_API || 'https://agents-production.up.railway.app',
SCRIPTS: process.env.REACT_APP_SCRIPTS_API || 'https://scripts-production.up.railway.app',
OVERVIEW_SERVICE: process.env.REACT_APP_OVERVIEW_SERVICE_API || 'https://overview-service-production.up.railway.app',
```

## 2. ADD MISSING ROUTING CASES TO App.js

Add these cases to switch statement:
```javascript
case 'ai-agent-platform':
  return <AIAgentPlatform />;

case 'unified-campaigns':
  return <UnifiedCampaigns />;

case 'audit-compliance':
  return <AuditCompliance />;

case 'scripts-manager':
  return <ScriptsManager />; // Need to create this page

case 'overview-service':
  return <OverviewService />; // Need to create this page
```

## 3. ADD MISSING SIDEBAR ITEMS

Add to sidebarItems array:
```javascript
{ id: 'ai-agent-platform', label: 'AI Agent Platform', icon: Bot, badge: 'PLATFORM' },
{ id: 'unified-campaigns', label: 'Unified Campaigns', icon: Zap, badge: 'MULTI' },
{ id: 'audit-compliance', label: 'Audit & Compliance', icon: FileText, badge: 'NEW' },
{ id: 'scripts-manager', label: 'Scripts Manager', icon: Code, badge: 'UTILITY' },
```

## 4. CREATE MISSING PAGES

Need to create these page components:
- ScriptsManager.js
- OverviewService.js (if different from Overview)

## 5. UPDATE EXISTING PAGES

Fix these existing pages:
- UnifiedCampaigns.js - Connect to backend API
- AuditCompliance.js - Add proper routing
- AIAgentPlatform.js - Connect to backend API
