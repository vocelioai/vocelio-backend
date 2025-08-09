from fastapi import APIRouter, Depends, HTTPException
import structlog

from shared.auth.dependencies import get_current_user

router = APIRouter()
logger = structlog.get_logger()

@router.get("/", summary="Get brand configuration")
async def get_brand_config(current_user = Depends(get_current_user)):
    """Get current brand configuration."""
    return {
        "brand_id": "brand_123",
        "company_name": "Custom Voice Solutions",
        "logo_url": "https://cdn.vocelio.com/brands/brand_123/logo.png",
        "primary_color": "#2563eb",
        "secondary_color": "#1e40af", 
        "accent_color": "#3b82f6",
        "font_family": "Inter",
        "custom_css": ".custom-header { background: linear-gradient(45deg, #2563eb, #1e40af); }",
        "favicon_url": "https://cdn.vocelio.com/brands/brand_123/favicon.ico",
        "white_label_enabled": True,
        "custom_domain": "voice.customcompany.com",
        "email_templates": {
            "welcome": "custom_welcome_template",
            "invoice": "custom_invoice_template"
        }
    }

@router.put("/", summary="Update brand configuration")
async def update_brand_config(current_user = Depends(get_current_user)):
    """Update brand configuration."""
    return {
        "message": "Brand configuration updated successfully",
        "brand_id": "brand_123",
        "updated_fields": [
            "primary_color",
            "company_name",
            "custom_css"
        ],
        "cache_cleared": True,
        "propagation_status": "in_progress"
    }

@router.get("/preview", summary="Preview brand configuration")
async def preview_brand(current_user = Depends(get_current_user)):
    """Generate preview of brand configuration."""
    return {
        "preview_url": "https://preview.vocelio.com/brand_123",
        "expires_at": "2024-01-25T11:30:00Z",
        "preview_pages": [
            "dashboard",
            "call_interface", 
            "settings",
            "billing"
        ]
    }
