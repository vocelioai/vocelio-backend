# apps/developer-api/src/api/v1/endpoints/keys.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def list_api_keys(organization_id: str):
    """List all API keys for organization"""
    
    # Mock API keys data
    api_keys = [
        {
            "id": "key_live_abc123def456",
            "name": "Production API Key",
            "prefix": "voc_live_",
            "created": "2025-07-15T10:30:00Z",
            "last_used": "2025-08-09T14:22:00Z",
            "permissions": ["calls:read", "calls:write", "agents:read", "campaigns:read"],
            "rate_limit": 10000,
            "environment": "live",
            "status": "active"
        },
        {
            "id": "key_test_xyz789ghi012",
            "name": "Development API Key", 
            "prefix": "voc_test_",
            "created": "2025-07-10T09:15:00Z",
            "last_used": "2025-08-09T12:05:00Z",
            "permissions": ["*"],
            "rate_limit": 1000,
            "environment": "test",
            "status": "active"
        }
    ]
    
    return {
        "api_keys": api_keys,
        "total_count": len(api_keys),
        "organization_id": organization_id
    }

@router.post("/")
async def create_api_key(
    organization_id: str,
    name: str,
    permissions: List[str],
    environment: str = "test",
    rate_limit: int = 1000
):
    """Create new API key"""
    
    # Generate secure API key
    prefix = f"voc_{environment}_"
    key_part = secrets.token_urlsafe(32)
    api_key = f"{prefix}{key_part}"
    
    new_key = {
        "id": f"key_{environment}_{secrets.token_hex(8)}",
        "name": name,
        "key": api_key,  # Only shown once during creation
        "prefix": prefix,
        "created": datetime.utcnow().isoformat(),
        "last_used": None,
        "permissions": permissions,
        "rate_limit": rate_limit,
        "environment": environment,
        "status": "active"
    }
    
    return {
        "message": "API key created successfully",
        "api_key": new_key,
        "warning": "Save this key now. You won't be able to see it again."
    }

@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    organization_id: str
):
    """Revoke API key"""
    
    return {
        "message": "API key revoked successfully",
        "key_id": key_id,
        "revoked_at": datetime.utcnow().isoformat()
    }

@router.get("/{key_id}/usage")
async def get_api_key_usage(
    key_id: str,
    days: int = 30
):
    """Get API key usage statistics"""
    
    # Mock usage data
    usage_data = {
        "key_id": key_id,
        "period_days": days,
        "total_requests": 45690,
        "successful_requests": 45234,
        "failed_requests": 456,
        "rate_limited_requests": 23,
        "average_daily_requests": 1523,
        "peak_requests_per_hour": 234,
        "endpoints_used": [
            {
                "endpoint": "/api/v1/calls",
                "requests": 15690,
                "percentage": 34.4
            },
            {
                "endpoint": "/api/v1/agents",
                "requests": 12340,
                "percentage": 27.0
            },
            {
                "endpoint": "/api/v1/campaigns",
                "requests": 9870,
                "percentage": 21.6
            }
        ],
        "daily_breakdown": [
            {"date": "2025-08-01", "requests": 1456},
            {"date": "2025-08-02", "requests": 1678},
            {"date": "2025-08-03", "requests": 1534},
            {"date": "2025-08-04", "requests": 1789},
            {"date": "2025-08-05", "requests": 1623},
            {"date": "2025-08-06", "requests": 1890},
            {"date": "2025-08-07", "requests": 1834}
        ]
    }
    
    return usage_data
