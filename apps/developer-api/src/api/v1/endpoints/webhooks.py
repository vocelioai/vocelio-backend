# apps/developer-api/src/api/v1/endpoints/webhooks.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def list_webhooks(organization_id: str):
    """List all configured webhooks"""
    
    webhooks = [
        {
            "id": "wh_001",
            "name": "Call Events Webhook",
            "url": "https://yourapp.com/webhooks/vocelio/calls",
            "events": ["call.started", "call.completed", "call.failed"],
            "status": "active",
            "created": "2025-07-15T10:30:00Z",
            "last_delivery": "2025-08-09T14:22:00Z",
            "success_rate": 98.5,
            "total_deliveries": 1234
        },
        {
            "id": "wh_002", 
            "name": "Campaign Updates",
            "url": "https://yourapp.com/webhooks/vocelio/campaigns",
            "events": ["campaign.started", "campaign.completed", "campaign.paused"],
            "status": "active",
            "created": "2025-07-20T14:45:00Z",
            "last_delivery": "2025-08-09T13:15:00Z", 
            "success_rate": 97.2,
            "total_deliveries": 567
        }
    ]
    
    return {
        "webhooks": webhooks,
        "total_count": len(webhooks),
        "organization_id": organization_id
    }

@router.post("/")
async def create_webhook(
    organization_id: str,
    name: str,
    url: str,
    events: List[str],
    secret: Optional[str] = None
):
    """Create new webhook"""
    
    if not secret:
        secret = f"whsec_{secrets.token_urlsafe(32)}"
    
    webhook = {
        "id": f"wh_{secrets.token_hex(8)}",
        "name": name,
        "url": url,
        "events": events,
        "secret": secret,
        "status": "active",
        "created": datetime.utcnow().isoformat(),
        "last_delivery": None,
        "success_rate": 0,
        "total_deliveries": 0
    }
    
    return {
        "message": "Webhook created successfully",
        "webhook": webhook
    }

@router.get("/events")
async def list_available_events():
    """List all available webhook events"""
    
    events = {
        "call_events": [
            "call.started",
            "call.answered", 
            "call.completed",
            "call.failed",
            "call.transferred",
            "call.recording_available"
        ],
        "campaign_events": [
            "campaign.created",
            "campaign.started",
            "campaign.paused",
            "campaign.completed",
            "campaign.deleted"
        ],
        "agent_events": [
            "agent.created",
            "agent.updated",
            "agent.trained",
            "agent.deleted"
        ],
        "billing_events": [
            "invoice.created",
            "invoice.paid",
            "invoice.failed",
            "subscription.created",
            "subscription.cancelled"
        ]
    }
    
    return events

@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: str,
    limit: int = 50
):
    """Get webhook delivery history"""
    
    deliveries = [
        {
            "id": "del_001",
            "event_type": "call.completed",
            "delivered_at": "2025-08-09T14:22:00Z",
            "status": "success",
            "response_code": 200,
            "response_time_ms": 234,
            "attempts": 1,
            "payload_size": 1024
        },
        {
            "id": "del_002",
            "event_type": "call.started", 
            "delivered_at": "2025-08-09T14:20:00Z",
            "status": "success",
            "response_code": 200,
            "response_time_ms": 189,
            "attempts": 1,
            "payload_size": 896
        },
        {
            "id": "del_003",
            "event_type": "call.failed",
            "delivered_at": "2025-08-09T14:15:00Z",
            "status": "failed",
            "response_code": 500,
            "response_time_ms": 5000,
            "attempts": 3,
            "payload_size": 567,
            "error": "Internal Server Error"
        }
    ]
    
    return {
        "deliveries": deliveries[:limit],
        "total_count": len(deliveries),
        "webhook_id": webhook_id
    }

@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    event_type: str = "test.webhook"
):
    """Send test webhook delivery"""
    
    test_payload = {
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "test": True,
            "webhook_id": webhook_id,
            "message": "This is a test webhook delivery"
        }
    }
    
    return {
        "message": "Test webhook sent successfully",
        "webhook_id": webhook_id,
        "test_payload": test_payload,
        "delivery_id": f"del_test_{secrets.token_hex(6)}"
    }
