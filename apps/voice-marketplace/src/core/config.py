# apps/voice-marketplace/src/core/config.py
"""
Voice Marketplace Service Configuration
"""

from pydantic import BaseSettings, Field
from typing import List, Dict, Any
import os


class VoiceMarketplaceSettings(BaseSettings):
    """Voice Marketplace service configuration"""
    
    # Basic service settings
    SERVICE_NAME: str = "voice-marketplace"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8006, env="PORT")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    
    # Authentication
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External APIs
    ELEVENLABS_API_KEY: str = Field(..., env="ELEVENLABS_API_KEY")
    RAMBLE_AI_API_KEY: str = Field(..., env="RAMBLE_AI_API_KEY")
    PIPER_TTS_URL: str = Field(default="http://piper-tts:8000", env="PIPER_TTS_URL")
    
    # Payment processing
    STRIPE_SECRET_KEY: str = Field(..., env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    
    # File storage
    VOICE_SAMPLES_BUCKET: str = Field(default="vocelio-voice-samples", env="VOICE_SAMPLES_BUCKET")
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Rate limiting
    RATE_LIMIT_CALLS: int = Field(default=1000, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int = Field(default=3600, env="RATE_LIMIT_PERIOD")
    
    # Voice tier pricing
    VOICE_TIER_PRICING: Dict[str, float] = {
        "standard": 0.08,
        "pro": 0.18,
        "enterprise": 0.25,
        "elite": 0.35
    }
    
    # Voice providers
    VOICE_PROVIDERS: Dict[str, Dict[str, Any]] = {
        "standard": {
            "provider": "Piper TTS",
            "languages": ["EN-US", "ES-ES", "EN-GB"],
            "features": ["Natural HD voice", "Basic emotions", "Fast response"]
        },
        "pro": {
            "provider": "Ramble.AI",
            "languages": ["EN-US", "ES-ES", "FR-FR", "DE-DE", "IT-IT", "EN-GB", "EN-AU", "EN-CA"],
            "features": ["Natural flow", "15+ languages", "Low latency", "Advanced emotions"]
        },
        "enterprise": {
            "provider": "ElevenLabs + Custom",
            "languages": "100+ languages",
            "features": ["Custom cloning", "Persona control", "Voice analytics", "Regional targeting"]
        },
        "elite": {
            "provider": "ElevenLabs Premium",
            "languages": "70+ languages",
            "features": ["Ultra-realistic", "Emotional tags", "Real-time optimization", "Celebrity quality"]
        }
    }
    
    # Marketplace settings
    MAX_COMPARISON_VOICES: int = Field(default=4, env="MAX_COMPARISON_VOICES")
    MAX_CART_ITEMS: int = Field(default=20, env="MAX_CART_ITEMS")
    VOICE_SAMPLE_DURATION: int = Field(default=30, env="VOICE_SAMPLE_DURATION")  # seconds
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=8007, env="METRICS_PORT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://vocelio.ai", "https://app.vocelio.ai"],
        env="ALLOWED_ORIGINS"
    )
    
    # API Gateway
    API_GATEWAY_URL: str = Field(default="http://api-gateway:8000", env="API_GATEWAY_URL")
    
    # Other microservices
    BILLING_SERVICE_URL: str = Field(default="http://billing-pro:8000", env="BILLING_SERVICE_URL")
    USER_SERVICE_URL: str = Field(default="http://team-hub:8000", env="USER_SERVICE_URL")
    ANALYTICS_SERVICE_URL: str = Field(default="http://analytics-pro:8000", env="ANALYTICS_SERVICE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = VoiceMarketplaceSettings()


# Voice tier validation
def validate_voice_tier(tier: str) -> bool:
    """Validate if voice tier is supported"""
    return tier.lower() in settings.VOICE_TIER_PRICING.keys()


def get_tier_price(tier: str) -> float:
    """Get price for voice tier"""
    return settings.VOICE_TIER_PRICING.get(tier.lower(), 0.0)


def get_tier_provider(tier: str) -> str:
    """Get provider for voice tier"""
    provider_info = settings.VOICE_PROVIDERS.get(tier.lower(), {})
    return provider_info.get("provider", "Unknown")


def get_tier_features(tier: str) -> List[str]:
    """Get features for voice tier"""
    provider_info = settings.VOICE_PROVIDERS.get(tier.lower(), {})
    return provider_info.get("features", [])


# Service URLs for inter-service communication
SERVICE_URLS = {
    "api_gateway": settings.API_GATEWAY_URL,
    "billing": settings.BILLING_SERVICE_URL,
    "users": settings.USER_SERVICE_URL,
    "analytics": settings.ANALYTICS_SERVICE_URL
}