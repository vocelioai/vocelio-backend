# apps/api-gateway/src/middleware/auth.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import jwt
import httpx
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

async def auth_middleware(request: Request, call_next):
    """Authentication middleware for gateway"""
    
    # Skip auth for health checks and docs
    skip_auth_paths = [
        "/health",
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/",
        "/webhooks"  # Webhooks have their own auth
    ]
    
    if any(request.url.path.startswith(path) for path in skip_auth_paths):
        return await call_next(request)
    
    # Get authorization header
    authorization = request.headers.get("Authorization")
    
    if not authorization:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Missing authorization header",
                "message": "Please provide a valid API key or JWT token"
            }
        )
    
    try:
        # Extract token
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
        
        # Validate token (you can customize this based on your auth system)
        if token.startswith("voc_"):  # API Key format
            # Validate API key with developer-api service
            is_valid = await validate_api_key(token)
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid API key")
        else:
            # Validate JWT token
            payload = jwt.decode(token, os.getenv("SECRET_KEY", "secret"), algorithms=["HS256"])
            request.state.user_id = payload.get("user_id")
            request.state.org_id = payload.get("org_id")
    
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token expired", "message": "Please refresh your token"}
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid token", "message": "Please provide a valid token"}
        )
    except Exception as e:
        logger.error(f"Auth middleware error: {e}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Authentication failed", "message": "Unable to validate credentials"}
        )
    
    return await call_next(request)

async def validate_api_key(api_key: str) -> bool:
    """Validate API key with developer-api service"""
    try:
        developer_api_url = os.getenv("DEVELOPER_API_SERVICE_URL", "http://localhost:8017")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{developer_api_url}/api/v1/validate-key",
                json={"api_key": api_key}
            )
            return response.status_code == 200
    except:
        # If developer-api service is down, allow request (graceful degradation)
        logger.warning("Could not validate API key - developer-api service unavailable")
        return True

logger = logging.getLogger(__name__)