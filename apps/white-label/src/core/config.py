from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "White Label Service"
    debug: bool = False
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/vocelio")
    
    # Storage for brand assets
    storage_url: str = os.getenv("STORAGE_URL", "")
    storage_bucket: str = os.getenv("STORAGE_BUCKET", "vocelio-brands")
    
    # CDN
    cdn_url: str = os.getenv("CDN_URL", "https://cdn.vocelio.com")
    
    # Branding limits
    max_logo_size_mb: float = 5.0
    max_custom_css_kb: float = 100.0
    allowed_domains_per_brand: int = 10
    
    # Template engine
    template_cache_ttl: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
