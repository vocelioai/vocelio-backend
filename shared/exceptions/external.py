# shared/exceptions/external.py
from typing import Optional, Dict, Any
from .base import VocelioException


class ExternalAPIError(VocelioException):
    """Raised when external API calls fail"""
    
    def __init__(
        self, 
        message: str = "External API error",
        error_code: str = "EXTERNAL_API_ERROR",
        status_code: Optional[int] = None,
        api_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.status_code = status_code
        self.api_name = api_name


class OpenAIAPIError(ExternalAPIError):
    """Raised when OpenAI API calls fail"""
    
    def __init__(
        self, 
        message: str = "OpenAI API error",
        error_code: str = "OPENAI_API_ERROR",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, status_code, "OpenAI", details)


class AnthropicAPIError(ExternalAPIError):
    """Raised when Anthropic API calls fail"""
    
    def __init__(
        self, 
        message: str = "Anthropic API error",
        error_code: str = "ANTHROPIC_API_ERROR",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, status_code, "Anthropic", details)


class ElevenLabsAPIError(ExternalAPIError):
    """Raised when ElevenLabs API calls fail"""
    
    def __init__(
        self, 
        message: str = "ElevenLabs API error",
        error_code: str = "ELEVENLABS_API_ERROR",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, status_code, "ElevenLabs", details)


class TwilioAPIError(ExternalAPIError):
    """Raised when Twilio API calls fail"""
    
    def __init__(
        self, 
        message: str = "Twilio API error",
        error_code: str = "TWILIO_API_ERROR",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, status_code, "Twilio", details)


class StripeAPIError(ExternalAPIError):
    """Raised when Stripe API calls fail"""
    
    def __init__(
        self, 
        message: str = "Stripe API error",
        error_code: str = "STRIPE_API_ERROR",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, status_code, "Stripe", details)


class SupabaseAPIError(ExternalAPIError):
    """Raised when Supabase API calls fail"""
    
    def __init__(
        self, 
        message: str = "Supabase API error",
        error_code: str = "SUPABASE_API_ERROR",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, status_code, "Supabase", details)
