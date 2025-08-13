# shared/exceptions/service.py
from typing import Optional, Dict, Any
from .base import VocelioException


class NotFoundError(VocelioException):
    """Raised when a requested resource is not found"""
    
    def __init__(
        self, 
        message: str = "Resource not found",
        error_code: str = "RESOURCE_NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ValidationError(VocelioException):
    """Raised when input validation fails"""
    
    def __init__(
        self, 
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.field_errors = field_errors or {}


class AuthenticationError(VocelioException):
    """Raised when authentication fails"""
    
    def __init__(
        self, 
        message: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class AuthorizationError(VocelioException):
    """Raised when authorization fails"""
    
    def __init__(
        self, 
        message: str = "Authorization failed",
        error_code: str = "AUTHORIZATION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class RateLimitError(VocelioException):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ServiceUnavailableError(VocelioException):
    """Raised when a service is unavailable"""
    
    def __init__(
        self, 
        message: str = "Service unavailable",
        error_code: str = "SERVICE_UNAVAILABLE",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ConfigurationError(VocelioException):
    """Raised when there's a configuration error"""
    
    def __init__(
        self, 
        message: str = "Configuration error",
        error_code: str = "CONFIGURATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class DatabaseError(VocelioException):
    """Raised when database operations fail"""
    
    def __init__(
        self, 
        message: str = "Database error",
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
