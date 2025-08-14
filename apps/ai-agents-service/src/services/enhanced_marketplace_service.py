"""
Enhanced Marketplace Service - Merged from agent-store
Handles commercial marketplace functionality with purchase, download, and review systems
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class PurchaseStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class EnhancedMarketplaceService:
    """Enhanced marketplace service with commercial features"""
    
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.marketplace_agents: Dict[str, dict] = {}
        self.featured_agents: List[str] = []
        self.user_purchases: Dict[str, List[dict]] = {}
        self.agent_reviews: Dict[str, List[dict]] = {}
        self.categories: Dict[str, dict] = {
            "sales": {"name": "Sales & Lead Generation", "count": 0},
            "support": {"name": "Customer Support", "count": 0},
            "healthcare": {"name": "Healthcare & Medical", "count": 0},
            "financial": {"name": "Financial Services", "count": 0},
            "education": {"name": "Education & Training", "count": 0},
            "general": {"name": "General Purpose", "count": 0}
        }
        self._initialize_sample_agents()
    
    def _initialize_sample_agents(self):
        """Initialize with sample marketplace agents"""
        sample_agents = [
            {
                "id": "agent_001",
                "name": "Sales Assistant Pro",
                "description": "Advanced AI agent for sales conversations and lead qualification with enterprise-grade features",
                "category": "sales",
                "price": 29.99,
                "rating": 4.8,
                "downloads": 1523,
                "creator_id": "user_123",
                "creator_name": "VoiceAI Labs",
                "capabilities": ["lead_qualification", "objection_handling", "appointment_setting", "crm_integration"],
                "languages": ["en", "es", "fr"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_featured": True,
                "is_verified": True,
                "trial_period_days": 7,
                "license_type": "per_user",
                "version": "2.1.0"
            },
            {
                "id": "agent_002", 
                "name": "Customer Support Specialist",
                "description": "Intelligent customer service agent with advanced problem resolution and escalation handling",
                "category": "support",
                "price": 19.99,
                "rating": 4.6,
                "downloads": 2341,
                "creator_id": "user_456",
                "creator_name": "Support Solutions Inc",
                "capabilities": ["ticket_resolution", "escalation_handling", "knowledge_base", "sentiment_analysis"],
                "languages": ["en", "de", "it"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_featured": False,
                "is_verified": True,
                "trial_period_days": 14,
                "license_type": "per_organization",
                "version": "1.8.3"
            },
            {
                "id": "agent_003",
                "name": "Healthcare Scheduler",
                "description": "Specialized agent for medical appointment scheduling, patient screening, and healthcare coordination",
                "category": "healthcare",
                "price": 49.99,
                "rating": 4.9,
                "downloads": 856,
                "creator_id": "user_789",
                "creator_name": "MedTech AI",
                "capabilities": ["appointment_scheduling", "patient_screening", "insurance_verification", "hipaa_compliance"],
                "languages": ["en"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_featured": True,
                "is_verified": True,
                "trial_period_days": 30,
                "license_type": "per_facility",
                "version": "3.0.1"
            }
        ]
        
        for agent in sample_agents:
            self.marketplace_agents[agent["id"]] = agent
            self.categories[agent["category"]]["count"] += 1

    async def get_marketplace_agents(
        self, 
        category: Optional[str] = None,
        featured: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: str = "rating",
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Get marketplace agents with advanced filtering"""
        agents = list(self.marketplace_agents.values())
        
        # Apply filters
        if category:
            agents = [a for a in agents if a["category"] == category]
        if featured is not None:
            agents = [a for a in agents if a["is_featured"] == featured]
        if min_price is not None:
            agents = [a for a in agents if a["price"] >= min_price]
        if max_price is not None:
            agents = [a for a in agents if a["price"] <= max_price]
        if search:
            search_lower = search.lower()
            agents = [a for a in agents if 
                     search_lower in a["name"].lower() or 
                     search_lower in a["description"].lower() or
                     any(search_lower in cap.lower() for cap in a["capabilities"])]
        
        # Sort agents
        reverse = sort_by in ["rating", "downloads", "created_at", "price"]
        if sort_by == "price":
            agents.sort(key=lambda x: x["price"], reverse=not reverse)  # Price ascending by default
        elif sort_by == "rating":
            agents.sort(key=lambda x: x["rating"], reverse=reverse)
        elif sort_by == "downloads":
            agents.sort(key=lambda x: x["downloads"], reverse=reverse)
        elif sort_by == "created_at":
            agents.sort(key=lambda x: x["created_at"], reverse=reverse)
        
        # Apply pagination
        total_count = len(agents)
        agents = agents[offset:offset + limit]
        
        return {
            "agents": agents,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }

    async def get_agent_details(self, agent_id: str) -> Optional[dict]:
        """Get detailed information about a specific agent"""
        agent = self.marketplace_agents.get(agent_id)
        if not agent:
            return None
        
        # Add reviews and additional metadata
        reviews = self.agent_reviews.get(agent_id, [])
        agent_details = agent.copy()
        agent_details["reviews"] = reviews
        agent_details["review_count"] = len(reviews)
        agent_details["avg_rating"] = sum(r["rating"] for r in reviews) / len(reviews) if reviews else agent["rating"]
        
        return agent_details

    async def purchase_agent(self, agent_id: str, user_id: str, payment_method: dict = None) -> dict:
        """Purchase an agent from the marketplace"""
        agent = self.marketplace_agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found in marketplace")
        
        # Check if user already owns this agent
        user_purchases = self.user_purchases.get(user_id, [])
        if any(p["agent_id"] == agent_id and p["status"] == PurchaseStatus.COMPLETED for p in user_purchases):
            raise ValueError("User already owns this agent")
        
        # Create purchase record
        purchase_id = str(uuid.uuid4())
        purchase = {
            "id": purchase_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "price": agent["price"],
            "status": PurchaseStatus.COMPLETED,  # Simplified for demo
            "purchase_date": datetime.utcnow(),
            "license_type": agent["license_type"],
            "trial_ends_at": datetime.utcnow().replace(day=datetime.utcnow().day + agent.get("trial_period_days", 0)) if agent.get("trial_period_days") else None,
            "payment_method": payment_method or {"type": "credit_card", "last4": "1234"}
        }
        
        # Store purchase
        if user_id not in self.user_purchases:
            self.user_purchases[user_id] = []
        self.user_purchases[user_id].append(purchase)
        
        # Update download count
        self.marketplace_agents[agent_id]["downloads"] += 1
        
        logger.info(f"Agent purchased: {agent_id} by user {user_id}")
        
        return {
            "purchase_id": purchase_id,
            "agent_id": agent_id,
            "status": "completed",
            "download_url": f"/marketplace/agents/{agent_id}/download?purchase_id={purchase_id}",
            "license_key": f"lic_{purchase_id[:8]}_{agent_id[:8]}",
            "support_url": "/support",
            "trial_ends_at": purchase["trial_ends_at"].isoformat() if purchase["trial_ends_at"] else None
        }

    async def download_agent(self, agent_id: str, user_id: str, purchase_id: str) -> dict:
        """Download a purchased agent"""
        # Verify purchase
        user_purchases = self.user_purchases.get(user_id, [])
        purchase = next((p for p in user_purchases if p["id"] == purchase_id and p["agent_id"] == agent_id), None)
        
        if not purchase:
            raise ValueError("Purchase not found or invalid")
        
        if purchase["status"] != PurchaseStatus.COMPLETED:
            raise ValueError("Purchase not completed")
        
        agent = self.marketplace_agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Generate download package (in production, this would be actual files)
        download_package = {
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "version": agent["version"],
            "files": [
                {"name": f"{agent['name'].lower().replace(' ', '_')}_config.json", "size": "2.3KB"},
                {"name": f"{agent['name'].lower().replace(' ', '_')}_model.pkl", "size": "45.7MB"},
                {"name": "installation_guide.pdf", "size": "1.2MB"},
                {"name": "api_documentation.html", "size": "856KB"}
            ],
            "license_key": f"lic_{purchase_id[:8]}_{agent_id[:8]}",
            "download_expires": datetime.utcnow().replace(hour=datetime.utcnow().hour + 24),
            "installation_instructions": f"1. Extract files\n2. Run setup.py\n3. Use license key: lic_{purchase_id[:8]}_{agent_id[:8]}"
        }
        
        logger.info(f"Agent download initiated: {agent_id} by user {user_id}")
        
        return download_package

    async def add_review(self, agent_id: str, user_id: str, review_data: dict) -> dict:
        """Add a review for an agent"""
        agent = self.marketplace_agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Check if user has purchased the agent
        user_purchases = self.user_purchases.get(user_id, [])
        has_purchased = any(p["agent_id"] == agent_id and p["status"] == PurchaseStatus.COMPLETED for p in user_purchases)
        
        if not has_purchased:
            raise ValueError("User must purchase agent before reviewing")
        
        review = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "user_id": user_id,
            "rating": max(1, min(5, review_data.get("rating", 5))),  # Clamp between 1-5
            "title": review_data.get("title", ""),
            "comment": review_data.get("comment", ""),
            "status": ReviewStatus.APPROVED,  # Simplified for demo
            "created_at": datetime.utcnow(),
            "helpful_count": 0
        }
        
        if agent_id not in self.agent_reviews:
            self.agent_reviews[agent_id] = []
        self.agent_reviews[agent_id].append(review)
        
        # Update agent rating
        reviews = self.agent_reviews[agent_id]
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        self.marketplace_agents[agent_id]["rating"] = round(avg_rating, 1)
        
        logger.info(f"Review added for agent {agent_id} by user {user_id}")
        
        return review

    async def get_user_purchases(self, user_id: str) -> List[dict]:
        """Get all purchases for a user"""
        purchases = self.user_purchases.get(user_id, [])
        
        # Enrich with agent details
        enriched_purchases = []
        for purchase in purchases:
            agent = self.marketplace_agents.get(purchase["agent_id"])
            if agent:
                enriched_purchase = purchase.copy()
                enriched_purchase["agent_name"] = agent["name"]
                enriched_purchase["agent_description"] = agent["description"]
                enriched_purchase["agent_version"] = agent["version"]
                enriched_purchases.append(enriched_purchase)
        
        return enriched_purchases

    async def get_categories(self) -> List[dict]:
        """Get all marketplace categories with agent counts"""
        return [
            {"id": cat_id, "name": cat_data["name"], "count": cat_data["count"]}
            for cat_id, cat_data in self.categories.items()
        ]

    async def get_featured_agents(self, limit: int = 10) -> List[dict]:
        """Get featured agents"""
        featured = [
            self.marketplace_agents[agent_id] 
            for agent_id in self.featured_agents 
            if agent_id in self.marketplace_agents
        ]
        return featured[:limit]

    async def publish_agent_to_marketplace(
        self, 
        agent_id: str, 
        publisher_id: str,
        marketplace_data: dict
    ) -> dict:
        """Publish an agent to the marketplace with commercial settings"""
        
        marketplace_agent = {
            "id": agent_id,
            "name": marketplace_data.get("name", f"Agent {agent_id[:8]}"),
            "description": marketplace_data.get("description", "AI agent for various tasks"),
            "category": marketplace_data.get("category", "general"),
            "price": marketplace_data.get("price", 9.99),
            "rating": 0.0,
            "downloads": 0,
            "creator_id": publisher_id,
            "creator_name": marketplace_data.get("creator_name", "Anonymous"),
            "capabilities": marketplace_data.get("capabilities", []),
            "languages": marketplace_data.get("languages", ["en"]),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_featured": False,
            "is_verified": marketplace_data.get("is_verified", False),
            "trial_period_days": marketplace_data.get("trial_period_days", 7),
            "license_type": marketplace_data.get("license_type", "per_user"),
            "version": marketplace_data.get("version", "1.0.0")
        }
        
        self.marketplace_agents[agent_id] = marketplace_agent
        
        # Update category count
        category = marketplace_agent["category"]
        if category in self.categories:
            self.categories[category]["count"] += 1
        
        logger.info(f"Agent published to marketplace: {agent_id}")
        
        return {
            "agent_id": agent_id,
            "status": "published",
            "marketplace_url": f"/marketplace/agents/{agent_id}",
            "publisher_dashboard": f"/marketplace/publisher/{publisher_id}/agents"
        }
