# apps/team-hub/src/core/config.py

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Basic service settings
    SERVICE_NAME: str = "team-hub"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "👥 Enterprise Team Management & Performance Center"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8008"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_HOSTS: List[str] = ["*"]  # Configure properly for production
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/vocelio_db")
    DATABASE_ECHO: bool = False
    
    # Supabase settings (if using Supabase)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Redis settings for caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    
    # API Gateway settings
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    
    # Other service URLs for inter-service communication
    AI_BRAIN_SERVICE_URL: str = os.getenv("AI_BRAIN_SERVICE_URL", "http://localhost:8010")
    CALL_CENTER_SERVICE_URL: str = os.getenv("CALL_CENTER_SERVICE_URL", "http://localhost:8004")
    ANALYTICS_SERVICE_URL: str = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8009")
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@vocelio.ai")
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".jpg", ".jpeg", ".png", ".pdf", ".csv", ".xlsx"]
    UPLOAD_DIR: str = "uploads"
    
    # Performance settings
    MAX_TEAM_MEMBERS_PER_PAGE: int = 50
    MAX_DEPARTMENTS_PER_ORG: int = 100
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Feature flags
    ENABLE_REAL_TIME_UPDATES: bool = True
    ENABLE_PERFORMANCE_TRACKING: bool = True
    ENABLE_NOTIFICATIONS: bool = True
    ENABLE_AUDIT_LOGGING: bool = True
    
    # Monitoring settings
    METRICS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
