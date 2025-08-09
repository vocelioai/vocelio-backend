# shared/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os
import logging
from typing import Optional, Dict, Any, List
import hashlib
import hmac

from ..database.client import user_repo, org_repo

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class AuthorizationError(Exception):
    """Custom authorization error"""
    pass

class TokenData:
    """Token data structure"""
    def __init__(self, user_id: str = None, org_id: str = None, email: str = None, role: str = None):
        self.user_id = user_id
        self.org_id = org_id
        self.email = email
        self.role = role

class CurrentUser:
    """Current user data structure"""
    def __init__(self, user_data: Dict[str, Any], organization_data: Dict[str, Any] = None):
        self.id = user_data.get("id")
        self.email = user_data.get("email")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")
        self.role = user_data.get("role", "user")
        self.organization_id = user_data.get("organization_id")
        self.timezone = user_data.get("timezone", "UTC")
        self.created_at = user_data.get("created_at")
        self.last_login = user_data.get("last_login")
        self.is_active = user_data.get("is_active", True)
        
        # Organization data
        self.organization = organization_data
        
        # Permissions cache
        self._permissions = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email.split("@")[0]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role in ["admin", "owner"]
    
    @property
    def is_owner(self) -> bool:
        """Check if user is organization owner"""
        return self.role == "owner"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_owner:
            return True  # Owner has all permissions
        
        # Define role-based permissions
        role_permissions = {
            "admin": [
                "users.create", "users.read", "users.update", "users.delete",
                "agents.create", "agents.read", "agents.update", "agents.delete",
                "campaigns.create", "campaigns.read", "campaigns.update", "campaigns.delete", 
                "calls.create", "calls.read", "calls.update", "calls.delete",
                "analytics.read", "billing.read", "settings.update"
            ],
            "manager": [
                "agents.create", "agents.read", "agents.update",
                "campaigns.create", "campaigns.read", "campaigns.update",
                "calls.read", "analytics.read"
            ],
            "agent": [
                "agents.read", "campaigns.read", "calls.read"
            ],
            "viewer": [
                "agents.read", "campaigns.read", "calls.read", "analytics.read"
            ]
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return permission in user_permissions
    
    def can_access_organization(self, org_id: str) -> bool:
        """Check if user can access specific organization"""
        return self.organization_id == org_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role,
            "organization_id": self.organization_id,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "is_owner": self.is_owner,
            "organization": self.organization
        }

# JWT Token functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"❌ Error creating access token: {e}")
        raise AuthenticationError("Could not create access token")

def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("user_id")
        org_id: str = payload.get("org_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
        
        return TokenData(user_id=user_id, org_id=org_id, email=email, role=role)
    
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
    except Exception as e:
        logger.error(f"❌ Error verifying token: {e}")
        raise AuthenticationError("Token verification failed")

def create_api_key(user_id: str, org_id: str, key_name: str = None) -> str:
    """Create API key for programmatic access"""
    # API keys are prefixed with 'voc_' for easy identification
    key_data = {
        "user_id": user_id,
        "org_id": org_id,
        "created_at": datetime.utcnow().isoformat(),
        "name": key_name or "API Key"
    }
    
    # Create a hash of the key data
    key_string = f"{user_id}:{org_id}:{datetime.utcnow().timestamp()}"
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    return f"voc_{key_hash}"

def verify_api_key(api_key: str) -> Optional[TokenData]:
    """Verify API key (this would typically check against database)"""
    if not api_key.startswith("voc_"):
        return None
    
    # In a real implementation, you would:
    # 1. Query the database for the API key
    # 2. Check if it's active and not expired
    # 3. Return the associated user/org data
    
    # For now, return None (implement in developer-api service)
    return None

# Authentication dependencies
async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """Get current user from JWT token"""
    try:
        # Extract token
        token = credentials.credentials
        
        # Handle API keys
        if token.startswith("voc_"):
            token_data = verify_api_key(token)
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            # Handle JWT tokens
            token_data = verify_token(token)
        
        # Get user data from database
        if not user_repo:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        user_data = await user_repo.get_by_id(token_data.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get organization data
        organization_data = None
        if user_data.get("organization_id") and org_repo:
            organization_data = await org_repo.get_by_id(user_data["organization_id"])
        
        # Update last seen
        try:
            await user_repo.update_last_login(user_data["id"])
        except Exception as e:
            logger.warning(f"⚠️ Could not update last login: {e}")
        
        return CurrentUser(user_data, organization_data)
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: CurrentUser = Depends(get_current_user_from_token)) -> CurrentUser:
    """Get current active user (additional check)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    return current_user

# Authorization dependencies
def require_role(required_roles: List[str]):
    """Require specific user roles"""
    def role_checker(current_user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

def require_permission(permission: str):
    """Require specific permission"""
    def permission_checker(current_user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {permission}"
            )
        return current_user
    return permission_checker

def require_organization_access(org_id: str = None):
    """Require access to specific organization"""
    def org_checker(current_user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        # If no org_id specified, just return current user
        if not org_id:
            return current_user
        
        if not current_user.can_access_organization(org_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this organization"
            )
        return current_user
    return org_checker

# Specific role dependencies (shortcuts)
require_admin = require_role(["admin", "owner"])
require_manager = require_role(["manager", "admin", "owner"])
require_agent = require_role(["agent", "manager", "admin", "owner"])

# Optional authentication (for public endpoints with optional user context)
async def get_current_user_optional(request: Request) -> Optional[CurrentUser]:
    """Get current user if token is provided, otherwise return None"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
        
        # Verify token
        if token.startswith("voc_"):
            token_data = verify_api_key(token)
        else:
            token_data = verify_token(token)
        
        if not token_data or not user_repo:
            return None
        
        # Get user data
        user_data = await user_repo.get_by_id(token_data.user_id)
        if not user_data or not user_data.get("is_active", True):
            return None
        
        # Get organization data
        organization_data = None
        if user_data.get("organization_id") and org_repo:
            organization_data = await org_repo.get_by_id(user_data["organization_id"])
        
        return CurrentUser(user_data, organization_data)
        
    except Exception as e:
        logger.debug(f"Optional auth failed: {e}")
        return None

# Rate limiting based on user
async def get_rate_limit_key(request: Request, current_user: Optional[CurrentUser] = None) -> str:
    """Get rate limiting key based on user or IP"""
    if current_user:
        return f"user:{current_user.id}"
    else:
        return f"ip:{request.client.host}"

# Organization-specific dependencies
async def get_user_organization(current_user: CurrentUser = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get current user's organization"""
    if not current_user.organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return current_user.organization

async def check_organization_limits(
    current_user: CurrentUser = Depends(get_current_active_user),
    organization: Dict[str, Any] = Depends(get_user_organization)
) -> Dict[str, Any]:
    """Check organization limits and return current usage"""
    try:
        # Get organization limits based on plan
        plan_limits = {
            "free": {
                "max_users": 1,
                "max_agents": 2,
                "max_calls_per_month": 100,
                "max_voice_generations": 1000,
                "max_campaigns": 3
            },
            "starter": {
                "max_users": 5,
                "max_agents": 10,
                "max_calls_per_month": 1000,
                "max_voice_generations": 10000,
                "max_campaigns": 10
            },
            "professional": {
                "max_users": 25,
                "max_agents": 50,
                "max_calls_per_month": 10000,
                "max_voice_generations": 100000,
                "max_campaigns": 50
            },
            "enterprise": {
                "max_users": -1,  # Unlimited
                "max_agents": -1,
                "max_calls_per_month": -1,
                "max_voice_generations": -1,
                "max_campaigns": -1
            }
        }
        
        org_plan = organization.get("plan", "free")
        limits = plan_limits.get(org_plan, plan_limits["free"])
        
        # Get current usage (would query actual usage from database)
        current_usage = organization.get("usage_stats", {})
        
        # Check limits
        over_limits = []
        for limit_name, limit_value in limits.items():
            if limit_value == -1:  # Unlimited
                continue
            
            current_value = current_usage.get(limit_name.replace("max_", ""), 0)
            if current_value >= limit_value:
                over_limits.append({
                    "limit": limit_name,
                    "current": current_value,
                    "max": limit_value
                })
        
        return {
            "organization_id": organization["id"],
            "plan": org_plan,
            "limits": limits,
            "current_usage": current_usage,
            "over_limits": over_limits,
            "can_upgrade": org_plan != "enterprise"
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking organization limits: {e}")
        return {
            "organization_id": current_user.organization_id,
            "plan": "free",
            "limits": {},
            "current_usage": {},
            "over_limits": [],
            "error": str(e)
        }

# Webhook authentication
def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature (for Twilio, Stripe, etc.)"""
    try:
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures safely
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"❌ Webhook signature verification failed: {e}")
        return False

async def verify_twilio_webhook(request: Request) -> bool:
    """Verify Twilio webhook signature"""
    try:
        twilio_signature = request.headers.get("X-Twilio-Signature", "")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        
        if not twilio_signature or not auth_token:
            return False
        
        # Get raw body
        body = await request.body()
        
        # Verify signature
        return verify_webhook_signature(body, twilio_signature, auth_token)
        
    except Exception as e:
        logger.error(f"❌ Twilio webhook verification failed: {e}")
        return False

async def verify_stripe_webhook(request: Request) -> bool:
    """Verify Stripe webhook signature"""
    try:
        stripe_signature = request.headers.get("Stripe-Signature", "")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        if not stripe_signature or not webhook_secret:
            return False
        
        # Get raw body
        body = await request.body()
        
        # Parse signature header
        sig_parts = {}
        for part in stripe_signature.split(","):
            key, value = part.split("=")
            sig_parts[key] = value
        
        signature = sig_parts.get("v1", "")
        timestamp = sig_parts.get("t", "")
        
        # Create expected signature
        payload = f"{timestamp}.{body.decode()}"
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"❌ Stripe webhook verification failed: {e}")
        return False

# Service-to-service authentication (for internal API calls)
class ServiceAuth:
    """Authentication for service-to-service communication"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.service_secret = os.getenv(f"{service_name.upper()}_SERVICE_SECRET", SECRET_KEY)
    
    def create_service_token(self, data: Dict[str, Any] = None) -> str:
        """Create token for service-to-service communication"""
        payload = {
            "service": self.service_name,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)  # Short-lived service tokens
        }
        
        if data:
            payload.update(data)
        
        return jwt.encode(payload, self.service_secret, algorithm=ALGORITHM)
    
    def verify_service_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify service token"""
        try:
            payload = jwt.decode(token, self.service_secret, algorithms=[ALGORITHM])
            
            if payload.get("service") != self.service_name:
                return None
            
            return payload
        except Exception as e:
            logger.error(f"❌ Service token verification failed: {e}")
            return None

# Create service auth instances for different services
gateway_auth = ServiceAuth("gateway")
ai_brain_auth = ServiceAuth("ai_brain")
voice_lab_auth = ServiceAuth("voice_lab")
call_center_auth = ServiceAuth("call_center")

def require_service_auth(service_name: str):
    """Require service-to-service authentication"""
    def service_auth_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
        service_auth = ServiceAuth(service_name)
        token_data = service_auth.verify_service_token(credentials.credentials)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token_data
    
    return service_auth_checker

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt-style hashing"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_reset_token(user_id: str) -> str:
    """Generate password reset token"""
    return create_access_token(
        data={"user_id": user_id, "type": "password_reset"},
        expires_delta=timedelta(hours=1)  # Reset tokens expire in 1 hour
    )

def verify_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "password_reset":
            return None
        
        return payload.get("user_id")
    except Exception:
        return None

# Session management
class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        self.active_sessions = {}  # In production, use Redis
    
    def create_session(self, user_id: str, device_info: Dict[str, Any] = None) -> str:
        """Create new session"""
        session_id = hashlib.sha256(f"{user_id}:{datetime.utcnow().timestamp()}".encode()).hexdigest()
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "device_info": device_info or {}
        }
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session and update last activity"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        # Check if session expired (24 hours)
        if (datetime.utcnow() - session["last_activity"]).total_seconds() > 86400:
            self.revoke_session(session_id)
            return None
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        return session
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke session"""
        return self.active_sessions.pop(session_id, None) is not None
    
    def revoke_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for user"""
        revoked = 0
        sessions_to_remove = []
        
        for session_id, session in self.active_sessions.items():
            if session["user_id"] == user_id:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.active_sessions.pop(session_id)
            revoked += 1
        
        return revoked

# Global session manager
session_manager = SessionManager()

# Export all auth components
__all__ = [
    "security",
    "SECRET_KEY",
    "ALGORITHM", 
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "AuthenticationError",
    "AuthorizationError",
    "TokenData",
    "CurrentUser",
    "create_access_token",
    "verify_token",
    "create_api_key",
    "verify_api_key",
    "get_current_user_from_token",
    "get_current_active_user",
    "get_current_user_optional",
    "require_role",
    "require_permission",
    "require_organization_access",
    "require_admin",
    "require_manager", 
    "require_agent",
    "get_rate_limit_key",
    "get_user_organization",
    "check_organization_limits",
    "verify_webhook_signature",
    "verify_twilio_webhook",
    "verify_stripe_webhook",
    "ServiceAuth",
    "gateway_auth",
    "ai_brain_auth",
    "voice_lab_auth",
    "call_center_auth",
    "require_service_auth",
    "hash_password",
    "verify_password",
    "generate_reset_token",
    "verify_reset_token",
    "SessionManager",
    "session_manager"
]