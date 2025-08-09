"""
Analytics Pro Configuration
📊 Service configuration and environment settings
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator, Field
from functools import lru_cache

class AnalyticsProSettings(BaseSettings):
    """Analytics Pro service configuration"""
    
    # Service Info
    SERVICE_NAME: str = "analytics-pro"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Advanced Analytics & Business Intelligence Service"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8006, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # Redis Configuration (for caching and real-time)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")
    REDIS_TIMEOUT: int = Field(default=5, env="REDIS_TIMEOUT")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://app.vocelio.ai"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "*.vocelio.ai", "*.railway.app"],
        env="ALLOWED_HOSTS"
    )
    
    # Analytics Configuration
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")  # 5 minutes
    REAL_TIME_UPDATE_INTERVAL: int = Field(default=3, env="REAL_TIME_UPDATE_INTERVAL")  # seconds
    MAX_QUERY_RANGE_DAYS: int = Field(default=90, env="MAX_QUERY_RANGE_DAYS")
    
    # Export Configuration
    MAX_EXPORT_ROWS: int = Field(default=100000, env="MAX_EXPORT_ROWS")
    EXPORT_FILE_RETENTION_DAYS: int = Field(default=7, env="EXPORT_FILE_RETENTION_DAYS")
    EXPORT_TEMP_DIR: str = Field(default="/tmp/vocelio_exports", env="EXPORT_TEMP_DIR")
    
    # Report Configuration
    REPORT_GENERATION_TIMEOUT: int = Field(default=300, env="REPORT_GENERATION_TIMEOUT")  # seconds
    REPORT_RETENTION_DAYS: int = Field(default=30, env="REPORT_RETENTION_DAYS")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # seconds (1 hour)
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")  # json or text
    
    # External Service URLs
    API_GATEWAY_URL: str = Field(default="http://api-gateway:8000", env="API_GATEWAY_URL")
    CALL_CENTER_SERVICE_URL: str = Field(default="http://call-center:8001", env="CALL_CENTER_SERVICE_URL")
    AGENTS_SERVICE_URL: str = Field(default="http://agents:8002", env="AGENTS_SERVICE_URL")
    CAMPAIGNS_SERVICE_URL: str = Field(default="http://smart-campaigns:8003", env="CAMPAIGNS_SERVICE_URL")
    VOICE_LAB_SERVICE_URL: str = Field(default="http://voice-lab:8005", env="VOICE_LAB_SERVICE_URL")
    AI_BRAIN_SERVICE_URL: str = Field(default="http://ai-brain:8009", env="AI_BRAIN_SERVICE_URL")
    
    # External API Keys
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Monitoring & Observability
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    ENABLE_TRACING: bool = Field(default=False, env="ENABLE_TRACING")
    JAEGER_ENDPOINT: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    
    # WebSocket Configuration
    WEBSOCKET_MAX_CONNECTIONS: int = Field(default=1000, env="WEBSOCKET_MAX_CONNECTIONS")
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(default=30, env="WEBSOCKET_HEARTBEAT_INTERVAL")
    
    # Data Retention
    METRICS_RETENTION_DAYS: int = Field(default=90, env="METRICS_RETENTION_DAYS")
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=365, env="AUDIT_LOG_RETENTION_DAYS")
    CACHE_CLEANUP_INTERVAL_HOURS: int = Field(default=6, env="CACHE_CLEANUP_INTERVAL_HOURS")
    
    # Performance Tuning
    ASYNC_POOL_SIZE: int = Field(default=100, env="ASYNC_POOL_SIZE")
    QUERY_TIMEOUT_SECONDS: int = Field(default=30, env="QUERY_TIMEOUT_SECONDS")
    BULK_INSERT_BATCH_SIZE: int = Field(default=1000, env="BULK_INSERT_BATCH_SIZE")
    
    # Feature Flags
    ENABLE_AI_INSIGHTS: bool = Field(default=True, env="ENABLE_AI_INSIGHTS")
    ENABLE_REAL_TIME_UPDATES: bool = Field(default=True, env="ENABLE_REAL_TIME_UPDATES")
    ENABLE_ADVANCED_ANALYTICS: bool = Field(default=True, env="ENABLE_ADVANCED_ANALYTICS")
    ENABLE_PREDICTIVE_ANALYTICS: bool = Field(default=False, env="ENABLE_PREDICTIVE_ANALYTICS")
    
    # Email Configuration (for reports and alerts)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST") 
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    FROM_EMAIL: str = Field(default="analytics@vocelio.ai", env="FROM_EMAIL")
    
    # File Storage Configuration
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")  # local, s3, gcs
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    S3_BUCKET_NAME: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    
    # Webhook Configuration
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    WEBHOOK_TIMEOUT: int = Field(default=10, env="WEBHOOK_TIMEOUT")  # seconds
    
    # Development/Testing
    MOCK_EXTERNAL_SERVICES: bool = Field(default=False, env="MOCK_EXTERNAL_SERVICES")
    GENERATE_SAMPLE_DATA: bool = Field(default=False, env="GENERATE_SAMPLE_DATA")
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True) 
    def parse_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v.lower()
    
    @validator("PORT")
    def validate_port(cls, v):
        if not 1024 <= v <= 65535:
            raise ValueError("PORT must be between 1024 and 65535")
        return v
    
    @validator("CACHE_TTL_SECONDS")
    def validate_cache_ttl(cls, v):
        if v < 60 or v > 3600:
            raise ValueError("CACHE_TTL_SECONDS must be between 60 and 3600")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

class DatabaseConfig:
    """Database-specific configuration"""
    
    def __init__(self, settings: AnalyticsProSettings):
        self.settings = settings
    
    @property
    def database_url(self) -> str:
        return self.settings.DATABASE_URL
    
    @property
    def engine_options(self) -> dict:
        return {
            "pool_size": self.settings.DATABASE_POOL_SIZE,
            "max_overflow": self.settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.settings.DATABASE_POOL_TIMEOUT,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
        }

class RedisConfig:
    """Redis-specific configuration"""
    
    def __init__(self, settings: AnalyticsProSettings):
        self.settings = settings
    
    @property
    def redis_url(self) -> str:
        return self.settings.REDIS_URL
    
    @property
    def connection_options(self) -> dict:
        return {
            "max_connections": self.settings.REDIS_POOL_SIZE,
            "socket_timeout": self.settings.REDIS_TIMEOUT,
            "socket_connect_timeout": self.settings.REDIS_TIMEOUT,
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }

class CacheConfig:
    """Cache configuration"""
    
    def __init__(self, settings: AnalyticsProSettings):
        self.settings = settings
    
    @property
    def cache_configs(self) -> dict:
        return {
            "overview_metrics": {
                "ttl": 180,  # 3 minutes
                "max_size": 1000
            },
            "performance_metrics": {
                "ttl": 240,  # 4 minutes  
                "max_size": 500
            },
            "agent_analytics": {
                "ttl": 300,  # 5 minutes
                "max_size": 2000
            },
            "campaign_analytics": {
                "ttl": 360,  # 6 minutes
                "max_size": 1000
            },
            "voice_analytics": {
                "ttl": 420,  # 7 minutes
                "max_size": 500
            },
            "ai_insights": {
                "ttl": 600,  # 10 minutes
                "max_size": 100
            },
            "chart_data": {
                "ttl": 120,  # 2 minutes
                "max_size": 3000
            }
        }

# Environment-specific configurations
class DevelopmentConfig(AnalyticsProSettings):
    """Development environment configuration"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    MOCK_EXTERNAL_SERVICES: bool = True
    GENERATE_SAMPLE_DATA: bool = True
    CACHE_TTL_SECONDS: int = 60  # Shorter cache for development

class ProductionConfig(AnalyticsProSettings):
    """Production environment configuration"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    MOCK_EXTERNAL_SERVICES: bool = False
    GENERATE_SAMPLE_DATA: bool = False
    WORKERS: int = 4
    
    # Enhanced security for production
    RATE_LIMIT_REQUESTS: int = 500  # More restrictive
    QUERY_TIMEOUT_SECONDS: int = 15  # Faster timeout

class TestingConfig(AnalyticsProSettings):
    """Testing environment configuration"""
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    MOCK_EXTERNAL_SERVICES: bool = True
    DATABASE_URL: str = "sqlite:///test_analytics.db"
    REDIS_URL: str = "redis://localhost:6379/15"  # Different DB for tests

@lru_cache()
def get_settings() -> AnalyticsProSettings:
    """Get settings instance with caching"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionConfig()
    elif environment == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return DatabaseConfig(get_settings())

def get_redis_config() -> RedisConfig:
    """Get Redis configuration"""
    return RedisConfig(get_settings())

def get_cache_config() -> CacheConfig:
    """Get cache configuration"""
    return CacheConfig(get_settings())

# Export settings instance
settings = get_settings()

# Configuration validation
def validate_configuration():
    """Validate configuration settings"""
    config = get_settings()
    errors = []
    
    # Required settings validation
    if not config.DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    if not config.SECRET_KEY:
        errors.append("SECRET_KEY is required")
    
    # Database URL format validation
    if config.DATABASE_URL and not (
        config.DATABASE_URL.startswith("postgresql://") or 
        config.DATABASE_URL.startswith("sqlite://")
    ):
        errors.append("DATABASE_URL must be a valid PostgreSQL or SQLite URL")
    
    # Redis URL validation
    if config.REDIS_URL and not config.REDIS_URL.startswith("redis://"):
        errors.append("REDIS_URL must be a valid Redis URL")
    
    # Port range validation
    if config.METRICS_PORT == config.PORT:
        errors.append("METRICS_PORT cannot be the same as main PORT")
    
    # Email configuration validation (if enabled)
    if config.SMTP_HOST and not config.SMTP_USERNAME:
        errors.append("SMTP_USERNAME is required when SMTP_HOST is set")
    
    # AWS S3 configuration validation
    if config.STORAGE_TYPE == "s3":
        if not config.AWS_ACCESS_KEY_ID:
            errors.append("AWS_ACCESS_KEY_ID is required for S3 storage")
        if not config.AWS_SECRET_ACCESS_KEY:
            errors.append("AWS_SECRET_ACCESS_KEY is required for S3 storage")
        if not config.S3_BUCKET_NAME:
            errors.append("S3_BUCKET_NAME is required for S3 storage")
    
    # Performance settings validation
    if config.BULK_INSERT_BATCH_SIZE > 10000:
        errors.append("BULK_INSERT_BATCH_SIZE should not exceed 10000 for optimal performance")
    
    if config.WEBSOCKET_MAX_CONNECTIONS > 5000:
        errors.append("WEBSOCKET_MAX_CONNECTIONS should not exceed 5000")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    return True

# Configuration helpers
def get_service_urls() -> dict:
    """Get all external service URLs"""
    config = get_settings()
    return {
        "api_gateway": config.API_GATEWAY_URL,
        "call_center": config.CALL_CENTER_SERVICE_URL,
        "agents": config.AGENTS_SERVICE_URL,
        "campaigns": config.CAMPAIGNS_SERVICE_URL,
        "voice_lab": config.VOICE_LAB_SERVICE_URL,
        "ai_brain": config.AI_BRAIN_SERVICE_URL,
    }

def get_feature_flags() -> dict:
    """Get all feature flags"""
    config = get_settings()
    return {
        "ai_insights": config.ENABLE_AI_INSIGHTS,
        "real_time_updates": config.ENABLE_REAL_TIME_UPDATES,
        "advanced_analytics": config.ENABLE_ADVANCED_ANALYTICS,
        "predictive_analytics": config.ENABLE_PREDICTIVE_ANALYTICS,
        "metrics": config.ENABLE_METRICS,
        "tracing": config.ENABLE_TRACING,
    }

def get_retention_settings() -> dict:
    """Get data retention settings"""
    config = get_settings()
    return {
        "metrics_days": config.METRICS_RETENTION_DAYS,
        "audit_log_days": config.AUDIT_LOG_RETENTION_DAYS,
        "export_files_days": config.EXPORT_FILE_RETENTION_DAYS,
        "reports_days": config.REPORT_RETENTION_DAYS,
    }

def is_development() -> bool:
    """Check if running in development mode"""
    return get_settings().ENVIRONMENT == "development"

def is_production() -> bool:
    """Check if running in production mode"""
    return get_settings().ENVIRONMENT == "production"

def is_testing() -> bool:
    """Check if running in testing mode"""
    return get_settings().ENVIRONMENT == "testing"

# Configuration constants
class AnalyticsConstants:
    """Constants used throughout the analytics service"""
    
    # Metric types
    METRIC_TYPES = {
        "CALLS": "calls",
        "REVENUE": "revenue", 
        "PERFORMANCE": "performance",
        "SATISFACTION": "satisfaction",
        "CONVERSION": "conversion"
    }
    
    # Time ranges
    TIME_RANGES = {
        "1H": "1h",
        "24H": "24h", 
        "7D": "7d",
        "30D": "30d",
        "90D": "90d"
    }
    
    # Chart types
    CHART_TYPES = {
        "LINE": "line",
        "BAR": "bar",
        "PIE": "pie",
        "AREA": "area"
    }
    
    # Export formats
    EXPORT_FORMATS = {
        "CSV": "csv",
        "XLSX": "xlsx", 
        "PDF": "pdf",
        "JSON": "json"
    }
    
    # Alert severities
    ALERT_SEVERITIES = {
        "LOW": "low",
        "MEDIUM": "medium",
        "HIGH": "high", 
        "CRITICAL": "critical"
    }
    
    # Agent statuses
    AGENT_STATUSES = {
        "ACTIVE": "active",
        "INACTIVE": "inactive",
        "TRAINING": "training",
        "OFFLINE": "offline"
    }
    
    # Campaign statuses
    CAMPAIGN_STATUSES = {
        "ACTIVE": "active",
        "PAUSED": "paused",
        "COMPLETED": "completed",
        "DRAFT": "draft"
    }
    
    # System health statuses
    HEALTH_STATUSES = {
        "HEALTHY": "healthy",
        "UNHEALTHY": "unhealthy",
        "DEGRADED": "degraded"
    }
    
    # Cache prefixes
    CACHE_PREFIXES = {
        "OVERVIEW": "overview_",
        "PERFORMANCE": "performance_",
        "AGENTS": "agents_",
        "CAMPAIGNS": "campaigns_",
        "VOICES": "voices_",
        "AI_INSIGHTS": "ai_insights_",
        "CHARTS": "chart_",
        "REAL_TIME": "real_time_"
    }
    
    # Default pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 1000
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = "1000/hour"
    EXPORT_RATE_LIMIT = "50/hour"
    REPORT_RATE_LIMIT = "100/hour"
    
    # File size limits
    MAX_EXPORT_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_REPORT_FILE_SIZE = 50 * 1024 * 1024   # 50MB
    
    # WebSocket message types
    WS_MESSAGE_TYPES = {
        "METRICS_UPDATE": "metrics_update",
        "ALERT": "alert",
        "SYSTEM_STATUS": "system_status",
        "HEARTBEAT": "heartbeat"
    }

# Load and validate configuration on import
try:
    validate_configuration()
except Exception as e:
    if not is_testing():  # Don't fail on import during tests
        raise e

# Export all configuration components
__all__ = [
    "AnalyticsProSettings",
    "DatabaseConfig", 
    "RedisConfig",
    "CacheConfig",
    "DevelopmentConfig",
    "ProductionConfig", 
    "TestingConfig",
    "get_settings",
    "get_database_config",
    "get_redis_config", 
    "get_cache_config",
    "validate_configuration",
    "get_service_urls",
    "get_feature_flags",
    "get_retention_settings",
    "is_development",
    "is_production",
    "is_testing",
    "AnalyticsConstants",
    "settings"
]