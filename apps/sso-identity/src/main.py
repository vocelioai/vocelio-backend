"""
SSO Identity Service - Vocelio AI Enterprise Platform
Enterprise Single Sign-On, Identity Management, and Access Control
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import jwt
import bcrypt
from passlib.context import CryptContext
import secrets
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

# SSO & Identity Models
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ENTERPRISE_ADMIN = "enterprise_admin"
    TENANT_ADMIN = "tenant_admin"
    DEPARTMENT_ADMIN = "department_admin"
    MANAGER = "manager"
    AGENT = "agent"
    USER = "user"
    GUEST = "guest"
    API_USER = "api_user"
    SERVICE_ACCOUNT = "service_account"

class AuthProvider(str, Enum):
    INTERNAL = "internal"
    ACTIVE_DIRECTORY = "active_directory"
    AZURE_AD = "azure_ad"
    OKTA = "okta"
    GOOGLE_WORKSPACE = "google_workspace"
    ONELOGIN = "onelogin"
    PING_IDENTITY = "ping_identity"
    SAML = "saml"
    OAUTH2 = "oauth2"
    LDAP = "ldap"

class MFAMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    TOTP = "totp"
    HARDWARE_TOKEN = "hardware_token"
    BIOMETRIC = "biometric"
    PUSH_NOTIFICATION = "push_notification"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPICIOUS = "suspicious"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    manager_id: Optional[str] = None
    employee_id: Optional[str] = None
    cost_center: Optional[str] = None
    location: Optional[str] = None
    timezone: str = "UTC"
    roles: List[UserRole] = [UserRole.USER]
    groups: List[str] = []
    permissions: List[str] = []
    auth_provider: AuthProvider = AuthProvider.INTERNAL
    external_id: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    must_change_password: bool = False
    password_expires_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_password_change: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_methods: List[MFAMethod] = []
    profile_image_url: Optional[str] = None
    preferences: Dict[str, Any] = {}
    custom_attributes: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class UserSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tenant_id: str
    session_token: str
    refresh_token: Optional[str] = None
    device_id: Optional[str] = None
    device_type: Optional[str] = None
    device_name: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: str
    location: Optional[str] = None
    user_agent: str
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    terminated_at: Optional[datetime] = None
    terminated_by: Optional[str] = None
    termination_reason: Optional[str] = None
    risk_score: float = 0.0
    suspicious_activities: List[str] = []

class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    domain: str = Field(..., min_length=3, max_length=100)
    subdomain: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str = "#007bff"
    secondary_color: str = "#6c757d"
    is_active: bool = True
    subscription_tier: str = "enterprise"
    max_users: int = 10000
    current_users: int = 0
    features: List[str] = []
    sso_config: Dict[str, Any] = {}
    security_policies: Dict[str, Any] = {}
    branding: Dict[str, Any] = {}
    custom_domains: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    tenant_domain: Optional[str] = None
    remember_me: bool = False
    device_id: Optional[str] = None
    device_name: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User
    tenant: Tenant
    permissions: List[str]
    requires_mfa: bool = False
    mfa_methods: List[MFAMethod] = []
    session_id: str

class MFAChallenge(BaseModel):
    challenge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    method: MFAMethod
    code: Optional[str] = None
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=5))
    attempts: int = 0
    verified: bool = False

class PasswordResetRequest(BaseModel):
    email: EmailStr
    tenant_domain: Optional[str] = None

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    phone_number: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    manager_id: Optional[str] = None
    roles: List[UserRole] = [UserRole.USER]
    groups: List[str] = []
    send_invitation: bool = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    manager_id: Optional[str] = None
    roles: Optional[List[UserRole]] = None
    groups: Optional[List[str]] = None
    is_active: Optional[bool] = None
    timezone: Optional[str] = None

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    ip_address: str
    user_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = {}
    risk_level: str = "low"
    success: bool = True
    error_message: Optional[str] = None

class SecurityPolicy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    description: Optional[str] = None
    policy_type: str
    rules: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# In-memory storage (replace with proper database in production)
users_db: Dict[str, User] = {}
sessions_db: Dict[str, UserSession] = {}
tenants_db: Dict[str, Tenant] = {}
audit_logs_db: List[AuditLog] = []
mfa_challenges_db: Dict[str, MFAChallenge] = {}
security_policies_db: Dict[str, SecurityPolicy] = {}

# Utility functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "your-secret-key", algorithm="HS256")
    return encoded_jwt

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def log_audit_event(
    tenant_id: str,
    action: str,
    resource: str,
    ip_address: str,
    user_agent: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None
):
    """Log an audit event"""
    audit_log = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        session_id=session_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {},
        success=success,
        error_message=error_message
    )
    audit_logs_db.append(audit_log)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Optional[Request] = None
) -> User:
    """Get the current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

async def get_current_tenant(user: User = Depends(get_current_user)) -> Tenant:
    # Get the current user's tenant
    tenant = tenants_db.get(user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("SSO Identity Service starting up...")
    
    # Create default tenant
    default_tenant = Tenant(
        id="default-tenant",
        name="Default Tenant",
        domain="default.vocelio.ai",
        subdomain="default"
    )
    tenants_db[default_tenant.id] = default_tenant
    
    # Create default admin user
    admin_user = User(
        id="admin-user",
        tenant_id=default_tenant.id,
        username="admin",
        email="admin@vocelio.ai",
        first_name="System",
        last_name="Administrator",
        roles=[UserRole.SUPER_ADMIN],
        is_verified=True
    )
    users_db[admin_user.id] = admin_user
    
    yield
    
    # Shutdown
    logger.info("SSO Identity Service shutting down...")

# FastAPI app
app = FastAPI(
    title="Vocelio SSO Identity Service",
    description="Enterprise Single Sign-On, Identity Management, and Access Control",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sso-identity",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest, request: Request):
    """Authenticate user and create session"""
    # Find user by username or email
    user = None
    for u in users_db.values():
        if (u.username == login_request.username or 
            u.email == login_request.username):
            user = u
            break
    
    if not user or not user.is_active:
        log_audit_event(
            tenant_id="unknown",
            action="login_failed",
            resource="authentication",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            error_message="Invalid credentials"
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check tenant domain if provided
    tenant = tenants_db.get(user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=500, detail="Tenant not found")
        
    if (login_request.tenant_domain and 
        tenant.domain != login_request.tenant_domain):
        raise HTTPException(status_code=401, detail="Invalid tenant domain")
    
    # Verify password (in production, this would check hashed password)
    # For demo, accept any password for admin user
    if user.username != "admin":
        # In production: verify_password(login_request.password, user.hashed_password)
        pass
    
    # Create session
    session_token = generate_session_token()
    refresh_token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    session = UserSession(
        user_id=user.id,
        tenant_id=user.tenant_id,
        session_token=session_token,
        refresh_token=refresh_token,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        expires_at=expires_at
    )
    sessions_db[session.id] = session
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "session_id": session.id},
        expires_delta=timedelta(hours=24)
    )
    
    # Update user last login
    user.last_login = datetime.utcnow()
    users_db[user.id] = user
    
    # Log successful login
    log_audit_event(
        tenant_id=user.tenant_id,
        user_id=user.id,
        session_id=session.id,
        action="login_success",
        resource="authentication",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=86400,  # 24 hours
        user=user,
        tenant=tenant,
        permissions=user.permissions,
        session_id=session.id
    )

@app.post("/auth/logout")
async def logout(
    session_id: str,
    user: User = Depends(get_current_user),
    request: Optional[Request] = None
):
    """Logout user and terminate session"""
    session = sessions_db.get(session_id)
    if session and session.user_id == user.id:
        session.status = SessionStatus.TERMINATED
        session.terminated_at = datetime.utcnow()
        session.terminated_by = user.id
        session.termination_reason = "user_logout"
        sessions_db[session_id] = session
    
    log_audit_event(
        tenant_id=user.tenant_id,
        user_id=user.id,
        session_id=session_id,
        action="logout",
        resource="authentication",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    
    return {"message": "Successfully logged out"}

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str, request: Request):
    """Refresh access token using refresh token"""
    # Find session by refresh token
    session = None
    for s in sessions_db.values():
        if s.refresh_token == refresh_token and s.status == SessionStatus.ACTIVE:
            session = s
            break
    
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    user = users_db.get(session.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": user.id, "session_id": session.id},
        expires_delta=timedelta(hours=24)
    )
    
    # Update session activity
    session.last_activity = datetime.utcnow()
    sessions_db[session.id] = session
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400
    }

# User management endpoints
@app.get("/users", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Get list of users in tenant"""
    if UserRole.TENANT_ADMIN not in user.roles and UserRole.SUPER_ADMIN not in user.roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tenant_users = [u for u in users_db.values() if u.tenant_id == tenant.id]
    return tenant_users[skip:skip + limit]

@app.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Get user by ID"""
    target_user = users_db.get(user_id)
    if not target_user or target_user.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can view their own profile or admins can view any user
    if (current_user.id != user_id and 
        UserRole.TENANT_ADMIN not in current_user.roles and 
        UserRole.SUPER_ADMIN not in current_user.roles):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return target_user

@app.post("/users", response_model=User)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Create new user"""
    if UserRole.TENANT_ADMIN not in current_user.roles and UserRole.SUPER_ADMIN not in current_user.roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if username or email already exists
    for existing_user in users_db.values():
        if (existing_user.tenant_id == tenant.id and 
            (existing_user.username == user_create.username or 
             existing_user.email == user_create.email)):
            raise HTTPException(status_code=400, detail="Username or email already exists")
    
    new_user = User(
        tenant_id=tenant.id,
        username=user_create.username,
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        phone_number=user_create.phone_number,
        department=user_create.department,
        title=user_create.title,
        manager_id=user_create.manager_id,
        roles=user_create.roles,
        groups=user_create.groups,
        created_by=current_user.id
    )
    
    users_db[new_user.id] = new_user
    tenant.current_users += 1
    tenants_db[tenant.id] = tenant
    
    return new_user

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Update user"""
    target_user = users_db.get(user_id)
    if not target_user or target_user.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can update their own profile or admins can update any user
    if (current_user.id != user_id and 
        UserRole.TENANT_ADMIN not in current_user.roles and 
        UserRole.SUPER_ADMIN not in current_user.roles):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target_user, field, value)
    
    target_user.updated_at = datetime.utcnow()
    target_user.updated_by = current_user.id
    users_db[user_id] = target_user
    
    return target_user

# Session management
@app.get("/sessions", response_model=List[UserSession])
async def get_user_sessions(
    user: User = Depends(get_current_user)
):
    """Get user's active sessions"""
    user_sessions = [s for s in sessions_db.values() 
                    if s.user_id == user.id and s.status == SessionStatus.ACTIVE]
    return user_sessions

@app.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: str,
    user: User = Depends(get_current_user)
):
    """Terminate a specific session"""
    session = sessions_db.get(session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = SessionStatus.TERMINATED
    session.terminated_at = datetime.utcnow()
    session.terminated_by = user.id
    session.termination_reason = "user_terminated"
    sessions_db[session_id] = session
    
    return {"message": "Session terminated successfully"}

# Audit logging
@app.get("/audit/logs", response_model=List[AuditLog])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Get audit logs for tenant"""
    if UserRole.TENANT_ADMIN not in user.roles and UserRole.SUPER_ADMIN not in user.roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    filtered_logs = [log for log in audit_logs_db if log.tenant_id == tenant.id]
    
    # Apply filters
    if action:
        filtered_logs = [log for log in filtered_logs if action in log.action]
    if user_id:
        filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
    if start_date:
        filtered_logs = [log for log in filtered_logs if log.timestamp >= start_date]
    if end_date:
        filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]
    
    return filtered_logs[skip:skip + limit]

# Analytics endpoints
@app.get("/analytics/users")
async def get_user_analytics(
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Get user analytics for tenant"""
    if UserRole.TENANT_ADMIN not in user.roles and UserRole.SUPER_ADMIN not in user.roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tenant_users = [u for u in users_db.values() if u.tenant_id == tenant.id]
    active_sessions = [s for s in sessions_db.values() 
                      if s.tenant_id == tenant.id and s.status == SessionStatus.ACTIVE]
    
    return {
        "total_users": len(tenant_users),
        "active_users": len([u for u in tenant_users if u.is_active]),
        "verified_users": len([u for u in tenant_users if u.is_verified]),
        "mfa_enabled_users": len([u for u in tenant_users if u.mfa_enabled]),
        "active_sessions": len(active_sessions),
        "user_roles_distribution": {
            role.value: len([u for u in tenant_users if role in u.roles])
            for role in UserRole
        },
        "departments": list(set([u.department for u in tenant_users if u.department])),
        "recent_logins": len([
            log for log in audit_logs_db 
            if (log.tenant_id == tenant.id and 
                log.action == "login_success" and 
                log.timestamp >= datetime.utcnow() - timedelta(days=1))
        ])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
