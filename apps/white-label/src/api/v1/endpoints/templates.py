from fastapi import APIRouter, Depends
import structlog

from shared.auth.dependencies import get_current_user

router = APIRouter()
logger = structlog.get_logger()

@router.get("/", summary="Get available templates")
async def get_templates(current_user = Depends(get_current_user)):
    """Get list of available white-label templates."""
    return {
        "templates": [
            {
                "id": "template_modern",
                "name": "Modern Dashboard",
                "description": "Clean, modern interface with card-based layout",
                "category": "dashboard",
                "preview_url": "https://preview.vocelio.com/templates/modern",
                "customizable_elements": [
                    "colors", "typography", "layout", "components"
                ]
            },
            {
                "id": "template_corporate",
                "name": "Corporate Professional", 
                "description": "Traditional corporate design with formal styling",
                "category": "dashboard",
                "preview_url": "https://preview.vocelio.com/templates/corporate",
                "customizable_elements": [
                    "colors", "typography", "logo_placement"
                ]
            },
            {
                "id": "template_minimal",
                "name": "Minimal Interface",
                "description": "Stripped-down interface focusing on functionality",
                "category": "dashboard", 
                "preview_url": "https://preview.vocelio.com/templates/minimal",
                "customizable_elements": [
                    "colors", "spacing"
                ]
            }
        ],
        "email_templates": [
            {
                "id": "email_welcome",
                "name": "Welcome Email",
                "description": "Customer onboarding email template",
                "preview_url": "https://preview.vocelio.com/email/welcome"
            },
            {
                "id": "email_invoice", 
                "name": "Invoice Email",
                "description": "Billing invoice email template",
                "preview_url": "https://preview.vocelio.com/email/invoice"
            }
        ]
    }

@router.get("/{template_id}", summary="Get template details")
async def get_template_details(
    template_id: str,
    current_user = Depends(get_current_user)
):
    """Get detailed information about a specific template."""
    return {
        "template_id": template_id,
        "name": "Modern Dashboard",
        "version": "2.1.0",
        "description": "Clean, modern interface with card-based layout and responsive design",
        "customization_options": {
            "colors": {
                "primary": {"type": "color", "default": "#2563eb"},
                "secondary": {"type": "color", "default": "#1e40af"},
                "accent": {"type": "color", "default": "#3b82f6"}
            },
            "typography": {
                "heading_font": {"type": "select", "options": ["Inter", "Roboto", "Open Sans"]},
                "body_font": {"type": "select", "options": ["Inter", "Roboto", "Open Sans"]}
            },
            "layout": {
                "sidebar_position": {"type": "select", "options": ["left", "right"]},
                "header_style": {"type": "select", "options": ["fixed", "static"]}
            }
        },
        "assets": {
            "css_variables": "/templates/modern/variables.css",
            "component_library": "/templates/modern/components.js",
            "style_guide": "/templates/modern/guide.pdf"
        }
    }

@router.post("/{template_id}/apply", summary="Apply template to brand")
async def apply_template(
    template_id: str,
    current_user = Depends(get_current_user)
):
    """Apply a template to the current brand."""
    return {
        "message": "Template applied successfully",
        "template_id": template_id,
        "brand_id": "brand_123",
        "applied_at": "2024-01-25T10:30:00Z",
        "backup_created": "backup_20240125_103000",
        "propagation_time": "5-10 minutes"
    }
