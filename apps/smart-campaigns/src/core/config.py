# apps/smart-campaigns/src/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Basic service configuration
    SERVICE_NAME: str = "smart-campaigns"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    PORT: int = Field(default=8002, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://vocelio.ai"], 
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "*.railway.app", "vocelio.ai"],
        env="ALLOWED_HOSTS"
    )
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # External Services
    API_GATEWAY_URL: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    AI_BRAIN_SERVICE_URL: str = Field(default="http://localhost:8010", env="AI_BRAIN_SERVICE_URL")
    CALL_CENTER_SERVICE_URL: str = Field(default="http://localhost:8004", env="CALL_CENTER_SERVICE_URL")
    VOICE_LAB_SERVICE_URL: str = Field(default="http://localhost:8007", env="VOICE_LAB_SERVICE_URL")
    ANALYTICS_SERVICE_URL: str = Field(default="http://localhost:8009", env="ANALYTICS_SERVICE_URL")
    
    # AI & ML Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    AI_OPTIMIZATION_ENABLED: bool = Field(default=True, env="AI_OPTIMIZATION_ENABLED")
    PREDICTION_MODEL_VERSION: str = Field(default="v1.0", env="PREDICTION_MODEL_VERSION")
    
    # Campaign Configuration
    MAX_CAMPAIGNS_PER_USER: int = Field(default=100, env="MAX_CAMPAIGNS_PER_USER")
    MAX_PROSPECTS_PER_CAMPAIGN: int = Field(default=50000, env="MAX_PROSPECTS_PER_CAMPAIGN")
    DEFAULT_CALL_TIMEOUT: int = Field(default=30, env="DEFAULT_CALL_TIMEOUT")
    MAX_CONCURRENT_CALLS: int = Field(default=10, env="MAX_CONCURRENT_CALLS")
    
    # Scheduling
    SCHEDULER_TIMEZONE: str = Field(default="UTC", env="SCHEDULER_TIMEZONE")
    MIN_SCHEDULE_INTERVAL: int = Field(default=5, env="MIN_SCHEDULE_INTERVAL")  # minutes
    MAX_SCHEDULE_INTERVAL: int = Field(default=1440, env="MAX_SCHEDULE_INTERVAL")  # 24 hours
    
    # Performance & Limits
    RATE_LIMIT_REQUESTS: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    MAX_BATCH_SIZE: int = Field(default=1000, env="MAX_BATCH_SIZE")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    
    # Redis Configuration
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    REDIS_PREFIX: str = Field(default="smart_campaigns:", env="REDIS_PREFIX")
    
    # Monitoring & Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PREFIX: str = Field(default="smart_campaigns", env="METRICS_PREFIX")
    
    # Feature Flags
    ENABLE_AB_TESTING: bool = Field(default=True, env="ENABLE_AB_TESTING")
    ENABLE_PREDICTIVE_ANALYTICS: bool = Field(default=True, env="ENABLE_PREDICTIVE_ANALYTICS")
    ENABLE_AUTO_OPTIMIZATION: bool = Field(default=True, env="ENABLE_AUTO_OPTIMIZATION")
    ENABLE_REAL_TIME_UPDATES: bool = Field(default=True, env="ENABLE_REAL_TIME_UPDATES")
    
    # Integrations
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    
    # File Storage
    UPLOAD_MAX_SIZE: int = Field(default=10 * 1024 * 1024, env="UPLOAD_MAX_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["csv", "xlsx", "txt", "json"],
        env="ALLOWED_FILE_TYPES"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Campaign Status Constants
class CampaignStatus:
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

# Campaign Priority Constants
class CampaignPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Prospect Status Constants
class ProspectStatus:
    NEW = "new"
    CONTACTED = "contacted"
    ANSWERED = "answered"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    VOICEMAIL = "voicemail"
    DISCONNECTED = "disconnected"
    CALLBACK_REQUESTED = "callback_requested"
    DO_NOT_CALL = "do_not_call"
    CONVERTED = "converted"
    FAILED = "failed"

# Campaign Types
class CampaignType:
    OUTBOUND_CALL = "outbound_call"
    FOLLOW_UP = "follow_up"
    APPOINTMENT_SETTING = "appointment_setting"
    LEAD_QUALIFICATION = "lead_qualification"
    CUSTOMER_SURVEY = "customer_survey"
    PRODUCT_PROMOTION = "product_promotion"

# AI Optimization Types
class OptimizationType:
    SUCCESS_RATE = "success_rate"
    CALL_DURATION = "call_duration"
    CONVERSION_RATE = "conversion_rate"
    COST_EFFICIENCY = "cost_efficiency"
    LEAD_QUALITY = "lead_quality"