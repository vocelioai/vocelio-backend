# apps/flow-builder/src/core/config.py
from pydantic import BaseSettings, Field
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Vocelio Flow Builder Service"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    supabase_url: str = Field(..., env="SUPABASE_URL") 
    supabase_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Authentication
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External Services
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    elevenlabs_api_key: Optional[str] = Field(None, env="ELEVENLABS_API_KEY")
    twilio_account_sid: Optional[str] = Field(None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(None, env="TWILIO_AUTH_TOKEN")
    
    # Service Discovery
    api_gateway_url: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    ai_brain_service_url: str = Field(default="http://localhost:8001", env="AI_BRAIN_SERVICE_URL")
    voice_lab_service_url: str = Field(default="http://localhost:8002", env="VOICE_LAB_SERVICE_URL")
    call_center_service_url: str = Field(default="http://localhost:8003", env="CALL_CENTER_SERVICE_URL")
    
    # Flow Builder Specific
    max_flow_nodes: int = Field(default=100, env="MAX_FLOW_NODES")
    max_execution_time: int = Field(default=300, env="MAX_EXECUTION_TIME")  # seconds
    max_concurrent_executions: int = Field(default=10, env="MAX_CONCURRENT_EXECUTIONS")
    
    # File Storage
    file_storage_path: str = Field(default="./storage", env="FILE_STORAGE_PATH")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    # Redis/Cache
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # CORS
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    cors_methods: str = Field(default="*", env="CORS_METHODS")
    cors_headers: str = Field(default="*", env="CORS_HEADERS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Helper functions
def get_cors_origins():
    """Get CORS origins as a list"""
    if settings.cors_origins == "*":
        return ["*"]
    return [origin.strip() for origin in settings.cors_origins.split(",")]

def is_development():
    """Check if running in development mode"""
    return settings.environment.lower() == "development"

def is_production():
    """Check if running in production mode"""
    return settings.environment.lower() == "production"