# apps/phone-numbers/src/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Phone Numbers Service Configuration"""
    
    # Service Configuration
    SERVICE_NAME: str = "phone-numbers"
    SERVICE_URL: str = Field(default="http://localhost:8000", env="SERVICE_URL")
    DEBUG: bool = Field(default=True, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = Field(..., env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = Field(..., env="TWILIO_AUTH_TOKEN")
    TWILIO_WEBHOOK_URL: str = Field(..., env="TWILIO_WEBHOOK_URL")
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str = Field(..., env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    STRIPE_LIVE_MODE: bool = Field(default=False, env="STRIPE_LIVE_MODE")
    
    # Security Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS Configuration
    ALLOWED_HOSTS: List[str] = Field(
        default=["http://localhost:3000", "https://vocelio.ai", "https://*.vocelio.ai"],
        env="ALLOWED_HOSTS"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Service Discovery
    API_GATEWAY_URL: str = Field(default="http://localhost:8080", env="API_GATEWAY_URL")
    BILLING_SERVICE_URL: str = Field(default="http://localhost:8007", env="BILLING_SERVICE_URL")
    COMPLIANCE_SERVICE_URL: str = Field(default="http://localhost:8010", env="COMPLIANCE_SERVICE_URL")
    
    # Phone Number Configuration
    DEFAULT_VOICE_URL: str = Field(default="https://api.vocelio.ai/voice/webhook", env="DEFAULT_VOICE_URL")
    DEFAULT_SMS_URL: str = Field(default="https://api.vocelio.ai/sms/webhook", env="DEFAULT_SMS_URL")
    
    # Number Search Configuration
    MAX_SEARCH_RESULTS: int = Field(default=50, env="MAX_SEARCH_RESULTS")
    SEARCH_TIMEOUT: int = Field(default=30, env="SEARCH_TIMEOUT")
    
    # Supported Countries and Pricing
    SUPPORTED_COUNTRIES: dict = {
        "US": {
            "name": "United States",
            "flag": "🇺🇸",
            "pricing": {"local": 1.15, "toll_free": 2.00, "mobile": 1.50},
            "area_codes": True,
            "features": ["voice", "sms", "mms"]
        },
        "CA": {
            "name": "Canada", 
            "flag": "🇨🇦",
            "pricing": {"local": 1.00, "toll_free": 2.00, "mobile": 1.25},
            "area_codes": True,
            "features": ["voice", "sms"]
        },
        "GB": {
            "name": "United Kingdom",
            "flag": "🇬🇧", 
            "pricing": {"local": 1.30, "toll_free": 2.50, "mobile": 1.80},
            "area_codes": False,
            "features": ["voice", "sms"]
        },
        "AU": {
            "name": "Australia",
            "flag": "🇦🇺",
            "pricing": {"local": 2.00, "toll_free": 3.00, "mobile": 2.50},
            "area_codes": False,
            "features": ["voice", "sms"]
        },
        "DE": {
            "name": "Germany",
            "flag": "🇩🇪",
            "pricing": {"local": 1.50, "toll_free": 2.80, "mobile": 2.00},
            "area_codes": False,
            "features": ["voice", "sms"]
        }
    }
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Redis Configuration (for caching)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Service-specific configurations
class TwilioConfig:
    """Twilio-specific configuration"""
    
    # Number types mapping
    NUMBER_TYPES = {
        "local": {"twilio_type": "Local", "description": "Geographic numbers"},
        "toll_free": {"twilio_type": "TollFree", "description": "Toll-free numbers"},
        "mobile": {"twilio_type": "Mobile", "description": "Mobile numbers"}
    }
    
    # Capabilities mapping
    CAPABILITIES = {
        "voice": "voice",
        "sms": "SMS", 
        "mms": "MMS",
        "fax": "fax"
    }
    
    # Search filters
    SEARCH_FILTERS = [
        "in_locality",
        "in_region", 
        "in_postal_code",
        "near_lat_long",
        "contains",
        "near_number"
    ]


class StripeConfig:
    """Stripe-specific configuration"""
    
    # Product configuration
    PHONE_NUMBER_PRODUCT_ID = "prod_phone_numbers"
    
    # Price configuration per country/type
    PRICE_MAPPING = {
        "US_local": "price_us_local_monthly",
        "US_toll_free": "price_us_toll_free_monthly", 
        "US_mobile": "price_us_mobile_monthly",
        "CA_local": "price_ca_local_monthly",
        # Add more as needed
    }
    
    # Webhook events we handle
    WEBHOOK_EVENTS = [
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
        "invoice.payment_succeeded",
        "customer.subscription.deleted"
    ]


# Export configurations
twilio_config = TwilioConfig()
stripe_config = StripeConfig()