"""
Settings Service Configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Settings service configuration"""
    
    # Service Configuration
    service_name: str = "settings"
    service_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://vocelio.vercel.app",
        "https://vocelio.ai"
    ]
    
    # Database Configuration
    database_url: str = os.getenv(
        "SUPABASE_URL", 
        "postgresql://user:password@localhost:5432/vocelio_settings"
    )
    database_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    
    # Authentication
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External Services
    gateway_url: str = os.getenv("GATEWAY_URL", "http://localhost:8001")
    ai_brain_url: str = os.getenv("AI_BRAIN_URL", "http://localhost:8010")
    call_center_url: str = os.getenv("CALL_CENTER_URL", "http://localhost:8004")
    
    # Security Settings
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")
    cors_origins: List[str] = [
        "http://localhost:3000",
        "https://vocelio.ai"
    ]
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Redis (for caching)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cache_ttl: int = 300  # 5 minutes
    
    # File Storage
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".jpg", ".jpeg", ".png", ".svg", ".pdf"]
    upload_path: str = "uploads/settings"
    
    # Notification Settings
    smtp_server: str = os.getenv("SMTP_SERVER", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    
    # Compliance
    gdpr_enabled: bool = True
    data_retention_days: int = 365
    audit_log_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
