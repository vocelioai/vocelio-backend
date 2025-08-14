"""
🔄 OVERVIEW SERVICES INTEGRATION PLAN

## DECISION: Enhance `overview` and deprecate `overview-service`

RATIONALE:
- `overview` has superior architecture (microservice-ready)
- `overview-service` has some useful simple endpoints
- Better to enhance the enterprise service than downgrade

## INTEGRATION STEPS:

1. **Merge Endpoints**: Add simple endpoints from overview-service to overview
2. **Keep Best Architecture**: Use overview's enterprise structure
3. **Update Railway Config**: Point to unified overview service
4. **Update Dashboard Config**: Single overview API endpoint
5. **Deprecate overview-service**: Remove redundant service

## FILES TO MODIFY:

### 1. apps/overview/src/api/v1/endpoints/dashboard.py
ADD: Simple dashboard endpoints from overview-service

### 2. apps/overview/src/main.py  
ADD: Simple root endpoints for backward compatibility

### 3. vocelio-dashboard-main/src/lib/config.js
UPDATE: Remove OVERVIEW_SERVICE, keep only OVERVIEW

### 4. Railway Configuration
UPDATE: overview-service railway.toml → deprecated

### 5. Dashboard Routing
UPDATE: Use single overview service endpoint

## BENEFITS:
✅ Single source of truth for overview data
✅ Reduced infrastructure complexity  
✅ Better architecture (enterprise-ready)
✅ Backward compatibility maintained
✅ Easier maintenance and updates
"""
