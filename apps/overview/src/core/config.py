"""
Overview Service Configuration
Core configuration settings for the dashboard service
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    """Overview service settings"""
    
    # Service Information
    SERVICE_NAME: str = "vocelio-overview"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_DESCRIPTION: str = "Vocelio.ai Overview/Command Center Service"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Vocelio.ai Overview API"
    
    # Database Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "vocelio-overview-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # External Services
    AI_BRAIN_SERVICE_URL: str = os.getenv("AI_BRAIN_SERVICE_URL", "http://localhost:8003")
    CALL_CENTER_SERVICE_URL: str = os.getenv("CALL_CENTER_SERVICE_URL", "http://localhost:8004")
    VOICE_LAB_SERVICE_URL: str = os.getenv("VOICE_LAB_SERVICE_URL", "http://localhost:8006")
    ANALYTICS_SERVICE_URL: str = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8009")
    BILLING_SERVICE_URL: str = os.getenv("BILLING_SERVICE_URL", "http://localhost:8012")
    
    # Service Discovery
    SERVICE_REGISTRY_URL: Optional[str] = os.getenv("SERVICE_REGISTRY_URL")
    ENABLE_SERVICE_DISCOVERY: bool = False
    
    # Caching
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    LIVE_METRICS_CACHE_TTL: int = 2  # 2 seconds for live metrics
    
    # Real-time Updates
    ENABLE_REAL_TIME_UPDATES: bool = True
    METRICS_UPDATE_INTERVAL: int = 2  # seconds
    WEBSOCKET_ENABLED: bool = True
    
    # Performance Monitoring
    ENABLE_METRICS_COLLECTION: bool = True
    METRICS_ENDPOINT: str = "/metrics"
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    ENABLE_JSON_LOGGING: bool = True
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://vocelio.ai",
        "https://app.vocelio.ai",
        "https://*.vocelio.ai"
    ]
    ALLOW_CREDENTIALS: bool = True
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # AI/ML Configuration
    AI_INSIGHTS_ENABLED: bool = True
    AI_ANALYSIS_QUEUE_SIZE: int = 100
    AI_CONFIDENCE_THRESHOLD: float = 0.7
    PREDICTIVE_ANALYTICS_ENABLED: bool = True
    
    # Dashboard Configuration
    DEFAULT_DASHBOARD_REFRESH_INTERVAL: int = 30  # seconds
    MAX_DASHBOARD_WIDGETS: int = 20
    ENABLE_CUSTOM_DASHBOARDS: bool = True
    DASHBOARD_EXPORT_FORMATS: List[str] = ["pdf", "csv", "excel", "json"]
    
    # Alert Configuration
    ALERTS_ENABLED: bool = True
    MAX_ALERTS_PER_ORGANIZATION: int = 1000
    ALERT_RETENTION_DAYS: int = 30
    
    # Data Export
    EXPORT_MAX_RECORDS: int = 100000
    EXPORT_TIMEOUT_SECONDS: int = 300
    EXPORT_STORAGE_PATH: str = "/tmp/exports"
    
    # Background Tasks
    BACKGROUND_TASKS_ENABLED: bool = True
    MAX_CONCURRENT_TASKS: int = 10
    TASK_TIMEOUT_SECONDS: int = 300
    
    # Security
    ENABLE_API_KEY_AUTH: bool = True
    ENABLE_JWT_AUTH: bool = True
    REQUIRE_HTTPS: bool = False  # Set to True in production
    SECURITY_HEADERS_ENABLED: bool = True
    
    # Feature Flags
    ENABLE_GLOBAL_METRICS: bool = True
    ENABLE_PREDICTIVE_INSIGHTS: bool = True
    ENABLE_REAL_TIME_ALERTS: bool = True
    ENABLE_CUSTOM_METRICS: bool = True
    ENABLE_COMPARATIVE_ANALYTICS: bool = True
    
    # Integration Settings
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "vocelio-webhook-secret")
    WEBHOOK_TIMEOUT_SECONDS: int = 30
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @validator("SUPABASE_URL")
    def validate_supabase_url(cls, v):
        if not v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SUPABASE_URL is required in production")
        return v
    
    @validator("SUPABASE_ANON_KEY")
    def validate_supabase_anon_key(cls, v):
        if not v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SUPABASE_ANON_KEY is required in production")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "vocelio-overview-secret-key-change-in-production" and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v
    
    @validator("ALLOWED_ORIGINS")
    def validate_allowed_origins(cls, v):
        if "*" in v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("Wildcard CORS origins not allowed in production")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Create global settings instance
settings = get_settings()

# Service-specific configuration classes
class DatabaseConfig:
    """Database configuration"""
    
    @staticmethod
    def get_database_url() -> str:
        """Get database connection URL"""
        return settings.SUPABASE_URL
    
    @staticmethod
    def get_connection_params() -> dict:
        """Get database connection parameters"""
        return {
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT
        }

class CacheConfig:
    """Cache configuration"""
    
    @staticmethod
    def get_redis_url() -> Optional[str]:
        """Get Redis URL"""
        return settings.REDIS_URL
    
    @staticmethod
    def get_cache_ttl(cache_type: str = "default") -> int:
        """Get cache TTL based on type"""
        ttl_map = {
            "default": settings.CACHE_TTL_SECONDS,
            "live_metrics": settings.LIVE_METRICS_CACHE_TTL,
            "dashboard": 60,
            "insights": 300,
            "system_health": 30
        }
        return ttl_map.get(cache_type, settings.CACHE_TTL_SECONDS)

class LoggingConfig:
    """Logging configuration"""
    
    @staticmethod
    def get_log_config() -> dict:
        """Get logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": settings.LOG_FORMAT,
                },
                "json": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "formatter": "json" if settings.ENABLE_JSON_LOGGING else "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "formatter": "json" if settings.ENABLE_JSON_LOGGING else "default",
                    "class": "logging.FileHandler",
                    "filename": settings.LOG_FILE,
                } if settings.LOG_FILE else None
            },
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": ["default"] + (["file"] if settings.LOG_FILE else [])
            }
        }

class ServiceUrls:
    """Service URL configuration"""
    
    AI_BRAIN = settings.AI_BRAIN_SERVICE_URL
    CALL_CENTER = settings.CALL_CENTER_SERVICE_URL
    VOICE_LAB = settings.VOICE_LAB_SERVICE_URL
    ANALYTICS = settings.ANALYTICS_SERVICE_URL
    BILLING = settings.BILLING_SERVICE_URL
    
    @classmethod
    def get_service_url(cls, service_name: str) -> str:
        """Get service URL by name"""
        service_map = {
            "ai_brain": cls.AI_BRAIN,
            "call_center": cls.CALL_CENTER,
            "voice_lab": cls.VOICE_LAB,
            "analytics": cls.ANALYTICS,
            "billing": cls.BILLING
        }
        return service_map.get(service_name, "")

# Export main settings
__all__ = ["settings", "Settings", "DatabaseConfig", "CacheConfig", "LoggingConfig", "ServiceUrls"]