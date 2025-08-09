from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "Vocelio.ai Voice Lab"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://vocelio.ai",
        "https://app.vocelio.ai",
        "https://*.vocelio.ai"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/vocelio_voices"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Voice AI Services
    ELEVENLABS_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = None
    
    # File Storage
    STATIC_DIR: Path = Path("static")
    VOICES_DIR: Path = STATIC_DIR / "voices"
    CLONES_DIR: Path = STATIC_DIR / "clones"
    GENERATED_DIR: Path = STATIC_DIR / "generated"
    PREVIEWS_DIR: Path = STATIC_DIR / "previews"
    
    # Voice Processing
    MAX_VOICE_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_AUDIO_FORMATS: List[str] = ["mp3", "wav", "m4a", "ogg"]
    DEFAULT_SAMPLE_RATE: int = 22050
    
    # Voice Generation Limits
    MAX_TEXT_LENGTH: int = 5000
    MAX_VOICES_PER_COMPARISON: int = 5
    MAX_BATCH_SIZE: int = 100
    
    # Caching
    CACHE_TTL: int = 3600  # 1 hour
    VOICE_CACHE_TTL: int = 24 * 3600  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    PREMIUM_RATE_LIMIT_PER_MINUTE: int = 300
    
    # Quality Thresholds
    MIN_VOICE_QUALITY_SCORE: float = 0.7
    MIN_CLONE_SIMILARITY_SCORE: float = 0.8
    
    # Analytics
    ANALYTICS_RETENTION_DAYS: int = 90
    PERFORMANCE_TRACKING_ENABLED: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # External Services
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = "us-east-1"
    S3_BUCKET: Optional[str] = None
    
    # Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # Feature Flags
    VOICE_CLONING_ENABLED: bool = True
    BATCH_OPERATIONS_ENABLED: bool = True
    ADVANCED_ANALYTICS_ENABLED: bool = True
    REAL_TIME_TESTING_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Voice Quality Presets
VOICE_PRESETS = {
    "professional": {
        "stability": 0.7,
        "similarity_boost": 0.8,
        "style": 0.2,
        "use_speaker_boost": True
    },
    "friendly": {
        "stability": 0.6,
        "similarity_boost": 0.85,
        "style": 0.4,
        "use_speaker_boost": True
    },
    "empathetic": {
        "stability": 0.65,
        "similarity_boost": 0.8,
        "style": 0.35,
        "use_speaker_boost": True
    },
    "confident": {
        "stability": 0.8,
        "similarity_boost": 0.75,
        "style": 0.3,
        "use_speaker_boost": True
    },
    "calm": {
        "stability": 0.85,
        "similarity_boost": 0.7,
        "style": 0.15,
        "use_speaker_boost": False
    },
    "enthusiastic": {
        "stability": 0.5,
        "similarity_boost": 0.9,
        "style": 0.6,
        "use_speaker_boost": True
    }
}

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese"
}

# Voice Categories
VOICE_CATEGORIES = [
    "premade",
    "cloned",
    "generated",
    "custom"
]

# Use Cases
USE_CASES = [
    "business",
    "sales", 
    "customer_service",
    "executive",
    "marketing",
    "training",
    "multilingual",
    "entertainment"
]

# Subscription Tiers
SUBSCRIPTION_TIERS = {
    "free": {
        "max_voices": 5,
        "max_generation_length": 1000,
        "voice_cloning": False,
        "batch_operations": False,
        "advanced_analytics": False,
        "rate_limit": 10
    },
    "starter": {
        "max_voices": 25,
        "max_generation_length": 2500,
        "voice_cloning": False,
        "batch_operations": True,
        "advanced_analytics": False,
        "rate_limit": 50
    },
    "pro": {
        "max_voices": 100,
        "max_generation_length": 5000,
        "voice_cloning": True,
        "batch_operations": True,
        "advanced_analytics": True,
        "rate_limit": 200
    },
    "enterprise": {
        "max_voices": -1,  # Unlimited
        "max_generation_length": -1,  # Unlimited
        "voice_cloning": True,
        "batch_operations": True,
        "advanced_analytics": True,
        "rate_limit": 1000
    }
}