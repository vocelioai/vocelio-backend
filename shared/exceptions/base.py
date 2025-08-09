# shared/exceptions/base.py
from typing import Optional, Dict, Any


class VocelioException(Exception):
    """Base exception for Vocelio services"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# shared/exceptions/service.py
from typing import Optional, Dict, Any
from .base import VocelioException


class ServiceException(VocelioException):
    """General service exception"""
    pass


class NotFoundError(ServiceException):
    """Resource not found exception"""
    
    def __init__(self, message: str, resource_type: str = "resource"):
        super().__init__(message, error_code="NOT_FOUND")
        self.resource_type = resource_type


class ValidationError(ServiceException):
    """Data validation exception"""
    
    def __init__(self, message: str, field_errors: Optional[Dict[str, list]] = None):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field_errors = field_errors or {}


class AuthenticationError(ServiceException):
    """Authentication exception"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(ServiceException):
    """Authorization exception"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, error_code="AUTHORIZATION_ERROR")


class RateLimitError(ServiceException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED")


class BusinessLogicError(ServiceException):
    """Business logic violation exception"""
    
    def __init__(self, message: str, business_rule: str):
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR")
        self.business_rule = business_rule


# shared/exceptions/external.py
from typing import Optional, Dict, Any
from .base import VocelioException


class ExternalAPIError(VocelioException):
    """External API error exception"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code="EXTERNAL_API_ERROR")
        self.service_name = service_name
        self.status_code = status_code
        self.response_data = response_data or {}


class TwilioError(ExternalAPIError):
    """Twilio API specific error"""
    
    def __init__(self, message: str, twilio_code: Optional[str] = None):
        super().__init__(message, "twilio")
        self.twilio_code = twilio_code


class StripeError(ExternalAPIError):
    """Stripe API specific error"""
    
    def __init__(self, message: str, stripe_code: Optional[str] = None):
        super().__init__(message, "stripe")
        self.stripe_code = stripe_code


class DatabaseError(VocelioException):
    """Database operation error"""
    
    def __init__(self, message: str, operation: str):
        super().__init__(message, error_code="DATABASE_ERROR")
        self.operation = operation