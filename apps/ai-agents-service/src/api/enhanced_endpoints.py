"""
Enhanced API Endpoints for Unified AI Agent Platform
Marketplace, Purchase Management, and Enhanced Agent Management
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional, Dict, Any
import logging

from ..services.enhanced_marketplace_service import EnhancedMarketplaceService
from ..services.purchase_management_service import PurchaseManagementService, PaymentMethod
from ..services.enhanced_agent_management_service import EnhancedAgentManagementService, DeploymentEnvironment
from ..models.enhanced_models import (
    MarketplaceListResponse, CreateReviewRequest, PurchaseRequest, 
    TransactionResponse, PaymentDetailsModel, CreateEnhancedAgentRequest,
    AgentCreationResponse, ConfigureCapabilitiesRequest, DeployAgentRequest,
    DeploymentResponse, UpdateConfigurationRequest, AgentAnalyticsRequest,
    AnalyticsResponse, CloneAgentRequest, PublishToMarketplaceRequest,
    HealthCheckResponse, CapabilityCatalogResponse, LicenseValidationResponse,
    RefundResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

# Initialize services
marketplace_service = EnhancedMarketplaceService()
purchase_service = PurchaseManagementService()
agent_management_service = EnhancedAgentManagementService()

# Create router
router = APIRouter(prefix="/api/v1", tags=["unified-ai-agent-platform"])

# ==================== MARKETPLACE ENDPOINTS ====================

@router.get("/marketplace/agents", response_model=MarketplaceListResponse)
async def get_marketplace_agents(
    category: Optional[str] = Query(None, description="Filter by category"),
    featured: Optional[bool] = Query(None, description="Filter featured agents"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    search: Optional[str] = Query(None, description="Search in name, description, capabilities"),
    sort_by: str = Query("rating", description="Sort by: rating, downloads, price, created_at"),
    limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Get marketplace agents with advanced filtering and search"""
    try:
        result = await marketplace_service.get_marketplace_agents(
            category=category,
            featured=featured,
            min_price=min_price,
            max_price=max_price,
            search=search,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        return MarketplaceListResponse(**result)
    except Exception as e:
        logger.error(f"Error fetching marketplace agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch marketplace agents")

@router.get("/marketplace/agents/{agent_id}")
async def get_marketplace_agent_details(
    agent_id: str = Path(..., description="Agent ID")
):
    """Get detailed information about a marketplace agent"""
    try:
        agent_details = await marketplace_service.get_agent_details(agent_id)
        if not agent_details:
            raise HTTPException(status_code=404, detail="Agent not found in marketplace")
        return agent_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent details")

@router.get("/marketplace/categories")
async def get_marketplace_categories():
    """Get all marketplace categories with agent counts"""
    try:
        categories = await marketplace_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@router.get("/marketplace/featured")
async def get_featured_agents(
    limit: int = Query(10, ge=1, le=20, description="Number of featured agents")
):
    """Get featured marketplace agents"""
    try:
        featured_agents = await marketplace_service.get_featured_agents(limit=limit)
        return {"featured_agents": featured_agents, "count": len(featured_agents)}
    except Exception as e:
        logger.error(f"Error fetching featured agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch featured agents")

@router.post("/marketplace/agents/{agent_id}/reviews")
async def add_agent_review(
    agent_id: str = Path(..., description="Agent ID"),
    review_data: CreateReviewRequest = ...,
    user_id: str = Query(..., description="User ID")  # In production, get from auth token
):
    """Add a review for a marketplace agent"""
    try:
        review = await marketplace_service.add_review(agent_id, user_id, review_data.dict())
        return {"review": review, "message": "Review added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add review")

# ==================== PURCHASE MANAGEMENT ENDPOINTS ====================

@router.post("/purchases/initiate", response_model=TransactionResponse)
async def initiate_purchase(
    purchase_request: PurchaseRequest,
    user_id: str = Query(..., description="User ID")  # In production, get from auth token
):
    """Initiate a new purchase transaction"""
    try:
        transaction = await purchase_service.initiate_purchase(
            user_id=user_id,
            items=purchase_request.items,
            payment_method=purchase_request.payment_method,
            billing_info=purchase_request.billing_info.dict(),
            metadata=purchase_request.metadata
        )
        return TransactionResponse(**transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating purchase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate purchase")

@router.post("/purchases/{transaction_id}/process")
async def process_payment(
    transaction_id: str = Path(..., description="Transaction ID"),
    payment_details: PaymentDetailsModel = ...
):
    """Process payment for a transaction"""
    try:
        result = await purchase_service.process_payment(transaction_id, payment_details.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process payment")

@router.get("/purchases/{transaction_id}/status")
async def get_transaction_status(
    transaction_id: str = Path(..., description="Transaction ID")
):
    """Get the status of a transaction"""
    try:
        status = await purchase_service.get_transaction_status(transaction_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching transaction status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch transaction status")

@router.get("/users/{user_id}/purchases")
async def get_user_purchases(
    user_id: str = Path(..., description="User ID")
):
    """Get all purchases for a user"""
    try:
        purchases = await purchase_service.get_user_purchases(user_id)
        return {"purchases": purchases, "total": len(purchases)}
    except Exception as e:
        logger.error(f"Error fetching user purchases: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user purchases")

@router.get("/users/{user_id}/licenses")
async def get_user_licenses(
    user_id: str = Path(..., description="User ID")
):
    """Get all licenses for a user"""
    try:
        licenses = await purchase_service.get_user_licenses(user_id)
        return {"licenses": licenses, "total": len(licenses)}
    except Exception as e:
        logger.error(f"Error fetching user licenses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user licenses")

@router.post("/licenses/validate", response_model=LicenseValidationResponse)
async def validate_license(
    license_key: str = Query(..., description="License key to validate"),
    agent_id: Optional[str] = Query(None, description="Agent ID for agent-specific licenses")
):
    """Validate a license key"""
    try:
        validation_result = await purchase_service.validate_license(license_key, agent_id)
        return LicenseValidationResponse(**validation_result)
    except Exception as e:
        logger.error(f"Error validating license: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate license")

@router.post("/marketplace/agents/{agent_id}/purchase")
async def purchase_marketplace_agent(
    agent_id: str = Path(..., description="Agent ID"),
    user_id: str = Query(..., description="User ID"),
    payment_method: Optional[Dict[str, Any]] = None
):
    """Quick purchase of a marketplace agent"""
    try:
        purchase_result = await marketplace_service.purchase_agent(
            agent_id=agent_id,
            user_id=user_id,
            payment_method=payment_method
        )
        return purchase_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error purchasing agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to purchase agent")

@router.get("/marketplace/agents/{agent_id}/download")
async def download_marketplace_agent(
    agent_id: str = Path(..., description="Agent ID"),
    user_id: str = Query(..., description="User ID"),
    purchase_id: str = Query(..., description="Purchase ID")
):
    """Download a purchased marketplace agent"""
    try:
        download_package = await marketplace_service.download_agent(agent_id, user_id, purchase_id)
        return download_package
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download agent")

# ==================== ENHANCED AGENT MANAGEMENT ENDPOINTS ====================

@router.post("/agents/enhanced", response_model=AgentCreationResponse)
async def create_enhanced_agent(
    agent_data: CreateEnhancedAgentRequest,
    user_id: str = Query(..., description="User ID")
):
    """Create an agent with enhanced capabilities and configuration"""
    try:
        result = await agent_management_service.create_enhanced_agent(
            user_id=user_id,
            agent_data=agent_data.dict(),
            capabilities=agent_data.capabilities,
            template_id=agent_data.template_id
        )
        return AgentCreationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating enhanced agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create enhanced agent")

@router.post("/agents/{agent_id}/capabilities/configure")
async def configure_agent_capabilities(
    agent_id: str = Path(..., description="Agent ID"),
    config_request: ConfigureCapabilitiesRequest = ...
):
    """Configure specific capabilities for an agent"""
    try:
        result = await agent_management_service.configure_agent_capabilities(
            agent_id=agent_id,
            capability_configs=config_request.capability_configs
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error configuring capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to configure capabilities")

@router.post("/agents/{agent_id}/deploy", response_model=DeploymentResponse)
async def deploy_agent(
    agent_id: str = Path(..., description="Agent ID"),
    deploy_request: DeployAgentRequest = ...
):
    """Deploy an agent to a specific environment"""
    try:
        result = await agent_management_service.deploy_agent(
            agent_id=agent_id,
            environment=deploy_request.environment,
            deployment_config=deploy_request.deployment_config
        )
        return DeploymentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deploying agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to deploy agent")

@router.get("/agents/{agent_id}/analytics", response_model=AnalyticsResponse)
async def get_agent_analytics(
    agent_id: str = Path(..., description="Agent ID"),
    time_range: str = Query("7d", description="Time range for analytics"),
    metrics: Optional[List[str]] = Query(None, description="Specific metrics to include")
):
    """Get comprehensive analytics for an agent"""
    try:
        analytics = await agent_management_service.get_agent_analytics(
            agent_id=agent_id,
            time_range=time_range,
            metrics=metrics
        )
        return AnalyticsResponse(**analytics)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching agent analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent analytics")

@router.put("/agents/{agent_id}/configuration")
async def update_agent_configuration(
    agent_id: str = Path(..., description="Agent ID"),
    config_request: UpdateConfigurationRequest = ...
):
    """Update agent configuration with validation"""
    try:
        result = await agent_management_service.update_agent_configuration(
            agent_id=agent_id,
            configuration_updates=config_request.configuration_updates
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@router.post("/agents/{agent_id}/clone")
async def clone_agent(
    agent_id: str = Path(..., description="Agent ID"),
    clone_request: CloneAgentRequest = ...,
    user_id: str = Query(..., description="User ID")
):
    """Clone an existing agent with all configurations"""
    try:
        result = await agent_management_service.clone_agent(
            agent_id=agent_id,
            new_name=clone_request.new_name,
            user_id=user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error cloning agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clone agent")

@router.get("/agents/{agent_id}/health", response_model=HealthCheckResponse)
async def get_agent_health(
    agent_id: str = Path(..., description="Agent ID")
):
    """Get health status and diagnostics for an agent"""
    try:
        health_status = await agent_management_service.get_agent_health(agent_id)
        return HealthCheckResponse(**health_status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching agent health: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent health")

@router.get("/capabilities/catalog", response_model=CapabilityCatalogResponse)
async def get_capability_catalog(
    category: Optional[str] = Query(None, description="Filter by capability category")
):
    """Get catalog of available agent capabilities"""
    try:
        catalog = await agent_management_service.get_capability_catalog(category=category)
        return CapabilityCatalogResponse(**catalog)
    except Exception as e:
        logger.error(f"Error fetching capability catalog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch capability catalog")

# ==================== MARKETPLACE PUBLISHING ENDPOINTS ====================

@router.post("/agents/{agent_id}/publish")
async def publish_agent_to_marketplace(
    agent_id: str = Path(..., description="Agent ID"),
    publish_request: PublishToMarketplaceRequest = ...,
    publisher_id: str = Query(..., description="Publisher ID")
):
    """Publish an agent to the marketplace with commercial settings"""
    try:
        result = await marketplace_service.publish_agent_to_marketplace(
            agent_id=agent_id,
            publisher_id=publisher_id,
            marketplace_data=publish_request.dict()
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error publishing agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish agent")

# ==================== REFUND MANAGEMENT ENDPOINTS ====================

@router.post("/purchases/{transaction_id}/refund", response_model=RefundResponse)
async def request_refund(
    transaction_id: str = Path(..., description="Transaction ID"),
    user_id: str = Query(..., description="User ID"),
    reason: str = Query(..., description="Refund reason")
):
    """Request a refund for a transaction"""
    try:
        refund_result = await purchase_service.request_refund(transaction_id, user_id, reason)
        return RefundResponse(**refund_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error requesting refund: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to request refund")

# ==================== SUBSCRIPTION MANAGEMENT ENDPOINTS ====================

@router.get("/subscriptions/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    try:
        plans = purchase_service.subscription_plans
        return {"plans": list(plans.values())}
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscription plans")

# ==================== AGENT TEMPLATES ENDPOINTS ====================

@router.get("/agents/templates")
async def get_agent_templates():
    """Get available agent templates for quick deployment"""
    try:
        templates = agent_management_service.templates
        return {"templates": list(templates.values())}
    except Exception as e:
        logger.error(f"Error fetching agent templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent templates")

@router.get("/agents/templates/{template_id}")
async def get_agent_template_details(
    template_id: str = Path(..., description="Template ID")
):
    """Get detailed information about an agent template"""
    try:
        template = agent_management_service.templates.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"template": template}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch template details")

# ==================== UNIFIED DASHBOARD ENDPOINTS ====================

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    user_id: str = Query(..., description="User ID")
):
    """Get unified dashboard overview with agents, purchases, and marketplace data"""
    try:
        # Get user's enhanced agents
        user_agents = [agent for agent in agent_management_service.agents.values() 
                      if agent["user_id"] == user_id]
        
        # Get user's purchases and licenses
        purchases = await purchase_service.get_user_purchases(user_id)
        licenses = await purchase_service.get_user_licenses(user_id)
        
        # Get marketplace stats if user has published agents
        published_agents = [agent for agent in marketplace_service.marketplace_agents.values()
                           if agent["creator_id"] == user_id]
        
        overview = {
            "user_id": user_id,
            "agents": {
                "total": len(user_agents),
                "deployed": len([a for a in user_agents if a["status"] == "deployed"]),
                "active": len([a for a in user_agents if a["status"] == "active"])
            },
            "purchases": {
                "total": len(purchases),
                "total_spent": sum(p.get("total_amount", 0) for p in purchases)
            },
            "licenses": {
                "total": len(licenses),
                "active": len([l for l in licenses if l["status"] == "active"])
            },
            "marketplace": {
                "published_agents": len(published_agents),
                "total_downloads": sum(a.get("downloads", 0) for a in published_agents),
                "total_revenue": sum(a.get("downloads", 0) * a.get("price", 0) for a in published_agents)
            }
        }
        
        return overview
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard overview")
