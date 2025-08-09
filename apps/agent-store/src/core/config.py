from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "Agent Store Service"
    debug: bool = False
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/vocelio")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External APIs
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Storage
    storage_bucket: str = os.getenv("STORAGE_BUCKET", "vocelio-agents")
    storage_url: str = os.getenv("STORAGE_URL", "")
    
    # Marketplace
    commission_rate: float = 0.15  # 15% platform commission
    min_agent_price: float = 9.99
    max_agent_price: float = 999.99
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
