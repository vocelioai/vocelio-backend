# apps/developer-api/src/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Vocelio.ai Developer API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API settings
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # API Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Webhook settings
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "webhook-secret-key")
    MAX_WEBHOOK_RETRIES: int = 3
    WEBHOOK_TIMEOUT: int = 30
    
    # SDK Generation
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    SDK_REPO_BASE: str = "vocelioai/vocelio-sdk"
    
    # Documentation
    DOCS_URL: str = os.getenv("DOCS_URL", "https://docs.vocelio.ai")
    
    class Config:
        case_sensitive = True

settings = Settings()
