"""
Vocelio API Gateway Configuration
World-class enterprise configuration with comprehensive settings
"""

import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with enterprise-grade configuration"""
    
    # Application
    APP_NAME: str = "Vocelio API Gateway"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    WORKERS: int = Field(default=1)
    
    # Security
    SECRET_KEY: str = Field(default="your-super-secret-key-change-in-production", description="Application secret key")
    JWT_SECRET_KEY: str = Field(default="your-jwt-secret-key", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "https://app.vocelio.ai",
            "https://dashboard.vocelio.ai"
        ]
    )
    # Alias expected by main.py
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "https://app.vocelio.ai",
            "https://dashboard.vocelio.ai"
        ]
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "*.vocelio.ai"]
    )
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost:5432/vocelio", description="PostgreSQL database URL")
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=0)
    
    # Redis
    # Use service hostname inside docker-compose network; override in .env for local non-docker runs
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    REDIS_MAX_CONNECTIONS: int = Field(default=100)
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=1000)
    RATE_LIMIT_WINDOW: int = Field(default=3600)  # 1 hour

    # Health / Service timeouts & resiliency (added for discovery & health modules)
    HEALTH_CHECK_TIMEOUT: int = Field(default=5)
    SERVICE_TIMEOUT: int = Field(default=10)
    UNHEALTHY_THRESHOLD: int = Field(default=3)
    CIRCUIT_BREAKER_ENABLED: bool = Field(default=True)
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=5)
    CIRCUIT_BREAKER_TIMEOUT: int = Field(default=30)
    LOAD_BALANCER_STRATEGY: str = Field(default="round_robin")
    HEALTH_CHECK_INTERVAL: int = Field(default=30)
    
    # Service URLs (Vocelio Custom Domains - Professional Branding)
    OVERVIEW_SERVICE_URL: str = Field(default="https://overview.vocelio.ai")
    AGENTS_SERVICE_URL: str = Field(default="https://agents.vocelio.ai")
    CAMPAIGNS_SERVICE_URL: str = Field(default="https://campaigns.vocelio.ai")
    CALL_CENTER_SERVICE_URL: str = Field(default="https://call.vocelio.ai")
    PHONE_NUMBERS_SERVICE_URL: str = Field(default="https://numbers.vocelio.ai")
    VOICE_MARKETPLACE_SERVICE_URL: str = Field(default="https://voicemarketplace.vocelio.ai")
    VOICE_LAB_SERVICE_URL: str = Field(default="https://voicelab.vocelio.ai")
    FLOW_BUILDER_SERVICE_URL: str = Field(default="https://flowbuilder.vocelio.ai")
    ANALYTICS_SERVICE_URL: str = Field(default="https://analytics.vocelio.ai")
    AI_BRAIN_SERVICE_URL: str = Field(default="https://brain.vocelio.ai")
    INTEGRATIONS_SERVICE_URL: str = Field(default="https://integrations.vocelio.ai")
    AGENT_STORE_SERVICE_URL: str = Field(default="https://backend.vocelio.ai")
    BILLING_SERVICE_URL: str = Field(default="https://billing.vocelio.ai")
    TEAM_HUB_SERVICE_URL: str = Field(default="https://team.vocelio.ai")
    COMPLIANCE_SERVICE_URL: str = Field(default="https://compliance.vocelio.ai")
    WHITE_LABEL_SERVICE_URL: str = Field(default="https://whitelabel.vocelio.ai")
    DEVELOPER_API_SERVICE_URL: str = Field(default="https://developer.vocelio.ai")
    SETTINGS_SERVICE_URL: str = Field(default="https://settings.vocelio.ai")
    
    # Additional Enterprise Services
    KNOWLEDGE_BASE_SERVICE_URL: str = Field(default="https://knowledge.vocelio.ai")
    LEAD_MANAGEMENT_SERVICE_URL: str = Field(default="https://lead.vocelio.ai")
    SCHEDULING_SERVICE_URL: str = Field(default="https://scheduling.vocelio.ai")
    DATA_WAREHOUSE_SERVICE_URL: str = Field(default="https://data.vocelio.ai")
    IDENTITY_SERVICE_URL: str = Field(default="https://identity.vocelio.ai")
    SECURITY_SERVICE_URL: str = Field(default="https://security.vocelio.ai")
    NOTIFICATIONS_SERVICE_URL: str = Field(default="https://notifications.vocelio.ai")
    SCRIPTS_SERVICE_URL: str = Field(default="https://scripts.vocelio.ai")
    WEBHOOKS_SERVICE_URL: str = Field(default="https://webhooks.vocelio.ai")
    API_MANAGEMENT_SERVICE_URL: str = Field(default="https://apimanagement.vocelio.ai")
    
    # External APIs
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key")
    ELEVENLABS_API_KEY: str = Field(default="", description="ElevenLabs API key")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = Field(default="", description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", description="Twilio Auth Token")
    TWILIO_PHONE_NUMBER: str = Field(default="", description="Twilio Phone Number")
    
    # Supabase
    SUPABASE_URL: str = Field(default="", description="Supabase URL")
    SUPABASE_SERVICE_KEY: str = Field(default="", description="Supabase Service Key")
    SUPABASE_JWT_SECRET: str = Field(default="", description="Supabase JWT Secret")
    
    # Cloud Storage
    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    AWS_REGION: str = Field(default="us-east-1")
    S3_BUCKET: str = Field(default="vocelio-storage")
    
    # Payment Processing
    STRIPE_SECRET_KEY: str = Field(default="")
    STRIPE_PUBLISHABLE_KEY: str = Field(default="")
    STRIPE_WEBHOOK_SECRET: str = Field(default="")
    
    # Monitoring & Logging
    SENTRY_DSN: str = Field(default="")
    LOG_LEVEL: str = Field(default="INFO")
    ENABLE_METRICS: bool = Field(default=True)
    
    # Performance
    REQUEST_TIMEOUT: int = Field(default=30)
    MAX_REQUEST_SIZE: int = Field(default=16 * 1024 * 1024)  # 16MB
    
    # Features
    ENABLE_WEBSOCKETS: bool = Field(default=True)
    ENABLE_CACHING: bool = Field(default=True)
    ENABLE_BACKGROUND_TASKS: bool = Field(default=True)
    
    # AI Configuration
    DEFAULT_AI_MODEL: str = Field(default="gpt-4")
    MAX_AI_TOKENS: int = Field(default=4000)
    AI_TEMPERATURE: float = Field(default=0.7)
    
    # Voice Configuration
    DEFAULT_VOICE_PROVIDER: str = Field(default="elevenlabs")
    VOICE_CACHE_DURATION: int = Field(default=3600)  # 1 hour
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [url.strip() for url in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables


class DatabaseConfig:
    """Database configuration with connection pooling"""
    
    def __init__(self, settings: Settings):
        self.url = settings.DATABASE_URL
        self.pool_size = settings.DATABASE_POOL_SIZE
        self.max_overflow = settings.DATABASE_MAX_OVERFLOW
        
    def get_engine_config(self) -> Dict[str, Any]:
        """Get SQLAlchemy engine configuration"""
        return {
            "url": self.url,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "echo": False,
        }


class RedisConfig:
    """Redis configuration for caching and sessions"""
    
    def __init__(self, settings: Settings):
        self.url = settings.REDIS_URL
        self.max_connections = settings.REDIS_MAX_CONNECTIONS
        
    def get_connection_config(self) -> Dict[str, Any]:
        """Get Redis connection configuration"""
        return {
            "url": self.url,
            "max_connections": self.max_connections,
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }


class ServiceConfig:
    """Microservices configuration"""
    
    def __init__(self, settings: Settings):
        self.services = {
            "overview": settings.OVERVIEW_SERVICE_URL,
            "agents": settings.AGENTS_SERVICE_URL,
            "smart-campaigns": settings.CAMPAIGNS_SERVICE_URL,
            "call-center": settings.CALL_CENTER_SERVICE_URL,
            "phone-numbers": settings.PHONE_NUMBERS_SERVICE_URL,
            "voice-marketplace": settings.VOICE_MARKETPLACE_SERVICE_URL,
            "voice-lab": settings.VOICE_LAB_SERVICE_URL,
            "flow-builder": settings.FLOW_BUILDER_SERVICE_URL,
            "analytics-pro": settings.ANALYTICS_SERVICE_URL,
            "ai-brain": settings.AI_BRAIN_SERVICE_URL,
            "integrations": settings.INTEGRATIONS_SERVICE_URL,
            "agent-store": settings.AGENT_STORE_SERVICE_URL,
            "billing-pro": settings.BILLING_SERVICE_URL,
            "team-hub": settings.TEAM_HUB_SERVICE_URL,
            "compliance": settings.COMPLIANCE_SERVICE_URL,
            "white-label": settings.WHITE_LABEL_SERVICE_URL,
            "developer-api": settings.DEVELOPER_API_SERVICE_URL,
            "settings": settings.SETTINGS_SERVICE_URL,
        }
    
    def get_service_url(self, service_name: str) -> str:
        """Get service URL by name"""
        return self.services.get(service_name, "")
    
    def get_all_services(self) -> Dict[str, str]:
        """Get all service configurations"""
        return self.services.copy()


# Create settings instance
settings = Settings()

# Export configuration instances
database_config = DatabaseConfig(settings)
redis_config = RedisConfig(settings)
service_config = ServiceConfig(settings)

# Placeholder (legacy) service configuration mapping expected by some modules
SERVICE_CONFIG: dict = {
    "overview-service": {"name": "Overview Service", "health_check_path": "/health", "timeout": 5, "retry_attempts": 2},
    "ai-agents-service": {"name": "AI Agents Service", "health_check_path": "/health", "timeout": 5, "retry_attempts": 2},
    "smart-campaigns-service": {"name": "Smart Campaigns Service", "health_check_path": "/health", "timeout": 5, "retry_attempts": 2},
}
