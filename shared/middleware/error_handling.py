# shared/middleware/error_handling.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import traceback

from shared.exceptions.base import VocelioException
from shared.exceptions.service import (
    NotFoundError, ValidationError, AuthenticationError, 
    AuthorizationError, RateLimitError
)
from shared.exceptions.external import ExternalAPIError

logger = logging.getLogger(__name__)


async def error_handling_middleware(request: Request, call_next):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
        
    except HTTPException:
        # Let FastAPI handle HTTP exceptions
        raise
        
    except NotFoundError as e:
        logger.warning(f"Resource not found: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "not_found",
                "message": e.message,
                "error_code": e.error_code
            }
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": e.message,
                "field_errors": e.field_errors,
                "error_code": e.error_code
            }
        )
        
    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "authentication_error",
                "message": e.message,
                "error_code": e.error_code
            }
        )
        
    except AuthorizationError as e:
        logger.warning(f"Authorization error: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "authorization_error",
                "message": e.message,
                "error_code": e.error_code
            }
        )
        
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_exceeded",
                "message": e.message,
                "error_code": e.error_code
            }
        )
        
    except ExternalAPIError as e:
        logger.error(f"External API error ({e.service_name}): {e.message}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "external_service_error",
                "message": f"External service ({e.service_name}) error: {e.message}",
                "service": e.service_name,
                "error_code": e.error_code
            }
        )
        
    except VocelioException as e:
        logger.error(f"Service error: {e.message}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "service_error",
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
        )
        
    except Exception as e:
        # Log full traceback for unexpected errors
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR"
            }
        )


# shared/middleware/request_logging.py
from fastapi import Request
import logging
import time
import uuid

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    """Request logging middleware"""
    
    # Generate request ID
    request_id = str(uuid.uuid4())[:8]
    
    # Log request start
    start_time = time.time()
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"[{request_id}] {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


# shared/middleware/rate_limiting.py
from fastapi import Request, HTTPException, status
from typing import Dict
import time
from collections import defaultdict, deque

from core.config import settings


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str, max_requests: int, window_seconds: int) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) >= max_requests:
            return False
        
        # Add current request
        client_requests.append(now)
        return True


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/docs", "/redoc"]:
        return await call_next(request)
    
    # Get client identifier
    client_ip = request.client.host if request.client else "unknown"
    client_id = f"{client_ip}:{request.url.path}"
    
    # Check rate limit
    if not rate_limiter.is_allowed(
        client_id,
        settings.RATE_LIMIT_REQUESTS,
        settings.RATE_LIMIT_WINDOW
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
        )
    
    return await call_next(request)


# shared/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict, Any

from core.config import settings

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Return user information from token
        return {
            "id": user_id,
            "email": payload.get("email"),
            "organization_id": payload.get("organization_id"),
            "role": payload.get("role", "user"),
            "permissions": payload.get("permissions", [])
        }
        
    except JWTError:
        raise credentials_exception


async def get_organization_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """Extract organization ID from current user"""
    organization_id = current_user.get("organization_id")
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No organization associated with user"
        )
    
    return organization_id


async def require_permission(permission: str):
    """Dependency factory for permission checking"""
    def check_permission(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        
        if permission not in user_permissions and "admin" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return current_user
    
    return check_permission


# Phone number specific permissions
require_phone_numbers_read = require_permission("phone_numbers:read")
require_phone_numbers_write = require_permission("phone_numbers:write")
require_phone_numbers_delete = require_permission("phone_numbers:delete")
require_phone_numbers_purchase = require_permission("phone_numbers:purchase")


# shared/database/client.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()