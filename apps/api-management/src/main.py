"""
API Management Service - Vocelio AI Enterprise Platform
Enterprise API Gateway, Rate Limiting, Analytics, and Developer Portal
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header, Request, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, EmailStr, validator, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import time
import aiohttp
from collections import defaultdict, deque
import re
import jwt
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# API Management Models
class APIStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    MAINTENANCE = "maintenance"
    BETA = "beta"

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class RateLimitScope(str, Enum):
    USER = "user"
    API_KEY = "api_key"
    IP = "ip"
    GLOBAL = "global"
    TENANT = "tenant"

class AuthType(str, Enum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    NONE = "none"

class AlertType(str, Enum):
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ERROR_RATE_HIGH = "error_rate_high"
    LATENCY_HIGH = "latency_high"
    QUOTA_EXCEEDED = "quota_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class API(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    version: str = "1.0.0"
    base_url: HttpUrl
    status: APIStatus = APIStatus.ACTIVE
    is_public: bool = False
    auth_required: bool = True
    auth_types: List[AuthType] = [AuthType.API_KEY]
    rate_limit_per_minute: int = 1000
    rate_limit_per_hour: int = 10000
    rate_limit_per_day: int = 100000
    quota_monthly: Optional[int] = None
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[HTTPMethod] = [HTTPMethod.GET, HTTPMethod.POST]
    custom_headers: Dict[str, str] = {}
    timeout_seconds: int = 30
    retry_attempts: int = 3
    health_check_url: Optional[str] = None
    health_check_interval: int = 300  # seconds
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    documentation_url: Optional[str] = None
    openapi_spec: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: Optional[str] = None

class APIEndpoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_id: str
    path: str = Field(..., pattern=r'^/.*')
    method: HTTPMethod
    description: Optional[str] = None
    is_active: bool = True
    auth_required: bool = True
    rate_limit_override: Optional[int] = None
    timeout_override: Optional[int] = None
    cache_ttl_seconds: Optional[int] = None
    request_validation: Optional[Dict[str, Any]] = None
    response_transformation: Optional[Dict[str, Any]] = None
    mock_response: Optional[Dict[str, Any]] = None
    is_mock: bool = False
    parameters: List[Dict[str, Any]] = []
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    examples: List[Dict[str, Any]] = []

class APIKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    key: str
    name: str
    description: Optional[str] = None
    user_id: Optional[str] = None
    api_ids: List[str] = []  # APIs this key can access, empty = all
    is_active: bool = True
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    rate_limit_override: Optional[int] = None
    quota_override: Optional[int] = None
    allowed_ips: List[str] = []
    scopes: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

class RateLimit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    scope: RateLimitScope
    scope_value: str  # user_id, api_key, ip_address, etc.
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 200
    is_active: bool = True
    api_ids: List[str] = []  # empty = applies to all APIs
    endpoint_patterns: List[str] = []  # regex patterns for endpoints
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class APIUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    api_id: str
    endpoint_id: Optional[str] = None
    api_key_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: str
    user_agent: Optional[str] = None
    method: HTTPMethod
    path: str
    query_params: Dict[str, Any] = {}
    request_headers: Dict[str, str] = {}
    response_status: int
    response_time_ms: float
    request_size_bytes: int = 0
    response_size_bytes: int = 0
    error_message: Optional[str] = None
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None

class APIAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    alert_type: AlertType
    title: str
    description: str
    severity: str = "medium"  # low, medium, high, critical
    api_id: Optional[str] = None
    api_key_id: Optional[str] = None
    threshold_value: float
    current_value: float
    is_active: bool = True
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    metadata: Dict[str, Any] = {}

class APIGatewayConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    config_name: str
    global_rate_limit: bool = True
    global_rate_limit_rpm: int = 10000
    cors_enabled: bool = True
    cors_origins: List[str] = ["*"]
    compression_enabled: bool = True
    cache_enabled: bool = True
    cache_default_ttl: int = 300
    logging_enabled: bool = True
    analytics_enabled: bool = True
    error_handling: Dict[str, Any] = {}
    middleware_configs: List[Dict[str, Any]] = []
    load_balancing: Dict[str, Any] = {}
    circuit_breaker: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# In-memory storage (replace with proper database in production)
apis_db: Dict[str, API] = {}
endpoints_db: Dict[str, APIEndpoint] = {}
api_keys_db: Dict[str, APIKey] = {}
rate_limits_db: Dict[str, RateLimit] = {}
usage_db: List[APIUsage] = []
alerts_db: Dict[str, APIAlert] = {}
gateway_configs_db: Dict[str, APIGatewayConfig] = {}

# Rate limiting storage
rate_limit_buckets = defaultdict(lambda: defaultdict(deque))
request_counts = defaultdict(lambda: defaultdict(int))

# Response cache
response_cache = {}

# Utility functions
def generate_api_key() -> str:
    """Generate a secure API key"""
    import secrets
    return f"voc_{secrets.token_urlsafe(32)}"

def check_rate_limit(scope: str, identifier: str, limit: int, window_seconds: int = 60) -> bool:
    """Check if request is within rate limit"""
    now = time.time()
    window_start = now - window_seconds
    
    # Clean old entries
    bucket = rate_limit_buckets[scope][identifier]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    
    # Check current count
    current_count = len(bucket)
    if current_count >= limit:
        return False
    
    # Add current request
    bucket.append(now)
    return True

def extract_client_identifier(request: Request, api_key: Optional[str] = None) -> str:
    """Extract client identifier for rate limiting"""
    if api_key:
        return f"api_key:{api_key}"
    
    # Try to get user from JWT token
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, options={"verify_signature": False})
            if "sub" in payload:
                return f"user:{payload['sub']}"
        except:
            pass
    
    # Fall back to IP address
    return f"ip:{request.client.host}"

async def proxy_request(
    api: API,
    endpoint: APIEndpoint,
    request: Request,
    path_params: Optional[Dict[str, str]] = None
) -> Response:
    """Proxy request to upstream API"""
    # Build target URL
    target_path = endpoint.path
    if path_params:
        for key, value in path_params.items():
            target_path = target_path.replace(f"{{{key}}}", value)
    
    target_url = urljoin(str(api.base_url), target_path.lstrip('/'))
    
    # Prepare headers
    headers = dict(request.headers)
    headers.update(api.custom_headers)
    
    # Remove hop-by-hop headers
    hop_by_hop = ['connection', 'keep-alive', 'proxy-authenticate', 
                  'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade']
    for header in hop_by_hop:
        headers.pop(header, None)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=endpoint.method.value,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                data=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout_override or api.timeout_seconds)
            ) as response:
                content = await response.read()
                
                # Create FastAPI Response
                return Response(
                    content=content,
                    status_code=response.status,
                    headers=dict(response.headers),
                    media_type=response.content_type
                )
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except Exception as e:
        logger.error(f"Proxy error: {str(e)}")
        raise HTTPException(status_code=502, detail="Bad gateway")

def validate_api_key(api_key: str, api_id: Optional[str] = None) -> Optional[APIKey]:
    """Validate API key and check permissions"""
    key_obj = None
    for key in api_keys_db.values():
        if key.key == api_key and key.is_active:
            key_obj = key
            break
    
    if not key_obj:
        return None
    
    # Check expiration
    if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
        return None
    
    # Check API access
    if api_id and key_obj.api_ids and api_id not in key_obj.api_ids:
        return None
    
    return key_obj

async def log_api_usage(
    api: API,
    endpoint: APIEndpoint,
    request: Request,
    response: Response,
    api_key_obj: Optional[APIKey] = None,
    response_time_ms: float = 0
):
    """Log API usage for analytics"""
    usage = APIUsage(
        tenant_id=api.tenant_id,
        api_id=api.id,
        endpoint_id=endpoint.id if endpoint else None,
        api_key_id=api_key_obj.id if api_key_obj else None,
        user_id=api_key_obj.user_id if api_key_obj else None,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        method=HTTPMethod(request.method),
        path=str(request.url.path),
        query_params=dict(request.query_params),
        request_headers={k: v for k, v in request.headers.items() if k.lower() not in ['authorization']},
        response_status=response.status_code,
        response_time_ms=response_time_ms,
        request_size_bytes=len(await request.body()) if hasattr(request, '_body') else 0,
        response_size_bytes=len(response.body) if hasattr(response, 'body') else 0
    )
    
    usage_db.append(usage)
    
    # Update API key usage
    if api_key_obj:
        api_key_obj.last_used = datetime.utcnow()
        api_key_obj.usage_count += 1
        api_keys_db[api_key_obj.id] = api_key_obj

# Mock authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"id": "user-123", "tenant_id": "tenant-123", "roles": ["api_admin"]}

async def get_api_key(api_key: Optional[str] = Depends(api_key_header)):
    return api_key

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("API Management Service starting up...")
    
    # Create default gateway config
    default_config = APIGatewayConfig(
        tenant_id="tenant-123",
        config_name="Default Configuration",
        global_rate_limit_rpm=10000,
        cors_origins=["*"],
        error_handling={
            "404": {"message": "API endpoint not found"},
            "429": {"message": "Rate limit exceeded"},
            "500": {"message": "Internal server error"}
        }
    )
    gateway_configs_db[default_config.id] = default_config
    
    yield
    
    # Shutdown
    logger.info("API Management Service shutting down...")

# FastAPI app
app = FastAPI(
    title="Vocelio API Management Service",
    description="Enterprise API Gateway, Rate Limiting, Analytics, and Developer Portal",
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
        "service": "api-management",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# API Management endpoints
@app.get("/apis", response_model=List[API])
async def get_apis(
    status: Optional[APIStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all APIs for tenant"""
    tenant_apis = [api for api in apis_db.values() if api.tenant_id == current_user["tenant_id"]]
    
    if status:
        tenant_apis = [api for api in tenant_apis if api.status == status]
    
    return tenant_apis

@app.get("/apis/{api_id}", response_model=API)
async def get_api(
    api_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific API"""
    api = apis_db.get(api_id)
    if not api or api.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="API not found")
    return api

@app.post("/apis", response_model=API)
async def create_api(
    api: API,
    current_user: dict = Depends(get_current_user)
):
    """Create new API"""
    api.tenant_id = current_user["tenant_id"]
    api.created_by = current_user["id"]
    apis_db[api.id] = api
    return api

@app.put("/apis/{api_id}", response_model=API)
async def update_api(
    api_id: str,
    api_update: API,
    current_user: dict = Depends(get_current_user)
):
    """Update API"""
    existing_api = apis_db.get(api_id)
    if not existing_api or existing_api.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="API not found")
    
    api_update.tenant_id = current_user["tenant_id"]
    api_update.updated_at = datetime.utcnow()
    api_update.updated_by = current_user["id"]
    apis_db[api_id] = api_update
    return api_update

@app.delete("/apis/{api_id}")
async def delete_api(
    api_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete API"""
    api = apis_db.get(api_id)
    if not api or api.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="API not found")
    
    # Remove associated endpoints
    endpoint_ids_to_remove = [ep_id for ep_id, ep in endpoints_db.items() if ep.api_id == api_id]
    for ep_id in endpoint_ids_to_remove:
        del endpoints_db[ep_id]
    
    del apis_db[api_id]
    return {"message": "API deleted successfully"}

# API Endpoints management
@app.get("/apis/{api_id}/endpoints", response_model=List[APIEndpoint])
async def get_api_endpoints(
    api_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get endpoints for API"""
    api = apis_db.get(api_id)
    if not api or api.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="API not found")
    
    return [ep for ep in endpoints_db.values() if ep.api_id == api_id]

@app.post("/apis/{api_id}/endpoints", response_model=APIEndpoint)
async def create_api_endpoint(
    api_id: str,
    endpoint: APIEndpoint,
    current_user: dict = Depends(get_current_user)
):
    """Create new API endpoint"""
    api = apis_db.get(api_id)
    if not api or api.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="API not found")
    
    endpoint.api_id = api_id
    endpoints_db[endpoint.id] = endpoint
    return endpoint

# API Keys management
@app.get("/api-keys", response_model=List[APIKey])
async def get_api_keys(
    current_user: dict = Depends(get_current_user)
):
    """Get API keys for tenant"""
    return [key for key in api_keys_db.values() if key.tenant_id == current_user["tenant_id"]]

@app.post("/api-keys", response_model=APIKey)
async def create_api_key(
    api_key_request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create new API key"""
    api_key = APIKey(
        tenant_id=current_user["tenant_id"],
        key=generate_api_key(),
        name=api_key_request.get("name", "Generated API Key"),
        description=api_key_request.get("description"),
        user_id=api_key_request.get("user_id"),
        api_ids=api_key_request.get("api_ids", []),
        expires_at=datetime.fromisoformat(api_key_request["expires_at"]) if "expires_at" in api_key_request else None,
        scopes=api_key_request.get("scopes", []),
        created_by=current_user["id"]
    )
    
    api_keys_db[api_key.id] = api_key
    return api_key

@app.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke API key"""
    api_key = api_keys_db.get(key_id)
    if not api_key or api_key.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = False
    api_keys_db[key_id] = api_key
    return {"message": "API key revoked successfully"}

# Gateway proxy endpoints
@app.api_route("/gateway/{api_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def gateway_proxy(
    api_name: str,
    request: Request,
    api_key: Optional[str] = Depends(get_api_key)
):
    """API Gateway proxy endpoint"""
    start_time = time.time()
    
    # Find API by name and path
    target_api = None
    target_endpoint = None
    
    for api in apis_db.values():
        if api.name.lower() == api_name.lower() and api.status == APIStatus.ACTIVE:
            # Find matching endpoint
            path = request.url.path.replace(f"/gateway/{api_name}", "")
            if not path.startswith("/"):
                path = "/" + path
            
            for endpoint in endpoints_db.values():
                if (endpoint.api_id == api.id and 
                    endpoint.path == path and 
                    endpoint.method.value == request.method and
                    endpoint.is_active):
                    target_api = api
                    target_endpoint = endpoint
                    break
            
            if target_api:
                break
    
    if not target_api or not target_endpoint:
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Check authentication
    api_key_obj = None
    if target_api.auth_required:
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")
        
        api_key_obj = validate_api_key(api_key, target_api.id)
        if not api_key_obj:
            raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limiting
    client_id = extract_client_identifier(request, api_key)
    rate_limit = target_endpoint.rate_limit_override or target_api.rate_limit_per_minute
    
    if not check_rate_limit("minute", client_id, rate_limit, 60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Handle mock responses
    if target_endpoint.is_mock and target_endpoint.mock_response:
        response = Response(
            content=json.dumps(target_endpoint.mock_response),
            status_code=200,
            media_type="application/json"
        )
    else:
        # Proxy to upstream API
        response = await proxy_request(target_api, target_endpoint, request)
    
    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000
    
    # Log usage
    await log_api_usage(target_api, target_endpoint, request, response, api_key_obj, response_time_ms)
    
    return response

# Analytics endpoints
@app.get("/analytics/usage")
async def get_usage_analytics(
    api_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get API usage analytics"""
    tenant_usage = [u for u in usage_db if u.tenant_id == current_user["tenant_id"]]
    
    # Apply filters
    if api_id:
        tenant_usage = [u for u in tenant_usage if u.api_id == api_id]
    if start_date:
        tenant_usage = [u for u in tenant_usage if u.timestamp >= start_date]
    if end_date:
        tenant_usage = [u for u in tenant_usage if u.timestamp <= end_date]
    
    # Calculate metrics
    total_requests = len(tenant_usage)
    total_errors = len([u for u in tenant_usage if u.response_status >= 400])
    avg_response_time = sum(u.response_time_ms for u in tenant_usage) / total_requests if total_requests > 0 else 0
    
    # Group by API
    api_stats = defaultdict(lambda: {"requests": 0, "errors": 0, "avg_response_time": 0.0})
    for usage in tenant_usage:
        api_stats[usage.api_id]["requests"] += 1
        if usage.response_status >= 400:
            api_stats[usage.api_id]["errors"] += 1
        api_stats[usage.api_id]["avg_response_time"] += usage.response_time_ms
    
    # Calculate averages
    for api_id, stats in api_stats.items():
        if stats["requests"] > 0:
            stats["avg_response_time"] /= stats["requests"]
            stats["error_rate"] = (stats["errors"] / stats["requests"]) * 100
    
    return {
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
        "avg_response_time_ms": avg_response_time,
        "api_stats": dict(api_stats)
    }

@app.get("/analytics/dashboard")
async def get_analytics_dashboard(
    time_range: int = 24,  # hours
    current_user: dict = Depends(get_current_user)
):
    """Get API management dashboard analytics"""
    tenant_id = current_user["tenant_id"]
    cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
    
    # Get recent usage
    recent_usage = [u for u in usage_db 
                   if u.tenant_id == tenant_id and u.timestamp >= cutoff_time]
    
    # Calculate metrics
    total_requests = len(recent_usage)
    unique_clients = len(set(u.api_key_id or u.ip_address for u in recent_usage))
    total_apis = len([api for api in apis_db.values() if api.tenant_id == tenant_id])
    active_api_keys = len([key for key in api_keys_db.values() 
                          if key.tenant_id == tenant_id and key.is_active])
    
    # Error analysis
    errors = [u for u in recent_usage if u.response_status >= 400]
    error_rate = (len(errors) / total_requests * 100) if total_requests > 0 else 0
    
    # Response time analysis
    response_times = [u.response_time_ms for u in recent_usage]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
    
    # Top APIs by usage
    api_usage_counts = defaultdict(int)
    for usage in recent_usage:
        api_usage_counts[usage.api_id] += 1
    
    top_apis = sorted(api_usage_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_apis_with_names = []
    for api_id, count in top_apis:
        api = apis_db.get(api_id)
        if api:
            top_apis_with_names.append({
                "api_id": api_id,
                "api_name": api.name,
                "request_count": count
            })
    
    # Request timeline (hourly buckets)
    timeline = []
    for i in range(time_range):
        hour_start = datetime.utcnow() - timedelta(hours=i+1)
        hour_end = datetime.utcnow() - timedelta(hours=i)
        hour_requests = [u for u in recent_usage if hour_start <= u.timestamp < hour_end]
        hour_errors = [u for u in hour_requests if u.response_status >= 400]
        
        timeline.append({
            "hour": hour_start.strftime("%H:00"),
            "requests": len(hour_requests),
            "errors": len(hour_errors),
            "avg_response_time": sum(u.response_time_ms for u in hour_requests) / len(hour_requests) if hour_requests else 0
        })
    
    timeline.reverse()  # Chronological order
    
    return {
        "total_requests": total_requests,
        "unique_clients": unique_clients,
        "total_apis": total_apis,
        "active_api_keys": active_api_keys,
        "error_rate": error_rate,
        "avg_response_time_ms": avg_response_time,
        "p95_response_time_ms": p95_response_time,
        "top_apis": top_apis_with_names,
        "request_timeline": timeline,
        "status_code_distribution": {
            "2xx": len([u for u in recent_usage if 200 <= u.response_status < 300]),
            "3xx": len([u for u in recent_usage if 300 <= u.response_status < 400]),
            "4xx": len([u for u in recent_usage if 400 <= u.response_status < 500]),
            "5xx": len([u for u in recent_usage if 500 <= u.response_status < 600])
        }
    }

# Rate limiting management
@app.get("/rate-limits", response_model=List[RateLimit])
async def get_rate_limits(
    current_user: dict = Depends(get_current_user)
):
    """Get rate limits for tenant"""
    return [rl for rl in rate_limits_db.values() if rl.tenant_id == current_user["tenant_id"]]

@app.post("/rate-limits", response_model=RateLimit)
async def create_rate_limit(
    rate_limit: RateLimit,
    current_user: dict = Depends(get_current_user)
):
    """Create new rate limit"""
    rate_limit.tenant_id = current_user["tenant_id"]
    rate_limits_db[rate_limit.id] = rate_limit
    return rate_limit

# Health check for APIs
@app.post("/apis/{api_id}/health-check")
async def check_api_health(
    api_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Perform health check on API"""
    api = apis_db.get(api_id)
    if not api or api.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="API not found")
    
    if not api.health_check_url:
        raise HTTPException(status_code=400, detail="No health check URL configured")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                api.health_check_url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                is_healthy = response.status == 200
                api.is_healthy = is_healthy
                api.last_health_check = datetime.utcnow()
                apis_db[api_id] = api
                
                return {
                    "api_id": api_id,
                    "is_healthy": is_healthy,
                    "status_code": response.status,
                    "response_time_ms": response.headers.get("x-response-time", "N/A"),
                    "checked_at": api.last_health_check.isoformat()
                }
    
    except Exception as e:
        api.is_healthy = False
        api.last_health_check = datetime.utcnow()
        apis_db[api_id] = api
        
        return {
            "api_id": api_id,
            "is_healthy": False,
            "error": str(e),
            "checked_at": api.last_health_check.isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
