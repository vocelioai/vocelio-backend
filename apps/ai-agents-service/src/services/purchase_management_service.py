"""
Purchase Management Service - Commercial Transaction Handling
Handles payment processing, license management, and transaction security
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class LicenseType(str, Enum):
    PER_USER = "per_user"
    PER_ORGANIZATION = "per_organization"
    PER_FACILITY = "per_facility"
    ENTERPRISE = "enterprise"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"

class PurchaseManagementService:
    """Service for managing commercial purchases and transactions"""
    
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.transactions: Dict[str, dict] = {}
        self.licenses: Dict[str, dict] = {}
        self.payment_methods: Dict[str, dict] = {}
        self.refund_requests: Dict[str, dict] = {}
        self.subscription_plans: Dict[str, dict] = self._initialize_subscription_plans()
        
    def _initialize_subscription_plans(self) -> Dict[str, dict]:
        """Initialize subscription plan options"""
        return {
            "starter": {
                "id": "starter",
                "name": "Starter Plan",
                "price_monthly": 29.99,
                "price_yearly": 299.99,
                "max_agents": 5,
                "max_calls_per_month": 10000,
                "support_level": "email",
                "features": ["basic_analytics", "email_support", "standard_integrations"]
            },
            "professional": {
                "id": "professional", 
                "name": "Professional Plan",
                "price_monthly": 99.99,
                "price_yearly": 999.99,
                "max_agents": 25,
                "max_calls_per_month": 100000,
                "support_level": "priority",
                "features": ["advanced_analytics", "priority_support", "premium_integrations", "custom_branding"]
            },
            "enterprise": {
                "id": "enterprise",
                "name": "Enterprise Plan", 
                "price_monthly": 299.99,
                "price_yearly": 2999.99,
                "max_agents": -1,  # Unlimited
                "max_calls_per_month": -1,  # Unlimited
                "support_level": "dedicated",
                "features": ["enterprise_analytics", "dedicated_support", "all_integrations", "white_label", "sla_guarantee"]
            }
        }

    async def initiate_purchase(
        self,
        user_id: str,
        items: List[dict],
        payment_method: PaymentMethod,
        billing_info: dict,
        metadata: Optional[dict] = None
    ) -> dict:
        """Initiate a new purchase transaction"""
        
        transaction_id = str(uuid.uuid4())
        
        # Calculate totals
        subtotal = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        tax_rate = billing_info.get("tax_rate", 0.08)  # Default 8% tax
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Apply discounts if any
        discount_code = metadata.get("discount_code") if metadata else None
        discount_amount = 0
        if discount_code:
            discount_amount = await self._apply_discount(discount_code, subtotal)
            total_amount -= discount_amount
        
        transaction = {
            "id": transaction_id,
            "user_id": user_id,
            "items": items,
            "subtotal": round(subtotal, 2),
            "tax_amount": round(tax_amount, 2),
            "discount_amount": round(discount_amount, 2),
            "total_amount": round(total_amount, 2),
            "currency": billing_info.get("currency", "USD"),
            "payment_method": payment_method.value,
            "payment_status": PaymentStatus.PENDING,
            "billing_info": billing_info,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": metadata or {},
            "expires_at": datetime.utcnow() + timedelta(minutes=30)  # 30 min expiration
        }
        
        self.transactions[transaction_id] = transaction
        
        logger.info(f"Purchase initiated: {transaction_id} for user {user_id}, total: ${total_amount}")
        
        return {
            "transaction_id": transaction_id,
            "total_amount": total_amount,
            "currency": transaction["currency"],
            "expires_at": transaction["expires_at"].isoformat(),
            "payment_url": f"/payment/process/{transaction_id}",
            "status": "pending"
        }

    async def process_payment(self, transaction_id: str, payment_details: dict) -> dict:
        """Process payment for a transaction"""
        
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        if transaction["payment_status"] != PaymentStatus.PENDING:
            raise ValueError("Transaction already processed")
        
        if datetime.utcnow() > transaction["expires_at"]:
            transaction["payment_status"] = PaymentStatus.CANCELLED
            raise ValueError("Transaction expired")
        
        # Update status to processing
        transaction["payment_status"] = PaymentStatus.PROCESSING
        transaction["updated_at"] = datetime.utcnow()
        
        try:
            # Simulate payment processing (in production, integrate with payment gateway)
            payment_result = await self._process_with_payment_gateway(transaction, payment_details)
            
            if payment_result["success"]:
                transaction["payment_status"] = PaymentStatus.COMPLETED
                transaction["payment_confirmation"] = payment_result["confirmation_code"]
                transaction["processed_at"] = datetime.utcnow()
                
                # Generate licenses for purchased items
                licenses = await self._generate_licenses(transaction)
                transaction["licenses"] = [license["id"] for license in licenses]
                
                logger.info(f"Payment completed: {transaction_id}")
                
                return {
                    "transaction_id": transaction_id,
                    "status": "completed",
                    "confirmation_code": payment_result["confirmation_code"],
                    "licenses": licenses,
                    "receipt_url": f"/purchases/{transaction_id}/receipt"
                }
            else:
                transaction["payment_status"] = PaymentStatus.FAILED
                transaction["failure_reason"] = payment_result.get("error", "Payment failed")
                
                logger.warning(f"Payment failed: {transaction_id} - {payment_result.get('error')}")
                
                return {
                    "transaction_id": transaction_id,
                    "status": "failed",
                    "error": payment_result.get("error", "Payment processing failed")
                }
                
        except Exception as e:
            transaction["payment_status"] = PaymentStatus.FAILED
            transaction["failure_reason"] = str(e)
            logger.error(f"Payment processing error: {transaction_id} - {str(e)}")
            
            return {
                "transaction_id": transaction_id,
                "status": "failed", 
                "error": "Payment processing error"
            }
        
        finally:
            transaction["updated_at"] = datetime.utcnow()

    async def _process_with_payment_gateway(self, transaction: dict, payment_details: dict) -> dict:
        """Simulate payment gateway processing"""
        # In production, integrate with Stripe, PayPal, etc.
        
        # Simulate processing delay
        import asyncio
        await asyncio.sleep(0.1)
        
        # Simulate different outcomes based on payment details
        test_card = payment_details.get("card_number", "")
        
        if test_card.endswith("0000"):  # Test failure case
            return {
                "success": False,
                "error": "Card declined - insufficient funds"
            }
        elif test_card.endswith("0001"):  # Test fraud case
            return {
                "success": False,
                "error": "Transaction blocked - suspected fraud"
            }
        else:  # Successful payment
            return {
                "success": True,
                "confirmation_code": f"conf_{str(uuid.uuid4())[:8]}",
                "gateway_transaction_id": f"gw_{str(uuid.uuid4())[:12]}",
                "processed_amount": transaction["total_amount"]
            }

    async def _generate_licenses(self, transaction: dict) -> List[dict]:
        """Generate licenses for purchased items"""
        licenses = []
        
        for item in transaction["items"]:
            if item.get("type") == "agent":
                license = await self._create_agent_license(
                    transaction["user_id"],
                    item["agent_id"],
                    item.get("license_type", LicenseType.PER_USER),
                    transaction["id"]
                )
                licenses.append(license)
            elif item.get("type") == "subscription":
                license = await self._create_subscription_license(
                    transaction["user_id"],
                    item["plan_id"],
                    item.get("billing_cycle", "monthly"),
                    transaction["id"]
                )
                licenses.append(license)
        
        return licenses

    async def _create_agent_license(
        self, 
        user_id: str, 
        agent_id: str, 
        license_type: LicenseType,
        transaction_id: str
    ) -> dict:
        """Create an agent license"""
        
        license_id = str(uuid.uuid4())
        license_key = f"agt_{license_id[:8]}_{agent_id[:8]}"
        
        license = {
            "id": license_id,
            "type": "agent",
            "license_key": license_key,
            "user_id": user_id,
            "agent_id": agent_id,
            "license_type": license_type.value,
            "transaction_id": transaction_id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": None,  # Permanent license for agents
            "usage_limits": self._get_license_limits(license_type),
            "activation_count": 0,
            "max_activations": self._get_max_activations(license_type)
        }
        
        self.licenses[license_id] = license
        
        return license

    async def _create_subscription_license(
        self,
        user_id: str,
        plan_id: str,
        billing_cycle: str,
        transaction_id: str
    ) -> dict:
        """Create a subscription license"""
        
        license_id = str(uuid.uuid4())
        license_key = f"sub_{license_id[:8]}_{plan_id[:8]}"
        
        # Calculate expiration based on billing cycle
        if billing_cycle == "monthly":
            expires_at = datetime.utcnow() + timedelta(days=30)
        elif billing_cycle == "yearly":
            expires_at = datetime.utcnow() + timedelta(days=365)
        else:
            expires_at = datetime.utcnow() + timedelta(days=30)
        
        plan = self.subscription_plans.get(plan_id, self.subscription_plans["starter"])
        
        license = {
            "id": license_id,
            "type": "subscription",
            "license_key": license_key,
            "user_id": user_id,
            "plan_id": plan_id,
            "billing_cycle": billing_cycle,
            "transaction_id": transaction_id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "auto_renewal": True,
            "plan_limits": {
                "max_agents": plan["max_agents"],
                "max_calls_per_month": plan["max_calls_per_month"],
                "support_level": plan["support_level"],
                "features": plan["features"]
            },
            "current_usage": {
                "agents_deployed": 0,
                "calls_this_month": 0,
                "last_reset": datetime.utcnow()
            }
        }
        
        self.licenses[license_id] = license
        
        return license

    def _get_license_limits(self, license_type: LicenseType) -> dict:
        """Get usage limits based on license type"""
        limits = {
            LicenseType.PER_USER: {"max_concurrent_sessions": 1, "max_monthly_calls": 10000},
            LicenseType.PER_ORGANIZATION: {"max_concurrent_sessions": 50, "max_monthly_calls": 500000},
            LicenseType.PER_FACILITY: {"max_concurrent_sessions": 100, "max_monthly_calls": 1000000},
            LicenseType.ENTERPRISE: {"max_concurrent_sessions": -1, "max_monthly_calls": -1}
        }
        return limits.get(license_type, limits[LicenseType.PER_USER])

    def _get_max_activations(self, license_type: LicenseType) -> int:
        """Get maximum activation count based on license type"""
        activations = {
            LicenseType.PER_USER: 1,
            LicenseType.PER_ORGANIZATION: 10,
            LicenseType.PER_FACILITY: 25,
            LicenseType.ENTERPRISE: -1  # Unlimited
        }
        return activations.get(license_type, 1)

    async def _apply_discount(self, discount_code: str, subtotal: float) -> float:
        """Apply discount code to purchase"""
        # Simple discount codes for demo
        discount_codes = {
            "WELCOME10": {"type": "percentage", "value": 0.10, "min_amount": 10.0},
            "SAVE20": {"type": "percentage", "value": 0.20, "min_amount": 50.0},
            "NEWUSER": {"type": "fixed", "value": 5.0, "min_amount": 20.0},
            "ENTERPRISE50": {"type": "fixed", "value": 50.0, "min_amount": 200.0}
        }
        
        discount = discount_codes.get(discount_code.upper())
        if not discount:
            return 0
        
        if subtotal < discount["min_amount"]:
            return 0
        
        if discount["type"] == "percentage":
            return subtotal * discount["value"]
        elif discount["type"] == "fixed":
            return min(discount["value"], subtotal)
        
        return 0

    async def get_transaction_status(self, transaction_id: str) -> dict:
        """Get the status of a transaction"""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        return {
            "transaction_id": transaction_id,
            "status": transaction["payment_status"],
            "total_amount": transaction["total_amount"],
            "currency": transaction["currency"],
            "created_at": transaction["created_at"].isoformat(),
            "updated_at": transaction["updated_at"].isoformat(),
            "expires_at": transaction["expires_at"].isoformat() if transaction.get("expires_at") else None
        }

    async def get_user_licenses(self, user_id: str) -> List[dict]:
        """Get all licenses for a user"""
        user_licenses = [
            license for license in self.licenses.values()
            if license["user_id"] == user_id
        ]
        
        # Check for expired subscriptions
        for license in user_licenses:
            if (license["type"] == "subscription" and 
                license.get("expires_at") and
                datetime.utcnow() > license["expires_at"]):
                license["status"] = "expired"
        
        return user_licenses

    async def validate_license(self, license_key: str, agent_id: Optional[str] = None) -> dict:
        """Validate a license key"""
        license = next(
            (lic for lic in self.licenses.values() if lic["license_key"] == license_key),
            None
        )
        
        if not license:
            return {"valid": False, "error": "License not found"}
        
        if license["status"] != "active":
            return {"valid": False, "error": f"License is {license['status']}"}
        
        # Check expiration for subscriptions
        if (license["type"] == "subscription" and
            license.get("expires_at") and
            datetime.utcnow() > license["expires_at"]):
            license["status"] = "expired"
            return {"valid": False, "error": "License expired"}
        
        # Check agent-specific license
        if agent_id and license["type"] == "agent" and license.get("agent_id") != agent_id:
            return {"valid": False, "error": "License not valid for this agent"}
        
        return {
            "valid": True,
            "license": license,
            "remaining_usage": self._calculate_remaining_usage(license)
        }

    def _calculate_remaining_usage(self, license: dict) -> dict:
        """Calculate remaining usage for a license"""
        if license["type"] == "agent":
            limits = license["usage_limits"]
            return {
                "monthly_calls_remaining": max(0, limits["max_monthly_calls"] - license.get("calls_used", 0)),
                "concurrent_sessions_available": limits["max_concurrent_sessions"] - license.get("active_sessions", 0)
            }
        elif license["type"] == "subscription":
            current_usage = license["current_usage"]
            plan_limits = license["plan_limits"]
            
            calls_remaining = plan_limits["max_calls_per_month"] - current_usage["calls_this_month"]
            if plan_limits["max_calls_per_month"] == -1:  # Unlimited
                calls_remaining = -1
            
            agents_remaining = plan_limits["max_agents"] - current_usage["agents_deployed"] 
            if plan_limits["max_agents"] == -1:  # Unlimited
                agents_remaining = -1
            
            return {
                "calls_remaining": calls_remaining,
                "agents_remaining": agents_remaining,
                "days_until_renewal": (license["expires_at"] - datetime.utcnow()).days if license.get("expires_at") else -1
            }
        
        return {}

    async def request_refund(self, transaction_id: str, user_id: str, reason: str) -> dict:
        """Request a refund for a transaction"""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        if transaction["user_id"] != user_id:
            raise ValueError("Unauthorized refund request")
        
        if transaction["payment_status"] != PaymentStatus.COMPLETED:
            raise ValueError("Cannot refund incomplete transaction")
        
        refund_id = str(uuid.uuid4())
        refund_request = {
            "id": refund_id,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": transaction["total_amount"],
            "reason": reason,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "processed_at": None
        }
        
        self.refund_requests[refund_id] = refund_request
        
        logger.info(f"Refund requested: {refund_id} for transaction {transaction_id}")
        
        return {
            "refund_id": refund_id,
            "status": "pending",
            "processing_time": "3-5 business days",
            "contact_support": "/support/refunds"
        }
